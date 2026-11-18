"""Testaa elokuvahavaintojen identiteetti, yhdistäminen ja tallennus."""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

from scripts.movie_observations import (
    JsonFileMovieRegistryStore, MovieObservationError, MovieRegistryConflictError,
    build_movie_observation, empty_registry, merge_movie_observation,
    build_observations_from_screening_state, normalize_title,
    reconcile_movie_observations, screening_snapshot, validate_registry,
)

NOW = "2026-11-18T08:00:00+02:00"
LATER = "2026-11-18T09:00:00+02:00"


def screening(screening_id, title="Testielokuva"):
    """Luo yleisen tapahtumavahdin film-screening-tilasta irrotetun näytöshavainnon."""
    return {
        "canonical_event_id": screening_id,
        "attributes": {"title": title, "venue": "Testiteatteri", "starts_at": LATER, "status": "scheduled"},
        "sources": [{
            "publisher": "Testiteatteri", "url": f"https://example.test/{screening_id}",
            "checked_at": NOW, "claim_level": "official",
        }],
    }


def criterion(criterion_id="test-criterion", matched_at=NOW, reason="Testikriteeri osui"):
    """Luo testikriteerin osuman."""
    return {
        "criterion_id": criterion_id, "criterion_version": "1.0.0",
        "matched_at": matched_at, "reason": reason,
        "source_urls": ["https://example.test/criterion"],
    }


class MovieObservationTests(unittest.TestCase):

    def test_screening_state_is_the_source_and_movie_registry_only_aggregates(self):
        """#109:n film-screening-tila on lähde; elokuvarekisteriin tallentuu vain viite."""
        event = screening("screening-1", "Elokuva A")
        event_state = {"event_type_id": "film-screening", "current_events": [event]}
        observations = build_observations_from_screening_state(
            event_state,
            {"screening-1": {"primary_title": "Elokuva A", "release_year": 2021}},
            {"screening-1": [criterion()]},
            NOW,
        )
        self.assertEqual(len(observations), 1)
        self.assertEqual(observations[0]["screening_refs"], ["screening-1"])
        self.assertNotIn("venue", observations[0])
        snapshot = screening_snapshot(event)
        self.assertEqual(snapshot["venue"], "Testiteatteri")
        self.assertEqual(snapshot["status"], "scheduled")

    def test_other_event_types_cannot_be_used_as_screening_source(self):
        """Elokuvahavaintoja ei saa johtaa esimerkiksi film-festival-tapahtumista."""
        with self.assertRaises(ValueError):
            build_observations_from_screening_state(
                {"event_type_id": "film-festival", "current_events": []},
                {}, {}, NOW,
            )


    def test_invalid_registry_is_rejected_by_schema(self):
        """Puutteellinen rekisteritietue ei pääse yhdistämis- tai tallennusvaiheeseen."""
        invalid = {"schema_version": 1, "films": [{"movie_id": "imdb:tt123"}]}
        with self.assertRaises(MovieObservationError):
            validate_registry(invalid)

    def test_external_identifier_is_stable_and_merges_screenings(self):
        """IMDb-tunniste yhdistää saman elokuvan eri näytöshavainnot."""
        metadata = {
            "primary_title": "Elokuva A", "aliases": ["Movie A"], "release_year": 2024,
            "external_ids": [{"provider": "imdb", "value": "tt1234567"}],
        }
        first = build_movie_observation(screening("screening-1", "Elokuva A"), metadata, [criterion()], NOW)
        second = build_movie_observation(screening("screening-2", "Movie A"), metadata, [criterion()], LATER)
        self.assertEqual(first["movie_id"], "imdb:tt1234567")
        registry = reconcile_movie_observations(empty_registry(), [first, second])
        self.assertEqual(len(registry["films"]), 1)
        film = registry["films"][0]
        self.assertEqual(set(film["screening_refs"]), {"screening-1", "screening-2"})
        self.assertEqual(film["first_seen_at"], NOW)
        self.assertEqual(film["last_seen_at"], LATER)
        self.assertIn("Movie A", film["aliases"])

    def test_title_and_year_are_deterministic_fallback(self):
        """Nimen ja vuoden täsmällinen varatunniste normalisoi välimerkit."""
        first = build_movie_observation(
            screening("screening-a", "The Film!"), {"primary_title": "The Film!", "release_year": 2023},
            [criterion()], NOW,
        )
        second = build_movie_observation(
            screening("screening-b", "the-film"), {"primary_title": "the-film", "release_year": 2023},
            [criterion()], LATER,
        )
        self.assertEqual(normalize_title("The Film!"), normalize_title("the-film"))
        self.assertEqual(first["movie_id"], second["movie_id"])
        self.assertEqual(first["identity_confidence"], "medium")
        self.assertFalse(first["needs_review"])

    def test_missing_year_does_not_merge_uncertain_titles(self):
        """Ilman vuotta tai ulkoista tunnistetta havainnot jäävät erillisiksi ehdokkaiksi."""
        first = build_movie_observation(screening("screening-a"), None, [criterion()], NOW)
        second = build_movie_observation(screening("screening-b"), None, [criterion()], LATER)
        self.assertNotEqual(first["movie_id"], second["movie_id"])
        self.assertTrue(first["needs_review"])
        self.assertEqual(first["identity_confidence"], "low")

    def test_repeated_criterion_match_is_idempotent_and_accumulates_evidence(self):
        """Sama kriteeri säilyy yhtenä osumana ja kerää perustelut sekä lähteet."""
        first = build_movie_observation(
            screening("screening-a"), {"primary_title": "Elokuva A", "release_year": 2022},
            [criterion(matched_at=NOW)], NOW,
        )
        second = build_movie_observation(
            screening("screening-b"), {"primary_title": "Elokuva A", "release_year": 2022},
            [criterion(matched_at=LATER, reason="Toinen vahvistava osuma")], LATER,
        )
        merged = merge_movie_observation(merge_movie_observation(empty_registry(), first), second)
        matches = merged["films"][0]["criterion_matches"]
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["first_matched_at"], NOW)
        self.assertEqual(matches[0]["last_matched_at"], LATER)
        self.assertEqual(len(matches[0]["reasons"]), 2)

    def test_movie_registry_stores_screening_references_not_screening_state(self):
        """Elokuvatasoinen rekisteri ei kopioi teatteria, aikaa tai näytöksen tilaa."""
        observation = build_movie_observation(
            screening("screening-1"), {"primary_title": "Elokuva A", "release_year": 2021},
            [criterion()], NOW,
        )
        self.assertEqual(observation["screening_refs"], ["screening-1"])
        self.assertNotIn("venue", observation)
        self.assertNotIn("starts_at", observation)
        self.assertNotIn("status", observation)

    def test_registry_store_rejects_stale_sha(self):
        """Vanhentunut SHA ei saa ylikirjoittaa uudempaa elokuvarekisteriä."""
        with tempfile.TemporaryDirectory() as folder:
            store = JsonFileMovieRegistryStore(Path(folder) / "movies.json")
            registry, sha = store.load()
            observation = build_movie_observation(
                screening("screening-1"), {"primary_title": "Elokuva A", "release_year": 2020},
                [criterion()], NOW,
            )
            updated = merge_movie_observation(registry, observation)
            store.save(updated, expected_sha=sha)
            with self.assertRaises(MovieRegistryConflictError):
                store.save(registry, expected_sha=sha)


if __name__ == "__main__":
    unittest.main()
