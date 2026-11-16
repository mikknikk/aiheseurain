#!/usr/bin/env python3
"""
Tarkistaa uutisseurannan RSS-syötteet ja niitä kuvaavan dokumentaation.

Skripti ei muuta tiedostoja. Se lukee syötteet, tarkistaa niiden rakenteen
ja päättää lopuksi, läpäiseekö repository automaattiset laatutestit.
"""

from __future__ import annotations

from datetime import datetime
from html.parser import HTMLParser
import json
import jsonschema
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from zoneinfo import ZoneInfo
from urllib.parse import urlsplit


# ROOT tarkoittaa projektin juurikansiota. Koska tämä skripti on scripts/-
# kansiossa, sen yläpuolella oleva kansio on koko repository.
ROOT = Path(__file__).resolve().parents[1]

# Kaikki kymmenen julkaistavaa RSS-syötettä. Viimeinen on näytösvahti,
# joka toimii erillään yhdeksän aiheen päivittäisestä tehtäväkierrosta.
FEEDS = [
    "feeds/tolkien.xml",
    "feeds/taylor-swift.xml",
    "feeds/gurmeet-ram-rahim-singh.xml",
    "feeds/muumit.xml",
    "feeds/wakaliwood.xml",
    "feeds/euroviisut.xml",
    "feeds/sompote-sands.xml",
    "feeds/shakkidraamat.xml",
    "feeds/intialaiset-elokuvat.xml",
    "feeds/intialaisten-elokuvien-naytokset.xml",
]
ROTATION_FEEDS = FEEDS[:-1]

# HTML:ssä on elementtejä, joilla ei ole erillistä sulkutagia.
# Esimerkiksi <br> ja <img> ovat tällaisia. Muut elementit pitää sulkea.
VOID = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
}


def fail(message: str) -> None:
    """Tulostaa virheen ja keskeyttää testin epäonnistuneena.

    GitHub Actions tulkitsee ohjelman päättymisen virhekoodiin epäonnistumiseksi.
    Näin virhe ei jää huomaamatta, vaikka testejä ajettaisiin automaattisesti.
    """
    print(f"VIRHE: {message}", file=sys.stderr)
    raise SystemExit(1)


class HTMLCheck(HTMLParser):
    """Tutkii RSS-kuvauksen sisällä olevaa HTML-koodia.

    RSS-kuvauksen sisältö on HTML-katkelma: tarkistamme, että tagit sulkeutuvat
    oikein, linkeissä on kelvolliset osoitteet ja kuvilla on vaihtoehtotekstit.
    Tämä ei ole täydellinen HTML-standardin tarkistin, vaan projektin tarpeisiin
    tehty kevyt rakennetarkistus.
    """

    def __init__(self, label: str):
        super().__init__(convert_charrefs=True)
        # label kertoo, minkä syötteen ja uutisen HTML:ää parhaillaan tutkitaan.
        self.label = label

        # stack pitää kirjaa avatuista elementeistä. Viimeisenä avattu pitää
        # sulkea ensimmäisenä, kuten sisäkkäisissä HTML-elementeissä kuuluu.
        self.stack = []
        self.errors = []

        # Laskemme linkit ja keräämme otsikkotasot myöhempää tarkistusta varten.
        self.links = 0
        self.headings = []

    def _start(self, tag, attrs, closed=False):
        """Käsittelee HTML-elementin aloituksen ja sen attribuutit."""
        attrs_map = {}

        # Muutamme attribuutit sanakirjaksi, jotta esimerkiksi href löytyy
        # helposti. Sama attribuutti kahdesti on yleensä virhe.
        for key, value in attrs:
            if key in attrs_map:
                self.errors.append(f"attribuutti {key!r} kahdesti")
            attrs_map[key] = value

        if tag == "a":
            # Linkin pitää osoittaa verkko-osoitteeseen, jossa on http/https
            # ja palvelimen nimi. Suhteelliset ja tyhjät osoitteet eivät kelpaa.
            href = (attrs_map.get("href") or "").strip()
            parsed = urlsplit(href)
            if parsed.scheme not in {"http", "https"} or not parsed.netloc:
                self.errors.append(f"virheellinen linkin href {href!r}")
            self.links += 1

        if tag == "img" and "alt" not in attrs_map:
            # Alt-teksti auttaa ruudunlukijan käyttäjää ymmärtämään kuvan sisällön.
            self.errors.append("img-elementiltä puuttuu alt")

        if re.fullmatch(r"h[1-6]", tag):
            # Tallennetaan otsikon taso (esimerkiksi h2 -> 2), jotta voimme
            # havaita myöhemmin epäloogiset hypyt otsikkotasojen välillä.
            self.headings.append(int(tag[1]))

        # Tavallinen avauselementti lisätään pinoon. Itse itsensä sulkevia
        # elementtejä ja HTML:n tyhjiä elementtejä ei lisätä.
        if not closed and tag not in VOID:
            self.stack.append(tag)

    def handle_starttag(self, tag, attrs):
        """HTMLParser kutsuu tätä tavallisen avaustagin kohdalla."""
        self._start(tag, attrs)

    def handle_startendtag(self, tag, attrs):
        """Käsittelee itse itsensä sulkevan tagin, esimerkiksi <br/>."""
        self._start(tag, attrs, True)

    def handle_endtag(self, tag):
        """Varmistaa, että sulkutagi vastaa viimeksi avattua elementtiä."""
        if tag in VOID or not self.stack or self.stack[-1] != tag:
            self.errors.append(f"virheellinen sulkutagi </{tag}>")

            # Jos sulkutagi löytyy pinon sisältä, siivoamme pinon siitä
            # ylöspäin. Näin tarkistin voi jatkaa muiden virheiden etsimistä.
            if tag in self.stack:
                while self.stack and self.stack[-1] != tag:
                    self.stack.pop()
                if self.stack:
                    self.stack.pop()
            return

        self.stack.pop()

    def close(self):
        """Viimeistelee tarkistuksen ja etsii keskeneräiset rakenteet."""
        super().close()

        # Jos pinoon jäi elementtejä, niiltä puuttuu sulkutagi.
        if self.stack:
            self.errors.append("sulkematta: " + ", ".join(self.stack))

        # Otsikkotasossa ei pitäisi hypätä esimerkiksi h2:sta suoraan h4:ään.
        # Tasojen ei tarvitse aina kasvaa, mutta yhden tason ylittävä hyppy
        # tekee dokumentin rakenteesta vaikeammin hahmotettavan.
        previous = 0
        for level in self.headings:
            if previous and level > previous + 1:
                self.errors.append(f"otsikkotaso hyppää h{previous} -> h{level}")
            previous = level


def timestamp(value, label):
    """Muuntaa aikaleiman päivämääräolioksi ja tarkistaa aikavyöhykkeen.

    Tyhjä tai puuttuva aikaleima voidaan esittää null-arvolla (Pythonissa None).
    Se on hyödyllistä silloin, kun vanhasta tarkistuksesta ei ole luotettavaa
    tietoa. Aikaleimaa ei pidä keksiä jälkikäteen.
    """
    if value is None:
        return None

    if not isinstance(value, str) or not value.strip():
        fail(f"{label}: aikaleiman pitää olla ISO 8601 -merkkijono tai null")

    try:
        # Pythonin datetime tunnistaa aikavyöhykkeen sisältävän ISO 8601 -ajan.
        # Z tarkoittaa UTC-aikaa, joten muutamme sen Pythonille sopivaksi +00:00:ksi.
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        fail(f"{label}: virheellinen ISO 8601 -aikaleima {value!r}")

    # Aikaleiman on sisällettävä aikavyöhyke. Ilman sitä emme voi luotettavasti
    # verrata eri ajojen aikoja tai määrittää Suomen paikallista seurantajaksoa.
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        fail(f"{label}: aikavyöhyke puuttuu")

    return parsed


def validate_state():
    """Tarkistaa data/seurantatila.json-tiedoston sisällön.

    Tiedosto kertoo, mitä aihetta seuraavaksi käsitellään ja milloin kukin
    aihe tai näytösvahti on viimeksi tarkistettu onnistuneesti.
    """
    path = ROOT / "data/seurantatila.json"

    if not path.is_file():
        fail("data/seurantatila.json puuttuu")

    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        fail(f"seurantatilan JSON virheellinen: {exc}")

    # Ylimmän tason pitää olla JSON-olio ja sen rakenteen version pitää olla 1.
    if not isinstance(state, dict) or state.get("schema_version") != 1:
        fail("seurantatilan pitää olla schema_version 1 -JSON-olio")

    # Kaikki projektin raportointiajat käyttävät Suomen aikavyöhykettä.
    if state.get("timezone") != "Europe/Helsinki":
        fail("timezone pitää olla Europe/Helsinki")

    timestamp(state.get("updated_at"), "updated_at")

    rotation = state.get("rotation")
    if not isinstance(rotation, dict):
        fail("rotation-olio puuttuu")

    tasks = rotation.get("tasks")
    if not isinstance(tasks, dict) or len(tasks) != 9:
        fail("rotation.tasks pitää sisältää yhdeksän tehtävää")

    # Seuraavan tehtävän nimen täytyy löytyä tehtävälistan avaimista.
    if rotation.get("next_task") not in tasks:
        fail("rotation.next_task ei viittaa tehtävään")

    mapped = []

    # Käymme jokaisen yhdeksästä kiertotehtävästä läpi erikseen.
    for key, task in tasks.items():
        label = f"rotation.tasks.{key}"

        if not isinstance(task, dict):
            fail(f"{label} ei ole olio")

        # Nimi, syötetiedosto ja viimeisimmän ajon tulos ovat pakollisia tietoja.
        for field in ("name", "feed", "last_result"):
            if not isinstance(task.get(field), str) or not task[field].strip():
                fail(f"{label}.{field} puuttuu")

        mapped.append(task["feed"])

        # Kiertotehtävä ei saa vahingossa osoittaa näytösvahtiin tai tuntemattomaan syötteeseen.
        if task["feed"] not in ROTATION_FEEDS:
            fail(f"{label}.feed ei kuulu kiertoon")

        # Virhelista on aina merkkijonoista koostuva lista, myös silloin kun se on tyhjä.
        if not isinstance(task.get("errors"), list) or not all(
            isinstance(x, str) for x in task["errors"]
        ):
            fail(f"{label}.errors pitää olla merkkijonolista")

        # Luemme onnistuneen tarkistuksen ajan sekä tarkistetun uutisjakson rajat.
        success = timestamp(task.get("last_successful_check"), label + ".last_successful_check")
        start = timestamp(task.get("last_period_start"), label + ".last_period_start")
        end = timestamp(task.get("last_period_end"), label + ".last_period_end")

        # Seurantajaksolla on aina sekä alku että loppu – tai ei kumpaakaan.
        if (start is None) != (end is None):
            fail(f"{label}: jakson alku ja loppu kirjattava yhdessä")

        # Ilman onnistunutta tarkistusta ei voida väittää, että jakso olisi käsitelty.
        if success is None and start is not None:
            fail(f"{label}: jakso ilman onnistunutta tarkistusta")

        # Jakson loppu ei voi olla myöhempi kuin tarkistus, jossa se käsiteltiin.
        if success is not None and end is not None and end > success:
            fail(f"{label}: seurantajakso päättyy onnistuneen tarkistuksen jälkeen")

        # Julkaistujen uutisten ja tarkistettujen lähteiden määrät ovat joko
        # ei-negatiivisia kokonaislukuja tai null, jos määrää ei tunneta.
        for field in ("published_items", "sources_checked"):
            value = task.get(field)
            if value is not None and (type(value) is not int or value < 0):
                fail(f"{label}.{field} pitää olla ei-negatiivinen kokonaisluku tai null")

    # Jokaisen kiertosyötteen pitää esiintyä täsmälleen kerran. Tämä estää
    # esimerkiksi saman aiheen lisäämisen kahdelle vuorolle ja jonkin unohtumisen.
    if len(set(mapped)) != 9 or set(mapped) != set(ROTATION_FEEDS):
        fail("JSON-tehtävät eivät vastaa yksilöllisesti yhdeksää kiertosyötettä")

    # Näytösvahti tarkistetaan erikseen, koska se ei ole osa yhdeksän aiheen kiertoa.
    watch = state.get("separate_screening_watch")
    if not isinstance(watch, dict):
        fail("separate_screening_watch puuttuu")

    if watch.get("feed") != FEEDS[-1] or watch.get("cadence") != "daily":
        fail("näytösvahdin feedin ja päivittäisen rytmin pitää olla oikein")

    if not isinstance(watch.get("errors"), list) or not all(
        isinstance(x, str) for x in watch["errors"]
    ):
        fail("näytösvahdin errors pitää olla merkkijonolista")

    success = timestamp(watch.get("last_successful_check"), "screening.last_successful_check")
    start = timestamp(watch.get("last_period_start"), "screening.last_period_start")
    end = timestamp(watch.get("last_period_end"), "screening.last_period_end")

    if (start is None) != (end is None) or (success is None and start is not None):
        fail("näytösvahdin seurantajakso on epäjohdonmukainen")

    for field in ("published_items", "sources_checked"):
        value = watch.get(field)
        if value is not None and (type(value) is not int or value < 0):
            fail(f"screening.{field} pitää olla ei-negatiivinen kokonaisluku tai null")

    return state




class ScreeningHistoryHTMLParser(HTMLParser):
    """Kerää HTML-kuvauksen Historialliset näytösajat -osion listakohdat."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.in_h2 = False
        self.in_li = False
        self.current_heading = ""
        self.current_li = []
        self.historical_rows = []
        self.historical_section_seen = False
        self.in_historical_section = False

    def handle_starttag(self, tag, attrs):
        if tag == "h2":
            self.in_h2 = True
            self.current_heading = ""
        elif tag == "li":
            self.in_li = True
            self.current_li = []

    def handle_endtag(self, tag):
        if tag == "h2":
            is_history_heading = (
                self.current_heading.strip().casefold() == "historialliset näytösajat"
            )
            self.historical_section_seen = self.historical_section_seen or is_history_heading
            self.in_historical_section = is_history_heading
            self.in_h2 = False
        elif tag == "li":
            if self.in_li and self.in_historical_section:
                row = " ".join("".join(self.current_li).split())
                if row:
                    self.historical_rows.append(row)
            self.in_li = False
            self.current_li = []

    def handle_data(self, data):
        if self.in_h2:
            self.current_heading += data
        if self.in_li:
            self.current_li.append(data)


def validate_screening_history_rss(history):
    """Varmistaa, että completed-tietueet näkyvät uusimmassa elokuvakohtaisessa RSS-itemissä.

    Vertailu tehdään näytöksen päivämäärän, kellonajan, teatterin ja kaupungin
    perusteella. Tarkistus on kaksisuuntainen: JSONista ei saa puuttua RSS-riviä,
    eikä RSS:n historiassa saa olla ylimääräistä tai kahteen kertaan julkaistua riviä.
    """
    feed_path = ROOT / "feeds/intialaisten-elokuvien-naytokset.xml"
    try:
        root = ET.fromstring(feed_path.read_text(encoding="utf-8"))
    except (OSError, ET.ParseError) as exc:
        fail(f"näytöshistorian RSS-vertailu ei onnistu: {exc}")

    channel = root.find("channel")
    if channel is None:
        fail("näytöshistorian RSS-vertailussa channel puuttuu")

    items = channel.findall("item")
    screenings = history["screenings"]
    films = sorted({item["film"] for item in screenings})
    completed_by_film = {
        film: [item for item in screenings
               if item["film"] == film and item["status"] == "completed"]
        for film in films
    }

    for film in films:
        completed = completed_by_film[film]
        if not completed:
            continue

        # Itemit ovat uusimmasta vanhimpaan. Valitaan ensimmäinen juuri tälle
        # elokuvalle kuuluva julkaisu, ei koko syötteen ensimmäistä itemiä.
        latest = next(
            (item for item in items
             if (item.findtext("title") or "").strip().startswith(film + " –")),
            None,
        )
        if latest is None:
            fail(f"{film}: RSS:stä puuttuu elokuvan uusin julkaisuitem")

        description = latest.findtext("description") or ""
        parser = ScreeningHistoryHTMLParser()
        parser.feed(description)
        parser.close()

        if not parser.historical_section_seen:
            fail(f"{film}: uusimmasta RSS-itemistä puuttuu Historialliset näytösajat -osio")

        expected = {}
        for screening in completed:
            starts = timestamp(
                screening["starts_at"],
                f"{film}/{screening['screening_id']}.starts_at",
            )
            local = starts.astimezone(ZoneInfo("Europe/Helsinki"))
            # Näytösten RSS käyttää Suomen paikallista aikaa.
            date_text = f"{local.day}.{local.month}."
            time_text = f"{local.hour:02d}.{local.minute:02d}"
            key = (date_text, time_text, screening["venue"], screening["city"])
            if key in expected:
                fail(f"{film}: JSON-historiassa on päällekkäinen completed-näytös {key}")
            expected[key] = screening["screening_id"]

        actual = {}
        for row in parser.historical_rows:
            match = re.search(
                r"(?P<date>\d{1,2}\.\d{1,2}\.)\s*klo\s*"
                r"(?P<time>\d{1,2}\.\d{2})\s*[–-]\s*"
                r"(?P<venue>.*?)\s*\((?P<city>[^()]+)\)",
                row,
            )
            if not match:
                fail(f"{film}: historiallisesta RSS-rivistä ei voi lukea näytöksen tietoja: {row}")
            key = (
                match.group("date"),
                match.group("time").zfill(5),
                match.group("venue").strip(),
                match.group("city").strip(),
            )
            if key in actual:
                fail(f"{film}: RSS:n historiallinen näytösrivi toistuu: {key}")
            actual[key] = row

        missing = sorted(set(expected) - set(actual))
        extra = sorted(set(actual) - set(expected))
        if missing or extra:
            details = []
            if missing:
                details.append("puuttuvat JSON-historian rivit: " + repr(missing))
            if extra:
                details.append("ylimääräiset RSS-historiarivit: " + repr(extra))
            fail(f"{film}: RSS:n historialliset näytösajat eivät vastaa JSON-historiaa; " + "; ".join(details))

    print("OK: RSS:n historialliset näytösajat vastaavat JSON-historian completed-tietueita.")



def validate_screening_history():
    """Tarkistaa näytösseurannan erillisen, tapahtumapohjaisen muutoshistorian.

    RSS-syöte säilyttää lukijalle julkaistut versiot. Tämä JSON-tiedosto
    puolestaan tallentaa koneellisesti nykyiset näytöstiedot ja jokaisen
    myöhemmin havaitun muutoksen. Tapahtumalokia saa vain täydentää.
    """
    path = ROOT / "data/naytosten-muutoshistoria.json"

    if not path.is_file():
        fail("data/naytosten-muutoshistoria.json puuttuu")

    try:
        history = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        fail(f"näytösten muutoshistorian JSON virheellinen: {exc}")

    # Tarkistamme ensin tietomallin virallista JSON Schema -määrittelyä vasten.
    # Näin pakolliset kentät, tietotyypit ja tapahtumien ehdollinen rakenne eivät
    # jää vain tämän Python-skriptin käsin kirjoitettujen ehtojen varaan.
    schema_path = ROOT / "schemas/naytosten-muutoshistoria.schema.json"
    if not schema_path.is_file():
        fail("näytöshistorian JSON Schema -määrittely puuttuu")

    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator.check_schema(schema)
        schema_validator = jsonschema.Draft202012Validator(
            schema, format_checker=jsonschema.FormatChecker()
        )
        schema_errors = sorted(
            schema_validator.iter_errors(history),
            key=lambda error: (list(map(str, error.absolute_path)), error.message),
        )
    except (json.JSONDecodeError, UnicodeDecodeError, jsonschema.SchemaError) as exc:
        fail(f"näytöshistorian JSON Schema on virheellinen: {exc}")

    if schema_errors:
        first = schema_errors[0]
        location = ".".join(str(part) for part in first.absolute_path) or "(juuritaso)"
        fail(f"näytöshistoria ei vastaa JSON Schemaa kohdassa {location}: {first.message}")

    if not isinstance(history, dict) or history.get("schema_version") != 1:
        fail("näytösten muutoshistorian pitää olla schema_version 1 -JSON-olio")

    if history.get("timezone") != "Europe/Helsinki":
        fail("näytösten muutoshistorian timezone pitää olla Europe/Helsinki")

    if history.get("baseline_status") not in {
        "pending_first_verified_run", "active"
    }:
        fail("näytösten muutoshistorian baseline_status on virheellinen")

    screenings = history.get("screenings")
    events = history.get("events")

    if not isinstance(screenings, list) or not isinstance(events, list):
        fail("näytösten muutoshistorian screenings ja events pitää olla listoja")

    # Näytöksen tunniste säilyy samana, vaikka sen aikaa tai muita tietoja
    # muutetaan. Tunnistetta ei saa luoda uudelleen jokaisessa päivityksessä.
    screening_ids = set()
    allowed_statuses = {"scheduled", "cancelled", "removed", "completed"}
    allowed_claim_types = {
        "TEATTERIN VAHVISTAMA",
        "JÄRJESTÄJÄN ILMOITTAMA",
        "KOLMANNEN OSAPUOLEN ILMOITTAMA",
    }

    for number, screening in enumerate(screenings, 1):
        label = f"screenings[{number}]"

        if not isinstance(screening, dict):
            fail(f"{label} ei ole JSON-olio")

        for field in ("screening_id", "film", "venue", "city", "status"):
            if not isinstance(screening.get(field), str) or not screening[field].strip():
                fail(f"{label}.{field} puuttuu tai on tyhjä")

        screening_id = screening["screening_id"]
        if screening_id in screening_ids:
            fail(f"näytöksen tunniste toistuu: {screening_id}")
        screening_ids.add(screening_id)

        if screening["status"] not in allowed_statuses:
            fail(f"{label}.status on virheellinen")

        starts_at = timestamp(screening.get("starts_at"), label + ".starts_at")
        if starts_at is None:
            fail(f"{label}.starts_at pitää olla aikavyöhykkeellinen ISO 8601 -aikaleima")

        if screening.get("source_claim_type") not in allowed_claim_types:
            fail(f"{label}.source_claim_type on virheellinen")

        sources = screening.get("sources")
        if not isinstance(sources, list) or not sources:
            fail(f"{label}.sources pitää sisältää vähintään yksi lähde")

        for source_number, source in enumerate(sources, 1):
            source_label = f"{label}.sources[{source_number}]"
            if not isinstance(source, dict):
                fail(f"{source_label} ei ole JSON-olio")

            for field in ("publisher", "url", "checked_at", "claim_type"):
                if not isinstance(source.get(field), str) or not source[field].strip():
                    fail(f"{source_label}.{field} puuttuu")

            parsed_url = urlsplit(source["url"])
            if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
                fail(f"{source_label}.url ei ole kelvollinen HTTP(S)-osoite")

            timestamp(source["checked_at"], source_label + ".checked_at")
            timestamp(source.get("published_at"), source_label + ".published_at")

            if source["claim_type"] not in allowed_claim_types:
                fail(f"{source_label}.claim_type on virheellinen")

    # Tapahtumaloki on append-only: tapahtumilla on yksilöllinen tunniste,
    # aikaleima, tyyppi ja tieto siitä, mitä näytöstä muutos koskee.
    allowed_event_types = {
        "baseline_created",
        "added",
        "time_changed",
        "venue_changed",
        "details_changed",
        "cancelled",
        "removed_from_listing",
        "reinstated",
        "correction",
    }
    event_ids = set()

    for number, event in enumerate(events, 1):
        label = f"events[{number}]"

        if not isinstance(event, dict):
            fail(f"{label} ei ole JSON-olio")

        for field in ("event_id", "observed_at", "type", "note"):
            if not isinstance(event.get(field), str) or not event[field].strip():
                fail(f"{label}.{field} puuttuu tai on tyhjä")

        if event["event_id"] in event_ids:
            fail(f"muutoshistorian event_id toistuu: {event['event_id']}")
        event_ids.add(event["event_id"])

        timestamp(event["observed_at"], label + ".observed_at")

        if event["type"] not in allowed_event_types:
            fail(f"{label}.type on tuntematon: {event['type']}")

        if event["type"] != "baseline_created":
            screening_id = event.get("screening_id")
            if not isinstance(screening_id, str) or not screening_id.strip():
                fail(f"{label}.screening_id puuttuu")
            if screening_id not in screening_ids:
                fail(f"{label} viittaa tuntemattomaan näytökseen: {screening_id}")

        sources = event.get("sources")
        if not isinstance(sources, list):
            fail(f"{label}.sources pitää olla lista")

        if event["type"] not in {"baseline_created", "correction"} and not sources:
            fail(f"{label}: muutostapahtuma tarvitsee vähintään yhden lähteen")

        for source_number, source in enumerate(sources, 1):
            source_label = f"{label}.sources[{source_number}]"
            if not isinstance(source, dict):
                fail(f"{source_label} ei ole JSON-olio")
            for field in ("publisher", "url", "checked_at", "claim_type"):
                if not isinstance(source.get(field), str) or not source[field].strip():
                    fail(f"{source_label}.{field} puuttuu")
            parsed_url = urlsplit(source["url"])
            if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
                fail(f"{source_label}.url ei ole kelvollinen HTTP(S)-osoite")
            timestamp(source["checked_at"], source_label + ".checked_at")
            timestamp(source.get("published_at"), source_label + ".published_at")
            if source["claim_type"] not in allowed_claim_types:
                fail(f"{source_label}.claim_type on virheellinen")

        for field in ("previous", "current"):
            value = event.get(field)
            if value is not None and not isinstance(value, dict):
                fail(f"{label}.{field} pitää olla JSON-olio tai null")

    # Lähtötason pitää olla selvästi keskeneräinen, kun historia on tyhjä.
    # Aktiivinen historia edellyttää nimenomaista lähtötason luontitapahtumaa.
    baseline_events = [event for event in events if event["type"] == "baseline_created"]
    if history["baseline_status"] == "pending_first_verified_run":
        if screenings or events:
            fail("odottavassa lähtötilassa screenings ja events pitää olla tyhjiä")
    elif len(baseline_events) != 1:
        fail("aktiivisessa muutoshistoriassa pitää olla täsmälleen yksi baseline_created-tapahtuma")

    return history


def validate_docs(state):
    """Vertaa README:tä ja tehtäväjonoa koneelliseen seurantatilaan."""
    queue_path = ROOT / "docs/tehtavajono.md"
    readme_path = ROOT / "README.md"

    if not queue_path.is_file() or not readme_path.is_file():
        fail("README.md tai docs/tehtavajono.md puuttuu")

    queue = queue_path.read_text(encoding="utf-8")
    readme = readme_path.read_text(encoding="utf-8")

    # Näytösten muutoshistorian rakenne ja käyttöohje ovat osa ylläpidettävää
    # järjestelmää. Varmistamme, ettei uusi tietomalli jää irralliseksi tiedostoksi.
    history_guide = ROOT / "docs/nayostohistorian-rakenne.md"
    screening_guide = ROOT / "docs/intialaisten-elokuvien-naytosseuranta.md"
    if not history_guide.is_file() or not screening_guide.is_file():
        fail("näytösten muutoshistorian tai näytösvahdin dokumentti puuttuu")

    if "docs/nayostohistorian-rakenne.md" not in readme:
        fail("README ei linkitä näytösten muutoshistorian tietomalliin")

    screening_instructions = screening_guide.read_text(encoding="utf-8")
    for required_phrase in (
        "data/naytosten-muutoshistoria.json",
        "baseline_created",
        "removed_from_listing",
        "event_id",
    ):
        if required_phrase not in screening_instructions:
            fail(
                "näytösvahdin ohjeesta puuttuu muutoshistorian sääntö: "
                + required_phrase
            )

    # Poimimme tehtäväjonosta numeroidut rivit, joissa on myös RSS-syötteen polku.
    # Näin voimme verrata dokumentissa kuvattua järjestystä JSON-tiedostoon.
    entries = re.findall(
        r"^\s*\d+\.\s+(.+?)\s+—\s+`(feeds/[^ `]+\.xml)`\s*$",
        queue,
        re.M,
    )

    if len(entries) != 9:
        fail(f"tehtäväjonossa pitää olla yhdeksän tehtävää, löytyi {len(entries)}")

    queue_feeds = [feed for _, feed in entries]

    # Tehtäväjonon järjestys on tarkoituksellinen: sen pitää vastata syötteiden
    # määriteltyä kiertojärjestystä, jotta seuraava vuoro ei vaihdu vahingossa.
    if queue_feeds != ROTATION_FEEDS:
        fail("tehtäväjonon järjestys tai feed-polut eivät vastaa määritystä")

    # Etsimme dokumentista tekstin, joka kertoo seuraavan vuorossa olevan aiheen.
    match = re.search(r"\*\*Vuorossa seuraavaksi:\s*(.+?)\.\*\*", queue)
    if not match:
        fail("tehtäväjonon seuraavaa vuoroa ei löydy")

    task = state["rotation"]["tasks"][state["rotation"]["next_task"]]
    expected = entries[queue_feeds.index(task["feed"])][0]

    if match.group(1).strip() != expected:
        fail(
            f"tehtäväjonon seuraava vuoro ({match.group(1).strip()}) "
            f"ei vastaa JSON-tilaa ({expected})"
        )

    # Tehtäväjono pidetään suppeana: yhteiset säännöt kuuluvat omiin ohjedokumentteihinsa.
    for obsolete_heading in (
        "## Seurantajakson aikaväli",
        "## Skriptien kommentointi",
        "## Koneellinen seurantatila",
    ):
        if obsolete_heading.lower() in queue.lower():
            fail(f"tehtäväjonossa on yhteinen sääntö, joka kuuluu erilliseen ohjeeseen: {obsolete_heading}")

    # Pääautomaation täysi ohjeistus on GitHubissa. Sen version on vastattava
    # koneelliseen seurantatilaan tallennettua nykyistä versiota, jotta automaatio
    # ei voi huomaamatta käyttää vanhaa tai väärää toimintakäsikirjaa.
    automation_guide = ROOT / "docs/paaautomaation-ohje.md"
    automation_version = state.get("automation_instructions")
    if not automation_guide.is_file() or not isinstance(automation_version, dict):
        fail("pääautomaation ohjekäsikirja tai sen versionhallinnan tila puuttuu")

    guide_text = automation_guide.read_text(encoding="utf-8")
    version_match = re.search(r"^Ohjeversion tunniste:\s*(\d+\.\d+\.\d+)\s*$", guide_text, re.M)
    if not version_match:
        fail("pääautomaation käsikirjasta puuttuu kelvollinen MAJOR.MINOR.PATCH-versio")

    if "docs/paaautomaation-ohje.md" not in readme:
        fail("README ei linkitä pääautomaation versionhallittua käsikirjaa")
    if "## pääautomaation lukujärjestys ja tehtäväkierto" not in readme.lower():
        fail("README:stä puuttuu pääautomaation lukujärjestys")

    if automation_version.get("document") != "docs/paaautomaation-ohje.md":
        fail("seurantatilan pääautomaation käsikirjan polku on virheellinen")
    if automation_version.get("current_version") != version_match.group(1):
        fail("pääautomaation käsikirjan ja seurantatilan nykyiset ohjeversiot eivät täsmää")

    for field in ("last_successful_run_version",):
        value = automation_version.get(field)
        if value is not None and not re.fullmatch(r"\d+\.\d+\.\d+", value):
            fail("automation_instructions." + field + " ei ole kelvollinen versiotunniste")
    timestamp(automation_version.get("last_successful_run_at"), "automation_instructions.last_successful_run_at")
    if (automation_version.get("last_successful_run_version") is None) != (automation_version.get("last_successful_run_at") is None):
        fail("pääautomaation viimeisimmän onnistuneen version ja ajan pitää olla molemmat asetettuja tai null")

    # Näytösvahdilla on oma versioitu käsikirja ja sen tila on erillään uutiskierron tilasta.
    screening_instructions = state["separate_screening_watch"].get("automation_instructions")
    if not isinstance(screening_instructions, dict):
        fail("näytösvahdin ohjeversion seurantatila puuttuu")
    screening_version = re.search(
        r"^Ohjeversion tunniste:\s*(\d+\.\d+\.\d+)\s*$",
        screening_guide.read_text(encoding="utf-8"),
        re.M,
    )
    if not screening_version:
        fail("näytösvahdin käsikirjasta puuttuu kelvollinen MAJOR.MINOR.PATCH-versio")
    if screening_instructions.get("document") != "docs/intialaisten-elokuvien-naytosseuranta.md":
        fail("näytösvahdin käsikirjan polku on virheellinen")
    if screening_instructions.get("current_version") != screening_version.group(1):
        fail("näytösvahdin käsikirjan ja JSONin nykyiset ohjeversiot eivät täsmää")
    if "docs/intialaisten-elokuvien-naytosseuranta.md" not in readme:
        fail("README ei viittaa näytösvahdin käsikirjaan")
    for field in ("last_successful_run_version",):
        value = screening_instructions.get(field)
        if value is not None and not re.fullmatch(r"\d+\.\d+\.\d+", value):
            fail("screening automation_instructions." + field + " ei ole kelvollinen versiotunniste")
    timestamp(screening_instructions.get("last_successful_run_at"), "screening.automation_instructions.last_successful_run_at")
    if (screening_instructions.get("last_successful_run_version") is None) != (screening_instructions.get("last_successful_run_at") is None):
        fail("näytösvahdin viimeisimmän onnistuneen version ja ajan pitää olla molemmat asetettuja tai null")

    # Viikoittaisen laatutarkistuksen käsikirjan version on vastattava koneellista tilaa.
    quality_guide = ROOT / "docs/laatutarkistuksen-ohje.md"
    quality_instructions = state.get("quality_check_instructions")
    if not quality_guide.is_file() or not isinstance(quality_instructions, dict):
        fail("laatutarkistuksen käsikirja tai sen versionhallinnan tila puuttuu")
    quality_version = re.search(
        r"^Ohjeversion tunniste:\s*(\d+\.\d+\.\d+)\s*$",
        quality_guide.read_text(encoding="utf-8"),
        re.M,
    )
    if not quality_version:
        fail("laatutarkistuksen käsikirjasta puuttuu kelvollinen MAJOR.MINOR.PATCH-versio")
    if quality_instructions.get("document") != "docs/laatutarkistuksen-ohje.md":
        fail("laatutarkistuksen käsikirjan polku on virheellinen")
    if quality_instructions.get("current_version") != quality_version.group(1):
        fail("laatutarkistuksen käsikirjan ja JSONin nykyiset ohjeversiot eivät täsmää")
    if "docs/laatutarkistuksen-ohje.md" not in readme:
        fail("README ei viittaa laatutarkistuksen käsikirjaan")
    value = quality_instructions.get("last_successful_run_version")
    if value is not None and not re.fullmatch(r"\d+\.\d+\.\d+", value):
        fail("quality_check_instructions.last_successful_run_version ei ole kelvollinen versiotunniste")
    timestamp(quality_instructions.get("last_successful_run_at"), "quality_check_instructions.last_successful_run_at")
    if (quality_instructions.get("last_successful_run_version") is None) != (quality_instructions.get("last_successful_run_at") is None):
        fail("laatutarkistuksen viimeisimmän onnistuneen version ja ajan pitää olla molemmat asetettuja tai null")

    tracking_guide = ROOT / "docs/seuranta.md"
    development_guide = ROOT / "docs/kehityskaytannot.md"
    if not tracking_guide.is_file() or not development_guide.is_file():
        fail("docs/seuranta.md tai docs/kehityskaytannot.md puuttuu")

    tracking_text = tracking_guide.read_text(encoding="utf-8").lower()
    development_text = development_guide.read_text(encoding="utf-8").lower()
    for required_phrase in ("seurantajakso", "rotation.next_task", "data/seurantatila.json", "github actions", "scripts/validate_feeds.py"):
        if required_phrase not in tracking_text:
            fail(f"docs/seuranta.md: pakollinen toimintaperiaate puuttuu: {required_phrase}")
    for required_phrase in ("python-skriptien kommentointi", "docstring", "suomeksi", "tarkistus ennen muutoksen valmistumista"):
        if required_phrase not in development_text:
            fail(f"docs/kehityskaytannot.md: kommentointikäytäntö puuttuu: {required_phrase}")

    # Dokumenttien vastuut pidetään yksiselitteisinä: tehtäväjono sisältää
    # vain kiertojärjestyksen ja seuraavan vuoron, kun taas raportointijaksot
    # ja koneellinen seurantatila kuuluvat seurantaohjeeseen.
    queue_lower = queue.lower()
    if "seurantajaksojen raportointisääntö" in queue_lower or "python-skriptien kommentointi" in queue_lower:
        fail("tehtäväjonossa on yhteisiä ohjeita, joiden pitää olla omissa dokumenteissaan")

    if "docs/seuranta.md" not in readme or "docs/kehityskaytannot.md" not in readme:
        fail("README ei ohjaa yleisiin seuranta- ja kehityskäytäntöihin")

    if "kahdeksan aihekohtaisen seurannan syötteet" in readme.lower():
        fail("README:n syötteiden lukumäärä on vanhentunut tai epäselvä")

    if "## yleiset seurantamerkinnät" in tracking_text:
        fail("docs/seuranta.md sisältää tyhjän tai tarpeettoman yleisotsikon")

    for required_section in (
        "## pääautomaation lukujärjestys ja tehtäväkierto",
        "## tiedostojen vastuut",
        "## automaattiset laatutestit",
    ):
        if required_section not in readme.lower():
            fail("README:stä puuttuu dokumentaation rakenteen kannalta keskeinen osio: " + required_section)

    # Tarkistamme dokumenttien väliset lukumäärät ja tehtävärajaukset,
    # koska ne vaikuttavat suoraan automaation tekemien hakujen laajuuteen.
    if "kaikissa yhdeksässä aihekierroksen tehtävässä" not in readme.lower():
        fail("README ei kuvaa maailmanlaajuisen haun kattavan kaikki yhdeksän kiertotehtävää")

    indian_news_guide = ROOT / "docs/intialaisen-elokuvan-uutiset.md"
    indian_overview = ROOT / "docs/intialaisen-elokuvan-ohje.md"
    if not indian_news_guide.is_file() or not indian_overview.is_file():
        fail("intialaisen elokuvan uutisohje tai yleisohje puuttuu")
    indian_news_text = indian_news_guide.read_text(encoding="utf-8").lower()
    indian_overview_text = indian_overview.read_text(encoding="utf-8").lower()
    if "kymmenen seuratun henkilön ja kahdeksan projektin" not in indian_news_text:
        fail("intialaisen elokuvan uutisohjeen seurattavien projektien lukumäärä ei vastaa kahdeksaa projektia")
    if "## näytösseuranta samassa tehtävässä" in indian_overview_text:
        fail("intialaisen elokuvan yleisohjeessa on vanhentunut näytösseurannan otsikko")

    # README:n pitää luetella kaikki kymmenen syötettä – myös erillinen näytösfeed.
    readme_feeds = set(re.findall(r"\]\((feeds/[^)]+\.xml)\)", readme))
    if readme_feeds != set(FEEDS):
        fail(
            "README:n feed-taulukko ei vastaa kymmentä feed-tiedostoa: "
            f"puuttuu {sorted(set(FEEDS) - readme_feeds)}"
        )

    # Varmistamme, että README kertoo yhdeksän aiheen kierrosta ja näytösvahdin
    # erillisyydestä. Tämä on kevyt tekstipohjainen ristiriitojen tunnistus.
    if "yhdeksän" not in readme.lower() or "ei kuluta" not in readme.lower():
        fail("README ei kuvaa yhdeksän aiheen kiertoa ja erillistä näytösvahtia")

    if "ei kuulu tähän jonoon" not in queue.lower():
        fail("tehtäväjono ei kuvaa näytösseurannan erillisyyttä")

    # Myös tehtävien nimet tarkistetaan, jotta syötepolku ei voi olla oikein
    # mutta aiheeseen liitetty nimi väärä.
    for name, feed in entries:
        state_task = next(
            (item for item in state["rotation"]["tasks"].values() if item["feed"] == feed),
            None,
        )
        if state_task is None or state_task["name"] != name:
            fail(f"JSON-tehtävän nimi ei vastaa tehtäväjonoa: {name}")

    # Nämä vanhat sanamuodot tarkoittaisivat, että näytösseuranta olisi yhä
    # tehtäväjonon vuoro. Nykyisessä mallissa se on oma päivittäinen automationsa.
    stale_phrases = (
        "tehtäväjonon omalla vuorolla",
        "tehtäväjonon erillisellä näytösvuorolla",
        "tehtäväjonon erillinen tehtävä",
        "erillinen jonotehtävä",
    )

    for relative in (
        "docs/intialaisen-elokuvan-ohje.md",
        "docs/intialaisen-elokuvan-uutiset.md",
        "docs/intialaisen-elokuvan-seuranta.md",
    ):
        doc = ROOT / relative

        if not doc.is_file():
            fail(f"intialaisen elokuvan dokumentti puuttuu: {relative}")

        lowered = doc.read_text(encoding="utf-8").lower()

        for phrase in stale_phrases:
            if phrase in lowered:
                fail(f"{relative}: vanhentunut näytösseurannan kuvaus: {phrase}")

    # Lopuksi varmistamme, että kaikki dokumentaatiossa odotetut syötetiedostot
    # todella löytyvät repositoryn kansiorakenteesta.
    for feed in FEEDS:
        if not (ROOT / feed).is_file():
            fail(f"RSS-syöte puuttuu: {feed}")


def validate_feeds():
    """Tarkistaa kaikki RSS-syötteet ja niiden uutisitemit."""
    seen = {}
    total = 0

    for relative in FEEDS:
        path = ROOT / relative

        if not path.is_file():
            fail(f"RSS-tiedosto puuttuu: {relative}")

        raw = path.read_text(encoding="utf-8")

        # XML-parseri tarkistaa, että tiedosto on rakenteellisesti kelvollista XML:ää.
        try:
            root = ET.fromstring(raw)
        except ET.ParseError as exc:
            fail(f"{relative}: XML ei jäsenny: {exc}")

        if root.tag != "rss" or root.find("channel") is None:
            fail(f"{relative}: rss/channel puuttuu")

        channel = root.find("channel")

        # Poimimme itemit myös alkuperäisestä tekstistä, jotta voimme varmistaa,
        # että jokaisen description-elementin ympärillä on CDATA-merkintä.
        raw_items = re.findall(r"<item\b[\s\S]*?</item\s*>", raw, re.I)
        items = channel.findall("item")

        if len(raw_items) != len(items):
            fail(f"{relative}: item-lukumäärä ei täsmää")

        for number, (item, raw_item) in enumerate(zip(items, raw_items), 1):
            label = f"{relative}, item {number}"

            # Projektin julkaisusäännön mukaan itemissä ei saa olla link-elementtiä.
            if item.find("link") is not None:
                fail(f"{label}: item-link on kielletty")

            # GUID on uutisen pysyvä tunniste. Se ei saa puuttua eikä toistua
            # missään kymmenestä syötteestä.
            guid = (item.findtext("guid") or "").strip()

            if not guid:
                fail(f"{label}: GUID puuttuu")

            if guid in seen:
                fail(f"{label}: GUID {guid!r} on jo tiedostossa {seen[guid]}")

            seen[guid] = relative

            # Description sisältää varsinaisen raportin ja sen lähdeluettelon.
            description = item.findtext("description") or ""

            if not description.strip():
                fail(f"{label}: description puuttuu")

            # XML-parseri purkaa CDATA-alueen tekstiksi, joten alkuperäisestä
            # tekstistä pitää erikseen tarkistaa, että CDATA todella oli käytössä.
            match = re.search(
                r"<description\b[^>]*>([\s\S]*?)</description\s*>",
                raw_item,
                re.I,
            )

            if not match or "<![CDATA[" not in match.group(1):
                fail(f"{label}: description ei ole CDATA-alueessa")

            # Lähdeluettelon otsikon pitää löytyä raportin lopusta/sisällöstä.
            if not re.search(
                r"lähdeluettelo|<h[1-6][^>]*>\s*lähteet\s*</h[1-6]>",
                description,
                re.I,
            ):
                fail(f"{label}: lähdeluettelon otsikko puuttuu")

            # Käynnistämme HTML-tarkistimen kuvaustekstille.
            parser = HTMLCheck(label)

            try:
                parser.feed(description)
                parser.close()
            except Exception as exc:
                fail(f"{label}: HTML:n käsittely epäonnistui: {exc}")

            # Tulostetaan ensimmäiset havaitut virheet, jotta ongelman etsintä
            # on helpompaa. Yksi virhe riittää kuitenkin hylkäämään itemin.
            if parser.errors:
                fail(f"{label}: kuvaus-HTML: " + "; ".join(parser.errors[:5]))

            if parser.links == 0:
                fail(f"{label}: kuvauksessa ei ole linkkejä")

            total += 1

    # Palautamme itemien kokonaismäärän ja yksilöllisten GUIDien määrän.
    return total, len(seen)


def main():
    """Ajaa kaikki tarkistukset oikeassa järjestyksessä."""
    # Ensin tarkistetaan seurantatila, jotta dokumentteja voidaan verrata siihen.
    state = validate_state()

    # Seuraavaksi tarkistetaan dokumenttien ja seurantatilan yhdenmukaisuus.
    validate_docs(state)

    # Tarkistetaan myös näytösseurannan koneellisesti luettava muutoshistoria.
    screening_history = validate_screening_history()
    validate_screening_history_rss(screening_history)

    # Lopuksi käydään RSS-syötteet ja niiden julkaistut itemit läpi.
    total, unique = validate_feeds()

    # Jos tähän asti päästiin, kaikki testit läpäisivät.
    print(f"OK: {len(FEEDS)} syötettä, {total} itemiä, {unique} yksilöllistä GUIDia.")
    print("OK: kuvausten HTML-rakenne, linkit, otsikkotasot, alt-attribuutit ja lähdeluettelot.")
    print("OK: README, tehtäväjono, feed-polut ja seurantatila ovat yhdenmukaiset.")
    print("OK: aikaleimat, seurantajaksot, erillinen näytösvahti ja näytösten muutoshistoria.")
    print("OK: näytöshistoria vastaa JSON Schema Draft 2020-12 -määrittelyä.")
    print("OK: RSS:n historialliset näytösajat vastaavat JSON-historian completed-tietueita.")


# Tämä ehto tarkoittaa, että main()-funktio suoritetaan vain, kun tiedosto
# käynnistetään suoraan skriptinä – ei silloin, jos joku tuo sen moduulina toiseen ohjelmaan.
if __name__ == "__main__":
    main()
