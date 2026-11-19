"""Testaa useiden ChatGPT-kohderaporttien RSS-ehdokkaan muodostus."""
from pathlib import Path
from types import SimpleNamespace
import json
import tempfile
import unittest
import xml.etree.ElementTree as ET
from unittest.mock import patch

from scripts.chatgpt_rss_candidate import ChatGPTRssCandidateBuilder
from scripts.github_module_adapters import GitHubAdapterError

ROOT = Path(__file__).resolve().parents[1]


def assessment():
    """Rakenna skeeman mukainen toimituksellinen arvio testiraportille."""
    keys = (
        "sources_opened", "claim_support", "source_independence", "uncertainty",
        "dates", "tracking_period", "duplicates", "guid_preservation",
        "xml_html", "rss_structure", "report_completeness", "accessibility",
    )
    checklist = {
        key: {"status": "pass", "note": "Tarkistettu.", "evidence": ["Testinäyttö"]}
        for key in keys
    }
    return {
        "checklist": checklist,
        "decision": "approved",
        "reviewer_notes": ["Testiraportti hyväksytty."],
        "claim_assessments": [{
            "claim_id": "claim-1",
            "claim": "Testiväite",
            "verification_status": "riippumattomissa_toimituksellisissa_lahteissa_vahvistettu",
            "sources": [{
                "source_id": "tolkien-com",
                "source_class": "A",
                "source_role": "ensisijainen",
                "independence": "riippumaton",
            }],
        }],
    }


class ChatGPTRssCandidateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "feeds").mkdir()
        (self.root / "data").mkdir()
        (self.root / "schemas").mkdir()
        (self.root / "feeds/tolkien.xml").write_text(
            '<?xml version="1.0"?><rss version="2.0"><channel>'
            '<title>Tolkien</title><description>Testisyöte</description>'
            '<link>https://example.invalid/</link></channel></rss>',
            encoding="utf-8",
        )
        (self.root / "data/feed-catalog.json").write_text(json.dumps({
            "feeds": [{"id": "tolkien", "type": "topic", "path": "feeds/tolkien.xml"}]
        }), encoding="utf-8")
        (self.root / "schemas/julkaisuportti.schema.json").write_text(
            (ROOT / "schemas/julkaisuportti.schema.json").read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        self.definition = {
            "module_id": "tolkien",
            "module_type": "topic",
        }
        self.registry = SimpleNamespace(
            modules=(SimpleNamespace(module_id="tolkien", definition=self.definition),)
        )
        self.targets = [
            {"target_id": "tolkien.people", "target_version": "1.0.0", "name": "Kirjailijat"},
            {"target_id": "tolkien.events", "target_version": "1.0.0", "name": "Tapahtumat"},
        ]
        self.reports = [
            {
                "target_id": "tolkien.people",
                "target_version": "1.0.0",
                "observation_types": ["news"],
                "period": {
                    "start": "2026-11-18T00:00:00+02:00",
                    "end": "2026-11-19T00:00:00+02:00",
                },
                "checked_at": "2026-11-19T09:00:00+02:00",
                "report_content": "Kirjailijoita koskeva raportti.",
            },
            {
                "target_id": "tolkien.events",
                "target_version": "1.0.0",
                "observation_types": ["events"],
                "period": {
                    "start": "2026-11-18T00:00:00+02:00",
                    "end": "2026-11-19T00:00:00+02:00",
                },
                "checked_at": "2026-11-19T09:01:00+02:00",
                "report_content": "Tapahtumia koskeva raportti.",
            },
        ]
        self.builder = ChatGPTRssCandidateBuilder(root=self.root)

    def tearDown(self):
        self.temp.cleanup()

    def build(self, reports=None):
        with (
            patch("scripts.chatgpt_rss_candidate.load_registry", return_value=self.registry),
            patch("scripts.chatgpt_rss_candidate.load_module_targets", return_value=self.targets),
        ):
            return self.builder(
                "tolkien",
                "tolkien-run-001",
                "",
                target_reports=reports or self.reports,
                publication_id="tolkien-feed",
                publication_metadata={"publication_assessment": assessment()},
                expected_feed_path="feeds/tolkien.xml",
                expected_public_url="https://mikknikk.github.io/aiheseurain/feeds/tolkien.xml",
            )

    def test_multiple_target_reports_form_one_feed_with_stable_unique_guids(self):
        first = self.build()
        second = self.build()
        self.assertEqual(len(first.report_guid_refs), 2)
        self.assertEqual(first.report_guid_refs, second.report_guid_refs)
        self.assertEqual(len(set(first.report_guid_refs)), 2)
        feed = ET.fromstring(first.files["feeds/tolkien.xml"])
        items = feed.findall("./channel/item")
        self.assertEqual(len(items), 2)
        self.assertEqual(
            {item.findtext("description") for item in items},
            {report["report_content"] for report in self.reports},
        )
        self.assertTrue(all(item.find("link") is None for item in items))
        self.assertEqual(
            len({item.findtext("guid") for item in items}),
            2,
        )
        gate = json.loads(first.files["reports/julkaisuportit/tolkien-run-001.json"])
        self.assertEqual(gate["decision"], "approved")
        self.assertEqual(gate["schema_version"], 2)

    def test_unknown_target_or_wrong_version_is_rejected(self):
        unknown = [dict(self.reports[0], target_id="another-module.private"), self.reports[1]]
        with self.assertRaises(GitHubAdapterError):
            self.build(unknown)
        wrong_version = [dict(self.reports[0], target_version="9.9.9"), self.reports[1]]
        with self.assertRaises(GitHubAdapterError):
            self.build(wrong_version)

    def test_unapproved_editorial_assessment_is_rejected(self):
        rejected = assessment()
        rejected["decision"] = "rejected"
        with (
            patch("scripts.chatgpt_rss_candidate.load_registry", return_value=self.registry),
            patch("scripts.chatgpt_rss_candidate.load_module_targets", return_value=self.targets),
        ):
            with self.assertRaises(ValueError):
                self.builder(
                    "tolkien", "tolkien-run-001", "",
                    target_reports=self.reports, publication_id="tolkien-feed",
                    publication_metadata={"publication_assessment": rejected},
                    expected_feed_path="feeds/tolkien.xml",
                    expected_public_url="https://mikknikk.github.io/aiheseurain/feeds/tolkien.xml",
                )


if __name__ == "__main__":
    unittest.main()
