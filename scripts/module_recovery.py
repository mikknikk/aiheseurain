"""Moduuliajon palautumisen päätöslogiikka ilman ulkoisia sivuvaikutuksia.

Funktio arvioi manifestin, RSS-PR:n, Pages-deploymentin, julkisen takaisinluvun
ja checkpointin yhteensopivuuden. Se ei käynnistä automaatioita eikä muuta
julkaisua, ajastuksia, käyttöoikeuksia tai moduulin tilaa.
"""
from __future__ import annotations

from typing import Any


class ModuleRecoveryError(ValueError):
    """Palautumisen lähtötiedot ovat virheelliset tai keskenään mahdottomat."""


PUBLICATION_STATES = {"not_started", "open", "closed_unmerged", "merged", "unknown"}
DEPLOYMENT_STATES = {"not_started", "in_progress", "success", "failure", "unknown"}
CHECKPOINT_STATES = {"not_advanced", "advanced", "unknown", "conflict"}
LEGACY_STATES = {"absent", "present", "unknown"}
MANIFEST_PHASES = {"prepared", "published", "artifacts_persisted", "checkpoint_updated"}


def recovery_action(
    manifest: dict[str, Any] | None,
    *,
    publication_status: str,
    deployment_status: str,
    public_feed_matches: bool | None,
    checkpoint_status: str,
    legacy_period_status: str,
    legacy_fallback_authorized: bool = False,
) -> str:
    """Palauta turvallinen seuraava toimi keskeytyneen topic-ajon perusteella.

    publication_status kuvaa RSS-PR:n tilaa; deployment_status kuvaa erikseen
    Pages-julkaisun tilaa. Näitä ei saa päätellä toisistaan.

    checkpoint_status:
    - not_advanced: nykyinen moduulitila vastaa manifestin lähtö-SHA:ta;
    - advanced: viimeisin onnistunut checkpoint on tämän run_id:n tulos;
    - conflict: tila on muuttunut jonkin muun ajon vuoksi;
    - unknown: tilaa ei voitu lukea luotettavasti.

    legacy_period_status kertoo, onko vanha raportointipolku jo julkaissut
    kyseisen moduulin seurantajakson. Vanhaan polkuun paluu vaatii varmennetun
    julkaisemattomuuden ja erillisen hyväksynnän. Funktio ei käynnistä polkuja.
    """
    if not isinstance(publication_status, str) or publication_status not in PUBLICATION_STATES:
        raise ModuleRecoveryError("Tuntematon RSS-julkaisun tila.")
    if not isinstance(deployment_status, str) or deployment_status not in DEPLOYMENT_STATES:
        raise ModuleRecoveryError("Tuntematon Pages-deploymentin tila.")
    if not isinstance(checkpoint_status, str) or checkpoint_status not in CHECKPOINT_STATES:
        raise ModuleRecoveryError("Tuntematon checkpointin tila.")
    if not isinstance(legacy_period_status, str) or legacy_period_status not in LEGACY_STATES:
        raise ModuleRecoveryError("Tuntematon vanhan raportointipolun julkaisutila.")
    if public_feed_matches is not None and type(public_feed_matches) is not bool:
        raise ModuleRecoveryError("Julkisen RSS-takaisinluvun tulos on virheellinen.")
    if not isinstance(legacy_fallback_authorized, bool):
        raise ModuleRecoveryError("Vanhaan raportointipolkuun paluun hyväksynnän pitää olla boolean.")

    if checkpoint_status == "conflict":
        return "manual_review"
    if legacy_period_status == "unknown":
        return "inspect_external_state"
    if publication_status == "unknown" or deployment_status == "unknown" or checkpoint_status == "unknown":
        return "inspect_external_state"

    if manifest is None:
        if checkpoint_status == "advanced":
            raise ModuleRecoveryError("Checkpoint on edennyt ilman julkaisumanifestia.")
        if checkpoint_status != "not_advanced" or publication_status != "not_started" or deployment_status != "not_started":
            return "inspect_external_state"
        if public_feed_matches is True:
            return "inspect_external_state"
        if legacy_period_status == "present":
            return "legacy_period_already_published"
        return "start_new_run"

    if not isinstance(manifest, dict):
        raise ModuleRecoveryError("Julkaisumanifestin pitää olla JSON-olio.")
    phase = manifest.get("phase")
    module_id, run_id = manifest.get("module_id"), manifest.get("run_id")
    if (not isinstance(phase, str) or phase not in MANIFEST_PHASES
            or not isinstance(module_id, str) or not module_id
            or not isinstance(run_id, str) or not run_id):
        raise ModuleRecoveryError("Julkaisumanifestin vaihe tai tunnisteet ovat virheellisiä.")

    # Jos vanha polku on jo julkaissut saman jakson, avointa tai yhdistettyä
    # moduulijulkaisua ei saa jatkaa automaattisesti.
    if legacy_period_status == "present":
        if publication_status not in {"not_started", "closed_unmerged"} or deployment_status != "not_started" or public_feed_matches is True:
            return "manual_review"
        return "legacy_period_already_published"

    if phase == "prepared":
        if checkpoint_status == "advanced":
            raise ModuleRecoveryError("Checkpoint on edennyt ennen julkaisumanifestin published-vaihetta.")
        if publication_status == "open":
            if deployment_status == "not_started" and public_feed_matches is False:
                return "wait_for_rss_pr"
            return "inspect_external_state"
        if publication_status == "merged":
            if deployment_status in {"not_started", "in_progress"}:
                return "wait_for_pages"
            if public_feed_matches is True:
                return "advance_publication_journal"
            return "retry_pages_publication" if deployment_status == "failure" else "reconcile_publication"
        if publication_status in {"not_started", "closed_unmerged"}:
            if deployment_status != "not_started" or public_feed_matches is not False:
                return "inspect_external_state"
            if legacy_fallback_authorized:
                return "return_to_legacy_path"
            return "legacy_fallback_requires_approval"

    if phase == "published":
        if checkpoint_status == "advanced":
            raise ModuleRecoveryError("Checkpoint on edennyt ennen artefaktien päiväkirjamerkintää.")
        if publication_status != "merged":
            return "inspect_external_state"
        if deployment_status in {"not_started", "in_progress"}:
            return "wait_for_pages"
        if public_feed_matches is True:
            return "resume_artifact_persistence"
        return "retry_pages_publication" if deployment_status == "failure" else "reconcile_publication"

    if phase == "artifacts_persisted":
        if publication_status != "merged":
            return "inspect_external_state"
        if deployment_status in {"not_started", "in_progress"}:
            return "wait_for_pages"
        if public_feed_matches is not True:
            return "retry_pages_publication" if deployment_status == "failure" else "reconcile_publication"
        if checkpoint_status == "advanced":
            return "advance_checkpoint_journal"
        return "resume_checkpoint"

    if phase == "checkpoint_updated":
        if checkpoint_status != "advanced":
            raise ModuleRecoveryError("Checkpoint-päiväkirja on edellä moduulin varmennettua tilaa.")
        if publication_status != "merged" or deployment_status != "success" or public_feed_matches is not True:
            return "reconcile_completed_publication"
        return "verify_completed_run"

    return "inspect_external_state"
