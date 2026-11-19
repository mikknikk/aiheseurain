"""ChatGPT-tulosten rakenteellinen laadunvarmistus moduulirekisteriä vasten."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import jsonschema

from scripts.module_orchestrator import (
    ModuleExecutionOutput, ModuleRunRequest, QualityGateResult,
)
from scripts.target_execution import load_module_targets, TargetExecutionError

ROOT = Path(__file__).resolve().parents[1]
ASSESSMENT_SCHEMA = ROOT / "schemas/chatgpt-publication-assessment.schema.json"
SENSITIVE_KEYS = {
    "api_key", "access_token", "authorization", "credential", "credentials",
    "password", "secret", "token", "report_content", "source_snippet",
    "snippet", "prompt", "request_content",
}


def _sensitive_field(value: Any) -> bool:
    """Etsi artefakteista salaisuuksia tai raporttitekstiä sisältäviä avainkenttiä."""
    if isinstance(value, dict):
        return any(key.lower() in SENSITIVE_KEYS or _sensitive_field(child)
                   for key, child in value.items())
    if isinstance(value, list):
        return any(_sensitive_field(child) for child in value)
    return False


class ChatGPTResultQualityGate:
    """Tarkista kohderaporttien omistajuus ja toimituksellinen portti.

    Lähteiden määrälle ei aseteta vähimmäisrajaa: täydellisyys ja luotettavuus
    arvioidaan moduulin tutkimusehtojen ja lähdeaineiston perusteella.
    """

    def __init__(self, *, root: Path = ROOT):
        self.root = Path(root).resolve()

    def _assessment_errors(self, assessment: Any, *, required: bool) -> list[str]:
        """Validoi julkaisuarvio ilman raportti- tai lähdesisällön kopiointia virheisiin."""
        if assessment is None:
            return ["publication_assessment_missing"] if required else []
        try:
            schema = json.loads(ASSESSMENT_SCHEMA.read_text(encoding="utf-8"))
            jsonschema.Draft202012Validator.check_schema(schema)
            jsonschema.Draft202012Validator(
                schema, format_checker=jsonschema.FormatChecker()
            ).validate(assessment)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError, jsonschema.SchemaError):
            return ["publication_assessment_schema_unavailable"]
        except jsonschema.ValidationError:
            return ["publication_assessment_invalid"]

        errors = []
        if assessment["decision"] != "approved":
            errors.append("publication_assessment_rejected")
        checklist = assessment["checklist"]
        for key, value in checklist.items():
            if value["status"] == "fail":
                errors.append(f"publication_check_failed:{key}")
        for key in ("guid_preservation", "xml_html", "rss_structure"):
            if checklist[key]["status"] != "pass":
                errors.append(f"publication_automated_check_not_passed:{key}")
        return errors

    def validate(
        self, definition: dict[str, Any], request: ModuleRunRequest,
        output: ModuleExecutionOutput,
    ) -> QualityGateResult:
        """Tarkista yksi moduuli ja vain sen rekisteröidyt kohderaportit."""
        errors: list[str] = []
        try:
            targets = load_module_targets(
                definition, root=self.root, require_active=request.mode == "production"
            )
        except (TargetExecutionError, OSError, ValueError):
            return QualityGateResult(False, ("module_targets_invalid",))
        target_by_id = {item["target_id"]: item for item in targets}

        if output.status not in {"succeeded", "partial", "failed"}:
            errors.append("result_status_invalid")
        if output.status == "succeeded" and not output.source_scan_complete:
            errors.append("successful_result_scan_incomplete")
        if output.sources_checked is not None and output.sources_checked < 0:
            errors.append("sources_checked_negative")
        if len(output.source_check_run_refs) != len(set(output.source_check_run_refs)):
            errors.append("source_check_refs_duplicate")
        if len(output.report_guid_refs) != len(set(output.report_guid_refs)):
            errors.append("report_guid_refs_duplicate")
        if output.artifacts is not None and not isinstance(output.artifacts, dict):
            errors.append("artifacts_not_object")
        elif _sensitive_field(output.artifacts or {}):
            errors.append("artifacts_contain_restricted_fields")
        if output.metadata is not None and not isinstance(output.metadata, dict):
            errors.append("metadata_not_object")

        if targets:
            if not output.target_reports:
                errors.append("target_reports_missing")
            seen = set()
            for report in output.target_reports:
                if report.target_id in seen:
                    errors.append("target_report_duplicate")
                    continue
                seen.add(report.target_id)
                target = target_by_id.get(report.target_id)
                if target is None:
                    errors.append("target_report_not_owned")
                    continue
                if report.target_version != target["target_version"]:
                    errors.append("target_report_version_mismatch")
                if not report.observation_types or len(report.observation_types) != len(set(report.observation_types)):
                    errors.append("target_report_observation_types_invalid")
                if (report.period_start != request.period_start
                        or report.period_end != request.period_end):
                    errors.append("target_report_period_mismatch")
                if not isinstance(report.report_content, str) or not report.report_content.strip():
                    errors.append("target_report_content_missing")
                try:
                    from scripts.chatgpt_module_result import _timestamp
                    if _timestamp(report.checked_at, "target_report.checked_at") < _timestamp(
                        request.requested_at, "requested_at"
                    ):
                        errors.append("target_report_checked_before_request")
                except ValueError:
                    errors.append("target_report_checked_at_invalid")
            if output.status == "succeeded" and seen != set(target_by_id):
                errors.append("successful_result_missing_target_reports")
        elif not isinstance(output.report_content, str) or not output.report_content.strip():
            errors.append("module_report_content_missing")

        metadata = output.metadata or {}
        assessment = metadata.get("publication_assessment") if isinstance(metadata, dict) else None
        errors.extend(self._assessment_errors(
            assessment, required=request.mode == "production"
        ))
        return QualityGateResult(not errors, tuple(errors))
