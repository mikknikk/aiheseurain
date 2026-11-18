"""RSS-julkaisumanifestin offline-yksikkötestit."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import rss_publication_manifest as manifest


class RssPublicationManifestTests(unittest.TestCase):
    def test_rss_metadata_requires_unique_guid_values(self):
        xml = b'<rss><channel><item><guid>a</guid></item><item><guid>b</guid></item></channel></rss>'
        self.assertEqual(manifest.rss_metadata(xml, "test.xml"), (["a", "b"], 2))
        duplicate = b'<rss><channel><item><guid>a</guid></item><item><guid>a</guid></item></channel></rss>'
        with self.assertRaises(manifest.PublicationError):
            manifest.rss_metadata(duplicate, "test.xml")

    def test_rss_metadata_rejects_malformed_xml(self):
        with self.assertRaises(manifest.PublicationError):
            manifest.rss_metadata(b"<rss><channel>", "test.xml")

    def test_build_manifest_captures_all_feeds_and_only_changed_feed_report(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "data").mkdir()
            (root / "feeds").mkdir()
            (root / "reports/julkaisuportit").mkdir(parents=True)
            (root / "data/feed-catalog.json").write_text(json.dumps({
                "feeds": [
                    {"id": "alpha", "path": "feeds/alpha.xml"},
                    {"id": "beta", "path": "feeds/beta.xml"},
                ]
            }), encoding="utf-8")
            alpha = b'<rss><channel><item><guid>alpha-guid</guid></item></channel></rss>'
            beta = b'<rss><channel><item><guid>beta-guid</guid></item></channel></rss>'
            (root / "feeds/alpha.xml").write_bytes(alpha)
            (root / "feeds/beta.xml").write_bytes(beta)
            report = {"decision": "approved", "feed_path": "feeds/alpha.xml", "run_id": "alpha-run-001"}
            report_path = root / "reports/julkaisuportit/alpha-run-001.json"
            report_path.write_text(json.dumps(report), encoding="utf-8")
            with patch.object(manifest, "ROOT", root), \
                 patch.object(manifest, "CATALOG", root / "data/feed-catalog.json"), \
                 patch.object(manifest, "git_changed_files", return_value={
                     "feeds/alpha.xml", "reports/julkaisuportit/alpha-run-001.json"
                 }):
                result = manifest.build_manifest("base-sha", "head-sha", "123", "1")
            self.assertEqual(result["phase"], "prepared")
            self.assertEqual(result["source_commit"], "head-sha")
            self.assertEqual(len(result["feeds"]), 2)
            changed = next(item for item in result["feeds"] if item["path"] == "feeds/alpha.xml")
            unchanged = next(item for item in result["feeds"] if item["path"] == "feeds/beta.xml")
            self.assertTrue(changed["changed_in_commit"])
            self.assertEqual(changed["report_run_id"], "alpha-run-001")
            self.assertFalse(unchanged["changed_in_commit"])
            self.assertIsNone(unchanged["report_run_id"])
            self.assertEqual(changed["sha256"], manifest.digest(alpha))
            self.assertEqual(changed["guids"], ["alpha-guid"])

    def test_build_manifest_refuses_missing_or_rejected_report(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "data").mkdir()
            (root / "feeds").mkdir()
            (root / "data/feed-catalog.json").write_text(json.dumps({
                "feeds": [{"id": "alpha", "path": "feeds/alpha.xml"}]
            }), encoding="utf-8")
            (root / "feeds/alpha.xml").write_text(
                '<rss><channel><item><guid>alpha-guid</guid></item></channel></rss>',
                encoding="utf-8")
            with patch.object(manifest, "ROOT", root), \
                 patch.object(manifest, "CATALOG", root / "data/feed-catalog.json"), \
                 patch.object(manifest, "git_changed_files", return_value={"feeds/alpha.xml"}):
                with self.assertRaises(manifest.PublicationError):
                    manifest.build_manifest("base", "head", "123", "1")


if __name__ == "__main__":
    unittest.main()
