"""Taylor Swift -moduulin erillisen varjoharjoituksen turvalliset portit.

Tämä moduulikohtainen työkalu valmistelee harjoituksen ja tallentaa vain
varjoartefakteja. Se ei käynnistä tutkimusta, julkaise RSS:ää eikä päivitä
tuotannon checkpointia, moduulitilaa, julkaisupäiväkirjaa tai tehtäväjonoa.
"""
from __future__ import annotations

from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
from typing import Any

from scripts.module_input_bundle import build_module_input_bundle, bundle_to_json

ROOT = Path(__file__).resolve().parents[1]
MODULE_ID = "taylor-swift"
TASK_ID = "taylor_swift"
RUN_ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]{7,127}$")
DATE_IN_GUID = re.compile(r":(20\d{2}-\d{2}-\d{2}):")


class TaylorSwiftShadowError(ValueError):
    """Varjoharjoituksen valmistelu- tai validointivirhe."""


def _read_json(root: Path, relative: str) -> tuple[dict[str, Any], str]:
    """Lue JSON-tiedosto ja palauta myös alkuperäisen sisällön SHA-256."""
    root = Path(root).resolve()
    path = (root / relative).resolve()
    if not path.is_relative_to(root) or not path.is_file():
        raise TaylorSwiftShadowError(f"Tiedostoviite poistuu repositoriosta tai puuttuu: {relative}")
    try:
        raw = path.read_bytes()
        value = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise TaylorSwiftShadowError(f"Vaadittua JSON-tiedostoa ei voi lukea: {relative}") from exc
    if not isinstance(value, dict):
        raise TaylorSwiftShadowError(f"JSON-tiedoston juuren pitää olla olio: {relative}")
    return value, hashlib.sha256(raw).hexdigest()


def _timestamp(value: str, field: str) -> datetime:
    """Vaadi aikavyöhykkeellinen ISO 8601 -aikaleima."""
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, TypeError, ValueError) as exc:
        raise TaylorSwiftShadowError(f"{field} ei ole kelvollinen ISO 8601 -aikaleima.") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise TaylorSwiftShadowError(f"{field} tarvitsee aikavyöhykkeen.")
    return parsed


def _feed_has_possible_period_duplicate(feed_path: Path, start: datetime, end: datetime) -> bool:
    """Estä ajo varovaisesti, jos tuotantosyötteessä on jaksoon osuva item.

    RSS-itemin julkaisupäivä tai GUID-päivä ei yksin todista raportin kattamaa
    seurantajaksoa. Siksi osuma tulkitaan mahdolliseksi kaksoistulokseksi ja
    valmistelu pysäytetään manuaaliseen tarkistukseen.
    """
    try:
        root = ET.parse(feed_path).getroot()
    except (OSError, ET.ParseError) as exc:
        raise TaylorSwiftShadowError("Taylor Swiftin tuotanto-RSS:ää ei voi tarkistaa.") from exc
    for item in root.findall("./channel/item"):
        dates: list[datetime] = []
        guid = item.findtext("guid") or ""
        match = DATE_IN_GUID.search(guid)
        if match:
            dates.append(datetime.fromisoformat(match.group(1)).replace(tzinfo=start.tzinfo))
        pub_date = item.findtext("pubDate")
        if pub_date:
            try:
                parsed = parsedate_to_datetime(pub_date)
                if parsed.tzinfo is None:
                    parsed = parsed.replace(tzinfo=timezone.utc)
                dates.append(parsed)
            except (TypeError, ValueError, OverflowError):
                # Virheellinen päiväys ei todista julkaisun puuttumista.
                raise TaylorSwiftShadowError("Tuotanto-RSS:n itemissä on virheellinen pubDate.")
        if any(start.date() <= value.astimezone(start.tzinfo).date() <= end.date()
               for value in dates):
            return True
    return False


def prepare_taylor_swift_shadow(
    *, run_id: str, period_start: str, period_end: str, requested_at: str,
    root: Path = ROOT,
) -> dict[str, Any]:
    """Muodosta harjoituskohtainen lähtötilakuva ilman tuotantokirjoituksia.

    Historiallista moduulicheckpointia ei validoida, korjata eikä käytetä
    harjoituksen jatkuvuustilana. Siitä säilytetään vain tiedoston tiiviste
    ja viite, jotta alkuperäinen migraatiosnapshot on tunnistettavissa.
    """
    if not isinstance(run_id, str) or not RUN_ID_PATTERN.fullmatch(run_id):
        raise TaylorSwiftShadowError("run_id ei vastaa turvallista tunnistemallia.")
    start, end = _timestamp(period_start, "period_start"), _timestamp(period_end, "period_end")
    requested = _timestamp(requested_at, "requested_at")
    if start > end:
        raise TaylorSwiftShadowError("Seurantajakson alku on loppua myöhempi.")
    root = Path(root).resolve()

    # Lue vain Taylor Swift -moduulin tarvitsemat rekisterit ja varmista omistajuus.
    registry, registry_sha = _read_json(root, "data/module-registry.json")
    matches = [item for item in registry.get("modules", []) if item.get("module_id") == MODULE_ID]
    if len(matches) != 1:
        raise TaylorSwiftShadowError("Taylor Swift -moduulia ei löydy rekisteristä yksikäsitteisesti.")
    entry = matches[0]
    if entry.get("module_type") != "topic" or entry.get("status") != "inactive":
        raise TaylorSwiftShadowError("Moduulin pitää olla inactive-tilassa oleva topic-moduuli.")
    module, module_sha = _read_json(root, entry["path"])
    if (any(module.get(key) != entry.get(key)
            for key in ("module_id", "module_type", "definition_version"))
            or module.get("contract_version") != registry.get("contract_version")):
        raise TaylorSwiftShadowError("Moduulimäärittelyn omistajuus tai versio ei täsmää.")

    targets, target_registry_sha = _read_json(root, "data/target-registry.json")
    target_refs = module.get("target_refs", [])
    if not isinstance(target_refs, list) or len(target_refs) != 1:
        raise TaylorSwiftShadowError("Taylor Swift -moduulilla pitää olla täsmälleen yksi hyväksytty kohde.")
    target_entries = [item for item in targets.get("targets", [])
                      if item.get("target_id") == target_refs[0]]
    if len(target_entries) != 1:
        raise TaylorSwiftShadowError("Taylor Swift -kohde puuttuu tai on rekisterissä kahteen kertaan.")
    if target_entries[0].get("status") != "inactive":
        raise TaylorSwiftShadowError("Taylor Swift -kohteen pitää olla inactive-tilassa.")
    target, target_sha = _read_json(root, target_entries[0]["path"])
    owner = target.get("module_ref", {})
    if (target.get("target_id") != target_refs[0] or owner.get("module_id") != MODULE_ID
            or owner.get("definition_version") != module.get("definition_version")):
        raise TaylorSwiftShadowError("Seurantakohteen omistajuus ei täsmää.")

    sources, sources_sha = _read_json(root, "data/sources/taylor_swift.json")
    if sources.get("task_id") != TASK_ID:
        raise TaylorSwiftShadowError("Taylor Swiftin lähderekisterin task_id ei täsmää.")
    source_catalog, catalog_sha = _read_json(root, "data/source-catalog.json")
    catalog_list = [item.get("id") for item in source_catalog.get("sources", [])]
    catalog_ids = set(catalog_list)
    if len(catalog_ids) != len(catalog_list):
        raise TaylorSwiftShadowError("Yhteisessä lähdekatalogissa on duplikaattitunnisteita.")
    source_refs = [item.get("source_id") for item in module.get("source_refs", [])]
    usage_ids = [item.get("source_id") for item in sources.get("sources", [])]
    if (not source_refs or len(source_refs) != len(set(source_refs))
            or len(usage_ids) != len(set(usage_ids))
            or set(source_refs) != set(usage_ids) or not set(source_refs).issubset(catalog_ids)):
        raise TaylorSwiftShadowError("Moduulin lähdeviitteet eivät vastaa lähderekisteriä ja katalogia.")

    feeds, feed_catalog_sha = _read_json(root, "data/feed-catalog.json")
    feed_matches = [item for item in feeds.get("feeds", [])
                    if item.get("id") == MODULE_ID and item.get("type") == "topic"]
    if len(feed_matches) != 1 or feed_matches[0].get("path") != "feeds/taylor-swift.xml":
        raise TaylorSwiftShadowError("Taylor Swiftin oma RSS-syöte puuttuu tai on ristiriitainen.")

    activation, activation_sha = _read_json(root, "data/module-production-activation.json")
    if activation.get("modules", {}).get(MODULE_ID) is not False:
        raise TaylorSwiftShadowError("Taylor Swift -moduulin tuotantoaktivointi ei ole varmasti pois päältä.")

    publication_registry, publication_registry_sha = _read_json(root, "data/publication-registry.json")
    publication_routing, publication_routing_sha = _read_json(root, "data/publication-routing.json")
    if publication_registry.get("publications") or publication_routing.get("routes"):
        raise TaylorSwiftShadowError("Julkaisurekisteri tai -reititys ei ole tyhjä; vaaditaan manuaalinen tarkistus.")

    feed_path = root / "feeds/taylor-swift.xml"
    if _feed_has_possible_period_duplicate(feed_path, start, end):
        raise TaylorSwiftShadowError(
            "Tuotanto-RSS:ssä on samaan päiväväliin osuva mahdollinen julkaisu; kaksoistuloksen riski on selvitettävä."
        )

    # Historiallista checkpointia ei tulkita lähtötilaksi; vain alkuperäinen tiedosto tiivistetään.
    _, historical_state_sha = _read_json(root, "data/module-state/taylor-swift.json")
    feed_bytes = feed_path.read_bytes()
    feed_sha = hashlib.sha256(feed_bytes).hexdigest()
    input_shas = {
        "data/module-registry.json": registry_sha,
        entry["path"]: module_sha,
        "data/target-registry.json": target_registry_sha,
        target_entries[0]["path"]: target_sha,
        "data/sources/taylor_swift.json": sources_sha,
        "data/source-catalog.json": catalog_sha,
        "data/feed-catalog.json": feed_catalog_sha,
        "data/module-production-activation.json": activation_sha,
        "data/publication-registry.json": publication_registry_sha,
        "data/publication-routing.json": publication_routing_sha,
        "data/module-state/taylor-swift.json": historical_state_sha,
        "feeds/taylor-swift.xml": feed_sha,
    }
    # Rakenna varsinainen ChatGPT:lle luovutettava paketti synteettisellä,
    # tyhjällä moduulitilalla. Tuotannon checkpointia tai GUID-historiaa ei kopioida.
    empty_shadow_state = {
        "schema_version": 1,
        "module_id": MODULE_ID,
        "module_definition_version": module["definition_version"],
        "checkpoint": {"last_successful_run": {
            "run_id": None, "run_history_ref": None, "definition_version": None,
            "checked_at": None, "period": {"start": None, "end": None},
            "result": "not_recorded", "published_items": None,
            "sources_checked": None, "errors": [],
        }},
        "checkpoint_history": [],
        "history": {
            "document_refs": [], "event_refs": [], "current_record_refs": [],
            "source_check_run_refs": [],
        },
        "publication": {"feed_path": "feeds/taylor-swift.xml", "guid_refs": []},
        "references": {
            "source_registry_ref": "data/sources/taylor_swift.json",
            "source_catalog_ref": "data/source-catalog.json",
            "feed_catalog_ref": "data/feed-catalog.json",
            "source_check_log_ref": "data/lahdetarkistukset.json",
            "legacy_state_pointer": "data/seurantatila.json#/rotation.tasks.taylor_swift",
        },
        "migration": {
            "source_task_id": TASK_ID,
            "source_state_ref": "data/module-state/taylor-swift.json",
            "migrated_on": "2026-11-18",
            "notes": "Harjoituskohtainen synteettinen tyhjä lähtötila; ei tuotannon checkpoint.",
        },
    }
    bundle = build_module_input_bundle(
        MODULE_ID, task_id=TASK_ID, run_id=run_id,
        period_start=period_start, period_end=period_end,
        module_state_override=empty_shadow_state, root=root,
    )
    bundle_json = bundle_to_json(bundle)
    handoff_input_sha256 = hashlib.sha256(bundle_json.encode("utf-8")).hexdigest()
    return {
        "schema_version": 1,
        "artifact_type": "taylor_swift_shadow_preparation",
        "status": "prepared",
        "module_id": MODULE_ID,
        "module_definition_version": module["definition_version"],
        "contract_version": registry["contract_version"],
        "run_id": run_id,
        "period": {"start": period_start, "end": period_end},
        "requested_at": requested.isoformat(),
        "execution_authorized": False,
        "research_performed": False,
        "publication_performed": False,
        "production_state_written": False,
        "baseline": {
            "kind": "isolated_empty_shadow_baseline",
            "checkpoint": {
                "run_id": None, "period": {"start": None, "end": None},
                "result": "not_recorded",
            },
            "historical_checkpoint_reference": {
                "path": "data/module-state/taylor-swift.json",
                "sha256": historical_state_sha,
                "used_as_baseline": False,
            },
        },
        "target_id": target["target_id"],
        "source_ids": source_refs,
        "input_bundle": json.loads(bundle_json),
        "source_registry_updated_at": sources.get("updated_at"),
        "source_freshness_rechecked": False,
        "input_sha256": input_shas,
        "handoff_input_sha256": handoff_input_sha256,
        "limitations": [
            "Tämä on tekninen valmistelu, ei live-tutkimus eikä harjoitusajo.",
            "Lähteiden ajantasaisuus tarkistetaan vasta erikseen hyväksytyssä harjoituksessa.",
            "Tuotanto-RSS:n päivämääräosuma tarkistetaan varovaisena kaksoistuloksen estona; se ei todista raporttijakson kattavuutta.",
            "Runtime-haaraa tai tuotannon julkaisupäiväkirjaa ei ole luettu eikä luotu.",
        ],
    }


def write_shadow_artifact(
    root: Path, artifact: dict[str, Any], *, kind: str,
    create_run_directory: bool = False,
) -> Path:
    """Tallenna JSON vain Taylor Swiftin omaan varjohakemistoon.

    Oletustapa sallii saman ajohakemiston eri artefaktit mutta ei koskaan
    ylikirjoita tiedostoa. Uuden testikierroksen alustus voi pyytää
    create_run_directory=True, jolloin myös run_id-hakemiston on oltava uusi.
    """
    if kind not in {"prepared", "result"}:
        raise TaylorSwiftShadowError("Varjoartefaktin tyyppi ei ole sallittu.")
    if artifact.get("module_id") != MODULE_ID:
        raise TaylorSwiftShadowError("Varjoartefaktin moduuliomistajuus ei täsmää.")
    run_id = artifact.get("run_id")
    if not isinstance(run_id, str) or not RUN_ID_PATTERN.fullmatch(run_id):
        raise TaylorSwiftShadowError("Varjoartefaktin run_id ei ole kelvollinen.")
    if kind == "prepared" and artifact.get("artifact_type") != "taylor_swift_shadow_preparation":
        raise TaylorSwiftShadowError("Valmisteluvarjoartefaktin tyyppi ei täsmää.")
    if kind == "result" and artifact.get("artifact_type") != "taylor_swift_shadow_result":
        raise TaylorSwiftShadowError("Tuloksen varjoartefaktin tyyppi ei täsmää.")
    root = Path(root).resolve()
    directory = root / "data/shadow-exercises" / MODULE_ID / run_id
    if not directory.resolve().is_relative_to(root):
        raise TaylorSwiftShadowError("Varjoartefaktin polku poistuu repositoriosta.")
    # Estä myös ylempien hakemistojen symboliset linkit, ei vain lopullista kansiota.
    for component in (
        root / "data", root / "data/shadow-exercises",
        root / "data/shadow-exercises" / MODULE_ID, directory,
    ):
        if component.is_symlink():
            raise TaylorSwiftShadowError("Varjoartefaktin polun osat eivät saa olla symbolisia linkkejä.")
    try:
        # Uusi testiajo saa oman uuden hakemiston; vanhaa ajohakemistoa ei tyhjennetä.
        directory.mkdir(parents=True, exist_ok=not create_run_directory)
    except FileExistsError as exc:
        raise TaylorSwiftShadowError(
            "run_id on jo käytössä; olemassa olevaa testiajoa ei nollata eikä ylikirjoiteta."
        ) from exc
    destination = directory / f"{kind}.json"
    payload = json.dumps(artifact, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    try:
        with destination.open("x", encoding="utf-8") as stream:
            stream.write(payload)
    except FileExistsError as exc:
        raise TaylorSwiftShadowError("Varjoartefakti on jo olemassa; sitä ei ylikirjoiteta.") from exc
    return destination


def start_fresh_taylor_swift_shadow_run(
    *, run_id: str, period_start: str, period_end: str, requested_at: str,
    root: Path = ROOT,
) -> tuple[dict[str, Any], Path]:
    """Alusta uusi, tyhjä Taylor Swift -varjoajo poistamatta aiempaa testidataa.

    Ensin kaikki tavalliset valmisteluportit tarkistetaan ilman kirjoituksia.
    Vasta niiden läpäisyn jälkeen luodaan uusi run_id-hakemisto ja tallennetaan
    valmisteluasiakirja. Olemassa olevaa hakemistoa ei koskaan tyhjennetä.
    """
    preparation = prepare_taylor_swift_shadow(
        run_id=run_id, period_start=period_start, period_end=period_end,
        requested_at=requested_at, root=root,
    )
    artifact_path = write_shadow_artifact(
        root, preparation, kind="prepared", create_run_directory=True,
    )
    return preparation, artifact_path
