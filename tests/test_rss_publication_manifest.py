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
            self.assertEqual((root / "_rollback_snapshot/feeds/a.xml").read_bytes(), alpha)
            self.assertEqual((root / "_rollback_snapshot/feeds/b.xml").read_bytes(), beta)

    def test_rollback_source_overlays_live_snapshot_without_changing_other_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "old-source"
            (source / "feeds").mkdir(parents=True)
            (source / "index.html").write_text("old site", encoding="utf-8")
            (source / "feeds/a.xml").write_text("stale committed feed", encoding="utf-8")
            snapshot = root / "_rollback_snapshot/feeds"
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
        with patch.object(manifest.urllib.request, "urlopen", side_effect=lambda *args, **kwargs: io.BytesIO(wrong)), patch.object(
            manifest.time, "sleep"
        ):
            with self.assertRaises(manifest.PublicationError):
                manifest.verify_feeds([{
                    "public_url": "https://example.test/a.xml", "path": "feeds/a.xml",
                    "sha256": "0" * 64, "guids": ["expected-guid"], "item_count": 1
                }])


    def test_finalize_accepts_ambiguous_deploy_result_only_after_content_verification(self):
        from types import SimpleNamespace
        manifest_payload = {"manifest_type": "aiheseurain-rss-publication", "feeds": [{}]}
        with patch.dict("os.environ", {"GITHUB_SHA": "head"}), patch.object(
            manifest, "api", side_effect=[
                {"object": {"sha": "head"}}, {"payload": manifest_payload}
            ]
        ), patch.object(manifest, "status") as status:
            manifest.finalize(SimpleNamespace(
                deployment_id="123", is_current="true", deploy_outcome="failure",
                candidate_verified="true", rollback_outcome="skipped",
                rollback_verified="false"
            ))
        status.assert_called_once_with(123, "success", "Kaikki 1 syötettä täsmäävät SHA/GUID/item-tasolla.")

    def test_finalize_keeps_workflow_failed_after_successful_rollback(self):
        from types import SimpleNamespace
        manifest_payload = {"manifest_type": "aiheseurain-rss-publication", "feeds": [{}]}
        with patch.dict("os.environ", {"GITHUB_SHA": "head"}), patch.object(
            manifest, "api", side_effect=[
                {"object": {"sha": "head"}}, {"payload": manifest_payload}
            ]
        ), patch.object(manifest, "status") as status:
            with self.assertRaises(manifest.PublicationError):
                manifest.finalize(SimpleNamespace(
                    deployment_id="123", is_current="true", deploy_outcome="success",
                    candidate_verified="false", rollback_outcome="success",
                    rollback_verified="true"
                ))
        status.assert_called_once_with(
            123, "failure", "Ehdokas hylättiin; aiempi varmennettu RSS-versio palautettiin."
        )

    def test_pages_workflow_contains_separate_verified_rollback_artifact(self):
        workflow = (manifest.ROOT / ".github/workflows/publish-pages.yml").read_text(encoding="utf-8")
        self.assertIn("name: github-pages-rollback", workflow)
        self.assertIn("artifact_name: github-pages-rollback", workflow)
        self.assertIn("steps.candidate_check.outputs.candidate_verified == 'false'", workflow)
        self.assertIn("verify-rollback", workflow)


    def test_existing_deployment_is_reused_for_same_workflow_run(self):
        payload = {
            "manifest_type": "aiheseurain-rss-publication",
            "workflow_run_id": "777", "source_commit": "a" * 40,
            "base_commit": "b" * 40
        }
        with patch.object(manifest, "api", return_value=[{"id": 456, "payload": payload}]) as api:
            found = manifest.find_existing_deployment("a" * 40, "b" * 40, "777")
        self.assertEqual(found, {"id": 456, "payload": payload})
        api.assert_called_once()

    def test_snapshot_validation_rejects_changed_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            folder = root / "_rollback_snapshot/feeds"
            folder.mkdir(parents=True)
            data = b'<rss><channel><item><guid>saved</guid></item></channel></rss>'
            (folder / "a.xml").write_bytes(data)
            expected = [{
                "path": "feeds/a.xml", "sha256": "0" * 64,
                "size_bytes": len(data), "guids": ["saved"], "item_count": 1
            }]
            with patch.object(manifest, "ROOT", root):
                with self.assertRaises(manifest.PublicationError):
                    manifest.validate_snapshot_files(expected)

    def test_deployment_status_write_is_idempotent(self):
        with patch.dict("os.environ", {
            "GITHUB_REPOSITORY": "mikknikk/aiheseurain",
            "GITHUB_RUN_ID": "777"
        }), patch.object(manifest, "api", return_value=[{
            "state": "failure",
            "description": "Ehdokas hylättiin; aiempi varmennettu RSS-versio palautettiin."
        }]) as api:
            manifest.status(123, "failure", "Ehdokas hylättiin; aiempi varmennettu RSS-versio palautettiin.")
        api.assert_called_once_with("GET", "deployments/123/statuses?per_page=1")

    def test_failure_alert_does_not_create_duplicate_issue(self):
        from types import SimpleNamespace
        with patch.dict("os.environ", {
            "GITHUB_REPOSITORY": "mikknikk/aiheseurain",
            "GITHUB_RUN_ID": "777"
        }), patch.object(manifest, "load_manifest", return_value={"source_commit": "a" * 40}), patch.object(
            manifest, "api", return_value=[{
                "number": 42,
                "title": "RSS-julkaisun palautus vaatii huomiota - ajo 777"
            }]
        ) as api:
            manifest.alert_failure(SimpleNamespace(deployment_id="123"))
        api.assert_called_once_with("GET", "issues?state=all&per_page=100")

    def test_production_pages_workflow_serializes_runs_and_keeps_snapshot_for_retries(self):
        workflow = (manifest.ROOT / ".github/workflows/publish-pages.yml").read_text(encoding="utf-8")
        self.assertIn("group: ${{ github.event_name", workflow)
        self.assertIn("cancel-in-progress: false", workflow)
        self.assertIn("name: rss-rollback-snapshot", workflow)
        self.assertIn("actions/download-artifact@v4", workflow)
        self.assertIn("alert-failure", workflow)

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


class RssPublicationFaultInjectionTests(unittest.TestCase):
    """Julkaisuketjun virhetilanteiden eristetyt fault-injection-testit."""

    def test_snapshot_stops_before_manifest_when_one_public_feed_is_unavailable(self):
        import io
        feeds = [
            {"feed_id": "a", "path": "feeds/a.xml", "public_url": "https://example.test/a.xml"},
            {"feed_id": "b", "path": "feeds/b.xml", "public_url": "https://example.test/b.xml"},
        ]
        valid = b'<rss><channel><item><guid>a</guid></item></channel></rss>'
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(manifest, "ROOT", Path(directory)), patch.object(
                manifest.urllib.request, "urlopen",
                side_effect=[io.BytesIO(valid), manifest.urllib.error.URLError("simulated outage")]
            ), patch.object(manifest, "api") as api:
                with self.assertRaises(manifest.PublicationError):
                    manifest.snapshot_live_feeds(feeds)
                api.assert_not_called()

    def test_candidate_verification_failure_is_reported_as_false_without_masking_workflow(self):
        from types import SimpleNamespace
        with patch.object(manifest, "load_manifest", side_effect=manifest.PublicationError("simulated API outage")), \\
             patch.object(manifest, "output") as output:
            manifest.verify_candidate(SimpleNamespace(deployment_id="123"))
        output.assert_called_once_with("candidate_verified", "false")

    def test_rollback_verification_failure_is_reported_as_false(self):
        from types import SimpleNamespace
        with patch.object(manifest, "load_manifest", return_value={"rollback_feeds": []}), \\
             patch.object(manifest, "verify_feeds", side_effect=manifest.PublicationError("simulated CDN mismatch")), \\
             patch.object(manifest, "output") as output:
            manifest.verify_rollback(SimpleNamespace(deployment_id="123"))
        output.assert_called_once_with("rollback_verified", "false")

    def test_snapshot_http_failure_does_not_return_a_partial_manifest(self):
        import io
        valid = b'<rss><channel><item><guid>one</guid></item></channel></rss>'
        feeds = [
            {"feed_id": "one", "path": "feeds/one.xml", "public_url": "https://example.test/one.xml"},
            {"feed_id": "two", "path": "feeds/two.xml", "public_url": "https://example.test/two.xml"},
        ]
        with tempfile.TemporaryDirectory() as directory, patch.object(
            manifest, "ROOT", Path(directory)
        ), patch.object(manifest.urllib.request, "urlopen", side_effect=[
            io.BytesIO(valid), manifest.urllib.error.URLError("simulated DNS failure")
        ]):
            with self.assertRaises(manifest.PublicationError):
                manifest.snapshot_live_feeds(feeds)
            saved = Path(directory) / "_rollback_snapshot/feeds/one.xml"
            self.assertTrue(saved.is_file())
            # A partial directory is not sufficient: the caller receives no complete manifest.
            self.assertFalse((Path(directory) / "_rollback_snapshot/feeds/two.xml").exists())

    def test_rollback_assembly_rejects_missing_snapshot_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            source.mkdir()
            (root / "_rollback_snapshot/feeds").mkdir(parents=True)
            catalog = root / "catalog.json"
            catalog.write_text(json.dumps({"feeds": [
                {"id": "missing", "path": "feeds/missing.xml"}
            ]}), encoding="utf-8")
            class Args:
                source_dir = str(source)
                destination_dir = str(root / "destination")
            with patch.object(manifest, "ROOT", root), patch.object(manifest, "CATALOG", catalog):
                with self.assertRaises(manifest.PublicationError):
                    manifest.assemble_rollback(Args())

    def test_github_api_timeout_is_converted_to_publication_error(self):
        from urllib.error import URLError
        with patch.dict("os.environ", {
            "GITHUB_TOKEN": "test-token", "GITHUB_REPOSITORY": "owner/repo"
        }), patch.object(manifest.urllib.request, "urlopen", side_effect=URLError("simulated timeout")):
            with self.assertRaises(manifest.PublicationError):
                manifest.api("POST", "deployments", {"ref": "abc"})

    def test_status_write_failure_is_not_silently_accepted(self):
        with patch.dict("os.environ", {
            "GITHUB_REPOSITORY": "owner/repo", "GITHUB_RUN_ID": "123"
        }), patch.object(manifest, "api", side_effect=[
            [], manifest.PublicationError("simulated status API failure")
        ]):
            with self.assertRaises(manifest.PublicationError):
                manifest.status(456, "failure", "simulated")

    def test_main_head_advance_prevents_stale_publication(self):
        from types import SimpleNamespace
        with patch.object(manifest, "api", return_value={"object": {"sha": "new-head"}}), \\
             patch.object(manifest, "output") as output:
            manifest.check_current(SimpleNamespace(source_commit="old-head"))
        output.assert_called_once_with("is_current", "false")

    def test_fault_matrix_documents_all_publication_boundaries(self):
        workflow = (manifest.ROOT / ".github/workflows/publish-pages.yml").read_text(encoding="utf-8")
        for boundary in (
            "prepare_manifest", "upload-artifact@v4", "upload-pages-artifact@v3",
            "deploy-pages@v4", "candidate_check", "rollback_deployment",
            "rollback_check", "finalize", "alert-failure"
        ):
            self.assertIn(boundary, workflow)


if __name__ == "__main__":
    unittest.main()
