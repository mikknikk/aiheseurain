"""Paikalliset, eristetyt tallennus- ja julkaisusovittimet moduuliorchestratorille.

Sovittimet on tarkoitettu testaukseen ja varjotilan kehitykseen. Ne eivät kirjoita
repositorion tuotannon moduulitiloihin tai RSS-syötteisiin, ellei kutsuja erikseen
anna kyseisiä polkuja. Tuotannon GitHub-sovittimet ovat erillinen toteutus.
"""
from __future__ import annotations

from copy import deepcopy
from contextlib import contextmanager
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
from typing import Any
import xml.etree.ElementTree as ET

from scripts.module_state import validate_module_state, StateConflictError
from scripts.module_orchestrator import (
    ModuleRunResult, QualityGateResult, PublicationReceipt,
)


ROOT = Path(__file__).resolve().parents[1]


MODULE_ID_PATTERN = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
SENSITIVE_KEYS = {
    "api_key", "access_token", "authorization", "credential", "credentials",
    "password", "secret", "token", "report_content", "source_snippet",
    "snippet", "prompt", "request_content",
}


class AdapterError(RuntimeError):
    """Paikallisen sovittimen yleinen virhe."""


class AdapterConflictError(AdapterError):
    """Odotettu tallennusversio tai idempotenssitunniste ei täsmää."""


def _canonical(value: Any) -> bytes:
    """Muunna JSON-arvo vakaaksi tavujonoksi hajautusta ja vertailua varten."""
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def _digest(content: bytes) -> str:
    """Palauta sisällön SHA-256-tunniste."""
    return hashlib.sha256(content).hexdigest()


def _safe_module_id(module_id: str) -> str:
    """Estä moduulitunnisteen käyttäminen polkuhyökkäyksenä."""
    if not isinstance(module_id, str) or not MODULE_ID_PATTERN.fullmatch(module_id):
        raise AdapterError("Moduulitunniste ei ole turvallinen tiedostonimeksi.")
    return module_id


def _safe_path(root: Path, relative: str) -> Path:
    """Varmista, että sovittimen polku pysyy sille annetun juuren alla."""
    root = root.resolve()
    candidate = (root / relative).resolve()
    if not candidate.is_relative_to(root):
        raise AdapterError("Sovittimen tiedostopolku poistuu sille annetusta juuresta.")
    return candidate


@contextmanager
def _exclusive_lock(path: Path):
    """Suojaa version tarkistuksen ja kirjoituksen samanaikaisilta prosesseilta."""
    path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = path.with_name(path.name + ".lock")
    with lock_path.open("a+b") as lock_file:
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)


def _atomic_write(path: Path, content: bytes) -> None:
    """Kirjoita tiedosto ensin samaan hakemistoon ja vaihda se atomisesti."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb", dir=path.parent, prefix=f".{path.name}.",
            suffix=".tmp", delete=False
        ) as stream:
            temporary = Path(stream.name)
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


class JsonFileModuleStateStore:
    """Moduulin checkpointin paikallinen SHA-tarkistettu tallennussovitin."""

    def __init__(self, root: Path):
        self.root = Path(root).resolve()

    def _path(self, module_id: str) -> Path:
        module_id = _safe_module_id(module_id)
        return _safe_path(self.root, f"{module_id}.json")

    def load(self, module_id: str) -> tuple[dict[str, Any], str]:
        """Lue validoitu tila ja palauta tiedoston SHA optimistista lukitusta varten."""
        path = self._path(module_id)
        try:
            content = path.read_bytes()
            state = json.loads(content.decode("utf-8"))
        except FileNotFoundError as exc:
            raise AdapterError(f"Moduulin {module_id} tilatiedostoa ei löydy.") from exc
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise AdapterError(f"Moduulin {module_id} tilatiedosto ei ole kelvollista JSONia.") from exc
        validate_module_state(state)
        if state["module_id"] != module_id:
            raise AdapterError("Tilatiedoston moduulitunniste ei vastaa pyydettyä moduulia.")
        return state, _digest(content)

    def save(self, module_id: str, state: dict[str, Any], *, expected_sha: str) -> str:
        """Tallenna tila vain, jos tiedoston nykyinen SHA vastaa odotettua."""
        path = self._path(module_id)
        validate_module_state(state)
        if state["module_id"] != module_id:
            raise AdapterError("Tallennettavan tilan moduulitunniste ei vastaa polkua.")
        with _exclusive_lock(path):
            try:
                current = _digest(path.read_bytes())
            except FileNotFoundError:
                current = "missing"
            if current != expected_sha:
                raise StateConflictError("Moduulitilan SHA muuttui ennen kirjoitusta.")
            content = _canonical(state) + b"\n"
            _atomic_write(path, content)
            return _digest(content)


class JsonFileArtifactStore:
    """Prosessin artefaktien erillinen, versiotarkistettu paikallinen tallennus."""

    def __init__(self, root: Path):
        self.root = Path(root).resolve()

    def _path(self, module_id: str) -> Path:
        module_id = _safe_module_id(module_id)
        return _safe_path(self.root, f"{module_id}.json")

    def _read(self, module_id: str) -> tuple[dict[str, Any], str]:
        path = self._path(module_id)
        try:
            raw = path.read_bytes()
        except FileNotFoundError:
            return {"schema_version": 1, "module_id": module_id, "runs": {}}, "missing"
        try:
            value = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise AdapterError("Artefaktitiedoston JSON on virheellinen.") from exc
        if (not isinstance(value, dict) or value.get("schema_version") != 1
                or value.get("module_id") != module_id or not isinstance(value.get("runs"), dict)):
            raise AdapterError("Artefaktitiedoston rakenne tai moduulitunniste on virheellinen.")
        return value, _digest(raw)

    def load_version(self, module_id: str) -> str:
        """Palauta artefaktitiedoston nykyinen versio tai missing."""
        return self._read(module_id)[1]

    def commit(
        self, module_id: str, run_id: str, artifacts: dict[str, Any],
        *, expected_version: str
    ) -> str:
        """Kirjaa ajon artefaktit idempotentisti odotettua versiota vasten."""
        if not isinstance(run_id, str) or not run_id.strip():
            raise AdapterError("Artefaktin run_id puuttuu.")
        if not isinstance(artifacts, dict):
            raise AdapterError("Artefaktien pitää olla JSON-olio.")
        path = self._path(module_id)
        with _exclusive_lock(path):
            current, version = self._read(module_id)
            if run_id in current["runs"]:
                if _canonical(current["runs"][run_id]) == _canonical(artifacts):
                    return version
                raise AdapterConflictError("Sama run_id sisältää jo eri artefaktit.")
            if version != expected_version:
                raise AdapterConflictError("Artefaktitiedosto muuttui ennen kirjoitusta.")
            updated = deepcopy(current)
            updated["runs"][run_id] = artifacts
            content = _canonical(updated) + b"\n"
            _atomic_write(path, content)
            return _digest(content)


def _audit_record(result: ModuleRunResult) -> dict[str, Any]:
    """Valitse ajotuloksesta vain auditointiin sallitut, ei-sisältöä sisältävät kentät."""
    comparison = result.comparison or {}
    record = {
        "schema_version": 1,
        "module_id": result.module_id,
        "module_type": result.module_type,
        "module_definition_version": result.module_definition_version,
        "contract_version": result.contract_version,
        "run_id": result.run_id,
        "period_start": result.period_start,
        "period_end": result.period_end,
        "mode": result.mode,
        "status": result.status,
        "phase": result.phase,
        "started_at": result.started_at,
        "finished_at": result.finished_at,
        "source_scan_complete": result.source_scan_complete,
        "quality_passed": result.quality_passed,
        "published": result.published,
        "checkpoint_updated": result.checkpoint_updated,
        "comparison_equivalent": comparison.get("equivalent"),
        "error_code": result.error_code,
    }
    return record


def _reject_sensitive_fields(value: Any) -> None:
    """Varmista rekursiivisesti, ettei auditointitallennukseen päädy salaisuuksia."""
    if isinstance(value, dict):
        for key, child in value.items():
            if key.lower() in SENSITIVE_KEYS:
                raise AdapterError(f"Auditointitallennuksessa on kielletty kenttä {key!r}.")
            _reject_sensitive_fields(child)
    elif isinstance(value, list):
        for child in value:
            _reject_sensitive_fields(child)


class JsonlRunRecorder:
    """Append-only-tyyppinen paikallinen ajotulosloki ilman raporttisisältöä."""

    def __init__(self, path: Path):
        self.path = Path(path).resolve()

    def record(self, result: ModuleRunResult) -> None:
        """Kirjaa ajon kerran; sama tunniste ja sama tulos ovat idempotentteja."""
        record = _audit_record(result)
        _reject_sensitive_fields(record)
        key = (record["module_id"], record["run_id"])
        with _exclusive_lock(self.path):
            existing_records = []
            if self.path.exists():
                for line_number, line in enumerate(self.path.read_text(encoding="utf-8").splitlines(), 1):
                    try:
                        existing_records.append(json.loads(line))
                    except json.JSONDecodeError as exc:
                        raise AdapterError(f"Ajotuloslokin rivi {line_number} ei ole kelvollista JSONia.") from exc
            for existing in existing_records:
                if (existing.get("module_id"), existing.get("run_id")) == key:
                    stable_existing = {k: v for k, v in existing.items() if k not in {"started_at", "finished_at"}}
                    stable_record = {k: v for k, v in record.items() if k not in {"started_at", "finished_at"}}
                    if _canonical(stable_existing) == _canonical(stable_record):
                        return
                    raise AdapterConflictError("Sama moduuli/run_id on kirjattu eri ajotuloksella.")
            existing_records.append(record)
            content = b"".join(_canonical(item) + b"\n" for item in existing_records)
            _atomic_write(self.path, content)


class LocalFileRssPublisher:
    """RSS-julkaisusovitin vain eristettyyn testihakemistoon."""

    def __init__(self, root: Path, feed_paths: dict[str, str]):
        self.root = Path(root).resolve()
        self.feed_paths = dict(feed_paths)
        self._expected_content: dict[str, str] = {}

    def _path(self, module_id: str) -> Path:
        _safe_module_id(module_id)
        relative = self.feed_paths.get(module_id)
        if not isinstance(relative, str) or not relative:
            raise AdapterError(f"Moduulille {module_id} ei ole määritelty testisyötettä.")
        return _safe_path(self.root, relative)

    def _load_tree(self, module_id: str) -> ET.Element:
        path = self._path(module_id)
        if not path.exists():
            rss = ET.Element("rss", {"version": "2.0"})
            channel = ET.SubElement(rss, "channel")
            ET.SubElement(channel, "title").text = f"Testisyöte: {module_id}"
            ET.SubElement(channel, "link").text = "https://example.invalid/"
            ET.SubElement(channel, "description").text = "Eristetty orkestroinnin testisyöte"
            return rss
        try:
            return ET.fromstring(path.read_bytes())
        except ET.ParseError as exc:
            raise AdapterError(f"Testisyötteen {module_id} XML on virheellinen.") from exc

    @staticmethod
    def _items(root: ET.Element) -> list[ET.Element]:
        channel = root.find("./channel")
        if root.tag != "rss" or channel is None:
            raise AdapterError("Testisyötteen RSS-rakenne on virheellinen.")
        return list(channel.findall("./item"))

    def publish(
        self, module_id: str, run_id: str, report_content: str,
        *, idempotency_key: str
    ) -> PublicationReceipt:
        """Lisää yhden itemin tai tunnistaa saman ajon aiemman julkaisun."""
        if not isinstance(report_content, str) or not report_content.strip():
            raise AdapterError("Julkaistava raportti on tyhjä.")
        expected_key = f"{module_id}:{run_id}"
        if idempotency_key != expected_key:
            raise AdapterError("Julkaisun idempotenssiavain ei vastaa moduulia ja ajoa.")
        guid = "urn:aiheseurain:run:" + hashlib.sha256(expected_key.encode("utf-8")).hexdigest()
        path = self._path(module_id)
        with _exclusive_lock(path):
            root = self._load_tree(module_id)
            items = self._items(root)
            guids = [(item.findtext("guid") or "").strip() for item in items]
            if len(guids) != len(set(guids)):
                raise AdapterError("Testisyötteessä on duplikaatti-GUID.")
            if guid in guids:
                existing = items[guids.index(guid)]
                if existing.findtext("description") != report_content:
                    raise AdapterConflictError("Saman ajon GUID on jo julkaistu eri sisällöllä.")
            else:
                item = ET.SubElement(root.find("./channel"), "item")
                ET.SubElement(item, "title").text = f"{module_id}: {run_id}"
                ET.SubElement(item, "guid", {"isPermaLink": "false"}).text = guid
                ET.SubElement(item, "description").text = report_content
                self._expected_content[guid] = report_content
                xml = ET.tostring(root, encoding="utf-8", xml_declaration=True)
                _atomic_write(path, xml)
        receipt = PublicationReceipt(
            verified=True, report_guid_refs=(guid,), published_items=1
        )
        if not self.verify(receipt):
            raise AdapterError("Testisyötteen takaisinlukutarkistus epäonnistui.")
        return receipt

    def verify(self, receipt: PublicationReceipt) -> bool:
        """Lue XML takaisin ja tarkista GUIDien yksilöllisyys sekä sisältö."""
        for module_id in self.feed_paths:
            path = self._path(module_id)
            if not path.exists():
                continue
            root = self._load_tree(module_id)
            items = self._items(root)
            guids = [(item.findtext("guid") or "").strip() for item in items]
            if len(guids) != len(set(guids)):
                return False
            for guid in receipt.report_guid_refs:
                if guid in guids:
                    expected = self._expected_content.get(guid)
                    actual = items[guids.index(guid)].findtext("description")
                    if expected is not None and actual != expected:
                        return False
                    break
            else:
                continue
            return True
        return False


class StructuralModuleQualityGate:
    """Orkestroinnin rakenteellinen laadunvarmistussovitin.

    Toimituksellinen väitearviointi ja varsinainen RSS-porttiraportti säilyvät
    omissa hyväksyntäprosesseissaan; tämä sovitin tarkistaa suorittajan tuloksen
    ennen kuin orkestrointi voi kutsua julkaisusovitinta.
    """

    def validate(self, definition: dict[str, Any], request: Any, output: Any) -> QualityGateResult:
        errors = []
        if output.status != "succeeded":
            errors.append("Suorittajan tila ei ole succeeded.")
        if not output.source_scan_complete:
            errors.append("Lähdehaku ei ole täydellinen.")
        target_reports = getattr(output, "target_reports", ()) or ()
        if not target_reports and (not isinstance(output.report_content, str) or not output.report_content.strip()):
            errors.append("Raporttisisältö puuttuu.")
        if output.period_start != request.period_start or output.period_end != request.period_end:
            errors.append("Raportin seurantajakso poikkeaa suorituspyynnöstä.")
        if not isinstance(output.checked_at, str) or not output.checked_at.strip():
            errors.append("Tarkistusajankohta puuttuu.")
        if output.sources_checked is not None and output.sources_checked < 0:
            errors.append("Lähteiden määrä ei voi olla negatiivinen.")
        if len(output.source_check_run_refs) != len(set(output.source_check_run_refs)):
            errors.append("Lähdetarkistusajojen viitteissä on duplikaatti.")

        if target_reports:
            try:
                schema_path = ROOT / "schemas/target-report.schema.json"
                schema = json.loads(schema_path.read_text(encoding="utf-8"))
                jsonschema.Draft202012Validator.check_schema(schema)
                validator = jsonschema.Draft202012Validator(
                    schema, format_checker=jsonschema.FormatChecker()
                )
                target_registry = json.loads(
                    (ROOT / "data/target-registry.json").read_text(encoding="utf-8")
                )
                target_entries = {
                    item["target_id"]: item for item in target_registry.get("targets", [])
                }
                allowed_target_ids = set(definition.get("target_refs", []))
                report_ids = []
                if not isinstance(target_reports, (list, tuple)):
                    errors.append("Kohderaporttien pitää olla lista.")
                    target_reports = ()
                for report in target_reports:
                    if not hasattr(report, "to_dict"):
                        errors.append("Kohderaportin pitää olla TargetReport-tyyppinen arvo.")
                        continue
                    report_value = report.to_dict()
                    schema_errors = sorted(
                        validator.iter_errors(report_value), key=lambda item: list(item.path)
                    )
                    if schema_errors:
                        errors.append(
                            "Kohderaportin skeemavirhe: " + schema_errors[0].message
                        )
                        continue
                    target_id = report.target_id
                    report_ids.append(target_id)
                    if target_id not in allowed_target_ids:
                        errors.append(f"Kohderaportin kohde ei kuulu moduulille: {target_id}")
                        continue
                    entry = target_entries.get(target_id)
                    if entry is None:
                        errors.append(f"Kohderaportin kohdetta ei löydy rekisteristä: {target_id}")
                        continue
                    target_path = (ROOT / entry["path"]).resolve()
                    if not target_path.is_relative_to(ROOT.resolve()) or not target_path.is_file():
                        errors.append(f"Kohderaportin kohdemääritystä ei löydy: {target_id}")
                        continue
                    target = json.loads(target_path.read_text(encoding="utf-8"))
                    target_module_ref = target.get("module_ref", {})
                    if target_module_ref.get("module_id") != definition.get("module_id"):
                        errors.append(f"Kohderaportin moduuliomistaja on väärä: {target_id}")
                    if target_module_ref.get("definition_version") != definition.get("definition_version"):
                        errors.append(f"Kohderaportin moduuliversio ei vastaa kohteen omistajaviitettä: {target_id}")
                    if report.target_version != target.get("target_version"):
                        errors.append(f"Kohderaportin kohdeversio ei vastaa rekisteriä: {target_id}")
                    if report.period_start != request.period_start or report.period_end != request.period_end:
                        errors.append(f"Kohderaportin seurantajakso poikkeaa pyynnöstä: {target_id}")
                    if report.checked_at != output.checked_at:
                        errors.append(f"Kohderaportin tarkistusajankohta poikkeaa ajosta: {target_id}")
                    if not isinstance(report.report_content, str) or not report.report_content.strip():
                        errors.append(f"Kohderaportin sisältö puuttuu: {target_id}")

                    declared_types = definition.get("observation_types")
                    if definition.get("module_type") == "process":
                        event_ref = definition.get("process_extension", {}).get("configuration", {}).get("event_type_ref")
                        if isinstance(event_ref, str):
                            event_path = (ROOT / event_ref).resolve()
                            if event_path.is_relative_to(ROOT.resolve()) and event_path.is_file():
                                event_definition = json.loads(event_path.read_text(encoding="utf-8"))
                                declared_types = [event_definition.get("event_type_id")]
                    if not declared_types:
                        output_type = definition.get("interfaces", {}).get("output", {}).get("id")
                        declared_types = [output_type] if output_type else []
                    if declared_types and not set(report.observation_types).issubset(set(declared_types)):
                        errors.append(f"Kohderaportin havaintotyyppi ei vastaa moduulin sopimusta: {target_id}")
                if len(report_ids) != len(set(report_ids)):
                    errors.append("Suorituksessa on useampi raportti samalle seurantakohteelle.")
            except (OSError, UnicodeDecodeError, json.JSONDecodeError, KeyError, TypeError) as exc:
                errors.append(f"Kohderaporttien rekisteritietojen lukeminen epäonnistui: {exc}")
        return QualityGateResult(passed=not errors, errors=tuple(errors))


class RoutedReportPublisher:
    """Julkaise suoritusorkestroinnin kohdekohtaiset raportit ratkaistuihin RSS-kanaviin.

    Sovitin on opt-in: orkestrointi kutsuu sitä vain, jos suorittajan metadata
    sisältää target_reports-listan. Ilman sitä vanha moduulikohtainen julkaisija
    jatkaa ennallaan. Julkaisukonteksti ja kirjoitusjuuri annetaan eksplisiittisesti.
    """

    def __init__(self, root: Path, context: dict[str, Any]):
        from scripts.publication_routing import LocalRoutedRssPublisher
        self.context = context
        self.publisher = LocalRoutedRssPublisher(root, context)
        self._last_receipt: PublicationReceipt | None = None
        self._last_receipt_details: list[dict[str, Any]] = []

    def publish_target_reports(self, module_id: str, run_id: str,
                               target_reports: list[dict[str, Any]]) -> PublicationReceipt:
        """Reititä ja julkaise yksi raportti kutakin seurantakohdetta kohti."""
        from scripts.publication_routing import (
            PublicationRoutingError, resolve_publication_plan,
        )
        if not isinstance(target_reports, list) or not target_reports:
            raise AdapterError("Kohdekohtaisten raporttien lista puuttuu tai on tyhjä.")
        target_ids = [item.get("target_id") for item in target_reports if isinstance(item, dict)]
        if len(target_ids) != len(target_reports) or len(target_ids) != len(set(target_ids)):
            raise AdapterError("Kohderaporteissa on virheellinen tai toistuva seurantakohde.")
        plans = []
        for item in target_reports:
            if set(item) != {"target_id", "observation_types", "report_content"}:
                raise AdapterError("Kohderaportin kentät eivät vastaa julkaisusopimusta.")
            try:
                plan = resolve_publication_plan(
                    self.context, module_id=module_id, target_id=item["target_id"],
                    run_id=run_id, observation_types=item["observation_types"],
                )
            except PublicationRoutingError as exc:
                raise AdapterError(str(exc)) from exc
            if not isinstance(item["report_content"], str) or not item["report_content"].strip():
                raise AdapterError("Kohdekohtainen raporttisisältö puuttuu.")
            plans.append((plan, item["report_content"]))
        # Reitit ja raporttien sisältö tarkistetaan ennen ensimmäistä kirjoitusta.
        receipts = []
        try:
            for plan, report_content in plans:
                receipts.append(self.publisher.publish_report(plan, report_content))
        except PublicationRoutingError as exc:
            raise AdapterError(str(exc)) from exc
        refs = tuple(
            receipt["guid"] for result in receipts for receipt in result["receipts"]
        )
        combined = PublicationReceipt(
            verified=all(result["verified"] for result in receipts),
            report_guid_refs=refs,
            published_items=sum(result["published_items"] for result in receipts),
        )
        self._last_receipt = combined
        self._last_receipt_details = [item for result in receipts for item in result["receipts"]]
        return combined

    def verify(self, receipt: PublicationReceipt) -> bool:
        """Lue jokainen julkaistu RSS-item takaisin ja tarkista GUID sekä sisältötiiviste."""
        if self._last_receipt != receipt or not receipt.verified:
            return False
        if len(self._last_receipt_details) != receipt.published_items:
            return False
        for expected in self._last_receipt_details:
            try:
                path = self.publisher._path(expected["publication_id"])
                root = ET.fromstring(path.read_bytes())
            except (OSError, ET.ParseError, AdapterError):
                return False
            matches = [
                item for item in root.findall("./channel/item")
                if (item.findtext("guid") or "").strip() == expected["guid"]
            ]
            if len(matches) != 1:
                return False
            content = matches[0].findtext("description") or ""
            if hashlib.sha256(content.encode("utf-8")).hexdigest() != expected["content_sha256"]:
                return False
        return True
