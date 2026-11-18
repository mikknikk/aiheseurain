"""Pysyvä julkaisumanifesti ja sen turvalliset tilasiirtymät.

Manifesti tallentaa ajokohtaisen julkaisun etenemisen ennen ulkoisia kirjoituksia.
Se ei sisällä raporttien tai lähteiden varsinaista sisältöä, vaan tunnisteet,
tiivisteet ja palautumisen kannalta tarpeelliset vaihetiedot.
"""
from __future__ import annotations

from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
from typing import Any
import fcntl


class PublicationJournalError(RuntimeError):
    """Manifestin luku-, kirjoitus- tai eheysvirhe."""


class PublicationJournalConflict(PublicationJournalError):
    """Sama ajoavain on jo varattu eri sisällölle tai ristiriitaiselle tilalle."""


PHASES = ("prepared", "published", "artifacts_persisted", "checkpoint_updated")
IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{2,180}$")


def content_digest(value: Any) -> str:
    """Laske JSON-sisällölle vakaa SHA-256-tiiviste."""
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True,
                         separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _safe_id(value: str) -> str:
    """Estä ajotunnisteen käyttäminen tiedostopolun manipulointiin."""
    if not isinstance(value, str) or not IDENTIFIER.fullmatch(value):
        raise PublicationJournalError("Julkaisumanifestin tunniste ei ole kelvollinen.")
    return value


@contextmanager
def _lock(path: Path):
    """Lukitse yhden manifestin luku-muutos-kirjoitusjakso."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.with_suffix(path.suffix + ".lock").open("a+b") as stream:
        fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


def _atomic_write(path: Path, value: dict[str, Any]) -> None:
    """Korvaa manifesti atomisesti vasta, kun koko JSON on levyllä."""
    path.parent.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="wb", dir=path.parent,
                                         prefix=f".{path.name}.", suffix=".tmp",
                                         delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        directory_fd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


class JsonFilePublicationJournal:
    """Tiedostopohjainen manifestivarasto testaukseen ja paikalliseen käyttöön.

    Tuotantosovittimen tulee toteuttaa sama sopimus pysyvällä, atomisella
    tallennuksella. Manifesti kirjoitetaan ennen julkaisua, joten tallennusvirhe
    estää julkaisun käynnistymisen.
    """

    def __init__(self, root: Path):
        self.root = Path(root).resolve()

    def _path(self, module_id: str, run_id: str) -> Path:
        module_id = _safe_id(module_id)
        run_id = _safe_id(run_id)
        name = hashlib.sha256(f"{module_id}:{run_id}".encode("utf-8")).hexdigest()
        path = (self.root / f"{name}.json").resolve()
        if not path.is_relative_to(self.root):
            raise PublicationJournalError("Manifestipolku poistuu varastosta.")
        return path

    def prepare(self, record: dict[str, Any]) -> dict[str, Any]:
        """Luo valmistelumerkinnän tai palauta saman ajon aiemman manifestin."""
        if not isinstance(record, dict):
            raise PublicationJournalError("Manifestin pitää olla JSON-objekti.")
        module_id = _safe_id(record.get("module_id"))
        run_id = _safe_id(record.get("run_id"))
        required = {"module_id", "run_id", "idempotency_key", "report_sha256",
                    "artifacts_sha256", "state_sha256", "artifact_version",
                    "publication_targets", "prepared_at"}
        if set(record) != required:
            raise PublicationJournalError("Manifestin kentät eivät vastaa sopimusta.")
        if not isinstance(record["publication_targets"], list):
            raise PublicationJournalError("Julkaisukohteiden pitää olla lista.")
        if any(not isinstance(item, str) or not item for item in record["publication_targets"]):
            raise PublicationJournalError("Julkaisukohteessa on virheellinen tunniste.")
        path = self._path(module_id, run_id)
        with _lock(path):
            if path.exists():
                existing = json.loads(path.read_text(encoding="utf-8"))
                stable = {key: value for key, value in existing.items()
                          if key not in {"phase", "updated_at", "receipt", "state_sha256", "artifact_version"}}
                if stable != record:
                    raise PublicationJournalConflict("Sama moduuli/run_id on varattu eri julkaisusisällölle.")
                return existing
            manifest = {**record, "phase": "prepared", "updated_at": record["prepared_at"],
                        "receipt": None}
            _atomic_write(path, manifest)
            return manifest

    def load(self, module_id: str, run_id: str) -> dict[str, Any]:
        """Lue ja tarkista yhden ajon manifesti."""
        path = self._path(module_id, run_id)
        try:
            manifest = json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError as exc:
            raise PublicationJournalError("Julkaisumanifestia ei löydy.") from exc
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise PublicationJournalError("Julkaisumanifestia ei voi lukea.") from exc
        if manifest.get("module_id") != module_id or manifest.get("run_id") != run_id:
            raise PublicationJournalError("Manifestin tunnisteet eivät vastaa tiedostoa.")
        if manifest.get("phase") not in PHASES:
            raise PublicationJournalError("Manifestin vaihe on tuntematon.")
        return manifest

    def advance(self, module_id: str, run_id: str, phase: str,
                *, updated_at: str, receipt: dict[str, Any] | None = None) -> dict[str, Any]:
        """Siirrä manifestia vain eteenpäin; jo saavutettu vaihe on idempotentti."""
        if phase not in PHASES:
            raise PublicationJournalError("Pyydetty manifestivaihe on tuntematon.")
        path = self._path(module_id, run_id)
        with _lock(path):
            try:
                current = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise PublicationJournalError("Manifestia ei voi lukea tilasiirtymää varten.") from exc
            current_index = PHASES.index(current.get("phase"))
            target_index = PHASES.index(phase)
            if target_index <= current_index:
                if receipt is not None and current.get("receipt") not in (None, receipt):
                    raise PublicationJournalConflict("Julkaisukuittaus poikkeaa manifestiin tallennetusta.")
                # Uusinta voi aloittaa koko orkestrointipolun alusta. Jo saavutettua
                # vaihetta ei kirjoiteta taaksepäin, vaan se hyväksytään idempotentisti.
                return current
            if target_index > current_index + 1:
                raise PublicationJournalConflict("Manifestivaihetta ei voi ohittaa.")
            current["phase"] = phase
            current["updated_at"] = updated_at
            if receipt is not None:
                current["receipt"] = receipt
            _atomic_write(path, current)
            return current
