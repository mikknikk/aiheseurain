"""Taylor Swift -varjotuloksen adapterin regressiotestit."""
from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
import jsonschema

from scripts.taylor_swift_shadow import prepare_taylor_swift_shadow, TaylorSwiftShadowError
from scripts.taylor_swift_shadow_result import validate_taylor_swift_shadow_result

ROOT = Path(__file__).resolve().parents[1]


class TaylorSwiftShadowResultTests(unittest.TestCase):
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
        self.preparation = prepare_taylor_swift_shadow(
            run_id="swift-shadow-20261120-01",
            period_start="2026-11-19T00:00:00+02:00",
            period_end="2026-11-19T23:59:59+02:00",
            requested_at="2026-11-20T12:00:00+02:00",
            root=self.root,
        )

    def tearDown(self):
        self.temp.cleanup()

    def payload(self):
        period = self.preparation["period"]
        return {
            "schema_version": 1,
            "module_id": "taylor-swift",
            "module_definition_version": "1.0.0",
            "contract_version": "1.0.0",
            "run_id": self.preparation["run_id"],
            "period": period,
            "status": "failed",
            "source_scan_complete": False,
            "checked_at": "2026-11-20T12:01:00+02:00",
            "handoff": {
                "dispatch_schema_version": 1,
                "module_id": "taylor-swift",
                "module_definition_version": "1.0.0",
                "contract_version": "1.0.0",
                "run_id": self.preparation["run_id"],
                "period": period,
                "requested_at": self.preparation["requested_at"],
                "input_sha256": self.preparation["handoff_input_sha256"],
            },
        }

    def test_failed_result_can_be_recorded_as_shadow_without_publication(self):
        result = validate_taylor_swift_shadow_result(
            self.preparation, self.payload(),
            approval_reference="user-approval-recorded-in-conversation",
            root=self.root,
        )
        self.assertEqual(result["artifact_type"], "taylor_swift_shadow_result")
        self.assertEqual(result["status"], "failed")
        self.assertTrue(result["research_performed"])
        self.assertFalse(result["publication_performed"])
        self.assertFalse(result["production_state_written"])
        schema = json.loads((ROOT / "schemas/taylor-swift-shadow-result.schema.json").read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator(
            schema, format_checker=jsonschema.FormatChecker()
        ).validate(result)

    def test_missing_separate_approval_reference_is_rejected(self):
        with self.assertRaises(TaylorSwiftShadowError):
            validate_taylor_swift_shadow_result(
                self.preparation, self.payload(), approval_reference="", root=self.root
            )

    def test_wrong_module_is_rejected(self):
        payload = self.payload()
        payload["module_id"] = "tolkien"
        with self.assertRaises(TaylorSwiftShadowError):
            validate_taylor_swift_shadow_result(
                self.preparation, payload, approval_reference="approval-1", root=self.root
            )

    def test_wrong_input_hash_is_rejected(self):
        payload = self.payload()
        payload["handoff"]["input_sha256"] = "0" * 64
        with self.assertRaises(TaylorSwiftShadowError):
            validate_taylor_swift_shadow_result(
                self.preparation, payload, approval_reference="approval-1", root=self.root
            )

    def test_other_target_report_is_rejected(self):
        payload = self.payload()
        payload["status"] = "succeeded"
        payload["source_scan_complete"] = True
        payload["target_reports"] = [{
            "target_id": "tolkien.j-r-r-tolkien",
            "target_version": "1.0.0",
            "observation_types": ["news"],
            "period": payload["period"],
            "checked_at": payload["checked_at"],
            "report_content": "Testiraportti",
        }]
        with self.assertRaises(TaylorSwiftShadowError):
            validate_taylor_swift_shadow_result(
                self.preparation, payload, approval_reference="approval-1", root=self.root
            )


if __name__ == "__main__":
    unittest.main()
