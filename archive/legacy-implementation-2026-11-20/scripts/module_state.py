"""Moduulikohtaisen jatkuvuustilan validointi ja turvallinen checkpoint-siirtymä.

Tämä moduuli tarjoaa puhtaat tietorakennesiirtymät. Se ei käynnistä automaatioita
eikä kirjoita GitHubiin. Kutsujan on tallennettava tulos versionhallinnan SHA-
optimistisella päivityksellä, jotta rinnakkaisten ajojen kirjoitukset eivät yliaja
toisiaan.
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
STATE_SCHEMA = ROOT / "schemas/module-state.schema.json"


class ModuleStateError(ValueError):
    """Moduulikohtaisen tilan sopimusrikkomus."""


class StateConflictError(ModuleStateError):
    """Rinnakkainen ajo tai ristiriitainen uusintayritys havaittiin."""


def _validator():
    """Lataa paikallisen skeeman ja tarkistaa skeeman oman rakenteen."""
    schema = json.loads(STATE_SCHEMA.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(schema)
    return jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker())


def _timestamp(value: str) -> datetime:
    """Jäsennä aikavyöhykkeellinen ISO 8601 -aikaleima."""
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, TypeError, ValueError) as exc:
        raise ModuleStateError(f"Virheellinen aikaleima: {value!r}") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ModuleStateError(f"Aikaleimasta puuttuu aikavyöhyke: {value}")
    return parsed


def validate_module_state(state: dict[str, Any], definition: dict[str, Any] | None = None) -> None:
    """Validoi moduulitilan skeemalla ja haluttaessa moduulimäärittelyä vasten."""
    errors = sorted(_validator().iter_errors(state), key=lambda item: list(item.path))
    if errors:
        first = errors[0]
        raise ModuleStateError(f"Moduulitilan virhe kohdassa {list(first.path)}: {first.message}")
    if definition is not None:
        if state["module_id"] != definition["module_id"]:
            raise ModuleStateError("Moduulitilan tunniste ei vastaa moduulimäärittelyä.")
        if state["module_definition_version"] != definition["definition_version"]:
            raise ModuleStateError("Moduulitilan määritysversio ei vastaa nykyistä moduulimääritystä.")
    event_ids = [item["event_id"] for item in state["checkpoint_history"]]
    run_ids = [item["run_id"] for item in state["checkpoint_history"] if item["run_id"] is not None]
    if len(event_ids) != len(set(event_ids)) or len(run_ids) != len(set(run_ids)):
        raise ModuleStateError("Checkpoint-historiassa on duplikaattitunniste.")
    latest = state["checkpoint"]["last_successful_run"]
    if state["checkpoint_history"]:
        previous = state["checkpoint_history"][-1]
        for field in ("run_id", "run_history_ref", "definition_version", "checked_at",
                      "period", "result", "published_items", "sources_checked"):
            if previous[field] != latest[field]:
                raise ModuleStateError(f"Viimeisin checkpoint ei vastaa historiatapahtumaa kentässä {field}.")


def _canonical(value: Any) -> str:
    """Muunna arvo deterministiseksi JSONiksi vertailua ja tunnisteita varten."""
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _event_id(module_id: str, run_id: str) -> str:
    """Muodosta checkpoint-tapahtumalle deterministinen tunniste."""
    digest = hashlib.sha256(f"{module_id}:{run_id}".encode("utf-8")).hexdigest()[:32]
    return f"checkpoint-{digest}"


def commit_successful_checkpoint(
    state: dict[str, Any], *, run_id: str, definition_version: str,
    checked_at: str, period_start: str | None, period_end: str | None,
    run_status: str, source_scan_complete: bool, publication_verified: bool,
    published_items: int | None, sources_checked: int | None,
    source_check_run_refs: list[str], report_guid_refs: list[str],
    expected_previous_run_id: str | None, expected_previous_checked_at: str | None,
    run_history_ref: str | None = None, recorded_on: str | None = None,
) -> dict[str, Any]:
    """Päivitä checkpoint vain kokonaan onnistuneesta ja varmennetusta ajosta.

    Epäonnistunut tai osittainen ajo palauttaa alkuperäisen tilan muuttumattomana.
    Sama run_id ja sama sisältö on idempotentti uusinta. Sama run_id eri sisällöllä
    tai vanhentunut expected_previous_checkpoint aiheuttaa konfliktin.
    """
    validate_module_state(state)
    if run_status != "succeeded" or not source_scan_complete or not publication_verified:
        return deepcopy(state)
    if not run_id or not isinstance(run_id, str):
        raise ModuleStateError("Onnistuneella ajolla pitää olla pysyvä run_id.")
    if definition_version != state["module_definition_version"]:
        raise ModuleStateError("Ajon moduulimäärittelyversio ei vastaa tilan nykyistä versiota.")
    checked = _timestamp(checked_at)
    if (period_start is None) != (period_end is None):
        raise ModuleStateError("Seurantajakson alku ja loppu pitää antaa yhdessä.")
    if period_start is not None:
        start, end = _timestamp(period_start), _timestamp(period_end)
        if start > end:
            raise ModuleStateError("Seurantajakson alku on loppua myöhempi.")
    if published_items is not None and published_items < 0:
        raise ModuleStateError("Julkaistujen itemien määrä ei voi olla negatiivinen.")
    if sources_checked is not None and sources_checked < 0:
        raise ModuleStateError("Tarkistettujen lähteiden määrä ei voi olla negatiivinen.")

    result = deepcopy(state)
    checkpoint = result["checkpoint"]["last_successful_run"]
    period = {"start": period_start, "end": period_end}
    event_payload = {
        "run_id": run_id, "run_history_ref": run_history_ref,
        "definition_version": definition_version, "checked_at": checked_at,
        "period": period, "result": "published" if published_items is not None else "success",
        "published_items": published_items, "sources_checked": sources_checked,
        "source_check_run_refs": sorted(set(source_check_run_refs)),
        "report_guid_refs": sorted(set(report_guid_refs)),
    }

    # Uusintayritys tarkistetaan ennen checkpointin vertailua: aiemmin hyväksytyn
    # run_id:n toistaminen ei saa luoda uutta tapahtumaa eikä siirtää tilaa.
    for existing in result["checkpoint_history"]:
        if existing["run_id"] == run_id:
            comparable = {key: existing[key] for key in event_payload if key in existing}
            if _canonical(comparable) == _canonical(event_payload):
                return deepcopy(state)
            raise StateConflictError("Sama run_id on jo kirjattu eri checkpoint-sisällöllä.")

    if checkpoint["run_id"] != expected_previous_run_id or checkpoint["checked_at"] != expected_previous_checked_at:
        raise StateConflictError("Moduulin checkpoint muuttui rinnakkaisen ajon aikana; lue tila uudelleen.")
    if checkpoint["checked_at"] is not None and checked <= _timestamp(checkpoint["checked_at"]):
        raise StateConflictError("Vanhempi tai samanaikainen ajo ei saa siirtää onnistumisen checkpointia taaksepäin.")

    event = {
        "event_id": _event_id(state["module_id"], run_id), "source": "module_run",
        **event_payload, "recorded_on": recorded_on or checked_at[:10],
        "notes": "Onnistunut ajo kirjattu moduulikohtaiseksi checkpointiksi."
    }
    result["checkpoint_history"].append(event)
    result["checkpoint"]["last_successful_run"] = {
        "run_id": run_id, "run_history_ref": run_history_ref,
        "definition_version": definition_version, "checked_at": checked_at,
        "period": period, "result": event_payload["result"],
        "published_items": published_items, "sources_checked": sources_checked, "errors": []
    }
    result["history"]["source_check_run_refs"] = sorted(
        set(result["history"]["source_check_run_refs"]) | set(source_check_run_refs)
    )
    result["publication"]["guid_refs"] = list(dict.fromkeys(
        result["publication"]["guid_refs"] + report_guid_refs
    ))
    validate_module_state(result)
    return result
