"""Valitse yksi uutisaihe ja luovuta vain sen syöte eristetylle runnerille.

Koordinaattori lukee teknisen vuorotilan, jonon ja aihe–moduuli-kytkennän.
Se muodostaa yhdelle moduulille rajatun syötepaketin ja käynnistää sen
bubblewrap-sandboxissa. Se ei tee verkkohakuja, julkaise RSS:ää eikä päivitä
checkpointteja. Tuloksena syntyy rajattu handoff-paketti erilliselle AI-
tutkimusajolle. Näytösvahti suljetaan pois tehtäväkierrosta.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any, Callable, Mapping
from zoneinfo import ZoneInfo

import jsonschema

from scripts.isolated_module_runner import IsolatedRunnerError, run_isolated_module
from scripts.module_input_bundle import build_module_input_bundle, bundle_to_json
from scripts.module_registry import load_registry

ROOT = Path(__file__).resolve().parents[1]
TIMEZONE = "Europe/Helsinki"


class TopicCoordinatorError(RuntimeError):
    """Tehtävävalinnan tai moduulikohtaisen käynnistyksen virhe."""


@dataclass(frozen=True)
class TopicSelection:
    """Yhden vuorossa olevan uutisaiheen tekniset tunnisteet."""

    task_id: str
    task_name: str
    feed_path: str
    module_id: str
    source_registry_task_id: str
    module_status: str
    module_definition_version: str


@dataclass(frozen=True)
class TopicDispatch:
    """Yhden aiheen eristetyn käynnistyksen tulos."""

    request: dict[str, Any]
    selection: TopicSelection
    runner_result: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        """Palauta koneellisesti siirrettävä yhden aiheen handoff."""
        return {
            "dispatch_schema_version": 1,
            "status": "ready_for_external_research",
            "request": self.request,
            "selection": asdict(self.selection),
            "runner_result": self.runner_result,
        }


def _read_json(path: Path) -> dict[str, Any]:
    """Lue JSON-olio ja muunna tiedostovirheet ymmärrettäväksi keskeytykseksi."""
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise TopicCoordinatorError(f"JSON-tiedostoa ei voi lukea: {path.relative_to(ROOT) if path.is_relative_to(ROOT) else path.name}") from exc
    if not isinstance(value, dict):
        raise TopicCoordinatorError(f"JSON-tiedoston ylimmän tason pitää olla olio: {path.name}")
    return value


def _aware_datetime(value: str, field: str) -> datetime:
    """Hyväksy vain ISO 8601 -aikaleima, jossa on aikavyöhyke."""
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, TypeError, ValueError) as exc:
        raise TopicCoordinatorError(f"{field} ei ole kelvollinen ISO 8601 -aikaleima.") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise TopicCoordinatorError(f"{field} tarvitsee aikavyöhykkeen.")
    return parsed


def _queue_order(queue_text: str) -> list[str]:
    """Poimi jonodokumentista vain syötepolut, älä aihekohtaisia ohjeita."""
    try:
        section = queue_text.split("## Kiinteä kiertojärjestys", 1)[1]
        section = section.split("## Seuraava tehtävä", 1)[0]
    except IndexError as exc:
        raise TopicCoordinatorError("Tehtäväjonon kiertojärjestyksen otsikko puuttuu.") from exc
    feeds = re.findall(r"^\s*\d+\.\s+.*?—\s+`?(feeds/[^\s`]+)`?\s*$", section, re.MULTILINE)
    if len(feeds) != 9 or len(feeds) != len(set(feeds)):
        raise TopicCoordinatorError("Tehtäväjonossa pitää olla täsmälleen yhdeksän yksilöllistä uutissyötettä.")
    return feeds


def _validate_task_map(task_map: dict[str, Any], schema_path: Path) -> dict[str, dict[str, str]]:
    """Validoi eksplisiittisen kiinnityksen kiertotehtävien ja moduulien välillä."""
    schema = _read_json(schema_path)
    jsonschema.Draft202012Validator.check_schema(schema)
    errors = sorted(
        jsonschema.Draft202012Validator(schema).iter_errors(task_map),
        key=lambda error: list(error.path),
    )
    if errors:
        raise TopicCoordinatorError(f"Aihe–moduulikartan skeemavirhe: {errors[0].message}")
    mapping = {entry["task_id"]: entry for entry in task_map["tasks"]}
    if len(mapping) != len(task_map["tasks"]) or len(mapping) != 9:
        raise TopicCoordinatorError("Aihe–moduulikartassa pitää olla yhdeksän yksilöllistä kiertotehtävää.")
    module_ids = [entry["module_id"] for entry in task_map["tasks"]]
    if len(module_ids) != len(set(module_ids)):
        raise TopicCoordinatorError("Sama moduuli on liitetty useaan kiertotehtävään.")
    if any(entry["module_type"] != "topic" for entry in task_map["tasks"]):
        raise TopicCoordinatorError("Kiertokartassa saa olla vain topic-tyyppisiä moduuleja.")
    if any(entry["module_id"] == "indian-film-screening-watch" for entry in task_map["tasks"]):
        raise TopicCoordinatorError("Erillistä näytösvahtia ei saa liittää uutiskiertoon.")
    return mapping


def validate_topic_rotation_configuration(root: Path = ROOT) -> TopicSelection:
    """Tarkista jonon, koneellisen tilan, kartan ja moduulirekisterin yhteensopivuus."""
    root = Path(root).resolve()
    state = _read_json(root / "data/seurantatila.json")
    rotation = state.get("rotation")
    if not isinstance(rotation, dict) or not isinstance(rotation.get("tasks"), dict):
        raise TopicCoordinatorError("Seurantatilan rotation.tasks-rakenne puuttuu.")
    task_id = rotation.get("next_task")
    task_state = rotation["tasks"].get(task_id)
    if not isinstance(task_id, str) or not isinstance(task_state, dict):
        raise TopicCoordinatorError("Seuraavaa tehtävää ei löydy koneellisesta seurantatilasta.")
    task_name = task_state.get("name")
    feed_path = task_state.get("feed")
    if not isinstance(task_name, str) or not isinstance(feed_path, str):
        raise TopicCoordinatorError("Seuraavan tehtävän nimi tai RSS-polku puuttuu.")

    queue_text = (root / "docs/tehtavajono.md").read_text(encoding="utf-8")
    queue_feeds = _queue_order(queue_text)
    state_feeds = [item.get("feed") for item in rotation["tasks"].values() if isinstance(item, dict)]
    if queue_feeds != state_feeds:
        raise TopicCoordinatorError("Dokumentoitu kiertojärjestys ja koneellisen seurantatilan järjestys eroavat.")
    if feed_path not in queue_feeds:
        raise TopicCoordinatorError("Seurantatilan seuraava tehtävä ei vastaa dokumentoitua kiertojonoa.")
    try:
        next_section = queue_text.split("## Seuraava tehtävä", 1)[1].split("## Kiertoperiaate", 1)[0]
    except IndexError as exc:
        raise TopicCoordinatorError("Tehtäväjonon seuraavan vuoron otsikko puuttuu.") from exc
    next_match = re.search(r"\*\*Vuorossa seuraavaksi:\s*(.+?)\*\*", next_section)
    if not next_match or next_match.group(1).strip().rstrip(".") != task_name:
        raise TopicCoordinatorError("Tehtäväjonon näkyvä seuraava vuoro ja JSON-seurantatila eroavat.")

    task_map = _read_json(root / "data/topic-task-map.json")
    mapping = _validate_task_map(task_map, root / "schemas/topic-task-map.schema.json")
    if set(mapping) != set(rotation["tasks"]):
        raise TopicCoordinatorError("Aihe–moduulikartan tehtävät eivät vastaa seurantatilan yhdeksää kiertotehtävää.")

    registry_result = load_registry(
        registry_path=root / "data/module-registry.json",
        root=root,
        include_inactive=True,
    )
    if registry_result.invalid_modules:
        raise TopicCoordinatorError("Moduulirekisterissä on virheellisiä määrityksiä.")
    entry = mapping[task_id]
    module_result = next(
        (item for item in registry_result.modules if item.module_id == entry["module_id"]),
        None,
    )
    if module_result is None or module_result.definition is None:
        raise TopicCoordinatorError("Vuorossa olevan aiheen moduulimäärittelyä ei voi ladata.")
    if module_result.status not in {"active", "inactive"}:
        raise TopicCoordinatorError("Vuorossa olevan moduulin tila ei ole suoritettavissa.")
    if module_result.definition.get("module_type") != "topic":
        raise TopicCoordinatorError("Uutiskierto saa käynnistää vain topic-tyyppisen moduulin.")
    return TopicSelection(
        task_id=task_id,
        task_name=task_name,
        feed_path=feed_path,
        module_id=entry["module_id"],
        source_registry_task_id=entry["source_registry_task_id"],
        module_status=module_result.status,
        module_definition_version=module_result.definition["definition_version"],
    )


def dispatch_next_topic(
    *,
    run_id: str,
    period_start: str,
    period_end: str,
    root: Path = ROOT,
    runner: Callable[..., dict[str, Any]] = run_isolated_module,
    timeout_seconds: int = 300,
) -> TopicDispatch:
    """Valmistele ja käynnistä täsmälleen yksi seuraava topic-moduuli varjotilassa.

    Tämä vaihe luovuttaa yhden aiheen tietopaketin erilliselle tutkimuspalvelulle.
    Se ei itse tee uutishakua eikä väitä tutkimusta tai julkaisua suoritetuksi.
    """
    if not isinstance(run_id, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]{2,127}", run_id):
        raise TopicCoordinatorError("run_id ei vastaa suorituspyynnön tunnistevaatimusta.")
    start = _aware_datetime(period_start, "period_start")
    end = _aware_datetime(period_end, "period_end")
    if end < start:
        raise TopicCoordinatorError("Seurantajakson loppu on ennen alkua.")

    root = Path(root).resolve()
    selection = validate_topic_rotation_configuration(root)
    requested_at = datetime.now(ZoneInfo(TIMEZONE)).isoformat()
    request = {
        "schema_version": 1,
        "module_id": selection.module_id,
        "module_definition_version": selection.module_definition_version,
        "contract_version": "1.0.0",
        "run_id": run_id,
        "period": {"start": period_start, "end": period_end},
        "mode": "shadow",
        "requested_at": requested_at,
    }
    request_schema = _read_json(root / "schemas/module-run-request.schema.json")
    jsonschema.Draft202012Validator.check_schema(request_schema)
    try:
        jsonschema.Draft202012Validator(
            request_schema, format_checker=jsonschema.FormatChecker()
        ).validate(request)
    except jsonschema.ValidationError as exc:
        raise TopicCoordinatorError(f"Suorituspyyntö ei täytä skeemaa: {exc.message}") from exc

    bundle = build_module_input_bundle(
        selection.module_id,
        task_id=selection.source_registry_task_id,
        source_registry_path=f"data/sources/{selection.source_registry_task_id}.json",
        run_id=run_id,
        period_start=period_start,
        period_end=period_end,
        root=root,
    )
    runner_source = (root / "scripts/topic_dispatch_runner.py").read_text(encoding="utf-8")
    result = runner(
        bundle,
        runner_source,
        timeout_seconds=timeout_seconds,
    )
    if not isinstance(result, dict):
        raise TopicCoordinatorError("Eristetty runner ei palauttanut JSON-oliota.")
    expected_bundle = json.loads(bundle_to_json(bundle))
    if result.get("dispatch_schema_version") != 1 or result.get("status") != "ready_for_external_research":
        raise TopicCoordinatorError("Eristetyn runnerin tulos ei ole hyväksytty dispatch-handoff.")
    if result.get("module_id") != selection.module_id or result.get("run_id") != run_id:
        raise TopicCoordinatorError("Eristetyn runnerin moduuli- tai ajotunniste ei vastaa pyyntöä.")
    if result.get("input_bundle") != expected_bundle:
        raise TopicCoordinatorError("Runnerin palauttama syötepaketti poikkeaa sille annetusta paketista.")
    expected_digest = hashlib.sha256(
        json.dumps(expected_bundle, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    if result.get("input_sha256") != expected_digest:
        raise TopicCoordinatorError("Runnerin syötepaketin SHA-256-tiiviste ei täsmää.")
    return TopicDispatch(request=request, selection=selection, runner_result=result)


def main(argv: list[str] | None = None) -> int:
    """Käsittele komentorivipyyntö ja tulosta vain valitun aiheen handoff."""
    parser = argparse.ArgumentParser(
        description="Valitse Aiheseuraimen seuraava uutisaihe ja käynnistä sen eristetty runner."
    )
    parser.add_argument("--run-id", required=True, help="Ajon yksilöllinen tunniste.")
    parser.add_argument("--period-start", required=True, help="Seurantajakson alku ISO 8601 -aikaleimana aikavyöhykkeineen.")
    parser.add_argument("--period-end", required=True, help="Seurantajakson loppu ISO 8601 -aikaleimana aikavyöhykkeineen.")
    parser.add_argument("--timeout-seconds", type=int, default=300, help="Sandboxin aikaraja (1–3600 sekuntia).")
    parser.add_argument("--root", type=Path, default=ROOT, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    try:
        dispatch = dispatch_next_topic(
            run_id=args.run_id,
            period_start=args.period_start,
            period_end=args.period_end,
            root=args.root,
            timeout_seconds=args.timeout_seconds,
        )
    except (TopicCoordinatorError, IsolatedRunnerError, OSError, ValueError) as exc:
        print(json.dumps({"status": "failed", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2
    print(json.dumps(dispatch.to_dict(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
