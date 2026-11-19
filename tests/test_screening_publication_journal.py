"""Näytösvahdin julkaisupäiväkirjan palautumis- ja idempotenssitestit."""
import copy
import unittest

from scripts.screening_publication_journal import (
    ScreeningJournalError, complete_run, prepare_run, validate_journal,
)


START = "2026-11-19T06:10:58+02:00"
END = "2026-11-20T06:10:58+02:00"
RUN_ID = "intialaiset_elokuvat_naytokset-20261120T061058-0200"
FEED_PATH = "feeds/intialaisten-elokuvien-naytokset.xml"


def empty_journal():
    """Palauta skeeman mukainen tyhjä päiväkirja."""
    return {
        "schema_version": 1,
        "task_id": "intialaiset_elokuvat_naytokset",
        "timezone": "Europe/Helsinki",
        "runs": [],
    }


def prepared_record(run_id=RUN_ID):
    """Muodosta testiin yksi valmisteltu, vielä julkaisematon ajo."""
    return {
        "run_id": run_id,
        "period": {"start": START, "end": END},
        "prepared_at": END,
        "phase": "prepared",
        "feed": {
            "path": FEED_PATH,
            "sha256": "a" * 64,
            "item_count": 2,
            "guids": ["urn:aiheseurain:screening:one", "urn:aiheseurain:screening:two"],
        },
        "publication": {"commit_sha": None, "deployment_id": None, "verified_at": None},
        "synchronization": {"commit_sha": None},
    }


def feed_catalog():
    """Kuvaa vain näytösvahtia vastaavan katalogimerkinnän."""
    return [{"id": "intialaisten-elokuvien-naytokset", "type": "screening", "path": FEED_PATH}]


def state(last_success=START):
    """Luo testiin seurantatilan onnistumispisteen."""
    return {"separate_screening_watch": {"last_successful_check": last_success}}


class ScreeningPublicationJournalTests(unittest.TestCase):
    def test_empty_journal_is_valid(self):
        validate_journal(empty_journal(), state(), feed_catalog())

    def test_preparing_same_run_is_idempotent(self):
        journal = empty_journal()
        record = prepared_record()
        first = prepare_run(journal, record)
        second = prepare_run(first, record)
        self.assertEqual(first, second)
        self.assertEqual(len(second["runs"]), 1)

    def test_same_run_id_with_different_feed_content_is_rejected(self):
        first = prepare_run(empty_journal(), prepared_record())
        conflicting = prepared_record()
        conflicting["feed"]["sha256"] = "b" * 64
        with self.assertRaises(ScreeningJournalError):
            prepare_run(first, conflicting)

    def test_second_pending_run_is_rejected(self):
        first = prepare_run(empty_journal(), prepared_record())
        with self.assertRaises(ScreeningJournalError):
            prepare_run(first, prepared_record("another-screening-run-002"))

    def test_pending_run_requires_old_success_checkpoint_to_remain_unchanged(self):
        journal = prepare_run(empty_journal(), prepared_record())
        validate_journal(journal, state(START), feed_catalog())
        with self.assertRaises(ScreeningJournalError):
            validate_journal(journal, state(END), feed_catalog())

    def test_completed_run_requires_publication_and_sync_receipts(self):
        journal = prepare_run(empty_journal(), prepared_record())
        completed = complete_run(
            journal, RUN_ID,
            publication_commit_sha="1" * 40,
            deployment_id=12345,
            rss_verified_at="2026-11-20T07:00:00+02:00",
            synchronization_commit_sha="2" * 40,
            rss_verified=True,
            state_synchronized=True,
        )
        completed_state = state(END)
        validate_journal(completed, completed_state, feed_catalog())
        self.assertEqual(completed["runs"][0]["phase"], "completed")

    def test_completion_is_rejected_without_both_verifications(self):
        journal = prepare_run(empty_journal(), prepared_record())
        with self.assertRaises(ScreeningJournalError):
            complete_run(
                journal, RUN_ID,
                publication_commit_sha="1" * 40,
                deployment_id=12345,
                rss_verified_at="2026-11-20T07:00:00+02:00",
                synchronization_commit_sha="2" * 40,
                rss_verified=True,
                state_synchronized=False,
            )

    def test_completing_same_run_with_same_receipts_is_idempotent(self):
        journal = prepare_run(empty_journal(), prepared_record())
        kwargs = {
            "publication_commit_sha": "1" * 40,
            "deployment_id": 12345,
            "rss_verified_at": "2026-11-20T07:00:00+02:00",
            "synchronization_commit_sha": "2" * 40,
            "rss_verified": True,
            "state_synchronized": True,
        }
        first = complete_run(journal, RUN_ID, **kwargs)
        second = complete_run(first, RUN_ID, **kwargs)
        self.assertEqual(first, second)

    def test_completed_run_rejects_different_receipt_on_retry(self):
        journal = prepare_run(empty_journal(), prepared_record())
        first = complete_run(
            journal, RUN_ID,
            publication_commit_sha="1" * 40,
            deployment_id=12345,
            rss_verified_at="2026-11-20T07:00:00+02:00",
            synchronization_commit_sha="2" * 40,
            rss_verified=True,
            state_synchronized=True,
        )
        with self.assertRaises(ScreeningJournalError):
            complete_run(
                first, RUN_ID,
                publication_commit_sha="3" * 40,
                deployment_id=12345,
                rss_verified_at="2026-11-20T07:00:00+02:00",
                synchronization_commit_sha="2" * 40,
                rss_verified=True,
                state_synchronized=True,
            )

    def test_duplicate_run_ids_are_rejected_by_validator(self):
        journal = empty_journal()
        journal["runs"] = [prepared_record(), copy.deepcopy(prepared_record())]
        with self.assertRaises(ScreeningJournalError):
            validate_journal(journal, state(), feed_catalog())

    def test_completed_run_requires_checkpoint_to_match_period_end(self):
        journal = prepare_run(empty_journal(), prepared_record())
        completed = complete_run(
            journal, RUN_ID,
            publication_commit_sha="1" * 40,
            deployment_id=12345,
            rss_verified_at="2026-11-20T07:00:00+02:00",
            synchronization_commit_sha="2" * 40,
            rss_verified=True,
            state_synchronized=True,
        )
        with self.assertRaises(ScreeningJournalError):
            validate_journal(completed, state(START), feed_catalog())


if __name__ == "__main__":
    unittest.main()
