"""Moduulikohtaisen tuotantoluvan fail-closed-lataus.

Tämä erillinen rekisteri ei aktivoi moduuleja itsestään. Kaikki moduulit ovat
oletusarvoisesti pois käytöstä, ja rekisterin on vastattava moduulirekisteriä
täsmälleen. Prosessimoduuleja ei voi aktivoida tämän topic-julkaisupolun kautta.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import jsonschema

from scripts.module_registry import load_registry

ROOT = Path(__file__).resolve().parents[1]
ACTIVATION_PATH = ROOT / "data/module-production-activation.json"
SCHEMA_PATH = ROOT / "schemas/module-production-activation.schema.json"


class ProductionActivationError(RuntimeError):
    """Tuotantoluparekisteri puuttuu, on virheellinen tai ristiriitainen."""


def load_production_activation(
    module_id: str,
    *,
    activation_path: Path = ACTIVATION_PATH,
    registry_loader: Any = load_registry,
) -> bool:
    """Palauta yhden topic-moduulin tuotantolupa; virheissä hylkää suljetusti."""
    try:
        document = json.loads(Path(activation_path).read_text(encoding="utf-8"))
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator.check_schema(schema)
        jsonschema.Draft202012Validator(schema).validate(document)
        registry = registry_loader(include_inactive=True)
        entries = {item.module_id: item for item in registry.modules}
        configured = document["modules"]
        if set(configured) != set(entries):
            raise ProductionActivationError("Aktivointirekisterin moduulit eivät vastaa moduulirekisteriä.")
        for key, enabled in configured.items():
            entry = entries[key]
            if entry.definition is None:
                raise ProductionActivationError(f"Moduulin {key} määritys ei ole kelvollinen.")
            if entry.definition.get("module_type") == "process" and enabled:
                raise ProductionActivationError("Prosessimoduulia ei voi aktivoida topic-julkaisupolkuun.")
        if module_id not in entries:
            raise ProductionActivationError("Tuntematonta moduulia ei voi aktivoida.")
        if entries[module_id].definition.get("module_type") != "topic":
            return False
        return configured[module_id]
    except ProductionActivationError:
        raise
    except Exception as exc:
        raise ProductionActivationError("Tuotantoluparekisteriä ei voitu validoida.") from exc
