"""Varmista runner-prosessin sandbox-raja ja suljettu virhekäyttäytyminen."""
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest

from scripts.isolated_module_runner import (
    IsolatedRunnerError,
    _sandbox_command,
    run_isolated_module,
)


class IsolatedModuleRunnerTests(unittest.TestCase):
    def setUp(self):
        self.bundle = {
            "bundle_schema_version": 1,
            "module_id": "tolkien",
            "module_definition_version": "1.0.0",
            "run": {"run_id": "sandbox-test", "period": {
                "start": "2026-11-19T00:00:00+02:00",
                "end": "2026-11-19T23:59:59+02:00"}},
            "module": {"module_id": "tolkien"},
            "targets": [],
            "sources": [],
            "module_state": {"module_id": "tolkien", "checkpoint": {}, "publication": {}},
        }

    def test_command_mounts_only_bundle_runner_and_output(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for name in ("input", "runner", "output"):
                (root / name).mkdir()
            command = _sandbox_command("/usr/bin/bwrap", root, timeout_seconds=15)
        self.assertIn("--unshare-all", command)
        self.assertIn("--clearenv", command)
        self.assertIn("--ro-bind", command)
        self.assertIn("--bind", command)
        self.assertIn("/input", command)
        self.assertIn("/runner", command)
        self.assertIn("/output", command)
        self.assertNotIn(str(Path.cwd()), command)
        self.assertIn("-I", command)

    def test_fails_closed_when_bubblewrap_is_missing(self):
        with self.assertRaises(IsolatedRunnerError):
            run_isolated_module(self.bundle, "pass", bubblewrap_path="/missing/bwrap")

    @unittest.skipUnless(os.name == "posix" and shutil.which("bwrap") and Path("/usr/bin/python3").is_file(),
                         "Linux bubblewrap and system Python are required for integration test")
    def test_runner_cannot_read_host_secret_and_can_write_only_result(self):
        with tempfile.TemporaryDirectory() as temp:
            secret = Path(temp) / "host-secret.txt"
            secret.write_text("OTHER TOPIC PRIVATE DATA", encoding="utf-8")
            source = (
                "import json, pathlib, sys\n"
                "secret = pathlib.Path(" + repr(str(secret)) + ")\n"
                "visible = secret.exists()\n"
                "pathlib.Path(sys.argv[2]).write_text(json.dumps({"
                "'module_id': json.loads(pathlib.Path(sys.argv[1]).read_text())['module_id'],"
                "'host_secret_visible': visible}), encoding='utf-8')\n"
            )
            result = run_isolated_module(self.bundle, source, timeout_seconds=30)
            self.assertEqual(result["module_id"], "tolkien")
            self.assertFalse(result["host_secret_visible"])
            self.assertEqual(secret.read_text(encoding="utf-8"), "OTHER TOPIC PRIVATE DATA")

    @unittest.skipUnless(os.name == "posix" and shutil.which("bwrap") and Path("/usr/bin/python3").is_file(),
                         "Linux bubblewrap and system Python are required for integration test")
    def test_runner_cannot_replace_output_file_with_host_symlink(self):
        with tempfile.TemporaryDirectory() as temp:
            secret = Path(temp) / "host-secret.txt"
            secret.write_text("DO NOT READ", encoding="utf-8")
            source = (
                "import pathlib, sys\\n"
                "target = pathlib.Path(sys.argv[2])\\n"
                "target.unlink()\\n"
                "target.symlink_to(" + repr(str(secret)) + ")\\n"
            )
            with self.assertRaises(IsolatedRunnerError):
                run_isolated_module(self.bundle, source, timeout_seconds=30)
            self.assertEqual(secret.read_text(encoding="utf-8"), "DO NOT READ")

    @unittest.skipUnless(os.name == "posix" and shutil.which("bwrap") and Path("/usr/bin/python3").is_file(),
                         "Linux bubblewrap and system Python are required for integration test")
    def test_runner_cannot_modify_read_only_input(self):
        source = (
            "import pathlib, sys\n"
            "pathlib.Path(sys.argv[1]).write_text('tampered', encoding='utf-8')\n"
            "pathlib.Path(sys.argv[2]).write_text('{}', encoding='utf-8')\n"
        )
        with self.assertRaises(IsolatedRunnerError):
            run_isolated_module(self.bundle, source, timeout_seconds=30)


if __name__ == "__main__":
    unittest.main()
