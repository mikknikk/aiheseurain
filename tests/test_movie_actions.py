"""Testaa kriteerikohtaiset jatkotoimet, Discord-sovitin ja outbox."""
from copy import deepcopy
from pathlib import Path
import json
import tempfile
import unittest

from scripts.movie_observations import JsonFileMovieRegistryStore
from scripts.movie_actions import (
    ActionOutboxConflictError, DiscordWebhookAdapter, JsonFileActionOutboxStore,
    RetryableDeliveryError, dispatch_pending_actions, empty_outbox,
    enqueue_movie_actions, resolve_uncertain_delivery,
)

ROOT = Path(__file__).resolve().parents[1]
NOW = "2026-11-18T08:00:00+02:00"
RETRY = "2026-11-18T08:01:00+02:00"
WEBHOOK = "https://discord.com/api/webhooks/test-secret/test-token"
SCREENING = {
    "screening_id": "screening-1", "title": "Testielokuva", "venue": "Testiteatteri",
    "city": "Helsinki", "starts_at": NOW, "status": "scheduled",
    "source_urls": ["https://example.test/show"],
}


def movie():
    """Luo kahteen kriteeriin osuneen elokuvahavainnon."""
    return {
        "movie_id": "imdb:tt1234567", "primary_title": "Testielokuva", "release_year": 2024,
        "first_seen_at": NOW, "last_seen_at": NOW, "screening_refs": ["screening-1"],
        "aliases": [], "external_ids": [{"provider": "imdb", "value": "tt1234567"}],
        "identity_confidence": "high", "needs_review": False,
        "sources": [{"publisher": "Teatteri", "url": "https://example.test/show",
                     "checked_at": NOW, "claim_level": "official"}],
        "criterion_matches": [
            {"match_id": "match-a", "criterion_id": "test-criterion-a", "criterion_version": "1.0.0",
             "first_matched_at": NOW, "last_matched_at": NOW, "reasons": ["testi"],
             "source_urls": ["https://example.test/criterion-a"]},
            {"match_id": "match-b", "criterion_id": "test-criterion-b", "criterion_version": "1.0.0",
             "first_matched_at": NOW, "last_matched_at": NOW, "reasons": ["testi"],
             "source_urls": ["https://example.test/criterion-b"]},
        ],
    }


def config():
    """Lataa fixture-konfiguraatio, jossa on vain testikriteerien toiminnot."""
    return json.loads((ROOT / "tests/fixtures/movie-action-config.json").read_text(encoding="utf-8"))


class MovieActionTests(unittest.TestCase):
    def test_only_enabled_matching_criteria_enqueue_actions(self):
        """Vain osuneelle ja käytössä olevalle kriteerille määritetty toiminto jonoutuu."""
        settings = config()
        settings["actions"].append({
            "criterion_id": "not-matched", "action_id": "ignored", "version": "1.0.0",
            "type": "discord_webhook", "enabled": True,
        })
        outbox = enqueue_movie_actions(movie(), settings, empty_outbox(), NOW, screening_observations=[SCREENING])
        self.assertEqual(len(outbox["actions"]), 2)
        self.assertEqual({item["criterion_id"] for item in outbox["actions"]},
                         {"test-criterion-a", "test-criterion-b"})
        for action in outbox["actions"]:
            self.assertEqual(
                action["payload"]["source_urls"],
                [f"https://example.test/criterion-{action['criterion_id'][-1]}"],
            )

    def test_duplicate_enqueue_is_idempotent_but_different_criteria_remain_distinct(self):
        """Sama toiminto ei monistu, mutta kahden eri kriteerin toiminnot säilyvät."""
        first = enqueue_movie_actions(movie(), config(), empty_outbox(), NOW, screening_observations=[SCREENING])
        second = enqueue_movie_actions(movie(), config(), first, NOW, screening_observations=[SCREENING])
        self.assertEqual(len(first["actions"]), 2)
        self.assertEqual(len(second["actions"]), 2)
        self.assertEqual(len({item["idempotency_key"] for item in second["actions"]}), 2)

    def test_discord_adapter_uses_injected_transport_and_redacts_secret(self):
        """Testikuljetin saa webhookin, mutta adapterin debug-esitys ei paljasta salaisuutta."""
        calls = []
        adapter = DiscordWebhookAdapter(
            WEBHOOK, lambda url, payload, key: calls.append((url, payload, key))
        )
        outbox = enqueue_movie_actions(movie(), config(), empty_outbox(), NOW, screening_observations=[SCREENING])
        updated = dispatch_pending_actions(
            outbox, {"discord_webhook": adapter}, NOW,
        )
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[0][1]["screening_observations"][0]["venue"], "Testiteatteri")
        self.assertTrue(all(item["status"] == "sent" for item in updated["actions"]))
        self.assertNotIn("test-secret", repr(adapter))
        self.assertNotIn("test-token", json.dumps(updated))

    def test_failed_delivery_is_retryable_and_does_not_store_secret(self):
        """Verkkovirhe säilyy outboxissa uusintaa varten ilman salaisuuden kirjaamista."""
        outbox = enqueue_movie_actions(movie(), config(), empty_outbox(), NOW, screening_observations=[SCREENING])
        class FailingTransport:
            def send(self, payload, idempotency_key):
                raise RetryableDeliveryError("Webhook rejected")
        first = dispatch_pending_actions(
            outbox, {"discord_webhook": FailingTransport()}, NOW, max_attempts=2,
        )
        self.assertTrue(all(item["status"] == "pending" for item in first["actions"]))
        self.assertTrue(all(item["attempts"] == 1 for item in first["actions"]))
        self.assertTrue(all(item["last_error_code"] == "RetryableDeliveryError" for item in first["actions"]))
        self.assertTrue(all(item["next_attempt_at"] is not None for item in first["actions"]))
        too_early = dispatch_pending_actions(
            first, {"discord_webhook": FailingTransport()}, NOW, max_attempts=2,
        )
        self.assertEqual(too_early, first)
        second = dispatch_pending_actions(
            first, {"discord_webhook": FailingTransport()}, RETRY, max_attempts=2,
        )
        self.assertTrue(all(item["status"] == "failed" for item in second["actions"]))
        serialized = json.dumps(second)
        self.assertNotIn("Webhook rejected", serialized)
        self.assertNotIn("test-secret", serialized)


    def test_rate_limit_retry_after_is_respected(self):
        """Rate limit -kuljettimen ilmoittamaa retry-after-viivettä noudatetaan."""
        outbox = enqueue_movie_actions(movie(), config(), empty_outbox(), NOW, screening_observations=[SCREENING])
        class RateLimited:
            def send(self, payload, idempotency_key):
                raise RetryableDeliveryError("rate limited", retry_after_seconds=120)
        delayed = dispatch_pending_actions(
            outbox, {"discord_webhook": RateLimited()}, NOW, max_attempts=3,
        )
        self.assertTrue(all(item["next_attempt_at"] == "2026-11-18T08:02:00+02:00"
                            for item in delayed["actions"]))
        too_early = dispatch_pending_actions(
            delayed, {"discord_webhook": RateLimited()}, RETRY, max_attempts=3,
        )
        self.assertEqual(too_early, delayed)


    def test_ambiguous_delivery_requires_manual_resolution(self):
        """Epäselvää aikakatkaisua ei uusita automaattisesti kaksoisviestin riskin vuoksi."""
        outbox = enqueue_movie_actions(movie(), config(), empty_outbox(), NOW, screening_observations=[SCREENING])
        class TimedOut:
            def send(self, payload, idempotency_key):
                raise TimeoutError("response lost")
        uncertain = dispatch_pending_actions(
            outbox, {"discord_webhook": TimedOut()}, NOW,
        )
        self.assertTrue(all(item["status"] == "uncertain" for item in uncertain["actions"]))
        retried = dispatch_pending_actions(
            uncertain, {"discord_webhook": TimedOut()}, RETRY,
        )
        self.assertEqual(retried, uncertain)
        resolved = resolve_uncertain_delivery(
            uncertain, uncertain["actions"][0]["event_id"],
            delivered=False, resolved_at=RETRY,
        )
        self.assertEqual(resolved["actions"][0]["status"], "pending")
        self.assertEqual(resolved["actions"][0]["next_attempt_at"], RETRY)


    def test_partial_registry_commit_can_recreate_outbox_without_losing_action(self):
        """Jos rekisteri tallentuu mutta outbox ei, seuraava ajo voi jonottaa toiminnon uudelleen."""
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            registry_store = JsonFileMovieRegistryStore(root / "movie-registry.json")
            registry, registry_sha = registry_store.load()
            registry["films"].append(movie())
            registry_store.save(registry, expected_sha=registry_sha)

            # Simuloi katkoa rekisterin ja outboxin tallennuksen välissä.
            outbox_store = JsonFileActionOutboxStore(root / "movie-outbox.json")
            empty, outbox_sha = outbox_store.load()
            self.assertEqual(empty["actions"], [])

            recovered_registry, _ = registry_store.load()
            recovered_movie = recovered_registry["films"][0]
            queued = enqueue_movie_actions(
                recovered_movie, config(), empty, NOW,
                screening_observations=[SCREENING],
            )
            outbox_store.save(queued, expected_sha=outbox_sha)

            # Uusinta lukee saman elokuvan ja outboxin; idempotenssi estää kaksoisjonotuksen.
            persisted, persisted_sha = outbox_store.load()
            retried = enqueue_movie_actions(
                recovered_movie, config(), persisted, RETRY,
                screening_observations=[SCREENING],
            )
            self.assertEqual(len(retried["actions"]), 2)
            self.assertEqual(len({item["idempotency_key"] for item in retried["actions"]}), 2)

    def test_outbox_store_rejects_stale_sha(self):
        """Toimitusjonon vanha SHA ei saa ylikirjoittaa uudempaa jonoa."""
        with tempfile.TemporaryDirectory() as folder:
            store = JsonFileActionOutboxStore(Path(folder) / "outbox.json")
            outbox, sha = store.load()
            updated = enqueue_movie_actions(movie(), config(), outbox, NOW, screening_observations=[SCREENING])
            store.save(updated, expected_sha=sha)
            with self.assertRaises(ActionOutboxConflictError):
                store.save(outbox, expected_sha=sha)

    def test_production_action_config_is_empty(self):
        """Tuotantoon ei ole lisätty kriteeriä, Discord-toimintoa tai webhook-salaisuutta."""
        production = json.loads((ROOT / "data/movie-action-config.json").read_text(encoding="utf-8"))
        self.assertEqual(production["actions"], [])


if __name__ == "__main__":
    unittest.main()
