"""Testaa ChatGPT-tuloksen moduuli- ja kohdekohtainen laadunvarmistus."""
from pathlib import Path
import unittest

from scripts.chatgpt_result_quality import ChatGPTResultQualityGate
from scripts.module_orchestrator import ModuleExecutionOutput, ModuleRunRequest, TargetReport
from scripts.module_registry import load_registry
from scripts.target_execution import load_module_targets

ROOT = Path(__file__).resolve().parents[1]


class ChatGPTResultQualityTests(unittest.TestCase):
    def setUp(self):
        registry = load_registry(root=ROOT, include_inactive=True)
        self.definition = registry.modules["muumit"].definition
        self.targets = load_module_targets(self.definition, root=ROOT, require_active=False)
        self.request = ModuleRunRequest(
            module_id="muumit",
            module_definition_version=self.definition["definition_version"],
            contract_version=self.definition["contract_version"],
            run_id="muumit-quality-001",
            period_start="2026-11-18T00:00:00+02:00",
            period_end="2026-11-19T00:00:00+02:00",
            mode="shadow",
            requested_at="2026-11-19T09:00:00+02:00",
        )
        self.gate = ChatGPTResultQualityGate(root=ROOT)
        self.reports = tuple(
            TargetReport(
                target_id=target["target_id"],
                target_version=target["target_version"],
                observation_types=("news",),
                period_start=self.request.period_start,
                period_end=self.request.period_end,
                checked_at="2026-11-19T09:30:00+02:00",
                report_content=f"Raportti kohteesta {target['target_id']}.",
            )
            for target in self.targets
        )

    def output(self, **changes):
        values = {
            "status": "succeeded",
            "source_scan_complete": True,
            "checked_at": "2026-11-19T09:30:00+02:00",
            "period_start": self.request.period_start,
            "period_end": self.request.period_end,
            "report_content": "",
            "sources_checked": 0,
            "target_reports": self.reports,
        }
        values.update(changes)
        return ModuleExecutionOutput(**values)

    def test_all_owned_target_reports_pass_without_numeric_source_threshold(self):
        result = self.gate.validate(self.definition, self.request, self.output())
        self.assertTrue(result.passed)
        self.assertEqual(result.errors, ())

    def test_succeeded_result_must_cover_every_target(self):
        result = self.gate.validate(
            self.definition, self.request,
            self.output(target_reports=self.reports[:-1]),
        )
        self.assertFalse(result.passed)
        self.assertIn("successful_result_missing_target_reports", result.errors)

    def test_unregistered_target_is_rejected(self):
        bad = TargetReport(
            target_id="other-module.private-target", target_version="1.0.0",
            observation_types=("news",), period_start=self.request.period_start,
            period_end=self.request.period_end, checked_at="2026-11-19T09:30:00+02:00",
            report_content="Vieraan aiheen sisältö.",
        )
        result = self.gate.validate(
            self.definition, self.request,
            self.output(target_reports=(self.reports[0], bad)),
        )
        self.assertFalse(result.passed)
        self.assertIn("target_report_not_owned", result.errors)

    def test_wrong_target_version_is_rejected(self):
        first = self.reports[0]
        bad = TargetReport(
            target_id=first.target_id, target_version="9.9.9",
            observation_types=first.observation_types,
            period_start=first.period_start, period_end=first.period_end,
            checked_at=first.checked_at, report_content=first.report_content,
        )
        result = self.gate.validate(
            self.definition, self.request,
            self.output(target_reports=(bad, *self.reports[1:])),
        )
        self.assertFalse(result.passed)
        self.assertIn("target_report_version_mismatch", result.errors)

    def test_sensitive_artifact_fields_are_rejected(self):
        result = self.gate.validate(
            self.definition, self.request,
            self.output(artifacts={"api_token": "must-not-be-stored"}),
        )
        self.assertFalse(result.passed)
        self.assertIn("artifacts_contain_restricted_fields", result.errors)

    def test_partial_result_can_report_only_completed_targets(self):
        result = self.gate.validate(
            self.definition, self.request,
            self.output(status="partial", target_reports=self.reports[:-1]),
        )
        self.assertTrue(result.passed)

    def assessment(self):
        keys = (
            "sources_opened", "claim_support", "source_independence", "uncertainty",
            "dates", "tracking_period", "duplicates", "guid_preservation",
            "xml_html", "rss_structure", "report_completeness", "accessibility",
        )
        checklist = {
            key: {"status": "pass", "note": "Tarkistettu.", "evidence": ["Tarkistuksen tulos"]}
            for key in keys
        }
        return {
            "checklist": checklist,
            "decision": "approved",
            "reviewer_notes": ["Raportti täyttää julkaisun laatuehdot."],
            "claim_assessments": [{
                "claim_id": "claim-1", "claim": "Esimerkkiväite",
                "verification_status": "riippumattomissa_toimituksellisissa_lahteissa_vahvistettu",
                "sources": [{
                    "source_id": "moomin-com", "source_class": "A",
                    "source_role": "ensisijainen", "independence": "riippumaton",
                }],
            }],
        }

    def test_production_requires_approved_publication_assessment(self):
        production_request = ModuleRunRequest(
            **{**self.request.__dict__, "mode": "production"}
        )
        # Aktiivisuus estää tässä vaiheessa tuotannon; arvioinnin erillinen
        # skeema tarkistetaan suoraan, jotta moduuleja ei tarvitse aktivoida.
        self.assertIn(
            "publication_assessment_missing",
            self.gate._assessment_errors(None, required=True),
        )
        self.assertEqual(self.gate._assessment_errors(self.assessment(), required=True), [])
        rejected = self.assessment()
        rejected["decision"] = "rejected"
        self.assertIn(
            "publication_assessment_rejected",
            self.gate._assessment_errors(rejected, required=True),
        )
        failed = self.assessment()
        failed["checklist"]["claim_support"]["status"] = "fail"
        self.assertIn(
            "publication_check_failed:claim_support",
            self.gate._assessment_errors(failed, required=True),
        )


if __name__ == "__main__":
    unittest.main()
