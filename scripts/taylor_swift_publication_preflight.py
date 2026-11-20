"""Taylor Swift -jakson aiemman julkaisun fail-closed-ennakkotarkistus.

Tämä moduulikohtainen tarkistin arvioi erikseen toimitetut, lähteistetyt
havainnot. Se ei hae verkosta eikä kirjoita GitHubiin tai tuotantotilaan.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any

MODULE_ID = "taylor-swift"
REQUIRED_CHANNELS = ("legacy", "runtime", "repository_rss", "pages")
ALLOWED_STATES = {"published", "unpublished", "unknown"}


class PublicationPreflightError(ValueError):
    """Ennakkotarkistuksen syöte on virheellinen."""


def _aware_datetime(value: str, field: str) -> datetime:
    """Varmista, että seurantajakson rajalla on aikavyöhyke."""
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, TypeError, ValueError) as exc:
        raise PublicationPreflightError(f"{field} ei ole kelvollinen ISO 8601 -aikaleima.") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise PublicationPreflightError(f"{field} tarvitsee aikavyöhykkeen.")
    return parsed


def assess_taylor_swift_publication_state(evidence: dict[str, Any]) -> dict[str, Any]:
    """Luokittele täsmällisen jakson julkaisutila ilman oletuksia puuttuvista tiedoista.

    Yksikin luotettava published-havainto osoittaa, että jakso on julkaistu.
    Ristiriita published- ja unpublished-havaintojen välillä pysäyttää ajon.
    Unpublished voidaan palauttaa vain, kun kaikki neljä kanavaa on tarkistettu
    ja jokainen niistä osoittaa saman täsmällisen jakson julkaisemattomaksi.
    """
    if not isinstance(evidence, dict) or evidence.get("module_id") != MODULE_ID:
        raise PublicationPreflightError("Ennakkotarkistus hyväksyy vain Taylor Swift -moduulin.")
    period = evidence.get("period")
    if not isinstance(period, dict):
        raise PublicationPreflightError("Täsmällinen seurantajakso puuttuu.")
    start_text, end_text = period.get("start"), period.get("end")
    start, end = _aware_datetime(start_text, "period.start"), _aware_datetime(end_text, "period.end")
    if start > end:
        raise PublicationPreflightError("Seurantajakson alku on loppua myöhempi.")

    observations = evidence.get("observations")
    if not isinstance(observations, dict):
        raise PublicationPreflightError("Julkaisukanavien havainnot puuttuvat.")

    states: list[str] = []
    missing: list[str] = []
    checked_channels: list[str] = []
    references: dict[str, str] = {}
    for channel in REQUIRED_CHANNELS:
        item = observations.get(channel)
        if not isinstance(item, dict):
            missing.append(channel)
            continue
        if item.get("period") != period:
            raise PublicationPreflightError(
                f"{channel}-havainto ei koske täsmälleen samaa seurantajaksoa."
            )
        status = item.get("check_status")
        publication_status = item.get("publication_status")
        reference = item.get("reference")
        if not isinstance(reference, str) or not reference.strip():
            raise PublicationPreflightError(f"{channel}-havainnon lähdeviite puuttuu.")
        references[channel] = reference
        if status != "checked":
            missing.append(channel)
            continue
        checked_channels.append(channel)
        if publication_status not in ALLOWED_STATES:
            raise PublicationPreflightError(f"{channel}-havainnon julkaisutila on virheellinen.")
        if publication_status == "unknown":
            missing.append(channel)
        else:
            states.append(publication_status)

    has_published = "published" in states
    has_unpublished = "unpublished" in states
    if has_published and has_unpublished:
        result = "conflict"
    elif has_published:
        result = "published"
    elif missing or len(states) != len(REQUIRED_CHANNELS):
        result = "unknown"
    elif has_unpublished:
        result = "unpublished"
    else:
        result = "unknown"

    return {
        "schema_version": 1,
        "module_id": MODULE_ID,
        "period": period,
        "publication_state": result,
        "execution_allowed": result == "unpublished",
        "checked_channels": checked_channels,
        "missing_or_unknown_channels": sorted(set(missing)),
        "references": references,
        "limitations": [
            "Tarkistin ei hae eikä varmista lähteitä itse; havaintojen oikeellisuus on kerääjän vastuulla.",
            "Puuttuva runtime-haara tai julkisen Pages-syötteen takaisinluvun puuttuminen ei todista julkaisemattomuutta.",
            "Tuntematon tai ristiriitainen tila estää harjoituksen.",
        ],
    }
