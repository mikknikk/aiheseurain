"""Validoi ChatGPT-automaation tuloksen moduuliorkestroinnin syötteeksi."""
from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
from typing import Any

import jsonschema

from scripts.module_orchestrator import ModuleExecutionOutput, ModuleRunRequest, TargetReport

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas/chatgpt-module-result.schema.json"


class ChatGPTResultError(ValueError):
    """ChatGPT-tuloksen sopimusvirhe."""


def _timestamp(value: str, field: str) -> datetime:
    """Vaadi aikavyöhykkeellinen ISO 8601 -aikaleima."""
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, TypeError, ValueError) as exc:
        raise ChatGPTResultError(f"{field} ei ole kelvollinen ISO 8601 -aikaleima.") from exc
    if result.tzinfo is None or result.utcoffset() is None:
        raise ChatGPTResultError(f"{field} tarvitsee aikavyöhykkeen.")
    return result


def validate_chatgpt_result(
    payload: dict[str, Any], definition: dict[str, Any], request: ModuleRunRequest
) -> None:
    """Tarkista skeema sekä moduuli-, versio-, ajo- ja aikajaksotunnisteet."""
    try:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator.check_schema(schema)
        jsonschema.Draft202012Validator(
            schema, format_checker=jsonschema.FormatChecker()
        ).validate(payload)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, jsonschema.SchemaError) as exc:
        raise ChatGPTResultError(f"Tulossopimuksen lukeminen epäonnistui: {exc}") from exc
    except jsonschema.ValidationError as exc:
        raise ChatGPTResultError(f"ChatGPT-tulos ei vastaa sopimusta: {exc.message}") from exc

    if payload["module_id"] != request.module_id or payload["module_id"] != definition["module_id"]:
        raise ChatGPTResultError("ChatGPT-tuloksen moduulitunniste ei vastaa suorituspyyntöä.")
    if payload["module_definition_version"] != definition["definition_version"]:
        raise ChatGPTResultError("ChatGPT-tuloksen moduuliversio ei vastaa rekisteriä.")
    if payload["contract_version"] != request.contract_version:
        raise ChatGPTResultError("ChatGPT-tuloksen sopimusversio ei vastaa suorituspyyntöä.")
    if payload["run_id"] != request.run_id:
        raise ChatGPTResultError("ChatGPT-tuloksen run_id ei vastaa suorituspyyntöä.")
    if payload["period"]["start"] != request.period_start or payload["period"]["end"] != request.period_end:
        raise ChatGPTResultError("ChatGPT-tuloksen seurantajakso ei vastaa suorituspyyntöä.")
    if _timestamp(payload["checked_at"], "checked_at") < _timestamp(request.requested_at, "requested_at"):
        raise ChatGPTResultError("Tuloksen tarkistusajankohta edeltää suorituspyyntöä.")
    if payload["status"] == "succeeded" and not payload["source_scan_complete"]:
        raise ChatGPTResultError("Onnistunut tulos edellyttää täydellistä lähdetarkistusta.")
    if "target_reports" in payload and "report_content" in payload:
        raise ChatGPTResultError("Tuloksessa käytetään joko moduuliraporttia tai kohderaportteja.")
    for report in payload.get("target_reports", []):
        if report["period"]["start"] != request.period_start or report["period"]["end"] != request.period_end:
            raise ChatGPTResultError("Kohderaportin seurantajakso ei vastaa suorituspyyntöä.")
        if _timestamp(report["checked_at"], "target_report.checked_at") < _timestamp(request.requested_at, "requested_at"):
            raise ChatGPTResultError("Kohderaportin tarkistusajankohta edeltää suorituspyyntöä.")



def chatgpt_result_to_execution_output(
    payload: dict[str, Any], definition: dict[str, Any], request: ModuleRunRequest
) -> ModuleExecutionOutput:
    """Muunna ChatGPT:n JSON-tulos orkestroinnin sisäiseksi tulosolioksi."""
    validate_chatgpt_result(payload, definition, request)
    target_reports = tuple(
        TargetReport(
            target_id=item["target_id"],
            target_version=item["target_version"],
            observation_types=tuple(item["observation_types"]),
            period_start=item["period"]["start"],
            period_end=item["period"]["end"],
            checked_at=item["checked_at"],
            report_content=item["report_content"],
        )
        for item in payload.get("target_reports", [])
    )
    return ModuleExecutionOutput(
        status=payload["status"],
        source_scan_complete=payload["source_scan_complete"],
        checked_at=payload["checked_at"],
        period_start=payload["period"]["start"],
        period_end=payload["period"]["end"],
        report_content=payload.get("report_content", ""),
        sources_checked=payload.get("sources_checked"),
        source_check_run_refs=tuple(payload.get("source_check_run_refs", [])),
        report_guid_refs=tuple(payload.get("report_guid_refs", [])),
        artifacts=payload.get("artifacts"),
        metadata=payload.get("metadata"),
        target_reports=target_reports,
    )


class ChatGPTResultExecutor:
    """ModuleExecutor-sovitin jo suoritetulle ChatGPT-tutkimukselle."""

    def __init__(self, payload: dict[str, Any]):
        self.payload = payload

    def execute(
        self, definition: dict[str, Any], request: ModuleRunRequest, provider_router: Any
    ) -> ModuleExecutionOutput:
        """Palauta validoitu tulos; ulkoista provider-routeria ei käytetä."""
        return chatgpt_result_to_execution_output(self.payload, definition, request)
