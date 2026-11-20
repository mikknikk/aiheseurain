"""Validoi Taylor Swift -varjoharjoituksen ChatGPT-tulos erilliseen artefaktiin.

Tämä sovitin ei käynnistä tutkimusta eikä kirjoita tuotantotietoja. Se hyväksyy
vain erikseen hyväksytyn harjoituksen tuloksen ja sitoo sen valmistelun
run_id-, seurantajakso- ja syötehash-arvoihin.
"""
from __future__ import annotations

from datetime import datetime
import hashlib
import json
from pathlib import Path
from typing import Any

from scripts.chatgpt_module_result import validate_chatgpt_result
from scripts.module_orchestrator import ModuleRunRequest
from scripts.taylor_swift_shadow import (
    MODULE_ID, TaylorSwiftShadowError, prepare_taylor_swift_shadow,
)


def validate_taylor_swift_shadow_result(
    preparation: dict[str, Any], payload: dict[str, Any], *,
    approval_reference: str, root: Path,
) -> dict[str, Any]:
    """Validoi aiemmin tuotetun tuloksen; ei suorita ajoa eikä muuta tuotantotilaa."""
    if preparation.get("artifact_type") != "taylor_swift_shadow_preparation":
        raise TaylorSwiftShadowError("Varjoharjoituksen valmisteluasiakirja puuttuu tai on virheellinen.")
    if preparation.get("module_id") != MODULE_ID or preparation.get("status") != "prepared":
        raise TaylorSwiftShadowError("Valmisteluasiakirjan moduuli tai tila ei täsmää.")
    if preparation.get("execution_authorized") is not False:
        raise TaylorSwiftShadowError("Valmisteluasiakirja ei ole turvallisessa odotustilassa.")
    if not isinstance(approval_reference, str) or not approval_reference.strip():
        raise TaylorSwiftShadowError("Varsinaisen harjoituksen erillisen hyväksynnän viite puuttuu.")

    root = Path(root).resolve()
    # Tarkista, etteivät moduulin lähdetiedot muuttuneet valmistelun jälkeen.
    try:
        fresh_preparation = prepare_taylor_swift_shadow(
            run_id=preparation["run_id"],
            period_start=preparation["period"]["start"],
            period_end=preparation["period"]["end"],
            requested_at=preparation["requested_at"],
            root=root,
        )
    except (KeyError, TypeError) as exc:
        raise TaylorSwiftShadowError("Valmistelun tunnisteet puuttuvat tuloksen uudelleentarkistuksesta.") from exc
    if (fresh_preparation["input_sha256"] != preparation.get("input_sha256")
            or fresh_preparation["handoff_input_sha256"] != preparation.get("handoff_input_sha256")):
        raise TaylorSwiftShadowError("Valmistelun lähdetiedostot ovat muuttuneet; tulosta ei voi liittää tähän lähtötilaan.")
    try:
        registry = json.loads((root / "data/module-registry.json").read_text(encoding="utf-8"))
        entries = [item for item in registry["modules"] if item.get("module_id") == MODULE_ID]
        if len(entries) != 1:
            raise TaylorSwiftShadowError("Taylor Swift -moduulin rekisterimerkintä ei ole yksikäsitteinen.")
        definition = json.loads((root / entries[0]["path"]).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, KeyError) as exc:
        raise TaylorSwiftShadowError("Moduulin määritystä ei voi lukea tuloksen validointia varten.") from exc

    period = preparation["period"]
    request = ModuleRunRequest(
        module_id=MODULE_ID,
        module_definition_version=preparation["module_definition_version"],
        contract_version=preparation["contract_version"],
        run_id=preparation["run_id"],
        period_start=period["start"],
        period_end=period["end"],
        mode="shadow",
        requested_at=preparation["requested_at"],
    )
    try:
        validate_chatgpt_result(payload, definition, request)
    except ValueError as exc:
        raise TaylorSwiftShadowError(f"ChatGPT-tulos ei täytä Taylor Swift -varjosopimusta: {exc}") from exc

    handoff = payload.get("handoff", {})
    if handoff.get("input_sha256") != preparation.get("handoff_input_sha256"):
        raise TaylorSwiftShadowError("ChatGPT-tuloksen syötehash ei vastaa valmistelun lukittua syötehashia.")
    allowed_targets = {preparation.get("target_id")}
    for report in payload.get("target_reports", []):
        if report.get("target_id") not in allowed_targets:
            raise TaylorSwiftShadowError("ChatGPT-tulos sisältää toisen moduulin tai kohteen raportin.")

    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return {
        "schema_version": 1,
        "artifact_type": "taylor_swift_shadow_result",
        "status": payload["status"],
        "module_id": MODULE_ID,
        "module_definition_version": preparation["module_definition_version"],
        "run_id": preparation["run_id"],
        "period": preparation["period"],
        "approval_reference": approval_reference.strip(),
        "preparation_input_sha256": preparation["handoff_input_sha256"],
        "chatgpt_result_sha256": hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
        "research_performed": True,
        "publication_performed": False,
        "production_state_written": False,
        "result": payload,
        "recorded_at": datetime.now().astimezone().isoformat(),
    }
