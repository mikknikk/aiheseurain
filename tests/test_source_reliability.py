"""Testaa Aiheseuraimen lähde- ja väitekohtaisten luotettavuusluokitusten rakennetta.

Testit tarkistavat sallitut arvot, katalogiviittaukset ja sen, että
lähdeluokka ja väitteen varmennustaso pysyvät eri kenttinä. Ne eivät
arvioi uutisväitteiden totuutta tai lähteiden todellista riippumattomuutta.
"""

from __future__ import annotations

import json
from pathlib import Path
import unittest

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
SOURCE_CLASSES = {"A", "B", "C", "D"}
CLAIM_STATUSES = {
    "ensisijaislahteella_vahvistettu",
    "riippumattomissa_toimituksellisissa_lahteissa_vahvistettu",
    "yhden_toimituksellisen_lahteen_raportoima",
    "nimettomaan_lahteeseen_perustuva",
    "huhu",
    "ristiriitainen_tai_selvittamaton",
}


def read_json(relative_path: str):
    """Lukee testissä käytettävän JSON-tiedoston projektin juuresta."""
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))


class ReliabilityClassificationTests(unittest.TestCase):
    """Varmistaa luotettavuusmallin rakenteen ja raportointitavan."""

    @classmethod
    def setUpClass(cls):
        cls.catalog = read_json("data/source-catalog.json")
        cls.catalog_schema = read_json("schemas/lahdekatalogi.schema.json")
        cls.gate_schema = read_json("schemas/julkaisuportti.schema.json")
        cls.sources_by_id = {source["id"]: source for source in cls.catalog["sources"]}

    def claim_schema(self):
        """Palauttaa porttiskeemasta väitearvion itsenäisen validointiskeeman."""
        return {
            "$schema": self.gate_schema["$schema"],
            "$defs": self.gate_schema["$defs"],
            "$ref": "#/$defs/claim_assessment",
        }

    def test_source_catalog_matches_schema_and_all_sources_have_allowed_class(self):
        """Kaikilla lähteillä on A–D-luokka, eikä source_type korvaa sitä."""
        jsonschema.validate(self.catalog, self.catalog_schema)
        self.assertEqual(self.catalog["schema_version"], 2)
        self.assertTrue(self.catalog["sources"])
        for source in self.catalog["sources"]:
            self.assertIn(source["reliability_class"], SOURCE_CLASSES)
            self.assertIn("source_type", source)
            self.assertNotEqual(source["source_type"], source["reliability_class"])

    def test_publication_gate_defines_separate_claim_and_source_enums(self):
        """Porttiskeema erottaa väitteen tilan lähteen yleisestä luokasta."""
        claim = self.gate_schema["$defs"]["claim_assessment"]
        statuses = set(claim["properties"]["verification_status"]["enum"])
        source_classes = set(
            claim["properties"]["sources"]["items"]["properties"]["source_class"]["enum"]
        )
        self.assertEqual(statuses, CLAIM_STATUSES)
        self.assertEqual(source_classes, SOURCE_CLASSES)
        self.assertNotEqual(statuses, source_classes)

    def test_claim_assessment_accepts_valid_catalog_source(self):
        """Kelvollinen väitearvio ja katalogiin kuuluva lähde hyväksytään."""
        source_id, source = next(iter(self.sources_by_id.items()))
        assessment = {
            "claim_id": "claim-test",
            "claim": "Esimerkkiväite.",
            "verification_status": "ensisijaislahteella_vahvistettu",
            "sources": [{
                "source_id": source_id,
                "source_class": source["reliability_class"],
                "source_role": "ensisijainen",
                "independence": "ei_sovellu",
            }],
        }
        jsonschema.validate(assessment, self.claim_schema())
        self.assertIn(source_id, self.sources_by_id)

    def test_invalid_claim_status_is_rejected(self):
        """Tuntematon väitteen varmennustaso ei läpäise porttiskeemaa."""
        assessment = {
            "claim_id": "claim-bad",
            "claim": "Testi.",
            "verification_status": "luotettava",
            "sources": [{
                "source_id": "test-source",
                "source_class": "A",
                "source_role": "ensisijainen",
                "independence": "ei_sovellu",
            }],
        }
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(assessment, self.claim_schema())

    def test_invalid_source_class_is_rejected(self):
        """Tuntematon lähdeluokka ei läpäise väitearvion skeemaa."""
        assessment = {
            "claim_id": "claim-bad-class",
            "claim": "Testi.",
            "verification_status": "huhu",
            "sources": [{
                "source_id": "test-source",
                "source_class": "E",
                "source_role": "muu",
                "independence": "tuntematon",
            }],
        }
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(assessment, self.claim_schema())

    def test_current_port_reports_remain_schema_valid(self):
        """Historialliset porttiraportit säilyvät kelvollisina ilman uutta kenttää."""
        for path in (ROOT / "reports/julkaisuportit").glob("*.json"):
            jsonschema.validate(
                json.loads(path.read_text(encoding="utf-8")),
                self.gate_schema,
            )

    def test_claim_assessment_sources_match_catalog_classes(self):
        """Porttiraportin lähdeluokan pitää vastata yhteistä lähdekatalogia."""
        for path in (ROOT / "reports/julkaisuportit").glob("*.json"):
            report = json.loads(path.read_text(encoding="utf-8"))
            for claim in report.get("claim_assessments", []):
                for source in claim["sources"]:
                    self.assertIn(source["source_id"], self.sources_by_id)
                    self.assertEqual(
                        source["source_class"],
                        self.sources_by_id[source["source_id"]]["reliability_class"],
                    )

    def test_documentation_uses_distinct_display_labels(self):
        """Ohjeissa lähteen luokka ja väitteen varmennus nimetään eri tavoin."""
        guide = (ROOT / "docs/luotettavuusluokitus.md").read_text(encoding="utf-8")
        self.assertIn("Väitteen varmennustaso:", guide)
        self.assertIn("Lähteen yleinen luotettavuusluokka:", guide)
        self.assertIn("ei ole artikkelin tai väitteen totuusarvosana", guide)
        self.assertIn("samaa alkuperäistä tiedotetta", guide)


if __name__ == "__main__":
    unittest.main()
