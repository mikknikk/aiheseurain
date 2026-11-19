"""Testaa ChatGPT-tuloksen validointi ja muunnos."""
import unittest

from scripts.chatgpt_module_result import (
    ChatGPTResultError,
    ChatGPTResultExecutor,
    chatgpt_result_to_execution_output,
)
from scripts.module_orchestrator import ModuleRunRequest


class ChatGPTModuleResultTests(unittest.TestCase):
    def setUp(self):
        self.definition = {
            "module_id": "muumit",
            "definition_version": "1.0.0",
            "contract_version": "1.0.0",
        }
        self.request = ModuleRunRequest(
            module_id="muumit",
            module_definition_version="1.0.0",
            contract_version="1.0.0",
            run_id="muumit-run-001",
            period_start="2026-11-19T00:00:00+02:00",
            period_end="2026-11-19T23:59:59+02:00",
            mode="shadow",
            requested_at="2026-11-19T10:00:00+02:00",
        )
        self.payload = {
            "schema_version": 1,
            "module_id": "muumit",
            "module_definition_version": "1.0.0",
            "contract_version": "1.0.0",
            "run_id": "muumit-run-001",
            "period": {
                "start": "2026-11-19T00:00:00+02:00",
                "end": "2026-11-19T23:59:59+02:00",
            },
            "status": "succeeded",
            "source_scan_complete": True,
            "checked_at": "2026-11-19T10:30:00+02:00",
            "report_content": "Testiraportti",
            "sources_checked": 5,
            "source_check_run_refs": ["muumit-source-check-001"],
            "report_guid_refs": ["urn:aiheseurain:muumit:2026-11-19:abc"],
        }

    def test_valid_result_is_converted(self):
        output = chatgpt_result_to_execution_output(self.payload, self.definition, self.request)
        self.assertEqual(output.status, "succeeded")
        self.assertTrue(output.source_scan_complete)
        self.assertEqual(output.report_content, "Testiraportti")
        self.assertEqual(output.sources_checked, 5)
        self.assertEqual(output.source_check_run_refs, ("muumit-source-check-001",))
        self.assertEqual(output.report_guid_refs, ("urn:aiheseurain:muumit:2026-11-19:abc",))

    def test_executor_implements_module_executor_contract(self):
        output = ChatGPTResultExecutor(self.payload).execute(self.definition, self.request, None)
        self.assertEqual(output.report_content, "Testiraportti")

    def test_rejects_another_module(self):
        payload = dict(self.payload, module_id="tolkien")
        with self.assertRaises(ChatGPTResultError):
            chatgpt_result_to_execution_output(payload, self.definition, self.request)

    def test_rejects_wrong_run_id(self):
        payload = dict(self.payload, run_id="another-run-001")
        with self.assertRaises(ChatGPTResultError):
            chatgpt_result_to_execution_output(payload, self.definition, self.request)

    def test_rejects_wrong_period(self):
        payload = dict(self.payload, period={**self.payload["period"], "start":"2026-11-18T00:00:00+02:00"})
        with self.assertRaises(ChatGPTResultError):
            chatgpt_result_to_execution_output(payload, self.definition, self.request)

    def test_rejects_success_with_incomplete_source_scan(self):
        payload = dict(self.payload, source_scan_complete=False)
        with self.assertRaises(ChatGPTResultError):
            chatgpt_result_to_execution_output(payload, self.definition, self.request)

    def test_converts_target_reports_for_separate_publication_targets(self):
        payload = dict(self.payload)
        payload.pop("report_content")
        payload["target_reports"] = [{
            "target_id": "moomin-news",
            "target_version": "1.0.0",
            "observation_types": ["news"],
            "period": self.payload["period"],
            "checked_at": "2026-11-19T10:30:00+02:00",
            "report_content": "Kohderaportti",
        }]
        output = chatgpt_result_to_execution_output(payload, self.definition, self.request)
        self.assertEqual(len(output.target_reports), 1)
        self.assertEqual(output.target_reports[0].target_id, "moomin-news")
        self.assertEqual(output.target_reports[0].report_content, "Kohderaportti")

    def test_rejects_target_report_with_wrong_period(self):
        payload = dict(self.payload)
        payload.pop("report_content")
        payload["target_reports"] = [{
            "target_id": "moomin-news",
            "target_version": "1.0.0",
            "observation_types": ["news"],
            "period": {"start": "2026-11-18T00:00:00+02:00", "end": self.payload["period"]["end"]},
            "checked_at": "2026-11-19T10:30:00+02:00",
            "report_content": "Kohderaportti",
        }]
        with self.assertRaises(ChatGPTResultError):
            chatgpt_result_to_execution_output(payload, self.definition, self.request)


if __name__ == "__main__":
    unittest.main()
