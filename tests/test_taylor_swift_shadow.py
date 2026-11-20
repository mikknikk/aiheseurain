"""Taylor Swift -varjoharjoituksen valmisteluporttien regressiotestit."""
from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
import jsonschema
import xml.etree.ElementTree as ET

from scripts.taylor_swift_shadow import (
    TaylorSwiftShadowError,
    prepare_taylor_swift_shadow,
    write_shadow_artifact,
)

ROOT = Path(__file__).resolve().parents[1]


class TaylorSwiftShadowPreparationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        for relative in (
            "data/module-registry.json", "data/target-registry.json",
            "data/targets/taylor-swift.taylor-swift.json",
            "data/sources/taylor_swift.json", "data/source-catalog.json",
            "data/feed-catalog.json", "data/module-production-activation.json",
            "data/publication-registry.json", "data/publication-routing.json",
            "data/module-state/taylor-swift.json", "feeds/taylor-swift.xml",
        ):
            source = ROOT / relative
            destination = self.root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(source.read_bytes())

    def tearDown(self):
        self.temp.cleanup()

    def prepare(self, **overrides):
        args = {
            "run_id": "swift-shadow-20261120-01",
            "period_start": "2026-11-19T00:00:00+02:00",
            "period_end": "2026-11-19T23:59:59+02:00",
            "requested_at": "2026-11-20T12:00:00+02:00",
            "root": self.root,
        }
        args.update(overrides)
        return prepare_taylor_swift_shadow(**args)

    def edit_json(self, relative, mutate):
        path = self.root / relative
        value = json.loads(path.read_text(encoding="utf-8"))
        mutate(value)
        path.write_text(json.dumps(value), encoding="utf-8")

    def test_preparation_uses_separate_empty_baseline_and_does_not_write(self):
        before = (self.root / "data/module-state/taylor-swift.json").read_bytes()
        result = self.prepare()
        self.assertEqual(result["status"], "prepared")
        self.assertFalse(result["execution_authorized"])
        self.assertFalse(result["research_performed"])
        self.assertFalse(result["publication_performed"])
        self.assertFalse(result["production_state_written"])
        self.assertEqual(result["baseline"]["kind"], "isolated_empty_shadow_baseline")
        self.assertFalse(result["baseline"]["historical_checkpoint_reference"]["used_as_baseline"])
        self.assertEqual(before, (self.root / "data/module-state/taylor-swift.json").read_bytes())
        self.assertFalse((self.root / "data/shadow-exercises").exists())

    def test_preparation_matches_its_json_schema(self):
        result = self.prepare()
        schema = json.loads((ROOT / "schemas/taylor-swift-shadow-preparation.schema.json").read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator(
            schema, format_checker=jsonschema.FormatChecker()
        ).validate(result)

    def test_only_taylor_swift_topic_module_is_accepted(self):
        self.edit_json("data/module-registry.json", lambda d: d["modules"][7].update({"module_type": "process"}))
        with self.assertRaises(TaylorSwiftShadowError):
            self.prepare()

    def test_production_activation_must_be_explicitly_false(self):
        self.edit_json("data/module-production-activation.json",
                       lambda d: d["modules"].update({"taylor-swift": True}))
        with self.assertRaises(TaylorSwiftShadowError):
            self.prepare()

    def test_target_ownership_mismatch_blocks_preparation(self):
        self.edit_json("data/targets/taylor-swift.taylor-swift.json",
                       lambda d: d["module_ref"].update({"module_id": "tolkien"}))
        with self.assertRaises(TaylorSwiftShadowError):
            self.prepare()

    def test_missing_source_reference_blocks_preparation(self):
        self.edit_json("data/sources/taylor_swift.json",
                       lambda d: d["sources"].pop())
        with self.assertRaises(TaylorSwiftShadowError):
            self.prepare()

    def test_nonempty_publication_route_blocks_preparation(self):
        self.edit_json("data/publication-routing.json",
                       lambda d: d["routes"].append({"module_id": "taylor-swift"}))
        with self.assertRaises(TaylorSwiftShadowError):
            self.prepare()

    def test_invalid_or_reversed_period_blocks_preparation(self):
        with self.assertRaises(TaylorSwiftShadowError):
            self.prepare(period_start="2026-11-19T00:00:00", period_end="2026-11-19T23:59:59+02:00")
        with self.assertRaises(TaylorSwiftShadowError):
            self.prepare(period_start="2026-11-20T00:00:00+02:00",
                         period_end="2026-11-19T00:00:00+02:00")

    def test_same_period_feed_date_is_conservatively_blocked(self):
        feed = self.root / "feeds/taylor-swift.xml"
        feed.write_text(
            '<rss version="2.0"><channel><item><guid>urn:test:2026-11-19:item</guid></item></channel></rss>',
            encoding="utf-8",
        )
        with self.assertRaises(TaylorSwiftShadowError):
            self.prepare()

    def test_bad_run_id_is_rejected(self):
        with self.assertRaises(TaylorSwiftShadowError):
            self.prepare(run_id="../other")

    def test_shadow_artifact_is_module_scoped_and_never_overwritten(self):
        artifact = self.prepare()
        path = write_shadow_artifact(self.root, artifact, kind="prepared")
        self.assertEqual(path.relative_to(self.root).as_posix(),
                         "data/shadow-exercises/taylor-swift/swift-shadow-20261120-01/prepared.json")
        with self.assertRaises(TaylorSwiftShadowError):
            write_shadow_artifact(self.root, artifact, kind="prepared")
        artifact["module_id"] = "tolkien"
        with self.assertRaises(TaylorSwiftShadowError):
            write_shadow_artifact(self.root, artifact, kind="prepared")

    def test_result_artifact_cannot_be_written_as_preparation(self):
        artifact = self.prepare()
        artifact["artifact_type"] = "taylor_swift_shadow_result"
        with self.assertRaises(TaylorSwiftShadowError):
            write_shadow_artifact(self.root, artifact, kind="prepared")


if __name__ == "__main__":
    unittest.main()
