"""Lukevasti sovita nykyinen näytöshistoria yleiseen tapahtumamalliin.

Sovitin säilyttää näytös-ID:t ja lähteiden alkuperäiset vahvistusluokat. Se ei
kirjoita nykyistä näytöshistoriaa uudelleen eikä muuta automaation asetuksia.
"""
from copy import deepcopy
from scripts.event_watch import empty_state, _identity, _sources

CLAIM_LEVELS = {"TEATTERIN VAHVISTAMA": "official",
                "JÄRJESTÄJÄN ILMOITTAMA": "organizer",
                "KOLMANNEN OSAPUOLEN ILMOITTAMA": "third_party"}

def _source_to_generic(source):
    """Muunna vanha lähdetietue ja säilytä sen alkuperäinen vahvistustaso."""
    original = source.get("claim_type", "KOLMANNEN OSAPUOLEN ILMOITTAMA")
    item = {"publisher": source["publisher"], "url": source["url"],
            "checked_at": source["checked_at"], "claim_level": CLAIM_LEVELS.get(original, "unknown"),
            "original_claim_type": original}
    if source.get("published_at") is not None:
        item["published_at"] = source["published_at"]
    return item

def screening_to_observation(screening, observed_at):
    """Muunna yksi näytöstietue yhteiseksi tapahtumahavainnoksi."""
    attributes = {"title": screening["film"], "venue": screening["venue"],
                  "city": screening["city"], "starts_at": screening["starts_at"],
                  "status": screening["status"]}
    for key in ("language", "subtitles", "booking_url", "external_show_id", "notes"):
        if screening.get(key) is not None:
            attributes[key] = screening[key]
    return {"event_type_id": "film-screening", "canonical_event_id": screening["screening_id"],
            "attributes": attributes,
            "sources": [_source_to_generic(source) for source in screening["sources"]],
            "observed_at": observed_at}

def screening_history_to_generic_state(history, definition):
    """Muodosta nykyisestä näytöshistoriasta yleinen lukutilanne muuttamatta lähdetiedostoa."""
    if definition.get("event_type_id") != "film-screening":
        raise ValueError("Näytössovitin tarvitsee film-screening-tapahtumatyypin.")
    state = empty_state("film-screening")
    for screening in history.get("screenings", []):
        observation = screening_to_observation(screening, screening["sources"][0]["checked_at"])
        attrs = deepcopy(observation["attributes"])
        state["current_events"].append({
            "canonical_event_id": observation["canonical_event_id"], "event_type_id": "film-screening",
            "identity_key": _identity(attrs, definition), "attributes": attrs, "status": attrs["status"],
            "sources": _sources(observation["sources"]),
            "first_seen_at": observation["observed_at"], "last_seen_at": observation["observed_at"]})
    for old in history.get("events", []):
        sources = _sources([_source_to_generic(item) for item in old.get("sources", [])])
        state["events"].append({
            "event_id": "legacy-" + old["event_id"], "observed_at": old["observed_at"],
            "event_type_id": "film-screening", "canonical_event_id": old.get("screening_id") or "baseline",
            "action": "legacy_history_imported", "legacy_event_type": old["type"],
            "previous": deepcopy(old.get("previous")), "current": deepcopy(old.get("current")),
            "sources": sources, "note": old.get("note") or "Vanha historiatapahtuma säilytetty lukutilassa."})
    return state
