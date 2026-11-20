"""Lue, validoi ja eristä Aiheseuraimen seurantamoduulirekisterin määritykset.

Rekisteri sisältää vain tekniset viitteet moduuleihin. Tämä lataaja ei käynnistä
moduuleja, ajastuksia tai ulkoisia palveluja. Yhden moduulin virhe kirjataan
kyseisen moduulin tulokseen eikä estä muiden riippumattomien moduulien lataamista.
Prosessilaajennusten skeemat etsitään vain tästä repositoriosta; verkosta ei ladata
skeemoja eikä niiden osoitteita käsitellä suoritettavana koodina.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "data/module-registry.json"
REGISTRY_SCHEMA_PATH = ROOT / "schemas/seurantamoduulirekisteri.schema.json"
MODULE_SCHEMA_PATH = ROOT / "schemas/seurantamoduuli.schema.json"
SUPPORTED_REGISTRY_VERSION = "1.0.0"
SUPPORTED_CONTRACT_VERSION = "1.0.0"


class RegistryError(ValueError):
    """Virhe, joka estää koko rekisterin luotettavan tulkinnan."""


@dataclass(frozen=True)
class ModuleResult:
    """Yhden rekisterimerkinnän latauksen tulos."""

    module_id: str
    status: str
    path: str | None = None
    definition: dict[str, Any] | None = None
    error: str | None = None


@dataclass(frozen=True)
class RegistryResult:
    """Deterministinen yhteenveto moduulirekisterin käsittelystä."""

    modules: tuple[ModuleResult, ...]

    @property
    def active_modules(self) -> dict[str, dict[str, Any]]:
        """Palauta vain onnistuneesti validoidut aktiiviset määritykset."""
        return {
            item.module_id: item.definition
            for item in self.modules
            if item.status == "active" and item.definition is not None
        }

    @property
    def invalid_modules(self) -> tuple[ModuleResult, ...]:
        """Palauta virheelliset merkinnät deterministisessä järjestyksessä."""
        return tuple(item for item in self.modules if item.status == "invalid")


def _read_json(path: Path) -> dict[str, Any]:
    """Lue JSON-objekti ja anna ymmärrettävä virhe, jos tiedosto ei kelpaa."""
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RegistryError(f"Tiedostoa {path} ei voi lukea kelvollisena JSONina: {exc}") from exc
    if not isinstance(value, dict):
        raise RegistryError(f"Tiedoston {path} ylimmän tason arvon pitää olla JSON-objekti.")
    return value


def _schema_validator(schema_path: Path) -> jsonschema.Draft202012Validator:
    """Lataa ja tarkista paikallinen Draft 2020-12 -skeema."""
    schema = _read_json(schema_path)
    jsonschema.Draft202012Validator.check_schema(schema)
    return jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker())


def _safe_definition_path(root: Path, relative_path: str) -> Path:
    """Ratkaise vain repositorion sisäinen suhteellinen moduulipolku."""
    candidate = Path(relative_path)
    if candidate.is_absolute():
        raise ValueError("Määrityksen polku ei saa olla absoluuttinen.")
    resolved_root = root.resolve()
    resolved_path = (resolved_root / candidate).resolve()
    if not resolved_path.is_relative_to(resolved_root):
        raise ValueError("Määrityksen polku poistuu repositorion juuresta.")
    if not resolved_path.is_file():
        raise ValueError(f"Määritystiedostoa ei löydy: {relative_path}")
    return resolved_path


def _extension_schemas(root: Path) -> tuple[dict[str, tuple[dict[str, Any], Path]], dict[str, str]]:
    """Indeksoi paikalliset laajennusskeemat niiden $id-osoitteilla."""
    schemas: dict[str, tuple[dict[str, Any], Path]] = {}
    errors: dict[str, str] = {}
    extension_dir = root / "schemas/module-extensions"
    if not extension_dir.is_dir():
        return schemas, errors

    for path in sorted(extension_dir.rglob("*.json")):
        try:
            schema = _read_json(path)
            jsonschema.Draft202012Validator.check_schema(schema)
            schema_id = schema.get("$id")
            if not isinstance(schema_id, str) or not schema_id:
                raise ValueError("Laajennusskeemalta puuttuu $id.")
            if schema_id in schemas:
                # Kahdella tiedostolla ei saa olla samaa tunnistetta: poista
                # epäselvä viite kokonaan, jotta kumpaakaan ei valita sattumalta.
                schemas.pop(schema_id, None)
                errors[schema_id] = f"Laajennusskeeman $id esiintyy useassa tiedostossa: {schema_id}"
                continue
            if schema_id in errors:
                continue
            schemas[schema_id] = (schema, path)
        except (RegistryError, jsonschema.SchemaError, ValueError) as exc:
            errors[str(path.relative_to(root))] = str(exc)
    return schemas, errors


def _validate_definition(
    definition: dict[str, Any],
    entry: dict[str, Any],
    module_validator: jsonschema.Draft202012Validator,
    extension_schemas: dict[str, tuple[dict[str, Any], Path]],
    extension_errors: dict[str, str],
) -> None:
    """Tarkista yhteinen sopimus, rekisteriviitteen eheys ja mahdollinen laajennus."""
    errors = sorted(module_validator.iter_errors(definition), key=lambda error: list(error.path))
    if errors:
        first = errors[0]
        location = ".".join(str(part) for part in first.path) or "<juuri>"
        raise ValueError(f"Moduulimääritys ei täytä tietosopimusta kohdassa {location}: {first.message}")

    for field in ("module_id", "module_type", "definition_version"):
        if definition.get(field) != entry.get(field):
            raise ValueError(
                f"Rekisterin {field} ({entry.get(field)!r}) ei vastaa "
                f"määrityksen arvoa ({definition.get(field)!r})."
            )

    if definition.get("contract_version") != SUPPORTED_CONTRACT_VERSION:
        raise ValueError(
            f"Tuntematon tietosopimusversio: {definition.get('contract_version')!r}."
        )

    if definition.get("module_type") != "process":
        return

    extension = definition["process_extension"]
    schema_uri = extension["schema_uri"]
    if schema_uri in extension_errors:
        raise ValueError(f"Laajennusskeema ei ole kelvollinen: {extension_errors[schema_uri]}")
    schema_record = extension_schemas.get(schema_uri)
    if schema_record is None:
        raise ValueError(
            f"Laajennusskeemaa ei löydy paikallisesta rekisteristä: {schema_uri}. "
            "Ulkopuolisia skeemoja ei ladata verkosta."
        )

    schema, schema_path = schema_record
    if schema.get("x-extension-id") != extension["extension_id"]:
        raise ValueError(f"Laajennuksen tunniste ei vastaa skeemaa: {schema_path.relative_to(ROOT)}")
    if schema.get("x-extension-version") != extension["extension_version"]:
        raise ValueError(f"Laajennuksen versio ei vastaa skeemaa: {schema_path.relative_to(ROOT)}")

    extension_validator = jsonschema.Draft202012Validator(
        schema, format_checker=jsonschema.FormatChecker()
    )
    extension_errors_found = sorted(
        extension_validator.iter_errors(extension["configuration"]),
        key=lambda error: list(error.path),
    )
    if extension_errors_found:
        first = extension_errors_found[0]
        location = ".".join(str(part) for part in first.path) or "<juuri>"
        raise ValueError(
            f"Prosessilaajennus ei täytä omaa skeemaansa kohdassa {location}: {first.message}"
        )


def load_registry(
    registry_path: Path = REGISTRY_PATH,
    root: Path = ROOT,
    *,
    include_inactive: bool = False,
) -> RegistryResult:
    """Lataa rekisterin moduulit ja eristää yksittäisten merkintöjen virheet.

    Oletuksena passiivisten moduulien määritystiedostoja ei ladata. Varjotila voi
    pyytää include_inactive=True, jolloin passiivisetkin määritykset validoidaan
    ja palautetaan definition-kentässä, mutta niiden status säilyy inactive.
    """

    root = root.resolve()
    registry_path = registry_path.resolve()
    if not registry_path.is_relative_to(root):
        raise RegistryError("Rekisteritiedoston pitää sijaita repositorion sisällä.")

    registry = _read_json(registry_path)
    registry_schema = _read_json(REGISTRY_SCHEMA_PATH if root == ROOT else root / "schemas/seurantamoduulirekisteri.schema.json")
    jsonschema.Draft202012Validator.check_schema(registry_schema)
    registry_validator = jsonschema.Draft202012Validator(
        registry_schema, format_checker=jsonschema.FormatChecker()
    )

    # Rekisterin ylätason virhe estää merkintöjen luotettavan tulkinnan.
    top_level = dict(registry)
    top_level["modules"] = []
    top_errors = sorted(
        registry_validator.iter_errors(top_level),
        key=lambda error: list(error.path),
    )
    if top_errors:
        raise RegistryError(f"Rekisterin ylätason rakenne on virheellinen: {top_errors[0].message}")
    if not isinstance(registry.get("modules"), list):
        raise RegistryError("Rekisterin modules-kentän pitää olla taulukko.")

    extension_schemas, extension_errors = _extension_schemas(root)
    module_validator = _schema_validator(root / "schemas/seurantamoduuli.schema.json")

    entries = registry["modules"]
    id_counts: dict[str, int] = {}
    for entry in entries:
        if isinstance(entry, dict) and isinstance(entry.get("module_id"), str):
            id_counts[entry["module_id"]] = id_counts.get(entry["module_id"], 0) + 1

    results: list[ModuleResult] = []
    seen_paths: set[str] = set()
    for entry in entries:
        module_id = entry.get("module_id", "<tuntematon>") if isinstance(entry, dict) else "<virheellinen>"
        # Validoi yksittäinen merkintä koko skeemakontekstissa, jotta myös
        # yhteisiin $defs-määritelmiin osoittavat viittaukset ratkeavat oikein.
        single_entry_registry = dict(top_level)
        single_entry_registry["modules"] = [entry]
        entry_errors = sorted(
            registry_validator.iter_errors(single_entry_registry),
            key=lambda error: list(error.path),
        )
        entry_errors = [
            error for error in entry_errors
            if error.path and error.path[0] == "modules"
        ]
        if entry_errors:
            results.append(ModuleResult(str(module_id), "invalid", error=entry_errors[0].message))
            continue

        if id_counts.get(module_id, 0) > 1:
            results.append(ModuleResult(module_id, "invalid", entry["path"], error="Moduulitunniste esiintyy rekisterissä useammin kuin kerran."))
            continue

        if entry["path"] in seen_paths:
            results.append(ModuleResult(module_id, "invalid", entry["path"], error="Samaa määrityspolkua käytetään useassa rekisterimerkinnässä."))
            continue
        seen_paths.add(entry["path"])

        if entry["status"] == "inactive" and not include_inactive:
            results.append(ModuleResult(module_id, "inactive", entry["path"]))
            continue

        try:
            if registry.get("registry_version") != SUPPORTED_REGISTRY_VERSION:
                raise ValueError(f"Tuntematon rekisteriversio: {registry.get('registry_version')!r}.")
            if registry.get("contract_version") != SUPPORTED_CONTRACT_VERSION:
                raise ValueError(f"Tuntematon rekisterin tietosopimusversio: {registry.get('contract_version')!r}.")
            definition_path = _safe_definition_path(root, entry["path"])
            definition = _read_json(definition_path)
            _validate_definition(
                definition, entry, module_validator, extension_schemas, extension_errors
            )
            results.append(ModuleResult(module_id, entry["status"], entry["path"], definition))
        except (RegistryError, ValueError, KeyError, jsonschema.SchemaError) as exc:
            results.append(ModuleResult(module_id, "invalid", entry["path"], error=str(exc)))

    results.sort(key=lambda item: (item.module_id, item.path or "", item.status))
    return RegistryResult(tuple(results))
