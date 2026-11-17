#!/usr/bin/env python3
"""
Validoi GitHub Actionsissa muodostetun Kehitysjonon JSON-aineiston.

Skripti tarkistaa ensin JSON Schema -rakenteen ja sen jälkeen projektin
omat eheysvaatimukset. Se ei hae tietoja verkosta eikä muuta aineistoa.
"""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema


# Projektin juurikansio on tämän skriptin yläpuolella.
ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data/kehitysjono.json"
SCHEMA_PATH = ROOT / "schemas/kehitysjono.schema.json"


def validate_dataset(dataset: dict, schema: dict) -> None:
    """Tarkistaa skeeman ja issueiden sekä riippuvuuksien keskinäisen eheyden.

    JSON Schema tarkistaa yksittäisten kenttien tyypit ja pakolliset arvot.
    Tässä tarkistetaan lisäksi suhteet, joita skeema ei yksin pysty ilmaisemaan:
    issueiden yksilöllisyys, yksi riippuvuustietue kutakin issuea kohti sekä
    ilmoitettujen lukumäärien vastaavuus todelliseen sisältöön.
    """
    jsonschema.Draft202012Validator.check_schema(schema)
    validator = jsonschema.Draft202012Validator(
        schema, format_checker=jsonschema.FormatChecker()
    )
    errors = sorted(
        validator.iter_errors(dataset),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        first = errors[0]
        location = ".".join(str(part) for part in first.absolute_path) or "(juuri)"
        raise ValueError(f"JSON Schema -virhe kohdassa {location}: {first.message}")

    issues = dataset["issues"]
    dependencies = dataset["dependencies"]
    issue_numbers = [issue["number"] for issue in issues]
    dependency_numbers = [item["issueNumber"] for item in dependencies]

    if len(set(issue_numbers)) != len(issue_numbers):
        raise ValueError("Issue-numero esiintyy aineistossa useammin kuin kerran.")
    if dataset["issue_count"] != len(issues):
        raise ValueError("issue_count ei vastaa issues-listan pituutta.")
    if len(dependencies) != len(issues):
        raise ValueError("Riippuvuustietueita ei ole täsmälleen yhtä kutakin issuea kohti.")
    if len(set(dependency_numbers)) != len(dependency_numbers):
        raise ValueError("Riippuvuustietue esiintyy useammin kuin kerran.")
    if set(dependency_numbers) != set(issue_numbers):
        raise ValueError("Riippuvuustietueiden issue-numerot eivät vastaa issues-listaa.")

    relation_count = sum(len(item["blockedBy"]) for item in dependencies)
    if dataset["dependency_relation_count"] != relation_count:
        raise ValueError("dependency_relation_count ei vastaa riippuvuussuhteiden määrää.")

    for item in dependencies:
        for blocker in item["blockedBy"]:
            if blocker["number"] == item["issueNumber"]:
                raise ValueError(
                    f"Tiketti #{item['issueNumber']} ei voi olla oman itsensä edeltäjä."
                )


def main() -> None:
    """Lukee Pages-buildin työtilaan muodostetun JSONin ja sen skeeman."""
    try:
        dataset = json.loads(DATA_PATH.read_text(encoding="utf-8"))
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        validate_dataset(dataset, schema)
    except (OSError, json.JSONDecodeError, UnicodeDecodeError, jsonschema.SchemaError, ValueError) as error:
        raise SystemExit(f"Kehitysjonon aineiston validointi epäonnistui: {error}") from error

    print(
        "OK: Kehitysjonon aineisto vastaa skeemaa; "
        f"{dataset['issue_count']} tikettiä ja "
        f"{dataset['dependency_relation_count']} riippuvuussuhdetta."
    )


if __name__ == "__main__":
    main()
