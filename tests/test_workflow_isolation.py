"""Varmista, etteivät käyttöliittymätestit kuulu seurantajulkaisun pakolliseen CI-porttiin."""

from pathlib import Path
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[1]


def read_workflow(path):
    """Lue GitHub Actions -työnkulku YAML-muodossa ilman avainten tyyppimuunnoksia."""
    with (ROOT / path).open(encoding="utf-8") as workflow_file:
        return yaml.load(workflow_file, Loader=yaml.BaseLoader)


class WorkflowIsolationTests(unittest.TestCase):
    """Testaa, että käyttöliittymien CI-virheet eivät kaada seurantavalidointia."""

    def test_tracking_validation_does_not_run_ui_tests(self):
        workflow = read_workflow(".github/workflows/validate-feeds.yml")
        job = workflow["jobs"]["validate"]
        step_names = [step.get("name", "") for step in job["steps"]]
        commands = "\n".join(step.get("run", "") for step in job["steps"])

        self.assertEqual(
            job["name"],
            "Tarkista RSS, HTML, dokumentaatio ja seurantatila",
            "Säilytä main-haaran rulesetissä vaaditun tarkistuksen nimi.",
        )
        self.assertNotIn(
            "Testaa Valvomon, RSS-lukijan ja Kehitysjonon logiikka",
            step_names,
        )
        self.assertNotIn("node --check", commands)
        self.assertNotIn("node --test", commands)
        self.assertIn("python scripts/validate_feeds.py", commands)
        self.assertIn("python scripts/validate_publication_gate.py", commands)

    def test_ui_tests_run_in_their_own_workflow(self):
        workflow = read_workflow(".github/workflows/test-ui.yml")
        job = workflow["jobs"]["ui-tests"]
        commands = "\n".join(step.get("run", "") for step in job["steps"])

        self.assertIn("pull_request", workflow["on"])
        self.assertIn("node --check assets/js/valvomo.js", commands)
        self.assertIn("node --test tests/valvomo.test.mjs", commands)
        self.assertNotIn("needs", job)


if __name__ == "__main__":
    unittest.main()
