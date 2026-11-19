"""Testaa ChatGPT-tuloksen hallittu shadow-käsittely."""
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch, MagicMock

from scripts import process_chatgpt_result as processor
from scripts.module_orchestrator import ModuleRunRequest

ROOT = Path(__file__).resolve().parents[1]


class ChatGPTResultProcessingTests(unittest.TestCase):
    def setUp(self):
        self.request = ModuleRunRequest(
            module_id="tolkien",
            module_definition_version="1.0.0",
            contract_version="1.0.0",
            run_id="tolkien-shadow-001",
            period_start="2026-11-18T00:00:00+02:00",
            period_end="2026-11-19T00:00:00+02:00",
            mode="shadow",
            requested_at="2026-11-19T09:00:00+02:00",
        )
        self.payload = {
            "module_id": "tolkien",
            "run_id": "tolkien-shadow-001",
        }
        self.definition = {
            "module_id": "tolkien",
            "module_type": "topic",
            "definition_version": "1.0.0",
        }
        self.accepted = {
            "task_id": "tolkien",
            "feed_path": "feeds/tolkien.xml",
        }

    def test_processing_always_uses_shadow_orchestrator_without_writers(self):
        fake_result = object()
        fake_orchestrator = MagicMock()
        fake_orchestrator.run.return_value = fake_result
        with (
            patch.object(processor, "validate_inbox_result", return_value=self.payload),
            patch.object(processor, "GitHubApiClient", return_value=object()),
            patch.object(processor, "GitHubRotationStateStore"),
            patch.object(processor, "GitHubModuleStateStore"),
            patch.object(processor, "GitHubHandoffStore"),
            patch.object(
                processor, "_validated_request_context",
                return_value=(self.request, self.definition, self.accepted, "tolkien"),
            ),
            patch.object(processor, "ChatGPTResultExecutor"),
            patch.object(processor, "ChatGPTResultQualityGate"),
            patch.object(processor, "GitHubRunRecorder"),
            patch.object(processor, "ModuleOrchestrator", return_value=fake_orchestrator) as orchestrator,
        ):
            result = processor.process_inbox_result(
                Path("unused.json"),
                relative_path="data/chatgpt-inbox/tolkien/tolkien-shadow-001.json",
                root=ROOT,
            )
        self.assertIs(result, fake_result)
        kwargs = orchestrator.call_args.kwargs
        self.assertNotIn("state_store", kwargs)
        self.assertNotIn("artifact_store", kwargs)
        self.assertNotIn("publication_journal", kwargs)
        self.assertNotIn("publisher", kwargs)
        run_request = fake_orchestrator.run.call_args.args[0]
        self.assertEqual(run_request.mode, "shadow")

    def test_production_mode_is_rejected_before_any_processing(self):
        with patch.object(processor, "validate_inbox_result") as validate:
            with self.assertRaises(processor.ChatGPTProcessingError):
                processor.process_inbox_result(
                    Path("unused.json"),
                    relative_path="data/chatgpt-inbox/tolkien/tolkien-shadow-001.json",
                    mode="production",
                    root=ROOT,
                )
        validate.assert_not_called()

    def test_changed_inbox_file_accepts_exactly_one_new_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "Test"], cwd=root, check=True)
            (root / "data/chatgpt-inbox/tolkien").mkdir(parents=True)
            path = root / "data/chatgpt-inbox/tolkien/tolkien-shadow-001.json"
            path.write_text("{}", encoding="utf-8")
            subprocess.run(["git", "add", "."], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "add result"], cwd=root, check=True)
            after = subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=root, text=True
            ).strip()
            result = processor.changed_inbox_file("0" * 40, after, root=root)
            self.assertEqual(
                result, "data/chatgpt-inbox/tolkien/tolkien-shadow-001.json"
            )

    def test_changed_inbox_file_rejects_modification(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "Test"], cwd=root, check=True)
            (root / "data/chatgpt-inbox/tolkien").mkdir(parents=True)
            path = root / "data/chatgpt-inbox/tolkien/tolkien-shadow-001.json"
            path.write_text("{}", encoding="utf-8")
            subprocess.run(["git", "add", "."], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "initial"], cwd=root, check=True)
            before = subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=root, text=True
            ).strip()
            path.write_text('{"changed": true}', encoding="utf-8")
            subprocess.run(["git", "add", "."], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "modify result"], cwd=root, check=True)
            after = subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=root, text=True
            ).strip()
            with self.assertRaises(processor.ChatGPTProcessingError):
                processor.changed_inbox_file(before, after, root=root)


if __name__ == "__main__":
    unittest.main()
