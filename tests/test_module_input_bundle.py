"""Testaa aihekohtaisen syötepaketin sisältörajaus ja omistajuus."""
import json
from pathlib import Path
import unittest
from jsonschema import Draft202012Validator
from scripts.module_input_bundle import ModuleInputBundleError, build_module_input_bundle, bundle_to_json

ROOT = Path(__file__).resolve().parents[1]


class ModuleInputBundleTests(unittest.TestCase):
    def build(self):
        return build_module_input_bundle(
            "tolkien", task_id="tolkien", run_id="isolation-test-001",
            period_start="2026-11-18T00:00:00+02:00",
            period_end="2026-11-18T23:59:59+02:00", root=ROOT)

    def test_bundle_contains_only_own_sources_targets_and_state(self):
        bundle = self.build()
        self.assertEqual(bundle["module_id"], "tolkien")
        self.assertTrue(all(item["module_ref"]["module_id"] == "tolkien" for item in bundle["targets"]))
        allowed = {ref["source_id"] for ref in bundle["module"]["source_refs"]}
        self.assertEqual({item["module_reference"]["source_id"] for item in bundle["sources"]}, allowed)
        serialized = bundle_to_json(bundle)
        self.assertNotIn("indian-film-screening-watch", serialized)
        self.assertNotIn("data/seurantatila.json", serialized)
        self.assertNotIn('"references"', serialized)
        schema = json.loads((ROOT / "schemas/module-input-bundle.schema.json").read_text(encoding="utf-8"))
        Draft202012Validator(schema, format_checker=Draft202012Validator.FORMAT_CHECKER).validate(json.loads(serialized))

    def test_bundle_is_recursively_read_only(self):
        bundle = self.build()
        with self.assertRaises(TypeError):
            bundle["module_id"] = "muumit"
        with self.assertRaises(TypeError):
            bundle["module"]["name"] = "Muutettu"

    def test_wrong_task_source_registry_is_rejected(self):
        with self.assertRaises(ModuleInputBundleError):
            build_module_input_bundle(
                "tolkien", task_id="muumit", run_id="isolation-test-002",
                period_start="2026-11-18T00:00:00+02:00",
                period_end="2026-11-18T23:59:59+02:00", root=ROOT)

    def test_runner_input_does_not_include_repository_wide_registries(self):
        serialized = bundle_to_json(self.build())
        self.assertNotIn('"modules"', serialized)
        self.assertNotIn('"references"', serialized)
        self.assertNotIn('"migration"', serialized)


if __name__ == "__main__":
    unittest.main()
