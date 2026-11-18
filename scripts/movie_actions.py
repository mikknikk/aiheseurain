"""Elokuvahavaintojen kriteerikohtainen jatkotoimien outbox ja Discord-liitäntä.

Tuotannon toimintomääritys on tyhjä. Testit käyttävät vain testikriteeriä ja
injektoitua kuljetinta; webhook-salaisuutta ei tallenneta rekisteriin tai lokiin.
"""
from __future__ import annotations

from copy import deepcopy
import fcntl
import hashlib
import json
from pathlib import Path
import tempfile
from typing import Any, Callable
import jsonschema

ROOT = Path(__file__).resolve().parents[1]
CONFIG_SCHEMA = ROOT / "schemas/movie-action-config.schema.json"
OUTBOX_SCHEMA = ROOT / "schemas/movie-action-outbox.schema.json"
EVENT_SCHEMA = ROOT / "schemas/movie-action-event.schema.json"


class MovieActionError(ValueError):
    """Jatkotoimen määrityksen, payloadin tai toimituksen virhe."""


class ActionOutboxConflictError(MovieActionError):
    """Outboxin SHA-versio muuttui ennen tallennusta."""


def _canonical(value: Any) -> bytes:
    """Muunna JSON-tietue vakaaksi tavujonoksi."""
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _sha(content: bytes) -> str:
    """Laske tiedoston SHA-256-versio."""
    return hashlib.sha256(content).hexdigest()


def _validate(value: dict[str, Any], schema_path: Path, label: str) -> None:
    """Validoi JSON-tietue paikallista skeemaa vasten."""
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(schema)
    errors = sorted(
        jsonschema.Draft202012Validator(
            schema, format_checker=jsonschema.FormatChecker()
        ).iter_errors(value),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        first = errors[0]
        raise MovieActionError(f"{label} virhe kohdassa {list(first.absolute_path)}: {first.message}")


def validate_action_config(config: dict[str, Any]) -> None:
    """Tarkista kriteeriin sidotut toiminnot ja niiden versiot."""
    _validate(config, CONFIG_SCHEMA, "Toimintomäärityksen")
    keys = [(item["criterion_id"], item["action_id"], item["version"]) for item in config["actions"]]
    if len(keys) != len(set(keys)):
        raise MovieActionError("Toimintomäärityksessä on sama kriteeri/toiminto/versio useammin kuin kerran.")


def empty_outbox() -> dict[str, Any]:
    """Luo tyhjän toimitusjonon."""
    return {"schema_version": 1, "actions": []}


def validate_outbox(outbox: dict[str, Any]) -> None:
    """Tarkista toimitusjonon rakenne ja idempotenssiavainten yksilöllisyys."""
    _validate(outbox, OUTBOX_SCHEMA, "Toimitusjonon")
    keys = [item["idempotency_key"] for item in outbox["actions"]]
    event_ids = [item["event_id"] for item in outbox["actions"]]
    if len(keys) != len(set(keys)) or len(event_ids) != len(set(event_ids)):
        raise MovieActionError("Toimitusjonossa on duplikaatti-idempotenssiavain tai tapahtumatunniste.")


def _idempotency_key(movie_id: str, criterion_id: str, action_id: str, version: str) -> str:
    """Yksilöi toiminnon elokuvan, osumakriteerin ja toimintoversion mukaan."""
    raw = "|".join((movie_id, criterion_id, action_id, version))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def enqueue_movie_actions(
    movie: dict[str, Any], config: dict[str, Any], outbox: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    """Lisää jokaiselle uudelle kriteeriosumalle sille määritellyt toiminnot kerran."""
    validate_action_config(config)
    validate_outbox(outbox)
    result = deepcopy(outbox)
    existing = {item["idempotency_key"] for item in result["actions"]}
    criterion_ids = {item["criterion_id"] for item in movie["criterion_matches"]}
    for action in sorted(config["actions"], key=lambda item: (
        item["criterion_id"], item["action_id"], item["version"]
    )):
        if not action["enabled"] or action["criterion_id"] not in criterion_ids:
            continue
        key = _idempotency_key(
            movie["movie_id"], action["criterion_id"], action["action_id"], action["version"]
        )
        if key in existing:
            continue
        criterion_source_urls = sorted({
            url
            for match in movie["criterion_matches"]
            if match["criterion_id"] == action["criterion_id"]
            for url in match["source_urls"]
        })
        if not criterion_source_urls:
            raise MovieActionError(
                f"Kriteerillä {action['criterion_id']} ei ole lähdeviitteitä; toimintoa ei jonoteta."
            )
        payload = {
            "schema_version": 1,
            "event_type": "movie_first_observed",
            "movie_id": movie["movie_id"],
            "title": movie["primary_title"],
            "release_year": movie["release_year"],
            "first_seen_at": movie["first_seen_at"],
            "criterion_id": action["criterion_id"],
            "action_id": action["action_id"],
            "action_version": action["version"],
            "screening_refs": sorted(movie["screening_refs"]),
            "source_urls": criterion_source_urls,
        }
        _validate(payload, EVENT_SCHEMA, "Toimintotapahtuman")
        event_id = "action-" + hashlib.sha256(key.encode("utf-8")).hexdigest()[:24]
        result["actions"].append({
            "event_id": event_id,
            "idempotency_key": key,
            "criterion_id": action["criterion_id"],
            "action_id": action["action_id"],
            "action_version": action["version"],
            "action_type": action["type"],
            "movie_id": movie["movie_id"],
            "payload": payload,
            "status": "pending",
            "attempts": 0,
            "created_at": created_at,
            "updated_at": created_at,
            "sent_at": None,
            "last_error_code": None,
        })
        existing.add(key)
    result["actions"].sort(key=lambda item: item["idempotency_key"])
    validate_outbox(result)
    return result


class DiscordWebhookAdapter:
    """Discord-webhookin liitäntä, jonka kuljetin ja salaisuus annetaan ajonaikaisesti."""

    def __init__(self, webhook_url: str, transport: Callable[[str, dict[str, Any], str], Any]):
        if not isinstance(webhook_url, str) or not webhook_url.startswith("https://discord.com/api/webhooks/"):
            raise MovieActionError("Discord-webhookin osoite puuttuu tai ei ole sallittu HTTPS-osoite.")
        if not callable(transport):
            raise MovieActionError("Discord-webhookin kuljetin puuttuu.")
        self.__webhook_url = webhook_url
        self.__transport = transport

    def __repr__(self) -> str:
        """Älä paljasta webhook-osoitetta debug-tulosteessa."""
        return "DiscordWebhookAdapter(webhook_url=<redacted>)"

    def send(self, payload: dict[str, Any], idempotency_key: str) -> None:
        """Lähetä payload injektoidun kuljettimen kautta ilman salaisuuden lokitusta."""
        self.__transport(self.__webhook_url, payload, idempotency_key)


def dispatch_pending_actions(
    outbox: dict[str, Any], adapters: dict[str, Any], attempted_at: str,
    *, max_attempts: int = 3,
) -> dict[str, Any]:
    """Yritä lähettää pending-toiminnot; säilytä virheelliset uusintaa varten."""
    validate_outbox(outbox)
    if max_attempts < 1:
        raise MovieActionError("max_attempts-arvon pitää olla vähintään yksi.")
    result = deepcopy(outbox)
    for action in result["actions"]:
        if action["status"] != "pending":
            continue
        adapter = adapters.get(action["action_type"])
        try:
            if adapter is None:
                raise MovieActionError("Toiminnolle ei ole rekisteröity sovitinta.")
            adapter.send(action["payload"], action["idempotency_key"])
        except Exception as exc:
            action["attempts"] += 1
            action["updated_at"] = attempted_at
            action["last_error_code"] = type(exc).__name__
            if action["attempts"] >= max_attempts:
                action["status"] = "failed"
        else:
            action["attempts"] += 1
            action["updated_at"] = attempted_at
            action["sent_at"] = attempted_at
            action["status"] = "sent"
            action["last_error_code"] = None
    validate_outbox(result)
    return result


class JsonFileActionOutboxStore:
    """Paikallinen SHA-tarkistettu toimitusjono testaukseen ja palautuvaan käsittelyyn."""

    def __init__(self, path: Path):
        self.path = Path(path).resolve()

    def load(self) -> tuple[dict[str, Any], str]:
        """Lue toimitusjono tai palauta tyhjä jono."""
        try:
            content = self.path.read_bytes()
        except FileNotFoundError:
            return empty_outbox(), "missing"
        try:
            value = json.loads(content.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise MovieActionError("Toimitusjonon JSON on virheellinen.") from exc
        validate_outbox(value)
        return value, _sha(content)

    def save(self, outbox: dict[str, Any], *, expected_sha: str) -> str:
        """Tallenna jono vain, jos odotettu SHA-versio on edelleen voimassa."""
        validate_outbox(outbox)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        lock_path = self.path.with_name(self.path.name + ".lock")
        with lock_path.open("a+b") as lock:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
            try:
                try:
                    current = _sha(self.path.read_bytes())
                except FileNotFoundError:
                    current = "missing"
                if current != expected_sha:
                    raise ActionOutboxConflictError("Toimitusjono muuttui ennen tallennusta.")
                content = _canonical(outbox) + b"\n"
                temporary = None
                try:
                    with tempfile.NamedTemporaryFile(
                        mode="wb", dir=self.path.parent, prefix=f".{self.path.name}.",
                        suffix=".tmp", delete=False
                    ) as stream:
                        temporary = Path(stream.name)
                        stream.write(content)
                        stream.flush()
                        import os
                        os.fsync(stream.fileno())
                    import os
                    os.replace(temporary, self.path)
                finally:
                    if temporary is not None and temporary.exists():
                        temporary.unlink()
                return _sha(content)
            finally:
                fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
