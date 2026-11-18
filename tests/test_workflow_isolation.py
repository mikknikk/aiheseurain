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
        self.assertIn("push", workflow["on"])
        self.assertIn("node --check assets/js/valvomo.js", commands)
        self.assertIn("node --test tests/valvomo.test.mjs", commands)
        self.assertNotIn("needs", job)

    def test_ui_failure_cannot_become_a_tracking_validation_dependency(self):
        """Mallinna riippuvuusrakenne: UI-ajon tulos ei ole vaaditun tarkistuksen syöte."""
        tracking = read_workflow(".github/workflows/validate-feeds.yml")
        ui = read_workflow(".github/workflows/test-ui.yml")

        # Vaaditun työnkulun pitää käynnistyä suoraan PR:stä eikä UI-ajon jälkeen.
        self.assertIn("pull_request", tracking["on"])
        self.assertEqual(set(tracking["jobs"]), {"validate"})
        tracking_job = tracking["jobs"]["validate"]
        self.assertNotIn("needs", tracking_job)
        self.assertNotIn("if", tracking_job)

        # UI-työnkulku käynnistyy itsenäisesti; workflow_run loisi työnkulkujen välisen ketjun.
        self.assertNotIn("workflow_run", ui["on"])
        self.assertEqual(set(ui["jobs"]), {"ui-tests"})
        ui_job = ui["jobs"]["ui-tests"]
        self.assertNotIn("needs", ui_job)
        self.assertNotIn("if", ui_job)

        # Kumpikaan työnkulku ei saa lukea toisen työnkulun lopputulosta ehtona.
        serialized = yaml.dump({"tracking": tracking, "ui": ui})
        for forbidden in ("workflow_run", "needs.ui-tests", "needs.validate"):
            self.assertNotIn(forbidden, serialized)

        self.assertEqual(
            tracking_job["name"],
            "Tarkista RSS, HTML, dokumentaatio ja seurantatila",
            "Säilytä rulesetin vaadittu status check muuttumattomana.",
        )


if __name__ == "__main__":
    unittest.main()
