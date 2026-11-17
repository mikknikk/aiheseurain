"""Validoi nykyisten aiheiden ja prosessien moduulimigraation kokonaisuuden.

Tämä tarkistus täydentää yleistä moduulirekisterin validaattoria: se varmistaa
nykyisten tehtäväkohtaisten lähderekisterien vastaavuuden, passiivisen käyttöönoton
ja näytösvahtimoduulin tapahtumatyyppiviitteen. Se ei muuta tuotantotietoja.
"""
from __future__ import annotations

from pathlib import Path
import json
import tempfile

from scripts.event_watch import load_event_type
from scripts.module_registry import ROOT, REGISTRY_PATH, load_registry


MODULE_TASKS = {
    "tolkien": "tolkien",
    "taylor-swift": "taylor_swift",
    "gurmeet-ram-rahim-singh": "gurmeet_ram_rahim_singh",
    "muumit": "muumit",
    "wakaliwood": "wakaliwood",
    "euroviisut": "euroviisut",
    "sompote-sands": "sompote_sands",
    "shakkidraamat": "shakkidraamat",
    "indian-film-news": "intialaiset_elokuvat_uutiset",
    "indian-film-screening-watch": "intialaiset_elokuvat_naytokset",
}
EXPECTED_TYPES = {"topic": 9, "process": 1}


def _read_json(path: Path):
    """Lue JSON-tiedosto ja palauta sen sisältö."""
    return json.loads(path.read_text(encoding="utf-8"))


def _source_role(source_type: str) -> str:
    """Muunna yhteisen lähdekatalogin lähdetyyppi moduulin viiterooliksi."""
    return {
        "primary": "primary",
        "editorial": "secondary",
        "research": "verification",
    }.get(source_type, "discovery")


def validate_migration() -> list[str]:
    """Palauta kaikki havaitut migraation eheysvirheet muuttamatta lähdetiedostoja."""
    errors: list[str] = []
    registry = _read_json(REGISTRY_PATH)
    entries = registry.get("modules", [])
    entry_by_id = {entry.get("module_id"): entry for entry in entries if isinstance(entry, dict)}

    if set(entry_by_id) != set(MODULE_TASKS):
        errors.append(
            "Rekisterin moduulitunnisteet eivät vastaa nykyisiä kymmentä seurantaa: "
            f"puuttuvat={sorted(set(MODULE_TASKS) - set(entry_by_id))}, "
            f"ylimääräiset={sorted(set(entry_by_id) - set(MODULE_TASKS))}."
        )

    actual_types: dict[str, int] = {}
    for entry in entries:
        if isinstance(entry, dict):
            actual_types[entry.get("module_type", "")] = actual_types.get(entry.get("module_type", ""), 0) + 1
            if entry.get("status") != "inactive":
                errors.append(
                    f"{entry.get('module_id')}: migraation moduuli pitää jättää inactive-tilaan."
                )
    if actual_types != EXPECTED_TYPES:
        errors.append(f"Moduulityyppien määrät ovat virheelliset: {actual_types!r}.")

    catalog = _read_json(ROOT / "data/source-catalog.json")
    catalog_sources = {source["id"]: source for source in catalog["sources"]}

    for module_id, task_id in MODULE_TASKS.items():
        entry = entry_by_id.get(module_id)
        if not entry:
            continue
        definition_path = (ROOT / entry.get("path", "")).resolve()
        if not definition_path.is_relative_to(ROOT.resolve()) or not definition_path.is_file():
            errors.append(f"{module_id}: moduulimäärityksen polku ei ole kelvollinen.")
            continue
        definition = _read_json(definition_path)
        if definition.get("module_id") != module_id:
            errors.append(f"{module_id}: tiedoston moduulitunniste ei vastaa rekisteriä.")

        source_registry_path = ROOT / f"data/sources/{task_id}.json"
        if not source_registry_path.is_file():
            errors.append(f"{module_id}: tehtäväkohtaista lähderekisteriä ei löydy ({task_id}).")
            continue
        task_sources = _read_json(source_registry_path)
        expected = {item["source_id"]: item for item in task_sources["sources"]}
        actual = {item["source_id"]: item for item in definition.get("source_refs", [])}
        if set(actual) != set(expected):
            errors.append(
                f"{module_id}: lähdeviitteet eivät vastaa tehtäväkohtaista rekisteriä; "
                f"puuttuvat={sorted(set(expected) - set(actual))}, "
                f"ylimääräiset={sorted(set(actual) - set(expected))}."
            )
        for source_id, reference in actual.items():
            catalog_source = catalog_sources.get(source_id)
            if catalog_source is None:
                errors.append(f"{module_id}: lähde {source_id} puuttuu yhteisestä lähdekatalogista.")
                continue
            expected_role = _source_role(catalog_source["source_type"])
            if reference.get("role") != expected_role:
                errors.append(f"{module_id}: lähteen {source_id} rooli ei vastaa lähdekatalogia.")
            if reference.get("required", False) != bool(expected.get(source_id, {}).get("critical")):
                errors.append(f"{module_id}: lähteen {source_id} required-arvo ei vastaa critical-arvoa.")

        profiles = definition.get("search_profiles", [])
        if not profiles:
            errors.append(f"{module_id}: hakuprofiili puuttuu.")
        else:
            languages = sorted({
                language for source_id in expected
                for language in catalog_sources.get(source_id, {}).get("language_regions", [])
            })
            regions = sorted({
                region for source_id in expected
                for region in catalog_sources.get(source_id, {}).get("regions", [])
            })
            if profiles[0].get("languages") != languages:
                errors.append(f"{module_id}: pääprofiilin kielet eivät vastaa lähderekisterin kattavuutta.")
            if profiles[0].get("regions") != regions:
                errors.append(f"{module_id}: pääprofiilin alueet eivät vastaa lähderekisterin kattavuutta.")

    # Yleinen lataaja ohittaa tarkoituksella inactive-merkintöjen määritystiedostot.
    # Tee siksi vain tarkistusta varten väliaikainen aktiivinen rekisterikopio, jotta
    # jokainen moduuli ja prosessilaajennus validoidaan samalla tuotantolataajalla.
    validation_registry = dict(registry)
    validation_registry["modules"] = [
        {**entry, "status": "active"} for entry in entries
    ]
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", suffix=".json",
            dir=REGISTRY_PATH.parent, delete=False
        ) as handle:
            json.dump(validation_registry, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            temporary_path = Path(handle.name)
        loaded = load_registry(temporary_path, root=ROOT)
        for module in loaded.modules:
            if module.status != "active" or module.definition is None:
                errors.append(f"{module.module_id}: moduulimääritys ei validoidu: {module.error}")
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)

    process = entry_by_id.get("indian-film-screening-watch")
    if process:
        definition_path = ROOT / process["path"]
        process_definition = _read_json(definition_path)
        config = process_definition["process_extension"]["configuration"]
        event_type_path = (ROOT / config["event_type_ref"]).resolve()
        if not event_type_path.is_relative_to(ROOT.resolve()) or not event_type_path.is_file():
            errors.append("Näytösvahtimoduulin tapahtumatyyppiviite ei osoita paikalliseen moduulitiedostoon.")
        else:
            try:
                event_type = load_event_type(event_type_path)
                if event_type.get("event_type_id") != "film-screening":
                    errors.append("Näytösvahtimoduulin tapahtumatyyppi ei ole film-screening.")
                if config["identity"]["event_key_fields"] != event_type.get("identity_fields"):
                    errors.append("Näytösvahtimoduulin identiteettikentät eivät vastaa tapahtumatyyppimääritystä.")
            except (ValueError, KeyError) as exc:
                errors.append(f"Näytösvahtimoduulin tapahtumatyyppimääritys ei validoidu: {exc}")

    return errors


def main() -> None:
    """Tulosta migraation tarkistuksen tulokset ja epäonnistu virheisiin."""
    errors = validate_migration()
    if errors:
        for error in errors:
            print(f"VIRHE: {error}")
        raise SystemExit(f"Moduulimigraatiossa havaittiin {len(errors)} virhettä.")
    print("OK: 9 aihemoduulia ja 1 prosessimoduuli on validoitu.")
    print("OK: kaikki lähdeviitteet, kielet ja alueet vastaavat nykyisiä lähderekistereitä.")
    print("OK: kaikki moduulit ovat passiivisia; yhtään moduulia ei aktivoitu.")
    print("OK: näytösvahtimoduulin tapahtumatyyppi ja identiteettikentät vastaavat yhteistä tapahtumavahtia.")


if __name__ == "__main__":
    main()
