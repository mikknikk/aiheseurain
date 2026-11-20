"""Lue moduulin checkpointin lähtötila ennen siirtymäharjoitusta.

Tämä moduuli tekee vain yhden GitHub Contents API -lukupyynnön. Se ei luo
runtime-haaraa, kirjoita checkpointia eikä muuta moduulin muuta tilaa.
Palautettua SHA:ta ja checkpointin tunnisteita voi käyttää myöhemmän
checkpoint-todisteen before_* -kenttinä.
"""
from __future__ import annotations

import json
import re
from typing import Any

from scripts.github_module_adapters import RUNTIME_BRANCH, _module, _run, _time


class CheckpointBaselineError(ValueError):
    """Checkpointin lähtötilaa ei voitu lukea tai validoida luotettavasti."""


def read_checkpoint_baseline(
    client: Any,
    module_id: str,
    *,
    observed_at: str,
    branch: str = RUNTIME_BRANCH,
) -> dict[str, Any]:
    """Palauta nykyisen moduulitilan muuttumaton lähtöhavainto.

    ``blob_sha`` sitoo havainnon täsmälleen luettuun Git-blobiin. Jos
    checkpointia ei ole vielä koskaan kirjattu, run_id ja checked_at ovat
    None; tätä ei tulkita onnistuneeksi tai epäonnistuneeksi ajoksi.
    """
    module_id = _module(module_id)
    _time(observed_at)
    if not isinstance(branch, str) or not branch.strip():
        raise CheckpointBaselineError("Runtime-haaran nimi puuttuu.")

    path = f"data/module-state/{module_id}.json"
    current = client.get_file(path, branch)
    if current is None:
        raise CheckpointBaselineError("Checkpoint-tiedostoa ei löydy runtime-haarasta.")
    if not isinstance(current.sha, str) or not re.fullmatch(r"[a-f0-9]{40}", current.sha):
        raise CheckpointBaselineError("Checkpoint-tiedoston Git-blob-SHA on virheellinen.")

    try:
        state = json.loads(current.content.decode("utf-8"))
        if not isinstance(state, dict) or state.get("module_id") != module_id:
            raise CheckpointBaselineError("Checkpoint-tiedoston moduuliomistajuus ei täsmää.")
        checkpoint_root = state.get("checkpoint")
        if not isinstance(checkpoint_root, dict):
            raise CheckpointBaselineError("Checkpoint-osa puuttuu tai ei ole JSON-olio.")
        last = checkpoint_root.get("last_successful_run")
        if not isinstance(last, dict):
            raise CheckpointBaselineError("Viimeisimmän onnistuneen ajon checkpoint puuttuu.")
        run_id = last.get("run_id")
        checked_at = last.get("checked_at")
        if run_id is not None:
            _run(run_id)
        if checked_at is not None:
            _time(checked_at)
    except (UnicodeDecodeError, json.JSONDecodeError, TypeError, KeyError) as exc:
        raise CheckpointBaselineError("Checkpoint-tiedoston JSON tai rakenne on virheellinen.") from exc

    return {
        "module_id": module_id,
        "branch": branch,
        "path": path,
        "blob_sha": current.sha,
        "run_id": run_id,
        "checked_at": checked_at,
        "observed_at": observed_at,
    }
