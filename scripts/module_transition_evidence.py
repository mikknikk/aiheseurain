"""Kerää ja säilyttää moduulisiirtymän ulkoiset todisteet ilman julkaisutoimia.

Kerääjä tekee vain GET-pyyntöjä GitHubiin ja julkiseen RSS:ään. EvidenceStore
kirjoittaa erilliset, sisällön tiivisteellä nimetyt tietueet runtime-haaraan.
Raporttitekstiä, RSS:n raakasisältöä tai tunnuksia ei tallenneta.
"""
from __future__ import annotations

from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from typing import Any, Callable

import jsonschema

from scripts.github_module_adapters import (
    GitHubApiError, GitHubAdapterConflict, GitHubAdapterError,
    MAIN_BRANCH, RUNTIME_BRANCH, ROOT, _json, _module, _run, _time,
)
from scripts.module_recovery import recovery_action


class TransitionEvidenceError(ValueError):
    """Todiste on virheellinen, puutteellinen tai ristiriitainen."""


EVENT_TYPES = {
    "pull_request", "pages_deployment", "public_feed", "checkpoint",
    "legacy_period", "recovery_decision", "legacy_approval",
}
SENSITIVE_KEYS = {
    "report_content", "full_report", "raw_xml", "rss_content", "source_content",
    "token", "password", "authorization", "secret", "api_key", "prompt",
    "source_package", "full_source_package",
}


def _canonical(value: Any) -> bytes:
    """JSONin vakaa tavuesitys, jota käytetään tapahtuman SHA-256-tunnisteessa."""
    return (json.dumps(value, ensure_ascii=False, sort_keys=True,
                       separators=(",", ":")) + "\n").encode("utf-8")


def _reject_sensitive(value: Any, path: str = "record") -> None:
    """Estä raporttien, lähdepakettien ja tunnusten kopiointi auditointilokiin."""
    if isinstance(value, dict):
        for key, child in value.items():
            if str(key).lower() in SENSITIVE_KEYS:
                raise TransitionEvidenceError(f"Auditointitietueessa on kielletty kenttä: {path}.{key}")
            _reject_sensitive(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_sensitive(child, f"{path}[{index}]")


def _valid_url(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urllib.parse.urlparse(value)
    return parsed.scheme == "https" and bool(parsed.netloc) and not parsed.username and not parsed.password


def _validate_record(record: dict[str, Any], schema_path: Path) -> None:
    if not isinstance(record, dict):
        raise TransitionEvidenceError("Auditointitietueen pitää olla JSON-olio.")
    _reject_sensitive(record)
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator.check_schema(schema)
        jsonschema.Draft202012Validator(
            schema, format_checker=jsonschema.FormatChecker()
        ).validate(record)
    except (OSError, json.JSONDecodeError, jsonschema.ValidationError,
            jsonschema.SchemaError) as exc:
        raise TransitionEvidenceError(f"Auditointitietue ei läpäise skeemaa: {exc}") from exc
    core = {key: value for key, value in record.items() if key != "event_id"}
    expected = hashlib.sha256(_canonical(core)).hexdigest()
    if record.get("event_id") != expected:
        raise TransitionEvidenceError("Auditointitietueen event_id ei vastaa sisällön SHA-256-tiivistettä.")


def _feed_url(module_id: str, *, repository_root: Path, pages_base_url: str) -> str:
    """Ratkaise julkinen URL vain topic-syötekatalogista; screening-syöte estyy."""
    catalog = json.loads((repository_root / "data/feed-catalog.json").read_text(encoding="utf-8"))
    matches = [item for item in catalog.get("feeds", [])
               if item.get("id") == module_id and item.get("type") == "topic"]
    if len(matches) != 1:
        raise TransitionEvidenceError("Moduulille ei löydy täsmälleen yhtä topic-syötettä.")
    return f"{pages_base_url.rstrip('/')}/{matches[0]['path']}"


class GitHubTransitionEvidenceCollector:
    """Read-only-kerääjä PR-, Pages-, RSS- ja checkpoint-todisteille."""

    def __init__(self, client: Any, *,
                 public_fetcher: Callable[[str], bytes] | None = None,
                 repository_root: Path | None = None,
                 pages_base_url: str = "https://mikknikk.github.io/aiheseurain"):
        self.client = client
        self.root = Path(repository_root or ROOT)
        self.pages_base_url = pages_base_url.rstrip("/")
        self.public_fetcher = public_fetcher or self._fetch_public

    @staticmethod
    def _fetch_public(url: str) -> bytes:
        """Ohita HTTP-välimuistit; älä lisää URL:iin muuttuvia kyselyparametreja."""
        request = urllib.request.Request(url, headers={
            "Cache-Control": "no-cache, no-store, max-age=0",
            "Pragma": "no-cache",
            "User-Agent": "aiheseurain-transition-evidence/1.0",
        })
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.read()

    @staticmethod
    def _record(module_id: str, run_id: str, event_type: str, observed_at: str,
                source: str, evidence: dict[str, Any]) -> dict[str, Any]:
        _module(module_id)
        _run(run_id)
        _time(observed_at)
        if event_type not in EVENT_TYPES:
            raise TransitionEvidenceError("Tuntematon auditointitapahtuma.")
        core = {
            "schema_version": 1, "module_id": module_id, "run_id": run_id,
            "event_type": event_type, "observed_at": observed_at,
            "source": source, "evidence": evidence,
        }
        return {**core, "event_id": hashlib.sha256(_canonical(core)).hexdigest()}

    def collect_pull_request(self, module_id: str, run_id: str, pr_number: int,
                             *, observed_at: str) -> dict[str, Any]:
        """Lue PR ja varmista, että sen otsikko/run_id/moduuli vastaavat pyyntöä."""
        module_id, run_id = _module(module_id), _run(run_id)
        if type(pr_number) is not int or pr_number < 1:
            raise TransitionEvidenceError("PR-numero on virheellinen.")
        value = self.client.request("GET", f"pulls/{pr_number}")
        body = value.get("body") or ""
        expected_title = f"RSS-julkaisu: {module_id} / {run_id}"
        if value.get("title") != expected_title or f"- Moduuli: {module_id}" not in body or f"- run_id: {run_id}" not in body:
            raise TransitionEvidenceError("PR:n sisältö ei sido sitä pyydettyyn moduuliin ja run_id:hin.")
        merged_at = value.get("merged_at")
        merged = bool(merged_at or value.get("merged"))
        state = value.get("state")
        if state not in {"open", "closed"}:
            raise TransitionEvidenceError("GitHub palautti tuntemattoman PR-tilan.")
        evidence = {
            "pr_number": pr_number, "pr_url": value.get("html_url"),
            "state": state, "merged": merged, "merged_at": merged_at,
            "merge_commit_sha": value.get("merge_commit_sha"),
            "head_sha": (value.get("head") or {}).get("sha"),
            "head_ref": (value.get("head") or {}).get("ref"),
            "base_ref": (value.get("base") or {}).get("ref"),
        }
        if not _valid_url(evidence["pr_url"]) or not evidence["head_sha"] or evidence["base_ref"] != MAIN_BRANCH:
            raise TransitionEvidenceError("PR:n URL, head-SHA tai base-haara ei kelpaa.")
        if merged and (not evidence["merge_commit_sha"] or not merged_at):
            raise TransitionEvidenceError("Yhdistetyn PR:n commit tai yhdistämisaika puuttuu.")
        return self._record(module_id, run_id, "pull_request", observed_at,
                            "github_pull_request_api", evidence)

    def collect_pages_deployment(self, module_id: str, run_id: str, merge_commit_sha: str,
                                 *, observed_at: str) -> dict[str, Any]:
        """Etsi täsmälleen yhdistämiscommitiin sidottu Pages-deployment ja sen tila."""
        module_id, run_id = _module(module_id), _run(run_id)
        if not isinstance(merge_commit_sha, str) or not re.fullmatch(r"[a-f0-9]{40}", merge_commit_sha):
            raise TransitionEvidenceError("Yhdistämiscommitin SHA on virheellinen.")
        deployments = self.client.request(
            "GET", "deployments?environment=github-pages&per_page=100"
        )
        if not isinstance(deployments, list):
            raise TransitionEvidenceError("GitHubin deployment-vastaus ei ole lista.")
        matches = [item for item in deployments
                   if item.get("sha") == merge_commit_sha
                   and item.get("environment") == "github-pages"]
        if not matches:
            evidence = {
                "deployment_id": None, "status_id": None, "state": "not_found",
                "environment": "github-pages", "commit_sha": merge_commit_sha,
                "created_at": None, "updated_at": None,
            }
        else:
            deployment = max(matches, key=lambda item: item.get("created_at") or "")
            deployment_id = deployment.get("id")
            if type(deployment_id) is not int:
                raise TransitionEvidenceError("Pages-deploymentin tunniste puuttuu.")
            statuses = self.client.request(
                "GET", f"deployments/{deployment_id}/statuses?per_page=100"
            )
            if not isinstance(statuses, list):
                raise TransitionEvidenceError("Deployment-tilavastaus ei ole lista.")
            latest = max(statuses, key=lambda item: item.get("created_at") or "") if statuses else {}
            raw_state = latest.get("state", "pending")
            state_map = {"queued": "pending", "in_progress": "in_progress",
                         "pending": "pending", "success": "success",
                         "failure": "failure", "error": "error", "inactive": "inactive"}
            if raw_state not in state_map:
                raise TransitionEvidenceError("Pages-deploymentin tila on tuntematon.")
            evidence = {
                "deployment_id": deployment_id, "status_id": latest.get("id"),
                "state": state_map[raw_state], "environment": "github-pages",
                "commit_sha": merge_commit_sha,
                "created_at": deployment.get("created_at"),
                "updated_at": latest.get("created_at") or deployment.get("created_at"),
            }
        return self._record(module_id, run_id, "pages_deployment", observed_at,
                            "github_deployments_api", evidence)

    @staticmethod
    def _rss_metadata(data: bytes) -> tuple[list[str], int]:
        """Lue vain GUIDit ja item-määrä; älä palauta tai tallenna item-sisältöä."""
        try:
            root = ET.fromstring(data)
        except ET.ParseError as exc:
            raise TransitionEvidenceError("Julkisen RSS:n XML ei jäsenny.") from exc
        channel = root.find("./channel")
        if root.tag != "rss" or channel is None:
            raise TransitionEvidenceError("Julkisesta syötteestä puuttuu RSS channel.")
        items = channel.findall("./item")
        guids = [(item.findtext("guid") or "").strip() for item in items]
        if any(not guid for guid in guids) or len(guids) != len(set(guids)):
            raise TransitionEvidenceError("Julkisen RSS:n GUIDit puuttuvat tai toistuvat.")
        if any(item.find("link") is not None for item in items):
            raise TransitionEvidenceError("Julkisen RSS:n item sisältää kielletyn link-elementin.")
        return guids, len(items)

    def collect_public_feed(self, module_id: str, run_id: str, *, observed_at: str) -> dict[str, Any]:
        """Lue moduulin katalogiin sidottu Pages-syöte ilman välimuistia."""
        module_id, run_id = _module(module_id), _run(run_id)
        url = _feed_url(module_id, repository_root=self.root, pages_base_url=self.pages_base_url)
        data = self.public_fetcher(url)
        if not isinstance(data, bytes):
            raise TransitionEvidenceError("Julkisen RSS-lukijan pitää palauttaa tavut.")
        guids, count = self._rss_metadata(data)
        evidence = {
            "url": url, "sha256": hashlib.sha256(data).hexdigest(),
            "item_count": count, "guids": guids,
        }
        return self._record(module_id, run_id, "public_feed", observed_at,
                            "public_pages_http_no_cache", evidence)

    def collect_checkpoint(self, module_id: str, run_id: str, *,
                           before_blob_sha: str, before_run_id: str | None,
                           before_checked_at: str | None, manifest_phase: str,
                           observed_at: str, branch: str = RUNTIME_BRANCH) -> dict[str, Any]:
        """Lue nykyinen moduulitila ja sido se aiemmin talletettuun lähtö-SHA:han."""
        module_id, run_id = _module(module_id), _run(run_id)
        if not isinstance(before_blob_sha, str) or not before_blob_sha:
            raise TransitionEvidenceError("Checkpointin lähtö-SHA puuttuu.")
        if before_checked_at is not None:
            _time(before_checked_at)
        if manifest_phase not in {"artifacts_persisted", "checkpoint_updated"}:
            raise TransitionEvidenceError("Checkpoint-todisteen manifestivaihe ei ole sallittu.")
        path = f"data/module-state/{module_id}.json"
        current = self.client.get_file(path, branch)
        if current is None:
            raise TransitionEvidenceError("Moduulin nykyistä checkpoint-tiedostoa ei löydy runtime-haarasta.")
        try:
            state = json.loads(current.content.decode("utf-8"))
            checkpoint = state["checkpoint"]["last_successful_run"]
        except (UnicodeDecodeError, json.JSONDecodeError, KeyError, TypeError) as exc:
            raise TransitionEvidenceError("Checkpoint-tiedosto ei sisällä odotettua rakennetta.") from exc
        if state.get("module_id") != module_id or checkpoint.get("run_id") != run_id:
            raise TransitionEvidenceError("Nykyinen checkpoint ei kuulu pyydettyyn moduuliin/run_id:hin.")
        evidence = {
            "before_blob_sha": before_blob_sha, "after_blob_sha": current.sha,
            "before_run_id": before_run_id, "after_run_id": checkpoint.get("run_id"),
            "before_checked_at": before_checked_at, "after_checked_at": checkpoint.get("checked_at"),
            "manifest_phase": manifest_phase,
        }
        return self._record(module_id, run_id, "checkpoint", observed_at,
                            "github_contents_api", evidence)

    def legacy_period_observation(self, module_id: str, run_id: str, *,
                                  status: str, source_url: str, period_start: str,
                                  period_end: str, reason: str | None,
                                  matching_guids: list[str], observed_at: str) -> dict[str, Any]:
        """Kirjaa vanhan polun tarkistetun havainnon; ei päättele puuttumista itse."""
        if status not in {"present", "absent", "unknown"} or not _valid_url(source_url):
            raise TransitionEvidenceError("Vanhan raportointipolun havainto tai lähde-URL on virheellinen.")
        _time(period_start)
        _time(period_end)
        if datetime.fromisoformat(period_start.replace("Z", "+00:00")) > datetime.fromisoformat(period_end.replace("Z", "+00:00")):
            raise TransitionEvidenceError("Vanhan polun seurantajakson alku on loppua myöhempi.")
        if status == "unknown" and (not isinstance(reason, str) or not reason.strip()):
            raise TransitionEvidenceError("Epäselvä vanhan polun havainto vaatii perustelun.")
        if status == "absent" and (not isinstance(reason, str) or not reason.strip()):
            raise TransitionEvidenceError("Julkaisemattomuuden toteaminen vaatii tarkistusperustelun.")
        if not isinstance(matching_guids, list) or any(not isinstance(x, str) or not x for x in matching_guids):
            raise TransitionEvidenceError("Vanhan polun GUID-lista on virheellinen.")
        if status == "present" and not matching_guids:
            raise TransitionEvidenceError("Löytyneelle vanhan polun julkaisulle on kirjattava GUID.")
        evidence = {
            "status": status, "source_url": source_url,
            "period_start": period_start, "period_end": period_end,
            "reason": reason, "matching_guids": matching_guids,
        }
        return self._record(_module(module_id), _run(run_id), "legacy_period", observed_at,
                            "legacy_archive_review", evidence)

    def recovery_decision(self, module_id: str, run_id: str, *,
                          manifest: dict[str, Any] | None,
                          publication_status: str, deployment_status: str,
                          public_feed_matches: bool | None, checkpoint_status: str,
                          legacy_period_status: str, legacy_fallback_authorized: bool,
                          observed_at: str) -> dict[str, Any]:
        """Laske ja tallenna palautuspäätös; ei suorita palautusta."""
        action = recovery_action(
            manifest, publication_status=publication_status,
            deployment_status=deployment_status, public_feed_matches=public_feed_matches,
            checkpoint_status=checkpoint_status, legacy_period_status=legacy_period_status,
            legacy_fallback_authorized=legacy_fallback_authorized,
        )
        evidence = {
            "manifest_phase": manifest.get("phase") if isinstance(manifest, dict) else None,
            "publication_status": publication_status, "deployment_status": deployment_status,
            "public_feed_matches": public_feed_matches, "checkpoint_status": checkpoint_status,
            "legacy_period_status": legacy_period_status,
            "legacy_fallback_authorized": legacy_fallback_authorized, "action": action,
        }
        return self._record(_module(module_id), _run(run_id), "recovery_decision",
                            observed_at, "module_recovery_action", evidence)

    def legacy_fallback_approval(self, module_id: str, run_id: str, *,
                                 approval_id: str, approved_at: str, reason: str,
                                 scope: str, observed_at: str) -> dict[str, Any]:
        """Kirjaa jo erikseen saadun hyväksynnän; tämä metodi ei pyydä eikä anna lupaa."""
        if not isinstance(approval_id, str) or not approval_id.strip():
            raise TransitionEvidenceError("Hyväksynnän tunniste puuttuu.")
        if not isinstance(reason, str) or not reason.strip() or not isinstance(scope, str) or not scope.strip():
            raise TransitionEvidenceError("Hyväksynnän perustelu tai rajaus puuttuu.")
        _time(approved_at)
        evidence = {"approval_id": approval_id, "approved_at": approved_at,
                    "reason": reason, "scope": scope}
        return self._record(_module(module_id), _run(run_id), "legacy_approval",
                            observed_at, "explicit_external_approval", evidence)

    def _record(self, module_id: str, run_id: str, event_type: str, observed_at: str,
                source: str, evidence: dict[str, Any]) -> dict[str, Any]:
        return self._record_factory(module_id, run_id, event_type, observed_at, source, evidence)

    @staticmethod
    def _record_factory(module_id: str, run_id: str, event_type: str, observed_at: str,
                        source: str, evidence: dict[str, Any]) -> dict[str, Any]:
        return GitHubTransitionEvidenceCollector._record(module_id, run_id, event_type,
                                                          observed_at, source, evidence)


class GitHubTransitionEvidenceStore:
    """Sisällön tiivisteellä nimetyt, muuttumattomat ja ajokohtaiset auditointitietueet."""

    def __init__(self, client: Any, *, branch: str = RUNTIME_BRANCH,
                 repository_root: Path | None = None):
        self.client, self.branch = client, branch
        self.root = Path(repository_root or ROOT)
        self.schema_path = self.root / "schemas/module-transition-evidence.schema.json"

    def _path(self, record: dict[str, Any]) -> str:
        return (f"data/module-transition-evidence/{_module(record['module_id'])}/"
                f"{_run(record['run_id'])}/{record['event_type']}-{record['event_id']}.json")

    def record(self, record: dict[str, Any]) -> str:
        """Tallenna tapahtuma kerran; epäselvä kirjoitus ratkaistaan takaisinluvulla."""
        _validate_record(record, self.schema_path)
        path, content = self._path(record), _canonical(record)
        self.client.ensure_branch(self.branch)
        existing = self.client.get_file(path, self.branch)
        if existing is not None:
            if existing.content == content:
                return path
            raise GitHubAdapterConflict("Saman auditointitapahtuman polussa on ristiriitainen sisältö.")
        try:
            self.client.put_file(path, content, self.branch,
                                 message=f"Record {record['module_id']} transition evidence {record['event_type']}")
        except GitHubApiError:
            actual = self.client.get_file(path, self.branch)
            if actual is None or actual.content != content:
                raise
        return path

    def load_run(self, module_id: str, run_id: str) -> list[dict[str, Any]]:
        """Lue kaikki yhden moduulin/ajon tapahtumat ilman kirjoituksia."""
        module_id, run_id = _module(module_id), _run(run_id)
        prefix = f"data/module-transition-evidence/{module_id}/{run_id}"
        query = urllib.parse.urlencode({"ref": self.branch})
        try:
            entries = self.client.request("GET", f"contents/{prefix}?{query}")
        except GitHubApiError as exc:
            if getattr(exc, "status", None) == 404:
                return []
            raise
        if not isinstance(entries, list):
            raise TransitionEvidenceError("Auditointihakemiston GitHub-vastaus ei ole lista.")
        records = []
        for entry in entries:
            name = entry.get("name", "")
            if not name.endswith(".json") or entry.get("type") != "file":
                continue
            file = self.client.get_file(f"{prefix}/{name}", self.branch)
            if file is None:
                raise TransitionEvidenceError("Auditointitiedosto katosi lukemisen aikana.")
            try:
                value = json.loads(file.content.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise TransitionEvidenceError("Auditointitiedosto ei ole kelvollista JSONia.") from exc
            _validate_record(value, self.schema_path)
            if value.get("module_id") != module_id or value.get("run_id") != run_id:
                raise TransitionEvidenceError("Auditointitiedoston moduuli-/ajo-omistajuus ei vastaa polkua.")
            records.append(value)
        records.sort(key=lambda item: (item["observed_at"], item["event_id"]))
        if len({item["event_id"] for item in records}) != len(records):
            raise TransitionEvidenceError("Auditointihakemistossa on duplikaattitapahtumia.")
        return records
