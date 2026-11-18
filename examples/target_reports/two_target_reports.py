"""Esimerkkisuorittaja kahden Tolkien-seurantakohteen raportille.

Tämä on testaus- ja tietomalliesimerkki. Se ei hae uutisia, julkaise RSS:ää,
muuta tuotantotiloja eikä aktivoi passiivisia moduuleja tai seurantakohteita.
"""
from scripts.module_orchestrator import ModuleExecutionOutput, ModuleRunRequest, TargetReport


def build_two_target_example(request: ModuleRunRequest) -> ModuleExecutionOutput:
    """Muodosta kaksi erillistä raporttia yhden moduuliajon tulokseen."""
    reports = (
        TargetReport(
            target_id="tolkien.j-r-r-tolkien",
            target_version="1.0.0",
            observation_types=("report.article",),
            period_start=request.period_start,
            period_end=request.period_end,
            checked_at=request.requested_at,
            report_content="<p>Esimerkkiraportti Tolkienin teoksista ja tapahtumista.</p>",
        ),
        TargetReport(
            target_id="tolkien.tolkien-estate",
            target_version="1.0.0",
            observation_types=("report.article",),
            period_start=request.period_start,
            period_end=request.period_end,
            checked_at=request.requested_at,
            report_content="<p>Esimerkkiraportti Tolkienin oikeudenhaltijasta.</p>",
        ),
    )
    return ModuleExecutionOutput(
        status="succeeded",
        source_scan_complete=True,
        checked_at=request.requested_at,
        period_start=request.period_start,
        period_end=request.period_end,
        report_content="",
        target_reports=reports,
    )
