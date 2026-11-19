"""Testaa vanhan ja uuden ajopolun kirjoitukseton varjovertaaminen."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import unittest

from scripts.compare_shadow_runs import ShadowComparisonError, compare_shadow_runs

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/shadow-comparison/tolkien.json"


class ShadowComparisonTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_representative_topic_and_same_period_are_compared(self):
        report = compare_shadow_runs(self.data)
        self.assertTrue(report["period_match"])
        self.assertEqual(report["module_id"], "tolkien")
        self.assertEqual(
            report["source_comparison"]["shared_source_ids"],
            ["tolkien-estate", "tolkien-society", "yle-tolkien"],
        )
        self.assertEqual(
            report["source_comparison"]["module_statuses"]["tolkien-society"],
            "unavailable",
        )
        self.assertIn(
            "Vanha raportti sisältää lisäväitteen.",
            report["report_comparison"]["legacy_only_claims"],
        )
        self.assertIn(
            "Tapahtumien seuranta käsittelee Suomessa järjestettävän tapahtuman.",
            report["report_comparison"]["module_only_claims"],
        )
        self.assertTrue(report["guid_comparison"]["legacy_unique"])
        self.assertTrue(report["guid_comparison"]["module_unique"])
        self.assertTrue(report["guid_comparison"]["module_format_valid"])
        self.assertTrue(report["uncertainty_comparison"]["module_documented"])
        self.assertTrue(report["publication_readiness"]["legacy_ready"])
        self.assertTrue(report["publication_readiness"]["module_ready"])

    def test_missing_source_is_reported_without_a_numeric_coverage_gate(self):
        data = deepcopy(self.data)
        data["module_result"]["metadata"]["source_audit"]["source_checks"] = [
            item for item in data["module_result"]["metadata"]["source_audit"]["source_checks"]
            if item["source_id"] != "tolkien-estate"
        ]
        data["module_result"]["sources_checked"] = 2
        report = compare_shadow_runs(data)
        self.assertEqual(
            report["source_comparison"]["legacy_only_source_ids"],
            ["tolkien-estate"],
        )
        # Vertailu kuvaa eron; se ei päätä onnistumista lähteiden lukumäärän perusteella.
        self.assertTrue(report["publication_readiness"]["module_ready"])

    def test_empty_news_result_is_a_valid_successful_comparison(self):
        data = deepcopy(self.data)
        module = data["module_result"]
        module["target_reports"] = [dict(
            module["target_reports"][0],
            report_content="<p>Seurantajaksolla ei löytynyt vahvistettuja uusia uutisia.</p>",
        )]
        module["report_guid_refs"] = [module["report_guid_refs"][0]]
        assessment = module["metadata"]["publication_assessment"]
        assessment["claim_assessments"] = [{
            "claim_id": "no-news",
            "claim": "Seurantajaksolla ei löytynyt vahvistettuja uusia uutisia.",
            "verification_status": "yhden_toimituksellisen_lahteen_raportoima",
            "sources": [{
                "source_id": "yle-tolkien",
                "source_class": "B",
                "source_role": "toimituksellinen",
                "independence": "riippumaton",
            }],
        }]
        report = compare_shadow_runs(data)
        self.assertEqual(report["statuses"]["module"], "succeeded")
        self.assertTrue(report["publication_readiness"]["module_ready"])
        self.assertGreater(report["report_comparison"]["module_word_count"], 0)

    def test_partial_and_interrupted_result_is_not_publication_ready(self):
        data = deepcopy(self.data)
        data["module_result"]["status"] = "partial"
        data["module_result"]["source_scan_complete"] = False
        report = compare_shadow_runs(data)
        self.assertFalse(report["publication_readiness"]["module_ready"])
        self.assertIn("result_status:partial", report["publication_readiness"]["module_blockers"])
        self.assertIn("source_scan_incomplete", report["publication_readiness"]["module_blockers"])

    def test_failed_result_is_compared_but_never_marked_ready(self):
        data = deepcopy(self.data)
        module = data["module_result"]
        module["status"] = "failed"
        module["source_scan_complete"] = False
        module.pop("target_reports")
        module.pop("report_guid_refs")
        module["sources_checked"] = 0
        module["metadata"].pop("publication_assessment")
        module["metadata"]["source_audit"]["source_checks"] = []
        report = compare_shadow_runs(data)
        self.assertFalse(report["publication_readiness"]["module_ready"])
        self.assertIn("report_content_missing", report["publication_readiness"]["module_blockers"])

    def test_invalid_result_is_rejected(self):
        data = deepcopy(self.data)
        data["module_result"].pop("checked_at")
        with self.assertRaises(ShadowComparisonError):
            compare_shadow_runs(data)

    def test_wrong_module_and_wrong_period_are_rejected(self):
        data = deepcopy(self.data)
        data["module_result"]["module_id"] = "muumit"
        with self.assertRaises(ShadowComparisonError):
            compare_shadow_runs(data)
        data = deepcopy(self.data)
        data["module_result"]["period"]["end"] = "2026-11-20T00:00:00+02:00"
        with self.assertRaises(ShadowComparisonError):
            compare_shadow_runs(data)

    def test_unregistered_source_cannot_be_smuggled_into_module_audit(self):
        data = deepcopy(self.data)
        data["module_result"]["metadata"]["source_audit"]["source_checks"].append({
            "source_id": "muumit-secret-source",
            "status": "checked",
            "note": "Ei kuulu Tolkien-moduulille.",
        })
        with self.assertRaises(ShadowComparisonError):
            compare_shadow_runs(data)

    def test_repeating_the_same_comparison_is_deterministic_and_read_only(self):
        before = hashlib.sha256(FIXTURE.read_bytes()).hexdigest()
        first = compare_shadow_runs(self.data)
        second = compare_shadow_runs(self.data)
        after = hashlib.sha256(FIXTURE.read_bytes()).hexdigest()
        self.assertEqual(first, second)
        self.assertEqual(before, after)
        self.assertEqual(first["side_effects"], {
            "production_writes": False,
            "rss_written": False,
            "checkpoint_updated": False,
            "rotation_advanced": False,
            "files_written": [],
        })


if __name__ == "__main__":
    unittest.main()
