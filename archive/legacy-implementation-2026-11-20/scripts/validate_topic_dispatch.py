"""Validoi, että uutiskierron koordinaattori voi valita yhden moduulin turvallisesti."""
from __future__ import annotations

import json
from pathlib import Path
import sys

from scripts.topic_rotation_coordinator import (
    ROOT,
    TopicCoordinatorError,
    validate_topic_rotation_configuration,
)


def main() -> int:
    """Tarkista jonon, seurantatilan, kytkentäkartan ja moduulirekisterin eheys."""
    try:
        selected = validate_topic_rotation_configuration(ROOT)
    except (TopicCoordinatorError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Aihekierron koordinaattorin validointi epäonnistui: {exc}", file=sys.stderr)
        return 1
    print(
        "Aihekierron koordinaattori valmis: "
        f"{selected.task_id} -> {selected.module_id} ({selected.module_status})."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
