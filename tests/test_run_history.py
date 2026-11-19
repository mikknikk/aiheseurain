"""Ajohistorian JSON Schema -sopimuksen yksikkötestit.

Testit varmistavat, että eri automaatioiden historiatiedostot käyttävät
yhteistä rakennetta ja että virheelliset tilat eivät läpäise skeemaa.
"""

from __future__ import annotations

import json
from pathlib import Path
import unittest

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "schemas/automation-run-history.schema.json").read_text(encoding="utf-8"))


def valid_history():
    """Palauttaa pienimmän hyväksyttävän esimerkin yhdestä ajosta."""
    return {
        "schema_version": 1,
        "automation_id": "main_automation",
        "updated_at": "2026-11-17T10:00:00Z",
        "runs": [{
            "run_id": "20261117T100000Z-test001",
            "automation_id": "main_automation",
            "status": "running",
            "started_at": "2026-11-17T10:00:00Z",
            "finished_at": None,
            "updated_at": "2026-11-17T10:00:00Z",
            "source": "chatgpt_scheduled_task",
            "summary": "Ajo käynnissä",
            "steps": [{
                "id": "preflight",
                "name": "Esitarkistus",
                "status": "succeeded",
                "started_at": "2026-11-17T10:00:00Z",
                "finished_at": "2026-11-17T10:00:05Z",
                "updated_at": "2026-11-17T10:00:05Z",
                "warnings": [],
                "errors": [],
            }],
            "warnings": [],
            "errors": [],
        }],
    }


class RunHistorySchemaTests(unittest.TestCase):
    """Testaa onnistuneet, epäonnistuneet ja keskeneräiset ajot."""

    def test_running_run_is_valid(self):
        jsonschema.validate(valid_history(), SCHEMA)

    def test_failed_run_with_error_is_valid(self):
        history = valid_history()
        history["runs"][0]["status"] = "failed"
        history["runs"][0]["finished_at"] = "2026-11-17T10:05:00Z"
        history["runs"][0]["steps"][0]["status"] = "failed"
        history["runs"][0]["steps"][0]["errors"] = ["Lähdepalvelu ei vastannut."]
        jsonschema.validate(history, SCHEMA)

    def test_interrupted_run_is_valid(self):
        history = valid_history()
        history["runs"][0]["status"] = "interrupted"
        history["runs"][0]["steps"][0]["status"] = "interrupted"
        jsonschema.validate(history, SCHEMA)

    def test_unknown_and_partial_results_are_valid(self):
        history = valid_history()
        history["runs"][0]["status"] = "partial"
        history["runs"][0]["steps"][0]["status"] = "unknown"
        jsonschema.validate(history, SCHEMA)


    def test_platform_observation_is_valid_without_fabricated_steps(self):
        history = valid_history()
        run = history["runs"][0]
        run.update({
            "run_id": "e93435ca-f034-832e-8787-d9c65dd82b84",
            "status": "failed",
            "started_at": "2026-11-19T04:40:14.605964Z",
            "finished_at": "2026-11-19T05:05:20.087466Z",
            "updated_at": "2026-11-19T06:40:00Z",
            "source": "chatgpt_platform_observation",
            "summary": "Ajastusalusta ilmoitti epäonnistumisesta; teknistä juurisyytä ei voitu varmistaa.",
            "steps": [],
            "warnings": ["chat_ref=null; keskustelulokia ei ole saatavilla."],
            "errors": ["There was a problem with your scheduled task."],
            "diagnostics": {
                "stage": "platform_execution",
                "category": "platform_error",
                "retryable": None,
                "root_cause_confirmed": False,
                "chat_ref_present": False,
                "platform_run_id": "e93435ca-f034-832e-8787-d9c65dd82b84",
            },
        })
        jsonschema.validate(history, SCHEMA)

    def test_platform_observation_requires_diagnostics_and_no_steps(self):
        history = valid_history()
        run = history["runs"][0]
        run["source"] = "chatgpt_platform_observation"
        run["status"] = "failed"
        run["steps"] = []
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(history, SCHEMA)
        run["diagnostics"] = {
            "stage": "platform_execution",
            "category": "platform_error",
            "retryable": None,
            "root_cause_confirmed": False,
            "chat_ref_present": False,
            "platform_run_id": run["run_id"],
        }
        run["steps"] = [{"id": "invented", "name": "Keksitty vaihe", "status": "failed",
                         "started_at": run["started_at"], "finished_at": run["finished_at"],
                         "updated_at": run["updated_at"], "warnings": [], "errors": []}]
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(history, SCHEMA)

    def test_platform_observation_cannot_claim_confirmed_root_cause(self):
        history = valid_history()
        run = history["runs"][0]
        run.update({
            "source": "chatgpt_platform_observation",
            "status": "failed",
            "steps": [],
            "diagnostics": {
                "stage": "platform_execution",
                "category": "platform_error",
                "retryable": None,
                "root_cause_confirmed": True,
                "chat_ref_present": False,
                "platform_run_id": run["run_id"],
            },
        })
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(history, SCHEMA)

    def test_wrong_automation_id_is_rejected(self):
        history = valid_history()
        history["runs"][0]["automation_id"] = "screening_watch"
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(history, SCHEMA)

    def test_unknown_step_state_is_rejected(self):
        history = valid_history()
        history["runs"][0]["steps"][0]["status"] = "finished-ish"
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(history, SCHEMA)


if __name__ == "__main__":
    unittest.main()
