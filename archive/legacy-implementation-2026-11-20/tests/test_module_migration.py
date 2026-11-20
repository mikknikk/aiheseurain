"""Testaa nykyisten seurantojen moduulimigraation eheys ja passiivisuus."""
import unittest

from scripts.validate_module_migration import MODULE_TASKS, validate_migration


class ModuleMigrationTests(unittest.TestCase):
    """Varmista, että kymmenen moduulin siirto vastaa nykyisiä lähderekistereitä."""

    def test_all_current_modules_and_sources_are_consistent(self):
        """Kaikki kymmenen moduulia ja niiden lähdeviitteet validoituvat."""
        self.assertEqual(len(MODULE_TASKS), 10)
        self.assertEqual(validate_migration(), [])

    def test_migration_does_not_activate_modules(self):
        """Migraatio jättää tuotantorekisterin kaikki merkinnät passiivisiksi."""
        from scripts.module_registry import REGISTRY_PATH
        import json
        registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        self.assertEqual(len(registry["modules"]), 10)
        self.assertTrue(all(item["status"] == "inactive" for item in registry["modules"]))


if __name__ == "__main__":
    unittest.main()
