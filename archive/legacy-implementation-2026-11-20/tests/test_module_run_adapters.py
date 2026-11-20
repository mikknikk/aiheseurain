"""Testaa orkestroinnin paikalliset tallennus- ja julkaisusovittimet."""
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace
import json
import tempfile
import unittest

from scripts.module_registry import load_registry
from scripts.module_state import StateConflictError
from scripts.publication_journal import JsonFilePublicationJournal, PublicationJournalConflict
from dataclasses import replace
from scripts.module_orchestrator import (
    ModuleExecutionOutput, ModuleOrchestrator, ModuleRunRequest,
)
from scripts.module_run_adapters import (
    AdapterConflictError, JsonFileArtifactStore, JsonFileModuleStateStore,
    JsonlRunRecorder, LocalFileRssPublisher, StructuralModuleQualityGate,
)

ROOT = Path(__file__).resolve().parents[1]
NOW = "2026-11-18T08:00:00+02:00"
START = "2026-11-17T00:00:00+02:00"
END = "2026-11-18T07:59:59+02:00"


def tolkien_definition():
    """Lataa testiin nykyisen, mutta passiivisen Tolkien-määrityksen."""
    registry = load_registry(include_inactive=True)
    return next(item.definition for item in registry.modules if item.module_id == "tolkien")


def request(run_id="local-adapter-run-001"):
    """Luo yhden tuotantotilaa simuloivan testipyynnön."""
    definition = tolkien_definition()
    return ModuleRunRequest(
        module_id="tolkien",
        module_definition_version=definition["definition_version"],
        contract_version=definition["contract_version"],
        run_id=run_id,
        period_start=START,
        period_end=END,
        mode="production",
        requested_at=NOW,
    )


def successful_output(req):
    """Luo rakenteellisesti kelvollisen testiraportin ja artefaktin."""
    return ModuleExecutionOutput(
        status="succeeded",
        source_scan_complete=True,
        checked_at=req.requested_at,
        period_start=req.period_start,
        period_end=req.period_end,
        report_content="<article><h1>Testiraportti</h1></article>",
        published_items=1,
        sources_checked=3,
        source_check_run_refs=("source-check-001",),
        artifacts={"observations": [{"id": "observation-1"}]},
    )


class StaticExecutor:
    """Palauttaa testin antaman tuloksen ilman ulkoisia palveluja."""

    def __init__(self, output):
        self.output = output

    def execute(self, definition, request, provider_router):
        return self.output


class LocalAdapterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.definition = tolkien_definition()
        self.state_root = self.root / "states"
        self.artifact_root = self.root / "artifacts"
        self.state_root.mkdir()
        source_state = json.loads(
            (ROOT / "data/module-state/tolkien.json").read_text(encoding="utf-8")
        )
        (self.state_root / "tolkien.json").write_text(
            json.dumps(source_state, ensure_ascii=False), encoding="utf-8"
        )
        self.state_store = JsonFileModuleStateStore(self.state_root)
        self.artifact_store = JsonFileArtifactStore(self.artifact_root)
        self.publisher = LocalFileRssPublisher(
            self.root, {"tolkien": "feeds/tolkien.xml"}
        )
        self.recorder = JsonlRunRecorder(self.root / "run-history" / "runs.jsonl")
        self.journal = JsonFilePublicationJournal(self.root / "publication-manifests")

    def tearDown(self):
        self.temp.cleanup()

    def orchestrator(self, req, output):
        """Rakenna orkestroija testirekisterillä, jossa vain testimoduuli on active."""
        module = SimpleNamespace(
            module_id="tolkien", status="active",
            definition=self.definition, error=None,
        )
        registry = SimpleNamespace(modules=[module])
        return ModuleOrchestrator(
            executor=StaticExecutor(output),
            quality_gate=StructuralModuleQualityGate(),
            state_store=self.state_store,
            artifact_store=self.artifact_store,
            publisher=self.publisher,
            publication_journal=self.journal,
            recorder=self.recorder,
            registry_loader=lambda include_inactive=True: registry,
            activation_loader=lambda module_id: True,
        )

    def test_complete_run_publishes_persists_and_updates_checkpoint(self):
        """Täydellinen ajo julkaisee, tallentaa artefaktit ja siirtää checkpointin."""
        req = request()
        orchestrator = self.orchestrator(req, successful_output(req))
        result = orchestrator.run(req, production_authorized=True)

        self.assertEqual(result.status, "succeeded")
        self.assertTrue(result.published)
        self.assertTrue(result.checkpoint_updated)

        state, _ = self.state_store.load("tolkien")
        self.assertEqual(
            state["checkpoint"]["last_successful_run"]["run_id"], req.run_id
        )

        artifact_path = self.artifact_root / "tolkien.json"
        artifacts = json.loads(artifact_path.read_text(encoding="utf-8"))
        self.assertIn(req.run_id, artifacts["runs"])

        feed = self.root / "feeds/tolkien.xml"
        self.assertTrue(feed.is_file())
        self.assertTrue(self.publisher.verify(
            SimpleNamespace(report_guid_refs=state["publication"]["guid_refs"][-1:])
        ))

        audit = self.recorder.path.read_text(encoding="utf-8")
        self.assertIn(req.run_id, audit)
        self.assertNotIn("Testiraportti", audit)
        self.assertNotIn("observations", audit)

    def test_same_run_is_idempotent_for_artifacts_and_rss(self):
        """Sama moduuli/run_id ei lisää toista artefaktia tai RSS-itemiä."""
        req = request()
        output = successful_output(req)
        orchestrator = self.orchestrator(req, output)
        first = orchestrator.run(req, production_authorized=True)
        self.assertEqual(first.status, "succeeded")

        feed = self.root / "feeds/tolkien.xml"
        before = feed.read_bytes()
        receipt = self.publisher.publish(
            "tolkien", req.run_id, output.report_content,
            idempotency_key=f"tolkien:{req.run_id}",
        )
        self.assertTrue(self.publisher.verify(receipt))
        self.assertEqual(feed.read_bytes(), before)

        artifacts = json.loads(
            (self.artifact_root / "tolkien.json").read_text(encoding="utf-8")
        )
        self.assertEqual(list(artifacts["runs"]), [req.run_id])


    def test_manifest_records_every_successful_publication_phase(self):
        """Manifesti todentaa julkaisun, artefaktit ja checkpointin valmistumisen."""
        req = request("manifest-run-001")
        result = self.orchestrator(req, successful_output(req)).run(req, production_authorized=True)
        manifest = self.journal.load("tolkien", req.run_id)
        self.assertEqual(result.status, "succeeded")
        self.assertEqual(manifest["phase"], "checkpoint_updated")
        self.assertEqual(manifest["publication_targets"], ["tolkien"])
        self.assertEqual(manifest["receipt"]["published_items"], 1)

    def test_manifest_blocks_a_second_run_for_the_same_module_period(self):
        """Paikallinenkin manifesti estää eri run_id:n saman moduulijakson varauksen."""
        req = request("period-claim-001")
        self.orchestrator(req, successful_output(req)).run(req, production_authorized=True)
        with self.assertRaises(PublicationJournalConflict):
            self.journal.prepare({
                "module_id": "tolkien", "run_id": "period-claim-002",
                "idempotency_key": "tolkien:period-claim-002",
                "report_sha256": "a" * 64, "artifacts_sha256": "b" * 64,
                "state_sha256": "state-sha", "artifact_version": "artifact-v",
                "publication_targets": ["tolkien"],
                "period_start": req.period_start, "period_end": req.period_end,
                "prepared_at": req.requested_at,
            })

    def test_manifest_rejects_same_run_with_different_report(self):
        """Saman moduuli-/ajotunnisteen eri raporttisisältö ei voi korvata manifestia."""
        req = request("manifest-conflict-001")
        self.orchestrator(req, successful_output(req)).run(req, production_authorized=True)
        changed = successful_output(req)
        changed = replace(changed, report_content="<article>eri sisältö</article>")
        with self.assertRaises(PublicationJournalConflict):
            self.journal.prepare({
                "module_id": "tolkien", "run_id": req.run_id,
                "idempotency_key": f"tolkien:{req.run_id}",
                "report_sha256": __import__("scripts.publication_journal", fromlist=["content_digest"]).content_digest(changed.report_content),
                "artifacts_sha256": __import__("scripts.publication_journal", fromlist=["content_digest"]).content_digest(changed.artifacts),
                "state_sha256": "state-sha", "artifact_version": "artifact-v",
                "publication_targets": ["tolkien"],
                "period_start": req.period_start, "period_end": req.period_end,
                "prepared_at": req.requested_at,
            })

    def test_state_store_rejects_stale_sha(self):
        """Vanha SHA ei saa ylikirjoittaa toisen ajon päivittämää tilaa."""
        state, old_sha = self.state_store.load("tolkien")
        updated = deepcopy(state)
        updated["migration"]["notes"] += " Tarkistettu."
        self.state_store.save("tolkien", updated, expected_sha=old_sha)
        with self.assertRaises(StateConflictError):
            self.state_store.save("tolkien", state, expected_sha=old_sha)

    def test_rss_publisher_preserves_previous_guids(self):
        """Uusi RSS-item säilyttää aiemmat GUIDit ja välttää item-linkin."""
        first = self.publisher.publish(
            "tolkien", "run-a", "<p>Ensimmäinen</p>",
            idempotency_key="tolkien:run-a",
        )
        second = self.publisher.publish(
            "tolkien", "run-b", "<p>Toinen</p>",
            idempotency_key="tolkien:run-b",
        )
        feed = self.root / "feeds/tolkien.xml"
        import xml.etree.ElementTree as ET
        root = ET.fromstring(feed.read_bytes())
        items = root.findall("./channel/item")
        guids = [item.findtext("guid") for item in items]
        self.assertEqual(len(guids), 2)
        self.assertEqual(len(set(guids)), 2)
        self.assertTrue(set(first.report_guid_refs + second.report_guid_refs).issubset(set(guids)))
        self.assertTrue(all(item.find("link") is None for item in items))

    def test_recorder_treats_timestamp_only_retry_as_idempotent(self):
        """Saman ajon uudelleenkirjaus ei luo duplikaattia pelkkien aikojen vuoksi."""
        req = request()
        result = self.orchestrator(req, successful_output(req)).run(
            req, production_authorized=True
        )
        before = self.recorder.path.read_bytes()
        retried = replace(
            result,
            started_at="2026-11-18T08:01:00+02:00",
            finished_at="2026-11-18T08:01:01+02:00",
        )
        self.recorder.record(retried)
        self.assertEqual(self.recorder.path.read_bytes(), before)

    def test_artifact_store_rejects_stale_version(self):
        """Vanhentunut artefaktiversio ei saa ylikirjoittaa uudempaa."""
        version = self.artifact_store.load_version("tolkien")
        self.artifact_store.commit(
            "tolkien", "run-a", {"value": 1}, expected_version=version
        )
        with self.assertRaises(AdapterConflictError):
            self.artifact_store.commit(
                "tolkien", "run-b", {"value": 2}, expected_version=version
            )

    def test_rss_publisher_rejects_same_guid_with_different_content(self):
        """Sama idempotenssitunniste ei voi julkaista toista sisältöä."""
        self.publisher.publish(
            "tolkien", "run-a", "<p>Ensimmäinen</p>",
            idempotency_key="tolkien:run-a",
        )
        with self.assertRaises(AdapterConflictError):
            self.publisher.publish(
                "tolkien", "run-a", "<p>Muuttunut</p>",
                idempotency_key="tolkien:run-a",
            )

    def test_partial_source_scan_does_not_write_publication_or_checkpoint(self):
        """Osittainen lähdehaku ei julkaise eikä muuta moduulin checkpointia."""
        req = request("partial-run-001")
        output = successful_output(req)
        output = ModuleExecutionOutput(
            status="partial", source_scan_complete=False,
            checked_at=output.checked_at, period_start=output.period_start,
            period_end=output.period_end, report_content=output.report_content,
            artifacts=output.artifacts,
        )
        before, before_sha = self.state_store.load("tolkien")
        result = self.orchestrator(req, output).run(req, production_authorized=True)
        after, after_sha = self.state_store.load("tolkien")

        self.assertEqual(result.status, "failed")
        self.assertEqual(before, after)
        self.assertEqual(before_sha, after_sha)
        self.assertFalse((self.root / "feeds/tolkien.xml").exists())
        self.assertFalse((self.artifact_root / "tolkien.json").exists())

    def test_run_recorder_is_idempotent_and_excludes_report_content(self):
        """Ajotulosloki ei tallenna raporttitekstiä eikä duplikoi samaa ajoa."""
        req = request()
        result = self.orchestrator(req, successful_output(req)).run(
            req, production_authorized=True
        )
        first = self.recorder.path.read_bytes()
        self.recorder.record(result)
        self.assertEqual(self.recorder.path.read_bytes(), first)
        self.assertNotIn(b"Testiraportti", first)


if __name__ == "__main__":
    unittest.main()
