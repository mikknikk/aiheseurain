"""Validoi moduulien, seurantakohteiden, julkaisukohteiden ja reititysten viitteet."""
from __future__ import annotations
import json
from pathlib import Path
import jsonschema
ROOT = Path(__file__).resolve().parents[1]
def read(path: Path):
    """Lue JSON-tiedosto UTF-8-muodossa."""
    return json.loads(path.read_text(encoding="utf-8"))
def validate(root: Path = ROOT) -> list[str]:
    """Tarkista skeemat, pysyvät tunnisteet ja kaikkien viitteiden eheys."""
    errors=[]
    names=["seurantamoduuli.schema.json","seurantakohde.schema.json","julkaisukohde.schema.json","julkaisureititys.schema.json","seurantakohderekisteri.schema.json","julkaisukohderekisteri.schema.json"]
    schemas={name:read(root/"schemas"/name) for name in names}
    for schema in schemas.values(): jsonschema.Draft202012Validator.check_schema(schema)
    modules=read(root/"data/module-registry.json")["modules"]; module_ids={m["module_id"] for m in modules}
    targets=read(root/"data/target-registry.json")["targets"]; target_ids=[x["target_id"] for x in targets]
    if len(target_ids)!=len(set(target_ids)): errors.append("Seurantakohderekisterissä on duplikaattitunniste.")
    target_by_id={}
    for entry in targets:
        path=root/entry["path"]
        if not path.is_file(): errors.append(f"Seurantakohteen tiedosto puuttuu: {entry['path']}"); continue
        target=read(path); target_by_id[entry["target_id"]]=target
        errors.extend(f"{entry['target_id']}: {e.message}" for e in jsonschema.Draft202012Validator(schemas["seurantakohde.schema.json"]).iter_errors(target))
        if target.get("target_id")!=entry["target_id"]: errors.append(f"Tunniste ei vastaa rekisteriä: {entry['target_id']}")
        if target.get("module_ref",{}).get("module_id") not in module_ids: errors.append(f"Tuntematon moduuliviite: {entry['target_id']}")
    for module in modules:
        path=root/module["path"]
        if not path.is_file(): errors.append(f"Moduulitiedosto puuttuu: {module['path']}"); continue
        definition=read(path)
        errors.extend(f"{module['module_id']}: {e.message}" for e in jsonschema.Draft202012Validator(schemas["seurantamoduuli.schema.json"]).iter_errors(definition))
        for target_id in definition.get("target_refs",[]):
            if target_id not in target_by_id: errors.append(f"{module['module_id']}: tuntematon seurantakohde {target_id}")
            elif target_by_id[target_id].get("module_ref",{}).get("module_id")!=module["module_id"]: errors.append(f"{module['module_id']}: kohde kuuluu toiselle moduulille: {target_id}")
    publications=read(root/"data/publication-registry.json")["publications"]; publication_by_id={}
    for entry in publications:
        path=root/entry["path"]
        if not path.is_file(): errors.append(f"Julkaisukohteen tiedosto puuttuu: {entry['path']}"); continue
        publication=read(path); publication_by_id[entry["publication_id"]]=publication
        errors.extend(f"{entry['publication_id']}: {e.message}" for e in jsonschema.Draft202012Validator(schemas["julkaisukohde.schema.json"]).iter_errors(publication))
        if publication.get("publication_id")!=entry["publication_id"]: errors.append(f"Julkaisukohteen tunniste ei vastaa rekisteriä: {entry['publication_id']}")
    routing=read(root/"data/publication-routing.json")
    errors.extend(e.message for e in jsonschema.Draft202012Validator(schemas["julkaisureititys.schema.json"]).iter_errors(routing))
    route_ids=set()
    target_publications={}
    for route in routing.get("routes",[]):
        if route["route_id"] in route_ids: errors.append(f"Duplikaatti reititystunniste: {route['route_id']}")
        route_ids.add(route["route_id"])
        if route["module_ref"] not in module_ids: errors.append(f"Tuntematon moduuliviite reitillä {route['route_id']}")
        if route["target_ref"] not in target_by_id: errors.append(f"Tuntematon seurantakohde reitillä {route['route_id']}")
        elif target_by_id[route["target_ref"]].get("module_ref",{}).get("module_id")!=route["module_ref"]: errors.append(f"Reitin kohde kuuluu toiselle moduulille: {route['route_id']}")
        if len(route.get("publication_refs",[])) != 1:
            errors.append(f"Reitillä pitää olla täsmälleen yksi julkaisukohde: {route['route_id']}")
        elif route["target_ref"] in target_publications and target_publications[route["target_ref"]] != route["publication_refs"][0]:
            errors.append(f"Seurantakohde viittaa useaan julkaisukohteeseen: {route['target_ref']}")
        elif route.get("target_ref"):
            target_publications[route["target_ref"]] = route["publication_refs"][0]
        for pub_id in route["publication_refs"]:
            if pub_id not in publication_by_id: errors.append(f"Tuntematon julkaisukohde reitillä {route['route_id']}: {pub_id}")
    return errors
if __name__=="__main__":
    found=validate()
    if found: raise SystemExit("\\n".join(found))
    print("OK: moduuli-, kohde-, julkaisu- ja reititysviitteet ovat eheät.")
