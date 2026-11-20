#!/usr/bin/env python3
"""Validoi yhteisen lähdekatalogin, aihekohtaiset lähdekäytöt ja ajolokit.

Katalogi sisältää lähteiden yhteiset perustiedot kerran. Aihekohtaisissa
rekistereissä säilytetään vain lähdeviittaus ja kyseisen tehtävän asetukset.
Skripti on vain luku -tarkistin eikä arvioi lähteiden tosiasiallista luotettavuutta.
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
    """Validoi katalogin, tehtäväkohtaiset viittaukset ja lähdetarkistuslokin."""
    loki = lue_json("data/lahdetarkistukset.json")
    katalogi = lue_json("data/source-catalog.json")
    jsonschema.validate(katalogi, lue_json("schemas/lahdekatalogi.schema.json"))
    jsonschema.validate(loki, lue_json("schemas/lahdetarkistukset.schema.json"))

    lahteet = {}
    for lahde in katalogi["sources"]:
        lahde_id = lahde["id"]
        if lahde_id in lahteet:
            raise ValueError(f"Lähdekatalogissa on toistuva ID: {lahde_id}")
        osat = urlsplit(lahde["url"])
        if osat.scheme not in {"http", "https"} or not osat.netloc:
            raise ValueError(f"Lähteen {lahde_id} URL ei ole kelvollinen HTTP(S)-osoite")
        lahteet[lahde_id] = lahde

    rekisterit = {}
    rekisteripolut = sorted((ROOT / "data" / "sources").glob("*.json"))
    if not rekisteripolut:
        raise ValueError("data/sources/ ei sisällä aihekohtaisia käyttörekistereitä")

    for polku in rekisteripolut:
        suhteellinen = polku.relative_to(ROOT).as_posix()
        rekisteri = lue_json(suhteellinen)
        jsonschema.validate(rekisteri, lue_json("schemas/lahderekisteri.schema.json"))
        tehtava = rekisteri["task_id"]
        if polku.stem != tehtava:
            raise ValueError(f"{suhteellinen}: tiedostonimen pitää vastata task_id-arvoa {tehtava}")
        if tehtava in rekisterit:
            raise ValueError(f"Tehtävälle {tehtava} on useita rekistereitä")
        tarkista_aikaleima(rekisteri.get("updated_at"), f"{suhteellinen}.updated_at", True)

        tehtavan_lahteet = {}
        for kaytto in rekisteri["sources"]:
            source_id = kaytto["source_id"]
            if source_id in tehtavan_lahteet:
                raise ValueError(f"{suhteellinen}: lähdeviittaus {source_id} esiintyy kahdesti")
            if source_id not in lahteet:
                raise ValueError(f"{suhteellinen}: lähdeviittaus {source_id} puuttuu katalogista")
            tarkista_aikaleima(kaytto["last_checked_at"], f"{tehtava}/{source_id}.last_checked_at", True)
            tehtavan_lahteet[source_id] = kaytto
        rekisterit[tehtava] = tehtavan_lahteet

    if set(rekisterit) != TOPICS:
        puuttuvat = sorted(TOPICS - set(rekisterit))
        ylimaaraiset = sorted(set(rekisterit) - TOPICS)
        raise ValueError(f"Aihekohtaisten rekisterien tehtäväjoukko ei täsmää; puuttuvat={puuttuvat}, ylimääräiset={ylimaaraiset}")

    run_ids = set()
    viimeisin = {}
    for ajo in loki["runs"]:
        if ajo["run_id"] in run_ids:
            raise ValueError(f"Ajolokissa on toistuva run_id: {ajo['run_id']}")
        run_ids.add(ajo["run_id"])
        tehtava = ajo["task_id"]
        if tehtava not in TOPICS:
            raise ValueError(f"Tuntematon tehtävä ajolokissa: {tehtava}")
        tarkista_aikaleima(ajo["started_at"], f"{ajo['run_id']}.started_at")
        tarkista_aikaleima(ajo["ended_at"], f"{ajo['run_id']}.ended_at")
        aloitus = datetime.fromisoformat(ajo["started_at"].replace("Z", "+00:00"))
        paattyminen = datetime.fromisoformat(ajo["ended_at"].replace("Z", "+00:00"))
        if paattyminen < aloitus:
            raise ValueError(f"{ajo['run_id']}: päättymisaika on ennen aloitusaikaa")

        kaikki_idt = ajo["checked_source_ids"] + [puute["source_id"] for puute in ajo["unchecked_sources"]]
        if len(kaikki_idt) != len(set(kaikki_idt)):
            raise ValueError(f"{ajo['run_id']}: sama lähde on merkitty useaan tilaan")
        tehtavan_lahteet = rekisterit[tehtava]
        for source_id in kaikki_idt:
            if source_id not in tehtavan_lahteet:
                raise ValueError(f"{ajo['run_id']}: lähde {source_id} ei kuulu tehtävän {tehtava} rekisteriin")

        # Uusissa ajoissa tarkistetaan lokin täydellisyys ajon oman rekisteri-
        # snapshotin perusteella. Vanhoissa merkinnöissä snapshot puuttuu,
        # joten säilytetään aiempi yhteensopiva kriittisten lähteiden tarkistus.
        if "registry_source_ids" in ajo:
            snapshot_ids = ajo["registry_source_ids"]
            if set(kaikki_idt) != set(snapshot_ids):
                puuttuvat = sorted(set(snapshot_ids) - set(kaikki_idt))
                ylimaaraiset = sorted(set(kaikki_idt) - set(snapshot_ids))
                raise ValueError(
                    f"{ajo['run_id']}: checked/unchecked ei vastaa registry_source_ids-kenttää; "
                    f"puuttuvat={puuttuvat}, ylimääräiset={ylimaaraiset}"
                )
            kriittiset_idt = snapshot_ids
        else:
            kriittiset_idt = tehtavan_lahteet.keys()

        for source_id in kriittiset_idt:
            kaytto = tehtavan_lahteet[source_id]
            if kaytto["critical"] and source_id not in kaikki_idt and ajo["status"] == "complete":
                raise ValueError(f"{ajo['run_id']}: kriittinen lähde {source_id} puuttuu sekä tarkistetuista että tarkistamatta jääneistä lähteistä")

        nykyinen = datetime.fromisoformat(ajo["ended_at"].replace("Z", "+00:00"))
        aiempi = viimeisin.get(tehtava)
        if aiempi is None or nykyinen > aiempi:
            viimeisin[tehtava] = nykyinen

    odotetut = {tehtava: aika.isoformat() for tehtava, aika in viimeisin.items()}
    if loki["latest_by_task"] != odotetut:
        raise ValueError("latest_by_task ei vastaa ajolokin uusimpia ajoja")

    kayttojen_maara = sum(len(r) for r in rekisterit.values())
    print(f"OK: {len(lahteet)} yksilöllistä katalogilähdettä, {kayttojen_maara} aihekohtaista lähdekäyttöä, {len(rekisterit)} rekisteriä ja {len(loki['runs'])} lähdetarkistusajoa.")


if __name__ == "__main__":
    validate_source_coverage()
