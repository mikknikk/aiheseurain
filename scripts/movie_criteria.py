"""Käyttäjän hyväksymien elokuvien hakukriteerien validointi ja arviointi.

Moduuli ei sisällä käyttäjän kiinnostuksen kohteita. Tuotannon kriteeritiedosto
aloitetaan tyhjänä; testikriteerit ovat erillisessä testifixtuurissa.
"""
from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
import unicodedata
from typing import Any
import jsonschema

ROOT = Path(__file__).resolve().parents[1]
CRITERIA_SCHEMA = ROOT / "schemas/movie-search-criteria.schema.json"
ARRAY_FIELDS = {
    "aliases", "director_ids", "cast_ids", "production_company_ids",
    "franchise_ids", "countries", "languages", "genres", "keywords",
}
SUPPORTED_FIELDS = ARRAY_FIELDS | {"title", "release_year", "release_type"}


class MovieCriteriaError(ValueError):
    """Hakukriteerin skeema-, versio- tai arviointivirhe."""


def _aware_datetime(value: str) -> datetime:
    """Lue ISO-aikaleima ja vaadi aikavyöhykkeen sisältävä arvo."""
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, TypeError, ValueError) as exc:
        raise MovieCriteriaError("Kriteerin aikaleima ei ole kelvollinen ISO 8601 -arvo.") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise MovieCriteriaError("Kriteerin aikaleimasta puuttuu aikavyöhyke.")
    return parsed


def normalize_value(value: str) -> str:
    """Normalisoi vertailtavan tekstin muuttamatta kirjainten kirjoitusjärjestelmää."""
    normalized = unicodedata.normalize("NFKC", value).casefold()
    output = []
    current = []
    for character in normalized:
        if character.isalnum():
            current.append(character)
        elif current:
            output.append("".join(current))
            current = []
    if current:
        output.append("".join(current))
    return " ".join(output)


def validate_criteria_registry(registry: dict[str, Any]) -> None:
    """Validoi skeema, tunniste/versio-yhdistelmät ja aktiiviset versiot."""
    schema = json.loads(CRITERIA_SCHEMA.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(schema)
    errors = sorted(
        jsonschema.Draft202012Validator(
            schema, format_checker=jsonschema.FormatChecker()
        ).iter_errors(registry),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        first = errors[0]
        raise MovieCriteriaError(
            f"Kriteerirekisterin virhe kohdassa {list(first.absolute_path)}: {first.message}"
        )
    seen_versions = set()
    active_by_id = {}
    for criterion in registry["criteria"]:
        key = (criterion["criterion_id"], criterion["version"])
        if key in seen_versions:
            raise MovieCriteriaError("Sama criterion_id/version on määritelty kahdesti.")
        seen_versions.add(key)
        start = _aware_datetime(criterion["valid_from"])
        end = criterion["valid_until"]
        if end is not None and _aware_datetime(end) <= start:
            raise MovieCriteriaError("Kriteerin valid_until pitää olla valid_from-arvoa myöhempi.")
        if _aware_datetime(criterion["updated_at"]) < _aware_datetime(criterion["created_at"]):
            raise MovieCriteriaError("Kriteerin updated_at ei voi olla created_at-arvoa aiempi.")
        if criterion["status"] == "active":
            active_by_id[criterion["criterion_id"]] = active_by_id.get(criterion["criterion_id"], 0) + 1
        for condition in criterion["include_conditions"] + criterion["exclude_conditions"]:
            validate_condition(condition)
    if any(count > 1 for count in active_by_id.values()):
        raise MovieCriteriaError("Samalla criterion_id-tunnisteella voi olla vain yksi aktiivinen versio.")


def validate_condition(condition: dict[str, Any]) -> None:
    """Varmista, että ehto käyttää kentälle sallittua operaattoria ja arvorakennetta."""
    field = condition["field"]
    operator = condition["operator"]
    value = condition["value"]
    if field not in SUPPORTED_FIELDS:
        raise MovieCriteriaError(f"Tuntematon kriteerikenttä: {field}")
    if operator == "in_range":
        if field != "release_year" or not isinstance(value, dict):
            raise MovieCriteriaError("in_range on sallittu vain julkaisuvuodelle.")
        if value["min"] > value["max"]:
            raise MovieCriteriaError("Vuosihaarukan min-arvo ylittää max-arvon.")
    elif operator == "contains_any_normalized":
        if field not in ARRAY_FIELDS or not isinstance(value, list):
            raise MovieCriteriaError("contains_any_normalized vaatii listakentän ja merkkijonolistauksen.")
    elif operator == "equals":
        if field not in {"title", "release_type"} or not isinstance(value, str):
            raise MovieCriteriaError("equals on sallittu vain tekstimuotoisille scalar-kentille.")
    elif operator == "contains_normalized":
        if field == "release_year" or not isinstance(value, str):
            raise MovieCriteriaError("contains_normalized vaatii tekstikentän ja merkkijonoarvon.")
    else:
        raise MovieCriteriaError(f"Tuntematon vertailuoperaattori: {operator}")


def validate_action_references(
    criteria_registry: dict[str, Any], action_config: dict[str, Any]
) -> None:
    """Varmista, että kriteerien action_ids-viitteet vastaavat #66:n toimintomääritystä."""
    validate_criteria_registry(criteria_registry)
    action_pairs = {
        (item["criterion_id"], item["action_id"])
        for item in action_config.get("actions", [])
    }
    criterion_pairs = {
        (criterion["criterion_id"], action_id)
        for criterion in criteria_registry["criteria"]
        for action_id in criterion["action_ids"]
    }
    missing = criterion_pairs - action_pairs
    unreferenced = action_pairs - criterion_pairs
    if missing:
        raise MovieCriteriaError(f"Kriteeriltä puuttuu #66:n toimintomääritys: {sorted(missing)}")
    if unreferenced:
        raise MovieCriteriaError(f"#66:n toimintomäärityksellä ei ole kriteeriviitettä: {sorted(unreferenced)}")


def _field_value(movie: dict[str, Any], field: str) -> Any:
    """Palauta kriteerin vertailema elokuvan metatieto."""
    return movie.get(field)


def _matches_condition(movie: dict[str, Any], condition: dict[str, Any]) -> bool:
    """Arvioi yhden sisällyttävän tai poissulkevan ehdon."""
    field = condition["field"]
    operator = condition["operator"]
    expected = condition["value"]
    actual = _field_value(movie, field)
    if actual is None:
        return False
    if operator == "in_range":
        return isinstance(actual, int) and expected["min"] <= actual <= expected["max"]
    if operator == "equals":
        return isinstance(actual, str) and normalize_value(actual) == normalize_value(expected)
    if operator == "contains_any_normalized":
        actual_values = actual if isinstance(actual, list) else [actual]
        expected_values = {normalize_value(item) for item in expected}
        return any(
            isinstance(item, str) and normalize_value(item) in expected_values
            for item in actual_values
        )
    expected_value = normalize_value(expected)
    actual_values = actual if isinstance(actual, list) else [actual]
    return any(
        isinstance(item, str) and normalize_value(item) == expected_value
        for item in actual_values
    )


def evaluate_movie_criteria(
    movie: dict[str, Any],
    registry: dict[str, Any],
    observed_at: str,
    source_urls: list[str],
) -> list[dict[str, Any]]:
    """Palauta kaikki aktiiviset kriteeriosumat #66:n havaintorekisterille."""
    validate_criteria_registry(registry)
    observed = _aware_datetime(observed_at)
    if not isinstance(source_urls, list):
        raise MovieCriteriaError("Kriteeriarvioinnin lähteiden pitää olla lista.")
    if any(not isinstance(url, str) for url in source_urls):
        raise MovieCriteriaError("Kriteeriarvioinnin lähdeviitteiden pitää olla merkkijonoja.")
    sources = sorted(set(source_urls))
    if any(not url.startswith(("https://", "http://")) for url in sources):
        raise MovieCriteriaError("Kriteeriosuman lähteiden pitää olla HTTP(S)-osoitteita.")
    matches = []
    for criterion in registry["criteria"]:
        if criterion["status"] != "active":
            continue
        if observed < _aware_datetime(criterion["valid_from"]):
            continue
        if criterion["valid_until"] is not None and observed >= _aware_datetime(criterion["valid_until"]):
            continue
        include = criterion["include_conditions"]
        include_results = [_matches_condition(movie, condition) for condition in include]
        included = all(include_results) if criterion["match_policy"] == "all" else any(include_results)
        if not included:
            continue
        if any(_matches_condition(movie, condition) for condition in criterion["exclude_conditions"]):
            continue
        matched_reasons = [
            condition["reason"]
            for condition, matched in zip(include, include_results)
            if matched
        ]
        if not sources:
            raise MovieCriteriaError("Kriteeriosuma vaatii vähintään yhden lähdeviitteen.")
        matches.append({
            "criterion_id": criterion["criterion_id"],
            "criterion_version": criterion["version"],
            "matched_at": observed_at,
            "reason": " ".join(matched_reasons),
            "source_urls": sources,
        })
    return sorted(matches, key=lambda item: (item["criterion_id"], item["criterion_version"]))
