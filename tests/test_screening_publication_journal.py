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
        "source_check_run_id": "screening-source-run-20261120",
        "source_check_ended_at": END,
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


def state(last_success=START, last_period_start="2026-11-18T17:37:16+02:00",
          last_period_end=START, last_result="success", sources_checked=1):
    """Luo testiin seurantatilan onnistumispisteen ja viimeisimmän jakson."""
    return {
        "separate_screening_watch": {
            "last_successful_check": last_success,
            "last_period_start": last_period_start,
            "last_period_end": last_period_end,
            "last_result": last_result,
            "sources_checked": sources_checked,
        }
    }


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
        completed_state = state(END, START, END, "success", 1)
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


    def consistent_inputs(self, journal):
        """Luo päiväkirjaan täsmäävät lähde-, moduuli- ja RSS-aineistot."""
        import hashlib

        record = journal["runs"][-1]
        guids = record["feed"]["guids"]
        feed_bytes = (
            "<rss><channel>"
            + "".join(f"<item><guid>{guid}</guid></item>" for guid in guids)
            + "</channel></rss>"
        ).encode("utf-8")
        record["feed"]["sha256"] = hashlib.sha256(feed_bytes).hexdigest()
        source_run = {
            "run_id": record["source_check_run_id"],
            "task_id": "intialaiset_elokuvat_naytokset",
            "started_at": START,
            "ended_at": END,
            "status": "complete",
            "checked_source_ids": ["source-a"],
            "unchecked_sources": [{"source_id": "source-b", "reason": "Sivua ei saatu avattua."}],
            "registry_source_ids": ["source-a", "source-b"],
        }
        source_log = {
            "runs": [source_run],
            "latest_by_task": {"intialaiset_elokuvat_naytokset": END},
        }
        source_registry = {
            "updated_at": END,
            "sources": [
                {"source_id": "source-a", "last_checked_at": END},
                {"source_id": "source-b", "last_checked_at": None},
            ],
        }
        module_state = {
            "history": {"source_check_run_refs": [record["source_check_run_id"]]},
            "publication": {"feed_path": FEED_PATH, "guid_refs": guids},
        }
        return source_log, source_registry, module_state, feed_bytes

    def validate_consistent(self, journal, last_success=START):
        source_log, source_registry, module_state, feed_bytes = self.consistent_inputs(journal)
        state_data = state(last_success)
        if last_success == END:
            state_data = state(END, START, END, "success", 1)
        validate_journal(
            journal, state_data, feed_catalog(),
            source_log=source_log,
            source_registry=source_registry,
            module_state=module_state,
            feed_bytes=feed_bytes,
        )


    def test_cross_file_consistency_accepts_completed_run_and_checkpoint(self):
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
        self.validate_consistent(completed, END)

    def test_cross_file_consistency_rejects_completed_source_count_mismatch(self):
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
        source_log, source_registry, module_state, feed_bytes = self.consistent_inputs(completed)
        with self.assertRaises(ScreeningJournalError):
            validate_journal(
                completed, state(END, START, END, "success", 2), feed_catalog(),
                source_log=source_log, source_registry=source_registry,
                module_state=module_state, feed_bytes=feed_bytes,
            )

    def test_cross_file_consistency_accepts_matching_pending_run(self):
        journal = prepare_run(empty_journal(), prepared_record())
        self.validate_consistent(journal)

    def test_cross_file_consistency_rejects_rss_hash_mismatch(self):
        journal = prepare_run(empty_journal(), prepared_record())
        source_log, source_registry, module_state, feed_bytes = self.consistent_inputs(journal)
        feed_bytes += b" "
        with self.assertRaises(ScreeningJournalError):
            validate_journal(
                journal, state(), feed_catalog(),
                source_log=source_log, source_registry=source_registry,
                module_state=module_state, feed_bytes=feed_bytes,
            )

    def test_cross_file_consistency_rejects_rss_guid_mismatch(self):
        journal = prepare_run(empty_journal(), prepared_record())
        source_log, source_registry, module_state, feed_bytes = self.consistent_inputs(journal)
        module_state["publication"]["guid_refs"] = ["wrong-guid"]
        with self.assertRaises(ScreeningJournalError):
            validate_journal(
                journal, state(), feed_catalog(),
                source_log=source_log, source_registry=source_registry,
                module_state=module_state, feed_bytes=feed_bytes,
            )

    def test_cross_file_consistency_requires_source_run(self):
        journal = prepare_run(empty_journal(), prepared_record())
        source_log, source_registry, module_state, feed_bytes = self.consistent_inputs(journal)
        source_log["runs"] = []
        with self.assertRaises(ScreeningJournalError):
            validate_journal(
                journal, state(), feed_catalog(),
                source_log=source_log, source_registry=source_registry,
                module_state=module_state, feed_bytes=feed_bytes,
            )

    def test_cross_file_consistency_requires_latest_by_task(self):
        journal = prepare_run(empty_journal(), prepared_record())
        source_log, source_registry, module_state, feed_bytes = self.consistent_inputs(journal)
        source_log["latest_by_task"]["intialaiset_elokuvat_naytokset"] = START
        with self.assertRaises(ScreeningJournalError):
            validate_journal(
                journal, state(), feed_catalog(),
                source_log=source_log, source_registry=source_registry,
                module_state=module_state, feed_bytes=feed_bytes,
            )

    def test_cross_file_consistency_rejects_source_registry_timestamp_mismatch(self):
        journal = prepare_run(empty_journal(), prepared_record())
        source_log, source_registry, module_state, feed_bytes = self.consistent_inputs(journal)
        source_registry["sources"][0]["last_checked_at"] = "2026-11-18T23:00:00+02:00"
        with self.assertRaises(ScreeningJournalError):
            validate_journal(
                journal, state(), feed_catalog(),
                source_log=source_log, source_registry=source_registry,
                module_state=module_state, feed_bytes=feed_bytes,
            )

    def test_cross_file_consistency_requires_module_source_reference(self):
        journal = prepare_run(empty_journal(), prepared_record())
        source_log, source_registry, module_state, feed_bytes = self.consistent_inputs(journal)
        module_state["history"]["source_check_run_refs"] = []
        with self.assertRaises(ScreeningJournalError):
            validate_journal(
                journal, state(), feed_catalog(),
                source_log=source_log, source_registry=source_registry,
                module_state=module_state, feed_bytes=feed_bytes,
            )

    def test_cross_file_consistency_rejects_missing_registry_source(self):
        journal = prepare_run(empty_journal(), prepared_record())
        source_log, source_registry, module_state, feed_bytes = self.consistent_inputs(journal)
        source_registry["sources"].pop()
        with self.assertRaises(ScreeningJournalError):
            validate_journal(
                journal, state(), feed_catalog(),
                source_log=source_log, source_registry=source_registry,
                module_state=module_state, feed_bytes=feed_bytes,
            )


if __name__ == "__main__":
    unittest.main()
