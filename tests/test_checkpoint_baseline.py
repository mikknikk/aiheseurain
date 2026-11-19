"""Testaa checkpointin lähtötilan read-only-lukua ja virhetilanteita."""
import hashlib
import json
import unittest
from pathlib import Path

from scripts.github_module_adapters import GitHubFile
from scripts.checkpoint_baseline import (
    CheckpointBaselineError, read_checkpoint_baseline,
)

ROOT = Path(__file__).resolve().parents[1]


def git_blob_sha(content: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(content)).encode() + b"\0" + content).hexdigest()


class ReadOnlyCheckpointClient:
    """Contents API -testitupla, joka laskee myös kirjoitusyritykset."""
    def __init__(self, value=None, *, sha=None):
        self.files = {}
        self.reads = []
        self.writes = 0
        if value is not None:
            content = json.dumps(value).encode("utf-8")
            self.files[("module-runtime-state", "data/module-state/taylor-swift.json")] = GitHubFile(
                content, sha or git_blob_sha(content)
            )

    def get_file(self, path, branch):
        self.reads.append((path, branch))
        return self.files.get((branch, path))

    def put_file(self, *args, **kwargs):
        self.writes += 1
        raise AssertionError("Lähtötilan lukija ei saa kirjoittaa.")


def valid_state():
    return {
        "schema_version": 1,
        "module_id": "taylor-swift",
        "checkpoint": {"last_successful_run": {
            "run_id": "previous-run-001",
            "checked_at": "2026-11-18T20:00:00Z",
        }},
    }


class CheckpointBaselineTests(unittest.TestCase):
    def setUp(self):
        self.now = "2026-11-19T21:00:00Z"

    def test_reads_baseline_and_returns_blob_sha_and_checkpoint(self):
        client = ReadOnlyCheckpointClient(valid_state())
        result = read_checkpoint_baseline(
            client, "taylor-swift", observed_at=self.now,
        )
        self.assertEqual(result["module_id"], "taylor-swift")
        self.assertEqual(result["run_id"], "previous-run-001")
        self.assertEqual(result["checked_at"], "2026-11-18T20:00:00Z")
        self.assertEqual(result["blob_sha"], git_blob_sha(
            json.dumps(valid_state()).encode("utf-8")
        ))
        self.assertEqual(client.reads, [(
            "data/module-state/taylor-swift.json", "module-runtime-state"
        )])
        self.assertEqual(client.writes, 0)

    def test_first_run_without_checkpoint_is_explicitly_null(self):
        state = valid_state()
        state["checkpoint"]["last_successful_run"] = {
            "run_id": None, "checked_at": None,
        }
        client = ReadOnlyCheckpointClient(state)
        result = read_checkpoint_baseline(client, "taylor-swift", observed_at=self.now)
        self.assertIsNone(result["run_id"])
        self.assertIsNone(result["checked_at"])
        self.assertEqual(client.writes, 0)

    def test_missing_checkpoint_fails_closed(self):
        client = ReadOnlyCheckpointClient()
        with self.assertRaises(CheckpointBaselineError):
            read_checkpoint_baseline(client, "taylor-swift", observed_at=self.now)
        self.assertEqual(client.writes, 0)

    def test_rejects_wrong_module_ownership(self):
        state = valid_state()
        state["module_id"] = "tolkien"
        client = ReadOnlyCheckpointClient(state)
        with self.assertRaises(CheckpointBaselineError):
            read_checkpoint_baseline(client, "taylor-swift", observed_at=self.now)

    def test_rejects_invalid_checkpoint_timestamp_and_blob_sha(self):
        state = valid_state()
        state["checkpoint"]["last_successful_run"]["checked_at"] = "not-a-date"
        with self.assertRaises(ValueError):
            read_checkpoint_baseline(
                ReadOnlyCheckpointClient(state), "taylor-swift", observed_at=self.now,
            )
        with self.assertRaises(CheckpointBaselineError):
            read_checkpoint_baseline(
                ReadOnlyCheckpointClient(valid_state(), sha="bad-sha"),
                "taylor-swift", observed_at=self.now,
            )


if __name__ == "__main__":
    unittest.main()
