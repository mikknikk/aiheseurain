"""Kytke yksi vastaanotettu ChatGPT-tulos moduuliorkestrointiin.

Tämä komentorivityökalu käsittelee vain main-haaraan hyväksytyn yhden tulostiedoston.
Oletustila on kirjoitukseton shadow; tuotantotila vaatii erillisen kutsulipun ja aktiivisen moduulin.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Callable

from scripts.chatgpt_module_result import ChatGPTResultExecutor
from scripts.chatgpt_result_quality import ChatGPTResultQualityGate
from scripts.chatgpt_rss_candidate import ChatGPTRssCandidateBuilder
from scripts.github_module_adapters import (
    GitHubApiClient, GitHubArtifactStore, GitHubHandoffStore,
    GitHubModuleStateStore, GitHubPagesRssPublisher,
    GitHubPublicationJournal, GitHubRotationStateStore, GitHubRunRecorder,
)
from scripts.module_input_bundle import build_module_input_bundle, bundle_to_json
from scripts.module_orchestrator import (
    ModuleOrchestrator, ModuleRunRequest, ModuleRunResult, load_registry,
)
from scripts.topic_rotation_coordinator import (
    TopicCoordinatorError, validate_topic_rotation_configuration,
)
from scripts.validate_chatgpt_inbox import validate_inbox_result

ROOT = Path(__file__).resolve().parents[1]


class ChatGPTProcessingError(RuntimeError):
    """Yhden ChatGPT-tuloksen käsittelyn turvallinen virhe."""


def _canonical_digest(value: dict[str, Any]) -> str:
    """Laske sama vakaa SHA-256 kuin moduulihandoffin runner."""
    canonical = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _compare_handoff(payload: dict[str, Any], record: dict[str, Any]) -> None:
    """Varmista, että ChatGPT palautti täsmälleen aiemmin hyväksytyn handoffin tunnisteet."""
    handoff = payload["handoff"]
    fields = (
        "module_id", "module_definition_version", "contract_version",
        "run_id", "period", "requested_at", "input_sha256",
    )
    for field in fields:
        if handoff.get(field) != record.get(field):
            raise ChatGPTProcessingError(f"ChatGPT-tuloksen handoff-kenttä {field} ei vastaa tallennettua alkuperää.")


def _validated_request_context(
    payload: dict[str, Any], *, root: Path, rotation_store: GitHubRotationStateStore,
    module_state_store: GitHubModuleStateStore, handoff_store: GitHubHandoffStore,
) -> tuple[ModuleRunRequest, dict[str, Any], dict[str, Any], str]:
    """Vahvista handoff nykyiseen kiertoon ja moduulipakettiin tai aiempaan hyväksyttyyn tiivisteeseen."""
    module_id, run_id = payload["module_id"], payload["run_id"]
    handoff = payload["handoff"]
    rotation_state, _rotation_sha = rotation_store.load()
    accepted = handoff_store.load(module_id, run_id)
    expected_task_id = accepted["task_id"] if accepted else None
    try:
        selection = validate_topic_rotation_configuration(
            root, state_override=rotation_state, expected_task_id=expected_task_id
        )
    except TopicCoordinatorError as exc:
        raise ChatGPTProcessingError("Handoff ei vastaa Aiheseuraimen nykyistä tehtäväkiertoa.") from exc

    registry = load_registry(root=root, include_inactive=True)
    module_result = next((item for item in registry.modules if item.module_id == module_id), None)
    if module_result is None:
        raise ChatGPTProcessingError("Handoffin moduulia ei löydy rekisteristä.")
    definition = module_result.definition
    if definition.get("module_type") != "topic":
        raise ChatGPTProcessingError("Tämä käsittelypolku hyväksyy vain topic-moduuleja.")
    if selection.module_id != module_id:
        raise ChatGPTProcessingError("Handoffin moduuli ei vastaa valittua kiertotehtävää.")
    if selection.module_definition_version != handoff["module_definition_version"]:
        raise ChatGPTProcessingError("Handoffin moduuliversio ei vastaa nykyistä rekisteriä.")
    if registry.contract_version != handoff["contract_version"]:
        raise ChatGPTProcessingError("Handoffin sopimusversio ei vastaa nykyistä rekisteriä.")
    if handoff["run_id"] != run_id:
        raise ChatGPTProcessingError("Handoffin run_id ei vastaa tulostiedostoa.")
    if handoff["period"] != payload["period"]:
        raise ChatGPTProcessingError("Handoffin seurantajakso ei vastaa tulosraporttia.")

    module_state, _state_sha = module_state_store.load(module_id)
    if accepted is None:
        # Ensimmäisellä vastaanotolla rakennetaan sama yhden moduulin syötepaketti
        # nykyisistä rekistereistä ja runtime-checkpointista. Myöhemmät uusinnat
        # sidotaan tämän jälkeen tallennettuun, muuttumattomaan tiivisteeseen.
        bundle = build_module_input_bundle(
            module_id,
            task_id=selection.source_registry_task_id,
            run_id=run_id,
            period_start=payload["period"]["start"],
            period_end=payload["period"]["end"],
            module_state_override=module_state,
            root=root,
        )
        expected_bundle = json.loads(bundle_to_json(bundle))
        expected_digest = _canonical_digest(expected_bundle)
        if handoff["input_sha256"] != expected_digest:
            raise ChatGPTProcessingError("Handoffin syötepaketin SHA-256 ei vastaa Aiheseuraimen nykyistä moduulipakettia.")
        validated_at = datetime.now(timezone.utc).isoformat()
        accepted = handoff_store.store_or_verify({
            "schema_version": 1,
            "module_id": module_id,
            "module_definition_version": selection.module_definition_version,
            "contract_version": registry.contract_version,
            "run_id": run_id,
            "task_id": selection.task_id,
            "feed_path": selection.feed_path,
            "period": payload["period"],
            "requested_at": handoff["requested_at"],
            "input_sha256": expected_digest,
            "validated_at": validated_at,
        })
    else:
        _compare_handoff(payload, accepted)
        if accepted["task_id"] != selection.task_id or accepted["feed_path"] != selection.feed_path:
            raise ChatGPTProcessingError("Tallennettu handoff ei vastaa tehtävän nykyisiä reitti- ja omistajuustietoja.")
    _compare_handoff(payload, accepted)

    request = ModuleRunRequest(
        module_id=module_id,
        module_definition_version=selection.module_definition_version,
        contract_version=registry.contract_version,
        run_id=run_id,
        period_start=payload["period"]["start"],
        period_end=payload["period"]["end"],
        mode="shadow",
        requested_at=handoff["requested_at"],
    )
    return request, definition, accepted, selection.task_id


def process_inbox_result(
    file_path: Path, *, relative_path: str, mode: str = "shadow",
    root: Path = ROOT, client: Any | None = None,
    candidate_builder: Callable[..., Any] | None = None,
    allow_production: bool = False,
) -> ModuleRunResult:
    """Validoi, sido alkuperään ja suorita yksi ChatGPT-tulos turvallisesti."""
    if mode not in {"shadow", "production"}:
        raise ChatGPTProcessingError("Ajon tila on virheellinen.")
    if mode == "production" and not allow_production:
        raise ChatGPTProcessingError("Tuotantotila edellyttää erillistä hyväksyntälippua.")
    root = Path(root).resolve()
    payload = validate_inbox_result(
        Path(file_path), relative_path=relative_path, root=root
    )
    runtime_client = client or GitHubApiClient()
    rotation_store = GitHubRotationStateStore(runtime_client, repository_root=root)
    state_store = GitHubModuleStateStore(runtime_client)
    handoff_store = GitHubHandoffStore(runtime_client)
    request, definition, accepted, task_id = _validated_request_context(
        payload, root=root, rotation_store=rotation_store,
        module_state_store=state_store, handoff_store=handoff_store,
    )
    request = ModuleRunRequest(
        module_id=request.module_id,
        module_definition_version=request.module_definition_version,
        contract_version=request.contract_version,
        run_id=request.run_id,
        period_start=request.period_start,
        period_end=request.period_end,
        mode=mode,
        requested_at=request.requested_at,
    )
    executor = ChatGPTResultExecutor(payload)
    quality_gate = ChatGPTResultQualityGate(root=root)
    recorder = GitHubRunRecorder(runtime_client)

    if mode == "shadow":
        orchestrator = ModuleOrchestrator(
            registry_loader=lambda include_inactive=False: load_registry(
                root=root, include_inactive=include_inactive
            ),
            executor=executor,
            quality_gate=quality_gate,
            recorder=recorder,
        )
        return orchestrator.run(request)

    publisher_token = __import__("os").getenv("AIHESEURAIN_GITHUB_TOKEN")
    if not publisher_token:
        raise ChatGPTProcessingError("Tuotantojulkaisu edellyttää AIHESEURAIN_GITHUB_TOKEN-tunnusta.")
    if candidate_builder is None:
        candidate_builder = ChatGPTRssCandidateBuilder(root=root)
    publisher_client = GitHubApiClient(token=publisher_token)
    publisher = GitHubPagesRssPublisher(
        publisher_client, candidate_builder, repository_root=root
    )
    orchestrator = ModuleOrchestrator(
        registry_loader=lambda include_inactive=False: load_registry(
            root=root, include_inactive=include_inactive
        ),
        executor=executor,
        quality_gate=quality_gate,
        state_store=state_store,
        artifact_store=GitHubArtifactStore(runtime_client),
        publication_journal=GitHubPublicationJournal(runtime_client),
        publisher=publisher,
        recorder=recorder,
        production_authorized=True,
    )
    result = orchestrator.run(request)
    if result.status == "succeeded" and result.published and result.checkpoint_updated:
        rotation_store.advance(result, task_id=task_id, feed_path=accepted["feed_path"])
    return result


def changed_inbox_file(before: str, after: str, *, root: Path = ROOT) -> str:
    """Vaadi pushissa täsmälleen yksi uusi inbox-JSON eikä hyväksy muokkauksia."""
    zero = "0" * 40
    if before != zero:
        command = ["git", "diff", "--name-status", before, after]
    else:
        # Ensimmäinen commit vaatii diff-tree --root -muodon; git diff --root ei
        # listaa tavallisen commitin lisättyjä tiedostoja tällä syntaksilla.
        command = ["git", "diff-tree", "--root", "--no-commit-id", "--name-status", "-r", after]
    command.extend(["--", "data/chatgpt-inbox/"])
    completed = subprocess.run(
        command, cwd=root, check=True, capture_output=True, text=True
    )
    entries = [line.split("\t", 1) for line in completed.stdout.splitlines() if line]
    if len(entries) != 1 or entries[0][0] != "A" or len(entries[0]) != 2:
        raise ChatGPTProcessingError("Yhden push-tapahtuman pitää lisätä täsmälleen yksi uusi ChatGPT-tulostiedosto.")
    return entries[0][1]


def main(argv: list[str] | None = None) -> int:
    """Käsittele GitHub push -tapahtuman yksi hyväksytty inbox-tiedosto."""
    parser = argparse.ArgumentParser(description="Käsittele yksi Aiheseuraimen ChatGPT-tulos.")
    parser.add_argument("--file", type=Path, help="Validoitava tiedosto (testi-/manuaalikäyttö).")
    parser.add_argument("--relative-path", help="Tiedoston repositoriopolku.")
    parser.add_argument("--before", help="GitHub push -tapahtuman before-SHA.")
    parser.add_argument("--after", help="GitHub push -tapahtuman after-SHA.")
    parser.add_argument("--mode", choices=["shadow", "production"], default="shadow")
    parser.add_argument("--allow-production", action="store_true")
    parser.add_argument("--root", type=Path, default=ROOT, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    try:
        if args.file is not None:
            if not args.relative_path or args.before or args.after:
                raise ChatGPTProcessingError("--file vaatii --relative-path eikä sitä voi yhdistää push-SHA-arvoihin.")
            file_path, relative_path = args.file, args.relative_path
        else:
            if not args.before or not args.after or args.relative_path:
                raise ChatGPTProcessingError("Anna joko --file ja --relative-path tai --before ja --after.")
            relative_path = changed_inbox_file(args.before, args.after, root=args.root)
            file_path = args.root / relative_path
        result = process_inbox_result(
            file_path, relative_path=relative_path, mode=args.mode,
            root=args.root, allow_production=args.allow_production,
        )
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        return 0
    except (ChatGPTProcessingError, OSError, ValueError, RuntimeError) as exc:
        print(f"ChatGPT-tuloksen käsittely epäonnistui: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
