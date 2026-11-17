"""Testaa tapahtumavahdin yleinen ydin, kaksi tapahtumatyyppiä ja näytössovitin."""
from copy import deepcopy
import json
from pathlib import Path
import unittest

from scripts.event_watch import (EventWatchError, collect_from_adapters, empty_state, load_event_type, reconcile, validate_state)
from scripts.event_watch_adapters import (reconcile_screening_observations, screening_history_to_generic_state, screening_to_observation)

ROOT = Path(__file__).resolve().parents[1]
FILM = ROOT / "examples/event-types/film-screening.json"
CONFERENCE = ROOT / "examples/event-types/conference-session.json"
NOW = "2026-11-18T12:00:00+02:00"

def source(publisher="Testijulkaisija", url="https://example.test/event"):
    """Luo testien yksilöitävän lähdetietueen."""
    return {"publisher": publisher, "url": url, "checked_at": NOW, "claim_level": "official"}

def observation(event_id, attributes, sources=None, event_type="film-screening"):
    """Rakenna tapahtumatyypin mukainen havainto."""
    return {"event_type_id": event_type, "canonical_event_id": event_id,
            "attributes": attributes, "sources": sources or [source()], "observed_at": NOW}

class EventWatchTests(unittest.TestCase):
    """Varmista, ettei yhteinen ydin riipu yksittäisestä tapahtumatyypistä."""
    def setUp(self):
        self.film = load_event_type(FILM)
        self.conference = load_event_type(CONFERENCE)
        self.state = empty_state("film-screening")
        self.base = {"title": "Testielokuva", "venue": "Testisali", "city": "Helsinki",
                     "starts_at": "2026-11-20T18:00:00+02:00", "status": "scheduled"}

    def test_both_event_type_definitions_validate(self):
        """Elokuvanäytös ja konferenssiesitys validoituvat samalla skeemalla."""
        self.assertEqual(self.film["event_type_id"], "film-screening")
        self.assertEqual(self.conference["event_type_id"], "conference-session")

    def test_new_event_and_retry_are_idempotent(self):
        """Uusi tapahtuma lisätään kerran myös saman käsittelyn uusinnassa."""
        result = reconcile(self.state, [observation("film-1", self.base)], self.film, NOW)
        again = reconcile(result, [observation("film-1", self.base)], self.film, NOW)
        self.assertEqual(len(result["events"]), 1)
        self.assertEqual(len(again["events"]), 1)
        self.assertEqual(result["events"][0]["event_id"], again["events"][0]["event_id"])


    def test_exact_identity_duplicates_from_different_sources_are_merged(self):
        """Sama tapahtuma yhdistetään eri lähteiden eri tunnisteistä huolimatta."""
        first = observation("source-a-event-1", self.base, [source("Lähde A", "https://a.example/event")])
        second = observation("source-b-event-9", self.base, [source("Lähde B", "https://b.example/event")])
        state = reconcile(self.state, [first, second], self.film, NOW)
        self.assertEqual(len(state["current_events"]), 1)
        self.assertEqual(len(state["current_events"][0]["sources"]), 2)
        self.assertEqual(len(state["events"]), 1)

    def test_change_and_cancellation_are_tracked(self):
        """Ajan muutos ja nimenomainen peruutus kirjataan erillisinä tapahtumina."""
        state = reconcile(self.state, [observation("film-1", self.base)], self.film, NOW)
        changed = deepcopy(self.base)
        changed["starts_at"] = "2026-11-20T19:00:00+02:00"
        state = reconcile(state, [observation("film-1", changed)], self.film, "2026-11-18T13:00:00+02:00")
        cancelled = deepcopy(changed)
        cancelled["status"] = "cancelled"
        state = reconcile(state, [observation("film-1", cancelled)], self.film, "2026-11-18T14:00:00+02:00")
        self.assertEqual([item["action"] for item in state["events"]], ["created", "changed", "cancelled"])
        self.assertEqual(state["events"][1]["change_categories"], ["time_changed"])

    def test_removed_event_can_be_reinstated(self):
        """Poistuma ja palautuminen kirjataan erillisinä tapahtumina."""
        state = reconcile(self.state, [observation("film-1", self.base)], self.film, NOW)
        removed = deepcopy(self.base)
        removed["status"] = "removed"
        state = reconcile(state, [observation("film-1", removed)], self.film, "2026-11-18T13:00:00+02:00")
        state = reconcile(state, [observation("film-1", self.base)], self.film, "2026-11-18T14:00:00+02:00")
        self.assertEqual([item["action"] for item in state["events"]], ["created", "removed", "reinstated"])

    def test_conflicting_sources_are_not_silently_merged(self):
        """Ristiriita säilyttää molemmat vaihtoehdot eikä valitse viimeistä lähdettä."""
        first_attributes = deepcopy(self.base)
        first_attributes["language"] = "suomi"
        first = observation("film-1", first_attributes, [source("Lähde A", "https://a.example/event")])
        other = deepcopy(self.base)
        other["language"] = "englanti"
        second = observation("film-1", other, [source("Lähde B", "https://b.example/event")])
        state = reconcile(self.state, [first, second], self.film, NOW)
        current = state["current_events"][0]
        self.assertNotIn("language", current["attributes"])
        self.assertEqual(current["conflicts"][0]["field"], "language")
        self.assertEqual(len(current["conflicts"][0]["values"]), 2)


    def test_conflicting_required_field_is_rejected_for_new_event(self):
        """Uutta tapahtumaa ei luoda, jos pakollisesta kentästä ei ole yksimielistä tietoa."""
        other = deepcopy(self.base)
        other["status"] = "cancelled"
        first = observation("film-1", self.base, [source("Lähde A", "https://a.example/event")])
        second = observation("film-1", other, [source("Lähde B", "https://b.example/event")])
        with self.assertRaises(EventWatchError):
            reconcile(self.state, [first, second], self.film, NOW)

    def test_old_conflicts_are_not_erased_by_an_unrelated_single_source_read(self):
        """Aiempi ristiriita säilyy, kunnes sitä voidaan ratkaista nimenomaisesti."""
        first = observation("film-1", self.base)
        state = reconcile(self.state, [first], self.film, NOW)
        other = deepcopy(self.base)
        other["city"] = "Espoo"
        state = reconcile(state, [
            observation("film-1", self.base, [source("Lähde A", "https://a.example/event")]),
            observation("film-1", other, [source("Lähde B", "https://b.example/event")])
        ], self.film, "2026-11-18T13:00:00+02:00")
        self.assertTrue(state["current_events"][0]["conflicts"])
        state = reconcile(state, [observation("film-1", self.base)], self.film,
                          "2026-11-18T14:00:00+02:00")
        self.assertTrue(state["current_events"][0]["conflicts"])

    def test_partial_source_failure_does_not_remove_existing_events(self):
        """Osittainen haku kirjataan eikä puuttuvaa havaintoa tulkita poistumaksi."""
        state = reconcile(self.state, [observation("film-1", self.base)], self.film, NOW)
        state = reconcile(state, [], self.film, "2026-11-18T13:00:00+02:00",
                          scan_complete=False, failed_sources=["source-b"])
        self.assertEqual(len(state["current_events"]), 1)
        self.assertFalse(state["scans"][-1]["complete"])
        self.assertEqual(state["scans"][-1]["failed_sources"], ["source-b"])

    def test_completed_event_is_retained(self):
        """Päättynyt tapahtuma säilyy nykytilassa completed-tilassa."""
        state = reconcile(self.state, [observation("film-1", self.base)], self.film, NOW)
        completed = deepcopy(self.base)
        completed["status"] = "completed"
        state = reconcile(state, [observation("film-1", completed)], self.film, "2026-11-21T20:00:00+02:00")
        self.assertEqual(state["current_events"][0]["status"], "completed")
        self.assertEqual(state["events"][-1]["action"], "completed")

    def test_different_conference_event_uses_same_core(self):
        """Konferenssiesitys käsitellään ilman muutoksia yhteisen ytimen koodiin."""
        state = empty_state("conference-session")
        attrs = {"title": "Avausesitys", "conference": "Teknologiakonferenssi",
                 "session_code": "A1", "starts_at": "2026-12-01T09:00:00+02:00",
                 "status": "scheduled", "room": "Auditorio 1", "speaker": "Testipuhuja"}
        result = reconcile(state, [observation("conf-a1", attrs, event_type="conference-session")],
                           self.conference, NOW)
        self.assertEqual(result["current_events"][0]["attributes"]["conference"], "Teknologiakonferenssi")


    def test_source_adapter_interface_isolates_partial_failures(self):
        """Yhden lähdeadapterin virhe ei estä muiden havaintojen keräämistä."""
        class WorkingAdapter:
            source_id = "source-a"
            event_type_id = "film-screening"
            def collect(self, search_context):
                return [observation("film-1", self_test.base)]

        class FailingAdapter:
            source_id = "source-b"
            event_type_id = "film-screening"
            def collect(self, search_context):
                raise RuntimeError("Lähde ei vastaa")

        self_test = self
        result = collect_from_adapters([FailingAdapter(), WorkingAdapter()], {}, "film-screening")
        self.assertFalse(result["complete"])
        self.assertEqual(result["failed_sources"], ["source-b"])
        self.assertEqual(len(result["observations"]), 1)

    def test_timezone_is_mandatory(self):
        """Aikaleima ilman aikavyöhykettä hylätään."""
        with self.assertRaises(EventWatchError):
            reconcile(self.state, [observation("film-1", self.base)], self.film, "2026-11-18T12:00:00")

    def test_reconcile_does_not_mutate_input(self):
        """Käsittely palauttaa uuden tilan eikä muuta kutsujan alkuperäistä objektia."""
        original = empty_state("film-screening")
        reconcile(original, [observation("film-1", self.base)], self.film, NOW)
        self.assertEqual(original["current_events"], [])
        self.assertEqual(original["events"], [])

class ScreeningAdapterTests(unittest.TestCase):
    """Varmista vanhan näytöshistorian lukevan sovittimen yhteensopivuus."""
    def test_current_history_is_read_without_mutation(self):
        """Kaikki nykyiset näytökset ja historiatapahtumat muunnetaan vain muistissa."""
        definition = load_event_type(FILM)
        history = json.loads((ROOT / "data/naytosten-muutoshistoria.json").read_text(encoding="utf-8"))
        original = deepcopy(history)
        state = screening_history_to_generic_state(history, definition)
        self.assertEqual(len(state["current_events"]), len(history["screenings"]))
        self.assertEqual(len(state["events"]), len(history["events"]))
        self.assertEqual(history, original)
        validate_state(state, definition)


    def test_screening_observations_use_generic_reconciliation_core(self):
        """Näytöshavainto käyttää yhteistä ydintä ja jättää kanonisen historian ennalleen."""
        definition = load_event_type(FILM)
        history = json.loads((ROOT / "data/naytosten-muutoshistoria.json").read_text(encoding="utf-8"))
        original = deepcopy(history)
        changed = deepcopy(history["screenings"][0])
        changed["language"] = "testikieli"
        state = reconcile_screening_observations(
            history, [changed], "2026-11-18T13:00:00+02:00", definition,
            scan_complete=False, failed_sources=["unavailable-source"])
        self.assertEqual(history, original)
        self.assertEqual(state["events"][-1]["action"], "changed")
        self.assertEqual(state["events"][-1]["change_categories"], ["details_changed"])
        self.assertFalse(state["scans"][-1]["complete"])

    def test_source_claim_type_is_preserved(self):
        """Alkuperäinen teatterin vahvistus säilyy yleisen luokan rinnalla."""
        item = {"screening_id": "film-1", "film": "Testi", "venue": "Teatteri", "city": "Helsinki",
                "starts_at": "2026-11-20T18:00:00+02:00", "status": "scheduled",
                "sources": [{"publisher": "Teatteri", "url": "https://example.test/show",
                             "published_at": None, "checked_at": NOW,
                             "claim_type": "TEATTERIN VAHVISTAMA"}]}
        result = screening_to_observation(item, NOW)
        self.assertEqual(result["canonical_event_id"], "film-1")
        self.assertEqual(result["sources"][0]["claim_level"], "official")
        self.assertEqual(result["sources"][0]["original_claim_type"], "TEATTERIN VAHVISTAMA")

if __name__ == "__main__":
    unittest.main()
