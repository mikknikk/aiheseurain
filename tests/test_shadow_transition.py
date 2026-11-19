"""Varjosiirtymän orkestroinnin päästä päähän -regressiotestit."""
from pathlib import Path
import json
import unittest

from scripts.shadow_transition import (
    ShadowTransitionError, ShadowTransitionOrchestrator, ShadowTransitionRequest,
)
from scripts.module_transition_evidence import (
    GitHubTransitionEvidenceCollector, GitHubTransitionEvidenceStore,
)
from test_module_transition_evidence import FakeEvidenceClient, ROOT
from scripts.github_module_adapters import GitHubFile


class ShadowTransitionOrchestratorTests(unittest.TestCase):
    def setUp(self):
        self.client = FakeEvidenceClient()
        # Runtime-haaran synteettinen checkpoint on lähtötilan todellinen
        # read-only-lähde; sen blob-SHA vastaa checkpoint-testien before_sha-arvoa.
        baseline_state = {
            "module_id": "taylor-swift",
            "checkpoint": {"last_successful_run": {
                "run_id": "old-run-001", "checked_at": "2026-11-19T21:00:00Z",
            }},
        }
        baseline_content = json.dumps(baseline_state).encode("utf-8")
        self.client.files[("module-runtime-state", "data/module-state/taylor-swift.json")] = GitHubFile(
            baseline_content, "e" * 40,
        )
        self.collector = GitHubTransitionEvidenceCollector(
            self.client,
            public_fetcher=lambda url: (
                b'<rss version="2.0"><channel><title>Swift</title>'
                b'<item><guid>urn:aiheseurain:taylor-swift:2026-11-19:one</guid></item>'
                b'</channel></rss>'
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
        self.client.pr["title"] = "RSS-julkaisu: taylor-swift / swift-run-239"
        self.client.pr["body"] = "- Moduuli: taylor-swift\\n- run_id: swift-run-239"
        self.now = "2026-11-19T21:00:00Z"
        self.expected_guid = "urn:aiheseurain:taylor-swift:2026-11-19:one"

    def _base_collectors(self):
        return {
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

    def _record(self, event_type, source, evidence):
        return self.collector._make_record(
            self.request.module_id, self.request.run_id, event_type,
            self.now, source, evidence,
        )

    def _manifest_record(self, phase="published"):
        return self._record("publication_manifest", "github_contents_api", {
            "manifest_blob_sha": "d" * 40, "phase": phase,
            "artifact_version": "artifact-v1", "report_sha256": "a" * 64,
            "artifacts_sha256": "b" * 64, "state_sha256": "c" * 64,
            "publication_targets": ["taylor-swift"],
            "period_start": self.request.period_start,
            "period_end": self.request.period_end,
            "prepared_at": self.now, "updated_at": self.now,
            "history": [{"phase": phase, "updated_at": self.now}],
            "receipt_present": phase != "prepared", "receipt_guid_count": 1,
            "receipt_published_items": 1 if phase != "prepared" else None,
        })

    def _checkpoint_record(self, *, before_sha="e" * 40, after_sha="e" * 40,
                           before_run="old-run-001", after_run="old-run-001",
                           phase="artifacts_persisted"):
        return self._record("checkpoint", "github_contents_api", {
            "before_blob_sha": before_sha, "after_blob_sha": after_sha,
            "before_run_id": before_run, "after_run_id": after_run,
            "before_checked_at": self.now, "after_checked_at": self.now,
            "manifest_phase": phase,
        })

    def _pages_record(self, state):
        return self._record("pages_deployment", "github_deployments_api", {
            "deployment_id": 99, "status_id": 100, "state": state,
            "environment": "github-pages", "commit_sha": "b" * 40,
            "created_at": self.now, "updated_at": self.now,
        })

    def _feed_record(self, guids=None):
        guids = [self.expected_guid] if guids is None else guids
        return self._record("public_feed", "public_pages_http_no_cache", {
            "url": "https://mikknikk.github.io/aiheseurain/taylor-swift.xml",
            "sha256": "f" * 64, "item_count": len(guids), "guids": guids,
        })

    def test_shadow_run_collects_decides_persists_and_reconstructs_one_run(self):
        result = self.orchestrator.run(
            self.request, collect=self._base_collectors(), observed_at=self.now,
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
            self.request.module_id, self.request.run_id, 42, observed_at=self.now
        )
        legacy = self._base_collectors()["legacy_period"]()
        wrong["run_id"] = "another-run-001"
        legacy["run_id"] = "another-run-001"
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
        collectors = self._base_collectors()
        collectors["legacy_period"] = fail
        with self.assertRaises(RuntimeError):
            self.orchestrator.run(self.request, collect=collectors, observed_at=self.now)
        self.assertEqual(self.client.writes, 0)

    def test_merged_pr_waits_for_pages_then_resumes_same_publication(self):
        self.client.pr.update({
            "state": "closed", "merged": True, "merged_at": self.now,
            "merge_commit_sha": "b" * 40,
        })
        base = self._base_collectors()
        base.update({
            "pages_deployment": lambda: self._pages_record("pending"),
            "public_feed": lambda: self._feed_record(),
            "publication_manifest": lambda: self._manifest_record("published"),
            "checkpoint": lambda: self._checkpoint_record(),
        })
        pending = self.orchestrator.run(
            self.request, collect=base, observed_at=self.now,
            expected_guids=[self.expected_guid],
        )
        self.assertEqual(pending["recovery_action"], "wait_for_pages")
        # Sama harjoitus samalla sisällöllä on idempotentti.
        retry = self.orchestrator.run(
            self.request, collect=base, observed_at=self.now,
            expected_guids=[self.expected_guid],
        )
        self.assertEqual(retry["event_ids"], pending["event_ids"])
        self.client.statuses = [{"id": 103, "state": "success", "created_at": self.now}]
        base["pages_deployment"] = lambda: self._pages_record("success")
        completed = self.orchestrator.run(
            self.request, collect=base, observed_at=self.now,
            expected_guids=[self.expected_guid],
        )
        self.assertEqual(completed["recovery_action"], "resume_artifact_persistence")

    def test_failed_pages_deployment_requests_retry_not_new_publication(self):
        self.client.pr.update({
            "state": "closed", "merged": True, "merged_at": self.now,
            "merge_commit_sha": "b" * 40,
        })
        base = self._base_collectors()
        base.update({
            "pages_deployment": lambda: self._pages_record("failure"),
            "public_feed": lambda: self._record(
                "public_feed", "public_pages_http_no_cache", {
                    "url": "https://mikknikk.github.io/aiheseurain/taylor-swift.xml",
                    "sha256": "f" * 64, "item_count": 0, "guids": [],
                }
            ),
            "publication_manifest": lambda: self._manifest_record("published"),
            "checkpoint": lambda: self._checkpoint_record(),
        })
        result = self.orchestrator.run(
            self.request, collect=base, observed_at=self.now,
            expected_guids=[self.expected_guid],
        )
        self.assertEqual(result["recovery_action"], "retry_pages_publication")

    def test_public_feed_guid_mismatch_and_manifest_period_mismatch_fail_safe(self):
        self.client.pr.update({
            "state": "closed", "merged": True, "merged_at": self.now,
            "merge_commit_sha": "b" * 40,
        })
        base = self._base_collectors()
        base.update({
            "pages_deployment": lambda: self._pages_record("success"),
            "public_feed": lambda: self._feed_record(["urn:wrong-guid"]),
            "publication_manifest": lambda: self._manifest_record("published"),
            "checkpoint": lambda: self._checkpoint_record(),
        })
        result = self.orchestrator.run(
            self.request, collect=base, observed_at=self.now,
            expected_guids=[self.expected_guid],
        )
        self.assertEqual(result["recovery_action"], "reconcile_publication")

        wrong_evidence = dict(self._manifest_record("published")["evidence"])
        wrong_evidence["period_start"] = "2026-11-17T00:00:00Z"
        wrong_manifest = self._record(
            "publication_manifest", "github_contents_api", wrong_evidence
        )
        base["publication_manifest"] = lambda: wrong_manifest
        with self.assertRaises(ShadowTransitionError):
            self.orchestrator.run(
                self.request, collect=base, observed_at=self.now,
                expected_guids=[self.expected_guid],
            )

    def test_checkpoint_callback_cannot_forge_the_baseline(self):
        base = self._base_collectors()
        base["checkpoint"] = lambda: self._checkpoint_record(before_sha="f" * 40)
        with self.assertRaises(ShadowTransitionError):
            self.orchestrator.run(self.request, collect=base, observed_at=self.now)
        self.assertEqual(self.client.writes, 0)

    def test_checkpoint_changed_by_another_run_forces_manual_review(self):
        self.client.pr.update({
            "state": "closed", "merged": True, "merged_at": self.now,
            "merge_commit_sha": "b" * 40,
        })
        base = self._base_collectors()
        base.update({
            "pages_deployment": lambda: self._pages_record("success"),
            "public_feed": lambda: self._feed_record(),
            "publication_manifest": lambda: self._manifest_record("artifacts_persisted"),
            "checkpoint": lambda: self._checkpoint_record(
                before_sha="e" * 40, after_sha="1" * 40,
                before_run="old-run-001", after_run="competing-run-002",
            ),
        })
        result = self.orchestrator.run(
            self.request, collect=base, observed_at=self.now,
            expected_guids=[self.expected_guid],
        )
        self.assertEqual(result["recovery_action"], "manual_review")

    def test_closed_unmerged_pr_requires_explicit_legacy_approval(self):
        self.client.pr.update({"state": "closed", "merged": False})
        base = self._base_collectors()
        base.update({
            "public_feed": lambda: self._feed_record(),
            "publication_manifest": lambda: self._manifest_record("prepared"),
            "checkpoint": lambda: self._checkpoint_record(),
        })
        # Tyhjä julkinen GUID-lista todistaa, ettei ehdokas ole julkaistu.
        base["public_feed"] = lambda: self._record(
            "public_feed", "public_pages_http_no_cache", {
                "url": "https://mikknikk.github.io/aiheseurain/taylor-swift.xml",
                "sha256": "f" * 64, "item_count": 0, "guids": [],
            }
        )
        result = self.orchestrator.run(
            self.request, collect=base, observed_at=self.now,
            expected_guids=[self.expected_guid],
        )
        self.assertEqual(result["recovery_action"], "legacy_fallback_requires_approval")
        base["legacy_approval"] = lambda: self.collector.legacy_fallback_approval(
            self.request.module_id, self.request.run_id,
            approval_id="approval-239", approved_at=self.now,
            reason="Erikseen hyväksytty synteettinen palautusharjoitus.",
            scope="Vain tämä moduuli ja seurantajakso.", observed_at=self.now,
        )
        approved = self.orchestrator.run(
            self.request, collect=base, observed_at=self.now,
            expected_guids=[self.expected_guid],
        )
        self.assertEqual(approved["recovery_action"], "return_to_legacy_path")

    def test_already_published_legacy_period_blocks_fallback(self):
        self.client.pr.update({"state": "closed", "merged": False})
        base = self._base_collectors()
        base["legacy_period"] = lambda: self.collector.legacy_period_observation(
            self.request.module_id, self.request.run_id, status="present",
            source_url="https://example.org/archive.xml",
            period_start=self.request.period_start, period_end=self.request.period_end,
            reason="Synteettinen aiempi julkaisu.", matching_guids=["urn:old:guid"],
            observed_at=self.now,
        )
        base["publication_manifest"] = lambda: self._manifest_record("prepared")
        base["checkpoint"] = lambda: self._checkpoint_record()
        result = self.orchestrator.run(
            self.request, collect=base, observed_at=self.now,
        )
        self.assertEqual(result["recovery_action"], "legacy_period_already_published")

    def test_shadow_writes_only_audit_events_and_leaves_runtime_state_untouched(self):
        before_files = dict(self.client.files)
        before_branches = set(self.client.branches)
        result = self.orchestrator.run(
            self.request, collect=self._base_collectors(), observed_at=self.now,
        )
        audit_files = {
            key for key in self.client.files
            if key[1].startswith("data/module-transition-evidence/")
        }
        self.assertEqual(len(audit_files), result["event_count"])
        self.assertEqual(
            {key: value for key, value in self.client.files.items() if key not in audit_files},
            before_files,
        )
        # Store saa luoda vain auditointivaraston runtime-haaran.
        self.assertEqual(self.client.branches, before_branches | {"module-runtime-state"})
        self.assertEqual(self.client.writes, result["event_count"])


if __name__ == "__main__":
    unittest.main()
