"""Yhteinen, kohdekohtaisesti eristetty suorituskehys moduulisuorittajille.

Kehys ei hae tietoa itse. Se antaa moduulin omalle hakurunnerille yhden
seurantakohteen määrityksen kerrallaan ja kokoaa onnistuneet tulokset
TargetReport-arvoiksi. Jokainen kohde saa oman syväkopionsa ja muuttumattoman
suoritusympäristön; virhe ei saa vuotaa seuraavan kohteen käsittelyyn.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping, Protocol

import jsonschema

from scripts.module_orchestrator import (
    ModuleExecutionOutput, ModuleRunRequest, TargetReport,
)

ROOT = Path(__file__).resolve().parents[1]


class TargetExecutionError(ValueError):
    """Seurantakohteen rekisteri- tai suoritusympäristön sopimusvirhe."""


@dataclass(frozen=True)
class TargetExecutionContext:
    """Yhden kohteen itsenäinen suoritusympäristö moduulin hakurunnerille."""
    module_id: str
    run_id: str
    target_id: str
    target_version: str
    period_start: str
    period_end: str
    requested_at: str
    target_definition: Mapping[str, Any]
    search_profiles: tuple[Mapping[str, Any], ...]


@dataclass(frozen=True)
class TargetExecutionResult:
    """Yhden kohteen runnerin normalisoitu tulos."""
    status: str
    source_scan_complete: bool
    checked_at: str
    observation_types: tuple[str, ...]
    report_content: str
    sources_checked: int | None = None
    source_check_run_refs: tuple[str, ...] = ()
    artifacts: dict[str, Any] | None = None


class TargetRunner(Protocol):
    """Moduulin aihekohtainen toteutus käsittelee vain sille annetun kohteen."""
    def execute(
        self, context: TargetExecutionContext, provider_router: Any
    ) -> TargetExecutionResult: ...


def _freeze(value: Any) -> Any:
    """Muunna JSON-rakenne rekursiivisesti vain luku -muotoon."""
    if isinstance(value, dict):
        return MappingProxyType({key: _freeze(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    return value


def _read_json(path: Path) -> dict[str, Any]:
    """Lue JSON-olio ja anna polun sisältävä selkeä sopimusvirhe."""
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise TargetExecutionError(f"JSON-tiedoston lukeminen epäonnistui: {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise TargetExecutionError(f"JSON-tiedoston ylimmän tason arvon pitää olla olio: {path}")
    return value


def _validate(value: dict[str, Any], schema_path: Path, label: str) -> None:
    """Validoi rekisteri tai kohdemääritys sen omalla skeemalla."""
    schema = _read_json(schema_path)
    jsonschema.Draft202012Validator.check_schema(schema)
    errors = sorted(
        jsonschema.Draft202012Validator(
            schema, format_checker=jsonschema.FormatChecker()
        ).iter_errors(value),
        key=lambda item: list(item.path),
    )
    if errors:
        first = errors[0]
        raise TargetExecutionError(
            f"{label} ei vastaa skeemaa kohdassa {list(first.path)}: {first.message}"
        )


def load_module_targets(
    definition: dict[str, Any], *, root: Path = ROOT
) -> tuple[dict[str, Any], ...]:
    """Ratkaise moduulin target_refs-viitteet rekisterin kautta ja tarkista omistajuus."""
    root = Path(root).resolve()
    module_id = definition.get("module_id")
    module_version = definition.get("definition_version")
    refs = definition.get("target_refs")
    if not isinstance(module_id, str) or not module_id:
        raise TargetExecutionError("Moduulin tunniste puuttuu.")
    if not isinstance(refs, list) or not refs:
        raise TargetExecutionError(f"Moduulilla {module_id} ei ole seurantakohdeviitteitä.")
    if any(not isinstance(item, str) or not item for item in refs):
        raise TargetExecutionError("Moduulin seurantakohdeviitteissä on virheellinen tunniste.")
    if len(refs) != len(set(refs)):
        raise TargetExecutionError("Moduulin seurantakohdeviitteissä on duplikaatti.")

    registry = _read_json(root / "data/target-registry.json")
    _validate(registry, root / "schemas/seurantakohderekisteri.schema.json", "Seurantakohderekisteri")
    entries = {item["target_id"]: item for item in registry["targets"]}
    missing = [target_id for target_id in refs if target_id not in entries]
    if missing:
        raise TargetExecutionError("Tuntemattomat seurantakohteet: " + ", ".join(missing))

    targets = []
    for target_id in refs:
        entry = entries[target_id]
        target_path = (root / entry["path"]).resolve()
        if not target_path.is_relative_to(root) or not target_path.is_file():
            raise TargetExecutionError(f"Seurantakohteen tiedostoviite on virheellinen: {target_id}")
        target = _read_json(target_path)
        _validate(target, root / "schemas/seurantakohde.schema.json", f"Seurantakohde {target_id}")
        if target.get("target_id") != target_id:
            raise TargetExecutionError(f"Seurantakohteen tunniste ei vastaa rekisteriä: {target_id}")
        owner = target.get("module_ref", {})
        if owner.get("module_id") != module_id:
            raise TargetExecutionError(f"Seurantakohteen moduuliomistaja on väärä: {target_id}")
        if owner.get("definition_version") != module_version:
            raise TargetExecutionError(f"Seurantakohteen moduuliversio ei vastaa moduulia: {target_id}")
        targets.append(target)
    return tuple(targets)


def _timestamp(value: str) -> datetime:
    """Vaadi aikavyöhykkeellinen ISO 8601 -aikaleima."""
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, TypeError, ValueError) as exc:
        raise TargetExecutionError(f"Virheellinen tarkistusajankohta: {value!r}") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise TargetExecutionError("Tarkistusajankohdasta puuttuu aikavyöhyke.")
    return parsed


class TargetExecutionCoordinator:
    """Aja moduulin kohteet erillisinä ja kokoa onnistuneet raportit."""

    def __init__(self, target_loader=load_module_targets):
        self.target_loader = target_loader

    def execute(
        self, definition: dict[str, Any], request: ModuleRunRequest,
        provider_router: Any, runner: TargetRunner,
    ) -> ModuleExecutionOutput:
        """Suorita runner kerran kutakin seurantakohdetta kohti eristetyssä kontekstissa."""
        targets = self.target_loader(definition)
        reports: list[TargetReport] = []
        failures: dict[str, str] = {}
        source_counts: list[int] = []
        source_refs: list[str] = []
        artifacts: dict[str, Any] = {}
        checked_times: list[datetime] = []

        for target in targets:
            target_id = target["target_id"]
            # Jokainen kohde saa oman kopion. Runnerin muutos ei vaikuta rekisteriin
            # eikä seuraavan kohteen suoritusympäristöön.
            isolated = deepcopy(target)
            context = TargetExecutionContext(
                module_id=request.module_id, run_id=request.run_id,
                target_id=target_id, target_version=target["target_version"],
                period_start=request.period_start, period_end=request.period_end,
                requested_at=request.requested_at,
                target_definition=_freeze(isolated),
                search_profiles=tuple(_freeze(item) for item in isolated["search_profiles"]),
            )
            try:
                result = runner.execute(context, provider_router)
                if not isinstance(result, TargetExecutionResult):
                    raise TargetExecutionError("Kohderunner palautti tuntemattoman tulossopimuksen.")
                if result.status != "succeeded" or not result.source_scan_complete:
                    raise TargetExecutionError("Kohdehaku ei valmistunut kokonaan.")
                checked = _timestamp(result.checked_at)
                if checked < _timestamp(request.requested_at):
                    raise TargetExecutionError("Kohteen tarkistusajankohta edeltää suorituspyyntöä.")
                if not result.observation_types or any(
                    not isinstance(item, str) or not item.strip()
                    for item in result.observation_types
                ):
                    raise TargetExecutionError("Kohderaportilta puuttuu kelvollinen havaintotyyppi.")
                if not isinstance(result.report_content, str) or not result.report_content.strip():
                    raise TargetExecutionError("Kohderaportin sisältö puuttuu.")
                if result.sources_checked is not None and result.sources_checked < 0:
                    raise TargetExecutionError("Lähteiden määrä ei voi olla negatiivinen.")
                if len(result.source_check_run_refs) != len(set(result.source_check_run_refs)):
                    raise TargetExecutionError("Lähdetarkistusviitteissä on duplikaatti.")

                reports.append(TargetReport(
                    target_id=target_id, target_version=target["target_version"],
                    observation_types=tuple(result.observation_types),
                    period_start=request.period_start, period_end=request.period_end,
                    checked_at=result.checked_at, report_content=result.report_content,
                ))
                checked_times.append(checked)
                if result.sources_checked is not None:
                    source_counts.append(result.sources_checked)
                source_refs.extend(result.source_check_run_refs)
                if result.artifacts is not None:
                    artifacts[target_id] = deepcopy(result.artifacts)
            except Exception as exc:
                # Älä kopioi poikkeusviestiä raporttiin tai auditointitietoon.
                failures[target_id] = getattr(exc, "code", type(exc).__name__)

        checked_at = max(checked_times).isoformat() if checked_times else request.requested_at
        complete = not failures and len(reports) == len(targets)
        status = "succeeded" if complete else ("partial" if reports else "failed")
        metadata = {
            "target_count": len(targets),
            "successful_target_ids": [item.target_id for item in reports],
            "failed_targets": failures,
        }
        return ModuleExecutionOutput(
            status=status, source_scan_complete=complete,
            checked_at=checked_at, period_start=request.period_start,
            period_end=request.period_end, report_content="",
            sources_checked=sum(source_counts) if source_counts else None,
            source_check_run_refs=tuple(sorted(set(source_refs))),
            artifacts={"target_artifacts": artifacts} if artifacts else None,
            metadata=metadata, target_reports=tuple(reports),
        )
