"""Aihekohtaisen varjosiirtymäharjoituksen orkestrointi.

Harjoitus yhdistää jo olemassa olevat read-only-todistekerääjät,
palautumispäätöksen ja auditointivaraston. Se ei julkaise, aktivoi eikä
muuta moduulitilaa tai automaatioiden asetuksia.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable

from scripts.module_transition_evidence import (
    GitHubTransitionEvidenceCollector,
    GitHubTransitionEvidenceStore,
    TransitionEvidenceError,
    _feed_url,
)
from scripts.github_module_adapters import _module, _run, _time


class ShadowTransitionError(ValueError):
    """Varjosiirtymän syöte tai kerätty näyttö on puutteellinen."""


@dataclass(frozen=True)
class ShadowTransitionRequest:
    """Yhden topic-moduulin varjoharjoituksen muuttumaton syötesopimus."""

    module_id: str
    run_id: str
    module_version: str
    period_start: str
    period_end: str
    mode: str = "shadow"

    def validate(self, repository_root) -> None:
        module_id = _module(self.module_id)
        _run(self.run_id)
        if module_id != self.module_id:
            raise ShadowTransitionError("Moduulitunniste ei ole kanoninen.")
        if self.mode != "shadow":
            raise ShadowTransitionError("Tämä rajapinta sallii vain mode=shadow.")
        if not isinstance(self.module_version, str) or not self.module_version.strip():
            raise ShadowTransitionError("Moduuliversio puuttuu.")
        _time(self.period_start)
        _time(self.period_end)
        start = datetime.fromisoformat(self.period_start.replace("Z", "+00:00"))
        end = datetime.fromisoformat(self.period_end.replace("Z", "+00:00"))
        if start > end:
            raise ShadowTransitionError("Seurantajakson alku on loppua myöhempi.")
        # Ratkaisu hyväksyy vain feed-catalogin topic-syötteet. Näytösvahti
        # on process-tyyppinen eikä voi kulkea tätä käyttöönoton polkua.
        try:
            _feed_url(module_id, repository_root=repository_root,
                      pages_base_url="https://example.invalid")
        except (TransitionEvidenceError, OSError, ValueError) as exc:
            raise ShadowTransitionError("Varjosiirtymä sallitaan vain rekisteröidylle topic-moduulille.") from exc


class ShadowTransitionOrchestrator:
    """Kerää yhden ajon todisteet, laskee päätöksen ja tallentaa tapahtumat."""

    def __init__(self, collector: GitHubTransitionEvidenceCollector,
                 store: GitHubTransitionEvidenceStore):
        self.collector = collector
        self.store = store

    @staticmethod
    def _required_record(records: list[dict[str, Any]], event_type: str) -> dict[str, Any]:
        matches = [record for record in records if record.get("event_type") == event_type]
        if len(matches) != 1:
            raise ShadowTransitionError(
                f"Ajossa pitää olla täsmälleen yksi {event_type}-todiste."
            )
        return matches[0]

    def run(
        self,
        request: ShadowTransitionRequest,
        *,
        collect: dict[str, Callable[[], dict[str, Any]]],
        observed_at: str,
        expected_guids: list[str] | None = None,
    ) -> dict[str, Any]:
        """Suorita varjoharjoitus annetuilla read-only-kerääjäkutsuilla.

        collect sisältää tapahtumatyypin ja vastaavan collector-metodin
        kutsun. Kutsut eivät saa tehdä muuta kuin lukea todisteita. Tallennus
        tapahtuu vasta, kun koko näyttö on kerätty ja omistajuus tarkistettu.
        """
        request.validate(self.collector.root)
        _time(observed_at)
        if not isinstance(collect, dict) or "pull_request" not in collect or "legacy_period" not in collect:
            raise ShadowTransitionError("PR- ja vanhan polun havainto ovat pakollisia.")
        allowed = {
            "pull_request", "pages_deployment", "public_feed",
            "publication_manifest", "checkpoint", "legacy_period",
        }
        if set(collect) - allowed or any(not callable(fn) for fn in collect.values()):
            raise ShadowTransitionError("Keräyssuunnitelmassa on tuntematon tapahtuma tai ei-kutsuttava arvo.")

        # Kerää kaikki havainnot ensin. Jos yksikin lukeminen epäonnistuu,
        # auditointiin ei synny harhaanjohtavaa osittaista siirtymäpäätöstä.
        records = [collect[event_type]() for event_type in sorted(collect)]
        for record in records:
            if (not isinstance(record, dict)
                    or record.get("module_id") != request.module_id
                    or record.get("run_id") != request.run_id
                    or record.get("event_type") not in allowed):
                raise ShadowTransitionError("Todiste kuuluu väärälle moduulille/ajolle tai tapahtumatyyppi ei kelpaa.")
        if len({record["event_type"] for record in records}) != len(records):
            raise ShadowTransitionError("Sama todistetyyppi kerättiin useammin kuin kerran.")

        pr = self._required_record(records, "pull_request")["evidence"]
        legacy = self._required_record(records, "legacy_period")["evidence"]
        if pr["merged"]:
            for kind in ("pages_deployment", "public_feed", "publication_manifest"):
                self._required_record(records, kind)
        pages = next((r["evidence"] for r in records if r["event_type"] == "pages_deployment"), None)
        feed = next((r["evidence"] for r in records if r["event_type"] == "public_feed"), None)
        manifest_evidence = next((r["evidence"] for r in records if r["event_type"] == "publication_manifest"), None)
        checkpoint = next((r["evidence"] for r in records if r["event_type"] == "checkpoint"), None)

        publication_status = "merged" if pr["merged"] else ("open" if pr["state"] == "open" else "closed_unmerged")
        deployment_map = {
            "not_found": "not_started", "pending": "in_progress",
            "in_progress": "in_progress", "success": "success",
            "failure": "failure", "error": "failure", "inactive": "unknown",
        }
        deployment_status = deployment_map.get(pages["state"], "not_started") if pages else "not_started"
        public_feed_matches = None
        if feed is not None and expected_guids is not None:
            if (not isinstance(expected_guids, list)
                    or any(not isinstance(guid, str) or not guid for guid in expected_guids)
                    or len(expected_guids) != len(set(expected_guids))):
                raise ShadowTransitionError("Odotettu GUID-luettelo on virheellinen.")
            public_feed_matches = set(feed["guids"]) == set(expected_guids)
        checkpoint_status = "unknown"
        if checkpoint is not None:
            checkpoint_status = "advanced" if checkpoint["after_run_id"] == request.run_id else "not_advanced"
        manifest = None
        if manifest_evidence is not None:
            manifest = {
                "module_id": request.module_id,
                "run_id": request.run_id,
                "phase": manifest_evidence["phase"],
            }
        approval = any(r["event_type"] == "legacy_approval" for r in records)
        decision = self.collector.recovery_decision(
            request.module_id, request.run_id, manifest=manifest,
            publication_status=publication_status,
            deployment_status=deployment_status,
            public_feed_matches=public_feed_matches,
            checkpoint_status=checkpoint_status,
            legacy_period_status=legacy["status"],
            legacy_fallback_authorized=approval,
            observed_at=observed_at,
        )
        # Vasta täydellisen keruun ja päätöksen jälkeen tallennetaan tapahtumat.
        for record in records:
            self.store.record(record)
        self.store.record(decision)
        reconstructed = self.store.load_run(request.module_id, request.run_id)
        expected_ids = {record["event_id"] for record in records + [decision]}
        if not expected_ids.issubset({record["event_id"] for record in reconstructed}):
            raise ShadowTransitionError("Auditointitapahtumien takaisinluku ei vastaa tallennusta.")
        return {
            "mode": request.mode,
            "module_id": request.module_id,
            "run_id": request.run_id,
            "module_version": request.module_version,
            "period_start": request.period_start,
            "period_end": request.period_end,
            "recovery_action": decision["evidence"]["action"],
            "event_count": len(reconstructed),
            "event_ids": sorted(expected_ids),
        }
