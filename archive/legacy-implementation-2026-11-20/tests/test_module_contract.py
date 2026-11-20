"""Yksikkötestit seurantamoduulien tietosopimukselle.

Testit kutsuvat samaa validointia, jota CI käyttää. Erillinen skripti pitää
tarkistuksen ajettavana myös ilman testikehyksen erikoisasetuksia.
"""

import unittest

from scripts.validate_module_contract import validate_examples


class ModuleContractTests(unittest.TestCase):
    """Varmista moduulisopimuksen esimerkit ja negatiiviset testit."""

    def test_module_contract_examples_and_rejections(self):
        """Molempien moduulityyppien esimerkit hyväksytään ja virhetapaukset hylätään."""
        validate_examples()


if __name__ == "__main__":
    unittest.main()
