"""Validoi Aiheseuraimen seurantamoduulien tietosopimuksen ja esimerkit.

Skripti tarkistaa yhteisen JSON Schema -skeeman, sen tyypitetyn prosessilaajennuksen
sekä aihe- ja prosessimoduulin esimerkkimääritykset. Se tekee lisäksi rajattuja
negatiivisia kokeita, jotta skeema hylkää puuttuvat, virheelliset ja väärän
moduulityypin kentät. Skripti lukee tiedostoja mutta ei muuta niitä eikä kutsu
ulkoisia palveluja.
"""

from copy import deepcopy
import json
from pathlib import Path

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
MODULE_SCHEMA_PATH = ROOT / "schemas/seurantamoduuli.schema.json"
SCREENING_EXTENSION_SCHEMA_PATH = (
    ROOT / "schemas/module-extensions/event-watch-film-screenings.schema.json"
)
EXAMPLES = (
    ROOT / "examples/seurantamoduulit/tolkien.topic.json",
    ROOT / "examples/seurantamoduulit/intialaisten-elokuvien-naytosvahti.process.json",
)


def read_json(path: Path) -> dict:
    """Lue UTF-8-koodattu JSON-tiedosto ja palauta sen sisältö."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"Tiedostoa {path.relative_to(ROOT)} ei voi lukea JSONina: {exc}") from exc


def expect_invalid(validator, value: dict, description: str) -> None:
    """Varmista, että tarkoituksella virheellinen esimerkki hylätään."""
    errors = list(validator.iter_errors(value))
    if not errors:
        raise AssertionError(f"Skeema hyväksyi virheellisen tapauksen: {description}")


def validate_examples() -> None:
    """Tarkista skeemat, esimerkit ja sopimuksen tärkeimmät hylkäystapaukset."""
    module_schema = read_json(MODULE_SCHEMA_PATH)
    extension_schema = read_json(SCREENING_EXTENSION_SCHEMA_PATH)

    # check_schema varmistaa, että skeemat itse ovat JSON Schema Draft 2020-12 -kelvollisia.
    jsonschema.Draft202012Validator.check_schema(module_schema)
    jsonschema.Draft202012Validator.check_schema(extension_schema)

    module_validator = jsonschema.Draft202012Validator(module_schema)
    extension_validator = jsonschema.Draft202012Validator(extension_schema)

    examples = [read_json(path) for path in EXAMPLES]
    if [example.get("module_type") for example in examples] != ["topic", "process"]:
        raise AssertionError("Esimerkkien pitää kattaa topic- ja process-moduulit tässä järjestyksessä.")

    for path, example in zip(EXAMPLES, examples):
        errors = sorted(module_validator.iter_errors(example), key=lambda error: list(error.path))
        if errors:
            first = errors[0]
            raise AssertionError(
                f"{path.relative_to(ROOT)} ei täytä moduulisopimusta: "
                f"{first.message} (polku: {list(first.path)})"
            )

    # Prosessilaajennuksen oma skeema validoidaan erikseen. Yhteinen moduulisopimus
    # ei yritä tuntea jokaisen tulevan prosessityypin kaikkia omia kenttiä.
    process_metadata = examples[1]["process_extension"]
    # Esimerkin laajennustunnisteen, version ja skeemaosoitteen pitää viitata
    # täsmälleen siihen skeemaan, jota tämä tarkistin käyttää.
    if process_metadata["extension_id"] != "event-watch.film-screenings":
        raise AssertionError("Prosessiesimerkin laajennustunniste ei vastaa testattua laajennusta.")
    if process_metadata["extension_version"] != "1.1.0":
        raise AssertionError("Prosessiesimerkin laajennusversio ei vastaa testattua skeemaversiota.")
    if process_metadata["schema_uri"] != extension_schema.get("$id"):
        raise AssertionError("Prosessiesimerkin schema_uri ei vastaa laajennusskeeman $id-arvoa.")

    extension_configuration = process_metadata["configuration"]
    extension_validator.validate(extension_configuration)

    topic_example, process_example = examples

    # Pakollisen tunnisteen puuttuminen ei saa jäädä huomaamatta.
    invalid = deepcopy(topic_example)
    del invalid["module_id"]
    expect_invalid(module_validator, invalid, "module_id puuttuu")

    # Semanttisen version on oltava MAJOR.MINOR.PATCH-muotoinen.
    invalid = deepcopy(topic_example)
    invalid["definition_version"] = "versio-yksi"
    expect_invalid(module_validator, invalid, "virheellinen definition_version")

    # Aihemoduuli ei saa sisältää prosessilaajennusta eikä päinvastoin.
    invalid = deepcopy(topic_example)
    invalid["process_extension"] = deepcopy(process_example["process_extension"])
    expect_invalid(module_validator, invalid, "aihemoduulissa on prosessilaajennus")

    # Tuntemattomat juuritason kentät hylätään kirjoitusvirheiden havaitsemiseksi.
    invalid = deepcopy(topic_example)
    invalid["provider_api_key"] = "ei-sallittu"
    expect_invalid(module_validator, invalid, "tuntematon tai palveluntarjoajakohtainen kenttä")

    # Myös prosessilaajennuksen tuntemattomat kentät hylätään sen omassa skeemassa.
    invalid_extension = deepcopy(extension_configuration)
    invalid_extension["provider_model"] = "ei-sallittu"
    expect_invalid(extension_validator, invalid_extension, "tuntematon prosessilaajennuksen kenttä")

    # Väärä tapahtumatyyppi ei saa läpäistä elokuvanäytöslaajennuksen validointia.
    invalid_extension = deepcopy(extension_configuration)
    invalid_extension["event_type_ref"] = "../outside/event-type.json"
    expect_invalid(extension_validator, invalid_extension, "yhteensopimaton tapahtumatyyppi")


def main() -> None:
    """Aja moduulisopimuksen rakennetarkistukset ja tulosta selkeä tulos."""
    validate_examples()
    print("OK: moduulisopimuksen ja prosessilaajennuksen JSON Schema -skeemat ovat kelvollisia.")
    print("OK: aihe- ja prosessimoduulin esimerkit täyttävät tietosopimuksen.")
    print("OK: puuttuvat, virheelliset, yhteensopimattomat ja tuntemattomat kentät hylätään.")


if __name__ == "__main__":
    main()
