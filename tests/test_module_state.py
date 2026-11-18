"""Testaa moduulikohtaisen tilan eheys ja onnistuneen checkpointin siirtymäsäännöt."""
from copy import deepcopy
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from scripts import validate_module_state as migration_validator
from scripts.module_state import ModuleStateError, StateConflictError, commit_successful_checkpoint, validate_module_state
from scripts.validate_module_state import validate_state_migration

ROOT = Path(__file__).resolve().parents[1]


class ModuleStateMigrationTests(unittest.TestCase):
    """Varmista, että vanha tila ja kaikki viitteet säilyivät migraatiossa."""

    def test_all_ten_module_states_match_legacy_sources(self):
        """Kymmenen moduulitilaa vastaa vanhaa seurantatilaa, lähdelokia ja syötteitä."""
        self.assertEqual(validate_state_migration(), [])

    def test_unknown_historical_checkpoints_remain_unknown(self):
        """Puuttuvia tarkistusaikoja tai ajotunnisteita ei ole päätelty."""
        registry = json.loads((ROOT / "data/module-registry.json").read_text(encoding="utf-8"))
        for entry in registry["modules"]:
            state = json.loads((ROOT / f"data/module-state/{entry['module_id']}.json").read_text(encoding="utf-8"))
            if entry["module_id"] not in {"tolkien", "taylor-swift", "gurmeet-ram-rahim-singh", "indian-film-screening-watch"}:
                self.assertIsNone(state["checkpoint"]["last_successful_run"]["checked_at"])
                self.assertIsNone(state["checkpoint"]["last_successful_run"]["run_id"])

    def test_gurmeet_migration_rejects_each_legacy_and_reference_mismatch(self):
        """Kaikki kuusi PR:ssä havaittua ristiriitatyyppiä pysäyttävät migraation."""
        # Kopioi validaattorin tarvitsemat tiedostot väliaikaiseen juureen, jotta
        # testit voivat rikkoa yhden kentän kerrallaan koskematta oikeaan dataan.
        with tempfile.TemporaryDirectory() as temporary:
            test_root = Path(temporary)
            for folder in ("data", "modules", "feeds", "docs"):
                shutil.copytree(ROOT / folder, test_root / folder)
            with patch.object(migration_validator, "ROOT", test_root), patch.object(
                migration_validator, "REGISTRY_PATH", test_root / "data/module-registry.json"
            ):
                state_path = test_root / "data/module-state/gurmeet-ram-rahim-singh.json"
                original = json.loads(state_path.read_text(encoding="utf-8"))
                cases = (
                    (("checkpoint", "last_successful_run", "checked_at"), None, "viimeisin tarkistusaika"),
                    (("checkpoint", "last_successful_run", "result"), "not_recorded", "viimeisin tulos"),
                    (("checkpoint", "last_successful_run", "published_items"), 0, "julkaistujen itemien määrä"),
                    (("checkpoint", "last_successful_run", "sources_checked"), 0, "tarkistettujen lähteiden määrä"),
                    (("history", "source_check_run_refs"), [], "lähdetarkistusajojen viitteet"),
                    (("publication", "guid_refs"), [], "RSS-GUID-viitteet"),
                )
                for path, bad_value, expected_error in cases:
                    with self.subTest(expected_error=expected_error):
                        candidate = deepcopy(original)
                        target = candidate
                        for key in path[:-1]:
                            target = target[key]
                        target[path[-1]] = bad_value
                        state_path.write_text(json.dumps(candidate, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                        errors = migration_validator.validate_state_migration()
                        self.assertTrue(any(expected_error in error for error in errors), errors)
                state_path.write_text(json.dumps(original, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                self.assertEqual(migration_validator.validate_state_migration(), [])


class CheckpointTransitionTests(unittest.TestCase):
    """Varmista idempotentti, järjestyksen säilyttävä ja ristiriidat tunnistava päivitys."""

    def setUp(self):
        self.state = json.loads((ROOT / "data/module-state/taylor-swift.json").read_text(encoding="utf-8"))
        self.definition = json.loads((ROOT / "modules/topics/taylor-swift/module.json").read_text(encoding="utf-8"))
        validate_module_state(self.state, self.definition)
        current = self.state["checkpoint"]["last_successful_run"]
        self.expected_id = current["run_id"]
        self.expected_time = current["checked_at"]
        self.args = {
            "run_id":"test-run-20261118-140000",
            "definition_version":self.definition["definition_version"],
            "checked_at":"2026-11-18T14:00:00+02:00",
            "period_start":"2026-11-17T00:00:00+02:00",
            "period_end":"2026-11-18T13:59:59+02:00",
            "run_status":"succeeded","source_scan_complete":True,"publication_verified":True,
            "published_items":2,"sources_checked":10,
            "source_check_run_refs":["test-source-check-1"],
            "report_guid_refs":["test-report-guid-1"],
            "expected_previous_run_id":self.expected_id,
            "expected_previous_checked_at":self.expected_time,
            "run_history_ref":"run-history/main-automation/history.json#test-run-20261118-140000",
            "recorded_on":"2026-11-18"
        }

    def test_partial_or_failed_run_does_not_advance_checkpoint(self):
        """Epäonnistunut, osittainen tai julkaisematon ajo ei muuta tilaa."""
        original = deepcopy(self.state)
        for changes in (
            {"run_status":"failed"},
            {"run_status":"partial"},
            {"source_scan_complete":False},
            {"publication_verified":False}
        ):
            args = dict(self.args)
            args.update(changes)
            self.assertEqual(commit_successful_checkpoint(self.state, **args), original)
        self.assertEqual(self.state, original)

    def test_successful_run_advances_checkpoint_and_appends_history(self):
        """Varmennettu onnistuminen päivittää checkpointin ja lisää historiatapahtuman."""
        result = commit_successful_checkpoint(self.state, **self.args)
        current = result["checkpoint"]["last_successful_run"]
        self.assertEqual(current["run_id"], self.args["run_id"])
        self.assertEqual(current["definition_version"], self.definition["definition_version"])
        self.assertEqual(current["published_items"], 2)
        self.assertEqual(len(result["checkpoint_history"]), len(self.state["checkpoint_history"]) + 1)
        self.assertIn("test-report-guid-1", result["publication"]["guid_refs"])
        self.assertIn("test-source-check-1", result["history"]["source_check_run_refs"])
        self.assertEqual(self.state["checkpoint"]["last_successful_run"]["run_id"], self.expected_id)

    def test_same_run_is_idempotent(self):
        """Saman onnistuneen run_id:n uusinta ei lisää toista historiatapahtumaa."""
        first = commit_successful_checkpoint(self.state, **self.args)
        second = commit_successful_checkpoint(first, **self.args)
        self.assertEqual(first, second)

    def test_same_run_id_with_different_result_is_rejected(self):
        """Saman run_id:n ristiriitainen sisältö pysäytetään."""
        first = commit_successful_checkpoint(self.state, **self.args)
        changed = dict(self.args)
        changed["published_items"] = 3
        with self.assertRaises(StateConflictError):
            commit_successful_checkpoint(first, **changed)

    def test_stale_concurrent_checkpoint_is_rejected(self):
        """Rinnakkainen ajo ei saa kirjoittaa vanhan checkpointin päälle."""
        first = commit_successful_checkpoint(self.state, **self.args)
        stale = dict(self.args)
        stale["run_id"] = "test-run-20261118-150000"
        stale["checked_at"] = "2026-11-18T15:00:00+02:00"
        with self.assertRaises(StateConflictError):
            commit_successful_checkpoint(first, **stale)

    def test_older_run_cannot_move_checkpoint_backwards(self):
        """Myöhemmin valmistunut vanha tulos ei saa siirtää checkpointia taaksepäin."""
        stale = dict(self.args)
        stale["checked_at"] = "2026-11-17T12:00:00+02:00"
        with self.assertRaises(StateConflictError):
            commit_successful_checkpoint(self.state, **stale)

    def test_timezone_is_required(self):
        """Checkpointin aikaleimasta on löydyttävä aikavyöhyke."""
        invalid = dict(self.args)
        invalid["checked_at"] = "2026-11-18T14:00:00"
        with self.assertRaises(ModuleStateError):
            commit_successful_checkpoint(self.state, **invalid)

    def test_definition_version_must_match(self):
        """Ajo ei voi päivittää tilaa väärällä moduuliversiolla."""
        invalid = dict(self.args)
        invalid["definition_version"] = "2.0.0"
        with self.assertRaises(ModuleStateError):
            commit_successful_checkpoint(self.state, **invalid)


if __name__ == "__main__":
    unittest.main()
