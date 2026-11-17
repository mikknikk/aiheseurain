"""Testaa seurantamoduulirekisterin deterministinen lataus ja virheiden eristys."""

from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from scripts.module_registry import ROOT, RegistryError, load_registry


class ModuleRegistryTests(unittest.TestCase):
    """Varmista rekisterin sopimus, polkurajat, tila ja virheiden eristys."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.temp_root = Path(self.temp_dir.name)
        for relative in ("schemas", "schemas/module-extensions", "data", "examples/seurantamoduulit"):
            (self.temp_root / relative).mkdir(parents=True, exist_ok=True)

        # Kopioi skeemat ja esimerkkimääritykset erilliseen testirepositorioon.
        for relative in (
            "schemas/seurantamoduuli.schema.json",
            "schemas/seurantamoduulirekisteri.schema.json",
            "schemas/module-extensions/event-watch-film-screenings.schema.json",
            "examples/seurantamoduulit/tolkien.topic.json",
            "examples/seurantamoduulit/intialaisten-elokuvien-naytosvahti.process.json",
        ):
            target = self.temp_root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text((ROOT / relative).read_text(encoding="utf-8"), encoding="utf-8")
        self.registry_path = self.temp_root / "data/module-registry.json"

    def write_registry(self, modules, registry_version="1.0.0", contract_version="1.0.0"):
        """Kirjoita testirekisteri annetuilla merkinnöillä."""
        self.registry_path.write_text(
            json.dumps(
                {
                    "registry_version": registry_version,
                    "contract_version": contract_version,
                    "modules": modules,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

    def fixture_entries(self):
        """Palauta testien kaksi erilaista moduuliviitettä."""
        return [
            {
                "module_id": "tolkien",
                "module_type": "topic",
                "definition_version": "1.0.0",
                "path": "examples/seurantamoduulit/tolkien.topic.json",
                "status": "active",
            },
            {
                "module_id": "indian-film-screening-watch",
                "module_type": "process",
                "definition_version": "1.0.0",
                "path": "examples/seurantamoduulit/intialaisten-elokuvien-naytosvahti.process.json",
                "status": "active",
            },
        ]

    def test_loads_topic_and_process_modules(self):
        """Aihe- ja prosessimoduulit latautuvat omien skeemojensa avulla."""
        self.write_registry(self.fixture_entries())
        result = load_registry(self.registry_path, self.temp_root)
        self.assertEqual(set(result.active_modules), {"tolkien", "indian-film-screening-watch"})
        self.assertEqual(result.invalid_modules, ())

    def test_inactive_module_is_not_loaded(self):
        """Passiivinen moduuli säilyy rekisterissä mutta ei päädy aktiivisiin määrityksiin."""
        entries = self.fixture_entries()
        entries[0]["status"] = "inactive"
        self.write_registry(entries)
        result = load_registry(self.registry_path, self.temp_root)
        statuses = {item.module_id: item.status for item in result.modules}
        self.assertEqual(statuses["tolkien"], "inactive")
        self.assertNotIn("tolkien", result.active_modules)
        self.assertIn("indian-film-screening-watch", result.active_modules)

    def test_one_invalid_module_does_not_block_another(self):
        """Virheellinen määritystiedosto eristetään ja toinen moduuli latautuu."""
        entries = self.fixture_entries()
        entries[0]["definition_version"] = "9.9.9"
        self.write_registry(entries)
        result = load_registry(self.registry_path, self.temp_root)
        self.assertIn("indian-film-screening-watch", result.active_modules)
        self.assertEqual([item.module_id for item in result.invalid_modules], ["tolkien"])

    def test_rejects_path_traversal_and_absolute_paths(self):
        """Rekisterimerkintä ei saa lukea tiedostoja repositorion ulkopuolelta."""
        entries = self.fixture_entries()
        entries[0]["path"] = "../outside.json"
        self.write_registry(entries)
        result = load_registry(self.registry_path, self.temp_root)
        self.assertEqual(result.modules[1].status, "invalid")
        entries[0]["path"] = str((self.temp_root / "outside.json").resolve())
        self.write_registry(entries)
        result = load_registry(self.registry_path, self.temp_root)
        self.assertEqual(result.modules[1].status, "invalid")

    def test_rejects_duplicate_module_ids(self):
        """Pysyvä tunniste voi esiintyä rekisterissä vain kerran."""
        entries = self.fixture_entries()
        entries[1]["module_id"] = entries[0]["module_id"]
        self.write_registry(entries)
        result = load_registry(self.registry_path, self.temp_root)
        self.assertEqual(len(result.invalid_modules), 2)
        self.assertEqual(result.active_modules, {})

    def test_rejects_registry_definition_mismatch(self):
        """Rekisterin tunnisteen, tyypin ja version pitää vastata tiedostoa."""
        entries = self.fixture_entries()
        entries[0]["module_type"] = "process"
        self.write_registry(entries)
        result = load_registry(self.registry_path, self.temp_root)
        self.assertEqual(result.modules[1].status, "invalid")

    def test_unknown_contract_version_is_invalid_but_isolated(self):
        """Tuntematon sopimusversio ei estä muiden merkintöjen tilan raportointia."""
        self.write_registry(self.fixture_entries(), contract_version="99.0.0")
        result = load_registry(self.registry_path, self.temp_root)
        self.assertEqual(len(result.invalid_modules), 2)
        self.assertEqual(result.active_modules, {})

    def test_invalid_module_file_does_not_abort_registry(self):
        """Virheellinen JSON tai puuttuva tiedosto tuottaa moduulikohtaisen virheen."""
        entries = self.fixture_entries()
        (self.temp_root / entries[0]["path"]).write_text("{", encoding="utf-8")
        self.write_registry(entries)
        result = load_registry(self.registry_path, self.temp_root)
        self.assertEqual(result.modules[1].status, "invalid")
        self.assertEqual(len(result.active_modules), 1)

    def test_registry_top_level_error_is_fatal(self):
        """Rekisterin ylätason rakenteen virhe ei ole turvallisesti eristettävissä."""
        self.write_registry(self.fixture_entries(), registry_version="99.0.0")
        with self.assertRaises(RegistryError):
            load_registry(self.registry_path, self.temp_root)

    def test_unknown_extension_schema_is_rejected_without_network_access(self):
        """Tuntematonta prosessilaajennusta ei haeta verkosta."""
        entries = self.fixture_entries()
        process_path = self.temp_root / entries[1]["path"]
        definition = json.loads(process_path.read_text(encoding="utf-8"))
        definition["process_extension"]["schema_uri"] = "https://example.invalid/remote.json"
        process_path.write_text(json.dumps(definition), encoding="utf-8")
        self.write_registry(entries)
        result = load_registry(self.registry_path, self.temp_root)
        self.assertEqual(result.modules[0].status, "invalid")
        self.assertEqual(len(result.active_modules), 1)

    def test_registry_order_does_not_change_result_order(self):
        """Tulokset palautetaan aina tunnisteen mukaan riippumatta syötetiedoston järjestyksestä."""
        entries = self.fixture_entries()
        self.write_registry(entries)
        first = [item.module_id for item in load_registry(self.registry_path, self.temp_root).modules]
        self.write_registry(list(reversed(entries)))
        second = [item.module_id for item in load_registry(self.registry_path, self.temp_root).modules]
        self.assertEqual(first, second)

    def test_rejects_duplicate_paths(self):
        """Samaa määritystiedostoa ei voi rekisteröidä kahdelle moduulille."""
        entries = self.fixture_entries()
        entries[1]["path"] = entries[0]["path"]
        self.write_registry(entries)
        result = load_registry(self.registry_path, self.temp_root)
        self.assertEqual(len(result.invalid_modules), 1)
        self.assertEqual(result.modules[1].status, "invalid")


if __name__ == "__main__":
    unittest.main()
