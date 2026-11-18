"""Testaa elokuvien hakukriteerien validointi, yhdistäminen ja arviointi."""
from copy import deepcopy
from pathlib import Path
import json
import unittest

from scripts.movie_criteria import (
    MovieCriteriaError, evaluate_and_build_movie_observation,
    evaluate_movie_criteria, normalize_value,
    validate_action_references, validate_criteria_registry,
)

ROOT = Path(__file__).resolve().parents[1]
OBSERVED = "2026-11-18T08:00:00+02:00"
SOURCES = ["https://example.test/film"]


def fixture():
    """Lataa testikriteerit erillisestä testifixtuurista."""
    return json.loads((ROOT / "tests/fixtures/movie-search-criteria.json").read_text(encoding="utf-8"))


def action_fixture():
    """Lataa #66:n testitoimintojen määrityksen."""
    return json.loads((ROOT / "tests/fixtures/movie-action-config.json").read_text(encoding="utf-8"))


def matching_movie():
    """Luo metatiedot, jotka osuvat kahteen testikriteeriin."""
    return {
        "title": "Testielokuva",
        "aliases": ["Test Movie"],
        "director_ids": ["person:test-director"],
        "cast_ids": ["person:test-actor"],
        "production_company_ids": ["company:test-studio"],
        "franchise_ids": [],
        "countries": ["IN"],
        "languages": ["te"],
        "genres": ["drama"],
        "keywords": ["action"],
        "release_year": 2024,
        "release_type": "feature",
    }


class MovieCriteriaTests(unittest.TestCase):

    def test_criteria_matches_are_written_to_movie_observation_registry(self):
        """Kaikki osuneet kriteerit ja niiden syyt siirtyvät #66:n havaintorekisteriin."""
        metadata = matching_movie()
        metadata.update({
            "primary_title": "Testielokuva",
            "external_ids": [{"provider": "imdb", "value": "tt7654321"}],
        })
        screening_event = {
            "canonical_event_id": "screening-criteria-1",
            "attributes": {
                "title": "Testielokuva", "venue": "Testiteatteri",
                "city": "Helsinki", "starts_at": OBSERVED, "status": "scheduled",
            },
            "sources": [{
                "publisher": "Testiteatteri", "url": SOURCES[0],
                "checked_at": OBSERVED, "claim_level": "official",
            }],
        }
        observation = evaluate_and_build_movie_observation(
            screening_event, metadata, fixture(), OBSERVED, SOURCES,
        )
        self.assertEqual(
            {item["criterion_id"] for item in observation["criterion_matches"]},
            {"test-criterion-a", "test-criterion-b"},
        )
        self.assertIn("user-criteria", observation["discovery_channels"])
        self.assertIn("indian-film-screening-baseline", observation["discovery_channels"])

    def test_multiple_active_criteria_return_all_stable_matches(self):
        """Kaikki osuneet aktiiviset kriteerit palautuvat omilla tunnisteillaan ja versioillaan."""
        matches = evaluate_movie_criteria(
            matching_movie(), fixture(), OBSERVED, SOURCES,
        )
        self.assertEqual(
            {item["criterion_id"] for item in matches},
            {"test-criterion-a", "test-criterion-b"},
        )
        self.assertTrue(all(item["criterion_version"] == "1.0.0" for item in matches))
        self.assertTrue(all(item["source_urls"] == SOURCES for item in matches))

    def test_exclusion_condition_overrides_inclusion(self):
        """Poissulkeva ehto estää osuman, vaikka kaikki sisällyttävät ehdot täyttyvät."""
        movie = matching_movie()
        movie["release_type"] = "short"
        matches = evaluate_movie_criteria(movie, fixture(), OBSERVED, SOURCES)
        self.assertEqual(
            {item["criterion_id"] for item in matches},
            {"test-criterion-b"},
        )

    def test_any_match_policy_accepts_one_of_several_values(self):
        """any-politiikka riittää, kun vähintään yksi kieliarvo täsmää."""
        movie = matching_movie()
        movie["languages"] = ["ta"]
        matches = evaluate_movie_criteria(movie, fixture(), OBSERVED, SOURCES)
        self.assertIn("test-criterion-b", {item["criterion_id"] for item in matches})

    def test_paused_and_future_criteria_are_not_evaluated(self):
        """Keskeytetty tai vasta myöhemmin voimaan tuleva kriteeri ei tuota osumaa."""
        registry = fixture()
        paused = next(item for item in registry["criteria"] if item["criterion_id"] == "test-paused-criterion")
        paused["include_conditions"][0]["value"] = "drama"
        future = deepcopy(registry["criteria"][0])
        future["criterion_id"] = "test-future"
        future["valid_from"] = "2026-11-19T00:00:00+02:00"
        future["action_ids"] = []
        registry["criteria"].append(future)
        matches = evaluate_movie_criteria(matching_movie(), registry, OBSERVED, SOURCES)
        ids = {item["criterion_id"] for item in matches}
        self.assertNotIn("test-paused-criterion", ids)
        self.assertNotIn("test-future", ids)

    def test_match_requires_source_evidence(self):
        """Kriteeriosumaa ei palauteta ilman jäljitettävää lähdeviitettä."""
        with self.assertRaises(MovieCriteriaError):
            evaluate_movie_criteria(matching_movie(), fixture(), OBSERVED, [])

    def test_criteria_and_action_references_must_match(self):
        """Kriteeritiedoston action_ids-viitteet vastaavat #66:n toimintomäärityksiä."""
        validate_action_references(fixture(), action_fixture())
        broken = action_fixture()
        broken["actions"] = broken["actions"][:1]
        with self.assertRaises(MovieCriteriaError):
            validate_action_references(fixture(), broken)

    def test_invalid_condition_field_operator_pair_is_rejected(self):
        """Väärä operaattori/kenttä-yhdistelmä havaitaan ennen hakua."""
        registry = fixture()
        criterion = registry["criteria"][0]
        criterion["include_conditions"][0]["operator"] = "in_range"
        criterion["include_conditions"][0]["value"] = {"min": 1, "max": 2}
        with self.assertRaises(MovieCriteriaError):
            validate_criteria_registry(registry)

    def test_invalid_year_range_is_rejected(self):
        """Virheellinen vuosihaarukka ei voi päästä tuotantohakuun."""
        registry = fixture()
        registry["criteria"][0]["include_conditions"][1]["value"] = {"min": 2030, "max": 2020}
        with self.assertRaises(MovieCriteriaError):
            validate_criteria_registry(registry)

    def test_normalization_preserves_non_latin_letters_and_ignores_punctuation(self):
        """Unicode-normalisointi säilyttää kirjoitusjärjestelmät ja tasaa välimerkit."""
        self.assertEqual(normalize_value("  Téѕt—FILM! "), normalize_value("Téѕt film"))
        self.assertEqual(normalize_value("தமிழ்"), normalize_value("தமிழ்"))

    def test_production_criteria_file_stays_empty(self):
        """Uusia kiinnostuksen kohteita ei aktivoida ilman käyttäjän hyväksyntää."""
        production = json.loads((ROOT / "data/movie-search-criteria.json").read_text(encoding="utf-8"))
        self.assertEqual(production["criteria"], [])


if __name__ == "__main__":
    unittest.main()
