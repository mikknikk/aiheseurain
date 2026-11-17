#!/usr/bin/env python3
"""Tarkistaa raporttikohtaisen laadunvarmistusportin ennen RSS-muutoksen PR-yhdistämistä.

Skripti ei arvioi uutisväitteiden totuutta. Se varmistaa, että toimittajan
tarkistuslista on täytetty, kaikki pakolliset toimitukselliset kohdat on
hyväksytty, automaattisesti tarkistettavat RSS-ehdot ovat jo läpäisseet
validate_feeds.py-testin ja vanhat GUIDit säilyvät.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import subprocess
import sys

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas/julkaisuportti.schema.json"
REPORT_DIR = "reports/julkaisuportit"
AUTOMATED_CHECKS = {"guid_preservation", "xml_html", "rss_structure"}
CHECK_IDS = {
    "sources_opened", "claim_support", "source_independence", "uncertainty",
    "dates", "tracking_period", "duplicates", "guid_preservation",
    "xml_html", "rss_structure", "report_completeness", "accessibility",
}


def fail(message: str) -> None:
    """Keskeyttää tarkistuksen virheeseen, jonka GitHub Actions näyttää PR:ssä."""
    print(f"VIRHE: {message}", file=sys.stderr)
    raise SystemExit(1)


def changed_paths(base_ref: str) -> set[str]:
    """Palauttaa PR:n muuttamat polut vertaamalla niitä kohdehaaraan."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", f"origin/{base_ref}...HEAD"],
            cwd=ROOT, check=True, capture_output=True, text=True,
        )
    except subprocess.CalledProcessError as exc:
        fail(f"Git-muutosten selvittäminen epäonnistui: {exc.stderr.strip()}")
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def load_json(path: Path, label: str):
    """Lukee JSON-tiedoston ja ilmoittaa virheestä suoraan."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        fail(f"{label}: JSON-tiedoston lukeminen epäonnistui: {exc}")


def validate_record(path: Path, feed_map: dict[str, str]) -> dict:
    """Tarkistaa yhden raportin tarkistuslomakkeen skeeman ja hyväksynnän."""
    record = load_json(path, str(path.relative_to(ROOT)))
    schema = load_json(SCHEMA_PATH, "julkaisuportin skeema")
    try:
        jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker()).validate(record)
    except jsonschema.ValidationError as exc:
        fail(f"{path.relative_to(ROOT)}: skeemavirhe kohdassa {list(exc.absolute_path)}: {exc.message}")

    if record["task_id"] not in feed_map:
        fail(f"{path.relative_to(ROOT)}: tuntematon task_id {record['task_id']!r}")
    if feed_map[record["task_id"]] != record["feed_path"]:
        fail(f"{path.relative_to(ROOT)}: task_id ja feed_path eivät vastaa toisiaan")

    failed = [
        key for key, value in record["checklist"].items()
        if value["status"] == "fail"
    ]
    not_applicable_without_reason = [
        key for key, value in record["checklist"].items()
        if value["status"] == "not_applicable" and len(value["note"].strip()) < 5
    ]
    if failed:
        fail(f"{path.relative_to(ROOT)}: hylätyt tarkistuskohdat: {', '.join(failed)}")
    if not_applicable_without_reason:
        fail(f"{path.relative_to(ROOT)}: soveltumattomilta kohdilta puuttuu perustelu: {', '.join(not_applicable_without_reason)}")
    if record["decision"] != "approved":
        fail(f"{path.relative_to(ROOT)}: päätös ei ole approved")
    if not record["reviewer_notes"]:
        fail(f"{path.relative_to(ROOT)}: reviewer_notes ei saa olla tyhjä; kirjaa lyhyt yhteenveto")
    for key in AUTOMATED_CHECKS:
        if record["checklist"][key]["status"] != "pass":
            fail(f"{path.relative_to(ROOT)}: automaattisen tarkistuksen {key} on oltava pass")
    return record


def feed_guids(xml_text: str, label: str) -> set[str]:
    """Poimii GUID-arvot XML:stä ja hylkää puuttuvat tai toistuvat tunnisteet."""
    import xml.etree.ElementTree as ET
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as exc:
        fail(f"{label}: XML ei jäsenny: {exc}")
    values = []
    for item in root.findall("./channel/item"):
        value = (item.findtext("guid") or "").strip()
        if not value:
            fail(f"{label}: itemiltä puuttuu GUID")
        values.append(value)
    if len(values) != len(set(values)):
        fail(f"{label}: GUID ei ole yksilöllinen")
    return set(values)


def verify_guid_preservation(feed_path: str, base_ref: str) -> None:
    """Varmistaa, ettei PR poista aiempia GUID-tunnisteita muutetusta syötteestä."""
    try:
        old = subprocess.run(
            ["git", "show", f"origin/{base_ref}:{feed_path}"],
            cwd=ROOT, check=True, capture_output=True, text=True,
        ).stdout
    except subprocess.CalledProcessError as exc:
        fail(f"Vanhan syötteen {feed_path} lukeminen epäonnistui: {exc.stderr.strip()}")
    current_path = ROOT / feed_path
    if not current_path.is_file():
        fail(f"PR poistaa syötetiedoston {feed_path}")
    old_guids = feed_guids(old, f"main/{feed_path}")
    new_guids = feed_guids(current_path.read_text(encoding="utf-8"), feed_path)
    missing = old_guids - new_guids
    if missing:
        fail(f"{feed_path}: vanhoja GUID-tunnisteita poistettu: {', '.join(sorted(missing))}")


def main() -> None:
    """Tarkistaa kaikki PR:ssä muuttuneet RSS-syötteet ja niiden porttiraportit."""
    base_ref = os.environ.get("GITHUB_BASE_REF")
    if not base_ref:
        print("OHITUS: julkaisulaadun portti suoritetaan vain pull request -työnkuluissa.")
        return

    catalog = load_json(ROOT / "data/feed-catalog.json", "syötekatalogi")
    feed_map = {entry["id"]: entry["path"] for entry in catalog["feeds"]}
    changed = changed_paths(base_ref)
    changed_feeds = {path for path in changed if path.startswith("feeds/") and path.endswith(".xml")}
    if not changed_feeds:
        print("OK: PR ei muuta RSS-syötteitä; raporttikohtaista porttia ei tarvita.")
        return

    report_paths = sorted(
        path for path in changed
        if path.startswith(REPORT_DIR + "/") and path.endswith(".json")
    )
    if len(report_paths) != len(changed_feeds):
        fail(
            f"PR muuttaa {len(changed_feeds)} RSS-syötettä, mutta sisältää "
            f"{len(report_paths)} uutta/muutettua julkaisulaadun porttiraporttia. "
            "Jokaisella muuttuneella syötteellä pitää olla oma raportti."
        )

    covered = set()
    for relative in report_paths:
        path = ROOT / relative
        record = validate_record(path, feed_map)
        feed_path = record["feed_path"]
        if feed_path not in changed_feeds:
            fail(f"{relative}: raportin feed_path ei ole PR:ssä muuttunut syöte")
        if feed_path in covered:
            fail(f"{relative}: samalle syötteelle on useampi julkaisulaadun porttiraportti")
        covered.add(feed_path)
        verify_guid_preservation(feed_path, base_ref)

    missing = changed_feeds - covered
    if missing:
        fail("Julkaisuportriraportti puuttuu syötteiltä: " + ", ".join(sorted(missing)))

    print(f"OK: {len(covered)} RSS-syötteen raporttikohtainen julkaisulaadun portti hyväksytty.")
    print("OK: toimitukselliset kohdat hyväksytty, automaattiset RSS-testit läpäisty ja vanhat GUIDit säilytetty.")


if __name__ == "__main__":
    main()
