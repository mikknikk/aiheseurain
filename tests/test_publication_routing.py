"""Julkaisureitityksen ja kohdekohtaisen RSS-julkaisun testit."""
from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET

from scripts.module_run_adapters import AdapterError, RoutedReportPublisher
from scripts.module_orchestrator import PublicationReceipt, TargetReport
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
            ),
            "demo.festival": (
                {"target_id": "demo.festival", "status": "active"},
                {"target_id": "demo.festival", "module_ref": {"module_id": "demo"}},
            ),
        },
        "publications": {
            "demo.film.rss": (
                {"publication_id": "demo.film.rss", "status": "active"},
                {"publication_id": "demo.film.rss", "name": "Elokuvaraportit",
                 "status": "active", "destination": {"path": "feeds/film.xml",
                 "url": "https://example.invalid/film.xml"}},
            ),
            "demo.festival.rss": (
                {"publication_id": "demo.festival.rss", "status": "active"},
                {"publication_id": "demo.festival.rss", "name": "Festivaalit",
                 "status": "active", "destination": {"path": "feeds/festival.xml",
                 "url": "https://example.invalid/festival.xml"}},
            ),
        },
        "routing": {"routes": [
            {"route_id": "film-own", "module_ref": "demo", "target_ref": "demo.film",
             "publication_refs": ["demo.film.rss"], "observation_types": ["film-screening"],
             "status": "active"},
            {"route_id": "festival-own", "module_ref": "demo", "target_ref": "demo.festival",
             "publication_refs": ["demo.festival.rss"],
             "observation_types": ["film-festival"], "status": "active"},
            {"route_id": "inactive", "module_ref": "demo", "target_ref": "demo.film",
             "publication_refs": ["demo.film.rss"], "observation_types": ["film-festival"],
             "status": "inactive"},
        ]},
    }


class PublicationRoutingTests(unittest.TestCase):
    def test_one_report_routes_only_to_its_own_feed(self):
        plan = resolve_publication_plan(
            context(), module_id="demo", target_id="demo.film", run_id="run-1",
            observation_types=["film-screening"],
        )
        self.assertEqual(plan.publication_ids, ("demo.film.rss",))

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
            for relative in ("feeds/film.xml",):
                root = ET.parse(Path(directory) / relative).getroot()
                self.assertEqual(len(root.findall("./channel/item")), 1)
            with self.assertRaises(PublicationRoutingError):
                publisher.publish_report(plan, "<p>Eri raportti</p>")

    def test_inactive_route_is_not_used(self):
        plan = resolve_publication_plan(context(), module_id="demo", target_id="demo.film",
                                        run_id="run-1", observation_types=["film-screening"])
        self.assertNotIn("inactive", plan.publication_ids)
    def test_inactive_module_and_target_can_only_be_previewed(self):
        data = context()
        data["modules"]["demo"]["status"] = "inactive"
        data["targets"]["demo.film"][0]["status"] = "inactive"
        plan = resolve_publication_plan(
            data, module_id="demo", target_id="demo.film", run_id="run-3",
            observation_types=["film-screening"], include_inactive=True,
        )
        preview = preview_publication_plan(plan)
        self.assertFalse(preview["would_publish"])
        self.assertIn("module:demo", preview["inactive_refs"])
        self.assertIn("target:demo.film", preview["inactive_refs"])
        with tempfile.TemporaryDirectory() as directory:
            publisher = LocalRoutedRssPublisher(Path(directory), data)
            with self.assertRaises(PublicationRoutingError):
                publisher.publish_report(plan, "<p>Ei julkaista</p>")
            self.assertEqual(list(Path(directory).rglob("*.xml")), [])


    def test_two_target_reports_publish_only_to_their_own_feeds(self):
        data = context()
        reports = [
            TargetReport("demo.film", "1.0.0", ("film-screening",), "2026-11-18T00:00:00+02:00",
                         "2026-11-18T22:00:00+02:00", "2026-11-18T22:00:00+02:00",
                         "<p>Elokuvanäytökset</p>").to_publication_dict(),
            TargetReport("demo.festival", "1.0.0", ("film-festival",), "2026-11-18T00:00:00+02:00",
                         "2026-11-18T22:00:00+02:00", "2026-11-18T22:00:00+02:00",
                         "<p>Festivaalit</p>").to_publication_dict(),
        ]
        with tempfile.TemporaryDirectory() as directory:
            publisher = RoutedReportPublisher(Path(directory), data)
            receipt = publisher.publish_target_reports("demo", "run-two-targets", reports)
            self.assertTrue(publisher.verify(receipt))
            self.assertFalse((Path(directory) / "feeds/all.xml").exists())
            own_film = ET.parse(Path(directory) / "feeds/film.xml").getroot()
            own_festival = ET.parse(Path(directory) / "feeds/festival.xml").getroot()
            self.assertEqual(len(own_film.findall("./channel/item")), 1)
            self.assertEqual(len(own_festival.findall("./channel/item")), 1)

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
            self.assertEqual(receipt.published_items, 1)
    def test_orchestration_adapter_detects_tampered_feed_after_publish(self):
        data = context()
        with tempfile.TemporaryDirectory() as directory:
            publisher = RoutedReportPublisher(Path(directory), data)
            receipt = publisher.publish_target_reports("demo", "run-4", [{
                "target_id": "demo.film", "observation_types": ["film-screening"],
                "report_content": "<p>Alkuperäinen</p>",
            }])
            path = Path(directory) / "feeds/film.xml"
            root = ET.parse(path).getroot()
            root.find("./channel/item/description").text = "<p>Muutettu</p>"
            path.write_bytes(ET.tostring(root, encoding="utf-8", xml_declaration=True))
            self.assertFalse(publisher.verify(receipt))

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
