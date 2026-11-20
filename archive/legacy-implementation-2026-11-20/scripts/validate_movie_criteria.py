"""Validoi elokuvien hakukriteerien tuotantotiedosto ja testifixtuurit.

Tuotannon kriteeritiedosto pidetään tyhjänä, kunnes käyttäjä on hyväksynyt
varsinaiset uudet kiinnostuksen kohteet. Testikriteerit sallitaan vain tests/fixtures-kansiossa.
"""
from __future__ import annotations

import json
from pathlib import Path

from scripts.movie_actions import validate_action_config
from scripts.movie_criteria import (
    validate_action_references, validate_criteria_registry,
)

ROOT = Path(__file__).resolve().parents[1]


def read_json(relative_path: str) -> dict:
    """Lue JSON-objekti ja ilmoita puuttuvasta tai virheellisestä tiedostosta."""
    path = ROOT / relative_path
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"Tiedostoa {relative_path} ei voi lukea kelvollisena JSONina: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"Tiedoston {relative_path} ylimmän tason arvon pitää olla objekti.")
    return value


def main() -> None:
    """Validoi tuotannon tyhjän rekisterin ja testifixtuurien kriteeri-/toimintoviitteet."""
    production = read_json("data/movie-search-criteria.json")
    production_actions = read_json("data/movie-action-config.json")
    validate_criteria_registry(production)
    validate_action_config(production_actions)
    validate_action_references(production, production_actions)

    # Varsinaisia kriteerejä ei aktivoida ennen käyttäjän hyväksyntää.
    if production["criteria"]:
        raise ValueError(
            "Tuotannon hakukriteeritiedosto pitää jättää tyhjäksi, kunnes käyttäjä hyväksyy kriteerit."
        )

    fixture = read_json("tests/fixtures/movie-search-criteria.json")
    fixture_actions = read_json("tests/fixtures/movie-action-config.json")
    validate_criteria_registry(fixture)
    validate_action_config(fixture_actions)
    validate_action_references(fixture, fixture_actions)
    if any(not item["criterion_id"].startswith("test-") for item in fixture["criteria"]):
        raise ValueError("Testifixtuurin kriteeritunnisteiden pitää alkaa test- etuliitteellä.")

    print("Elokuvien hakukriteerit ja niiden toimintoviitteet ovat kelvollisia.")


if __name__ == "__main__":
    main()
