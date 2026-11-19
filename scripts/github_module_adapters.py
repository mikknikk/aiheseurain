"""GitHub-pohjaiset pysyvät moduuliorkestroinnin sovittimet.

Runtime-tila tallennetaan erilliselle haaralle. RSS-ehdokas toimitetaan PR:na
main-haaraan, jotta nykyinen julkaisulaadun portti ja Pages-varmennus säilyvät.
"""
from __future__ import annotations
import base64
from copy import deepcopy
from dataclasses import dataclass
import hashlib
import json
import os
from datetime import datetime
import re
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Callable
import jsonschema
from pathlib import Path
import xml.etree.ElementTree as ET

from scripts.module_state import validate_module_state, StateConflictError
from scripts.module_orchestrator import PublicationReceipt
from scripts.publication_journal import PHASES, PublicationJournalConflict, PublicationJournalError
from scripts.module_run_adapters import AdapterError, AdapterConflictError, _audit_record, _reject_sensitive_fields
from scripts.publication_routing import load_publication_context, resolve_publication_plan

REPO_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
MODULE_RE = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
RUN_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{2,180}$")
RUNTIME_BRANCH = "module-runtime-state"
MAIN_BRANCH = "main"
MAX_GITHUB_FILE_BYTES = 50 * 1024 * 1024
ROOT = Path(__file__).resolve().parents[1]


class GitHubAdapterError(AdapterError):
    """GitHub-pohjaisen sovittimen yleinen virhe."""


class GitHubAdapterConflict(AdapterConflictError):
    """GitHubin optimistisen kirjoituksen ristiriita."""


class GitHubApiError(GitHubAdapterError):
    """GitHub API -virhe, jota takaisinluku ei ratkaissut."""


def _module(value: str) -> str:
    """Validoi moduulitunniste ennen tiedostopolun muodostamista."""
    if not isinstance(value, str) or not MODULE_RE.fullmatch(value):
        raise GitHubAdapterError("Virheellinen moduulitunniste.")
    return value


def _run(value: str) -> str:
    """Validoi ajotunniste ennen tiedostopolun muodostamista."""
    if not isinstance(value, str) or not RUN_RE.fullmatch(value):
        raise GitHubAdapterError("Virheellinen ajotunniste.")
    return value


def _json(value: Any) -> bytes:
    """Muodosta deterministinen JSON-tavujono."""
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def _validate_schema(value: dict[str, Any], filename: str) -> None:
    """Validoi pysyvä runtime-tietue repositorion versionoidulla JSON-skeemalla."""
    schema = json.loads((ROOT / "schemas" / filename).read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(
        schema, format_checker=jsonschema.FormatChecker()
    ).validate(value)


def _time(value: str) -> None:
    """Vaadi aikavyöhykkeellinen ISO 8601 -aikaleima."""
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, TypeError, ValueError) as exc:
        raise GitHubAdapterError("Virheellinen ISO 8601 -aikaleima.") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise GitHubAdapterError("Aikaleimasta puuttuu aikavyöhyke.")


@dataclass(frozen=True)
class GitHubFile:
    """Tiedoston tavut ja GitHubin blob-SHA."""
    content: bytes
    sha: str


class GitHubApiClient:
    """Pieni GitHub REST -asiakas, jonka verkkorajapinnan voi korvata testeissä."""

    def __init__(self, repository: str | None = None, token: str | None = None,
                 *, api_url: str = "https://api.github.com", timeout: int = 30):
        self.repository = repository or os.getenv("GITHUB_REPOSITORY", "")
        self.token = token or os.getenv("GITHUB_TOKEN", "")
        self.api_url = api_url.rstrip("/")
        self.timeout = timeout
        if not REPO_RE.fullmatch(self.repository) or not self.token:
            raise GitHubAdapterError("GITHUB_REPOSITORY tai GITHUB_TOKEN puuttuu.")

    def request(self, method: str, path: str, payload: dict | None = None) -> Any:
        """Suorita GitHub API -pyyntö ja säilytä HTTP-tilakoodi virheluokassa."""
        body = _json(payload) if payload is not None else None
        request = urllib.request.Request(
            f"{self.api_url}/repos/{self.repository}/{path.lstrip('/')}",
            data=body, method=method,
            headers={"Authorization": f"Bearer {self.token}",
                     "Accept": "application/vnd.github+json",
                     "X-GitHub-Api-Version": "2022-11-28",
                     "Content-Type": "application/json",
                     "User-Agent": "aiheseurain-module-runtime"})
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                raw = response.read()
            return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace")[:800]
            error = GitHubApiError(f"GitHub API {method} {path}: HTTP {exc.code}: {detail}")
            error.status = exc.code
            raise error from exc
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise GitHubApiError(f"GitHub API -pyyntö epäonnistui: {exc}") from exc

    def get_file(self, path: str, branch: str) -> GitHubFile | None:
        """Lue yksi tiedosto täsmälliseltä haaralta."""
        query = urllib.parse.urlencode({"ref": branch})
        encoded = urllib.parse.quote(path, safe="/")
        try:
            value = self.request("GET", f"contents/{encoded}?{query}")
        except GitHubApiError as exc:
            if getattr(exc, "status", None) == 404:
                return None
            raise
        if not isinstance(value, dict) or value.get("type") != "file":
            raise GitHubAdapterError(f"Polku ei ole tiedosto: {path}")
        try:
            sha = value["sha"]
            size = int(value.get("size", 0))
            if size > MAX_GITHUB_FILE_BYTES:
                raise GitHubAdapterError(f"GitHub-tiedosto ylittää 50 MiB:n turvarajan: {path}")
            encoded_content = value.get("content", "")
            if not encoded_content and value.get("encoding") == "none":
                blob = self.request("GET", f"git/blobs/{sha}")
                encoded_content = blob["content"]
            content = base64.b64decode(encoded_content)
            if len(content) > MAX_GITHUB_FILE_BYTES:
                raise GitHubAdapterError(f"GitHub-tiedosto ylittää 50 MiB:n turvarajan: {path}")
            return GitHubFile(content, sha)
        except (KeyError, ValueError, TypeError) as exc:
            raise GitHubAdapterError(f"Tiedoston sisältö on virheellinen: {path}") from exc

    def put_file(self, path: str, content: bytes, branch: str, *,
                 message: str, sha: str | None = None) -> GitHubFile:
        """Kirjoita tiedosto; ratkaise epäselvyys takaisinluvulla ja yritä rinnakkaiskonflikti rajatusti."""
        if len(content) > MAX_GITHUB_FILE_BYTES:
            raise GitHubAdapterError("GitHub-tiedoston kirjoitus ylittää 50 MiB:n turvarajan.")
        expected_sha = sha
        for _attempt in range(3):
            current = self.get_file(path, branch)
            if current is not None and current.content == content:
                return current
            if expected_sha is not None and (current is None or current.sha != expected_sha):
                raise GitHubAdapterConflict(f"Tiedoston SHA muuttui ennen kirjoitusta: {path}")
            if expected_sha is None and current is not None:
                raise GitHubAdapterConflict(f"Tiedosto on jo olemassa eri sisällöllä: {path}")
            payload = {"message": message, "content": base64.b64encode(content).decode("ascii"),
                       "branch": branch}
            if current is not None:
                payload["sha"] = current.sha
            try:
                result = self.request("PUT", f"contents/{urllib.parse.quote(path, safe='/')}", payload)
                returned = result.get("content", {})
                if returned.get("sha"):
                    return GitHubFile(content, returned["sha"])
            except GitHubApiError as exc:
                actual = self.get_file(path, branch)
                if actual is not None and actual.content == content:
                    return actual
                if getattr(exc, "status", None) not in {409, 422}:
                    raise
                if expected_sha is not None and (actual is None or actual.sha != expected_sha):
                    raise GitHubAdapterConflict(f"Tiedoston SHA muuttui rinnakkaisessa kirjoituksessa: {path}") from exc
                # Muu haara-commit ehti edelle; yritä uudelleen, jos tämä tiedosto ei muuttunut.
                continue
            actual = self.get_file(path, branch)
            if actual is not None and actual.content == content:
                return actual
            raise GitHubAdapterError(f"GitHub ei vahvistanut kirjoitusta: {path}")
        raise GitHubAdapterConflict(f"GitHubin rinnakkaiskirjoitus ei rauhoittunut kolmella yrityksellä: {path}")

    def ensure_branch(self, branch: str, base: str = MAIN_BRANCH) -> None:
        """Luo runtime-haara mainin nykyisestä kärjestä vain ensimmäisellä käyttökerralla."""
        ref = urllib.parse.quote(branch, safe="/")
        try:
            self.request("GET", f"git/ref/heads/{ref}")
            return
        except GitHubApiError as exc:
            if getattr(exc, "status", None) != 404:
                raise
        base_ref = self.request("GET", f"git/ref/heads/{urllib.parse.quote(base, safe='/')}")
        try:
            self.request("POST", "git/refs", {"ref": f"refs/heads/{branch}",
                                              "sha": base_ref["object"]["sha"]})
        except GitHubApiError as exc:
            if getattr(exc, "status", None) not in {409, 422}:
                raise
            self.request("GET", f"git/ref/heads/{ref}")

    def find_pull_request(self, branch: str, base: str = MAIN_BRANCH) -> dict | None:
        """Etsi aiempi PR myös suljetuista ja yhdistetyistä."""
        owner = self.repository.split("/")[0]
        query = urllib.parse.urlencode({"head": f"{owner}:{branch}", "base": base,
                                        "state": "all", "per_page": 100})
        values = self.request("GET", f"pulls?{query}")
        return values[0] if values else None

    def create_pull_request(self, title: str, body: str, branch: str,
                            base: str = MAIN_BRANCH) -> dict:
        """Avaa RSS-ehdokkaan PR ilman automaattista yhdistämistä."""
        return self.request("POST", "pulls", {
            "title": title, "body": body, "head": branch, "base": base,
            "maintainer_can_modify": False})


class GitHubModuleStateStore:
    """Moduulikohtainen checkpoint-varasto GitHubin blob-SHA-CAS-menetelmällä."""

    def __init__(self, client: Any, *, branch: str = RUNTIME_BRANCH):
        self.client, self.branch = client, branch

    def _path(self, module_id: str) -> str:
        return f"data/module-state/{_module(module_id)}.json"

    def _file(self, module_id: str) -> GitHubFile:
        path = self._path(module_id)
        value = self.client.get_file(path, self.branch)
        if value is None:
            value = self.client.get_file(path, MAIN_BRANCH)
        if value is None:
            raise GitHubAdapterError(f"Moduulin tilatiedostoa ei löydy: {module_id}")
        return value

    def load(self, module_id: str) -> tuple[dict[str, Any], str]:
        """Lue vain pyydetyn moduulin tila ja palauta blob-SHA."""
        file = self._file(module_id)
        try:
            state = json.loads(file.content.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise GitHubAdapterError("Moduulitilan JSON on virheellinen.") from exc
        validate_module_state(state)
        if state.get("module_id") != module_id:
            raise GitHubAdapterError("Moduulitiedoston omistajuus ei vastaa pyydettyä moduulia.")
        return state, file.sha

    def save(self, module_id: str, state: dict[str, Any], *, expected_sha: str) -> str:
        """Tallenna checkpoint vain odotetun SHA:n ollessa edelleen voimassa."""
        module_id = _module(module_id)
        validate_module_state(state)
        if state.get("module_id") != module_id:
            raise GitHubAdapterError("Checkpointin moduulitunniste ei vastaa tiedostopolkua.")
        self.client.ensure_branch(self.branch)
        path, content = self._path(module_id), _json(state)
        current = self.client.get_file(path, self.branch)
        if current is None:
            source = self.client.get_file(path, MAIN_BRANCH)
            if source is None or source.sha != expected_sha:
                raise StateConflictError("Moduulin lähtötila muuttui ennen runtime-haaran alustusta.")
            current = self.client.put_file(path, source.content, self.branch,
                                           message=f"Initialize {module_id} runtime state")
        if current.sha != expected_sha:
            if current.content == content:
                return current.sha
            raise StateConflictError("Moduulin GitHub-blob-SHA muuttui rinnakkaisen ajon aikana.")
        try:
            return self.client.put_file(path, content, self.branch,
                message=f"Update {module_id} module checkpoint", sha=current.sha).sha
        except GitHubApiError:
            actual = self.client.get_file(path, self.branch)
            if actual is not None and actual.content == content:
                return actual.sha
            raise


class GitHubArtifactStore:
    """Ajokohtaiset muuttumattomat artefaktit ja SHA-tarkistettu moduuli-indeksi."""

    def __init__(self, client: Any, *, branch: str = RUNTIME_BRANCH):
        self.client, self.branch = client, branch

    def _index(self, module_id: str) -> str:
        return f"data/module-artifacts/{_module(module_id)}/index.json"

    def _artifact(self, module_id: str, run_id: str) -> str:
        return f"data/module-artifacts/{_module(module_id)}/{_run(run_id)}.json"

    def _read_index(self, module_id: str) -> tuple[dict[str, Any], str]:
        file = self.client.get_file(self._index(module_id), self.branch)
        if file is None:
            return {"schema_version": 1, "module_id": module_id, "runs": {}}, "missing"
        try:
            value = json.loads(file.content.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise GitHubAdapterError("Artefakti-indeksin JSON on virheellinen.") from exc
        if (not isinstance(value, dict) or value.get("schema_version") != 1 or value.get("module_id") != module_id
                or not isinstance(value.get("runs"), dict)):
            raise GitHubAdapterError("Artefakti-indeksin rakenne tai omistajuus on virheellinen.")
        _validate_schema(value, "module-artifact-index.schema.json")
        return value, file.sha

    def load_version(self, module_id: str) -> str:
        """Palauta indeksin blob-SHA tai missing."""
        return self._read_index(_module(module_id))[1]

    def commit(self, module_id: str, run_id: str, artifacts: dict[str, Any], *,
               expected_version: str) -> str:
        """Kirjoita artefakti ensin muuttumattomana ja sitten indeksoi se CAS:lla."""
        module_id, run_id = _module(module_id), _run(run_id)
        if not isinstance(artifacts, dict):
            raise GitHubAdapterError("Artefaktien pitää olla JSON-olio.")
        _reject_sensitive_fields(artifacts)
        index, version = self._read_index(module_id)
        if version != expected_version:
            if run_id in index["runs"]:
                expected_digest = hashlib.sha256(_json(artifacts)).hexdigest()
                if index["runs"][run_id].get("sha256") == expected_digest:
                    return version
            raise GitHubAdapterConflict("Artefakti-indeksi muuttui ennen kirjoitusta.")
        self.client.ensure_branch(self.branch)
        path, content = self._artifact(module_id, run_id), _json(artifacts)
        digest = hashlib.sha256(content).hexdigest()
        old = self.client.get_file(path, self.branch)
        if old is not None and old.content != content:
            raise GitHubAdapterConflict("Sama artefaktipolku on jo varattu eri sisällölle.")
        if old is None:
            self.client.put_file(path, content, self.branch,
                                 message=f"Store {module_id} artifacts {run_id}")
        latest, latest_version = self._read_index(module_id)
        if run_id in latest["runs"]:
            if latest["runs"][run_id].get("sha256") == digest:
                return latest_version
            raise GitHubAdapterConflict("Sama run_id on jo sidottu eri artefaktiin.")
        if latest_version != expected_version:
            raise GitHubAdapterConflict("Artefakti-indeksi muuttui rinnakkaisen kirjoituksen aikana.")
        latest = deepcopy(latest)
        latest["runs"][run_id] = {"path": path, "sha256": digest, "size_bytes": len(content)}
        _validate_schema(latest, "module-artifact-index.schema.json")
        index_content = _json(latest)
        current_file = self.client.get_file(self._index(module_id), self.branch)
        try:
            return self.client.put_file(self._index(module_id), index_content, self.branch,
                message=f"Index {module_id} artifacts {run_id}",
                sha=current_file.sha if current_file else None).sha
        except GitHubApiError:
            confirmed, confirmed_sha = self._read_index(module_id)
            if confirmed.get("runs", {}).get(run_id, {}).get("sha256") == digest:
                return confirmed_sha
            raise


class GitHubPublicationJournal:
    """Ajokohtainen pysyvä manifesti ja yksisuuntainen vaihehistoria."""

    def __init__(self, client: Any, *, branch: str = RUNTIME_BRANCH):
        self.client, self.branch = client, branch

    def _path(self, module_id: str, run_id: str) -> str:
        return f"data/module-publication-journal/{_module(module_id)}/{_run(run_id)}.json"

    def _read(self, module_id: str, run_id: str) -> tuple[dict[str, Any], str]:
        file = self.client.get_file(self._path(module_id, run_id), self.branch)
        if file is None:
            raise PublicationJournalError("Julkaisumanifestia ei löydy.")
        try:
            value = json.loads(file.content.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise PublicationJournalError("Julkaisumanifestin JSON on virheellinen.") from exc
        if (not isinstance(value, dict) or value.get("module_id") != module_id or value.get("run_id") != run_id
                or value.get("phase") not in PHASES or not isinstance(value.get("history"), list)):
            raise PublicationJournalError("Manifestin tunnisteet tai vaihehistoria ovat virheellisiä.")
        _validate_schema(value, "module-publication-journal.schema.json")
        return value, file.sha

    def prepare(self, record: dict[str, Any]) -> dict[str, Any]:
        """Luo prepared-manifesti tai palauta täsmälleen saman ajon aiempi manifesti."""
        required = {"module_id", "run_id", "idempotency_key", "report_sha256",
                    "artifacts_sha256", "state_sha256", "artifact_version",
                    "publication_targets", "prepared_at"}
        if not isinstance(record, dict) or set(record) != required:
            raise PublicationJournalError("Manifestin kentät eivät vastaa sopimusta.")
        module_id, run_id = _module(record["module_id"]), _run(record["run_id"])
        if not isinstance(record["publication_targets"], list) or not record["publication_targets"]:
            raise PublicationJournalError("Julkaisukohteiden pitää olla ei-tyhjä lista.")
        _time(record["prepared_at"])
        self.client.ensure_branch(self.branch)
        path = self._path(module_id, run_id)
        old = self.client.get_file(path, self.branch)
        stable_keys = required - {"state_sha256", "artifact_version"}
        if old is not None:
            value = json.loads(old.content.decode("utf-8"))
            if {key: value.get(key) for key in stable_keys} != {key: record[key] for key in stable_keys}:
                raise PublicationJournalConflict("Sama moduuli/run_id on varattu eri julkaisusisällölle.")
            return value
        value = {**record, "phase": "prepared", "updated_at": record["prepared_at"],
                 "receipt": None, "history": [{"phase": "prepared",
                 "updated_at": record["prepared_at"], "receipt": None}]}
        _validate_schema(value, "module-publication-journal.schema.json")
        content = _json(value)
        try:
            self.client.put_file(path, content, self.branch,
                                 message=f"Prepare {module_id} publication {run_id}")
        except GitHubApiError:
            check = self.client.get_file(path, self.branch)
            if check is None or check.content != content:
                raise
        return value

    def load(self, module_id: str, run_id: str) -> dict[str, Any]:
        """Lue ajokohtainen manifesti."""
        return self._read(module_id, run_id)[0]

    def advance(self, module_id: str, run_id: str, phase: str, *,
                updated_at: str, receipt: dict[str, Any] | None = None) -> dict[str, Any]:
        """Siirrä vaihetta yhden askeleen SHA-CAS-kirjoituksella."""
        if phase not in PHASES:
            raise PublicationJournalError("Tuntematon julkaisumanifestin vaihe.")
        _time(updated_at)
        for _ in range(3):
            current, sha = self._read(module_id, run_id)
            old_index, new_index = PHASES.index(current["phase"]), PHASES.index(phase)
            if new_index <= old_index:
                if receipt is not None and current.get("receipt") not in (None, receipt):
                    raise PublicationJournalConflict("Julkaisukuittaus poikkeaa aiemmasta.")
                return current
            if new_index != old_index + 1:
                raise PublicationJournalConflict("Manifestivaihetta ei voi ohittaa.")
            updated = deepcopy(current)
            updated.update({"phase": phase, "updated_at": updated_at})
            if receipt is not None:
                updated["receipt"] = deepcopy(receipt)
            updated["history"].append({"phase": phase, "updated_at": updated_at,
                                       "receipt": deepcopy(receipt)})
            _validate_schema(updated, "module-publication-journal.schema.json")
            try:
                self.client.put_file(self._path(module_id, run_id), _json(updated),
                    self.branch, message=f"Advance {module_id} {run_id}: {phase}", sha=sha)
                return updated
            except (GitHubApiError, GitHubAdapterConflict):
                actual, _ = self._read(module_id, run_id)
                if actual["phase"] == phase:
                    if receipt is not None and actual.get("receipt") != receipt:
                        raise PublicationJournalConflict("Tallennettu kuittaus poikkeaa uusinnasta.")
                    return actual
                if PHASES.index(actual["phase"]) != old_index:
                    raise PublicationJournalConflict("Manifesti muuttui rinnakkaisen tilasiirtymän aikana.")
        raise PublicationJournalConflict("Manifestin SHA-CAS epäonnistui kolmesti.")


@dataclass(frozen=True)
class PublicationCandidate:
    """Nykyiseen RSS/Pages-putkeen toimitettava yhden syötteen ehdokas."""
    files: dict[str, str]
    feed_path: str
    public_url: str


class GitHubPagesRssPublisher:
    """Avaa hyväksytyn RSS-ehdokkaan PR:n ja odottaa Pages-takaisinlukua.

    Candidate builderin on tuotettava yksi RSS/XML-tiedosto ja saman run_id:n
    hyväksytty julkaisulaadun porttiraportti. Adapteri ei yhdistä PR:ää eikä
    hyväksy toimituksellista sisältöä itse.
    """

    def __init__(self, client: Any, candidate_builder: Callable[..., PublicationCandidate],
                 *, public_fetcher: Callable[[str], bytes] | None = None,
                 pages_base_url: str = "https://mikknikk.github.io/aiheseurain",
                 repository_root: Path | None = None):
        self.client, self.candidate_builder = client, candidate_builder
        self.public_fetcher = public_fetcher or self._fetch_public
        self.pages_base_url = pages_base_url.rstrip("/")
        self.root = Path(repository_root or Path(__file__).resolve().parents[1])
        self.expected: dict[str, tuple[str, tuple[str, ...], int, str]] = {}
        self.run_guids: dict[str, str] = {}

    @staticmethod
    def _fetch_public(url: str) -> bytes:
        """Lue julkinen RSS-syöte ilman välimuistia."""
        request = urllib.request.Request(url, headers={"Cache-Control": "no-cache",
            "Pragma": "no-cache", "User-Agent": "aiheseurain-module-publisher"})
        with urllib.request.urlopen(request, timeout=20) as response:
            return response.read()

    @staticmethod
    def _metadata(data: bytes) -> tuple[list[str], int]:
        """Tarkista RSS/XML, GUIDien yksilöllisyys ja item-linkkien kielto."""
        try:
            root = ET.fromstring(data)
        except ET.ParseError as exc:
            raise GitHubAdapterError("RSS-ehdokkaan XML ei jäsenny.") from exc
        channel = root.find("./channel")
        if root.tag != "rss" or channel is None:
            raise GitHubAdapterError("RSS channel puuttuu.")
        items = channel.findall("./item")
        guids = [(item.findtext("guid") or "").strip() for item in items]
        if any(not guid for guid in guids) or len(guids) != len(set(guids)):
            raise GitHubAdapterError("RSS-itemien GUIDit puuttuvat tai eivät ole yksilöllisiä.")
        if any(item.find("link") is not None for item in items):
            raise GitHubAdapterError("RSS-item ei saa sisältää link-elementtiä.")
        return guids, len(items)

    def _build(self, module_id: str, run_id: str, report_content: str, *,
               expected_feed_path: str, expected_public_url: str | None = None,
               target_id: str | None = None) -> PublicationCandidate:
        if target_id is None:
            candidate = self.candidate_builder(module_id, run_id, report_content)
        else:
            candidate = self.candidate_builder(module_id, run_id, report_content, target_id=target_id)
        if not isinstance(candidate, PublicationCandidate):
            raise GitHubAdapterError("candidate_builder palautti väärän tulossopimuksen.")
        if not isinstance(candidate.files, dict) or any(not isinstance(value, str) for value in candidate.files.values()):
            raise GitHubAdapterError("Julkaisuehdokkaan tiedostojen pitää olla UTF-8-merkkijonoja.")
        gate_path = f"reports/julkaisuportit/{run_id}.json"
        if set(candidate.files) != {candidate.feed_path, gate_path}:
            raise GitHubAdapterError("Julkaisu-PR saa sisältää vain yhden RSS-syötteen ja porttiraportin.")
        if not candidate.feed_path.startswith("feeds/") or not candidate.feed_path.endswith(".xml"):
            raise GitHubAdapterError("Julkaisupolun pitää olla feeds/*.xml.")
        if candidate.feed_path != expected_feed_path:
            raise GitHubAdapterError("Ehdokkaan syötepolku ei vastaa rekisterin julkaisukohdetta.")
        expected_url = expected_public_url or f"{self.pages_base_url}/{candidate.feed_path}"
        if candidate.public_url != expected_url:
            raise GitHubAdapterError("Julkinen URL ei vastaa rekisterin Pages-syötepolkua.")
        feed_bytes = candidate.files[candidate.feed_path].encode("utf-8")
        guids, count = self._metadata(feed_bytes)
        if count < 1:
            raise GitHubAdapterError("RSS-ehdokas ei sisällä yhtään itemiä.")
        try:
            gate = json.loads(candidate.files[gate_path])
        except json.JSONDecodeError as exc:
            raise GitHubAdapterError("Julkaisulaadun porttiraportti ei ole JSONia.") from exc
        if (gate.get("decision") != "approved" or gate.get("run_id") != run_id
                or gate.get("feed_path") != candidate.feed_path):
            raise GitHubAdapterError("Porttiraportin hyväksyntä tai tunnisteet eivät täsmää.")
        expected_task = candidate.feed_path.removeprefix("feeds/").removesuffix(".xml")
        if gate.get("task_id") not in {module_id, expected_task}:
            raise GitHubAdapterError("Porttiraportin task_id ei vastaa moduulia tai syötettä.")
        self.expected[guids[-1]] = (
            candidate.public_url, tuple(guids), count, hashlib.sha256(feed_bytes).hexdigest()
        )
        self.run_guids[f"{module_id}:{run_id}"] = guids[-1]
        return candidate

    def publish(self, module_id: str, run_id: str, report_content: str, *,
                idempotency_key: str, expected_feed_path: str | None = None,
                expected_public_url: str | None = None,
                target_id: str | None = None) -> PublicationReceipt:
        """Luo yhden julkaisuehdokkaan PR:n; sama ajo käyttää aina samaa haaraa."""
        module_id, run_id = _module(module_id), _run(run_id)
        if idempotency_key != f"{module_id}:{run_id}":
            raise GitHubAdapterError("Julkaisun idempotenssiavain ei täsmää.")
        if expected_feed_path is None:
            catalog = json.loads((self.root / "data/feed-catalog.json").read_text(encoding="utf-8"))
            matches = [item for item in catalog.get("feeds", [])
                       if item.get("id") == module_id and item.get("type") == "topic"]
            if len(matches) != 1:
                raise GitHubAdapterError("Moduulille ei löydy yksikäsitteistä topic-RSS-syötettä.")
            expected_feed_path = matches[0]["path"]
        candidate = self._build(
            module_id, run_id, report_content,
            expected_feed_path=expected_feed_path,
            expected_public_url=expected_public_url,
            target_id=target_id,
        )
        branch_id = hashlib.sha256(f"{module_id}:{run_id}".encode("utf-8")).hexdigest()[:20]
        branch = f"module-publish/{module_id}/{branch_id}"
        self.client.ensure_branch(branch)
        pull = self.client.find_pull_request(branch)
        gate_path = f"reports/julkaisuportit/{run_id}.json"
        for path, text in candidate.files.items():
            desired = text.encode("utf-8")
            current = self.client.get_file(path, branch)
            if pull is not None:
                # Kun PR on jo olemassa, sen ehdokastiedostot ovat muuttumattomia.
                if current is None or current.content != desired:
                    raise GitHubAdapterConflict("Saman ajon olemassa olevan julkaisun sisältöä ei voi vaihtaa.")
                continue
            main_file = self.client.get_file(path, MAIN_BRANCH)
            if path == gate_path and main_file is not None:
                raise GitHubAdapterConflict("Julkaisulaadun porttiraportin run_id on jo käytössä main-haarassa.")
            if current is not None:
                if current.content == desired:
                    continue
                if main_file is None or current.content != main_file.content:
                    raise GitHubAdapterConflict("Julkaisuehdokkaan haara sisältää aiemmasta yrityksestä poikkeavaa sisältöä.")
                self.client.put_file(path, desired, branch,
                    message=f"Prepare RSS publication {module_id} {run_id}", sha=current.sha)
            else:
                if path == gate_path and self.client.get_file(path, MAIN_BRANCH) is not None:
                    raise GitHubAdapterConflict("Julkaisulaadun porttiraportin run_id on jo käytössä main-haarassa.")
                self.client.put_file(path, desired, branch,
                    message=f"Prepare RSS publication {module_id} {run_id}")
        if pull is None:
            pull = self.client.create_pull_request(
                f"RSS-julkaisu: {module_id} / {run_id}",
                ("Tämä PR toimittaa yhden RSS-ehdokkaan nykyiseen RSS/Pages-putkeen.\n\n"
                 f"- Moduuli: {module_id}\n- run_id: {run_id}\n- Syöte: {candidate.feed_path}\n\n"
                 "PR:n CI tarkistaa RSS:n ja julkaisulaadun porttiraportin. Yhdistäminen "
                 "käynnistää nykyisen Pages-julkaisun ja julkisen takaisinluvun. "
                 "Tämä sovitin ei yhdistä PR:ää."),
                branch)
        guid = (self.run_guids[f"{module_id}:{run_id}"],)
        if not (pull.get("merged") or pull.get("merged_at")):
            if pull.get("state") == "closed":
                raise GitHubAdapterConflict("Julkaisun PR suljettiin yhdistämättä; samaa ajoa ei voi julkaista uudelleen.")
            return PublicationReceipt(False, guid, 1)
        receipt = PublicationReceipt(True, guid, 1)
        return receipt if self.verify(receipt) else PublicationReceipt(False, guid, 1)

    def publish_target_reports(self, module_id: str, run_id: str,
                               reports: list[dict[str, Any]]) -> PublicationReceipt:
        """Rajaa ensimmäisen toteutuksen yhteen kohderaporttiin ja RSS-kohteeseen."""
        if len(reports) != 1:
            raise GitHubAdapterError("Yksi GitHub-julkaisupyyntö voi sisältää tässä vaiheessa yhden kohderaportin.")
        report = reports[0]
        context = load_publication_context(self.root)
        module = context["modules"].get(module_id)
        if module is None or module.get("module_type") != "topic":
            raise GitHubAdapterError("RSS-julkaisusovitin hyväksyy vain topic-moduuleja.")
        plan = resolve_publication_plan(
            context, module_id=module_id, target_id=report["target_id"],
            run_id=run_id, observation_types=report["observation_types"],
        )
        if len(plan.publication_ids) != 1:
            raise GitHubAdapterError("Kohteelle ei ratkennut yhtä aktiivista RSS-julkaisukohdetta.")
        publication = context["publications"][plan.publication_ids[0]][1]
        destination = publication["destination"]
        return self.publish(
            module_id, run_id, report["report_content"],
            idempotency_key=f"{module_id}:{run_id}",
            expected_feed_path=destination["path"],
            expected_public_url=destination["url"],
            target_id=report["target_id"],
        )

    def verify(self, receipt: PublicationReceipt) -> bool:
        """Varmista julkisen Pages-syötteen GUIDit ja item-määrä."""
        if len(receipt.report_guid_refs) != 1 or receipt.published_items != 1:
            return False
        expected = self.expected.get(receipt.report_guid_refs[0])
        if expected is None:
            return False
        url, guids, count, expected_sha256 = expected
        try:
            actual = self.public_fetcher(url)
            actual_guids, actual_count = self._metadata(actual)
        except Exception:
            return False
        return (actual_guids == list(guids) and actual_count == count
                and hashlib.sha256(actual).hexdigest() == expected_sha256)


class GitHubRunRecorder:
    """Pysyvä, tietosuojattu ajotulosloki muuttumattomina ajokohtaisina tiedostoina."""

    def __init__(self, client: Any, *, branch: str = RUNTIME_BRANCH):
        self.client, self.branch = client, branch

    def record(self, result: Any) -> None:
        """Tallenna vain ajon metatiedot; raporttisisältö ja salaisuudet rajataan pois."""
        record = _audit_record(result)
        _reject_sensitive_fields(record)
        module_id, run_id = _module(record["module_id"]), _run(record["run_id"])
        path, content = f"data/module-run-history/{module_id}/{run_id}.json", _json(record)
        self.client.ensure_branch(self.branch)
        old = self.client.get_file(path, self.branch)
        if old is not None:
            if old.content == content:
                return
            raise GitHubAdapterConflict("Sama moduuli/run_id on jo kirjattu eri ajotuloksella.")
        try:
            self.client.put_file(path, content, self.branch,
                                 message=f"Record {module_id} run {run_id}")
        except GitHubApiError:
            check = self.client.get_file(path, self.branch)
            if check is None or check.content != content:
                raise
