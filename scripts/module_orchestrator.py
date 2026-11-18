"""Yhteinen moduulien suoritusorkestrointi ja varjotila.

Orkestrointi koordinoi sopimuksia ja portteja, mutta ei sisällä aihekohtaista
hakulogiikkaa. Tuotantokirjoitukset vaativat aktiivisen moduulin, erillisen
käyttöönottohyväksynnän ja idempotentit julkaisu-/tallennusportit.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import json
from pathlib import Path
import re
from typing import Any, Protocol, Callable
import jsonschema

from scripts.module_registry import load_registry, RegistryResult, ModuleResult
from scripts.module_state import commit_successful_checkpoint, validate_module_state, StateConflictError
from scripts.event_watch import load_event_type, empty_state, reconcile

ROOT = Path(__file__).resolve().parents[1]
REQUEST_SCHEMA = ROOT / "schemas/module-run-request.schema.json"
RESULT_SCHEMA = ROOT / "schemas/module-run-result.schema.json"


class OrchestrationError(RuntimeError):
    """Virhe yhteisen moduuliajon elinkaaressa."""
    code = "orchestration_error"


class ProductionActivationRequired(OrchestrationError):
    """Tuotantokäyttöä ei ole erikseen hyväksytty."""
    code = "production_activation_required"


class ModuleInactiveError(OrchestrationError):
    """Passiivista moduulia ei saa suorittaa tuotantotilassa."""
    code = "module_inactive"


class OrchestrationConflict(OrchestrationError):
    """Tallennusversion tai ajon idempotenssin ristiriita."""
    code = "state_conflict"


@dataclass(frozen=True)
class ModuleRunRequest:
    """Yhteinen suorituspyyntö kaikille moduulityypeille."""
    module_id: str
    module_definition_version: str
    contract_version: str
    run_id: str
    period_start: str
    period_end: str
    mode: str
    requested_at: str
    schema_version: int = 1

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version, "module_id": self.module_id,
            "module_definition_version": self.module_definition_version,
            "contract_version": self.contract_version, "run_id": self.run_id,
            "period": {"start": self.period_start, "end": self.period_end},
            "mode": self.mode, "requested_at": self.requested_at
        }


@dataclass(frozen=True)
class TargetReport:
    """Yhden seurantakohteen raportti ennen julkaisukanavan ratkaisemista."""
    target_id: str
    target_version: str
    observation_types: tuple[str, ...]
    period_start: str
    period_end: str
    checked_at: str
    report_content: str

    def to_dict(self) -> dict[str, Any]:
        """Palauta kohderaportin skeeman mukainen koneellinen esitys."""
        return {
            "report_schema_version": 1, "target_id": self.target_id,
            "target_version": self.target_version,
            "observation_types": list(self.observation_types),
            "period": {"start": self.period_start, "end": self.period_end},
            "checked_at": self.checked_at, "report_content": self.report_content,
        }

    def to_publication_dict(self) -> dict[str, Any]:
        """Rajaa julkaisureitittimelle vain sen tarvitsemat tiedot."""
        return {
            "target_id": self.target_id,
            "observation_types": list(self.observation_types),
            "report_content": self.report_content,
        }


@dataclass(frozen=True)
class ModuleExecutionOutput:
    """Suorittajan normalisoitu tulos ilman teknistä julkaisuvastuuta."""
    status: str
    source_scan_complete: bool
    checked_at: str
    period_start: str
    period_end: str
    report_content: str
    published_items: int | None = None
    sources_checked: int | None = None
    source_check_run_refs: tuple[str, ...] = ()
    report_guid_refs: tuple[str, ...] = ()
    artifacts: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None
    target_reports: tuple[TargetReport, ...] = ()


@dataclass(frozen=True)
class QualityGateResult:
    """Yhteisen laadunvarmistusportin tulos."""
    passed: bool
    errors: tuple[str, ...] = ()


@dataclass(frozen=True)
class PublicationReceipt:
    """Julkaisupalvelun idempotentti kuittaus ja takaisinlukutulos."""
    verified: bool
    report_guid_refs: tuple[str, ...]
    published_items: int


@dataclass(frozen=True)
class ShadowComparison:
    """Vanhan ja uuden käsittelyn jäljitettävä vertailutulos."""
    equivalent: bool | None
    summary: str


@dataclass(frozen=True)
class ModuleRunResult:
    """Yhden moduuliajon koneellisesti validoitava jälki."""
    module_id: str
    module_type: str
    module_definition_version: str
    contract_version: str
    run_id: str
    period_start: str
    period_end: str
    mode: str
    status: str
    phase: str
    started_at: str
    finished_at: str
    source_scan_complete: bool = False
    quality_passed: bool | None = None
    published: bool = False
    checkpoint_updated: bool = False
    comparison: dict[str, Any] | None = None
    error_code: str | None = None
    schema_version: int = 1

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version":self.schema_version,"module_id":self.module_id,"module_type":self.module_type,
            "module_definition_version":self.module_definition_version,"contract_version":self.contract_version,
            "run_id":self.run_id,"period":{"start":self.period_start,"end":self.period_end},
            "mode":self.mode,"status":self.status,"phase":self.phase,"started_at":self.started_at,
            "finished_at":self.finished_at,"source_scan_complete":self.source_scan_complete,
            "quality_passed":self.quality_passed,"published":self.published,
            "checkpoint_updated":self.checkpoint_updated,"comparison":self.comparison,"error_code":self.error_code
        }


class ModuleExecutor(Protocol):
    def execute(self, definition: dict[str, Any], request: ModuleRunRequest, provider_router: Any) -> ModuleExecutionOutput: ...


class QualityGate(Protocol):
    def validate(self, definition: dict[str, Any], request: ModuleRunRequest, output: ModuleExecutionOutput) -> QualityGateResult: ...


class ModuleStateStore(Protocol):
    def load(self, module_id: str) -> tuple[dict[str, Any], str]: ...
    def save(self, module_id: str, state: dict[str, Any], *, expected_sha: str) -> str: ...


class ArtifactStore(Protocol):
    def load_version(self, module_id: str) -> str: ...
    def commit(self, module_id: str, run_id: str, artifacts: dict[str, Any], *, expected_version: str) -> str: ...


class Publisher(Protocol):
    def publish(self, module_id: str, run_id: str, report_content: str, *, idempotency_key: str) -> PublicationReceipt: ...
    def verify(self, receipt: PublicationReceipt) -> bool: ...


class ShadowComparator(Protocol):
    def compare(self, definition: dict[str, Any], request: ModuleRunRequest, output: ModuleExecutionOutput) -> ShadowComparison: ...


class RunRecorder(Protocol):
    def record(self, result: ModuleRunResult) -> None: ...


class EventObservationProvider(Protocol):
    def collect(self, definition: dict[str, Any], request: ModuleRunRequest, provider_router: Any) -> "ObservationBatch": ...


class EventWatchModuleExecutor:
    """Suorittaa minkä tahansa moduulin ilmoittaman tapahtumatyypin samalla ytimellä."""

    def __init__(self, observation_provider: EventObservationProvider,
                 state_loader: Callable[[str, str], dict[str, Any]] | None = None):
        self.observation_provider = observation_provider
        self.state_loader = state_loader or (lambda module_id, event_type_id: empty_state(event_type_id))

    def execute(self, definition: dict[str, Any], request: ModuleRunRequest, provider_router: Any) -> ModuleExecutionOutput:
        extension = definition.get("process_extension", {})
        configuration = extension.get("configuration", {})
        relative = configuration.get("event_type_ref")
        if not isinstance(relative, str):
            raise OrchestrationError("Prosessimoduulilta puuttuu tapahtumatyypin paikallinen viite.")
        event_path = (ROOT / relative).resolve()
        if not event_path.is_relative_to(ROOT.resolve()) or not event_path.is_file():
            raise OrchestrationError("Tapahtumatyypin viite poistuu repositoriosta tai tiedostoa ei löydy.")
        event_type = load_event_type(event_path)
        batch = self.observation_provider.collect(definition, request, provider_router)
        if not isinstance(batch, ObservationBatch):
            raise OrchestrationError("Tapahtumahavaintojen lähde palautti virheellisen tuloksen.")
        observed_at = batch.observed_at or request.requested_at
        state = self.state_loader(definition["module_id"], event_type["event_type_id"])
        updated = reconcile(
            state, list(batch.observations), event_type, observed_at,
            scan_complete=batch.complete,
            failed_sources=list(batch.failed_sources)
        )
        complete = batch.complete
        report = {
            "event_type_id":event_type["event_type_id"],
            "new_history_events":len(updated["events"])-len(state["events"]),
            "current_event_count":len(updated["current_events"]),
            "scan_complete":complete
        }
        return ModuleExecutionOutput(
            status="succeeded" if complete else "partial", source_scan_complete=complete,
            checked_at=observed_at, period_start=request.period_start, period_end=request.period_end,
            report_content=json.dumps(report,ensure_ascii=False,sort_keys=True),
            published_items=None, sources_checked=batch.sources_checked,
            source_check_run_refs=batch.source_check_run_refs,
            artifacts={"event_state":updated},
            metadata={"event_type_id":event_type["event_type_id"]}
        )


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _validate_timestamp(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z","+00:00"))
    except (AttributeError,TypeError,ValueError) as exc:
        raise OrchestrationError("Aikaleima ei ole kelvollinen ISO 8601 -arvo.") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise OrchestrationError("Aikaleimasta puuttuu aikavyöhyke.")
    return parsed


def validate_run_request(request: ModuleRunRequest) -> None:
    """Validoi suorituspyyntö ja sen aikajakso."""
    schema=json.loads(REQUEST_SCHEMA.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(schema)
    errors=sorted(jsonschema.Draft202012Validator(schema,format_checker=jsonschema.FormatChecker()).iter_errors(request.to_dict()),key=lambda item:list(item.path))
    if errors:
        raise OrchestrationError(f"Suorituspyynnön sopimusvirhe: {errors[0].message}")
    if _validate_timestamp(request.period_start) > _validate_timestamp(request.period_end):
        raise OrchestrationError("Seurantajakson alku on loppua myöhempi.")
    _validate_timestamp(request.requested_at)


def validate_run_result(result: ModuleRunResult) -> None:
    """Validoi orkestroinnin palauttama jäljitettävä tulos."""
    schema=json.loads(RESULT_SCHEMA.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(schema)
    errors=sorted(jsonschema.Draft202012Validator(schema,format_checker=jsonschema.FormatChecker()).iter_errors(result.to_dict()),key=lambda item:list(item.path))
    if errors:
        raise OrchestrationError(f"Suoritustuloksen sopimusvirhe: {errors[0].message}")


class ModuleOrchestrator:
    """Koordinoi moduulin elinkaaren; varjotila ei koskaan kirjoita tai julkaise."""

    def __init__(self, *, executor: ModuleExecutor, quality_gate: QualityGate,
                 provider_router: Any = None, state_store: ModuleStateStore | None = None,
                 artifact_store: ArtifactStore | None = None, publisher: Publisher | None = None,
                 comparator: ShadowComparator | None = None, recorder: RunRecorder | None = None,
                 registry_loader: Callable[..., RegistryResult] = load_registry):
        self.executor=executor
        self.quality_gate=quality_gate
        self.provider_router=provider_router
        self.state_store=state_store
        self.artifact_store=artifact_store
        self.publisher=publisher
        self.comparator=comparator
        self.recorder=recorder
        self.registry_loader=registry_loader
        self.run_records: list[ModuleRunResult]=[]

    def _module(self, module_id: str) -> ModuleResult:
        registry=self.registry_loader(include_inactive=True)
        item=next((module for module in registry.modules if module.module_id==module_id),None)
        if item is None:
            raise OrchestrationError(f"Moduulia {module_id} ei löydy rekisteristä.")
        if item.status=="invalid":
            raise OrchestrationError(f"Moduuli {module_id} on virheellinen: {item.error}")
        if item.definition is None:
            raise OrchestrationError(f"Moduulin {module_id} määritystä ei voitu ladata.")
        return item

    def _result(self, request: ModuleRunRequest, module_type: str, started: str, *,
                status: str, phase: str, source_scan_complete: bool=False,
                quality_passed: bool | None=None, published: bool=False,
                checkpoint_updated: bool=False, comparison: ShadowComparison | None=None,
                error_code: str | None=None) -> ModuleRunResult:
        # Virheellisestä pyynnöstäkin muodostetaan turvallinen, skeeman mukainen
        # virhetulos. Alkuperäinen virhe kuvataan error_code-kentässä.
        version_pattern = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")
        safe_mode = request.mode if request.mode in {"shadow","production"} else "shadow"
        fallback_time = "1970-01-01T00:00:00+00:00"
        try:
            safe_period_start = request.period_start
            _validate_timestamp(safe_period_start)
        except Exception:
            safe_period_start = fallback_time
        try:
            safe_period_end = request.period_end
            _validate_timestamp(safe_period_end)
        except Exception:
            safe_period_end = safe_period_start
        if _validate_timestamp(safe_period_end) < _validate_timestamp(safe_period_start):
            safe_period_end = safe_period_start
        result=ModuleRunResult(
            module_id=request.module_id if isinstance(request.module_id,str) and request.module_id else "unknown-module",
            module_type=module_type if module_type in {"topic","process"} else "topic",
            module_definition_version=request.module_definition_version if isinstance(request.module_definition_version,str) and version_pattern.fullmatch(request.module_definition_version) else "0.0.0",
            contract_version=request.contract_version if isinstance(request.contract_version,str) and version_pattern.fullmatch(request.contract_version) else "0.0.0",
            run_id=request.run_id if isinstance(request.run_id,str) and len(request.run_id)>=3 else "invalid-run",
            period_start=safe_period_start,period_end=safe_period_end,mode=safe_mode,
            status=status,phase=phase,started_at=started,finished_at=_now(),
            source_scan_complete=source_scan_complete,quality_passed=quality_passed,
            published=published,checkpoint_updated=checkpoint_updated,
            comparison=({"equivalent":comparison.equivalent,"summary":comparison.summary} if comparison else None),
            error_code=error_code
        )
        validate_run_result(result)
        self.run_records.append(result)
        if self.recorder is not None:
            self.recorder.record(result)
        return result

    def run(self, request: ModuleRunRequest, *, production_authorized: bool=False) -> ModuleRunResult:
        """Suorita yksi moduuli eristettynä; kaikki virheet palautuvat ajokohtaisina tuloksina."""
        started=_now()
        phase="request_validation"
        module_type="topic"
        try:
            validate_run_request(request)
            phase="module_resolution"
            module=self._module(request.module_id)
            definition=module.definition
            module_type=definition["module_type"]
            if definition["definition_version"] != request.module_definition_version:
                raise OrchestrationError("Suorituspyynnön moduulimäärityksen versio ei vastaa rekisteriä.")
            if definition["contract_version"] != request.contract_version:
                raise OrchestrationError("Suorituspyynnön sopimusversio ei vastaa moduulimääritystä.")
            if request.mode=="production":
                if not production_authorized:
                    raise ProductionActivationRequired("Tuotantokäyttö vaatii erillisen hyväksynnän.")
                if module.status!="active":
                    raise ModuleInactiveError("Passiivista moduulia ei voi suorittaa tuotantotilassa.")
                if any(item is None for item in (self.state_store,self.artifact_store,self.publisher)):
                    raise OrchestrationError("Tuotantoajon tallennus- ja julkaisupalvelut puuttuvat.")
                state,state_sha=self.state_store.load(request.module_id)
                validate_module_state(state,definition)
                artifact_version=self.artifact_store.load_version(request.module_id)
            else:
                state=None
                state_sha=None
                artifact_version=None

            phase="execution"
            output=self.executor.execute(definition,request,self.provider_router)
            if not isinstance(output,ModuleExecutionOutput):
                raise OrchestrationError("Moduulisuorittaja palautti tuntemattoman tulossopimuksen.")
            _validate_timestamp(output.checked_at)
            if output.period_start!=request.period_start or output.period_end!=request.period_end:
                raise OrchestrationError("Suorittajan seurantajakso poikkeaa suorituspyynnöstä.")
            if output.status not in {"succeeded","partial","failed"}:
                raise OrchestrationError("Suorittajan tulostila on tuntematon.")

            phase="quality_gate"
            quality=self.quality_gate.validate(definition,request,output)
            if not isinstance(quality,QualityGateResult):
                raise OrchestrationError("Laadunvarmistusportti palautti tuntemattoman tulossopimuksen.")
            if not quality.passed:
                return self._result(request,module_type,started,status="failed",phase=phase,
                                    source_scan_complete=output.source_scan_complete,
                                    quality_passed=False,error_code="quality_gate_rejected")
            if output.status!="succeeded" or not output.source_scan_complete:
                comparison=self.comparator.compare(definition,request,output) if request.mode=="shadow" and self.comparator else None
                return self._result(request,module_type,started,status="partial" if output.status!="failed" else "failed",
                                    phase="shadow_comparison" if request.mode=="shadow" else phase,
                                    source_scan_complete=output.source_scan_complete,quality_passed=True,
                                    comparison=comparison,error_code="incomplete_source_scan")

            if request.mode=="shadow":
                phase="shadow_comparison"
                comparison=self.comparator.compare(definition,request,output) if self.comparator else None
                return self._result(request,module_type,started,status="succeeded",phase=phase,
                                    source_scan_complete=True,quality_passed=True,comparison=comparison)

            phase="publication"
            target_reports = (
                [item.to_publication_dict() for item in output.target_reports]
                if output.target_reports else (output.metadata or {}).get("target_reports")
            )
            if target_reports is not None:
                routed_publish = getattr(self.publisher, "publish_target_reports", None)
                if not callable(routed_publish):
                    raise OrchestrationError(
                        "Kohdekohtaiset raportit vaativat reititetyn julkaisusovittimen."
                    )
                receipt = routed_publish(request.module_id, request.run_id, target_reports)
            else:
                # Vanha moduulikohtainen julkaisupolku säilyy yhteensopivana.
                receipt=self.publisher.publish(
                    request.module_id,request.run_id,output.report_content,
                    idempotency_key=f"{request.module_id}:{request.run_id}"
                )
            if not self.publisher.verify(receipt) or not receipt.verified:
                return self._result(request,module_type,started,status="failed",phase=phase,
                                    source_scan_complete=True,quality_passed=True,error_code="publication_unverified")

            phase="artifact_persistence"
            self.artifact_store.commit(
                request.module_id,request.run_id,output.artifacts or {},
                expected_version=artifact_version
            )

            phase="checkpoint"
            updated=commit_successful_checkpoint(
                state,run_id=request.run_id,definition_version=request.module_definition_version,
                checked_at=output.checked_at,period_start=request.period_start,period_end=request.period_end,
                run_status="succeeded",source_scan_complete=True,publication_verified=True,
                published_items=receipt.published_items,sources_checked=output.sources_checked,
                source_check_run_refs=list(output.source_check_run_refs),
                report_guid_refs=list(receipt.report_guid_refs),
                expected_previous_run_id=state["checkpoint"]["last_successful_run"]["run_id"],
                expected_previous_checked_at=state["checkpoint"]["last_successful_run"]["checked_at"],
                recorded_on=output.checked_at[:10]
            )
            self.state_store.save(request.module_id,updated,expected_sha=state_sha)
            return self._result(request,module_type,started,status="succeeded",phase="complete",
                                source_scan_complete=True,quality_passed=True,published=True,
                                checkpoint_updated=True)
        except ProductionActivationRequired as exc:
            return self._result(request,module_type,started,status="rejected",phase=phase,error_code=exc.code)
        except ModuleInactiveError as exc:
            return self._result(request,module_type,started,status="rejected",phase=phase,error_code=exc.code)
        except Exception as exc:
            code=getattr(exc,"code", "state_conflict" if isinstance(exc,StateConflictError) else type(exc).__name__)
            published=phase in {"artifact_persistence","checkpoint"}
            return self._result(request,module_type,started,status="partial" if published else "failed",
                                phase=phase,published=published,error_code=str(code))

    def run_many(self, requests: list[ModuleRunRequest], *, production_authorized: bool=False) -> list[ModuleRunResult]:
        """Aja moduulit erikseen ja eristä yhden moduulin virhe muista."""
        results=[]
        for request in requests:
            results.append(self.run(request,production_authorized=production_authorized))
        return results


@dataclass(frozen=True)
class ObservationBatch:
    """Yhden tapahtumatyypin lähdehaun normalisoitu erä."""
    observations: tuple[dict[str, Any], ...]
    complete: bool
    failed_sources: tuple[str, ...] = ()
    sources_checked: int | None = None
    source_check_run_refs: tuple[str, ...] = ()
    observed_at: str | None = None


