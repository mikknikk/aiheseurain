"""Validoi moduulikohtaisen tilan migraatio vanhoista kanonisista tietolähteistä.

Tarkistus on vain lukeva. Se varmistaa, että vanhoja tarkistuspisteitä, lähdeajojen
tunnisteita, RSS-GUIDeja ja näytöshistorian tunnisteita ei ole muutettu tai keksitty.
"""
from __future__ import annotations
from pathlib import Path
from datetime import datetime
import json
import xml.etree.ElementTree as ET

from scripts.module_state import validate_module_state
from scripts.module_registry import ROOT, REGISTRY_PATH


MODULES = {
 "tolkien": {"task":"tolkien","feed":"feeds/tolkien.xml","pointer":"rotation.tasks.tolkien","docs":[("docs/seuranta.md","J. R. R. Tolkien")]},
 "taylor-swift": {"task":"taylor_swift","feed":"feeds/taylor-swift.xml","pointer":"rotation.tasks.taylor_swift","docs":[("docs/seuranta.md","Taylor Swift")]},
 "gurmeet-ram-rahim-singh": {"task":"gurmeet_ram_rahim_singh","feed":"feeds/gurmeet-ram-rahim-singh.xml","pointer":"rotation.tasks.gurmeet_ram_rahim_singh","docs":[("docs/seuranta.md","Saint Dr. Gurmeet Ram Rahim Singh Ji Insan")]},
 "muumit": {"task":"muumit","feed":"feeds/muumit.xml","pointer":"rotation.tasks.muumit","docs":[("docs/seuranta.md","Muumit")]},
 "wakaliwood": {"task":"wakaliwood","feed":"feeds/wakaliwood.xml","pointer":"rotation.tasks.wakaliwood","docs":[("docs/seuranta.md","Wakaliwood")]},
 "euroviisut": {"task":"euroviisut","feed":"feeds/euroviisut.xml","pointer":"rotation.tasks.euroviisut","docs":[("docs/seuranta.md","Euroviisut ja kansalliset karsinnat")]},
 "sompote-sands": {"task":"sompote_sands","feed":"feeds/sompote-sands.xml","pointer":"rotation.tasks.sompote_sands","docs":[("docs/seuranta.md","Sompote Sands")]},
 "shakkidraamat": {"task":"shakkidraamat","feed":"feeds/shakkidraamat.xml","pointer":"rotation.tasks.shakkidraamat","docs":[("docs/seuranta.md","Shakkidraamat")]},
 "indian-film-news": {"task":"intialaiset_elokuvat","feed":"feeds/intialaiset-elokuvat.xml","pointer":"rotation.tasks.intialaiset_elokuvat","docs":[("docs/seuranta.md","Intialaisen elokuvan seuranta (tehtäväkierron mukainen)"),("docs/intialaisen-elokuvan-seuranta.md","Seurattavat henkilöt"),("docs/intialaisen-elokuvan-seuranta.md","Erityisseurattavat projektit"),("docs/intialaisen-elokuvan-seuranta.md","Uutistapahtumien historiakirja"),("docs/intialaisen-elokuvan-seuranta.md","Suomalaisen median seuranta")]},
 "indian-film-screening-watch": {"task":"intialaiset_elokuvat_naytokset","feed":"feeds/intialaisten-elokuvien-naytokset.xml","pointer":"separate_screening_watch","screening":True,"docs":[("docs/intialaisten-elokuvien-naytosseuranta.md",None),("docs/intialaisen-elokuvan-seuranta.md","Suomen näytösten seuranta")]}
}
RUN_HISTORY = {
 "taylor-swift": {
  "run_id":"main-automation-20261117T105033Z-r01",
  "ref":"run-history/main-automation/history.json#main-automation-20261117T105033Z-r01"
 }
}


def _read(path: Path):
    """Lue JSON-tiedosto ilman sen muuttamista."""
    return json.loads(path.read_text(encoding="utf-8"))


def _feed_guids(path: Path) -> list[str]:
    """Poimi RSS-syötteen GUIDit alkuperäisessä järjestyksessä."""
    root = ET.parse(path).getroot()
    values = []
    for node in root.iter():
        if node.tag.rsplit("}", 1)[-1] == "guid" and node.text:
            values.append(node.text.strip())
    if len(values) != len(set(values)):
        raise ValueError(f"RSS-syötteessä {path} on duplikaatti-GUID.")
    return values


def _parse_datetime(value: str) -> datetime:
    """Jäsennä aikavyöhykkeellinen ISO-aikaleima vertailua varten."""
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def validate_state_migration() -> list[str]:
    """Palauta moduulitilan migraation eheysvirheet."""
    errors = []
    registry = _read(REGISTRY_PATH)
    registry_entries = {item["module_id"]: item for item in registry["modules"]}
    legacy = _read(ROOT / "data/seurantatila.json")
    source_log = _read(ROOT / "data/lahdetarkistukset.json")
    screening_history = _read(ROOT / "data/naytosten-muutoshistoria.json")
    expected_ids = set(MODULES)
    state_dir = ROOT / "data/module-state"
    state_files = {path.stem: path for path in state_dir.glob("*.json")}
    if set(state_files) != expected_ids:
        errors.append(
            f"Moduulitilan tiedostot eivät vastaa moduulijoukkoa: "
            f"puuttuvat={sorted(expected_ids - set(state_files))}, "
            f"ylimääräiset={sorted(set(state_files) - expected_ids)}."
        )

    source_runs = {}
    for module_id, metadata in MODULES.items():
        task_id = metadata["task"]
        source_runs[module_id] = [
            item["run_id"] for item in source_log["runs"] if item["task_id"] == task_id
        ]

    for module_id, metadata in MODULES.items():
        path = state_files.get(module_id)
        entry = registry_entries.get(module_id)
        if path is None or entry is None:
            errors.append(f"{module_id}: moduulitilan tiedosto tai rekisterimerkintä puuttuu.")
            continue
        try:
            state = _read(path)
            definition_path = ROOT / entry["path"]
            definition = _read(definition_path)
            validate_module_state(state, definition)
        except (OSError, ValueError, KeyError) as exc:
            errors.append(f"{module_id}: tilan tai määrityksen validointi epäonnistui: {exc}")
            continue

        if state["module_id"] != module_id:
            errors.append(f"{module_id}: moduulitilan tunniste on virheellinen.")
        if state["module_definition_version"] != entry["definition_version"]:
            errors.append(f"{module_id}: moduulitilan määritysversio ei vastaa rekisteriä.")
        if state["references"]["source_registry_ref"] != f"data/sources/{metadata['task']}.json":
            errors.append(f"{module_id}: lähderekisteriviite ei vastaa tehtävää.")
        if state["publication"]["feed_path"] != metadata["feed"]:
            errors.append(f"{module_id}: RSS-syötteen viite ei vastaa moduulia.")
        if state["references"]["legacy_state_pointer"] != f"data/seurantatila.json#/{metadata['pointer']}":
            errors.append(f"{module_id}: vanhan seurantatilan osoitin on virheellinen.")
        if state["migration"]["source_task_id"] != metadata["task"]:
            errors.append(f"{module_id}: lähdetehtävän tunniste on virheellinen.")

        if metadata.get("screening"):
            old_task = legacy["separate_screening_watch"]
        else:
            old_task = legacy["rotation"]["tasks"][metadata["task"]]
        checkpoint = state["checkpoint"]["last_successful_run"]
        old_period = {"start": old_task.get("last_period_start"), "end": old_task.get("last_period_end")}
        legacy_checked_at = old_task.get("last_successful_check")
        checkpoint_checked_at = checkpoint["checked_at"]

        # Näytösvahti käyttää edelleen vanhaa automaatiotilaa, vaikka sen
        # moduulikohtainen tila on vasta migraation rinnakkaiskuva. Siksi vanha
        # automaatio saa edetä checkpointin ohi vain täydellisen, lähdelokiin ja
        # hyväksyttyyn julkaisuraporttiin sidotun onnistuneen ajon perusteella.
        legacy_advanced = False
        if metadata.get("screening") and legacy_checked_at != checkpoint_checked_at:
            try:
                legacy_advanced = (
                    legacy_checked_at is not None
                    and checkpoint_checked_at is not None
                    and _parse_datetime(legacy_checked_at) > _parse_datetime(checkpoint_checked_at)
                )
            except (TypeError, ValueError):
                legacy_advanced = False

            latest_run = next(
                (item for item in reversed(source_log["runs"]) if item["task_id"] == task_id),
                None,
            )
            report = None
            if latest_run is not None:
                report_path = ROOT / "reports/julkaisuportit" / f"{latest_run['run_id']}.json"
                if report_path.is_file():
                    report = _read(report_path)
            expected_period_note = (
                f"Seurantajakso Suomen ajassa: {old_period['start']}–{old_period['end']}."
            )
            valid_legacy_advance = (
                legacy_advanced
                and latest_run is not None
                and latest_run["status"] == "complete"
                and latest_run["ended_at"] == legacy_checked_at
                and source_log["latest_by_task"].get(task_id) == legacy_checked_at
                and len(latest_run["checked_source_ids"]) == old_task.get("sources_checked")
                and expected_period_note in latest_run["coverage_notes"]
                and old_task.get("last_result") == "success"
                and old_task.get("errors", []) == []
                and report is not None
                and report.get("decision") == "approved"
                and report.get("feed_path") == metadata["feed"]
                and report.get("checked_at") == legacy_checked_at
            )
            if not valid_legacy_advance:
                errors.append(
                    f"{module_id}: uudempi vanhan automaation seurantatila ei vastaa "
                    "täydellistä lähdetarkistusajoa ja hyväksyttyä julkaisuraporttia."
                )
        else:
            if checkpoint_checked_at != legacy_checked_at:
                errors.append(f"{module_id}: viimeisin tarkistusaika ei vastaa vanhaa seurantatilaa.")
            if checkpoint["period"] != old_period:
                errors.append(f"{module_id}: seurantajakso ei vastaa vanhaa seurantatilaa.")
            if checkpoint["result"] != (old_task.get("last_result") or "not_recorded"):
                errors.append(f"{module_id}: viimeisin tulos ei vastaa vanhaa seurantatilaa.")
            if checkpoint["published_items"] != old_task.get("published_items"):
                errors.append(f"{module_id}: julkaistujen itemien määrä ei vastaa vanhaa seurantatilaa.")
            if checkpoint["sources_checked"] != old_task.get("sources_checked"):
                errors.append(f"{module_id}: tarkistettujen lähteiden määrä ei vastaa vanhaa seurantatilaa.")
            if checkpoint["errors"] != old_task.get("errors", []):
                errors.append(f"{module_id}: virhelista ei vastaa vanhaa seurantatilaa.")

        expected_run = RUN_HISTORY.get(module_id, {})
        if checkpoint["run_id"] != expected_run.get("run_id"):
            errors.append(f"{module_id}: ajotunniste ei vastaa eksplisiittistä ajohistoriatietoa.")
        if checkpoint["run_history_ref"] != expected_run.get("ref"):
            errors.append(f"{module_id}: ajohistoriaviite ei vastaa eksplisiittistä ajohistoriatietoa.")
        if checkpoint["definition_version"] is not None:
            errors.append(f"{module_id}: historialliselle ajolle on asetettu jälkikäteen moduuliversio.")

        expected_source_runs = source_runs[module_id]
        if state["history"]["source_check_run_refs"] != expected_source_runs:
            errors.append(f"{module_id}: lähdetarkistusajojen viitteet eivät vastaa lähdelokia.")
        if len(state["checkpoint_history"]) != (1 if checkpoint["checked_at"] else 0):
            errors.append(f"{module_id}: migroidun checkpoint-historian määrä on virheellinen.")
        if state["checkpoint_history"]:
            migrated = state["checkpoint_history"][0]
            if migrated["source"] != "legacy_migration" or migrated["definition_version"] is not None:
                errors.append(f"{module_id}: vanha checkpoint on luokiteltu virheellisesti.")
            # Migraatiotapahtuma säilyttää vain lähdeajot, jotka olivat olemassa
            # checkpointin syntyhetkellä. Nykyinen history.source_check_run_refs
            # sisältää edelleen kaikki myöhemmätkin lähdetarkistusajot.
            if metadata.get("screening") and migrated["checked_at"] is not None:
                cutoff = _parse_datetime(migrated["checked_at"])
                migration_source_runs = [
                    item["run_id"] for item in source_log["runs"]
                    if item["task_id"] == task_id
                    and _parse_datetime(item["ended_at"]) <= cutoff
                ]
            else:
                migration_source_runs = expected_source_runs
            if migrated["source_check_run_refs"] != migration_source_runs:
                errors.append(f"{module_id}: checkpointin migraatiohetken lähdetarkistusviitteet eivät täsmää.")

        expected_guids = _feed_guids(ROOT / metadata["feed"])
        if state["publication"]["guid_refs"] != expected_guids:
            errors.append(f"{module_id}: RSS-GUID-viitteet eivät vastaa julkaistua syötettä.")

        expected_documents = [{"path": path, "heading": heading} for path, heading in metadata["docs"]]
        if state["history"]["document_refs"] != expected_documents:
            errors.append(f"{module_id}: dokumenttihistoriaviitteet eivät vastaa dokumentaatiota.")
        for document in metadata["docs"]:
            doc_path, heading = document
            if not (ROOT / doc_path).is_file():
                errors.append(f"{module_id}: historiadokumenttia ei löydy ({doc_path}).")
            elif heading is not None and heading not in (ROOT / doc_path).read_text(encoding="utf-8"):
                errors.append(f"{module_id}: historiadokumentin otsikkoa ei löydy ({heading}).")

        if metadata.get("screening"):
            expected_events = [
                {"store_path":"data/naytosten-muutoshistoria.json","record_id":item["event_id"]}
                for item in screening_history["events"]
            ]
            expected_current = [
                {"store_path":"data/naytosten-muutoshistoria.json","record_id":item["screening_id"]}
                for item in screening_history["screenings"]
            ]
        else:
            expected_events, expected_current = [], []
        if state["history"]["event_refs"] != expected_events:
            errors.append(f"{module_id}: tapahtumahistoriaviitteet eivät vastaa kanonista historiaa.")
        if state["history"]["current_record_refs"] != expected_current:
            errors.append(f"{module_id}: nykytilan tietueviitteet eivät vastaa kanonista historiaa.")

    return errors


def main() -> None:
    """Tulosta tarkistuksen tulos ja pysäytä CI virheisiin."""
    errors = validate_state_migration()
    if errors:
        for error in errors:
            print(f"VIRHE: {error}")
        raise SystemExit(f"Moduulitilan migraatiossa havaittiin {len(errors)} virhettä.")
    print("OK: kymmenen moduulitilaa vastaa nykyisiä moduulimäärittelyjä ja vanhaa seurantatilaa.")
    print("OK: tarkistusajat, seurantajaksot ja ajotunnisteet säilyvät vain, kun ne on lähteissä kirjattu.")
    print("OK: lähdetarkistusajot, RSS-GUIDit ja näytöshistorian tunnisteet on säilytetty.")
    print("OK: vanhoja seurantatiloja, julkaisuja tai historioita ei muuteta.")


if __name__ == "__main__":
    main()
