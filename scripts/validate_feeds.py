#!/usr/bin/env python3
"""Validate the repository's RSS feeds and publication conventions."""
from __future__ import annotations
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FEEDS = [
    "feeds/tolkien.xml", "feeds/taylor-swift.xml",
    "feeds/gurmeet-ram-rahim-singh.xml", "feeds/muumit.xml",
    "feeds/wakaliwood.xml", "feeds/euroviisut.xml",
    "feeds/sompote-sands.xml", "feeds/shakkidraamat.xml",
    "feeds/intialaiset-elokuvat.xml",
    "feeds/intialaisten-elokuvien-naytokset.xml",
]

def fail(message: str) -> None:
    print(f"VIRHE: {message}", file=sys.stderr)
    raise SystemExit(1)

def main() -> None:
    seen: dict[str, str] = {}
    total = 0
    for relative in FEEDS:
        path = ROOT / relative
        if not path.is_file():
            fail(f"RSS-tiedosto puuttuu: {relative}")
        raw = path.read_text(encoding="utf-8")
        try:
            root = ET.fromstring(raw)
        except ET.ParseError as exc:
            fail(f"{relative}: XML ei jäsenny: {exc}")
        if root.tag != "rss" or root.find("channel") is None:
            fail(f"{relative}: odotettu rss/channel-rakenne puuttuu")
        channel = root.find("channel")
        raw_items = re.findall(r"<item\b[\s\S]*?</item\s*>", raw, re.I)
        items = channel.findall("item")
        if len(raw_items) != len(items):
            fail(f"{relative}: item-lukumäärä ei täsmää")
        for number, (item, raw_item) in enumerate(zip(items, raw_items), 1):
            label = f"{relative}, item {number}"
            if item.find("link") is not None:
                fail(f"{label}: item-kohtainen link-elementti on kielletty")
            guid = (item.findtext("guid") or "").strip()
            if not guid:
                fail(f"{label}: GUID puuttuu")
            if guid in seen:
                fail(f"{label}: GUID {guid!r} on jo tiedostossa {seen[guid]}")
            seen[guid] = relative
            description = item.findtext("description") or ""
            if not description.strip():
                fail(f"{label}: description puuttuu")
            match = re.search(r"<description\b[^>]*>([\s\S]*?)</description\s*>", raw_item, re.I)
            if not match or "<![CDATA[" not in match.group(1):
                fail(f"{label}: description ei ole CDATA-alueessa")
            if not re.search(r"lähdeluettelo|<h[1-6][^>]*>\s*lähteet\s*</h[1-6]>", description, re.I):
                fail(f"{label}: lähdeluettelon otsikko puuttuu")
            if not re.search(r"<a\b[^>]*href\s*=", description, re.I):
                fail(f"{label}: lähdelinkkejä ei löydy descriptionista")
            total += 1

    state_path = ROOT / "data/seurantatila.json"
    if state_path.exists():
        try:
            state = json.loads(state_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            fail(f"seurantatilan JSON ei jäsenny: {exc}")
        tasks = state.get("rotation", {}).get("tasks", {})
        if state.get("schema_version") != 1 or state.get("rotation", {}).get("next_task") not in tasks:
            fail("seurantatilan schema_version tai next_task on virheellinen")
        if len(tasks) != 9:
            fail("seurantatilassa pitää olla täsmälleen yhdeksän kiertotehtävää")
        if "separate_screening_watch" not in state:
            fail("erillisen näytösvahdin tila puuttuu")
    print(f"OK: {len(FEEDS)} RSS-syötettä, {total} itemiä, {len(seen)} yksilöllistä GUIDia.")
    print("OK: XML, CDATA-descriptionit, item-linkkien kielto ja lähdeluettelot tarkistettu.")

if __name__ == "__main__":
    main()
