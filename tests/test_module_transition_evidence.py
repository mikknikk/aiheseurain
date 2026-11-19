"""Testaa moduulisiirtymän read-only-todistekeräys ja append-only-loki."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from scripts.github_module_adapters import (
    GitHubApiError, GitHubAdapterConflict, GitHubFile,
)
from scripts.module_transition_evidence import (
    GitHubTransitionEvidenceCollector, GitHubTransitionEvidenceStore,
    TransitionEvidenceError,
)
from scripts.validate_transition_evidence import validate_evidence_tree

ROOT = Path(__file__).resolve().parents[1]


def blob_sha(content):
    return hashlib.sha1(b"blob " + str(len(content)).encode() + b"\0" + content).hexdigest()


class FakeEvidenceClient:
    """Muistissa toimiva GitHub API -testitupla; ei tee verkkopyyntöjä."""

    def __init__(self):
        self.files = {}
        self.branches = {"main"}
        self.writes = 0
        self.fail_after_write = False
        self.pr = {
            "title": "RSS-julkaisu: taylor-swift / swift-run-001",
            "body": "- Moduuli: taylor-swift\n- run_id: swift-run-001",
            "html_url": "https://github.com/mikknikk/aiheseurain/pull/42",
            "state": "open", "merged": False, "merged_at": None,
            "merge_commit_sha": None,
            "head": {"sha": "a" * 40, "ref": "module-publish/taylor-swift/abc"},
            "base": {"ref": "main"},
        }
        self.deployments = [{
            "id": 99, "sha": "b" * 40, "environment": "github-pages",
            "created_at": "2026-11-19T20:00:00Z",
        }]
        self.statuses = [{
            "id": 100, "state": "success", "created_at": "2026-11-19T20:05:00Z",
        }]

    def ensure_branch(self, branch, base="main"):
        if branch not in self.branches:
            self.branches.add(branch)
            for (source_branch, path), value in list(self.files.items()):
                if source_branch == base:
                    self.files[(branch, path)] = value

    def get_file(self, path, branch):
        return self.files.get((branch, path))

    def put_file(self, path, content, branch, *, message, sha=None):
        current = self.get_file(path, branch)
        if sha is None and current is not None:
            if current.content == content:
                return current
            raise GitHubAdapterConflict("Tiedosto on jo olemassa eri sisällöllä.")
        if sha is not None and (current is None or current.sha != sha):
            raise GitHubAdapterConflict("SHA-konflikti.")
        value = GitHubFile(content, blob_sha(content))
        self.files[(branch, path)] = value
        self.writes += 1
        if self.fail_after_write:
            self.fail_after_write = False
            raise GitHubApiError("kuittaus katosi kirjoituksen jälkeen")
        return value

    def request(self, method, path, payload=None):
        if method != "GET" or payload is not None:
            raise AssertionError("Todistekerääjän pitää käyttää vain GET-pyyntöjä.")
        if path == "pulls/42":
            return deepcopy(self.pr)
        if path == f"deployments?environment=github-pages&sha={"b" * 40}&per_page=100":
            return deepcopy(self.deployments)
        if path == "deployments/99/statuses?per_page=100":
            return deepcopy(self.statuses)
        if path.startswith("contents/data/module-transition-evidence/"):
            prefix = path.split("?", 1)[0].removeprefix("contents/")
            rows = []
            for (branch, file_path), value in self.files.items():
                if branch == "module-runtime-state" and file_path.startswith(prefix + "/"):
                    name = file_path.rsplit("/", 1)[-1]
                    rows.append({"name": name, "type": "file"})
            return rows
        raise AssertionError(f"Odottamaton API-pyyntö: {path}")


class TransitionEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.client = FakeEvidenceClient()
        self.collector = GitHubTransitionEvidenceCollector(
            self.client,
            public_fetcher=lambda url: (
                b'<rss version="2.0"><channel><title>Swift</title>'
                b'<item><guid>urn:aiheseurain:taylor-swift:2026-11-19:one</guid></item>'
                b'<item><guid>urn:aiheseurain:taylor-swift:2026-11-19:two</guid></item>'
                b'</channel></rss>'
            ),
            repository_root=ROOT,
        )
        self.store = GitHubTransitionEvidenceStore(self.client, repository_root=ROOT)
        self.now = "2026-11-19T20:30:00Z"

    def test_collectors_are_read_only(self):
        self.collector.collect_pull_request("taylor-swift", "swift-run-001", 42, observed_at=self.now)
        self.collector.collect_pages_deployment(
            "taylor-swift", "swift-run-001", "b" * 40, observed_at=self.now
        )
        self.collector.collect_public_feed("taylor-swift", "swift-run-001", observed_at=self.now)
        self.assertEqual(self.client.writes, 0)
        self.assertEqual(self.client.branches, {"main"})

    def test_pull_request_evidence_is_bound_to_exact_module_and_run(self):
        record = self.collector.collect_pull_request(
            "taylor-swift", "swift-run-001", 42, observed_at=self.now
        )
        self.assertEqual(record["event_type"], "pull_request")
        self.assertEqual(record["evidence"]["pr_number"], 42)
        self.assertFalse(record["evidence"]["merged"])
        self.assertEqual(record["evidence"]["base_ref"], "main")

    def test_pull_request_mismatch_is_rejected(self):
        with self.assertRaises(TransitionEvidenceError):
            self.collector.collect_pull_request(
                "tolkien", "swift-run-001", 42, observed_at=self.now
            )
        self.assertEqual(self.client.writes, 0)

    def test_merged_pull_request_requires_commit_and_timestamp(self):
        self.client.pr.update({
            "state": "closed", "merged": True,
            "merged_at": self.now, "merge_commit_sha": "b" * 40,
        })
        record = self.collector.collect_pull_request(
            "taylor-swift", "swift-run-001", 42, observed_at=self.now
        )
        self.assertTrue(record["evidence"]["merged"])
        self.assertEqual(record["evidence"]["merge_commit_sha"], "b" * 40)

    def test_pages_deployment_is_matched_by_exact_merge_commit(self):
        record = self.collector.collect_pages_deployment(
            "taylor-swift", "swift-run-001", "b" * 40, observed_at=self.now
        )
        self.assertEqual(record["evidence"]["deployment_id"], 99)
        self.assertEqual(record["evidence"]["state"], "success")
        self.assertEqual(record["evidence"]["status_id"], 100)

    def test_pages_deployment_not_found_is_not_misreported_as_success(self):
        self.client.deployments = []
        record = self.collector.collect_pages_deployment(
            "taylor-swift", "swift-run-001", "c" * 40, observed_at=self.now
        )
        self.assertEqual(record["evidence"]["state"], "not_found")
        self.assertIsNone(record["evidence"]["deployment_id"])

    def test_pages_deployment_pending_and_failure_states_are_preserved(self):
        self.client.statuses = [{"id": 101, "state": "in_progress",
                                 "created_at": "2026-11-19T20:04:00Z"}]
        pending = self.collector.collect_pages_deployment(
            "taylor-swift", "swift-run-001", "b" * 40, observed_at=self.now
        )
        self.assertEqual(pending["evidence"]["state"], "in_progress")
        self.client.statuses = [{"id": 102, "state": "failure",
                                 "created_at": "2026-11-19T20:06:00Z"}]
        failed = self.collector.collect_pages_deployment(
            "taylor-swift", "swift-run-001", "b" * 40, observed_at=self.now
        )
        self.assertEqual(failed["evidence"]["state"], "failure")

    def test_public_feed_records_hash_guids_and_count_not_report_content(self):
        record = self.collector.collect_public_feed(
            "taylor-swift", "swift-run-001", observed_at=self.now
        )
        self.assertEqual(record["evidence"]["item_count"], 2)
        self.assertEqual(len(record["evidence"]["guids"]), 2)
        self.assertEqual(len(record["evidence"]["sha256"]), 64)
        self.assertNotIn("report_content", json.dumps(record))

    def test_screening_feed_is_rejected_by_topic_evidence_collector(self):
        with self.assertRaises(TransitionEvidenceError):
            self.collector.collect_public_feed(
                "intialaisten-elokuvien-naytokset", "screen-run-001", observed_at=self.now
            )

    def test_public_feed_rejects_duplicate_guids_and_item_links(self):
        duplicate = (
            b'<rss version="2.0"><channel><item><guid>x</guid></item>'
            b'<item><guid>x</guid></item></channel></rss>'
        )
        collector = GitHubTransitionEvidenceCollector(
            self.client, public_fetcher=lambda url: duplicate, repository_root=ROOT
        )
        with self.assertRaises(TransitionEvidenceError):
            collector.collect_public_feed("taylor-swift", "swift-run-001", observed_at=self.now)
        linked = b'<rss version="2.0"><channel><item><guid>x</guid><link>https://x.test</link></item></channel></rss>'
        collector = GitHubTransitionEvidenceCollector(
            self.client, public_fetcher=lambda url: linked, repository_root=ROOT
        )
        with self.assertRaises(TransitionEvidenceError):
            collector.collect_public_feed("taylor-swift", "swift-run-001", observed_at=self.now)


    def test_publication_manifest_evidence_preserves_phase_history_and_hashes(self):
        manifest = {
            "module_id": "taylor-swift", "run_id": "swift-run-001",
            "idempotency_key": "taylor-swift:swift-run-001",
            "report_sha256": "a" * 64, "artifacts_sha256": "b" * 64,
            "state_sha256": "c" * 64, "artifact_version": "artifact-v1",
            "publication_targets": ["taylor-swift"], 
            "period_start": "2026-11-18T00:00:00Z",
            "period_end": "2026-11-19T00:00:00Z",
            "prepared_at": "2026-11-19T20:00:00Z",
            "phase": "published", "updated_at": "2026-11-19T20:10:00Z",
            "receipt": {"verified": True, "report_guid_refs": ["urn:swift:one"],
                        "published_items": 1},
            "history": [
                {"phase": "prepared", "updated_at": "2026-11-19T20:00:00Z", "receipt": None},
                {"phase": "published", "updated_at": "2026-11-19T20:10:00Z",
                 "receipt": {"verified": True, "report_guid_refs": ["urn:swift:one"],
                             "published_items": 1}},
            ],
        }
        content = json.dumps(manifest).encode("utf-8")
        self.client.files[("module-runtime-state",
                           "data/module-publication-journal/taylor-swift/swift-run-001.json")] = GitHubFile(
            content, blob_sha(content)
        )
        record = self.collector.collect_publication_manifest(
            "taylor-swift", "swift-run-001", observed_at=self.now
        )
        self.assertEqual(record["event_type"], "publication_manifest")
        self.assertEqual(record["evidence"]["phase"], "published")
        self.assertEqual(len(record["evidence"]["history"]), 2)
        self.assertEqual(record["evidence"]["receipt_guid_count"], 1)
        self.assertNotIn("urn:swift:one", record["evidence"]["history"][0].values())

    def test_publication_manifest_rejects_cross_module_ownership(self):
        manifest = {
            "module_id": "tolkien", "run_id": "swift-run-001",
            "idempotency_key": "tolkien:swift-run-001",
            "report_sha256": "a" * 64, "artifacts_sha256": "b" * 64,
            "state_sha256": "c" * 64, "artifact_version": "artifact-v1",
            "publication_targets": ["tolkien"],
            "period_start": "2026-11-18T00:00:00Z",
            "period_end": "2026-11-19T00:00:00Z",
            "prepared_at": "2026-11-19T20:00:00Z",
            "phase": "prepared", "updated_at": "2026-11-19T20:00:00Z",
            "receipt": None,
            "history": [{"phase": "prepared", "updated_at": "2026-11-19T20:00:00Z",
                         "receipt": None}],
        }
        content = json.dumps(manifest).encode("utf-8")
        self.client.files[("module-runtime-state",
                           "data/module-publication-journal/taylor-swift/swift-run-001.json")] = GitHubFile(
            content, blob_sha(content)
        )
        with self.assertRaises(TransitionEvidenceError):
            self.collector.collect_publication_manifest(
                "taylor-swift", "swift-run-001", observed_at=self.now
            )

    def test_checkpoint_evidence_checks_current_module_and_run(self):
        state = json.loads((ROOT / "data/module-state/taylor-swift.json").read_text(encoding="utf-8"))
        state["checkpoint"]["last_successful_run"].update({
            "run_id": "swift-run-001", "checked_at": self.now,
        })
        content = json.dumps(state).encode("utf-8")
        self.client.files[("module-runtime-state", "data/module-state/taylor-swift.json")] = GitHubFile(
            content, blob_sha(content)
        )
        record = self.collector.collect_checkpoint(
            "taylor-swift", "swift-run-001", before_blob_sha="c" * 40,
            before_run_id="swift-run-000", before_checked_at="2026-11-18T20:30:00Z",
            manifest_phase="checkpoint_updated", observed_at=self.now,
        )
        self.assertEqual(record["evidence"]["after_run_id"], "swift-run-001")
        self.assertEqual(record["evidence"]["before_blob_sha"], "c" * 40)

    def test_checkpoint_refuses_wrong_current_run(self):
        with self.assertRaises(TransitionEvidenceError):
            self.collector.collect_checkpoint(
                "taylor-swift", "swift-run-001", before_blob_sha="c" * 40,
                before_run_id=None, before_checked_at=None,
                manifest_phase="checkpoint_updated", observed_at=self.now,
            )

    def test_legacy_period_observation_requires_proof_and_reason(self):
        with self.assertRaises(TransitionEvidenceError):
            self.collector.legacy_period_observation(
                "taylor-swift", "swift-run-001", status="absent",
                source_url="https://example.org/archive.xml",
                period_start="2026-11-18T00:00:00Z", period_end="2026-11-19T00:00:00Z",
                reason=None, matching_guids=[], observed_at=self.now,
            )
        record = self.collector.legacy_period_observation(
            "taylor-swift", "swift-run-001", status="present",
            source_url="https://example.org/archive.xml",
            period_start="2026-11-18T00:00:00Z", period_end="2026-11-19T00:00:00Z",
            reason="Vanhan polun RSS:stä löytyi täsmäävä jakso.",
            matching_guids=["urn:legacy:one"], observed_at=self.now,
        )
        self.assertEqual(record["evidence"]["status"], "present")

    def test_recovery_decision_is_recomputed_and_recorded_without_action(self):
        record = self.collector.recovery_decision(
            "taylor-swift", "swift-run-001", manifest={
                "module_id": "taylor-swift", "run_id": "swift-run-001", "phase": "prepared",
            },
            publication_status="closed_unmerged", deployment_status="not_started",
            public_feed_matches=False, checkpoint_status="not_advanced",
            legacy_period_status="absent", legacy_fallback_authorized=False,
            observed_at=self.now,
        )
        self.assertEqual(record["evidence"]["action"], "legacy_fallback_requires_approval")
        self.assertEqual(self.client.writes, 0)

    def test_legacy_approval_is_only_recorded_not_granted(self):
        record = self.collector.legacy_fallback_approval(
            "taylor-swift", "swift-run-001", approval_id="approval-42",
            approved_at=self.now, reason="Erillinen hyväksyntä saatu.",
            scope="Yksi moduuli ja yksi seurantajakso.", observed_at=self.now,
        )
        self.assertEqual(record["evidence"]["approval_id"], "approval-42")
        self.assertEqual(self.client.writes, 0)

    def test_evidence_store_is_idempotent_and_immutable(self):
        record = self.collector.collect_pull_request(
            "taylor-swift", "swift-run-001", 42, observed_at=self.now
        )
        path = self.store.record(record)
        self.assertEqual(self.store.record(record), path)
        stored = self.client.get_file(path, "module-runtime-state")
        self.assertEqual(json.loads(stored.content), record)
        self.assertEqual(self.client.writes, 1)
        self.assertEqual(self.client.branches, {"main", "module-runtime-state"})

    def test_evidence_store_resolves_lost_write_acknowledgement(self):
        record = self.collector.collect_pull_request(
            "taylor-swift", "swift-run-001", 42, observed_at=self.now
        )
        self.client.fail_after_write = True
        path = self.store.record(record)
        self.assertIsNotNone(self.client.get_file(path, "module-runtime-state"))

    def test_evidence_store_rejects_conflicting_existing_path(self):
        record = self.collector.collect_pull_request(
            "taylor-swift", "swift-run-001", 42, observed_at=self.now
        )
        path = self.store._path(record)
        self.client.ensure_branch("module-runtime-state")
        self.client.files[("module-runtime-state", path)] = GitHubFile(b"{}", "wrong-sha")
        with self.assertRaises(GitHubAdapterConflict):
            self.store.record(record)

    def test_load_run_reconstructs_events_in_time_order(self):
        first = self.collector.collect_pull_request(
            "taylor-swift", "swift-run-001", 42, observed_at="2026-11-19T20:00:00Z"
        )
        second = self.collector.collect_public_feed(
            "taylor-swift", "swift-run-001", observed_at="2026-11-19T20:10:00Z"
        )
        self.store.record(second)
        self.store.record(first)
        writes_before = self.client.writes
        loaded = self.store.load_run("taylor-swift", "swift-run-001")
        self.assertEqual([item["event_type"] for item in loaded], ["pull_request", "public_feed"])
        self.assertEqual(self.client.writes, writes_before)

    def test_store_rejects_tampered_event_id_and_sensitive_content(self):
        record = self.collector.collect_pull_request(
            "taylor-swift", "swift-run-001", 42, observed_at=self.now
        )
        tampered = deepcopy(record)
        tampered["evidence"]["pr_number"] = 43
        with self.assertRaises(TransitionEvidenceError):
            self.store.record(tampered)
        sensitive = deepcopy(record)
        sensitive["evidence"]["report_content"] = "koko raportti"
        with self.assertRaises(TransitionEvidenceError):
            self.store.record(sensitive)


    def test_repository_validator_checks_schema_and_exact_record_path(self):
        record = self.collector.collect_pull_request(
            "taylor-swift", "swift-run-001", 42, observed_at=self.now
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "schemas").mkdir()
            (root / "schemas/module-transition-evidence.schema.json").write_bytes(
                (ROOT / "schemas/module-transition-evidence.schema.json").read_bytes()
            )
            target = root / "data/module-transition-evidence/taylor-swift/swift-run-001"
            target.mkdir(parents=True)
            event = target / f"pull_request-{record['event_id']}.json"
            event.write_text(json.dumps(record), encoding="utf-8")
            self.assertEqual(validate_evidence_tree(root), 1)
            event.rename(target / "wrong-name.json")
            with self.assertRaises(TransitionEvidenceError):
                validate_evidence_tree(root)

    def test_legacy_approval_cannot_be_future_dated(self):
        with self.assertRaises(TransitionEvidenceError):
            self.collector.legacy_fallback_approval(
                "taylor-swift", "swift-run-001", approval_id="approval-future",
                approved_at="2026-11-20T00:00:00Z",
                reason="Testi.", scope="Yksi ajo.",
                observed_at=self.now,
            )

    def test_store_rejects_cross_module_or_cross_run_path_content(self):
        record = self.collector.collect_pull_request(
            "taylor-swift", "swift-run-001", 42, observed_at=self.now
        )
        self.store.record(record)
        loaded = self.store.load_run("tolkien", "swift-run-001")
        self.assertEqual(loaded, [])
        loaded = self.store.load_run("taylor-swift", "another-run-001")
        self.assertEqual(loaded, [])


if __name__ == "__main__":
    unittest.main()
