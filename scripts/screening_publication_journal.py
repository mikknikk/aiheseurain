"""Näytösvahdin pysyvä julkaisupäiväkirja ja palautumisen eheystarkistukset.

Moduuli validoi GitHubissa säilytettävän ajokohtaisen tietueen. Se ei julkaise
RSS:ää eikä kirjoita GitHubiin. Sen tehtävä on estää saman ajon käsittely
ristiriitaisena tai uutena ajona silloin, kun edellinen julkaisu jäi kesken.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime
import hashlib
from pathlib import Path
from typing import Any
import json
import xml.etree.ElementTree as ET

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
                     feed_catalog: list[dict[str, Any]], *,
                     source_log: dict[str, Any] | None = None,
                     source_registry: dict[str, Any] | None = None,
                     module_state: dict[str, Any] | None = None,
                     feed_bytes: bytes | None = None) -> None:
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
    source_run_ids = [run["source_check_run_id"] for run in runs]
    if len(run_ids) != len(set(run_ids)):
        raise ScreeningJournalError("Julkaisupäiväkirjassa on sama run_id useammin kuin kerran.")
    if len(source_run_ids) != len(set(source_run_ids)):
        raise ScreeningJournalError("Julkaisupäiväkirjassa on sama source-check-run_id useammin kuin kerran.")

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
        if run["source_check_ended_at"] != run["period"]["end"]:
            raise ScreeningJournalError(f"{run['run_id']}: lähdetarkistusajon loppu ei vastaa seurantajakson loppua.")
        if run["feed"]["item_count"] != len(run["feed"]["guids"]):
            raise ScreeningJournalError(f"{run['run_id']}: RSS-itemien määrä ei vastaa GUID-listaa.")

    if runs:
        latest = max(runs, key=lambda run: _time(run["prepared_at"], "prepared_at"))
        last_success = state.get("separate_screening_watch", {}).get("last_successful_check")
        if pending and latest["run_id"] != pending[0]["run_id"]:
            raise ScreeningJournalError("Keskeneräisen ajon pitää olla päiväkirjan viimeisin ajo.")
        if latest["phase"] == "prepared":
            if last_success != latest["period"]["start"]:
                raise ScreeningJournalError(
                    "Keskeneräisen ajon pitää säilyttää edellinen onnistunut tarkistuspiste."
                )
        elif last_success != latest["period"]["end"]:
            raise ScreeningJournalError(
                "Viimeisimmän valmiin päiväkirjamerkinnän jakson loppu ei vastaa seurantatilan onnistumispistettä."
            )


    # Kun kaikki riippuvat aineistot annetaan, tarkistetaan niiden keskinäiset
    # viitteet. Yksikkötestit voivat kutsua perusvalidointia pienillä fixtureillä.
    cross_values = (source_log, source_registry, module_state, feed_bytes)
    if any(value is not None for value in cross_values):
        if any(value is None for value in cross_values):
            raise ScreeningJournalError("Ristiviittausten tarkistus vaatii lähdelokin, lähderekisterin, moduulitilan ja RSS-tavut.")
        if runs:
            _validate_cross_references(
                latest, state, source_log, source_registry, module_state, feed_bytes
            )


def _validate_cross_references(latest: dict[str, Any], state: dict[str, Any],
                               source_log: dict[str, Any], source_registry: dict[str, Any],
                               module_state: dict[str, Any], feed_bytes: bytes) -> None:
    """Vertaa viimeisintä päiväkirja-ajoa sen todellisiin RSS- ja tilatiedostoihin."""
    # RSS-tavut ovat kanoninen sisältö. Hash, item-määrä ja GUIDit tarkistetaan
    # samoista tavuista, jotta eri tiedostojen välinen vertailu ei perustu otsikoihin.
    actual_hash = hashlib.sha256(feed_bytes).hexdigest()
    if actual_hash != latest["feed"]["sha256"]:
        raise ScreeningJournalError("RSS-tiedoston SHA-256 ei vastaa päiväkirjan ehdokasta.")
    try:
        root = ET.fromstring(feed_bytes)
    except ET.ParseError as exc:
        raise ScreeningJournalError(f"Julkaistu RSS ei ole kelvollista XML:ää: {exc}") from exc
    channel = root.find("channel")
    if channel is None:
        raise ScreeningJournalError("Näytösvahtisyötteen channel-elementti puuttuu.")
    items = channel.findall("item")
    actual_guids = [(item.findtext("guid") or "").strip() for item in items]
    if len(items) != latest["feed"]["item_count"]:
        raise ScreeningJournalError("RSS-itemien määrä ei vastaa päiväkirjan item_count-arvoa.")
    if actual_guids != latest["feed"]["guids"]:
        raise ScreeningJournalError("RSS-itemien GUID-järjestys tai sisältö ei vastaa päiväkirjaa.")
    if not all(actual_guids) or len(actual_guids) != len(set(actual_guids)):
        raise ScreeningJournalError("RSS:ssä on puuttuva tai kahdentunut GUID.")

    # Päiväkirjan source-check-tunnisteen on osoitettava yhteen täydelliseen
    # näytösvahtiajoon. Tämä säilyy palautettavana myös, jos seuraava vaihe keskeytyy.
    source_runs = [
        run for run in source_log.get("runs", [])
        if run.get("run_id") == latest["source_check_run_id"]
    ]
    if len(source_runs) != 1:
        raise ScreeningJournalError("Päiväkirjan lähdeajon tunniste ei osoita täsmälleen yhteen lokimerkintään.")
    source_run = source_runs[0]
    if source_run.get("task_id") != TASK_ID or source_run.get("status") != "complete":
        raise ScreeningJournalError("Päiväkirjan lähdeajon tehtävätunniste tai tila ei ole kelvollinen.")
    if source_run.get("ended_at") != latest["source_check_ended_at"]:
        raise ScreeningJournalError("Päiväkirjan ja lähdetarkistuslokin päättymisajat eroavat.")
    if source_run.get("ended_at") != latest["period"]["end"]:
        raise ScreeningJournalError("Lähdetarkistusajon päättymisaika ei vastaa seurantajakson loppua.")

    checked = set(source_run.get("checked_source_ids", []))
    unchecked_list = [item.get("source_id") for item in source_run.get("unchecked_sources", [])]
    unchecked = set(unchecked_list)
    registry_ids = set(source_run.get("registry_source_ids", []))
    if (None in unchecked or len(unchecked_list) != len(unchecked)
            or checked & unchecked or checked | unchecked != registry_ids):
        raise ScreeningJournalError("Lähdeajon tarkistetut, tarkistamatta jääneet ja rekisterin lähdejoukot eivät täsmää.")

    # Viimeisimmän lähdeajon pitää olla myös tehtävän latest_by_task-viite.
    if source_log.get("latest_by_task", {}).get(TASK_ID) != source_run.get("ended_at"):
        raise ScreeningJournalError("latest_by_task ei osoita päiväkirjan viimeisimpään näytösvahtiajoon.")

    registry_sources = source_registry.get("sources", [])
    registry_by_id = {item.get("source_id"): item for item in registry_sources}
    if len(registry_by_id) != len(registry_sources) or set(registry_by_id) != registry_ids:
        raise ScreeningJournalError("Näytösvahtiajon lähdejoukko ei vastaa aihekohtaista lähderekisteriä.")

    started = _time(source_run["started_at"], "source_run.started_at")
    ended = _time(source_run["ended_at"], "source_run.ended_at")
    for source_id in checked:
        checked_at = registry_by_id[source_id].get("last_checked_at")
        if checked_at is None:
            raise ScreeningJournalError(f"Tarkistetulta lähteeltä {source_id} puuttuu last_checked_at.")
        checked_time = _time(checked_at, f"{source_id}.last_checked_at")
        if checked_time < started or checked_time > ended:
            raise ScreeningJournalError(f"Lähteen {source_id} tarkistusaika ei kuulu tähän lähdeajoon.")
    for source_id in unchecked:
        checked_at = registry_by_id[source_id].get("last_checked_at")
        if checked_at is not None and _time(checked_at, f"{source_id}.last_checked_at") >= started:
            raise ScreeningJournalError(f"Tarkistamatta jääneen lähteen {source_id} tarkistusaika on virheellisesti päivitetty.")

    # Legacy-seurantatila saa siirtyä vasta, kun Pages on varmennettu ja
    # päiväkirja merkitään completed-tilaan. Valmistellussa ajossa vanha
    # onnistumispiste ja sitä vastaava edellinen jakson loppu säilyvät.
    watch = state.get("separate_screening_watch", {})
    if latest["phase"] == "prepared":
        if watch.get("last_period_end") != latest["period"]["start"]:
            raise ScreeningJournalError("Keskeneräinen ajo ei säilytä edellisen jakson loppua seurantatilassa.")
    else:
        if (watch.get("last_period_start") != latest["period"]["start"]
                or watch.get("last_period_end") != latest["period"]["end"]
                or watch.get("last_result") != "success"
                or watch.get("sources_checked") != len(checked)):
            raise ScreeningJournalError("Valmiin päiväkirja-ajon seurantatiedot eivät vastaa lähdeajoa ja seurantajaksoa.")

    # Moduulitila säilyttää lähdeajon viitteen ja koko syötteen GUID-joukon.
    # Sen migraation checkpoint voi olla tarkoituksellisesti vanha snapshot,
    # joten sitä ei verrata legacy-seurantatilan viimeisimpään onnistumiseen.
    history_refs = module_state.get("history", {}).get("source_check_run_refs", [])
    if latest["source_check_run_id"] not in history_refs:
        raise ScreeningJournalError("Moduulitilan historiasta puuttuu päiväkirjan lähdeajon viite.")
    publication = module_state.get("publication", {})
    if publication.get("feed_path") != latest["feed"]["path"]:
        raise ScreeningJournalError("Moduulitilan julkaisupolku ei vastaa näytösvahtisyötettä.")
    module_guids = publication.get("guid_refs", [])
    if len(module_guids) != len(set(module_guids)) or set(module_guids) != set(actual_guids):
        raise ScreeningJournalError("Moduulitilan GUID-viitteet eivät vastaa julkaistua RSS-syötettä.")


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
                 rss_verified_at: str, synchronization_commit_sha: str,
                 rss_verified: bool, state_synchronized: bool) -> dict[str, Any]:
    """Merkitse ajo valmiiksi vasta julkisen RSS:n ja tilasynkronoinnin varmennuttua."""
    if rss_verified is not True or state_synchronized is not True:
        raise ScreeningJournalError("Ajon valmistuminen vaatii julkisen RSS:n ja tilasynkronoinnin varmennuksen.")
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
    verified_time = _time(rss_verified_at, "rss_verified_at")
    prepared_time = _time(run["prepared_at"], "prepared_at")
    if verified_time < prepared_time:
        raise ScreeningJournalError("RSS-varmennus ei voi edeltää julkaisun valmistelua.")
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
