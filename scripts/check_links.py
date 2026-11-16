#!/usr/bin/env python3
"""Tarkistaa lähdekatalogin sekä RSS-syötteiden kanava- ja artikkelilinkit.

Skripti tekee rajattuja HTTP-pyyntöjä ja seuraa uudelleenohjauksia.
Se kirjoittaa JSON- ja Markdown-raportin erilliseen tuloshakemistoon,
mutta ei muuta lähderekisteriä eikä RSS-tiedostoja.
"""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from html.parser import HTMLParser
import json
from pathlib import Path
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
USER_AGENT = "Uutisvahti-link-checker/1.0 (+https://github.com/mikknikk/uutiset)"


class LinkParser(HTMLParser):
    """Poimii HTML-linkkielementtien href-osoitteet."""
    def __init__(self):
        super().__init__()
        self.urls = []

    def handle_starttag(self, tag, attrs):
        """Tallentaa a-elementtien osoitteet; ei esimerkiksi kuvien src-arvoja."""
        if tag.lower() == "a":
            self.urls.extend(value.strip() for key, value in attrs
                             if key.lower() == "href" and value)


def kerää_osoitteet():
    """Kokoaa yksilölliset katalogi-, kanava- ja artikkelilinkit."""
    osoitteet = {}
    def lisaa(url, lahde):
        """Yhdistää saman URL:n eri käyttökohteet yhteen tietueeseen."""
        if isinstance(url, str) and url.startswith(("http://", "https://")):
            osoitteet.setdefault(url, set()).add(lahde)

    katalogi = json.loads((ROOT / "data/source-catalog.json").read_text(encoding="utf-8"))
    for lahde in katalogi["sources"]:
        lisaa(lahde["url"], "lähdekatalogi:" + lahde["id"])

    for polku in sorted((ROOT / "feeds").glob("*.xml")):
        juuri = ET.fromstring(polku.read_text(encoding="utf-8"))
        kanava = juuri.find("channel")
        if kanava is None:
            continue
        lisaa((kanava.findtext("link") or "").strip(), polku.name + ":kanava")
        for numero, item in enumerate(kanava.findall("item"), 1):
            parser = LinkParser()
            parser.feed(item.findtext("description") or "")
            for url in parser.urls:
                lisaa(url, f"{polku.name}:item-{numero}")
    return [{"url": url, "sources": sorted(lahteet)}
            for url, lahteet in sorted(osoitteet.items())]


def luokittele_vastaus(status, alkuperainen, lopullinen):
    """Luokittelee HTTP-vastauksen ilman oletusta, että jokainen virhe on rikkinäinen linkki."""
    if 200 <= status < 300:
        return "redirected" if alkuperainen != lopullinen else "ok"
    if status in (404, 410):
        return "broken"
    if status in (401, 403):
        return "blocked"
    if status == 429:
        return "rate_limited"
    if status >= 500:
        return "server_error"
    return "http_error"


def tee_pyyntö(url, method, timeout):
    """Tekee HTTP-pyynnön; urllib seuraa tavalliset uudelleenohjaukset."""
    request = urllib.request.Request(
        url, method=method,
        headers={"User-Agent": USER_AGENT, "Accept": "*/*"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status, response.geturl()
    except urllib.error.HTTPError as error:
        # HTTP-virhe on silti palvelimen vastaus: palauta sen koodi,
        # jotta esimerkiksi 403 ja 404 eivät muutu verkkoyhteysvirheiksi.
        return error.code, error.geturl()


def tarkista_osoite(kohde, timeout):
    """Kokeilee HEAD-pyyntöä ja käyttää GET-pyyntöä, jos HEAD ei ole tuettu."""
    url = kohde["url"]
    viimeinen_virhe = None
    for yritys in range(3):
        try:
            try:
                status, lopullinen = tee_pyyntö(url, "HEAD", timeout)
            except urllib.error.HTTPError as error:
                if error.code in (403, 405, 501):
                    status, lopullinen = tee_pyyntö(url, "GET", timeout)
                else:
                    status, lopullinen = error.code, error.geturl()
            if status in (403, 405, 501):
                status, lopullinen = tee_pyyntö(url, "GET", timeout)
            tulos = luokittele_vastaus(status, url, lopullinen)
            if tulos not in ("rate_limited", "server_error") or yritys == 2:
                return {**kohde, "status_code": status, "final_url": lopullinen,
                        "result": tulos, "attempts": yritys + 1, "error": None}
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            viimeinen_virhe = str(error)
        if yritys < 2:
            time.sleep(1 + yritys)
    return {**kohde, "status_code": None, "final_url": None,
            "result": "network_error", "attempts": 3, "error": viimeinen_virhe}


def kirjoita_raportit(tulokset, output_dir):
    """Kirjoittaa JSON-raportin ja lyhyen Markdown-yhteenvedon."""
    output_dir.mkdir(parents=True, exist_ok=True)
    aika = datetime.now(timezone.utc).isoformat()
    counts = {tila: sum(t["result"] == tila for t in tulokset)
              for tila in sorted({t["result"] for t in tulokset})}
    raportti = {"checked_at": aika, "repository": "mikknikk/uutiset",
                "total": len(tulokset), "counts": counts, "results": tulokset}
    (output_dir / "link-check.json").write_text(
        json.dumps(raportti, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    rivit = ["# Lähde- ja RSS-linkkien tarkistus", "",
             f"- Tarkistushetki (UTC): {aika}",
             f"- Tarkistettuja yksilöllisiä osoitteita: {len(tulokset)}", "",
             "## Yhteenveto", ""]
    rivit.extend(f"- {tila}: {maara}" for tila, maara in counts.items())
    rivit.extend(["", "## Muut kuin suorat onnistumiset", ""])
    poikkeamat = [t for t in tulokset if t["result"] != "ok"]
    if not poikkeamat:
        rivit.append("Kaikki osoitteet vastasivat ilman uudelleenohjausta.")
    for t in poikkeamat:
        koodi = t["status_code"] if t["status_code"] is not None else "ei HTTP-vastausta"
        rivit.append(f"- **{t['result']}** ({koodi}): {t['url']}")
        rivit.append("  - Käyttökohteet: " + ", ".join(t["sources"]))
        if t["final_url"] and t["final_url"] != t["url"]:
            rivit.append("  - Lopullinen osoite: " + t["final_url"])
        if t["error"]:
            rivit.append("  - Virhe: " + t["error"])
    rivit.extend(["", "## Tulkinta", "",
        "- broken = HTTP 404 tai 410.",
        "- redirected = onnistunut vastaus eri lopullisesta osoitteesta.",
        "- blocked, rate_limited, server_error ja network_error eivät yksin todista linkkiä rikkinäiseksi.",
        "- Raportti ei muuta lähderekisteriä tai RSS-syötteitä; osoitteen korjaus vaatii ihmisen tarkistuksen.", ""])
    (output_dir / "link-check.md").write_text("\n".join(rivit), encoding="utf-8")


def main():
    """Suorittaa tarkistuksen; epäonnistuu vain varmasti rikkinäisistä 404/410-linkeistä."""
    parser = argparse.ArgumentParser(description="Tarkistaa uutisseurannan lähde- ja RSS-linkit.")
    parser.add_argument("--timeout", type=int, default=15)
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--output-dir", default="link-check-results")
    args = parser.parse_args()
    kohteet = kerää_osoitteet()
    tulokset = [None] * len(kohteet)
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        tulevat = {pool.submit(tarkista_osoite, kohde, args.timeout): i
                   for i, kohde in enumerate(kohteet)}
        for future in as_completed(tulevat):
            tulokset[tulevat[future]] = future.result()
    kirjoita_raportit(tulokset, ROOT / args.output_dir)
    rikkinäiset = sum(t["result"] == "broken" for t in tulokset)
    print(f"Tarkistettu {len(tulokset)} URL-osoitetta; 404/410-linkkejä: {rikkinäiset}.")
    return 1 if rikkinäiset else 0


if __name__ == "__main__":
    raise SystemExit(main())
