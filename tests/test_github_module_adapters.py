"""Testaa GitHub-pohjaiset moduulien pysyvät tallennus- ja julkaisusovittimet."""
from copy import deepcopy
from dataclasses import replace
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.module_orchestrator import ModuleRunResult, PublicationReceipt
from scripts.module_state import StateConflictError
from scripts.publication_journal import PublicationJournalConflict
from scripts.github_module_adapters import (
    GitHubFile, GitHubModuleStateStore, GitHubArtifactStore,
    GitHubPublicationJournal, GitHubPagesRssPublisher, GitHubRunRecorder,
    GitHubHandoffStore, GitHubRotationStateStore,
    GitHubAdapterConflict, GitHubAdapterError, GitHubApiClient, GitHubApiError, PublicationCandidate,
)

ROOT = Path(__file__).resolve().parents[1]


def blob_sha(content):
    """Laske Gitin blob-SHA testivarastolle."""
    return hashlib.sha1(b"blob " + str(len(content)).encode() + b"\0" + content).hexdigest()


class FakeGitHubClient:
    """Muistissa toimiva GitHub-sisältö- ja PR-rajapinnan testitupla."""

    def __init__(self):
        self.files = {}
        self.branches = {"main"}
        self.pull_requests = {}
        self.fail_after_write_path = None

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
            raise GitHubAdapterConflict("Tiedosto on jo olemassa.")
        if sha is not None and (current is None or current.sha != sha):
            raise GitHubAdapterConflict("SHA-konflikti.")
        result = GitHubFile(content, blob_sha(content))
        self.files[(branch, path)] = result
        if self.fail_after_write_path == path:
            self.fail_after_write_path = None
            raise GitHubApiError("simulated lost response after successful write")
        return result

    def find_pull_request(self, branch, base="main"):
        return self.pull_requests.get(branch)

    def create_pull_request(self, title, body, branch, base="main"):
        result = {"number": 12, "title": title, "merged": False, "state": "open"}
        self.pull_requests[branch] = result
        return result


class GitHubAdapterTests(unittest.TestCase):
    """Testit eivät käytä GitHub-verkkoa tai kirjoita tuotannon tilatiedostoihin."""

    def setUp(self):
        self.client = FakeGitHubClient()
        source = json.loads((ROOT / "data/module-state/tolkien.json").read_text(encoding="utf-8"))
        self.client.files[("main", "data/module-state/tolkien.json")] = GitHubFile(
            json.dumps(source, ensure_ascii=False).encode("utf-8"), "source-sha"
        )
        old_feed = b'<rss version="2.0"><channel><title>Tolkien</title></channel></rss>'
        self.client.files[("main", "feeds/tolkien.xml")] = GitHubFile(
            old_feed, blob_sha(old_feed)
        )
        rotation = (ROOT / "data/seurantatila.json").read_bytes()
        self.client.files[("main", "data/seurantatila.json")] = GitHubFile(
            rotation, blob_sha(rotation)
        )

    def test_rss_publisher_rejects_default_actions_token(self):
        with patch.dict(os.environ, {
            "GITHUB_REPOSITORY": "mikknikk/aiheseurain",
            "GITHUB_TOKEN": "actions-token",
        }, clear=True):
            client = GitHubApiClient()
            self.assertEqual(client.token_source, "GITHUB_TOKEN")
            with self.assertRaises(GitHubAdapterError):
                GitHubPagesRssPublisher(client, lambda *args, **kwargs: None)

    def test_rss_publisher_accepts_dedicated_workflow_triggering_token(self):
        with patch.dict(os.environ, {
            "GITHUB_REPOSITORY": "mikknikk/aiheseurain",
            "GITHUB_TOKEN": "actions-token",
            "AIHESEURAIN_GITHUB_TOKEN": "app-installation-token",
        }, clear=True):
            client = GitHubApiClient()
            self.assertEqual(client.token, "app-installation-token")
            self.assertEqual(client.token_source, "AIHESEURAIN_GITHUB_TOKEN")
            publisher = GitHubPagesRssPublisher(client, lambda *args, **kwargs: None)
            self.assertIsNotNone(publisher)

    def test_read_only_state_load_does_not_create_runtime_branch(self):
        store = GitHubModuleStateStore(self.client)
        store.load("tolkien")
        self.assertEqual(self.client.branches, {"main"})

    def test_github_contents_write_ambiguous_response_is_resolved_by_readback(self):
        client = GitHubApiClient("mikknikk/aiheseurain", "test-token")
        content = b'{"durable":true}\\n'
        encoded = __import__("base64").b64encode(content).decode("ascii")
        calls = {"get": 0}
        def request(method, path, payload=None):
            if method == "GET":
                calls["get"] += 1
                if calls["get"] == 1:
                    error = GitHubApiError("not found")
                    error.status = 404
                    raise error
                return {"type": "file", "content": encoded, "sha": blob_sha(content)}
            if method == "PUT":
                raise GitHubApiError("connection closed after write")
            raise AssertionError(method)
        with patch.object(client, "request", side_effect=request):
            result = client.put_file("data/test.json", content, "module-runtime-state",
                                     message="test write")
        self.assertEqual(result.content, content)
        self.assertEqual(calls["get"], 2)

    def test_github_contents_write_retries_unrelated_branch_conflict(self):
        client = GitHubApiClient("mikknikk/aiheseurain", "test-token")
        content = b'{"retry":true}\\n'
        calls = {"put": 0}
        def request(method, path, payload=None):
            if method == "GET":
                error = GitHubApiError("not found")
                error.status = 404
                raise error
            if method == "PUT":
                calls["put"] += 1
                if calls["put"] == 1:
                    error = GitHubApiError("branch advanced")
                    error.status = 409
                    raise error
                return {"content": {"sha": blob_sha(content)}}
            raise AssertionError(method)
        with patch.object(client, "request", side_effect=request):
            result = client.put_file("data/test.json", content, "module-runtime-state",
                                     message="test retry")
        self.assertEqual(result.content, content)
        self.assertEqual(calls["put"], 2)

    def test_state_store_load_and_sha_checked_save(self):
        store = GitHubModuleStateStore(self.client)
        state, sha = store.load("tolkien")
        updated = deepcopy(state)
        updated["migration"]["notes"] += " Runtime-testi."
        new_sha = store.save("tolkien", updated, expected_sha=sha)
        self.assertNotEqual(new_sha, sha)
        actual, actual_sha = store.load("tolkien")
        self.assertEqual(actual["migration"]["notes"], updated["migration"]["notes"])
        self.assertEqual(actual_sha, new_sha)

    def test_state_store_recovers_ambiguous_checkpoint_write(self):
        store = GitHubModuleStateStore(self.client)
        state, sha = store.load("tolkien")
        updated = deepcopy(state)
        updated["migration"]["notes"] += " Kirjoitus ehti perille."
        self.client.fail_after_write_path = "data/module-state/tolkien.json"
        new_sha = store.save("tolkien", updated, expected_sha=sha)
        actual, actual_sha = store.load("tolkien")
        self.assertEqual(actual["migration"]["notes"], updated["migration"]["notes"])
        self.assertEqual(new_sha, actual_sha)

    def test_state_store_rejects_stale_sha(self):
        store = GitHubModuleStateStore(self.client)
        state, sha = store.load("tolkien")
        first = deepcopy(state)
        first["migration"]["notes"] += " Ensimmäinen."
        store.save("tolkien", first, expected_sha=sha)
        second = deepcopy(state)
        second["migration"]["notes"] += " Vanhentunut."
        with self.assertRaises(StateConflictError):
            store.save("tolkien", second, expected_sha=sha)

    def test_state_store_rejects_wrong_module_ownership(self):
        store = GitHubModuleStateStore(self.client)
        state, sha = store.load("tolkien")
        state["module_id"] = "muumit"
        with self.assertRaises(GitHubAdapterError):
            store.save("tolkien", state, expected_sha=sha)

    def test_artifact_store_persists_immutable_run_and_index(self):
        store = GitHubArtifactStore(self.client)
        version = store.load_version("tolkien")
        artifact = {"observations": [{"id": "obs-1"}]}
        new_version = store.commit("tolkien", "run-212-001", artifact, expected_version=version)
        self.assertNotEqual(new_version, "missing")
        self.assertEqual(store.commit("tolkien", "run-212-001", artifact,
                                      expected_version=version), new_version)
        index = json.loads(self.client.get_file(
            "data/module-artifacts/tolkien/index.json", "module-runtime-state"
        ).content)
        self.assertIn("run-212-001", index["runs"])
        stored = json.loads(self.client.get_file(
            "data/module-artifacts/tolkien/run-212-001.json", "module-runtime-state"
        ).content)
        self.assertEqual(stored, artifact)

    def test_artifact_store_recovers_after_artifact_write_before_index(self):
        store = GitHubArtifactStore(self.client)
        version = store.load_version("tolkien")
        path = "data/module-artifacts/tolkien/run-212-recovery.json"
        self.client.fail_after_write_path = path
        with self.assertRaises(GitHubApiError):
            store.commit("tolkien", "run-212-recovery", {"value": "persisted"},
                         expected_version=version)
        self.assertIsNotNone(self.client.get_file(path, "module-runtime-state"))
        store.commit("tolkien", "run-212-recovery", {"value": "persisted"},
                     expected_version=version)
        index = json.loads(self.client.get_file(
            "data/module-artifacts/tolkien/index.json", "module-runtime-state"
        ).content)
        self.assertIn("run-212-recovery", index["runs"])

    def test_artifact_store_resolves_ambiguous_index_write_by_readback(self):
        store = GitHubArtifactStore(self.client)
        version = store.load_version("tolkien")
        index_path = "data/module-artifacts/tolkien/index.json"
        self.client.fail_after_write_path = index_path
        result = store.commit("tolkien", "run-212-index-retry", {"value": "persisted"},
                              expected_version=version)
        self.assertNotEqual(result, "missing")
        index = json.loads(self.client.get_file(index_path, "module-runtime-state").content)
        self.assertIn("run-212-index-retry", index["runs"])

    def test_artifact_store_rejects_different_content_for_same_run(self):
        store = GitHubArtifactStore(self.client)
        version = store.load_version("tolkien")
        store.commit("tolkien", "run-212-002", {"value": 1}, expected_version=version)
        with self.assertRaises(GitHubAdapterConflict):
            store.commit("tolkien", "run-212-002", {"value": 2},
                         expected_version=store.load_version("tolkien"))

    def test_artifact_store_rejects_stale_index_version(self):
        store = GitHubArtifactStore(self.client)
        old = store.load_version("tolkien")
        store.commit("tolkien", "run-212-003", {"value": 1}, expected_version=old)
        with self.assertRaises(GitHubAdapterConflict):
            store.commit("tolkien", "run-212-004", {"value": 2}, expected_version=old)

    def journal_record(self, run_id="run-212-journal"):
        return {
            "module_id": "tolkien", "run_id": run_id,
            "idempotency_key": f"tolkien:{run_id}",
            "report_sha256": "a" * 64, "artifacts_sha256": "b" * 64,
            "state_sha256": "state-sha", "artifact_version": "artifact-sha",
            "publication_targets": ["tolkien"],
            "period_start": "2026-11-19T00:00:00+02:00",
            "period_end": "2026-11-19T23:59:59+02:00",
            "prepared_at": "2026-11-19T09:00:00+02:00",
        }

    def test_publication_journal_persists_ordered_phase_history(self):
        journal = GitHubPublicationJournal(self.client)
        record = self.journal_record()
        self.assertEqual(journal.prepare(record)["phase"], "prepared")
        receipt = {"verified": True, "report_guid_refs": ["urn:aiheseurain:tolkien:2026-11-19:abc"], "published_items": 1}
        journal.advance("tolkien", record["run_id"], "published",
                        updated_at="2026-11-19T09:10:00+02:00", receipt=receipt)
        journal.advance("tolkien", record["run_id"], "artifacts_persisted",
                        updated_at="2026-11-19T09:11:00+02:00")
        final = journal.advance("tolkien", record["run_id"], "checkpoint_updated",
                                updated_at="2026-11-19T09:12:00+02:00")
        self.assertEqual(final["phase"], "checkpoint_updated")
        self.assertEqual([item["phase"] for item in final["history"]],
                         ["prepared", "published", "artifacts_persisted", "checkpoint_updated"])

    def test_publication_journal_recovers_ambiguous_phase_write(self):
        journal = GitHubPublicationJournal(self.client)
        record = self.journal_record("run-212-journal-retry")
        journal.prepare(record)
        path = "data/module-publication-journal/tolkien/run-212-journal-retry.json"
        self.client.fail_after_write_path = path
        advanced = journal.advance("tolkien", record["run_id"], "published",
                                   updated_at="2026-11-19T09:10:00+02:00",
                                   receipt={"verified": True, "report_guid_refs": ["urn:test"], "published_items": 1})
        self.assertEqual(advanced["phase"], "published")
        self.assertEqual(journal.load("tolkien", record["run_id"])["phase"], "published")

    def test_publication_journal_rejects_skipped_phase_and_conflicting_run(self):
        journal = GitHubPublicationJournal(self.client)
        record = self.journal_record()
        journal.prepare(record)
        with self.assertRaises(PublicationJournalConflict):
            journal.advance("tolkien", record["run_id"], "artifacts_persisted",
                            updated_at="2026-11-19T09:10:00+02:00")
        changed = dict(record, report_sha256="c" * 64)
        with self.assertRaises(PublicationJournalConflict):
            journal.prepare(changed)

    def test_publication_journal_same_phase_retry_is_idempotent(self):
        journal = GitHubPublicationJournal(self.client)
        record = self.journal_record()
        first = journal.prepare(record)
        second = journal.prepare(record)
        self.assertEqual(first, second)

    def test_publisher_opens_pr_but_never_merges_it(self):
        client = self.client
        guid = "urn:aiheseurain:tolkien:2026-11-19:00000000-0000-5000-8000-000000000001"
        xml = ('<?xml version="1.0"?><rss version="2.0"><channel><title>Tolkien</title>'
               '<item><title>Uusi raportti</title><guid isPermaLink="false">'
               + guid + '</guid><description>Raportti</description></item></channel></rss>')
        gate = {"decision": "approved", "run_id": "run-212-publish",
                "feed_path": "feeds/tolkien.xml", "task_id": "tolkien"}
        def builder(module_id, run_id, report_content):
            return PublicationCandidate(
                files={"feeds/tolkien.xml": xml,
                       f"reports/julkaisuportit/{run_id}.json": json.dumps(gate)},
                feed_path="feeds/tolkien.xml",
                public_url="https://mikknikk.github.io/aiheseurain/feeds/tolkien.xml")
        publisher = GitHubPagesRssPublisher(
            client, builder, public_fetcher=lambda url: b"<rss version=\"2.0\"><channel /></rss>")
        receipt = publisher.publish("tolkien", "run-212-publish", "Raportti",
                                    idempotency_key="tolkien:run-212-publish")
        self.assertFalse(receipt.verified)
        self.assertFalse(client.pull_requests[
            next(iter(client.pull_requests))
        ]["merged"])
        self.assertFalse(publisher.verify(receipt))

    def test_publisher_verifies_public_feed_after_pr_is_merged(self):
        client = self.client
        guid = "urn:aiheseurain:tolkien:2026-11-19:00000000-0000-5000-8000-000000000002"
        xml = ('<?xml version="1.0"?><rss version="2.0"><channel><title>Tolkien</title>'
               '<item><title>Uusi raportti</title><guid isPermaLink="false">'
               + guid + '</guid><description>Raportti</description></item></channel></rss>')
        gate = {"decision": "approved", "run_id": "run-212-merged",
                "feed_path": "feeds/tolkien.xml", "task_id": "tolkien"}
        def builder(module_id, run_id, report_content):
            return PublicationCandidate(
                files={"feeds/tolkien.xml": xml,
                       f"reports/julkaisuportit/{run_id}.json": json.dumps(gate)},
                feed_path="feeds/tolkien.xml",
                public_url="https://mikknikk.github.io/aiheseurain/feeds/tolkien.xml")
        publisher = GitHubPagesRssPublisher(
            client, builder, public_fetcher=lambda url: xml.encode("utf-8"))
        publisher.publish("tolkien", "run-212-merged", "Raportti",
                          idempotency_key="tolkien:run-212-merged")
        branch = next(iter(client.pull_requests))
        client.pull_requests[branch]["merged"] = True
        receipt = publisher.publish("tolkien", "run-212-merged", "Raportti",
                                    idempotency_key="tolkien:run-212-merged")
        self.assertTrue(receipt.verified)
        self.assertTrue(publisher.verify(receipt))

    def test_publisher_rejects_public_feed_with_same_guids_but_changed_content(self):
        client = self.client
        guid = "urn:aiheseurain:tolkien:2026-11-19:00000000-0000-5000-8000-000000000003"
        xml = ('<?xml version="1.0"?><rss version="2.0"><channel><title>Tolkien</title>'
               '<item><title>Uusi raportti</title><guid isPermaLink="false">'
               + guid + '</guid><description>Oikea raportti</description></item></channel></rss>')
        changed_xml = xml.replace("Oikea raportti", "Eri sisältö")
        gate = {"decision": "approved", "run_id": "run-212-digest",
                "feed_path": "feeds/tolkien.xml", "task_id": "tolkien"}
        def builder(module_id, run_id, report_content):
            return PublicationCandidate(
                files={"feeds/tolkien.xml": xml,
                       f"reports/julkaisuportit/{run_id}.json": json.dumps(gate)},
                feed_path="feeds/tolkien.xml",
                public_url="https://mikknikk.github.io/aiheseurain/feeds/tolkien.xml")
        publisher = GitHubPagesRssPublisher(
            client, builder, public_fetcher=lambda url: changed_xml.encode("utf-8"))
        publisher.publish("tolkien", "run-212-digest", "Raportti",
                          idempotency_key="tolkien:run-212-digest")
        branch = next(iter(client.pull_requests))
        client.pull_requests[branch]["merged"] = True
        receipt = publisher.publish("tolkien", "run-212-digest", "Raportti",
                                    idempotency_key="tolkien:run-212-digest")
        self.assertFalse(receipt.verified)

    def test_target_publisher_requires_an_active_registry_route(self):
        publisher = GitHubPagesRssPublisher(self.client, lambda *args, **kwargs: None)
        report = {
            "target_id": "tolkien.j-r-r-tolkien",
            "observation_types": ["news"],
            "report_content": "Testiraportti",
        }
        with self.assertRaises(ValueError):
            publisher.publish_target_reports("tolkien", "run-212-route", [report])

    def test_process_module_cannot_use_topic_rss_publisher(self):
        publisher = GitHubPagesRssPublisher(self.client, lambda *args, **kwargs: None)
        report = {
            "target_id": "indian-film-screening-watch.all-indian-film-screenings-finland",
            "observation_types": ["screening"],
            "report_content": "Näytösraportti",
        }
        with self.assertRaises(GitHubAdapterError):
            publisher.publish_target_reports("indian-film-screening-watch", "run-212-screening", [report])

    def test_publisher_rejects_unapproved_gate_report(self):
        gate = {"decision": "pending", "run_id": "run-212-gate",
                "feed_path": "feeds/tolkien.xml", "task_id": "tolkien"}
        xml = ('<rss version="2.0"><channel><title>Tolkien</title><item>'
               '<guid>urn:aiheseurain:tolkien:2026-11-19:abc</guid>'
               '</item></channel></rss>')
        def builder(module_id, run_id, report_content):
            return PublicationCandidate(
                files={"feeds/tolkien.xml": xml,
                       f"reports/julkaisuportit/{run_id}.json": json.dumps(gate)},
                feed_path="feeds/tolkien.xml",
                public_url="https://mikknikk.github.io/aiheseurain/feeds/tolkien.xml")
        publisher = GitHubPagesRssPublisher(self.client, builder)
        with self.assertRaises(GitHubAdapterError):
            publisher.publish("tolkien", "run-212-gate", "Raportti",
                              idempotency_key="tolkien:run-212-gate")

    def test_run_recorder_keeps_report_content_out_of_history(self):
        recorder = GitHubRunRecorder(self.client)
        result = ModuleRunResult(
            module_id="tolkien", module_type="topic",
            module_definition_version="1.0.0", contract_version="1.0.0",
            run_id="run-212-history", period_start="2026-11-18T00:00:00+02:00",
            period_end="2026-11-19T00:00:00+02:00", mode="shadow",
            status="succeeded", phase="complete",
            started_at="2026-11-19T09:00:00+02:00",
            finished_at="2026-11-19T09:05:00+02:00",
            source_scan_complete=True, quality_passed=True,
            checked_at="2026-11-19T09:04:00+02:00",
            published_items=1, sources_checked=3,
            report_guid_refs=("urn:aiheseurain:tolkien:2026-11-19:abc",),
        )
        recorder.record(result)
        prefix = "data/module-run-history/tolkien/run-212-history/"
        paths = [path for (branch, path) in self.client.files if branch == "module-runtime-state" and path.startswith(prefix)]
        self.assertEqual(len(paths), 1)
        content = self.client.get_file(paths[0], "module-runtime-state").content
        self.assertIn(b"run-212-history", content)
        self.assertIn(b"report_guid_refs", content)
        self.assertNotIn(b"report_content", content)
        # Uusi yritys samalle run_id:lle saa oman muuttumattoman auditointitietueen.
        recorder.record(replace(
            result, started_at="2026-11-19T09:10:00+02:00",
            finished_at="2026-11-19T09:15:00+02:00",
        ))
        paths = [path for (branch, path) in self.client.files if branch == "module-runtime-state" and path.startswith(prefix)]
        self.assertEqual(len(paths), 2)

    def test_handoff_store_is_immutable_and_idempotent(self):
        store = GitHubHandoffStore(self.client)
        record = {
            "schema_version": 1, "module_id": "tolkien",
            "module_definition_version": "1.0.0", "contract_version": "1.0.0",
            "run_id": "run-213-handoff", "task_id": "tolkien",
            "feed_path": "feeds/tolkien.xml",
            "period": {"start": "2026-11-18T00:00:00+02:00", "end": "2026-11-19T00:00:00+02:00"},
            "requested_at": "2026-11-19T09:00:00+02:00",
            "input_sha256": "a" * 64, "validated_at": "2026-11-19T09:01:00+02:00",
        }
        stored = store.store_or_verify(record)
        self.assertEqual(store.load("tolkien", "run-213-handoff"), stored)
        retried = dict(record, validated_at="2026-11-19T09:02:00+02:00")
        self.assertEqual(store.store_or_verify(retried), stored)
        with self.assertRaises(GitHubAdapterConflict):
            store.store_or_verify(dict(retried, input_sha256="b" * 64))

    def test_handoff_store_read_does_not_create_runtime_branch(self):
        store = GitHubHandoffStore(self.client)
        self.assertIsNone(store.load("tolkien", "run-213-missing"))
        self.assertEqual(self.client.branches, {"main"})

    def _successful_rotation_result(self, run_id="run-213-rotation"):
        return ModuleRunResult(
            module_id="muumit", module_type="topic",
            module_definition_version="1.0.0", contract_version="1.0.0",
            run_id=run_id, period_start="2026-11-18T00:00:00+02:00",
            period_end="2026-11-19T00:00:00+02:00", mode="production",
            status="succeeded", phase="complete",
            started_at="2026-11-19T09:00:00+02:00",
            finished_at="2026-11-19T09:05:00+02:00",
            source_scan_complete=True, quality_passed=True,
            published=True, checkpoint_updated=True,
            checked_at="2026-11-19T09:04:00+02:00",
            published_items=1, sources_checked=4,
            report_guid_refs=("urn:aiheseurain:muumit:2026-11-19:abc",),
        )

    def test_rotation_advances_only_after_verified_checkpoint_and_is_idempotent(self):
        store = GitHubRotationStateStore(self.client)
        before, _ = store.load()
        screening_before = deepcopy(before["separate_screening_watch"])
        result = self._successful_rotation_result()
        after, sha = store.advance(result, task_id="muumit", feed_path="feeds/muumit.xml")
        self.assertEqual(after["rotation"]["next_task"], "wakaliwood")
        self.assertEqual(after["rotation"]["last_completed_run_id"], result.run_id)
        self.assertEqual(after["rotation"]["tasks"]["muumit"]["last_result"], "published")
        self.assertEqual(after["separate_screening_watch"], screening_before)
        retried, retry_sha = store.advance(result, task_id="muumit", feed_path="feeds/muumit.xml")
        self.assertEqual(retried, after)
        self.assertEqual(retry_sha, sha)

    def test_rotation_rejects_partial_or_unpublished_result(self):
        store = GitHubRotationStateStore(self.client)
        result = replace(self._successful_rotation_result(), status="partial")
        with self.assertRaises(GitHubAdapterError):
            store.advance(result, task_id="muumit", feed_path="feeds/muumit.xml")
        result = replace(self._successful_rotation_result(), published=False)
        with self.assertRaises(GitHubAdapterError):
            store.advance(result, task_id="muumit", feed_path="feeds/muumit.xml")

    def test_rotation_rejects_out_of_order_task_and_process_module(self):
        store = GitHubRotationStateStore(self.client)
        with self.assertRaises(GitHubAdapterError):
            store.advance(self._successful_rotation_result(), task_id="tolkien", feed_path="feeds/tolkien.xml")
        process_result = replace(
            self._successful_rotation_result(),
            module_id="indian-film-screening-watch", module_type="process",
        )
        with self.assertRaises(GitHubAdapterError):
            store.advance(process_result, task_id="indian_film_screenings", feed_path="feeds/intialaisten-elokuvien-naytokset.xml")


if __name__ == "__main__":
    unittest.main()
