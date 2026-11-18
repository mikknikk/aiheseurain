"""Elokuvatasoisten näytöshavaintojen rekisteri.

Tämä rekisteri kokoaa yksittäisistä näytöshavainnoista elokuvan pysyvän
havaintotietueen. Se ei kopioi näytösten aikoja, teattereita tai tiloja:
yksittäisten näytösten kanoninen omistaja on yleisen tapahtumavahdin
film-screening-tila ja sen append-only-historia.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
import unicodedata
from typing import Any
import jsonschema

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_SCHEMA = ROOT / "schemas/movie-observation-registry.schema.json"
CLAIM_LEVELS = {"official", "organizer", "third_party", "unknown"}


class MovieObservationError(ValueError):
    """Elokuvahavainnon tietosopimuksen tai tunnistuksen virhe."""


class MovieRegistryConflictError(MovieObservationError):
    """Elokuvarekisterin SHA-versio muuttui ennen kirjoitusta."""


def _canonical(value: Any) -> bytes:
    """Muunna JSON-tietue deterministiseksi tavujonoksi."""
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _sha(content: bytes) -> str:
    """Laske tiedoston SHA-256-versio."""
    return hashlib.sha256(content).hexdigest()


def _stable_id(prefix: str, value: Any) -> str:
    """Muodosta toistettava tunniste JSON-sisällöstä."""
    return f"{prefix}:{hashlib.sha256(_canonical(value)).hexdigest()[:24]}"


def normalize_title(title: str) -> str:
    """Normalisoi nimi vertailua varten säilyttäen eri kirjoitusjärjestelmät."""
    if not isinstance(title, str) or not title.strip():
        raise MovieObservationError("Elokuvan nimi puuttuu.")
    normalized = unicodedata.normalize("NFKC", title).casefold()
    words = []
    current = []
    for character in normalized:
        if character.isalnum():
            current.append(character)
        elif current:
            words.append("".join(current))
            current = []
    if current:
        words.append("".join(current))
    return " ".join(words)


def _timestamp(value: str) -> datetime:
    """Vaadi ISO 8601 -aikaleima, jossa on aikavyöhyke."""
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, TypeError, ValueError) as exc:
        raise MovieObservationError(f"Virheellinen aikaleima: {value!r}") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise MovieObservationError("Aikaleimasta puuttuu aikavyöhyke.")
    return parsed


def _external_ids(values: list[dict[str, str]] | None) -> list[dict[str, str]]:
    """Validoi IMDb- ja TMDB-tunnisteet ja estä saman palvelun ristiriidat."""
    found: dict[str, str] = {}
    for item in values or []:
        provider = item.get("provider")
        value = item.get("value")
        if provider not in {"imdb", "tmdb"} or not isinstance(value, str) or not value.strip():
            raise MovieObservationError("Ulkoisen tunnisteen pitää olla kelvollinen IMDb- tai TMDB-tunniste.")
        value = value.strip()
        if provider in found and found[provider] != value:
            raise MovieObservationError(f"Elokuvalla on ristiriitaiset {provider}-tunnisteet.")
        found[provider] = value
    return [{"provider": key, "value": found[key]} for key in sorted(found)]


def identify_movie(
    title: str, release_year: int | None, external_ids: list[dict[str, str]] | None,
    screening_id: str,
) -> tuple[str, str, bool]:
    """Muodosta elokuvalle vakaa tunniste ilman epävarmaa automaattista yhdistämistä.

    IMDb/TMDB on ensisijainen. Varatunniste käyttää normalisoitua nimeä ja vuotta.
    Jos vuotta tai ulkoista tunnistetta ei ole, havainto pysyy näytöskohtaisena
    tarkistusehdokkaana eikä sitä yhdistetä toiseen samannimiseen elokuvaan.
    """
    identifiers = _external_ids(external_ids)
    for provider in ("imdb", "tmdb"):
        match = next((item for item in identifiers if item["provider"] == provider), None)
        if match:
            return f"{provider}:{match['value']}", "high", False
    normalized = normalize_title(title)
    if release_year is not None:
        if not isinstance(release_year, int) or not 1888 <= release_year <= 2200:
            raise MovieObservationError("Julkaisuvuosi ei ole kelvollinen.")
        return _stable_id("title-year", {"title": normalized, "year": release_year}), "medium", False
    if not screening_id:
        raise MovieObservationError("Ilman ulkoista tunnistetta tai julkaisuvuotta tarvitaan screening_id.")
    return _stable_id("unresolved", {"title": normalized, "screening_id": screening_id}), "low", True


def _normalize_sources(sources: list[dict[str, Any]]) -> list[dict[str, str]]:
    """Säilytä lähteen alkuperäinen vahvistustaso ja poista täsmälliset duplikaatit."""
    found = {}
    for source in sources:
        for key in ("publisher", "url", "checked_at"):
            if not isinstance(source.get(key), str) or not source[key].strip():
                raise MovieObservationError(f"Lähteeltä puuttuu {key}.")
        if not source["url"].startswith(("https://", "http://")):
            raise MovieObservationError("Lähteen URL-osoitteen pitää käyttää HTTP(S)-protokollaa.")
        _timestamp(source["checked_at"])
        level = source.get("claim_level", "unknown")
        if level not in CLAIM_LEVELS:
            raise MovieObservationError(f"Tuntematon lähteen vahvistustaso: {level}")
        item = {key: source[key] for key in ("publisher", "url", "checked_at")}
        item["claim_level"] = level
        key = (item["publisher"], item["url"], item["claim_level"])
        if key not in found or item["checked_at"] > found[key]["checked_at"]:
            found[key] = item
    return [found[key] for key in sorted(found)]


def _criterion_matches(matches: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Yhdistä saman kriteerin toistuvat osumat yhdeksi jäljitettäväksi tietueeksi."""
    found = {}
    for match in matches or []:
        criterion_id = match.get("criterion_id")
        version = match.get("criterion_version")
        matched_at = match.get("matched_at")
        reason = match.get("reason")
        if not isinstance(criterion_id, str) or not criterion_id.strip():
            raise MovieObservationError("Kriteeriosumalta puuttuu criterion_id.")
        if not isinstance(version, str) or not re.fullmatch(r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)", version):
            raise MovieObservationError("Kriteeriosuman criterion_version ei ole semanttinen versio.")
        _timestamp(matched_at)
        if not isinstance(reason, str) or not reason.strip():
            raise MovieObservationError("Kriteeriosuman perustelu puuttuu.")
        urls = sorted(set(match.get("source_urls", [])))
        for url in urls:
            if not isinstance(url, str) or not url.startswith(("https://", "http://")):
                raise MovieObservationError("Kriteeriosuman lähdeviitteen pitää olla HTTP(S)-osoite.")
        match_id = _stable_id("match", {"criterion_id": criterion_id, "criterion_version": version})
        if match_id not in found:
            found[match_id] = {
                "match_id": match_id,
                "criterion_id": criterion_id,
                "criterion_version": version,
                "first_matched_at": matched_at,
                "last_matched_at": matched_at,
                "reasons": [reason],
                "source_urls": urls,
            }
        else:
            item = found[match_id]
            item["first_matched_at"] = min(item["first_matched_at"], matched_at)
            item["last_matched_at"] = max(item["last_matched_at"], matched_at)
            item["reasons"] = sorted(set(item["reasons"]) | {reason})
            item["source_urls"] = sorted(set(item["source_urls"]) | set(urls))
    return [found[key] for key in sorted(found)]

def build_movie_observation(
    screening_event: dict[str, Any], film_metadata: dict[str, Any] | None,
    criterion_matches: list[dict[str, Any]], observed_at: str,
) -> dict[str, Any]:
    """Muodosta elokuvatason tietue yleisen tapahtumavahdin näytöshavainnosta."""
    _timestamp(observed_at)
    screening_id = screening_event.get("canonical_event_id")
    attributes = screening_event.get("attributes")
    if not isinstance(screening_id, str) or not screening_id.strip() or not isinstance(attributes, dict):
        raise MovieObservationError("Näytöshavainto ei sisällä kanonista screening_id-tunnistetta.")
    metadata = film_metadata or {}
    title = metadata.get("primary_title") or attributes.get("title")
    aliases = sorted({item.strip() for item in metadata.get("aliases", []) if isinstance(item, str) and item.strip()})
    screening_title = attributes.get("title")
    if isinstance(screening_title, str) and normalize_title(screening_title) != normalize_title(title):
        aliases.append(screening_title.strip())
    aliases = sorted(set(aliases))
    release_year = metadata.get("release_year")
    external_ids = _external_ids(metadata.get("external_ids"))
    movie_id, confidence, needs_review = identify_movie(title, release_year, external_ids, screening_id)
    sources = _normalize_sources(screening_event.get("sources", []))
    matches = _criterion_matches(criterion_matches)
    return {
        "movie_id": movie_id,
        "primary_title": title,
        "aliases": sorted(set(aliases)),
        "release_year": release_year,
        "external_ids": external_ids,
        "first_seen_at": observed_at,
        "last_seen_at": observed_at,
        "identity_confidence": confidence,
        "needs_review": needs_review,
        "screening_refs": [screening_id],
        "sources": sources,
        "criterion_matches": matches,
    }


def empty_registry() -> dict[str, Any]:
    """Luo tyhjän elokuvahavaintorekisterin."""
    return {"schema_version": 1, "films": []}


def validate_registry(registry: dict[str, Any]) -> None:
    """Tarkista rekisterin skeema ja elokuvakohtainen eheys."""
    schema = json.loads(REGISTRY_SCHEMA.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(schema)
    errors = sorted(
        jsonschema.Draft202012Validator(
            schema, format_checker=jsonschema.FormatChecker()
        ).iter_errors(registry),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        first = errors[0]
        raise MovieObservationError(f"Elokuvarekisterin virhe kohdassa {list(first.absolute_path)}: {first.message}")
    movie_ids = [film["movie_id"] for film in registry["films"]]
    if len(movie_ids) != len(set(movie_ids)):
        raise MovieObservationError("Elokuvarekisterissä on duplikaatti movie_id.")
    for film in registry["films"]:
        if _timestamp(film["first_seen_at"]) > _timestamp(film["last_seen_at"]):
            raise MovieObservationError("Elokuvan ensihavainto on viimeisintä havaintoa myöhempi.")
        providers = [item["provider"] for item in film["external_ids"]]
        if len(providers) != len(set(providers)):
            raise MovieObservationError("Elokuvalla on saman palvelun ulkoinen tunniste kahdesti.")


def merge_movie_observation(
    registry: dict[str, Any], observation: dict[str, Any]
) -> dict[str, Any]:
    """Lisää tai päivitä elokuvan kooste säilyttäen aiemmat kriteeriosumat ja viitteet."""
    validate_registry(registry)
    result = deepcopy(registry)
    existing = next((item for item in result["films"] if item["movie_id"] == observation["movie_id"]), None)
    if existing is None:
        result["films"].append(deepcopy(observation))
    else:
        old_external = {item["provider"]: item["value"] for item in existing["external_ids"]}
        new_external = {item["provider"]: item["value"] for item in observation["external_ids"]}
        for provider, value in new_external.items():
            if provider in old_external and old_external[provider] != value:
                raise MovieObservationError(f"Elokuvan {provider}-tunniste muuttui ristiriitaisesti.")
        existing["aliases"] = sorted(set(existing["aliases"]) | set(observation["aliases"]))
        if normalize_title(existing["primary_title"]) != normalize_title(observation["primary_title"]):
            existing["aliases"] = sorted(set(existing["aliases"]) | {observation["primary_title"]})
        existing["external_ids"] = _external_ids(
            [{"provider": key, "value": value} for key, value in (old_external | new_external).items()]
        )
        if existing["release_year"] is None:
            existing["release_year"] = observation["release_year"]
        elif observation["release_year"] is not None and existing["release_year"] != observation["release_year"]:
            existing["needs_review"] = True
        existing["first_seen_at"] = min(existing["first_seen_at"], observation["first_seen_at"])
        existing["last_seen_at"] = max(existing["last_seen_at"], observation["last_seen_at"])
        existing["identity_confidence"] = max(
            (existing["identity_confidence"], observation["identity_confidence"]),
            key=lambda value: {"low": 0, "medium": 1, "high": 2}[value],
        )
        existing["needs_review"] = existing["needs_review"] or observation["needs_review"]
        existing["screening_refs"] = sorted(set(existing["screening_refs"]) | set(observation["screening_refs"]))
        existing["sources"] = _normalize_sources(existing["sources"] + observation["sources"])
        matches = {item["match_id"]: item for item in existing["criterion_matches"]}
        matches.update({item["match_id"]: item for item in observation["criterion_matches"]})
        existing["criterion_matches"] = [matches[key] for key in sorted(matches)]
    result["films"].sort(key=lambda item: item["movie_id"])
    validate_registry(result)
    return result


def reconcile_movie_observations(
    registry: dict[str, Any], observations: list[dict[str, Any]]
) -> dict[str, Any]:
    """Yhdistä yhden näytösvahtiajon elokuvakoosteet deterministisessä järjestyksessä."""
    result = deepcopy(registry)
    for observation in sorted(observations, key=lambda item: (item["movie_id"], item["screening_refs"][0])):
        result = merge_movie_observation(result, observation)
    return result


class JsonFileMovieRegistryStore:
    """Paikallinen SHA-tarkistettu rekisteritallennus; testit käyttävät väliaikaistiedostoja."""

    def __init__(self, path: Path):
        self.path = Path(path).resolve()

    def load(self) -> tuple[dict[str, Any], str]:
        """Lue ja validoi rekisteri tai palauta tyhjä rekisteri."""
        try:
            content = self.path.read_bytes()
        except FileNotFoundError:
            return empty_registry(), "missing"
        try:
            registry = json.loads(content.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise MovieObservationError("Elokuvarekisterin JSON on virheellinen.") from exc
        validate_registry(registry)
        return registry, _sha(content)

    def save(self, registry: dict[str, Any], *, expected_sha: str) -> str:
        """Tallenna rekisteri vain odotettua SHA-versiota vasten."""
        validate_registry(registry)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        lock_path = self.path.with_name(self.path.name + ".lock")
        with lock_path.open("a+b") as lock:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
            try:
                try:
                    current = _sha(self.path.read_bytes())
                except FileNotFoundError:
                    current = "missing"
                if current != expected_sha:
                    raise MovieRegistryConflictError("Elokuvarekisteri muuttui ennen tallennusta.")
                content = _canonical(registry) + b"\n"
                temporary = None
                try:
                    with tempfile.NamedTemporaryFile(
                        mode="wb", dir=self.path.parent, prefix=f".{self.path.name}.",
                        suffix=".tmp", delete=False
                    ) as stream:
                        temporary = Path(stream.name)
                        stream.write(content)
                        stream.flush()
                        os.fsync(stream.fileno())
                    os.replace(temporary, self.path)
                finally:
                    if temporary is not None and temporary.exists():
                        temporary.unlink()
                return _sha(content)
            finally:
                fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
