"""Testaa ChatGPT-tulosten GitHub-vastaanoton turvallisuusrajat."""
import json
from pathlib import Path
import tempfile
import unittest
from scripts.validate_chatgpt_inbox import InboxValidationError, validate_inbox_result

class ChatGPTInboxTests(unittest.TestCase):
    """Testit käyttävät väliaikaisia rekistereitä eivätkä muuta projektin tietoja."""
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "schemas").mkdir()
        (self.root / "data").mkdir()
        source = Path(__file__).resolve().parents[1] / "schemas/chatgpt-module-result.schema.json"
        (self.root / "schemas/chatgpt-module-result.schema.json").write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
        registry = {"contract_version":"1.0.0","modules":[
            {"module_id":"tolkien","module_type":"topic","definition_version":"1.0.0"},
            {"module_id":"indian-film-screening-watch","module_type":"process","definition_version":"1.0.0"}]}
        (self.root / "data/module-registry.json").write_text(json.dumps(registry), encoding="utf-8")
        period = {"start":"2026-11-18T00:00:00+02:00","end":"2026-11-19T00:00:00+02:00"}
        self.payload = {"schema_version":1,"module_id":"tolkien","module_definition_version":"1.0.0",
            "contract_version":"1.0.0","run_id":"tolkien-test-001","period":period,"status":"succeeded",
            "source_scan_complete":True,"checked_at":"2026-11-19T10:00:00+02:00","report_content":"Testiraportti.",
            "handoff":{"dispatch_schema_version":1,"module_id":"tolkien","module_definition_version":"1.0.0",
                "contract_version":"1.0.0","run_id":"tolkien-test-001","period":period,
                "requested_at":"2026-11-19T09:00:00+02:00","input_sha256":"a"*64}}
        self.file = self.root / "result.json"
        self.file.write_text(json.dumps(self.payload), encoding="utf-8")
        self.relative = "data/chatgpt-inbox/tolkien/tolkien-test-001.json"

    def tearDown(self):
        self.temp.cleanup()

    def test_valid_result(self):
        self.assertEqual(validate_inbox_result(self.file, relative_path=self.relative, root=self.root)["run_id"], "tolkien-test-001")

    def test_wrong_module_path(self):
        with self.assertRaises(InboxValidationError):
            validate_inbox_result(self.file, relative_path="data/chatgpt-inbox/muumit/tolkien-test-001.json", root=self.root)

    def test_wrong_run_path(self):
        with self.assertRaises(InboxValidationError):
            validate_inbox_result(self.file, relative_path="data/chatgpt-inbox/tolkien/other-run.json", root=self.root)

    def test_handoff_run_id_mismatch(self):
        self.payload["handoff"]["run_id"] = "different-run"
        self.file.write_text(json.dumps(self.payload), encoding="utf-8")
        with self.assertRaises(InboxValidationError):
            validate_inbox_result(self.file, relative_path=self.relative, root=self.root)

    def test_wrong_module_version(self):
        self.payload["module_definition_version"] = "2.0.0"
        self.payload["handoff"]["module_definition_version"] = "2.0.0"
        self.file.write_text(json.dumps(self.payload), encoding="utf-8")
        with self.assertRaises(InboxValidationError):
            validate_inbox_result(self.file, relative_path=self.relative, root=self.root)

    def test_process_module_is_rejected(self):
        self.payload["module_id"] = "indian-film-screening-watch"
        self.payload["handoff"]["module_id"] = "indian-film-screening-watch"
        self.payload["run_id"] = "screening-test-001"
        self.payload["handoff"]["run_id"] = "screening-test-001"
        self.file.write_text(json.dumps(self.payload), encoding="utf-8")
        with self.assertRaises(InboxValidationError):
            validate_inbox_result(self.file, relative_path="data/chatgpt-inbox/indian-film-screening-watch/screening-test-001.json", root=self.root)

    def test_succeeded_requires_complete_scan(self):
        self.payload["source_scan_complete"] = False
        self.file.write_text(json.dumps(self.payload), encoding="utf-8")
        with self.assertRaises(InboxValidationError):
            validate_inbox_result(self.file, relative_path=self.relative, root=self.root)

if __name__ == "__main__":
    unittest.main()
