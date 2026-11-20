"""Unit tests for the read-only Pages history checker."""
from datetime import datetime, timezone
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

from scripts.audit_pages_publication_history import (
    AuditError, deployment_manifest, parse_time, report_period_matches, status_for, validate_period,
)

START = datetime(2026, 11, 18, tzinfo=timezone.utc)
END = datetime(2026, 11, 19, 23, 59, tzinfo=timezone.utc)

class PagesHistoryAuditTests(unittest.TestCase):
    def test_timezone_is_required(self):
        with self.assertRaises(AuditError):
            parse_time("2026-11-18T00:00:00", "start")

    def test_reversed_period_is_rejected(self):
        with self.assertRaises(AuditError):
            validate_period(END, START)

    def test_manifest_object_and_json_payload_are_supported(self):
        obj = {"payload": {"manifest_type": "aiheseurain-rss-publication"}}
        encoded = {"payload": '{"manifest_type":"aiheseurain-rss-publication"}'}
        self.assertIsNotNone(deployment_manifest(obj))
        self.assertIsNotNone(deployment_manifest(encoded))

    def test_unrelated_and_malformed_payloads_are_ignored(self):
        self.assertIsNone(deployment_manifest({"payload": {"manifest_type": "other"}}))
        self.assertIsNone(deployment_manifest({"payload": "not-json"}))

    def test_explicit_period_text_matches(self):
        item = ET.fromstring("<item><description><![CDATA[<p>Seurantajakso: 2026-11-18 – 2026-11-19</p>]]></description></item>")
        self.assertTrue(report_period_matches(item, START, END))


    def test_finnish_date_format_in_report_period_matches(self):
        item = ET.fromstring("<item><description><![CDATA[<p>Seurantajakso: 18.11.2026 – 19.11.2026</p>]]></description></item>")
        self.assertTrue(report_period_matches(item, START, END))

    def test_pubdate_without_explicit_period_is_not_evidence(self):
        item = ET.fromstring("<item><pubDate>Wed, 18 Nov 2026 10:00:00 +0000</pubDate></item>")
        self.assertFalse(report_period_matches(item, START, END))

    def test_pubdate_outside_period_does_not_match(self):
        item = ET.fromstring("<item><pubDate>Mon, 16 Nov 2026 10:00:00 +0000</pubDate></item>")
        self.assertFalse(report_period_matches(item, START, END))

    def test_latest_deployment_status_is_selected(self):
        rows = [{"state": "success", "created_at": "2026-11-19T10:00:00Z"},
                {"state": "inactive", "created_at": "2026-11-20T10:00:00Z"}]
        with patch("scripts.audit_pages_publication_history.paginated", return_value=rows):
            self.assertEqual(status_for(42, "token")["state"], "inactive")

    def test_missing_status_is_not_success(self):
        with patch("scripts.audit_pages_publication_history.paginated", return_value=[]):
            self.assertEqual(status_for(42, "token")["state"], "no_status")

if __name__ == "__main__":
    unittest.main()
