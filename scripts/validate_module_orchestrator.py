"""Validoi yhteisen moduuliorchestratorin sopimukset ja käyttöönoton turvarajat."""
import json
from pathlib import Path
import jsonschema
from scripts.module_registry import load_registry

ROOT = Path(__file__).resolve().parents[1]
from scripts.module_orchestrator import (
    ModuleRunRequest, ModuleRunResult, validate_run_request, validate_run_result
)


def main() -> None:
    """Varmista skeemat ja että tuotantoon ei ole aktivoitu moduuleja."""
    registry = load_registry(include_inactive=True)
    if registry.invalid_modules:
        raise SystemExit("Moduulirekisterissä on virheellisiä määrityksiä.")
    if len(registry.modules) != 10 or any(item.status != "inactive" for item in registry.modules):
        raise SystemExit("Orkestroinnin käyttöönottoportti odottaa kymmentä passiivista moduulia.")
    if any(item.definition is None for item in registry.modules):
        raise SystemExit("Varjotilan määritysten validointi ei ladannut kaikkia moduuleja.")

    request = ModuleRunRequest(
        module_id="tolkien", module_definition_version="1.0.0", contract_version="1.0.0",
        run_id="schema-validation-run", period_start="2026-11-17T00:00:00+02:00",
        period_end="2026-11-18T00:00:00+02:00", mode="shadow",
        requested_at="2026-11-18T00:00:00+02:00"
    )
    validate_run_request(request)
    target_report_schema = json.loads((ROOT / "schemas/target-report.schema.json").read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(target_report_schema)
    # Tarkista myös GitHub-runtime-varaston skeemat ennen sovittimien käyttöä.
    for schema_name in ("module-artifact-index.schema.json", "module-publication-journal.schema.json"):
        runtime_schema = json.loads((ROOT / "schemas" / schema_name).read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator.check_schema(runtime_schema)
    result = ModuleRunResult(
        module_id="tolkien", module_type="topic", module_definition_version="1.0.0",
        contract_version="1.0.0", run_id="schema-validation-run",
        period_start=request.period_start, period_end=request.period_end,
        mode="shadow", status="succeeded", phase="complete",
        started_at="2026-11-18T00:00:00+00:00", finished_at="2026-11-18T00:00:01+00:00"
    )
    validate_run_result(result)
    print("OK: suorituspyyntö-, tulos-, kohderaportti- ja GitHub-runtime-sopimukset validoituvat.")
    print("OK: kaikki kymmenen moduulia voidaan lukea varjotilaan, mutta yksikään ei ole aktiivinen.")
    print("OK: tuotantokäyttöönotto vaatii erillisen hyväksynnän eikä CI muuta automaatioasetuksia.")


if __name__ == "__main__":
    main()
