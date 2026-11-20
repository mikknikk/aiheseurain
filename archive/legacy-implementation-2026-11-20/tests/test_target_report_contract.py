"""Kohdekohtaisen raporttisopimuksen ja laadunvarmistuksen testit."""
from __future__ import annotations

import unittest

from scripts.module_orchestrator import ModuleExecutionOutput, ModuleRunRequest, TargetReport
from scripts.module_run_adapters import StructuralModuleQualityGate
from scripts.module_registry import load_registry
from examples.target_reports.two_target_reports import build_two_target_example


NOW = "2026-11-18T23:00:00+02:00"
START = "2026-11-18T00:00:00+02:00"
END = "2026-11-18T22:59:59+02:00"


def module_definition():
    """Lataa oikea, mutta tuotantotilaltaan passiivinen Tolkien-moduulimäärittely."""
    registry = load_registry(include_inactive=True)
    return next(item.definition for item in registry.modules if item.module_id == "tolkien")


def request():
    """Muodosta yhden testiajon vakaa suorituspyyntö."""
    definition = module_definition()
    return ModuleRunRequest(
        module_id="tolkien",
        module_definition_version=definition["definition_version"],
        contract_version=definition["contract_version"],
        run_id="target-report-test-01",
        period_start=START,
        period_end=END,
        mode="shadow",
        requested_at=NOW,
    )


def report(target_id, *, version="1.0.0", types=("report.article",),
           start=START, end=END, checked_at=NOW, content="<p>Raportti</p>"):
    """Rakenna testiin yksi kohderaportti."""
    return TargetReport(
        target_id=target_id, target_version=version,
        observation_types=types, period_start=start, period_end=end,
        checked_at=checked_at, report_content=content,
    )


def output(reports, *, content=""):
    """Rakenna onnistunut suorittajan tulos ilman moduulikohtaista raporttia."""
    return ModuleExecutionOutput(
        status="succeeded", source_scan_complete=True, checked_at=NOW,
        period_start=START, period_end=END, report_content=content,
        target_reports=tuple(reports),
    )


class TargetReportContractTests(unittest.TestCase):
    def setUp(self):
        self.definition = module_definition()
        self.request = request()
        self.gate = StructuralModuleQualityGate()

    def test_example_executor_produces_two_valid_target_reports(self):
        result = build_two_target_example(self.request)
        quality = self.gate.validate(self.definition, self.request, result)
        self.assertTrue(quality.passed, quality.errors)
        self.assertEqual(
            {item.target_id for item in result.target_reports},
            {"tolkien.j-r-r-tolkien", "tolkien.tolkien-estate"},
        )
        self.assertEqual(len(result.target_reports), 2)

    def test_unknown_target_is_rejected(self):
        result = output([report("tolkien.unknown")])
        quality = self.gate.validate(self.definition, self.request, result)
        self.assertFalse(quality.passed)
        self.assertTrue(any("ei kuulu moduulille" in error for error in quality.errors))

    def test_duplicate_target_reports_are_rejected(self):
        result = output([
            report("tolkien.j-r-r-tolkien"),
            report("tolkien.j-r-r-tolkien"),
        ])
        quality = self.gate.validate(self.definition, self.request, result)
        self.assertFalse(quality.passed)
        self.assertTrue(any("useampi raportti samalle" in error for error in quality.errors))

    def test_wrong_target_version_is_rejected(self):
        result = output([report("tolkien.j-r-r-tolkien", version="2.0.0")])
        quality = self.gate.validate(self.definition, self.request, result)
        self.assertFalse(quality.passed)
        self.assertTrue(any("kohdeversio" in error for error in quality.errors))

    def test_unsupported_observation_type_is_rejected(self):
        result = output([report("tolkien.j-r-r-tolkien", types=("film-screening",))])
        quality = self.gate.validate(self.definition, self.request, result)
        self.assertFalse(quality.passed)
        self.assertTrue(any("havaintotyyppi" in error for error in quality.errors))

    def test_period_mismatch_is_rejected(self):
        result = output([report("tolkien.j-r-r-tolkien", start="2026-11-17T00:00:00+02:00")])
        quality = self.gate.validate(self.definition, self.request, result)
        self.assertFalse(quality.passed)
        self.assertTrue(any("seurantajakso" in error for error in quality.errors))

    def test_missing_report_content_is_rejected(self):
        result = output([report("tolkien.j-r-r-tolkien", content="  ")])
        quality = self.gate.validate(self.definition, self.request, result)
        self.assertFalse(quality.passed)
        self.assertTrue(any("sisältö puuttuu" in error for error in quality.errors))

    def test_legacy_module_report_remains_supported(self):
        result = ModuleExecutionOutput(
            status="succeeded", source_scan_complete=True, checked_at=NOW,
            period_start=START, period_end=END, report_content="<p>Vanha raportti</p>",
        )
        quality = self.gate.validate(self.definition, self.request, result)
        self.assertTrue(quality.passed, quality.errors)


if __name__ == "__main__":
    unittest.main()
