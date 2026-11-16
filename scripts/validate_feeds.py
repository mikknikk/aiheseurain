#!/usr/bin/env python3
"""
Tarkistaa uutisseurannan RSS-syötteet ja niitä kuvaavan dokumentaation.

Skripti ei muuta tiedostoja. Se lukee syötteet, tarkistaa niiden rakenteen
ja päättää lopuksi, läpäiseekö repository automaattiset laatutestit.
"""

from __future__ import annotations

from datetime import datetime
from html.parser import HTMLParser
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlsplit


# ROOT tarkoittaa projektin juurikansiota. Koska tämä skripti on scripts/-
# kansiossa, sen yläpuolella oleva kansio on koko repository.
ROOT = Path(__file__).resolve().parents[1]

# Kaikki kymmenen julkaistavaa RSS-syötettä. Viimeinen on näytösvahti,
# joka toimii erillään yhdeksän aiheen päivittäisestä tehtäväkierrosta.
FEEDS = [
    "feeds/tolkien.xml",
    "feeds/taylor-swift.xml",
    "feeds/gurmeet-ram-rahim-singh.xml",
    "feeds/muumit.xml",
    "feeds/wakaliwood.xml",
    "feeds/euroviisut.xml",
    "feeds/sompote-sands.xml",
    "feeds/shakkidraamat.xml",
    "feeds/intialaiset-elokuvat.xml",
    "feeds/intialaisten-elokuvien-naytokset.xml",
]
ROTATION_FEEDS = FEEDS[:-1]

# HTML:ssä on elementtejä, joilla ei ole erillistä sulkutagia.
# Esimerkiksi <br> ja <img> ovat tällaisia. Muut elementit pitää sulkea.
VOID = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
}


def fail(message: str) -> None:
    """Tulostaa virheen ja keskeyttää testin epäonnistuneena.

    GitHub Actions tulkitsee ohjelman päättymisen virhekoodiin epäonnistumiseksi.
    Näin virhe ei jää huomaamatta, vaikka testejä ajettaisiin automaattisesti.
    """
    print(f"VIRHE: {message}", file=sys.stderr)
    raise SystemExit(1)


class HTMLCheck(HTMLParser):
    """Tutkii RSS-kuvauksen sisällä olevaa HTML-koodia.

    RSS-kuvauksen sisältö on HTML-katkelma: tarkistamme, että tagit sulkeutuvat
    oikein, linkeissä on kelvolliset osoitteet ja kuvilla on vaihtoehtotekstit.
    Tämä ei ole täydellinen HTML-standardin tarkistin, vaan projektin tarpeisiin
    tehty kevyt rakennetarkistus.
    """

    def __init__(self, label: str):
        super().__init__(convert_charrefs=True)
        # label kertoo, minkä syötteen ja uutisen HTML:ää parhaillaan tutkitaan.
        self.label = label

        # stack pitää kirjaa avatuista elementeistä. Viimeisenä avattu pitää
        # sulkea ensimmäisenä, kuten sisäkkäisissä HTML-elementeissä kuuluu.
        self.stack = []
        self.errors = []

        # Laskemme linkit ja keräämme otsikkotasot myöhempää tarkistusta varten.
        self.links = 0
        self.headings = []

    def _start(self, tag, attrs, closed=False):
        """Käsittelee HTML-elementin aloituksen ja sen attribuutit."""
        attrs_map = {}

        # Muutamme attribuutit sanakirjaksi, jotta esimerkiksi href löytyy
        # helposti. Sama attribuutti kahdesti on yleensä virhe.
        for key, value in attrs:
            if key in attrs_map:
                self.errors.append(f"attribuutti {key!r} kahdesti")
            attrs_map[key] = value

        if tag == "a":
            # Linkin pitää osoittaa verkko-osoitteeseen, jossa on http/https
            # ja palvelimen nimi. Suhteelliset ja tyhjät osoitteet eivät kelpaa.
            href = (attrs_map.get("href") or "").strip()
            parsed = urlsplit(href)
            if parsed.scheme not in {"http", "https"} or not parsed.netloc:
                self.errors.append(f"virheellinen linkin href {href!r}")
            self.links += 1

        if tag == "img" and "alt" not in attrs_map:
            # Alt-teksti auttaa ruudunlukijan käyttäjää ymmärtämään kuvan sisällön.
            self.errors.append("img-elementiltä puuttuu alt")

        if re.fullmatch(r"h[1-6]", tag):
            # Tallennetaan otsikon taso (esimerkiksi h2 -> 2), jotta voimme
            # havaita myöhemmin epäloogiset hypyt otsikkotasojen välillä.
            self.headings.append(int(tag[1]))

        # Tavallinen avauselementti lisätään pinoon. Itse itsensä sulkevia
        # elementtejä ja HTML:n tyhjiä elementtejä ei lisätä.
        if not closed and tag not in VOID:
            self.stack.append(tag)

    def handle_starttag(self, tag, attrs):
        """HTMLParser kutsuu tätä tavallisen avaustagin kohdalla."""
        self._start(tag, attrs)

    def handle_startendtag(self, tag, attrs):
        """Käsittelee itse itsensä sulkevan tagin, esimerkiksi <br/>."""
        self._start(tag, attrs, True)

    def handle_endtag(self, tag):
        """Varmistaa, että sulkutagi vastaa viimeksi avattua elementtiä."""
        if tag in VOID or not self.stack or self.stack[-1] != tag:
            self.errors.append(f"virheellinen sulkutagi </{tag}>")

            # Jos sulkutagi löytyy pinon sisältä, siivoamme pinon siitä
            # ylöspäin. Näin tarkistin voi jatkaa muiden virheiden etsimistä.
            if tag in self.stack:
                while self.stack and self.stack[-1] != tag:
                    self.stack.pop()
                if self.stack:
                    self.stack.pop()
            return

        self.stack.pop()

    def close(self):
        """Viimeistelee tarkistuksen ja etsii keskeneräiset rakenteet."""
        super().close()

        # Jos pinoon jäi elementtejä, niiltä puuttuu sulkutagi.
        if self.stack:
            self.errors.append("sulkematta: " + ", ".join(self.stack))

        # Otsikkotasossa ei pitäisi hypätä esimerkiksi h2:sta suoraan h4:ään.
        # Tasojen ei tarvitse aina kasvaa, mutta yhden tason ylittävä hyppy
        # tekee dokumentin rakenteesta vaikeammin hahmotettavan.
        previous = 0
        for level in self.headings:
            if previous and level > previous + 1:
                self.errors.append(f"otsikkotaso hyppää h{previous} -> h{level}")
            previous = level


def timestamp(value, label):
    """Muuntaa aikaleiman päivämääräolioksi ja tarkistaa aikavyöhykkeen.

    Tyhjä tai puuttuva aikaleima voidaan esittää null-arvolla (Pythonissa None).
    Se on hyödyllistä silloin, kun vanhasta tarkistuksesta ei ole luotettavaa
    tietoa. Aikaleimaa ei pidä keksiä jälkikäteen.
    """
    if value is None:
        return None

    if not isinstance(value, str) or not value.strip():
        fail(f"{label}: aikaleiman pitää olla ISO 8601 -merkkijono tai null")

    try:
        # Pythonin datetime tunnistaa aikavyöhykkeen sisältävän ISO 8601 -ajan.
        # Z tarkoittaa UTC-aikaa, joten muutamme sen Pythonille sopivaksi +00:00:ksi.
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        fail(f"{label}: virheellinen ISO 8601 -aikaleima {value!r}")

    # Aikaleiman on sisällettävä aikavyöhyke. Ilman sitä emme voi luotettavasti
    # verrata eri ajojen aikoja tai määrittää Suomen paikallista seurantajaksoa.
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        fail(f"{label}: aikavyöhyke puuttuu")

    return parsed


def validate_state():
    """Tarkistaa data/seurantatila.json-tiedoston sisällön.

    Tiedosto kertoo, mitä aihetta seuraavaksi käsitellään ja milloin kukin
    aihe tai näytösvahti on viimeksi tarkistettu onnistuneesti.
    """
    path = ROOT / "data/seurantatila.json"

    if not path.is_file():
        fail("data/seurantatila.json puuttuu")

    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        fail(f"seurantatilan JSON virheellinen: {exc}")

    # Ylimmän tason pitää olla JSON-olio ja sen rakenteen version pitää olla 1.
    if not isinstance(state, dict) or state.get("schema_version") != 1:
        fail("seurantatilan pitää olla schema_version 1 -JSON-olio")

    # Kaikki projektin raportointiajat käyttävät Suomen aikavyöhykettä.
    if state.get("timezone") != "Europe/Helsinki":
        fail("timezone pitää olla Europe/Helsinki")

    timestamp(state.get("updated_at"), "updated_at")

    rotation = state.get("rotation")
    if not isinstance(rotation, dict):
        fail("rotation-olio puuttuu")

    tasks = rotation.get("tasks")
    if not isinstance(tasks, dict) or len(tasks) != 9:
        fail("rotation.tasks pitää sisältää yhdeksän tehtävää")

    # Seuraavan tehtävän nimen täytyy löytyä tehtävälistan avaimista.
    if rotation.get("next_task") not in tasks:
        fail("rotation.next_task ei viittaa tehtävään")

    mapped = []

    # Käymme jokaisen yhdeksästä kiertotehtävästä läpi erikseen.
    for key, task in tasks.items():
        label = f"rotation.tasks.{key}"

        if not isinstance(task, dict):
            fail(f"{label} ei ole olio")

        # Nimi, syötetiedosto ja viimeisimmän ajon tulos ovat pakollisia tietoja.
        for field in ("name", "feed", "last_result"):
            if not isinstance(task.get(field), str) or not task[field].strip():
                fail(f"{label}.{field} puuttuu")

        mapped.append(task["feed"])

        # Kiertotehtävä ei saa vahingossa osoittaa näytösvahtiin tai tuntemattomaan syötteeseen.
        if task["feed"] not in ROTATION_FEEDS:
            fail(f"{label}.feed ei kuulu kiertoon")

        # Virhelista on aina merkkijonoista koostuva lista, myös silloin kun se on tyhjä.
        if not isinstance(task.get("errors"), list) or not all(
            isinstance(x, str) for x in task["errors"]
        ):
            fail(f"{label}.errors pitää olla merkkijonolista")

        # Luemme onnistuneen tarkistuksen ajan sekä tarkistetun uutisjakson rajat.
        success = timestamp(task.get("last_successful_check"), label + ".last_successful_check")
        start = timestamp(task.get("last_period_start"), label + ".last_period_start")
        end = timestamp(task.get("last_period_end"), label + ".last_period_end")

        # Seurantajaksolla on aina sekä alku että loppu – tai ei kumpaakaan.
        if (start is None) != (end is None):
            fail(f"{label}: jakson alku ja loppu kirjattava yhdessä")

        # Ilman onnistunutta tarkistusta ei voida väittää, että jakso olisi käsitelty.
        if success is None and start is not None:
            fail(f"{label}: jakso ilman onnistunutta tarkistusta")

        # Jakson loppu ei voi olla myöhempi kuin tarkistus, jossa se käsiteltiin.
        if success is not None and end is not None and end > success:
            fail(f"{label}: seurantajakso päättyy onnistuneen tarkistuksen jälkeen")

        # Julkaistujen uutisten ja tarkistettujen lähteiden määrät ovat joko
        # ei-negatiivisia kokonaislukuja tai null, jos määrää ei tunneta.
        for field in ("published_items", "sources_checked"):
            value = task.get(field)
            if value is not None and (type(value) is not int or value < 0):
                fail(f"{label}.{field} pitää olla ei-negatiivinen kokonaisluku tai null")

    # Jokaisen kiertosyötteen pitää esiintyä täsmälleen kerran. Tämä estää
    # esimerkiksi saman aiheen lisäämisen kahdelle vuorolle ja jonkin unohtumisen.
    if len(set(mapped)) != 9 or set(mapped) != set(ROTATION_FEEDS):
        fail("JSON-tehtävät eivät vastaa yksilöllisesti yhdeksää kiertosyötettä")

    # Näytösvahti tarkistetaan erikseen, koska se ei ole osa yhdeksän aiheen kiertoa.
    watch = state.get("separate_screening_watch")
    if not isinstance(watch, dict):
        fail("separate_screening_watch puuttuu")

    if watch.get("feed") != FEEDS[-1] or watch.get("cadence") != "daily":
        fail("näytösvahdin feedin ja päivittäisen rytmin pitää olla oikein")

    if not isinstance(watch.get("errors"), list) or not all(
        isinstance(x, str) for x in watch["errors"]
    ):
        fail("näytösvahdin errors pitää olla merkkijonolista")

    success = timestamp(watch.get("last_successful_check"), "screening.last_successful_check")
    start = timestamp(watch.get("last_period_start"), "screening.last_period_start")
    end = timestamp(watch.get("last_period_end"), "screening.last_period_end")

    if (start is None) != (end is None) or (success is None and start is not None):
        fail("näytösvahdin seurantajakso on epäjohdonmukainen")

    for field in ("published_items", "sources_checked"):
        value = watch.get(field)
        if value is not None and (type(value) is not int or value < 0):
            fail(f"screening.{field} pitää olla ei-negatiivinen kokonaisluku tai null")

    return state


def validate_docs(state):
    """Vertaa README:tä ja tehtäväjonoa koneelliseen seurantatilaan."""
    queue_path = ROOT / "docs/tehtavajono.md"
    readme_path = ROOT / "README.md"

    if not queue_path.is_file() or not readme_path.is_file():
        fail("README.md tai docs/tehtavajono.md puuttuu")

    queue = queue_path.read_text(encoding="utf-8")
    readme = readme_path.read_text(encoding="utf-8")

    # Poimimme tehtäväjonosta numeroidut rivit, joissa on myös RSS-syötteen polku.
    # Näin voimme verrata dokumentissa kuvattua järjestystä JSON-tiedostoon.
    entries = re.findall(
        r"^\s*\d+\.\s+(.+?)\s+—\s+`(feeds/[^ `]+\.xml)`\s*$",
        queue,
        re.M,
    )

    if len(entries) != 9:
        fail(f"tehtäväjonossa pitää olla yhdeksän tehtävää, löytyi {len(entries)}")

    queue_feeds = [feed for _, feed in entries]

    # Tehtäväjonon järjestys on tarkoituksellinen: sen pitää vastata syötteiden
    # määriteltyä kiertojärjestystä, jotta seuraava vuoro ei vaihdu vahingossa.
    if queue_feeds != ROTATION_FEEDS:
        fail("tehtäväjonon järjestys tai feed-polut eivät vastaa määritystä")

    # Etsimme dokumentista tekstin, joka kertoo seuraavan vuorossa olevan aiheen.
    match = re.search(r"\*\*Vuorossa seuraavaksi:\s*(.+?)\.\*\*", queue)
    if not match:
        fail("tehtäväjonon seuraavaa vuoroa ei löydy")

    task = state["rotation"]["tasks"][state["rotation"]["next_task"]]
    expected = entries[queue_feeds.index(task["feed"])][0]

    if match.group(1).strip() != expected:
        fail(
            f"tehtäväjonon seuraava vuoro ({match.group(1).strip()}) "
            f"ei vastaa JSON-tilaa ({expected})"
        )

    # README:n pitää luetella kaikki kymmenen syötettä – myös erillinen näytösfeed.
    readme_feeds = set(re.findall(r"\]\((feeds/[^)]+\.xml)\)", readme))
    if readme_feeds != set(FEEDS):
        fail(
            "README:n feed-taulukko ei vastaa kymmentä feed-tiedostoa: "
            f"puuttuu {sorted(set(FEEDS) - readme_feeds)}"
        )

    # Varmistamme, että README kertoo yhdeksän aiheen kierrosta ja näytösvahdin
    # erillisyydestä. Tämä on kevyt tekstipohjainen ristiriitojen tunnistus.
    if "yhdeksän" not in readme.lower() or "ei kuluta" not in readme.lower():
        fail("README ei kuvaa yhdeksän aiheen kiertoa ja erillistä näytösvahtia")

    if "ei kuulu tähän jonoon" not in queue.lower():
        fail("tehtäväjono ei kuvaa näytösseurannan erillisyyttä")

    # Myös tehtävien nimet tarkistetaan, jotta syötepolku ei voi olla oikein
    # mutta aiheeseen liitetty nimi väärä.
    for name, feed in entries:
        state_task = next(
            (item for item in state["rotation"]["tasks"].values() if item["feed"] == feed),
            None,
        )
        if state_task is None or state_task["name"] != name:
            fail(f"JSON-tehtävän nimi ei vastaa tehtäväjonoa: {name}")

    # Nämä vanhat sanamuodot tarkoittaisivat, että näytösseuranta olisi yhä
    # tehtäväjonon vuoro. Nykyisessä mallissa se on oma päivittäinen automationsa.
    stale_phrases = (
        "tehtäväjonon omalla vuorolla",
        "tehtäväjonon erillisellä näytösvuorolla",
        "tehtäväjonon erillinen tehtävä",
        "erillinen jonotehtävä",
    )

    for relative in (
        "docs/intialaisen-elokuvan-ohje.md",
        "docs/intialaisen-elokuvan-uutiset.md",
        "docs/intialaisen-elokuvan-seuranta.md",
    ):
        doc = ROOT / relative

        if not doc.is_file():
            fail(f"intialaisen elokuvan dokumentti puuttuu: {relative}")

        lowered = doc.read_text(encoding="utf-8").lower()

        for phrase in stale_phrases:
            if phrase in lowered:
                fail(f"{relative}: vanhentunut näytösseurannan kuvaus: {phrase}")

    # Lopuksi varmistamme, että kaikki dokumentaatiossa odotetut syötetiedostot
    # todella löytyvät repositoryn kansiorakenteesta.
    for feed in FEEDS:
        if not (ROOT / feed).is_file():
            fail(f"RSS-syöte puuttuu: {feed}")


def validate_feeds():
    """Tarkistaa kaikki RSS-syötteet ja niiden uutisitemit."""
    seen = {}
    total = 0

    for relative in FEEDS:
        path = ROOT / relative

        if not path.is_file():
            fail(f"RSS-tiedosto puuttuu: {relative}")

        raw = path.read_text(encoding="utf-8")

        # XML-parseri tarkistaa, että tiedosto on rakenteellisesti kelvollista XML:ää.
        try:
            root = ET.fromstring(raw)
        except ET.ParseError as exc:
            fail(f"{relative}: XML ei jäsenny: {exc}")

        if root.tag != "rss" or root.find("channel") is None:
            fail(f"{relative}: rss/channel puuttuu")

        channel = root.find("channel")

        # Poimimme itemit myös alkuperäisestä tekstistä, jotta voimme varmistaa,
        # että jokaisen description-elementin ympärillä on CDATA-merkintä.
        raw_items = re.findall(r"<item\b[\s\S]*?</item\s*>", raw, re.I)
        items = channel.findall("item")

        if len(raw_items) != len(items):
            fail(f"{relative}: item-lukumäärä ei täsmää")

        for number, (item, raw_item) in enumerate(zip(items, raw_items), 1):
            label = f"{relative}, item {number}"

            # Projektin julkaisusäännön mukaan itemissä ei saa olla link-elementtiä.
            if item.find("link") is not None:
                fail(f"{label}: item-link on kielletty")

            # GUID on uutisen pysyvä tunniste. Se ei saa puuttua eikä toistua
            # missään kymmenestä syötteestä.
            guid = (item.findtext("guid") or "").strip()

            if not guid:
                fail(f"{label}: GUID puuttuu")

            if guid in seen:
                fail(f"{label}: GUID {guid!r} on jo tiedostossa {seen[guid]}")

            seen[guid] = relative

            # Description sisältää varsinaisen raportin ja sen lähdeluettelon.
            description = item.findtext("description") or ""

            if not description.strip():
                fail(f"{label}: description puuttuu")

            # XML-parseri purkaa CDATA-alueen tekstiksi, joten alkuperäisestä
            # tekstistä pitää erikseen tarkistaa, että CDATA todella oli käytössä.
            match = re.search(
                r"<description\b[^>]*>([\s\S]*?)</description\s*>",
                raw_item,
                re.I,
            )

            if not match or "<![CDATA[" not in match.group(1):
                fail(f"{label}: description ei ole CDATA-alueessa")

            # Lähdeluettelon otsikon pitää löytyä raportin lopusta/sisällöstä.
            if not re.search(
                r"lähdeluettelo|<h[1-6][^>]*>\s*lähteet\s*</h[1-6]>",
                description,
                re.I,
            ):
                fail(f"{label}: lähdeluettelon otsikko puuttuu")

            # Käynnistämme HTML-tarkistimen kuvaustekstille.
            parser = HTMLCheck(label)

            try:
                parser.feed(description)
                parser.close()
            except Exception as exc:
                fail(f"{label}: HTML:n käsittely epäonnistui: {exc}")

            # Tulostetaan ensimmäiset havaitut virheet, jotta ongelman etsintä
            # on helpompaa. Yksi virhe riittää kuitenkin hylkäämään itemin.
            if parser.errors:
                fail(f"{label}: kuvaus-HTML: " + "; ".join(parser.errors[:5]))

            if parser.links == 0:
                fail(f"{label}: kuvauksessa ei ole linkkejä")

            total += 1

    # Palautamme itemien kokonaismäärän ja yksilöllisten GUIDien määrän.
    return total, len(seen)


def main():
    """Ajaa kaikki tarkistukset oikeassa järjestyksessä."""
    # Ensin tarkistetaan seurantatila, jotta dokumentteja voidaan verrata siihen.
    state = validate_state()

    # Seuraavaksi tarkistetaan dokumenttien ja seurantatilan yhdenmukaisuus.
    validate_docs(state)

    # Lopuksi käydään RSS-syötteet ja niiden julkaistut itemit läpi.
    total, unique = validate_feeds()

    # Jos tähän asti päästiin, kaikki testit läpäisivät.
    print(f"OK: {len(FEEDS)} syötettä, {total} itemiä, {unique} yksilöllistä GUIDia.")
    print("OK: kuvausten HTML-rakenne, linkit, otsikkotasot, alt-attribuutit ja lähdeluettelot.")
    print("OK: README, tehtäväjono, feed-polut ja seurantatila ovat yhdenmukaiset.")
    print("OK: aikaleimat, seurantajaksot ja erillinen näytösvahti.")


# Tämä ehto tarkoittaa, että main()-funktio suoritetaan vain, kun tiedosto
# käynnistetään suoraan skriptinä – ei silloin, jos joku tuo sen moduulina toiseen ohjelmaan.
if __name__ == "__main__":
    main()
