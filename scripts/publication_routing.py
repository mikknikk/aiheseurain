"""Julkaisukohteiden reitityksen ratkaisu ja paikallinen RSS-julkaisusovitin.

Reititin lukee moduuli-, kohde-, julkaisu- ja reititysrekisterit erillisinä.
Kuivaharjoittelu ei kirjoita tiedostoja. RSS-sovitin kirjoittaa vain sille
erikseen annettuun juureen; tuotantorekistereitä ei aktivoida automaattisesti.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
import tempfile
import os
import fcntl
import xml.etree.ElementTree as ET
from typing import Any

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
PUBLICATION_ID = re.compile(r"^[a-z][a-z0-9]*(?:[.-][a-z0-9]+)*$")
TARGET_ID = re.compile(r"^[a-z][a-z0-9]*(?:[.-][a-z0-9]+)*$")


class PublicationRoutingError(ValueError):
    """Julkaisurekisterin, reitin tai julkaisun sopimusvirhe."""


@dataclass(frozen=True)
class PublicationPlan:
    """Yhden kohdekohtaisen raportin ratkaistut julkaisukohteet."""
    module_id: str
    target_id: str
    run_id: str
    publication_ids: tuple[str, ...]
    inactive_publication_ids: tuple[str, ...]
    inactive_refs: tuple[str, ...]
    observation_types: tuple[str, ...]


def _read_json(path: Path) -> dict[str, Any]:
    """Lue JSON-olio ja muunna lukuvirheet ymmärrettäviksi reititysvirheiksi."""
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PublicationRoutingError(f"JSON-tiedoston lukeminen epäonnistui: {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise PublicationRoutingError(f"JSON-tiedoston ylimmän tason arvon pitää olla olio: {path}")
    return value


def _validate(value: dict[str, Any], schema_path: Path, label: str) -> None:
    """Tarkista rekisterin tai määrityksen rakenne virallista skeemaa vasten."""
    schema = _read_json(schema_path)
    jsonschema.Draft202012Validator.check_schema(schema)
    errors = sorted(
        jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker()).iter_errors(value),
        key=lambda error: list(error.path),
    )
    if errors:
        first = errors[0]
        raise PublicationRoutingError(
            f"{label} ei vastaa skeemaa kohdassa {list(first.path)}: {first.message}"
        )


def load_publication_context(root: Path = ROOT) -> dict[str, Any]:
    """Lataa ja validoi julkaisuun liittyvät rekisterit muuttamatta niitä."""
    root = Path(root)
    module_registry = _read_json(root / "data/module-registry.json")
    target_registry = _read_json(root / "data/target-registry.json")
    publication_registry = _read_json(root / "data/publication-registry.json")
    routing = _read_json(root / "data/publication-routing.json")
    _validate(target_registry, root / "schemas/seurantakohderekisteri.schema.json", "Seurantakohderekisteri")
    _validate(publication_registry, root / "schemas/julkaisukohderekisteri.schema.json", "Julkaisukohderekisteri")
    _validate(routing, root / "schemas/julkaisureititys.schema.json", "Julkaisureititys")
    modules = {item["module_id"]: item for item in module_registry.get("modules", [])}
    targets = {}
    for entry in target_registry["targets"]:
        if entry["target_id"] in targets:
            raise PublicationRoutingError(f"Duplikaatti seurantakohde: {entry['target_id']}")
        target = _read_json(root / entry["path"])
        _validate(target, root / "schemas/seurantakohde.schema.json", f"Seurantakohde {entry['target_id']}")
        if target["target_id"] != entry["target_id"]:
            raise PublicationRoutingError(f"Seurantakohteen tunniste ei vastaa rekisteriä: {entry['target_id']}")
        if target["module_ref"]["module_id"] not in modules:
            raise PublicationRoutingError(f"Seurantakohteen moduulia ei tunneta: {entry['target_id']}")
        targets[entry["target_id"]] = (entry, target)
    publications = {}
    for entry in publication_registry["publications"]:
        if entry["publication_id"] in publications:
            raise PublicationRoutingError(f"Duplikaatti julkaisukohde: {entry['publication_id']}")
        publication = _read_json(root / entry["path"])
        _validate(publication, root / "schemas/julkaisukohde.schema.json", f"Julkaisukohde {entry['publication_id']}")
        if publication["publication_id"] != entry["publication_id"]:
            raise PublicationRoutingError(f"Julkaisukohteen tunniste ei vastaa rekisteriä: {entry['publication_id']}")
        publications[entry["publication_id"]] = (entry, publication)
    route_ids = set()
    for route in routing["routes"]:
        if route["route_id"] in route_ids:
            raise PublicationRoutingError(f"Duplikaatti reittitunniste: {route['route_id']}")
        route_ids.add(route["route_id"])
        if route["module_ref"] not in modules:
            raise PublicationRoutingError(f"Reitin moduulia ei tunneta: {route['module_ref']}")
        if route["target_ref"] not in targets:
            raise PublicationRoutingError(f"Reitin seurantakohdetta ei tunneta: {route['target_ref']}")
        target_module = targets[route["target_ref"]][1]["module_ref"]["module_id"]
        if target_module != route["module_ref"]:
            raise PublicationRoutingError(f"Reitin moduuli ei omista seurantakohdetta: {route['route_id']}")
        for publication_id in route["publication_refs"]:
            if publication_id not in publications:
                raise PublicationRoutingError(f"Reitin julkaisukohdetta ei tunneta: {publication_id}")
    return {"modules": modules, "targets": targets, "publications": publications, "routing": routing}


def resolve_publication_plan(
    context: dict[str, Any], *, module_id: str, target_id: str, run_id: str,
    observation_types: list[str] | tuple[str, ...], include_inactive: bool = False,
) -> PublicationPlan:
    """Ratkaise kohdekohtaisen raportin julkaisukanavat ilman kirjoituksia."""
    if module_id not in context["modules"]:
        raise PublicationRoutingError(f"Tuntematon moduuli: {module_id}")
    if target_id not in context["targets"]:
        raise PublicationRoutingError(f"Tuntematon seurantakohde: {target_id}")
    if context["targets"][target_id][1]["module_ref"]["module_id"] != module_id:
        raise PublicationRoutingError(f"Moduuli {module_id} ei omista kohdetta {target_id}.")
    if not isinstance(run_id, str) or not run_id.strip():
        raise PublicationRoutingError("Ajon tunniste puuttuu.")
    if not isinstance(observation_types, (list, tuple)) or not observation_types:
        raise PublicationRoutingError("Raportilla pitää olla vähintään yksi havaintotyyppi.")
    if any(not isinstance(item, str) or not item.strip() for item in observation_types):
        raise PublicationRoutingError("Havaintotyyppien pitää olla ei-tyhjiä merkkijonoja.")
    types = tuple(sorted(set(observation_types)))
    routes = [
        route for route in context["routing"]["routes"]
        if route["module_ref"] == module_id and route["target_ref"] == target_id
        and set(route["observation_types"]).intersection(types)
    ]
    if not routes:
        raise PublicationRoutingError(
            f"Julkaisureittiä ei löydy moduulille {module_id}, kohteelle {target_id} "
            f"ja havaintotyypeille {', '.join(types)}."
        )
    inactive_refs = []
    if context["modules"][module_id].get("status") != "active":
        inactive_refs.append(f"module:{module_id}")
    target_entry = context["targets"][target_id][0]
    if target_entry.get("status") != "active":
        inactive_refs.append(f"target:{target_id}")
    active_routes = []
    for route in routes:
        if route["status"] == "active":
            active_routes.append(route)
        else:
            inactive_refs.append(f"route:{route['route_id']}")
    publication_ids = sorted({pid for route in active_routes for pid in route["publication_refs"]})
    if not publication_ids and include_inactive:
        publication_ids = sorted({pid for route in routes for pid in route["publication_refs"]})
    if not publication_ids:
        raise PublicationRoutingError("Sopivaa aktiivista julkaisureittiä ei löytynyt.")
    inactive_publications = []
    for publication_id in publication_ids:
        entry, publication = context["publications"][publication_id]
        if entry["status"] != "active" or publication["status"] != "active":
            inactive_publications.append(publication_id)
            inactive_refs.append(f"publication:{publication_id}")
    if inactive_refs and not include_inactive:
        raise PublicationRoutingError(
            "Reititys sisältää passiivisia osia: " + ", ".join(sorted(set(inactive_refs)))
        )
    return PublicationPlan(
        module_id=module_id, target_id=target_id, run_id=run_id,
        publication_ids=tuple(publication_ids),
        inactive_publication_ids=tuple(sorted(set(inactive_publications))),
        inactive_refs=tuple(sorted(set(inactive_refs))),
        observation_types=types,
    )


def preview_publication_plan(plan: PublicationPlan) -> dict[str, Any]:
    """Palauta ihmiselle luettava kuivaharjoittelutulos; ei kirjoita tiedostoja."""
    return {
        "module_id": plan.module_id, "target_id": plan.target_id, "run_id": plan.run_id,
        "observation_types": list(plan.observation_types),
        "publication_ids": list(plan.publication_ids),
        "inactive_publication_ids": list(plan.inactive_publication_ids),
        "would_publish": not bool(plan.inactive_refs),
        "inactive_refs": list(plan.inactive_refs),
    }


class LocalRoutedRssPublisher:
    """Kirjoita kohdekohtainen raportti useaan RSS-syötteeseen paikallisessa testijuurella."""

    def __init__(self, root: Path, context: dict[str, Any]):
        self.root = Path(root).resolve()
        self.context = context

    def _path(self, publication_id: str) -> Path:
        if publication_id not in self.context["publications"]:
            raise PublicationRoutingError(f"Tuntematon julkaisukohde: {publication_id}")
        relative = self.context["publications"][publication_id][1]["destination"]["path"]
        candidate = (self.root / relative).resolve()
        if not candidate.is_relative_to(self.root):
            raise PublicationRoutingError("RSS-polku poistuu julkaisusovittimen juuresta.")
        return candidate

    @staticmethod
    def _guid(plan: PublicationPlan, publication_id: str) -> str:
        """Sama raportti saa kohdekohtaisen GUIDin, joka on vakaa uusinta-ajoissa."""
        key = f"{plan.module_id}:{plan.target_id}:{plan.run_id}:{publication_id}"
        return "urn:aiheseurain:report:" + hashlib.sha256(key.encode("utf-8")).hexdigest()

    def publish_report(self, plan: PublicationPlan, report_content: str) -> dict[str, Any]:
        """Julkaise yksi kohderaportti suunnitelman kanaviin idempotentisti."""
        if plan.inactive_refs:
            raise PublicationRoutingError("Passiiviseen moduuliin, kohteeseen tai julkaisureittiin ei saa kirjoittaa.")
        if not isinstance(report_content, str) or not report_content.strip():
            raise PublicationRoutingError("Julkaistava kohderaportti on tyhjä.")
        report_hash = hashlib.sha256(report_content.encode("utf-8")).hexdigest()
        receipts = []
        # Reititys on jo ratkaistu; tässä käsitellään vain kanavakohtainen RSS-tallennus.
        for publication_id in plan.publication_ids:
            path = self._path(publication_id)
            path.parent.mkdir(parents=True, exist_ok=True)
            lock_path = path.with_name(path.name + ".lock")
            with lock_path.open("a+b") as lock:
                fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
                try:
                    if path.exists():
                        try:
                            tree = ET.fromstring(path.read_bytes())
                        except ET.ParseError as exc:
                            raise PublicationRoutingError(f"RSS-tiedoston XML on virheellinen: {path}") from exc
                    else:
                        publication = self.context["publications"][publication_id][1]
                        tree = ET.Element("rss", {"version": "2.0"})
                        channel = ET.SubElement(tree, "channel")
                        ET.SubElement(channel, "title").text = publication["name"]
                        ET.SubElement(channel, "link").text = publication["destination"]["url"]
                        ET.SubElement(channel, "description").text = publication["name"]
                    channel = tree.find("./channel")
                    if tree.tag != "rss" or channel is None:
                        raise PublicationRoutingError(f"RSS-rakenne on virheellinen: {path}")
                    guid = self._guid(plan, publication_id)
                    existing = [
                        item for item in channel.findall("./item")
                        if (item.findtext("guid") or "").strip() == guid
                    ]
                    if len(existing) > 1:
                        raise PublicationRoutingError(f"Syötteessä on saman raportin duplikaatti-GUID: {guid}")
                    if existing:
                        if existing[0].findtext("description") != report_content:
                            raise PublicationRoutingError("Sama raporttitunniste on jo julkaistu eri sisällöllä.")
                    else:
                        item = ET.SubElement(channel, "item")
                        ET.SubElement(item, "title").text = f"{plan.target_id}: {plan.run_id}"
                        ET.SubElement(item, "guid", {"isPermaLink": "false"}).text = guid
                        ET.SubElement(item, "description").text = report_content
                        xml = ET.tostring(tree, encoding="utf-8", xml_declaration=True)
                        with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False) as temp:
                            temp.write(xml)
                            temp.flush()
                            os.fsync(temp.fileno())
                            temporary = Path(temp.name)
                        try:
                            os.replace(temporary, path)
                        finally:
                            if temporary.exists():
                                temporary.unlink()
                    receipts.append({"publication_id": publication_id, "guid": guid, "content_sha256": report_hash})
                finally:
                    fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
        return {"verified": True, "published_items": len(receipts), "receipts": receipts}
