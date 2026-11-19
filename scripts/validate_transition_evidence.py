"""Validoi pysyvän moduulisiirtymän auditointilokin skeema ja tietuepolut."""
from __future__ import annotations

import json
from pathlib import Path

from scripts.module_transition_evidence import (
    TransitionEvidenceError, _validate_record,
)

ROOT = Path(__file__).resolve().parents[1]


def validate_evidence_tree(repository_root: Path = ROOT) -> int:
    """Validoi kaikki repositoriossa olevat auditointitietueet ja niiden omistajuuspolut."""
    root = Path(repository_root)
    schema_path = root / "schemas/module-transition-evidence.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    import jsonschema
    jsonschema.Draft202012Validator.check_schema(schema)

    evidence_root = root / "data/module-transition-evidence"
    if not evidence_root.exists():
        return 0

    count = 0
    for path in sorted(evidence_root.rglob("*.json")):
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise TransitionEvidenceError(f"Auditointitiedostoa ei voi lukea: {path}") from exc
        _validate_record(record, schema_path)
        relative = path.relative_to(evidence_root)
        expected = Path(
            record["module_id"], record["run_id"],
            f"{record['event_type']}-{record['event_id']}.json",
        )
        if relative != expected:
            raise TransitionEvidenceError(f"Auditointitietueen polku ei vastaa sen tunnisteita: {path}")
        count += 1
    return count


def main() -> int:
    count = validate_evidence_tree()
    print(f"Moduulisiirtymän auditointitietueet validoitu: {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
