"""Yleiskäyttöinen tapahtumien tunnistus-, vertailu- ja historiaydin.

Ydin ei tunne yksittäisiä aiheita, tapahtumapaikkoja tai lähdepalveluja. Tapahtumatyypin
määritys kertoo seurattavat kentät ja tilat. Tämä moduuli käsittelee vain sille annettuja
havaintoja: se ei hae verkosta, kirjoita tiedostoja eikä käynnistä automaatioita.
"""
from __future__ import annotations
from copy import deepcopy
from datetime import datetime
import hashlib
import json
from pathlib import Path
from typing import Any
import jsonschema

ROOT = Path(__file__).resolve().parents[1]
TYPE_SCHEMA = ROOT / "schemas/event-watch/event-type.schema.json"
HISTORY_SCHEMA = ROOT / "schemas/event-watch/event-history.schema.json"
CLAIM_LEVELS = {"official", "organizer", "third_party", "unknown"}

class EventWatchError(ValueError):
    """Tapahtumatyypin tai tapahtumahistorian sopimusrikkomus."""

def _read_json(path: Path) -> dict[str, Any]:
    """Lue JSON-objekti ja anna ymmärrettävä virhe virheellisestä tiedostosta."""
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise EventWatchError(f"Tiedostoa {path} ei voi lukea kelvollisena JSONina: {exc}") from exc
    if not isinstance(value, dict):
        raise EventWatchError(f"Tiedoston {path} ylimmän tason arvon pitää olla objekti.")
    return value

def _validator(path: Path):
    """Lataa paikallisen skeeman ja tarkistaa myös skeeman oman rakenteen."""
    schema = _read_json(path)
    jsonschema.Draft202012Validator.check_schema(schema)
    return jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker())

def load_event_type(path: Path) -> dict[str, Any]:
    """Lue ja validoi tapahtumatyypin versioitu määritys."""
    definition = _read_json(path)
    errors = sorted(_validator(TYPE_SCHEMA).iter_errors(definition), key=lambda item: list(item.path))
    if errors:
        first = errors[0]
        raise EventWatchError(f"Tapahtumatyypin määritysvirhe kohdassa {list(first.path)}: {first.message}")
    allowed = set(definition["statuses"])
    for key in ("cancelled_statuses", "removed_statuses", "completed_statuses"):
        if not set(definition[key]).issubset(allowed):
            raise EventWatchError(f"{key} sisältää tuntemattoman tilan.")
    return definition

def empty_state(event_type_id: str) -> dict[str, Any]:
    """Luo uuden tyhjän tilan muuttamatta tiedostoja."""
    if not event_type_id:
        raise EventWatchError("Tapahtumatyypin tunniste ei saa olla tyhjä.")
    return {"schema_version": 1, "event_type_id": event_type_id, "current_events": [], "events": [], "scans": []}

def _timestamp(value: str) -> None:
    """Vaadi ISO 8601 -aikaleima, jossa on eksplisiittinen aikavyöhyke."""
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, TypeError, ValueError) as exc:
        raise EventWatchError(f"Virheellinen ISO 8601 -aikaleima: {value!r}") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise EventWatchError(f"Aikaleimasta puuttuu aikavyöhyke: {value}")

def _json(value: Any) -> str:
    """Tuota vakaa JSON-esitys tunnisteiden muodostamista varten."""
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

def _stable_id(prefix: str, value: Any) -> str:
    """Muodosta deterministinen tunniste SHA-256-tiivisteellä."""
    return prefix + "-" + hashlib.sha256(_json(value).encode("utf-8")).hexdigest()[:24]

def _source(source: dict[str, Any]) -> dict[str, Any]:
    """Tarkista lähteen jäljitettävyystiedot ja säilytä alkuperäinen vahvistusluokka."""
    for key in ("publisher", "url", "checked_at"):
        if not isinstance(source.get(key), str) or not source[key].strip():
            raise EventWatchError(f"Lähteeltä puuttuu pakollinen kenttä {key}.")
    if not source["url"].startswith(("https://", "http://")):
        raise EventWatchError("Lähteen URL-osoitteen pitää käyttää HTTP(S)-protokollaa.")
    _timestamp(source["checked_at"])
    level = source.get("claim_level", "unknown")
    if level not in CLAIM_LEVELS:
        raise EventWatchError(f"Tuntematon lähteen vahvistustaso: {level}")
    result = {key: source[key] for key in ("publisher", "url", "checked_at")}
    result["claim_level"] = level
    if source.get("published_at") is not None:
        _timestamp(source["published_at"])
        result["published_at"] = source["published_at"]
    if source.get("original_claim_type"):
        result["original_claim_type"] = source["original_claim_type"]
    return result

def _sources(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Deduplikoi saman julkaisijan, URL:n ja vahvistusluokan lähteet."""
    found = {}
    for item in items:
        value = _source(item)
        key = (value["publisher"], value["url"], value["claim_level"])
        if key not in found or value["checked_at"] > found[key]["checked_at"]:
            found[key] = value
    return [found[key] for key in sorted(found)]

def _identity(attributes: dict[str, Any], definition: dict[str, Any]) -> str:
    """Laske identiteetti tapahtumatyypin määrittelemistä kentistä."""
    fields = definition["identity_fields"]
    missing = [field for field in fields if attributes.get(field) in (None, "")]
    if missing:
        raise EventWatchError(f"Tapahtuman identiteetistä puuttuu kenttiä: {missing}")
    return _stable_id("identity", {"type": definition["event_type_id"], "fields": {key: attributes[key] for key in fields}})

def validate_state(state: dict[str, Any], definition: dict[str, Any]) -> None:
    """Validoi yleisen tilan rakenteen, tyypin ja tunnisteiden yksilöllisyyden."""
    if state.get("event_type_id") != definition["event_type_id"]:
        raise EventWatchError("Tapahtumatilan tyyppi ei vastaa määritystä.")
    errors = sorted(_validator(HISTORY_SCHEMA).iter_errors(state), key=lambda item: list(item.path))
    if errors:
        first = errors[0]
        raise EventWatchError(f"Tapahtumahistorian virhe kohdassa {list(first.path)}: {first.message}")
    current_ids = [item["canonical_event_id"] for item in state["current_events"]]
    history_ids = [item["event_id"] for item in state["events"]]
    if len(current_ids) != len(set(current_ids)) or len(history_ids) != len(set(history_ids)):
        raise EventWatchError("Nykytilassa tai tapahtumahistoriassa on duplikaattitunniste.")

def _history_event(definition, canonical_id, action, observed_at, previous, current, sources, categories=None):
    """Rakenna append-only-tapahtuma deterministisellä tunnisteella."""
    payload = {"event_type_id": definition["event_type_id"], "canonical_event_id": canonical_id,
               "action": action, "observed_at": observed_at, "previous": previous,
               "current": current, "sources": sources, "categories": sorted(set(categories or []))}
    item = {"event_id": _stable_id("evt", payload), "observed_at": observed_at,
            "event_type_id": definition["event_type_id"], "canonical_event_id": canonical_id,
            "action": action, "previous": previous, "current": current, "sources": sources,
            "note": "Tapahtuman havaittu tila tai seurattavat tiedot muuttuivat."}
    if categories:
        item["change_categories"] = sorted(set(categories))
    return item

def reconcile(state: dict[str, Any], observations: list[dict[str, Any]], definition: dict[str, Any],
              observed_at: str, *, scan_complete: bool = True,
              failed_sources: list[str] | None = None) -> dict[str, Any]:
    """Yhdistä havainnot nykytilaan ja lisää vain aidot muutokset historiaan.

    Puuttuva havainto ei koskaan tarkoita poistumista. Poistuma ja peruutus vaativat
    sovittimelta nimenomaisen tilatiedon. Osittaisen haun epäonnistumiset kirjataan.
    """
    _timestamp(observed_at)
    validate_state(state, definition)
    result = deepcopy(state)
    current = {item["canonical_event_id"]: item for item in result["current_events"]}
    grouped: dict[str, list[dict[str, Any]]] = {}
    for observation in observations:
        if observation.get("event_type_id") != definition["event_type_id"]:
            raise EventWatchError("Havainto kuuluu eri tapahtumatyyppiin.")
        canonical_id = observation.get("canonical_event_id")
        attributes = observation.get("attributes")
        if not isinstance(canonical_id, str) or not canonical_id.strip() or not isinstance(attributes, dict):
            raise EventWatchError("Havainnolta puuttuu kanoninen tunniste tai attribuutit.")
        missing = [key for key in definition["required_attributes"] if attributes.get(key) in (None, "")]
        if missing:
            raise EventWatchError(f"Havainnosta puuttuu pakollisia attribuutteja: {missing}")
        if attributes.get(definition["status_field"]) not in definition["statuses"]:
            raise EventWatchError("Havainnolla on tuntematon tilatieto.")
        source_list = _sources(observation.get("sources", []))
        if not source_list:
            raise EventWatchError("Havainnolla pitää olla vähintään yksi lähde.")
        _identity(attributes, definition)
        _timestamp(observation.get("observed_at", observed_at))
        grouped.setdefault(canonical_id, []).append({"attributes": deepcopy(attributes), "sources": source_list})

    new_events = []
    for canonical_id in sorted(grouped):
        group = grouped[canonical_id]
        sources = _sources([source for item in group for source in item["sources"]])
        old = current.get(canonical_id)
        previous = deepcopy(old) if old else None
        attributes = {}
        conflicts = []
        fields = sorted({field for item in group for field in item["attributes"]})
        for field in fields:
            values = {}
            for item in group:
                if field in item["attributes"]:
                    key = _json(item["attributes"][field])
                    values.setdefault(key, item["attributes"][field])
            if len(values) == 1:
                attributes[field] = next(iter(values.values()))
            else:
                conflicts.append({"field": field, "values": [values[key] for key in sorted(values)], "sources": sources})
                if old and field in old["attributes"]:
                    attributes[field] = old["attributes"][field]
                elif field in definition["required_attributes"]:
                    raise EventWatchError(
                        f"Uuden tapahtuman pakollinen kenttä {field} on ristiriitainen; "
                        "tapahtumaa ei voi luoda turvallisesti."
                    )
        if old:
            for field, value in old["attributes"].items():
                attributes.setdefault(field, value)
            # Aiempi ratkaisematon ristiriita ei katoa vain siksi, ettei tämän ajon
            # havaintoryhmä toista sitä. Korjaus vaatii uuden, yksiselitteisen päätöksen.
            if old.get("conflicts") and not conflicts:
                conflicts = deepcopy(old["conflicts"])
        status = attributes[definition["status_field"]]
        if old is None:
            action, categories, first_seen = "created", [], observed_at
        else:
            old_status = old["status"]
            cancelled = set(definition["cancelled_statuses"])
            removed = set(definition["removed_statuses"])
            completed = set(definition["completed_statuses"])
            if status in cancelled and old_status not in cancelled:
                action, categories = "cancelled", []
            elif status in removed and old_status not in removed:
                action, categories = "removed", []
            elif status in completed and old_status not in completed:
                action, categories = "completed", []
            elif status not in cancelled | removed | completed and old_status in cancelled | removed:
                action, categories = "reinstated", []
            else:
                categories = sorted({definition["tracked_attributes"][field]
                    for field in definition["tracked_attributes"]
                    if old["attributes"].get(field) != attributes.get(field)})
                action = "changed" if categories else ""
            first_seen = old["first_seen_at"]
            if conflicts:
                action = "source_conflict"
        snapshot = {"canonical_event_id": canonical_id, "event_type_id": definition["event_type_id"],
                    "identity_key": _identity(attributes, definition), "attributes": attributes,
                    "status": status, "sources": sources, "first_seen_at": first_seen, "last_seen_at": observed_at}
        if conflicts:
            snapshot["conflicts"] = conflicts
        if action:
            new_events.append(_history_event(definition, canonical_id, action, observed_at,
                                             previous, deepcopy(snapshot), sources, categories))
        elif old:
            snapshot["first_seen_at"] = old["first_seen_at"]
        current[canonical_id] = snapshot

    result["current_events"] = [current[key] for key in sorted(current)]
    known = {item["event_id"] for item in result["events"]}
    result["events"].extend(item for item in new_events if item["event_id"] not in known)
    result["scans"].append({"observed_at": observed_at, "complete": bool(scan_complete),
                            "failed_sources": sorted(set(failed_sources or []))})
    validate_state(result, definition)
    return result
