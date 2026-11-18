"""Validoi elokuvahavaintojen ja jatkotoimien tuotantotietomallit.

Tarkistus varmistaa, että tuotannon toimintomääritys pysyy tyhjänä, kunnes
käyttäjä hyväksyy varsinaisen kriteerin ja Discord-käyttöönoton erikseen.
Testikriteerit sallitaan vain tests/fixtures-hakemistossa.
"""
from __future__ import annotations

import json
from pathlib import Path
import jsonschema

ROOT = Path(__file__).resolve().parents[1]


def read_json(relative_path: str) -> dict:
    """Lue JSON-tiedosto ja anna selkeä virhe puuttuvasta tai virheellisestä sisällöstä."""
    path = ROOT / relative_path
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"Tiedostoa {relative_path} ei voi lukea kelvollisena JSONina: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"Tiedoston {relative_path} ylimmän tason arvon pitää olla objekti.")
    return value


def validate(relative_path: str, schema_path: str) -> dict:
    """Tarkista tietue paikallista JSON Schema -skeemaa vasten."""
    schema = read_json(schema_path)
    jsonschema.Draft202012Validator.check_schema(schema)
    value = read_json(relative_path)
    errors = sorted(
        jsonschema.Draft202012Validator(
            schema, format_checker=jsonschema.FormatChecker()
        ).iter_errors(value),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        first = errors[0]
        raise ValueError(
            f"{relative_path}: virhe kohdassa {list(first.absolute_path)}: {first.message}"
        )
    return value


def main() -> None:
    """Validoi elokuvarekisteri, toimintomääritykset ja toimitusjonon."""
    validate(
        "data/movie-observations.json",
        "schemas/movie-observation-registry.schema.json",
    )
    production = validate(
        "data/movie-action-config.json",
        "schemas/movie-action-config.schema.json",
    )
    validate(
        "data/movie-action-outbox.json",
        "schemas/movie-action-outbox.schema.json",
    )
    validate(
        "tests/fixtures/movie-action-config.json",
        "schemas/movie-action-config.schema.json",
    )
    validate(
        "schemas/movie-action-event.schema.json",
        "schemas/movie-action-event.schema.json",
    )

    # Varsinaista tuotantokriteeriä tai Discord-toimintoa ei aktivoida ilman käyttäjän hyväksyntää.
    if production["actions"]:
        raise ValueError(
            "Tuotannon elokuvatoimintomääritys ei saa sisältää toimintoja ennen erillistä hyväksyntää."
        )

    fixture = read_json("tests/fixtures/movie-action-config.json")
    if any(
        not item["criterion_id"].startswith("test-")
        or not item["action_id"].startswith("test-")
        for item in fixture["actions"]
    ):
        raise ValueError("Testifixtuurissa saa olla vain test-alkuisia kriteeri- ja toimintotunnisteita.")

    print("Elokuvahavaintojen rekisteri ja jatkotoimien tietomallit ovat kelvollisia.")


if __name__ == "__main__":
    main()
