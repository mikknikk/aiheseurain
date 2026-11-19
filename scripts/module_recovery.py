"""Moduuliajon palautumisen päätöslogiikka ilman ulkoisia sivuvaikutuksia.

Funktio arvioi manifestin, RSS-julkaisun, julkisen takaisinluvun ja checkpointin
yhteensopivuuden. Se ei käynnistä vanhaa tai uutta automaatiota eikä muuta
julkaisua, ajastuksia, käyttöoikeuksia tai moduulin tilaa.
"""
from __future__ import annotations

from typing import Any


class ModuleRecoveryError(ValueError):
    """Palautumisen lähtötiedot ovat virheelliset tai keskenään mahdottomat."""


PUBLICATION_STATES = {"not_started", "open", "closed_unmerged", "merged", "unknown"}
CHECKPOINT_STATES = {"not_advanced", "advanced", "unknown", "conflict"}
LEGACY_STATES = {"absent", "present", "unknown"}
MANIFEST_PHASES = {"prepared", "published", "artifacts_persisted", "checkpoint_updated"}


def recovery_action(
    manifest: dict[str, Any] | None,
    *,
    publication_status: str,
    public_feed_matches: bool | None,
    checkpoint_status: str,
    legacy_period_status: str,
    legacy_fallback_authorized: bool = False,
) -> str:
    """Palauta turvallinen seuraava toimi keskeytyneen topic-ajon perusteella.

    checkpoint_status:
    - not_advanced: moduulin nykyinen tila vastaa manifestin lähtö-SHA:ta;
    - advanced: viimeisin onnistunut checkpoint on tämän run_id:n tulos;
    - conflict: tila on muuttunut jonkin muun ajon vuoksi;
    - unknown: tilaa ei voitu lukea luotettavasti.

    legacy_period_status kertoo, onko vanha raportointipolku jo julkaissut
    kyseisen moduulin seurantajakson. Vanhaan polkuun paluu vaatii sekä
    varmennetun julkaisemattomuuden että erillisen eksplisiittisen hyväksynnän.
    Päätösfunktio ei itse käynnistä kumpaakaan polkua.
    """
    if publication_status not in PUBLICATION_STATES:
        raise ModuleRecoveryError("Tuntematon RSS-julkaisun tila.")
    if checkpoint_status not in CHECKPOINT_STATES:
        raise ModuleRecoveryError("Tuntematon checkpointin tila.")
    if legacy_period_status not in LEGACY_STATES:
        raise ModuleRecoveryError("Tuntematon vanhan raportointipolun julkaisutila.")
    if public_feed_matches not in (True, False, None):
        raise ModuleRecoveryError("Julkisen RSS-takaisinluvun tulos on virheellinen.")
    if not isinstance(legacy_fallback_authorized, bool):
        raise ModuleRecoveryError("Vanhaan raportointipolkuun paluun hyväksynnän pitää olla boolean.")

    if manifest is None:
        if checkpoint_status == "advanced":
            raise ModuleRecoveryError("Checkpoint on edennyt ilman julkaisumanifestia.")
        if checkpoint_status != "not_advanced" or publication_status != "not_started":
            return "inspect_external_state"
        if public_feed_matches is True:
            return "inspect_external_state"
        if legacy_period_status == "present":
            return "legacy_period_already_published"
        if legacy_period_status == "unknown":
            return "inspect_external_state"
        return "start_new_run"

    if not isinstance(manifest, dict):
        raise ModuleRecoveryError("Julkaisumanifestin pitää olla JSON-olio.")
    phase = manifest.get("phase")
    module_id, run_id = manifest.get("module_id"), manifest.get("run_id")
    if phase not in MANIFEST_PHASES or not isinstance(module_id, str) or not module_id or not isinstance(run_id, str) or not run_id:
        raise ModuleRecoveryError("Julkaisumanifestin vaihe tai tunnisteet ovat virheellisiä.")

    if checkpoint_status == "conflict":
        return "manual_review"
    if checkpoint_status == "unknown" or publication_status == "unknown":
        return "inspect_external_state"

    if phase == "prepared":
        if checkpoint_status == "advanced":
            raise ModuleRecoveryError("Checkpoint on edennyt ennen julkaisumanifestin published-vaihetta.")
        if publication_status == "open":
            return "wait_for_rss_pr" if public_feed_matches is False else "inspect_external_state"
        if publication_status == "merged":
            if public_feed_matches is True:
                return "advance_publication_journal"
            return "reconcile_publication" if public_feed_matches is False else "inspect_external_state"
        if publication_status in {"not_started", "closed_unmerged"}:
            if public_feed_matches is True:
                return "inspect_external_state"
            if legacy_period_status == "present":
                return "legacy_period_already_published"
            if legacy_period_status == "unknown" or public_feed_matches is None:
                return "inspect_external_state"
            if legacy_fallback_authorized:
                return "return_to_legacy_path"
            return "legacy_fallback_requires_approval"

    if phase == "published":
        if checkpoint_status == "advanced":
            raise ModuleRecoveryError("Checkpoint on edennyt ennen artefaktien päiväkirjamerkintää.")
        if publication_status != "merged":
            return "inspect_external_state"
        if public_feed_matches is True:
            return "resume_artifact_persistence"
        return "reconcile_publication" if public_feed_matches is False else "inspect_external_state"

    if phase == "artifacts_persisted":
        if publication_status != "merged":
            return "inspect_external_state"
        if public_feed_matches is not True:
            return "reconcile_publication" if public_feed_matches is False else "inspect_external_state"
        if checkpoint_status == "advanced":
            return "advance_checkpoint_journal"
        return "resume_checkpoint"

    if phase == "checkpoint_updated":
        if checkpoint_status != "advanced":
            raise ModuleRecoveryError("Checkpoint-päiväkirja on edellä moduulin varmennettua tilaa.")
        if publication_status != "merged" or public_feed_matches is not True:
            return "reconcile_completed_publication"
        return "verify_completed_run"

    return "inspect_external_state"
