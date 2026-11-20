"""Aiheajojen eristyksen regressiotestit: pakettivuodot, omistajuus ja rajapinta."""
from __future__ import annotations

import inspect
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from scripts.module_input_bundle import (
    ModuleInputBundleError,
    build_module_input_bundle,
    bundle_to_json,
)
from scripts.isolated_module_runner import run_isolated_module

ROOT = Path(__file__).resolve().parents[1]


class ModuleIsolationGuardTests(unittest.TestCase):
    """Testaa kielteiset tapaukset erillisessä kopiossa muuttamatta työtiedostoa."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        # Kopioi vain paketin muodostamiseen tarvittavat data- ja moduulitiedostot.
        shutil.copytree(ROOT / "data", self.root / "data")
        shutil.copytree(ROOT / "modules", self.root / "modules")

    def tearDown(self):
        self.temp.cleanup()

    def read_json(self, relative_path):
        return json.loads((self.root / relative_path).read_text(encoding="utf-8"))

    def write_json(self, relative_path, value):
        (self.root / relative_path).write_text(
            json.dumps(value, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def build(self):
        return build_module_input_bundle(
            "tolkien",
            task_id="tolkien",
            run_id="isolation-guard-test",
            period_start="2026-11-19T00:00:00+02:00",
            period_end="2026-11-19T23:59:59+02:00",
            root=self.root,
        )

    def test_other_module_content_and_unreferenced_catalog_sources_never_leak(self):
        """Toisen moduulin salaiset merkkijonot eivät saa päätyä pakettiin."""
        marker = "MUUMIT_PRIVATE_SENTINEL_201"
        other_module = self.read_json("modules/topics/muumit/module.json")
        other_module["description"] += " " + marker
        self.write_json("modules/topics/muumit/module.json", other_module)

        catalog = self.read_json("data/source-catalog.json")
        catalog["sources"].append({
            "id": "other-topic-private-source-201",
            "name": marker,
            "url": "https://example.invalid/private",
            "language_regions": ["xx"],
            "source_type": "editorial",
            "regions": ["GLOBAL"],
            "reliability_class": "C",
        })
        self.write_json("data/source-catalog.json", catalog)

        serialized = bundle_to_json(self.build())
        self.assertNotIn(marker, serialized)
        self.assertNotIn("other-topic-private-source-201", serialized)
        self.assertNotIn("indian-film-screening-watch", serialized)

    def test_registry_cannot_redirect_module_to_another_modules_definition(self):
        """Rekisterin väärä moduulipolku hylätään ennen tietojen luovutusta."""
        registry = self.read_json("data/module-registry.json")
        entry = next(item for item in registry["modules"] if item["module_id"] == "tolkien")
        entry["path"] = "modules/topics/muumit/module.json"
        self.write_json("data/module-registry.json", registry)

        with self.assertRaises(ModuleInputBundleError):
            self.build()

    def test_path_traversal_in_module_definition_is_rejected(self):
        """Moduulirekisterin polku ei saa poistua repositorion juuresta."""
        registry = self.read_json("data/module-registry.json")
        entry = next(item for item in registry["modules"] if item["module_id"] == "tolkien")
        entry["path"] = "../outside/module.json"
        self.write_json("data/module-registry.json", registry)

        with self.assertRaises(ModuleInputBundleError):
            self.build()

    def test_target_owned_by_another_module_is_rejected(self):
        """Kohteen module_ref-omistajuuden on vastattava pyydettyä moduulia."""
        target = self.read_json("data/targets/tolkien.j-r-r-tolkien.json")
        target["module_ref"]["module_id"] = "muumit"
        self.write_json("data/targets/tolkien.j-r-r-tolkien.json", target)

        with self.assertRaises(ModuleInputBundleError):
            self.build()

    def test_module_task_mismatch_is_rejected(self):
        """Toisen tehtävän käyttörekisteriä ei voi liittää Tolkien-moduuliin."""
        with self.assertRaises(ModuleInputBundleError):
            build_module_input_bundle(
                "tolkien",
                task_id="muumit",
                run_id="wrong-task",
                period_start="2026-11-19T00:00:00+02:00",
                period_end="2026-11-19T23:59:59+02:00",
                root=self.root,
            )

    def test_runner_public_api_does_not_accept_repository_or_global_registry_paths(self):
        """Runnerille ei voi antaa repojuurta eikä yhteisten rekisterien polkuja."""
        parameters = set(inspect.signature(run_isolated_module).parameters)
        self.assertEqual(
            parameters,
            {"bundle", "runner_source", "timeout_seconds", "bubblewrap_path"},
        )
        self.assertFalse(
            {"root", "repository_root", "module_registry_path", "source_catalog_path"}
            & parameters
        )


if __name__ == "__main__":
    unittest.main()
