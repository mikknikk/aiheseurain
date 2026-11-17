"""Julkaisulaadun portin yksikkötestit."""

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts/validate_publication_gate.py"
SPEC = importlib.util.spec_from_file_location("validate_publication_gate", MODULE_PATH)
gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate)


def approved_record():
    checks = {
        key: {"status": "pass", "note": "Tarkistettu ja hyväksytty."}
        for key in gate.CHECK_IDS
    }
    # Lähteiden avaamisesta, väitteiden vastaavuudesta ja riippumattomuudesta
    # vaaditaan yksilöitävä näyttöviite myös hyväksytyssä testitietueessa.
    checks["sources_opened"]["evidence"] = ["Lähde A: avattu ja tarkistettu."]
    checks["claim_support"]["evidence"] = ["Väitteet 1–3 verrattu lähteeseen A."]
    checks["source_independence"]["evidence"] = ["Lähteet A ja B ovat eri toimituksia."]

    return {
        "schema_version": 1,
        "run_id": "test-run-001",
        "task_id": "tolkien",
        "feed_path": "feeds/tolkien.xml",
        "checked_at": "2026-11-17T12:00:00+02:00",
        "checklist": checks,
        "decision": "approved",
        "reviewer_notes": ["Testiraportti."],
    }


class PublicationGateTests(unittest.TestCase):
    def test_approved_report_passes(self):
        record = approved_record()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "test-run-001.json"
            path.write_text(json.dumps(record), encoding="utf-8")
            result = gate.validate_record(path, {"tolkien": "feeds/tolkien.xml"})
        self.assertEqual(result["decision"], "approved")

    def test_required_source_evidence_cannot_be_omitted(self):
        record = approved_record()
        del record["checklist"]["sources_opened"]["evidence"]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "test-run-001.json"
            path.write_text(json.dumps(record), encoding="utf-8")
            with self.assertRaises(SystemExit):
                gate.validate_record(path, {"tolkien": "feeds/tolkien.xml"})

    def test_failed_editorial_check_is_rejected(self):
        record = approved_record()
        record["checklist"]["claim_support"] = {
            "status": "fail", "note": "Väite ei vastaa lähdettä.", "evidence": ["Raportin väite 2 ei vastaa lähteen A sisältöä."]
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "test-run-001.json"
            path.write_text(json.dumps(record), encoding="utf-8")
            with self.assertRaises(SystemExit):
                gate.validate_record(path, {"tolkien": "feeds/tolkien.xml"})

    def test_not_applicable_requires_reason(self):
        record = approved_record()
        record["checklist"]["accessibility"] = {
            "status": "not_applicable", "note": " "
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "test-run-001.json"
            path.write_text(json.dumps(record), encoding="utf-8")
            with self.assertRaises(SystemExit):
                gate.validate_record(path, {"tolkien": "feeds/tolkien.xml"})

    def test_automated_checks_cannot_be_skipped(self):
        record = approved_record()
        record["checklist"]["xml_html"] = {
            "status": "not_applicable", "note": "Automaattinen testi ohitettiin."
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "test-run-001.json"
            path.write_text(json.dumps(record), encoding="utf-8")
            with self.assertRaises(SystemExit):
                gate.validate_record(path, {"tolkien": "feeds/tolkien.xml"})

    def test_task_and_feed_must_match(self):
        record = approved_record()
        record["feed_path"] = "feeds/taylor-swift.xml"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "test-run-001.json"
            path.write_text(json.dumps(record), encoding="utf-8")
            with self.assertRaises(SystemExit):
                gate.validate_record(path, {"tolkien": "feeds/tolkien.xml"})


if __name__ == "__main__":
    unittest.main()
