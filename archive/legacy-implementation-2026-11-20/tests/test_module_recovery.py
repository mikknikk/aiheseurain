"""Varmistaa moduuliajon palautumispäätökset kaikissa julkaisuvaiheissa."""
import unittest

from scripts.module_recovery import ModuleRecoveryError, recovery_action


def manifest(phase="prepared"):
    return {"module_id": "tolkien", "run_id": "recovery-run-001", "phase": phase}


class ModuleRecoveryTests(unittest.TestCase):
    def test_empty_journal_starts_only_when_all_prior_state_is_clear(self):
        args = dict(publication_status="not_started", deployment_status="not_started",
                    public_feed_matches=None, checkpoint_status="not_advanced",
                    legacy_period_status="absent")
        self.assertEqual(recovery_action(None, **args), "start_new_run")
        self.assertEqual(
            recovery_action(None, **{**args, "legacy_period_status": "present"}),
            "legacy_period_already_published",
        )

    def test_open_rss_pr_waits_and_never_falls_back_to_legacy(self):
        self.assertEqual(
            recovery_action(manifest(), publication_status="open", deployment_status="not_started",
                            public_feed_matches=False, checkpoint_status="not_advanced",
                            legacy_period_status="absent", legacy_fallback_authorized=True),
            "wait_for_rss_pr",
        )

    def test_prepared_run_requires_explicit_approval_before_legacy_fallback(self):
        args = dict(publication_status="closed_unmerged", deployment_status="not_started",
                    public_feed_matches=False, checkpoint_status="not_advanced",
                    legacy_period_status="absent")
        self.assertEqual(recovery_action(manifest(), **args), "legacy_fallback_requires_approval")
        self.assertEqual(
            recovery_action(manifest(), **args, legacy_fallback_authorized=True),
            "return_to_legacy_path",
        )

    def test_legacy_publication_blocks_open_or_merged_module_publication(self):
        for publication_status in ("open", "merged", "unknown"):
            with self.subTest(publication_status=publication_status):
                self.assertEqual(
                    recovery_action(manifest(), publication_status=publication_status,
                                    deployment_status="not_started", public_feed_matches=False,
                                    checkpoint_status="not_advanced", legacy_period_status="present",
                                    legacy_fallback_authorized=True),
                    "manual_review" if publication_status != "unknown" else "inspect_external_state",
                )

    def test_legacy_fallback_is_blocked_when_old_path_already_published(self):
        self.assertEqual(
            recovery_action(manifest(), publication_status="closed_unmerged",
                            deployment_status="not_started", public_feed_matches=False,
                            checkpoint_status="not_advanced", legacy_period_status="present",
                            legacy_fallback_authorized=True),
            "legacy_period_already_published",
        )

    def test_unknown_legacy_period_blocks_fallback(self):
        self.assertEqual(
            recovery_action(manifest(), publication_status="closed_unmerged",
                            deployment_status="not_started", public_feed_matches=False,
                            checkpoint_status="not_advanced", legacy_period_status="unknown",
                            legacy_fallback_authorized=True),
            "inspect_external_state",
        )

    def test_merged_publication_waits_for_pages_deployment(self):
        for deployment_status in ("not_started", "in_progress"):
            with self.subTest(deployment_status=deployment_status):
                self.assertEqual(
                    recovery_action(manifest(), publication_status="merged",
                                    deployment_status=deployment_status, public_feed_matches=False,
                                    checkpoint_status="not_advanced", legacy_period_status="absent"),
                    "wait_for_pages",
                )

    def test_merged_publication_advances_manifest_only_after_public_backread(self):
        self.assertEqual(
            recovery_action(manifest(), publication_status="merged", deployment_status="success",
                            public_feed_matches=True, checkpoint_status="not_advanced",
                            legacy_period_status="absent"),
            "advance_publication_journal",
        )
        self.assertEqual(
            recovery_action(manifest(), publication_status="merged", deployment_status="success",
                            public_feed_matches=False, checkpoint_status="not_advanced",
                            legacy_period_status="absent"),
            "reconcile_publication",
        )
        self.assertEqual(
            recovery_action(manifest(), publication_status="merged", deployment_status="failure",
                            public_feed_matches=False, checkpoint_status="not_advanced",
                            legacy_period_status="absent"),
            "retry_pages_publication",
        )

    def test_published_phase_resumes_artifacts_after_verified_rss(self):
        self.assertEqual(
            recovery_action(manifest("published"), publication_status="merged",
                            deployment_status="success", public_feed_matches=True,
                            checkpoint_status="not_advanced", legacy_period_status="absent"),
            "resume_artifact_persistence",
        )

    def test_artifacts_phase_resumes_checkpoint_or_records_ambiguous_checkpoint_write(self):
        args = dict(publication_status="merged", deployment_status="success",
                    public_feed_matches=True, legacy_period_status="absent")
        self.assertEqual(
            recovery_action(manifest("artifacts_persisted"), **args,
                            checkpoint_status="not_advanced"),
            "resume_checkpoint",
        )
        self.assertEqual(
            recovery_action(manifest("artifacts_persisted"), **args,
                            checkpoint_status="advanced"),
            "advance_checkpoint_journal",
        )

    def test_completed_phase_requires_matching_checkpoint_and_publication(self):
        args = dict(publication_status="merged", deployment_status="success",
                    public_feed_matches=True, legacy_period_status="absent")
        self.assertEqual(
            recovery_action(manifest("checkpoint_updated"), **args,
                            checkpoint_status="advanced"),
            "verify_completed_run",
        )
        self.assertEqual(
            recovery_action(manifest("checkpoint_updated"), publication_status="merged",
                            deployment_status="success", public_feed_matches=False,
                            checkpoint_status="advanced", legacy_period_status="absent"),
            "reconcile_completed_publication",
        )

    def test_conflicting_checkpoint_requires_manual_review(self):
        self.assertEqual(
            recovery_action(manifest("artifacts_persisted"), publication_status="merged",
                            deployment_status="success", public_feed_matches=True,
                            checkpoint_status="conflict", legacy_period_status="absent"),
            "manual_review",
        )

    def test_impossible_phase_orderings_are_rejected(self):
        with self.assertRaises(ModuleRecoveryError):
            recovery_action(manifest("prepared"), publication_status="merged",
                            deployment_status="success", public_feed_matches=True,
                            checkpoint_status="advanced", legacy_period_status="absent")
        with self.assertRaises(ModuleRecoveryError):
            recovery_action(manifest("published"), publication_status="merged",
                            deployment_status="success", public_feed_matches=True,
                            checkpoint_status="advanced", legacy_period_status="absent")
        with self.assertRaises(ModuleRecoveryError):
            recovery_action(manifest("checkpoint_updated"), publication_status="merged",
                            deployment_status="success", public_feed_matches=True,
                            checkpoint_status="not_advanced", legacy_period_status="absent")

    def test_unknown_states_are_rejected(self):
        with self.assertRaises(ModuleRecoveryError):
            recovery_action(manifest(), publication_status="pending", deployment_status="not_started",
                            public_feed_matches=False, checkpoint_status="not_advanced",
                            legacy_period_status="absent")
        with self.assertRaises(ModuleRecoveryError):
            recovery_action(manifest(), publication_status="not_started", deployment_status="not_started",
                            public_feed_matches=False, checkpoint_status="not_advanced",
                            legacy_period_status="missing")
        with self.assertRaises(ModuleRecoveryError):
            recovery_action(manifest(), publication_status="merged", deployment_status="pending",
                            public_feed_matches=False, checkpoint_status="not_advanced",
                            legacy_period_status="absent")


if __name__ == "__main__":
    unittest.main()
