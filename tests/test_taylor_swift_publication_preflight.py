"""Taylor Swift -julkaisutilan ennakkotarkistuksen fail-closed-testit."""
from __future__ import annotations

import unittest

from scripts.taylor_swift_publication_preflight import (
    PublicationPreflightError,
    assess_taylor_swift_publication_state,
)

PERIOD = {
    "start": "2026-11-18T00:00:00+02:00",
    "end": "2026-11-19T23:59:59+02:00",
}


def evidence(state="unpublished"):
    return {
        "module_id": "taylor-swift",
        "period": PERIOD,
        "observations": {
            channel: {
                "period": PERIOD,
                "check_status": "checked",
                "publication_status": state,
                "reference": f"verified:{channel}",
            }
            for channel in ("legacy", "runtime", "repository_rss", "pages")
        },
    }


class TaylorSwiftPublicationPreflightTests(unittest.TestCase):
    def test_all_four_checked_unpublished_channels_allow_shadow_only(self):
        result = assess_taylor_swift_publication_state(evidence())
        self.assertEqual(result["publication_state"], "unpublished")
        self.assertTrue(result["execution_allowed"])

    def test_any_confirmed_publication_blocks_execution(self):
        data = evidence()
        data["observations"]["repository_rss"]["publication_status"] = "published"
        result = assess_taylor_swift_publication_state(data)
        self.assertEqual(result["publication_state"], "conflict")
        self.assertFalse(result["execution_allowed"])

    def test_missing_runtime_branch_is_unknown_not_unpublished(self):
        data = evidence()
        data["observations"]["runtime"]["check_status"] = "unavailable"
        data["observations"]["runtime"]["publication_status"] = "unknown"
        result = assess_taylor_swift_publication_state(data)
        self.assertEqual(result["publication_state"], "unknown")
        self.assertFalse(result["execution_allowed"])
        self.assertIn("runtime", result["missing_or_unknown_channels"])

    def test_missing_pages_readback_is_unknown(self):
        data = evidence()
        data["observations"]["pages"]["check_status"] = "not_checked"
        data["observations"]["pages"]["publication_status"] = "unknown"
        result = assess_taylor_swift_publication_state(data)
        self.assertEqual(result["publication_state"], "unknown")
        self.assertFalse(result["execution_allowed"])

    def test_conflicting_publication_evidence_blocks_execution(self):
        data = evidence()
        data["observations"]["legacy"]["publication_status"] = "published"
        result = assess_taylor_swift_publication_state(data)
        self.assertEqual(result["publication_state"], "conflict")
        self.assertFalse(result["execution_allowed"])

    def test_malformed_observation_is_unknown_not_an_exception(self):
        data = evidence()
        data["observations"]["runtime"] = "branch not found"
        result = assess_taylor_swift_publication_state(data)
        self.assertEqual(result["publication_state"], "unknown")
        self.assertFalse(result["execution_allowed"])

    def test_period_mismatch_is_rejected(self):
        data = evidence()
        data["observations"]["runtime"]["period"] = {
            "start": "2026-11-17T00:00:00+02:00",
            "end": "2026-11-17T23:59:59+02:00",
        }
        with self.assertRaises(PublicationPreflightError):
            assess_taylor_swift_publication_state(data)

    def test_timezone_is_required(self):
        data = evidence()
        data["period"]["start"] = "2026-11-18T00:00:00"
        with self.assertRaises(PublicationPreflightError):
            assess_taylor_swift_publication_state(data)

    def test_other_module_is_rejected(self):
        data = evidence()
        data["module_id"] = "tolkien"
        with self.assertRaises(PublicationPreflightError):
            assess_taylor_swift_publication_state(data)


if __name__ == "__main__":
    unittest.main()
