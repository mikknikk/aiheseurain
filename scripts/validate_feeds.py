#!/usr/bin/env python3
"""Validate RSS feeds, embedded HTML, documentation consistency and tracking state."""
from __future__ import annotations
from datetime import datetime
from html.parser import HTMLParser
import json, re, sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
FEEDS = [
    "feeds/tolkien.xml", "feeds/taylor-swift.xml",
    "feeds/gurmeet-ram-rahim-singh.xml", "feeds/muumit.xml",
    "feeds/wakaliwood.xml", "feeds/euroviisut.xml",
    "feeds/sompote-sands.xml", "feeds/shakkidraamat.xml",
    "feeds/intialaiset-elokuvat.xml",
    "feeds/intialaisten-elokuvien-naytokset.xml",
]
ROTATION_FEEDS = FEEDS[:-1]
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input",
        "link", "meta", "param", "source", "track", "wbr"}

def fail(message: str) -> None:
    print(f"VIRHE: {message}", file=sys.stderr)
    raise SystemExit(1)

class HTMLCheck(HTMLParser):
    def __init__(self, label: str):
        super().__init__(convert_charrefs=True)
        self.label, self.stack, self.errors = label, [], []
        self.links, self.headings = 0, []

    def _start(self, tag, attrs, closed=False):
        attrs_map = {}
        for key, value in attrs:
            if key in attrs_map:
                self.errors.append(f"attribuutti {key!r} kahdesti")
            attrs_map[key] = value
        if tag == "a":
            href = (attrs_map.get("href") or "").strip()
            parsed = urlsplit(href)
            if parsed.scheme not in {"http", "https"} or not parsed.netloc:
                self.errors.append(f"virheellinen linkin href {href!r}")
            self.links += 1
        if tag == "img" and "alt" not in attrs_map:
            self.errors.append("img-elementiltä puuttuu alt")
        if re.fullmatch(r"h[1-6]", tag):
            self.headings.append(int(tag[1]))
        if not closed and tag not in VOID:
            self.stack.append(tag)

    def handle_starttag(self, tag, attrs): self._start(tag, attrs)
    def handle_startendtag(self, tag, attrs): self._start(tag, attrs, True)
    def handle_endtag(self, tag):
        if tag in VOID or not self.stack or self.stack[-1] != tag:
            self.errors.append(f"virheellinen sulkutagi </{tag}>")
            if tag in self.stack:
                while self.stack and self.stack[-1] != tag: self.stack.pop()
                if self.stack: self.stack.pop()
            return
        self.stack.pop()
    def close(self):
        super().close()
        if self.stack: self.errors.append("sulkematta: " + ", ".join(self.stack))
        previous = 0
        for level in self.headings:
            if previous and level > previous + 1:
                self.errors.append(f"otsikkotaso hyppää h{previous} -> h{level}")
            previous = level

def timestamp(value, label):
    if value is None: return None
    if not isinstance(value, str) or not value.strip():
        fail(f"{label}: aikaleiman pitää olla ISO 8601 -merkkijono tai null")
    try: parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError: fail(f"{label}: virheellinen ISO 8601 -aikaleima {value!r}")
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        fail(f"{label}: aikavyöhyke puuttuu")
    return parsed

def validate_state():
    path = ROOT / "data/seurantatila.json"
    if not path.is_file(): fail("data/seurantatila.json puuttuu")
    try: state = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc: fail(f"seurantatilan JSON virheellinen: {exc}")
    if not isinstance(state, dict) or state.get("schema_version") != 1:
        fail("seurantatilan pitää olla schema_version 1 -JSON-olio")
    if state.get("timezone") != "Europe/Helsinki": fail("timezone pitää olla Europe/Helsinki")
    timestamp(state.get("updated_at"), "updated_at")
    rotation = state.get("rotation")
    if not isinstance(rotation, dict): fail("rotation-olio puuttuu")
    tasks = rotation.get("tasks")
    if not isinstance(tasks, dict) or len(tasks) != 9: fail("rotation.tasks pitää sisältää yhdeksän tehtävää")
    if rotation.get("next_task") not in tasks: fail("rotation.next_task ei viittaa tehtävään")
    mapped = []
    for key, task in tasks.items():
        label = f"rotation.tasks.{key}"
        if not isinstance(task, dict): fail(f"{label} ei ole olio")
        for field in ("name", "feed", "last_result"):
            if not isinstance(task.get(field), str) or not task[field].strip():
                fail(f"{label}.{field} puuttuu")
        mapped.append(task["feed"])
        if task["feed"] not in ROTATION_FEEDS: fail(f"{label}.feed ei kuulu kiertoon")
        if not isinstance(task.get("errors"), list) or not all(isinstance(x, str) for x in task["errors"]):
            fail(f"{label}.errors pitää olla merkkijonolista")
        success = timestamp(task.get("last_successful_check"), label+".last_successful_check")
        start = timestamp(task.get("last_period_start"), label+".last_period_start")
        end = timestamp(task.get("last_period_end"), label+".last_period_end")
        if (start is None) != (end is None): fail(f"{label}: jakson alku ja loppu kirjattava yhdessä")
        if success is None and start is not None: fail(f"{label}: jakso ilman onnistunutta tarkistusta")
        if success is not None and end is not None and end > success:
            fail(f"{label}: seurantajakso päättyy onnistuneen tarkistuksen jälkeen")
        for field in ("published_items", "sources_checked"):
            value = task.get(field)
            if value is not None and (type(value) is not int or value < 0):
                fail(f"{label}.{field} pitää olla ei-negatiivinen kokonaisluku tai null")
    if len(set(mapped)) != 9 or set(mapped) != set(ROTATION_FEEDS):
        fail("JSON-tehtävät eivät vastaa yksilöllisesti yhdeksää kiertosyötettä")
    watch = state.get("separate_screening_watch")
    if not isinstance(watch, dict): fail("separate_screening_watch puuttuu")
    if watch.get("feed") != FEEDS[-1] or watch.get("cadence") != "daily":
        fail("näytösvahdin feedin ja päivittäisen rytmin pitää olla oikein")
    if not isinstance(watch.get("errors"), list) or not all(isinstance(x, str) for x in watch["errors"]):
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
    queue_path, readme_path = ROOT/"docs/tehtavajono.md", ROOT/"README.md"
    if not queue_path.is_file() or not readme_path.is_file(): fail("README.md tai docs/tehtavajono.md puuttuu")
    queue, readme = queue_path.read_text(encoding="utf-8"), readme_path.read_text(encoding="utf-8")
    entries = re.findall(r"^\s*\d+\.\s+(.+?)\s+—\s+`(feeds/[^ `]+\.xml)`\s*$", queue, re.M)
    if len(entries) != 9: fail(f"tehtäväjonossa pitää olla yhdeksän tehtävää, löytyi {len(entries)}")
    queue_feeds = [feed for _, feed in entries]
    if queue_feeds != ROTATION_FEEDS: fail("tehtäväjonon järjestys tai feed-polut eivät vastaa määritystä")
    match = re.search(r"\*\*Vuorossa seuraavaksi:\s*(.+?)\.\*\*", queue)
    if not match: fail("tehtäväjonon seuraavaa vuoroa ei löydy")
    task = state["rotation"]["tasks"][state["rotation"]["next_task"]]
    expected = entries[queue_feeds.index(task["feed"])][0]
    if match.group(1).strip() != expected:
        fail(f"tehtäväjonon seuraava vuoro ({match.group(1).strip()}) ei vastaa JSON-tilaa ({expected})")
    readme_feeds = set(re.findall(r"\]\((feeds/[^)]+\.xml)\)", readme))
    if readme_feeds != set(FEEDS):
        fail(f"README:n feed-taulukko ei vastaa kymmentä feed-tiedostoa: puuttuu {sorted(set(FEEDS)-readme_feeds)}")
    if "yhdeksän" not in readme.lower() or "ei kuluta" not in readme.lower():
        fail("README ei kuvaa yhdeksän aiheen kiertoa ja erillistä näytösvahtia")
    if "ei kuulu tähän jonoon" not in queue.lower():
        fail("tehtäväjono ei kuvaa näytösseurannan erillisyyttä")
    for name, feed in entries:
        state_task = next((item for item in state["rotation"]["tasks"].values()
                           if item["feed"] == feed), None)
        if state_task is None or state_task["name"] != name:
            fail(f"JSON-tehtävän nimi ei vastaa tehtäväjonoa: {name}")
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
    for feed in FEEDS:
        if not (ROOT/feed).is_file(): fail(f"RSS-syöte puuttuu: {feed}")

def validate_feeds():
    seen, total = {}, 0
    for relative in FEEDS:
        path = ROOT/relative
        if not path.is_file(): fail(f"RSS-tiedosto puuttuu: {relative}")
        raw = path.read_text(encoding="utf-8")
        try: root = ET.fromstring(raw)
        except ET.ParseError as exc: fail(f"{relative}: XML ei jäsenny: {exc}")
        if root.tag != "rss" or root.find("channel") is None: fail(f"{relative}: rss/channel puuttuu")
        channel = root.find("channel")
        raw_items = re.findall(r"<item\b[\s\S]*?</item\s*>", raw, re.I)
        items = channel.findall("item")
        if len(raw_items) != len(items): fail(f"{relative}: item-lukumäärä ei täsmää")
        for number, (item, raw_item) in enumerate(zip(items, raw_items), 1):
            label = f"{relative}, item {number}"
            if item.find("link") is not None: fail(f"{label}: item-link on kielletty")
            guid = (item.findtext("guid") or "").strip()
            if not guid: fail(f"{label}: GUID puuttuu")
            if guid in seen: fail(f"{label}: GUID {guid!r} on jo tiedostossa {seen[guid]}")
            seen[guid] = relative
            description = item.findtext("description") or ""
            if not description.strip(): fail(f"{label}: description puuttuu")
            match = re.search(r"<description\b[^>]*>([\s\S]*?)</description\s*>", raw_item, re.I)
            if not match or "<![CDATA[" not in match.group(1): fail(f"{label}: description ei ole CDATA-alueessa")
            if not re.search(r"lähdeluettelo|<h[1-6][^>]*>\s*lähteet\s*</h[1-6]>", description, re.I):
                fail(f"{label}: lähdeluettelon otsikko puuttuu")
            parser = HTMLCheck(label)
            try: parser.feed(description); parser.close()
            except Exception as exc: fail(f"{label}: HTML:n käsittely epäonnistui: {exc}")
            if parser.errors: fail(f"{label}: kuvaus-HTML: " + "; ".join(parser.errors[:5]))
            if parser.links == 0: fail(f"{label}: kuvauksessa ei ole linkkejä")
            total += 1
    return total, len(seen)

def main():
    state = validate_state()
    validate_docs(state)
    total, unique = validate_feeds()
    print(f"OK: {len(FEEDS)} syötettä, {total} itemiä, {unique} yksilöllistä GUIDia.")
    print("OK: kuvausten HTML-rakenne, linkit, otsikkotasot, alt-attribuutit ja lähdeluettelot.")
    print("OK: README, tehtäväjono, feed-polut ja seurantatila ovat yhdenmukaiset.")
    print("OK: aikaleimat, seurantajaksot ja erillinen näytösvahti.")

if __name__ == "__main__":
    main()
