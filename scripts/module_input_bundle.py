"""Muodosta yhdelle moduulille rajattu ja vain luku -muotoinen syötepaketti.

Pakettirakentaja toimii luotetun koordinaattorin puolella. Runner saa vain oman
moduulinsa määrityksen, kohteet, lähteet, käyttöasetukset ja jatkuvuustilan.
Tämä on sovellusrajapinnan eristys, ei käyttöjärjestelmän prosessisandbox.
"""
from __future__ import annotations
import json
from pathlib import Path
import re
from types import MappingProxyType
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]


class ModuleInputBundleError(ValueError):
    """Syötepaketin kokoamisen tai omistajuuden tarkistuksen virhe."""


def _read(path: Path) -> dict[str, Any]:
    """Lue JSON-olio ja anna tiedostovirheestä rajattu sopimusvirhe."""
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ModuleInputBundleError(f"JSON-tiedostoa ei voi lukea: {path}") from exc
    if not isinstance(value, dict):
        raise ModuleInputBundleError(f"JSON-tiedoston pitää sisältää olio: {path}")
    return value


def _inside(root: Path, relative: str) -> Path:
    """Estä absoluuttiset ja repositorion ulkopuolelle johtavat polut."""
    candidate = Path(relative)
    resolved_root = root.resolve()
    resolved = (resolved_root / candidate).resolve()
    if candidate.is_absolute() or not resolved.is_relative_to(resolved_root) or not resolved.is_file():
        raise ModuleInputBundleError(f"Virheellinen tai puuttuva tiedostoviite: {relative}")
    return resolved


def _freeze(value: Any) -> Any:
    """Tee kaikki sisäkkäiset oliot ja listat vain luku -muotoisiksi."""
    if isinstance(value, dict):
        return MappingProxyType({key: _freeze(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    return value


def _thaw(value: Any) -> Any:
    """Muunna vain luku -rakenne JSON-serialisointia varten."""
    if isinstance(value, Mapping):
        return {key: _thaw(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_thaw(item) for item in value]
    return value


def build_module_input_bundle(
    module_id: str, *, task_id: str, run_id: str, period_start: str,
    period_end: str, source_registry_path: str | None = None, root: Path = ROOT,
) -> Mapping[str, Any]:
    """Kokoa vain yhden moduulin tiedot koordinaattorin luotetussa ympäristössä."""
    if not re.fullmatch(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*", module_id):
        raise ModuleInputBundleError("Virheellinen moduulitunniste.")
    if not all(isinstance(value, str) and value for value in (task_id, run_id, period_start, period_end)):
        raise ModuleInputBundleError("Tehtävätunniste, ajotunniste ja seurantajakso ovat pakollisia.")
    root = Path(root).resolve()

    # Rekisteriä käytetään vain yhden pyydetyn moduulin määrityksen ratkaisemiseen.
    registry = _read(root / "data/module-registry.json")
    matches = [item for item in registry.get("modules", []) if item.get("module_id") == module_id]
    if len(matches) != 1:
        raise ModuleInputBundleError("Moduulia ei löydy yksikäsitteisesti rekisteristä.")
    entry = matches[0]
    module = _read(_inside(root, entry["path"]))
    if any(module.get(key) != entry.get(key) for key in ("module_id", "module_type", "definition_version")):
        raise ModuleInputBundleError("Moduulimäärittely ei vastaa rekisterimerkintää.")

    # Kohderekisteristä luovutetaan vain moduulin omistamat kohteet.
    target_refs = module.get("target_refs", [])
    if not isinstance(target_refs, list) or not target_refs or len(target_refs) != len(set(target_refs)):
        raise ModuleInputBundleError("Moduulin kohdeviitteet puuttuvat tai ovat virheelliset.")
    target_registry = _read(root / "data/target-registry.json")
    target_entries = {item["target_id"]: item for item in target_registry.get("targets", [])
                      if item.get("target_id") in target_refs}
    if set(target_entries) != set(target_refs):
        raise ModuleInputBundleError("Kaikkia moduulin omia seurantakohteita ei löydy.")
    targets = []
    for target_id in target_refs:
        target = _read(_inside(root, target_entries[target_id]["path"]))
        owner = target.get("module_ref", {})
        if (target.get("target_id") != target_id or owner.get("module_id") != module_id
                or owner.get("definition_version") != module.get("definition_version")):
            raise ModuleInputBundleError(f"Seurantakohteen omistajuus ei täsmää: {target_id}")
        targets.append(target)

    # Yhteinen lähdekatalogi rajataan moduulin source_refs-listaan.
    refs = module.get("source_refs", [])
    source_ids = [item.get("source_id") for item in refs]
    if not source_ids or len(source_ids) != len(set(source_ids)):
        raise ModuleInputBundleError("Moduulin lähdeviitteet puuttuvat tai sisältävät duplikaatteja.")
    catalog = _read(root / "data/source-catalog.json")
    catalog_by_id = {item["id"]: item for item in catalog.get("sources", [])}
    if len(catalog_by_id) != len(catalog.get("sources", [])):
        raise ModuleInputBundleError("Lähdekatalogissa on duplikaattitunnisteita.")
    usage_path = source_registry_path or f"data/sources/{task_id}.json"
    if not re.fullmatch(r"data/sources/[a-z0-9_-]+\.json", usage_path):
        raise ModuleInputBundleError("Lähdekäyttörekisterin polku ei ole sallittu.")
    usage = _read(_inside(root, usage_path))
    if usage.get("task_id") != task_id:
        raise ModuleInputBundleError("Lähderekisterin task_id ei vastaa koordinaattorin arvoa.")
    usage_by_id = {item["source_id"]: item for item in usage.get("sources", [])}
    if len(usage_by_id) != len(usage.get("sources", [])) or set(usage_by_id) != set(source_ids):
        raise ModuleInputBundleError("Moduulin lähdeviitteet eivät vastaa sen käyttörekisteriä.")
    sources = []
    for reference in refs:
        source_id = reference["source_id"]
        if source_id not in catalog_by_id:
            raise ModuleInputBundleError(f"Lähde puuttuu yhteisestä katalogista: {source_id}")
        sources.append({"source": catalog_by_id[source_id],
                        "module_reference": reference, "usage": usage_by_id[source_id]})

    # Vain moduulin viimeisin checkpoint ja oman syötteen GUIDit välitetään eteenpäin.
    state_path = root / "data/module-state" / f"{module_id}.json"
    state = _read(state_path) if state_path.is_file() else {
        "schema_version": 1, "module_id": module_id, "checkpoint": {}, "publication": {}}
    if state.get("module_id") != module_id:
        raise ModuleInputBundleError("Moduulitilan omistajuus ei täsmää.")
    own_state = {
        "schema_version": state.get("schema_version", 1), "module_id": module_id,
        "module_definition_version": state.get("module_definition_version"),
        "checkpoint": {"last_successful_run": state.get("checkpoint", {}).get("last_successful_run", {})},
        "publication": state.get("publication", {}),
    }
    payload = {
        "bundle_schema_version": 1, "module_id": module_id,
        "module_definition_version": module["definition_version"],
        "run": {"run_id": run_id, "period": {"start": period_start, "end": period_end}},
        "module": module, "targets": targets, "sources": sources, "module_state": own_state,
    }
    return _freeze(payload)


def bundle_to_json(bundle: Mapping[str, Any]) -> str:
    """Sarjallista rajattu paketti lisäämättä koordinaattorin muuta tilaa."""
    return json.dumps(_thaw(bundle), ensure_ascii=False, sort_keys=True, indent=2) + "\n"
