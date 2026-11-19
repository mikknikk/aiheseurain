"""Varjosiirtymän orkestroinnin päästä päähän -regressiotestit."""
from pathlib import Path
import unittest

from scripts.shadow_transition import (
    ShadowTransitionError, ShadowTransitionOrchestrator, ShadowTransitionRequest,
)
from scripts.module_transition_evidence import (
    GitHubTransitionEvidenceCollector, GitHubTransitionEvidenceStore,
)
from test_module_transition_evidence import FakeEvidenceClient, ROOT


class ShadowTransitionOrchestratorTests(unittest.TestCase):
    def setUp(self):
        self.client = FakeEvidenceClient()
        self.collector = GitHubTransitionEvidenceCollector(
            self.client,
            public_fetcher=lambda url: (
                b'<rss version="2.0"><channel><title>Swift</title>'
                b'<item><guid>urn:swift:one</guid></item></channel></rss>'
            ),
            repository_root=ROOT,
        )
        self.store = GitHubTransitionEvidenceStore(self.client, repository_root=ROOT)
        self.orchestrator = ShadowTransitionOrchestrator(self.collector, self.store)
        self.request = ShadowTransitionRequest(
            module_id="taylor-swift", run_id="swift-run-239",
            module_version="1.0.0",
            period_start="2026-11-18T00:00:00Z",
            period_end="2026-11-19T00:00:00Z",
        )
        self.now = "2026-11-19T21:00:00Z"

    def _collectors(self):
        return {
            "pull_request": lambda: self.collector.collect_pull_request(
                "taylor-swift", "swift-run-001", 42, observed_at=self.now
            ),
            "legacy_period": lambda: self.collector.legacy_period_observation(
                "taylor-swift", "swift-run-001", status="absent",
                source_url="https://example.org/archive.xml",
                period_start="2026-11-18T00:00:00Z",
                period_end="2026-11-19T00:00:00Z",
                reason="Tarkistettu synteettinen vanhan polun arkisto.",
                matching_guids=[], observed_at=self.now,
            ),
        }

    def test_shadow_run_collects_decides_persists_and_reconstructs_one_run(self):
        # Keräyskutsut käyttävät täsmälleen pyynnön moduuli- ja ajotunnisteita.
        collectors = {
            "pull_request": lambda: self.collector.collect_pull_request(
                self.request.module_id, self.request.run_id, 42, observed_at=self.now
            ),
            "legacy_period": lambda: self.collector.legacy_period_observation(
                self.request.module_id, self.request.run_id, status="absent",
                source_url="https://example.org/archive.xml",
                period_start=self.request.period_start, period_end=self.request.period_end,
                reason="Tarkistettu synteettinen vanhan polun arkisto.",
                matching_guids=[], observed_at=self.now,
            ),
        }
        result = self.orchestrator.run(
            self.request, collect=collectors, observed_at=self.now,
        )
        self.assertEqual(result["mode"], "shadow")
        self.assertEqual(result["recovery_action"], "inspect_external_state")
        self.assertEqual(result["event_count"], 3)
        self.assertEqual(self.client.writes, 3)
        reconstructed = self.store.load_run(self.request.module_id, self.request.run_id)
        self.assertEqual({item["event_type"] for item in reconstructed},
                         {"pull_request", "legacy_period", "recovery_decision"})

    def test_refuses_production_mode_and_screening_process(self):
        with self.assertRaises(ShadowTransitionError):
            ShadowTransitionRequest(
                "taylor-swift", "swift-run-239", "1.0.0",
                self.request.period_start, self.request.period_end, mode="production",
            ).validate(ROOT)
        with self.assertRaises(ShadowTransitionError):
            ShadowTransitionRequest(
                "intialaisten-elokuvien-naytokset", "screen-run-239", "1.0.0",
                self.request.period_start, self.request.period_end,
            ).validate(ROOT)

    def test_rejects_cross_module_or_cross_run_evidence_before_writing(self):
        wrong = self.collector.collect_pull_request(
            "taylor-swift", "swift-run-001", 42, observed_at=self.now
        )
        legacy = self.collector.legacy_period_observation(
            "taylor-swift", "swift-run-001", status="absent",
            source_url="https://example.org/archive.xml",
            period_start=self.request.period_start, period_end=self.request.period_end,
            reason="Tarkistettu synteettinen vanhan polun arkisto.",
            matching_guids=[], observed_at=self.now,
        )
        with self.assertRaises(ShadowTransitionError):
            self.orchestrator.run(
                self.request,
                collect={"pull_request": lambda: wrong, "legacy_period": lambda: legacy},
                observed_at=self.now,
            )
        self.assertEqual(self.client.writes, 0)

    def test_collection_failure_does_not_write_partial_audit_log(self):
        def fail():
            raise RuntimeError("simuloitu API-epäselvyys")
        collectors = self._collectors()
        collectors["legacy_period"] = fail
        with self.assertRaises(RuntimeError):
            self.orchestrator.run(self.request, collect=collectors, observed_at=self.now)
        self.assertEqual(self.client.writes, 0)


if __name__ == "__main__":
    unittest.main()
