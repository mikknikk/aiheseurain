"""Seurantakohteiden yhteisen suorituskehyksen testit."""
from __future__ import annotations

import unittest

from scripts.module_orchestrator import ModuleRunRequest
from scripts.module_registry import load_registry
from scripts.module_run_adapters import StructuralModuleQualityGate
from scripts.target_execution import (
    TargetExecutionContext, TargetExecutionCoordinator, TargetExecutionError,
    TargetExecutionResult, load_module_targets,
)
from examples.target_reports.coordinator_demo import build_example_output


NOW = "2026-11-18T23:00:00+02:00"
START = "2026-11-18T00:00:00+02:00"
END = "2026-11-18T22:59:59+02:00"


def module_definition():
    registry = load_registry(include_inactive=True)
    return next(item.definition for item in registry.modules if item.module_id == "tolkien")


def request(mode="shadow"):
    definition = module_definition()
    return ModuleRunRequest(
        module_id="tolkien", module_definition_version=definition["definition_version"],
        contract_version=definition["contract_version"], run_id="target-coordinator-run",
        period_start=START, period_end=END, mode=mode, requested_at=NOW,
    )


def fake_targets():
    """Kaksi erillistä testikohdetta eri hakuprofiileilla."""
    return (
        {
            "target_id": "demo.first", "target_version": "1.0.0",
            "search_profiles": [{"id": "first-profile", "query_terms": ["ensimmäinen"]}],
        },
        {
            "target_id": "demo.second", "target_version": "2.0.0",
            "search_profiles": [{"id": "second-profile", "query_terms": ["toinen"]}],
        },
    )


class FakeRunner:
    def __init__(self, fail_target=None):
        self.fail_target = fail_target
        self.seen = []

    def execute(self, context: TargetExecutionContext, provider_router):
        self.seen.append((context.target_id, context.search_profiles[0]["id"]))
        if context.target_id == self.fail_target:
            raise RuntimeError("test runner failed")
        return TargetExecutionResult(
            status="succeeded", source_scan_complete=True,
            checked_at=NOW, observation_types=("report.article",),
            report_content=f"<p>{context.target_id}</p>",
            sources_checked=1, source_check_run_refs=(f"check-{context.target_id}",),
        )


class TargetExecutionFrameworkTests(unittest.TestCase):
    def test_module_targets_load_from_registry_and_match_refs(self):
        targets = load_module_targets(module_definition())
        self.assertEqual(
            {item["target_id"] for item in targets},
            {"tolkien.j-r-r-tolkien", "tolkien.tolkien-estate"},
        )

    def test_two_targets_get_isolated_profiles_and_two_reports(self):
        runner = FakeRunner()
        coordinator = TargetExecutionCoordinator(target_loader=lambda definition, **kwargs: fake_targets())
        definition = {
            "module_id": "tolkien", "definition_version": "1.0.0",
            "target_refs": ["demo.first", "demo.second"],
        }
        output = coordinator.execute(definition, request(), None, runner)
        self.assertEqual(output.status, "succeeded")
        self.assertTrue(output.source_scan_complete)
        self.assertEqual(len(output.target_reports), 2)
        self.assertEqual(
            runner.seen,
            [("demo.first", "first-profile"), ("demo.second", "second-profile")],
        )
        self.assertEqual({item.target_id for item in output.target_reports},
                         {"demo.first", "demo.second"})

    def test_target_context_is_immutable(self):
        class MutatingRunner(FakeRunner):
            def execute(self, context, provider_router):
                with self.assertRaises(TypeError):
                    context.target_definition["name"] = "Muutettu"
                return super().execute(context, provider_router)

        runner = MutatingRunner()
        coordinator = TargetExecutionCoordinator(target_loader=lambda definition, **kwargs: fake_targets())
        definition = {"module_id": "tolkien", "definition_version": "1.0.0",
                     "target_refs": ["demo.first", "demo.second"]}
        output = coordinator.execute(definition, request(), None, runner)
        self.assertEqual(output.status, "succeeded")

    def test_one_target_failure_is_isolated_and_marks_run_partial(self):
        runner = FakeRunner(fail_target="demo.second")
        coordinator = TargetExecutionCoordinator(target_loader=lambda definition, **kwargs: fake_targets())
        definition = {"module_id": "tolkien", "definition_version": "1.0.0",
                     "target_refs": ["demo.first", "demo.second"]}
        output = coordinator.execute(definition, request(), None, runner)
        self.assertEqual(output.status, "partial")
        self.assertFalse(output.source_scan_complete)
        self.assertEqual([item.target_id for item in output.target_reports], ["demo.first"])
        self.assertEqual(output.metadata["failed_targets"], {"demo.second": "RuntimeError"})

    def test_missing_module_target_reference_is_rejected(self):
        definition = module_definition()
        definition["target_refs"] = ["tolkien.missing"]
        with self.assertRaises(TargetExecutionError):
            load_module_targets(definition)

    def test_duplicate_module_target_reference_is_rejected(self):
        definition = module_definition()
        definition["target_refs"] = [definition["target_refs"][0], definition["target_refs"][0]]
        with self.assertRaises(TargetExecutionError):
            load_module_targets(definition)

    def test_inactive_targets_cannot_run_in_production_mode(self):
        runner = FakeRunner()
        with self.assertRaises(TargetExecutionError):
            TargetExecutionCoordinator().execute(module_definition(), request("production"), None, runner)
        self.assertEqual(runner.seen, [])

    def test_example_output_passes_target_report_quality_gate(self):
        definition = module_definition()
        req = request()
        output = build_example_output(req)
        quality = StructuralModuleQualityGate().validate(definition, req, output)
        self.assertTrue(quality.passed, quality.errors)
        self.assertEqual(len(output.target_reports), 2)


if __name__ == "__main__":
    unittest.main()
