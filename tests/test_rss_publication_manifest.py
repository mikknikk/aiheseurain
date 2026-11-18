"""RSS-julkaisumanifestin offline-yksikkötestit."""
import json
from pathlib import Path
import tempfile
import unittest
import jsonschema
from unittest.mock import patch

from scripts import rss_publication_manifest as manifest


class RssPublicationManifestTests(unittest.TestCase):
    def test_manifest_schema_is_valid_json_schema(self):
        schema = json.loads(manifest.SCHEMA.read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator.check_schema(schema)

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


    def test_snapshot_records_exact_public_feed_bytes(self):
        import io
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            alpha = b'<rss><channel><item><guid>live-a</guid></item></channel></rss>'
            beta = b'<rss><channel><item><guid>live-b</guid></item></channel></rss>'
            responses = [io.BytesIO(alpha), io.BytesIO(beta)]
            feeds = [
                {"feed_id": "a", "path": "feeds/a.xml", "public_url": "https://example.test/a.xml"},
                {"feed_id": "b", "path": "feeds/b.xml", "public_url": "https://example.test/b.xml"},
            ]
            with patch.object(manifest, "ROOT", root), patch.object(
                manifest.urllib.request, "urlopen", side_effect=responses
            ):
                saved = manifest.snapshot_live_feeds(feeds)
            self.assertEqual([item["sha256"] for item in saved],
                             [manifest.digest(alpha), manifest.digest(beta)])
            self.assertEqual((root / "rollback_snapshot/feeds/a.xml").read_bytes(), alpha)
            self.assertEqual((root / "rollback_snapshot/feeds/b.xml").read_bytes(), beta)

    def test_rollback_source_overlays_live_snapshot_without_changing_other_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "old-source"
            (source / "feeds").mkdir(parents=True)
            (source / "index.html").write_text("old site", encoding="utf-8")
            (source / "feeds/a.xml").write_text("stale committed feed", encoding="utf-8")
            snapshot = root / "rollback_snapshot/feeds"
            snapshot.mkdir(parents=True)
            live = b'<rss><channel><item><guid>last-live-guid</guid></item></channel></rss>'
            (snapshot / "a.xml").write_bytes(live)
            catalog = root / "data"
            catalog.mkdir()
            (catalog / "feed-catalog.json").write_text(json.dumps({
                "feeds": [{"id": "a", "path": "feeds/a.xml"}]
            }), encoding="utf-8")
            class Args:
                source_dir = str(source)
                destination_dir = str(root / "rollback-source")
            with patch.object(manifest, "ROOT", root), patch.object(
                manifest, "CATALOG", catalog / "feed-catalog.json"
            ):
                manifest.assemble_rollback(Args())
            self.assertEqual((root / "rollback-source/index.html").read_text(encoding="utf-8"), "old site")
            self.assertEqual((root / "rollback-source/feeds/a.xml").read_bytes(), live)

    def test_verify_feeds_rejects_hash_mismatch_without_long_wait(self):
        import io
        wrong = b'<rss><channel><item><guid>wrong-guid</guid></item></channel></rss>'
        with patch.object(manifest.urllib.request, "urlopen", return_value=io.BytesIO(wrong)), patch.object(
            manifest.time, "sleep"
        ):
            with self.assertRaises(manifest.PublicationError):
                manifest.verify_feeds([{
                    "public_url": "https://example.test/a.xml", "path": "feeds/a.xml",
                    "sha256": "0" * 64, "guids": ["expected-guid"], "item_count": 1
                }])

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
