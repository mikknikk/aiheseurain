"""Kohdekohtaisen suorituskehyksen verkkohakuton esimerkki.

Esimerkki käyttää rekisteriin tallennettuja Tolkien-kohteita ja niiden
hakuprofiileja, mutta runner palauttaa synteettisen testituloksen. Se ei
käytä verkkoyhteyttä, julkaise RSS:ää tai muuta tuotannon tilaa.
"""
from scripts.module_orchestrator import ModuleRunRequest
from scripts.target_execution import (
    TargetExecutionContext, TargetExecutionCoordinator, TargetExecutionResult,
)


class ExampleTargetRunner:
    """Testirunner käyttää vain sille annetun kohteen omaa hakuprofiilia."""

    def execute(
        self, context: TargetExecutionContext, provider_router: object
    ) -> TargetExecutionResult:
        profile_names = ", ".join(profile["id"] for profile in context.search_profiles)
        return TargetExecutionResult(
            status="succeeded",
            source_scan_complete=True,
            checked_at=context.requested_at,
            observation_types=("report.article",),
            report_content=(
                f"<p>Synteettinen esimerkkiraportti kohteelle {context.target_id}. "
                f"Kohteen omat hakuprofiilit: {profile_names}.</p>"
            ),
            sources_checked=len(context.search_profiles),
            source_check_run_refs=(f"example-source-check-{context.target_id}",),
        )


def build_example_output(request: ModuleRunRequest):
    """Palauta kahden rekisteröidyn Tolkien-kohteen erilliset testiraportit."""
    definition = {
        "module_id": "tolkien",
        "definition_version": "1.0.0",
        "target_refs": ["tolkien.j-r-r-tolkien", "tolkien.tolkien-estate"],
    }
    return TargetExecutionCoordinator().execute(
        definition, request, provider_router=None, runner=ExampleTargetRunner()
    )
