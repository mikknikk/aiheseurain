"""Testaa moduulikohtaisen tuotantoluparekisterin fail-closed-käytöksen."""
import json
from pathlib import Path
import tempfile
import unittest

from scripts.production_activation import (
    ProductionActivationError, load_production_activation,
)

ROOT = Path(__file__).resolve().parents[1]


class ProductionActivationTests(unittest.TestCase):
    def test_every_module_is_disabled_by_default(self):
        """Kaikkien aihe- ja prosessimoduulien tuotantolupa on pois päältä."""
        document = json.loads((ROOT / "data/module-production-activation.json").read_text(encoding="utf-8"))
        self.assertTrue(document["modules"])
        self.assertTrue(all(value is False for value in document["modules"].values()))
        self.assertFalse(load_production_activation("tolkien"))

    def test_unknown_module_is_rejected(self):
        """Tuntematon moduuli ei saa tuotantolupaa."""
        with self.assertRaises(ProductionActivationError):
            load_production_activation("unknown-topic")

    def test_missing_activation_file_fails_closed(self):
        """Puuttuva aktivointitiedosto ei koskaan muutu hiljaiseksi sallinnaksi."""
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ProductionActivationError):
                load_production_activation("tolkien", activation_path=Path(directory) / "missing.json")

    def test_registry_mismatch_fails_closed(self):
        """Puuttuva tai ylimääräinen moduuli aktivointitiedostossa hylätään."""
        document = json.loads((ROOT / "data/module-production-activation.json").read_text(encoding="utf-8"))
        document["modules"].pop("tolkien")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "activation.json"
            path.write_text(json.dumps(document), encoding="utf-8")
            with self.assertRaises(ProductionActivationError):
                load_production_activation("tolkien", activation_path=path)

    def test_process_module_cannot_be_enabled_for_topic_publication(self):
        """Erillinen näytösvahti/prosessimoduuli ei voi käyttää topic-julkaisulupaa."""
        document = json.loads((ROOT / "data/module-production-activation.json").read_text(encoding="utf-8"))
        document["modules"]["indian-film-screening-watch"] = True
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "activation.json"
            path.write_text(json.dumps(document), encoding="utf-8")
            with self.assertRaises(ProductionActivationError):
                load_production_activation("tolkien", activation_path=path)


if __name__ == "__main__":
    unittest.main()
