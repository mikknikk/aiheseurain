"""Julkaisureitityksen ja kohdekohtaisen RSS-julkaisun testit."""
from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET

from scripts.module_run_adapters import AdapterError, RoutedReportPublisher
from scripts.module_orchestrator import PublicationReceipt
from scripts.publication_routing import (
    LocalRoutedRssPublisher, PublicationPlan, PublicationRoutingError,
    preview_publication_plan, resolve_publication_plan,
)


def context():
    """Muodosta pieni muistissa oleva rekisterijoukko ilman tuotantotietojen muuttamista."""
    return {
        "modules": {"demo": {"module_id": "demo", "status": "active"}},
        "targets": {
            "demo.film": (
                {"target_id": "demo.film", "status": "active"},
                {"target_id": "demo.film", "module_ref": {"module_id": "demo"}},
            )
        },
        "publications": {
            "demo.film.rss": (
                {"publication_id": "demo.film.rss", "status": "active"},
                {"publication_id": "demo.film.rss", "name": "Elokuvaraportit",
                 "status": "active", "destination": {"path": "feeds/film.xml",
                 "url": "https://example.invalid/film.xml"}},
            ),
            "demo.all.rss": (
                {"publication_id": "demo.all.rss", "status": "active"},
                {"publication_id": "demo.all.rss", "name": "Kaikki",
                 "status": "active", "destination": {"path": "feeds/all.xml",
                 "url": "https://example.invalid/all.xml"}},
            ),
        },
        "routing": {"routes": [
            {"route_id": "film-own", "module_ref": "demo", "target_ref": "demo.film",
             "publication_refs": ["demo.film.rss"], "observation_types": ["film-screening"],
             "status": "active"},
            {"route_id": "film-combined", "module_ref": "demo", "target_ref": "demo.film",
             "publication_refs": ["demo.all.rss"], "observation_types": ["film-screening"],
             "status": "active"},
            {"route_id": "inactive", "module_ref": "demo", "target_ref": "demo.film",
             "publication_refs": ["demo.film.rss"], "observation_types": ["film-festival"],
             "status": "inactive"},
        ]},
    }


class PublicationRoutingTests(unittest.TestCase):
    def test_one_report_routes_to_own_and_combined_feed(self):
        plan = resolve_publication_plan(
            context(), module_id="demo", target_id="demo.film", run_id="run-1",
            observation_types=["film-screening"],
        )
        self.assertEqual(plan.publication_ids, ("demo.all.rss", "demo.film.rss"))

    def test_preview_does_not_write_files(self):
        plan = resolve_publication_plan(
            context(), module_id="demo", target_id="demo.film", run_id="run-1",
            observation_types=["film-screening"],
        )
        with tempfile.TemporaryDirectory() as directory:
            preview = preview_publication_plan(plan)
            self.assertTrue(preview["would_publish"])
            self.assertEqual(list(Path(directory).iterdir()), [])

    def test_unknown_target_and_wrong_owner_are_rejected(self):
        with self.assertRaises(PublicationRoutingError):
            resolve_publication_plan(context(), module_id="demo", target_id="missing",
                                     run_id="run-1", observation_types=["film-screening"])
        with self.assertRaises(PublicationRoutingError):
            resolve_publication_plan(context(), module_id="other", target_id="demo.film",
                                     run_id="run-1", observation_types=["film-screening"])

    def test_no_matching_active_route_is_rejected(self):
        with self.assertRaises(PublicationRoutingError):
            resolve_publication_plan(context(), module_id="demo", target_id="demo.film",
                                     run_id="run-1", observation_types=["film-festival"])

    def test_inactive_publication_is_not_publishable(self):
        data = context()
        data["publications"]["demo.all.rss"][0]["status"] = "inactive"
        data["publications"]["demo.all.rss"][1]["status"] = "inactive"
        with self.assertRaises(PublicationRoutingError):
            resolve_publication_plan(data, module_id="demo", target_id="demo.film",
                                     run_id="run-1", observation_types=["film-screening"])

    def test_publication_is_idempotent_per_feed_and_conflict_safe(self):
        data = context()
        plan = resolve_publication_plan(data, module_id="demo", target_id="demo.film",
                                        run_id="run-1", observation_types=["film-screening"])
        with tempfile.TemporaryDirectory() as directory:
            publisher = LocalRoutedRssPublisher(Path(directory), data)
            first = publisher.publish_report(plan, "<p>Raportti</p>")
            second = publisher.publish_report(plan, "<p>Raportti</p>")
            self.assertEqual(first, second)
            for relative in ("feeds/film.xml", "feeds/all.xml"):
                root = ET.parse(Path(directory) / relative).getroot()
                self.assertEqual(len(root.findall("./channel/item")), 1)
            with self.assertRaises(PublicationRoutingError):
                publisher.publish_report(plan, "<p>Eri raportti</p>")

    def test_inactive_route_is_not_used(self):
        plan = resolve_publication_plan(context(), module_id="demo", target_id="demo.film",
                                        run_id="run-1", observation_types=["film-screening"])
        self.assertNotIn("inactive", plan.publication_ids)

    def test_orchestration_adapter_accepts_target_reports_and_verifies_receipt(self):
        data = context()
        with tempfile.TemporaryDirectory() as directory:
            publisher = RoutedReportPublisher(Path(directory), data)
            receipt = publisher.publish_target_reports("demo", "run-2", [{
                "target_id": "demo.film",
                "observation_types": ["film-screening"],
                "report_content": "<p>Kohderaportti</p>",
            }])
            self.assertIsInstance(receipt, PublicationReceipt)
            self.assertTrue(publisher.verify(receipt))
            self.assertEqual(receipt.published_items, 2)

    def test_orchestration_adapter_rejects_unknown_target_before_writing(self):
        data = context()
        with tempfile.TemporaryDirectory() as directory:
            publisher = RoutedReportPublisher(Path(directory), data)
            with self.assertRaises(AdapterError):
                publisher.publish_target_reports("demo", "run-2", [{
                    "target_id": "missing", "observation_types": ["film-screening"],
                    "report_content": "<p>Ei saa julkaista</p>",
                }])
            self.assertEqual(list(Path(directory).rglob("*.xml")), [])


if __name__ == "__main__":
    unittest.main()
