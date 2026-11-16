#!/usr/bin/env python3
"""Tarkistaa lähderekisterin ja ajokohtaisen lähdekattavuuslokin rakenteen.

Skripti on vain luku -tarkistin. Se ei käy verkkosivuilla eikä päättele,
onko lähde tosiasiassa tarkistettu tai onko aiheen kattavuus riittävä.
"""

from __future__ import annotations

from datetime import datetime
import json
import jsonschema
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
TOPICS = {
    "tolkien", "taylor_swift", "gurmeet_ram_rahim_singh", "muumit",
    "wakaliwood", "euroviisut", "sompote_sands", "shakkidraamat",
    "intialaiset_elokuvat_uutiset", "intialaiset_elokuvat_naytokset",
}


def lue_json(polku: str):
    """Lukee JSON-tiedoston ja antaa ymmärrettävän virheen, jos se ei kelpaa."""
    try:
        return json.loads((ROOT / polku).read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ValueError(f"{polku} puuttuu")
    except (json.JSONDecodeError, UnicodeDecodeError) as virhe:
        raise ValueError(f"{polku}: virheellinen JSON: {virhe}") from virhe


def tarkista_aikaleima(arvo, sijainti: str, sallii_null: bool = False):
    """Varmistaa ISO 8601 -aikaleiman ja aikavyöhykkeen."""
    if arvo is None and sallii_null:
        return
    if not isinstance(arvo, str):
        raise ValueError(f"{sijainti}: aikaleima puuttuu tai ei ole merkkijono")
    try:
        aika = datetime.fromisoformat(arvo.replace("Z", "+00:00"))
    except ValueError as virhe:
        raise ValueError(f"{sijainti}: virheellinen aikaleima {arvo!r}") from virhe
    if aika.tzinfo is None or aika.utcoffset() is None:
        raise ValueError(f"{sijainti}: aikavyöhyke puuttuu")


def validate_source_coverage():
    """Tarkistaa skeemat sekä lähde-ID:iden ja ajolokien väliset viittaukset."""
    rekisteri = lue_json("data/lahderekisteri.json")
    loki = lue_json("data/lahdetarkistukset.json")
    rekisteri_skeema = lue_json("schemas/lahderekisteri.schema.json")
    loki_skeema = lue_json("schemas/lahdetarkistukset.schema.json")

    jsonschema.validate(rekisteri, rekisteri_skeema)
    jsonschema.validate(loki, loki_skeema)
    tarkista_aikaleima(rekisteri.get("updated_at"), "lahderekisteri.updated_at", True)

    lahteet = rekisteri["sources"]
    tunnisteet = [lahde["id"] for lahde in lahteet]
    if len(tunnisteet) != len(set(tunnisteet)):
        raise ValueError("Lähderekisterissä on päällekkäisiä lähde-ID-tunnisteita")

    lahde_idt = set(tunnisteet)
    for lahde in lahteet:
        osat = urlsplit(lahde["url"])
        if osat.scheme not in {"http", "https"} or not osat.netloc:
            raise ValueError(f"Lähteen {lahde['id']} URL ei ole kelvollinen HTTP(S)-osoite")
        if not lahde["regions"]:
            raise ValueError(f"Lähteeltä {lahde['id']} puuttuvat maantieteelliset alueet")
        tarkista_aikaleima(
            lahde["last_checked_at"],
            f"lähde {lahde['id']}.last_checked_at",
            True,
        )

    run_ids = set()
    viimeisin = {}
    for ajo in loki["runs"]:
        if ajo["run_id"] in run_ids:
            raise ValueError(f"Ajolokissa on toistuva run_id: {ajo['run_id']}")
        run_ids.add(ajo["run_id"])
        if ajo["task_id"] not in TOPICS:
            raise ValueError(f"Tuntematon tehtävä ajolokissa: {ajo['task_id']}")
        tarkista_aikaleima(ajo["started_at"], f"{ajo['run_id']}.started_at")
        tarkista_aikaleima(ajo["ended_at"], f"{ajo['run_id']}.ended_at")
        aloitus = datetime.fromisoformat(ajo["started_at"].replace("Z", "+00:00"))
        paattyminen = datetime.fromisoformat(ajo["ended_at"].replace("Z", "+00:00"))
        if paattyminen < aloitus:
            raise ValueError(f"{ajo['run_id']}: päättymisaika on ennen aloitusaikaa")

        kaikki_idt = ajo["checked_source_ids"] + [
            puute["source_id"] for puute in ajo["unchecked_sources"]
        ]
        if len(kaikki_idt) != len(set(kaikki_idt)):
            raise ValueError(f"{ajo['run_id']}: sama lähde on merkitty useaan tilaan")
        for source_id in kaikki_idt:
            if source_id not in lahde_idt:
                raise ValueError(f"{ajo['run_id']}: tuntematon lähde-ID {source_id}")
            lahde = next(item for item in lahteet if item["id"] == source_id)
            if ajo["task_id"] not in lahde["topics"]:
                raise ValueError(
                    f"{ajo['run_id']}: lähde {source_id} ei kuulu tehtävään {ajo['task_id']}"
                )
        for lahde in lahteet:
            if ajo["task_id"] in lahde["topics"] and lahde["critical"]:
                if lahde["id"] not in kaikki_idt and ajo["status"] == "complete":
                    raise ValueError(
                        f"{ajo['run_id']}: kriittinen lähde {lahde['id']} puuttuu "
                        "sekä tarkistetuista että tarkistamatta jääneistä lähteistä"
                    )
        nykyinen = datetime.fromisoformat(ajo["ended_at"].replace("Z", "+00:00"))
        aiempi = viimeisin.get(ajo["task_id"])
        if aiempi is None or nykyinen > aiempi:
            viimeisin[ajo["task_id"]] = nykyinen

    odotetut = {
        tehtava: aika.isoformat()
        for tehtava, aika in viimeisin.items()
    }
    if loki["latest_by_task"] != odotetut:
        raise ValueError("latest_by_task ei vastaa ajolokin uusimpia ajoja")

    print(
        f"OK: {len(lahteet)} lähderekisterimerkintää, "
        f"{len(loki['runs'])} lähdetarkistusajoa."
    )


if __name__ == "__main__":
    validate_source_coverage()
