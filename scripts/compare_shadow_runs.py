"""Vertaa vanhaa raporttia ja uutta ChatGPT-moduulitulosta ilman kirjoituksia."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import uuid
from typing import Any

import jsonschema

from scripts.module_registry import load_registry

ROOT = Path(__file__).resolve().parents[1]
INPUT_SCHEMA = ROOT / "schemas/shadow-comparison-input.schema.json"
RESULT_SCHEMA = ROOT / "schemas/chatgpt-module-result.schema.json"
REPORT_SCHEMA = ROOT / "schemas/shadow-comparison-report.schema.json"


class ShadowComparisonError(ValueError):
    """Varjotilan vertailusyötteen tai vertailun sopimusvirhe."""


def _read_json(path: Path) -> dict[str, Any]:
    """Lue vertailutiedosto ilman, että sitä muutetaan."""
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ShadowComparisonError("Vertailutiedoston lukeminen epäonnistui.") from exc
    if not isinstance(value, dict):
        raise ShadowComparisonError("Vertailutiedoston juuren pitää olla JSON-olio.")
    return value


def _validate(value: dict[str, Any], schema_path: Path, label: str) -> None:
    """Tarkista JSON-skeema ja muotoile virhe käyttäjälle turvallisesti."""
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator.check_schema(schema)
        jsonschema.Draft202012Validator(
            schema, format_checker=jsonschema.FormatChecker()
        ).validate(value)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, jsonschema.SchemaError) as exc:
        raise ShadowComparisonError(f"{label}: skeeman lukeminen epäonnistui.") from exc
    except jsonschema.ValidationError as exc:
        raise ShadowComparisonError(f"{label}: rakenne ei vastaa sopimusta ({exc.message}).") from exc


def _instant(value: str) -> datetime:
    """Muunna aikavyöhykkeellinen ISO-aikaleima vertailukelpoiseksi UTC-ajaksi."""
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, TypeError, ValueError) as exc:
        raise ShadowComparisonError("Seurantajakson aikaleima ei ole kelvollinen.") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ShadowComparisonError("Seurantajakson aikaleimasta puuttuu aikavyöhyke.")
    return parsed.astimezone(timezone.utc)


def _period_matches(first: dict[str, str], second: dict[str, str]) -> bool:
    """Vertaa jaksoja ajanhetkinä, ei pelkkinä aikavyöhykkeen sisältävinä merkkijonoina."""
    return (
        _instant(first["start"]) == _instant(second["start"])
        and _instant(first["end"]) == _instant(second["end"])
    )


def _module_report_content(result: dict[str, Any]) -> str:
    """Yhdistä kohderaportit vertailua varten säilyttäen niiden rekisterijärjestyksen."""
    if isinstance(result.get("report_content"), str):
        return result["report_content"]
    reports = result.get("target_reports", [])
    return "\n\n".join(
        item["report_content"] for item in reports
        if isinstance(item, dict) and isinstance(item.get("report_content"), str)
    )


def _claim_key(value: str) -> str:
    """Normalisoi vain välilyönnit ja kirjainkoon; ei väitä semanttista vastaavuutta."""
    return re.sub(r"\s+", " ", value).strip().casefold()


def _word_count(value: str) -> int:
    """Laske raportin sanat kuvailevaa vertailutietoa varten."""
    return len(re.findall(r"\w+", value, flags=re.UNICODE))


def _module_guid_is_valid(guid: str, module_id: str) -> bool:
    """Varmista uuden GUID-käytännön aihe-, päiväys- ja UUID-osat."""
    prefix = f"urn:aiheseurain:{module_id}:"
    if not guid.startswith(prefix):
        return False
    try:
        date_part, uuid_part = guid[len(prefix):].split(":", 1)
        datetime.strptime(date_part, "%Y-%m-%d")
        return str(uuid.UUID(uuid_part)) == uuid_part.lower()
    except (ValueError, AttributeError):
        return False


def _module_definition(module_id: str, root: Path) -> dict[str, Any]:
    """Varmista, että vertailun uusi tulos kuuluu rekisteröidylle topic-moduulille."""
    registry = load_registry(root=root, include_inactive=True)
    module = next((item for item in registry.modules if item.module_id == module_id), None)
    if module is None or module.definition is None:
        raise ShadowComparisonError("Vertailun moduulia ei löydy rekisteristä.")
    if module.definition.get("module_type") != "topic":
        raise ShadowComparisonError("Varjovertaillun moduulin pitää olla topic-moduuli.")
    return module.definition


def _publication_readiness(result: dict[str, Any]) -> tuple[bool, list[str], dict[str, str | None]]:
    """Arvioi rakenteellisen julkaisukelpoisuuden; ei julkaise eikä korvaa RSS-validointia."""
    blockers: list[str] = []
    assessment = (result.get("metadata") or {}).get("publication_assessment")
    if result.get("status") != "succeeded":
        blockers.append(f"result_status:{result.get('status', 'missing')}")
    if not result.get("source_scan_complete", False):
        blockers.append("source_scan_incomplete")
    if not isinstance(assessment, dict):
        blockers.append("publication_assessment_missing")
        return False, blockers, {}
    if assessment.get("decision") != "approved":
        blockers.append("publication_assessment_not_approved")
    checklist = assessment.get("checklist", {})
    automated = {}
    for key in ("guid_preservation", "xml_html", "rss_structure"):
        status = checklist.get(key, {}).get("status")
        automated[key] = status
        if status != "pass":
            blockers.append(f"automated_check_not_passed:{key}")
    for key, value in checklist.items():
        if isinstance(value, dict) and value.get("status") == "fail":
            blockers.append(f"check_failed:{key}")
    if not result.get("report_content") and not result.get("target_reports"):
        blockers.append("report_content_missing")
    if not result.get("report_guid_refs"):
        blockers.append("report_guid_refs_missing")
    return not blockers, sorted(set(blockers)), automated


def compare_shadow_runs(data: dict[str, Any], *, root: Path = ROOT) -> dict[str, Any]:
    """Vertaa saman aiheen ja jakson vanhaa raporttia sekä uutta moduulitulosta."""
    root = Path(root).resolve()
    _validate(data, root / INPUT_SCHEMA.relative_to(ROOT), "Vertailusyöte")
    legacy = data["legacy"]
    module = data["module_result"]
    _validate(module, root / RESULT_SCHEMA.relative_to(ROOT), "ChatGPT-moduulitulos")

    module_id = legacy["module_id"]
    if module["module_id"] != module_id:
        raise ShadowComparisonError("Vanhan ja uuden ajon moduulitunnisteet eroavat.")
    if not _period_matches(legacy["period"], module["period"]):
        raise ShadowComparisonError("Vanhan ja uuden ajon seurantajaksot eroavat.")

    definition = _module_definition(module_id, root)
    if module["module_definition_version"] != definition["definition_version"]:
        raise ShadowComparisonError("Uuden tuloksen moduuliversio ei vastaa rekisteriä.")
    if module["contract_version"] != definition["contract_version"]:
        raise ShadowComparisonError("Uuden tuloksen sopimusversio ei vastaa moduulimääritystä.")
    handoff = module["handoff"]
    for field, expected in (
        ("module_id", module_id),
        ("module_definition_version", module["module_definition_version"]),
        ("contract_version", module["contract_version"]),
        ("run_id", module["run_id"]),
        ("period", module["period"]),
    ):
        if handoff.get(field) != expected:
            raise ShadowComparisonError(f"Uuden tuloksen handoff-kenttä {field} ei vastaa tulosta.")
    registered_sources = {
        item["source_id"] for item in definition.get("source_refs", [])
        if isinstance(item, dict) and isinstance(item.get("source_id"), str)
    }
    source_audit = (module.get("metadata") or {}).get("source_audit")
    if not isinstance(source_audit, dict):
        raise ShadowComparisonError("Uudesta tuloksesta puuttuu rakenteinen source_audit.")
    source_checks = source_audit.get("source_checks", [])
    module_source_ids = [item["source_id"] for item in source_checks]
    if len(module_source_ids) != len(set(module_source_ids)):
        raise ShadowComparisonError("Uuden tuloksen source_audit sisältää lähteen useammin kuin kerran.")
    if any(source_id not in registered_sources for source_id in module_source_ids):
        raise ShadowComparisonError("Uuden tuloksen source_audit sisältää toisen moduulin tai tuntemattoman lähteen.")

    legacy_checks = legacy["source_checks"]
    legacy_ids_in_order = [item["source_id"] for item in legacy_checks]
    if len(legacy_ids_in_order) != len(set(legacy_ids_in_order)):
        raise ShadowComparisonError("Vanhan ajon lähdetarkistus sisältää lähteen useammin kuin kerran.")
    legacy_source_ids = sorted(set(legacy_ids_in_order))
    module_source_ids = sorted(module_source_ids)
    legacy_set, module_set = set(legacy_source_ids), set(module_source_ids)

    legacy_content = legacy.get("report_content", "")
    module_content = _module_report_content(module)
    legacy_claims = legacy.get("claims", [])
    assessment = (module.get("metadata") or {}).get("publication_assessment", {})
    module_claims = [
        item["claim"] for item in assessment.get("claim_assessments", [])
        if isinstance(item, dict) and isinstance(item.get("claim"), str)
    ]
    legacy_claim_map = {_claim_key(item): item for item in legacy_claims}
    module_claim_map = {_claim_key(item): item for item in module_claims}

    legacy_guids = legacy.get("guid_refs", [])
    module_guids = module.get("report_guid_refs", [])
    uncertainty = assessment.get("checklist", {}).get("uncertainty", {})
    module_ready, blockers, automated = _publication_readiness(module)
    module_guid_valid = bool(module_guids) and all(
        _module_guid_is_valid(guid, module_id) for guid in module_guids
    )
    if module.get("target_reports"):
        feed_catalog = _read_json(root / "data/feed-catalog.json")
        feed_matches = [
            item for item in feed_catalog.get("feeds", [])
            if item.get("id") == module_id and item.get("type") == "topic"
        ]
        if len(feed_matches) != 1:
            raise ShadowComparisonError("Moduulille ei löydy yksikäsitteistä topic-syötettä GUID-tarkistusta varten.")
        feed_id = module_id
        expected_guids = []
        for report in module["target_reports"]:
            checked_date = datetime.fromisoformat(
                report["checked_at"].replace("Z", "+00:00")
            ).date().isoformat()
            stable_id = uuid.uuid5(
                uuid.NAMESPACE_URL,
                f"aiheseurain:{module_id}:{module['run_id']}:{report['target_id']}",
            )
            expected_guids.append(
                f"urn:aiheseurain:{feed_id}:{checked_date}:{stable_id}"
            )
        if module_guids != expected_guids:
            module_guid_valid = False
    if not module_guid_valid and "module_guid_format_invalid" not in blockers:
        blockers.append("module_guid_format_invalid")
        module_ready = False
    if len(module_guids) != len(set(module_guids)):
        blockers.append("module_guid_duplicate")
        module_ready = False
    audited_count = sum(item["status"] != "skipped" for item in source_checks)
    if module.get("sources_checked") is not None and module["sources_checked"] != audited_count:
        blockers.append("source_audit_count_mismatch")
        module_ready = False

    output = {
        "schema_version": 1,
        "comparison_id": data["comparison_id"],
        "module_id": module_id,
        "run_ids": {"legacy": legacy["run_id"], "module": module["run_id"]},
        "period": legacy["period"],
        "period_match": True,
        "statuses": {"legacy": legacy["status"], "module": module["status"]},
        "source_comparison": {
            "legacy_source_ids": legacy_source_ids,
            "module_source_ids": module_source_ids,
            "shared_source_ids": sorted(legacy_set & module_set),
            "legacy_only_source_ids": sorted(legacy_set - module_set),
            "module_only_source_ids": sorted(module_set - legacy_set),
            "legacy_statuses": {item["source_id"]: item["status"] for item in legacy_checks},
            "module_statuses": {item["source_id"]: item["status"] for item in source_checks},
        },
        "report_comparison": {
            "legacy_sha256": hashlib.sha256(legacy_content.encode("utf-8")).hexdigest() if legacy_content else None,
            "module_sha256": hashlib.sha256(module_content.encode("utf-8")).hexdigest() if module_content else None,
            "exact_match": bool(legacy_content) and legacy_content == module_content,
            "legacy_word_count": _word_count(legacy_content),
            "module_word_count": _word_count(module_content),
            "legacy_only_claims": [legacy_claim_map[key] for key in sorted(legacy_claim_map.keys() - module_claim_map.keys())],
            "module_only_claims": [module_claim_map[key] for key in sorted(module_claim_map.keys() - legacy_claim_map.keys())],
            "shared_claims": [legacy_claim_map[key] for key in sorted(legacy_claim_map.keys() & module_claim_map.keys())],
        },
        "guid_comparison": {
            "legacy_guid_refs": legacy_guids,
            "module_guid_refs": module_guids,
            "legacy_unique": len(legacy_guids) == len(set(legacy_guids)),
            "module_unique": len(module_guids) == len(set(module_guids)),
            "module_format_valid": module_guid_valid,
            "shared_guid_refs": sorted(set(legacy_guids) & set(module_guids)),
        },
        "uncertainty_comparison": {
            "legacy_notes": legacy.get("uncertainty_notes", []),
            "module_status": uncertainty.get("status"),
            "module_note": uncertainty.get("note"),
            "module_claim_verification_statuses": sorted({
                item.get("verification_status", "")
                for item in assessment.get("claim_assessments", [])
                if isinstance(item, dict)
            }),
            "module_documented": isinstance(uncertainty.get("note"), str) and bool(uncertainty["note"].strip()),
        },
        "publication_readiness": {
            "legacy_ready": legacy["publication_ready"],
            "module_ready": module_ready,
            "module_blockers": sorted(set(blockers)),
            "automated_checks": automated,
        },
        "side_effects": {
            "production_writes": False,
            "rss_written": False,
            "checkpoint_updated": False,
            "rotation_advanced": False,
            "files_written": [],
        },
    }
    _validate(output, root / REPORT_SCHEMA.relative_to(ROOT), "Vertailuraportti")
    return output


def main(argv: list[str] | None = None) -> int:
    """Tulosta vertailu JSON-muodossa; komento ei tarjoa tiedostoon kirjoittavaa valitsinta."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Vertaa vanhaa ja uutta ajotulosta kirjoituksettomasti.")
    parser.add_argument("--input", type=Path, required=True, help="Rajattu vertailusyöte JSON-tiedostona.")
    args = parser.parse_args(argv)
    try:
        output = compare_shadow_runs(_read_json(args.input))
    except (ShadowComparisonError, OSError, ValueError) as exc:
        print(f"Varjotilan vertailu epäonnistui: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
