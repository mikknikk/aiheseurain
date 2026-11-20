"""Validoi yhden moduulin ChatGPT-tuloksen GitHub-vastaanoton.

Skripti lukee vain nimetyn tulos-JSONin, yhteisen tulosskeeman ja moduulirekisterin.
Se ei julkaise RSS:ää, muuta moduulitilaa tai käynnistä muita aiheajoja.
PR-työnkulku suorittaa tämän main-haaran luotetun version väliaikaiselle tiedostolle.
"""
from __future__ import annotations
import argparse
from datetime import datetime
import json
from pathlib import Path
import re
import sys
from typing import Any
import jsonschema

ROOT = Path(__file__).resolve().parents[1]
INBOX_PATTERN = re.compile(
    r"^data/chatgpt-inbox/(?P<module>[a-z0-9][a-z0-9-]*)/"
    r"(?P<run>[A-Za-z0-9][A-Za-z0-9._:-]{2,127})\.json$"
)

class InboxValidationError(ValueError):
    """Vastaanotettavan tuloksen validointivirhe."""

def read_json(path: Path) -> dict[str, Any]:
    """Lue UTF-8 JSON-olio ja hylkää virheellinen tai vääräntyyppinen tiedosto."""
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise InboxValidationError(f"JSON-tiedostoa ei voi lukea: {path.name}") from exc
    if not isinstance(value, dict):
        raise InboxValidationError("Tuloksen ylimmän tason pitää olla JSON-olio.")
    return value

def aware_timestamp(value: str, field: str) -> datetime:
    """Vaadi ISO 8601 -aikaleima, jossa on aikavyöhyke."""
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, TypeError, ValueError) as exc:
        raise InboxValidationError(f"{field} ei ole kelvollinen ISO 8601 -aikaleima.") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise InboxValidationError(f"{field} tarvitsee aikavyöhykkeen.")
    return parsed

def validate_inbox_result(file_path: Path, *, relative_path: str, root: Path = ROOT) -> dict[str, Any]:
    """Tarkista polku, skeema, moduulin omistajuus ja handoff-tunnisteiden vastaavuus."""
    root = Path(root).resolve()
    match = INBOX_PATTERN.fullmatch(relative_path)
    if not match:
        raise InboxValidationError("Polun pitää olla data/chatgpt-inbox/{module_id}/{run_id}.json.")
    payload = read_json(Path(file_path))
    try:
        schema = read_json(root / "schemas/chatgpt-module-result.schema.json")
        registry = read_json(root / "data/module-registry.json")
        jsonschema.Draft202012Validator.check_schema(schema)
        jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker()).validate(payload)
    except jsonschema.SchemaError as exc:
        raise InboxValidationError(f"Tulosskeema on virheellinen: {exc.message}") from exc
    except jsonschema.ValidationError as exc:
        raise InboxValidationError(f"Tulos ei vastaa sopimusta: {exc.message}") from exc

    module_id, run_id = match.group("module"), match.group("run")
    if payload["module_id"] != module_id or payload["run_id"] != run_id:
        raise InboxValidationError("JSON-tuloksen moduuli- tai run_id ei vastaa tiedostopolkua.")
    matches = [item for item in registry.get("modules", []) if item.get("module_id") == module_id]
    if len(matches) != 1:
        raise InboxValidationError("Moduulia ei löydy rekisteristä yksikäsitteisesti.")
    module = matches[0]
    if module.get("module_type") != "topic":
        raise InboxValidationError("Vastaanottokanava hyväksyy vain topic-moduuleja.")
    if payload["module_definition_version"] != module.get("definition_version"):
        raise InboxValidationError("Tuloksen moduuliversio ei vastaa rekisteriä.")
    if payload["contract_version"] != registry.get("contract_version"):
        raise InboxValidationError("Tuloksen sopimusversio ei vastaa moduulirekisteriä.")

    handoff = payload["handoff"]
    for field in ("module_id", "module_definition_version", "contract_version", "run_id", "period"):
        if handoff[field] != payload[field]:
            raise InboxValidationError(f"Handoffin {field} ei vastaa tutkimustulosta.")
    requested_at = aware_timestamp(handoff["requested_at"], "handoff.requested_at")
    if aware_timestamp(payload["checked_at"], "checked_at") < requested_at:
        raise InboxValidationError("Tarkistusajankohta edeltää handoff-pyyntöä.")
    if payload["status"] == "succeeded" and not payload["source_scan_complete"]:
        raise InboxValidationError("Onnistunut tutkimus edellyttää täydellistä lähdetarkistusta.")
    if "target_reports" in payload and "report_content" in payload:
        raise InboxValidationError("Tuloksessa käytetään joko moduuliraporttia tai kohderaportteja.")
    for report in payload.get("target_reports", []):
        if report["period"] != payload["period"]:
            raise InboxValidationError("Kohderaportin seurantajakso poikkeaa handoffista.")
        if aware_timestamp(report["checked_at"], "target_report.checked_at") < requested_at:
            raise InboxValidationError("Kohderaportin tarkistusajankohta edeltää handoff-pyyntöä.")
    # Estä saman run_id:n toinen, sisällöltään erilainen vastaanotto. Sama jo
    # hyväksytty tiedosto ja täsmälleen sama JSON ovat turvallinen idempotentti uusinta.
    inbox = root / "data/chatgpt-inbox"
    if inbox.exists():
        for existing_path in inbox.glob("*/*.json"):
            if existing_path.resolve() == Path(file_path).resolve():
                continue
            existing_payload = read_json(existing_path)
            if existing_payload.get("run_id") == run_id:
                if (
                    existing_path.relative_to(root).as_posix() == relative_path
                    and existing_payload == payload
                ):
                    return payload
                raise InboxValidationError("Sama run_id on jo vastaanotettu eri sisällöllä tai eri moduulille.")
    # input_sha256:n muoto tarkistetaan skeemassa. Sen riippumaton vertailu
    # alkuperäiseen, pysyvästi tallennettuun handoffiin kuuluu seuraavaan vaiheeseen.
    return payload

def validate_all(root: Path = ROOT) -> int:
    """Validoi kaikki päähaaraan jo hyväksytyt tulokset."""
    inbox = Path(root) / "data/chatgpt-inbox"
    paths = sorted(inbox.glob("*/*.json")) if inbox.exists() else []
    for path in paths:
        validate_inbox_result(path, relative_path=path.relative_to(root).as_posix(), root=root)
    return len(paths)

def main(argv: list[str] | None = None) -> int:
    """Tarjoa PR- ja päähaaran validointiin sama komentorivikäyttöliittymä."""
    parser = argparse.ArgumentParser(description="Validoi Aiheseuraimen ChatGPT-tuloksen vastaanotto.")
    parser.add_argument("--file", type=Path, help="Validoitava JSON-tiedosto.")
    parser.add_argument("--relative-path", help="Tuloksen suunniteltu polku repositoriossa.")
    parser.add_argument("--all", action="store_true", help="Validoi kaikki tallennetut tulokset.")
    parser.add_argument("--root", type=Path, default=ROOT, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    try:
        if args.all and not args.file and not args.relative_path:
            count = validate_all(args.root)
            print(f"ChatGPT-tulosten vastaanotto validoitu: {count} tiedostoa.")
        elif args.file and args.relative_path and not args.all:
            validate_inbox_result(args.file, relative_path=args.relative_path, root=args.root)
            print(f"ChatGPT-tulos hyväksytty rakenteellisesti: {args.relative_path}")
        else:
            raise InboxValidationError("Anna joko --all tai sekä --file että --relative-path.")
    except (InboxValidationError, OSError, ValueError) as exc:
        print(f"ChatGPT-tuloksen validointi epäonnistui: {exc}", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
