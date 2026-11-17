import json
import unittest

from scripts.validate_kanban_data import SCHEMA_PATH, validate_dataset


def make_issue(number):
    """Luo testissä käytettävän yksinkertaisen issue-tietueen."""
    return {
        "number": number,
        "title": f"Tehtävä {number}",
        "html_url": f"https://github.com/mikknikk/aiheseurain/issues/{number}",
        "state": "open",
        "labels": [{"name": "tila:ready"}],
        "updated_at": "2026-11-17T10:00:00Z",
    }


def make_dataset():
    """Palauttaa pienen, rakenteellisesti kelvollisen testiaineiston."""
    issue = make_issue(12)
    return {
        "schema_version": 1,
        "generated_at": "2026-11-17T10:00:00Z",
        "status": "complete",
        "issue_count": 1,
        "dependency_relation_count": 0,
        "issues": [issue],
        "dependencies": [{"issueNumber": 12, "blockedBy": []}],
    }


def load_schema():
    """Lukee repositorion varsinaisen skeeman, jotta testit tarkistavat sen."""
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

class KanbanDataValidationTests(unittest.TestCase):
    """Testaa Kehitysjonon julkaistavan aineiston eheystarkistuksia."""

    def test_complete_dataset_is_accepted(self):
        """Täydellinen aineisto hyväksytään."""
        validate_dataset(make_dataset(), load_schema())

    def test_partial_dataset_is_rejected(self):
        """Osittaista aineistoa ei saa julkaista."""
        dataset = make_dataset()
        dataset["status"] = "partial"
        with self.assertRaisesRegex(ValueError, "JSON Schema"):
            validate_dataset(dataset, load_schema())

    def test_issue_count_must_match(self):
        """Ilmoitetun issue-määrän pitää vastata sisältöä."""
        dataset = make_dataset()
        dataset["issue_count"] = 2
        with self.assertRaisesRegex(ValueError, "issue_count"):
            validate_dataset(dataset, load_schema())

    def test_each_issue_must_have_one_dependency_record(self):
        """Riippuvuustietueiden pitää vastata kaikkia issueita."""
        dataset = make_dataset()
        dataset["dependencies"] = []
        with self.assertRaisesRegex(ValueError, "täsmälleen yhtä"):
            validate_dataset(dataset, load_schema())


if __name__ == "__main__":
    unittest.main()
