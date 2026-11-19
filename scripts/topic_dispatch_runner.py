"""Eristetty handoff-runner: validoi yhden moduulin paketin ja palauttaa sen AI-rajapinnalle.

Tämä ohjelma toimii bubblewrap-sandboxissa eikä tee verkkohakuja, kirjoita
repositorioon tai lue muita moduuleja. Se palauttaa ainoastaan sille annetun
yhden moduulin syötepaketin sekä sen tarkistussumman.
"""
import hashlib
import json
import sys


def main():
    """Lue sandboxin syöte ja kirjoita rajattu handoff-tulos."""
    if len(sys.argv) != 3:
        raise SystemExit(2)
    input_path, output_path = sys.argv[1], sys.argv[2]
    with open(input_path, "r", encoding="utf-8") as stream:
        bundle = json.load(stream)

    required = {
        "bundle_schema_version", "module_id", "module_definition_version",
        "run", "module", "targets", "sources", "module_state",
    }
    if not isinstance(bundle, dict) or set(bundle) != required:
        raise SystemExit(3)
    module_id = bundle.get("module_id")
    module = bundle.get("module")
    run = bundle.get("run")
    if not isinstance(module_id, str) or not isinstance(module, dict) or module.get("module_id") != module_id:
        raise SystemExit(4)
    if module.get("module_type") != "topic":
        raise SystemExit(5)
    if not isinstance(run, dict) or not isinstance(run.get("run_id"), str):
        raise SystemExit(6)
    if not isinstance(bundle.get("targets"), list) or not isinstance(bundle.get("sources"), list):
        raise SystemExit(7)
    # Varmista, ettei bundle sisällä koordinaattorin globaalia tehtäväjonoa,
    # koko moduulirekisteriä tai erillisen näytösvahdin tietoja.
    serialized = json.dumps(bundle, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    forbidden = (
        "indian-film-screening-watch", "module_registry", "task_queue",
        "rotation", "other_modules",
    )
    if any(token in serialized for token in forbidden):
        raise SystemExit(8)
    digest = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
    result = {
        "dispatch_schema_version": 1,
        "status": "ready_for_external_research",
        "module_id": module_id,
        "run_id": run["run_id"],
        "input_sha256": digest,
        "input_bundle": bundle,
    }
    with open(output_path, "w", encoding="utf-8") as stream:
        json.dump(result, stream, ensure_ascii=False, separators=(",", ":"))


if __name__ == "__main__":
    main()
