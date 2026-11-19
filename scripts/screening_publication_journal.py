"""Näytösvahdin pysyvä julkaisupäiväkirja ja palautumisen eheystarkistukset.

Moduuli validoi GitHubissa säilytettävän ajokohtaisen tietueen. Se ei julkaise
RSS:ää eikä kirjoita GitHubiin. Sen tehtävä on estää saman ajon käsittely
ristiriitaisena tai uutena ajona silloin, kun edellinen julkaisu jäi kesken.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Any
import json

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas/screening-publication-journal.schema.json"
JOURNAL_PATH = ROOT / "data/screening-publication-journal.json"
TASK_ID = "intialaiset_elokuvat_naytokset"
FEED_PATH = "feeds/intialaisten-elokuvien-naytokset.xml"


class ScreeningJournalError(ValueError):
    """Päiväkirjan rakenne, ajotunniste tai tilasiirtymä on ristiriitainen."""


def _time(value: str, label: str) -> datetime:
    """Lue aikavyöhykkeellinen ISO-aika, jotta jaksoja voidaan verrata oikein."""
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, TypeError, ValueError) as exc:
        raise ScreeningJournalError(f"{label}: virheellinen ISO 8601 -aika.") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ScreeningJournalError(f"{label}: aikavyöhyke puuttuu.")
    return parsed


def validate_journal(journal: dict[str, Any], state: dict[str, Any],
                     feed_catalog: list[dict[str, Any]]) -> None:
    """Validoi skeeman lisäksi ajopäiväkirjan suhteet todelliseen seurantatilaan.

    Skeema tarkistaa yksittäisten kenttien muodot. Tämä funktio tarkistaa
    esimerkiksi, ettei keskeneräisen ajon onnistumispistettä ole jo siirretty.
    """
    try:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator.check_schema(schema)
        errors = sorted(
            jsonschema.Draft202012Validator(
                schema, format_checker=jsonschema.FormatChecker()
            ).iter_errors(journal),
            key=lambda error: list(error.path),
        )
    except (OSError, json.JSONDecodeError, jsonschema.SchemaError) as exc:
        raise ScreeningJournalError(f"Julkaisupäiväkirjan skeema ei ole kelvollinen: {exc}") from exc
    if errors:
        first = errors[0]
        location = ".".join(str(part) for part in first.path) or "juuri"
        raise ScreeningJournalError(f"Julkaisupäiväkirja, {location}: {first.message}")

    screening_feeds = [
        item.get("path") for item in feed_catalog
        if item.get("type") == "screening" and item.get("id") == "intialaisten-elokuvien-naytokset"
    ]
    if screening_feeds != [FEED_PATH]:
        raise ScreeningJournalError("Näytösvahtipäiväkirjan RSS-polku ei vastaa syötekatalogia.")

    runs = journal["runs"]
    run_ids = [run["run_id"] for run in runs]
    if len(run_ids) != len(set(run_ids)):
        raise ScreeningJournalError("Julkaisupäiväkirjassa on sama run_id useammin kuin kerran.")

    pending = [run for run in runs if run["phase"] == "prepared"]
    if len(pending) > 1:
        raise ScreeningJournalError("Julkaisupäiväkirjassa voi olla vain yksi keskeneräinen ajo.")

    for run in runs:
        period_start = _time(run["period"]["start"], f"{run['run_id']} period.start")
        period_end = _time(run["period"]["end"], f"{run['run_id']} period.end")
        if period_start > period_end:
            raise ScreeningJournalError(f"{run['run_id']}: seurantajakson alku on loppua myöhempi.")
        prepared_at = _time(run["prepared_at"], f"{run['run_id']} prepared_at")
        if prepared_at < period_end:
            raise ScreeningJournalError(f"{run['run_id']}: päiväkirja on valmisteltu ennen seurantajakson loppua.")
        if run["feed"]["item_count"] != len(run["feed"]["guids"]):
            raise ScreeningJournalError(f"{run['run_id']}: RSS-itemien määrä ei vastaa GUID-listaa.")

    if runs:
        latest = max(runs, key=lambda run: _time(run["prepared_at"], "prepared_at"))
        last_success = state.get("separate_screening_watch", {}).get("last_successful_check")
        if latest["phase"] == "prepared":
            if last_success != latest["period"]["start"]:
                raise ScreeningJournalError(
                    "Keskeneräisen ajon pitää säilyttää edellinen onnistunut tarkistuspiste."
                )
        elif last_success != latest["period"]["end"]:
            raise ScreeningJournalError(
                "Viimeisimmän valmiin päiväkirjamerkinnän jakson loppu ei vastaa seurantatilan onnistumispistettä."
            )


def prepare_run(journal: dict[str, Any], record: dict[str, Any]) -> dict[str, Any]:
    """Lisää valmistellun ajon kerran; saman tunnisteen eri sisältö hylätään."""
    updated = deepcopy(journal)
    run_id = record.get("run_id")
    existing = next((run for run in updated.get("runs", []) if run.get("run_id") == run_id), None)
    if existing is not None:
        if existing != record:
            raise ScreeningJournalError("Sama run_id on jo varattu eri julkaisusisällölle.")
        return updated
    if any(run.get("phase") == "prepared" for run in updated.get("runs", [])):
        raise ScreeningJournalError("Edellinen RSS-julkaisu on vielä kesken; palauta se ensin.")
    if record.get("phase") != "prepared":
        raise ScreeningJournalError("Uusi päiväkirjamerkintä pitää aloittaa prepared-vaiheesta.")
    updated.setdefault("runs", []).append(deepcopy(record))
    return updated


def complete_run(journal: dict[str, Any], run_id: str, *,
                 publication_commit_sha: str, deployment_id: int,
                 rss_verified_at: str, synchronization_commit_sha: str) -> dict[str, Any]:
    """Merkitse ajo valmiiksi vasta julkisen RSS:n ja tilasynkronoinnin varmennuttua."""
    updated = deepcopy(journal)
    run = next((item for item in updated.get("runs", []) if item.get("run_id") == run_id), None)
    if run is None:
        raise ScreeningJournalError("Valmisteltua ajoa ei löydy julkaisupäiväkirjasta.")
    completed_publication = {
        "commit_sha": publication_commit_sha,
        "deployment_id": deployment_id,
        "verified_at": rss_verified_at,
    }
    completed_sync = {"commit_sha": synchronization_commit_sha}
    if run["phase"] == "completed":
        if run["publication"] != completed_publication or run["synchronization"] != completed_sync:
            raise ScreeningJournalError("Valmiin ajon varmennustiedot eivät täsmää uusinnan kanssa.")
        return updated
    if run["phase"] != "prepared":
        raise ScreeningJournalError("Ajon vaihe ei salli valmistumista.")
    _time(rss_verified_at, "rss_verified_at")
    if not isinstance(deployment_id, int) or deployment_id < 1:
        raise ScreeningJournalError("Pages-deploymentin tunniste ei ole kelvollinen.")
    for value, label in (
        (publication_commit_sha, "publication_commit_sha"),
        (synchronization_commit_sha, "synchronization_commit_sha"),
    ):
        if not isinstance(value, str) or len(value) != 40 or any(ch not in "0123456789abcdef" for ch in value):
            raise ScreeningJournalError(f"{label} ei ole kelvollinen Git-commitin SHA.")
    run["publication"] = completed_publication
    run["synchronization"] = completed_sync
    run["phase"] = "completed"
    return updated
