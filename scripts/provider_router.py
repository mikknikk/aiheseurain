"""Tekninen reititin moduulien AI- ja tutkimuspalveluille."""
from __future__ import annotations
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import time
from typing import Any, Callable
from urllib.parse import urlparse
import jsonschema

from scripts.provider_contracts import (
    AIProcessor, AIRequest, AIResult, CostBudget, ProviderCallRecord,
    ProviderContractError, ProviderError, ProviderRateLimitError,
    ProviderTimeoutError, ProviderUnavailableError, ProviderAuthenticationError,
    ProviderCostLimitError, ResearchProvider, ResearchQuery, ResearchResult,
    ResearchSource, RetryPolicy, call_with_retry,
)

ROOT = Path(__file__).resolve().parents[1]


def _validate_datetime(value: str, field: str) -> None:
    """Varmista, että lähdeaikaleima sisältää myös aikavyöhykkeen."""
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, TypeError, ValueError) as exc:
        raise ProviderContractError(f"Lähteen {field} ei ole kelvollinen ISO 8601 -aikaleima.") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ProviderContractError(f"Lähteen {field} puuttuu aikavyöhyke.")


ROUTING_SCHEMA = ROOT / "schemas/provider-routing.schema.json"
ROUTING_CONFIG = ROOT / "data/provider-routing.json"


def validate_provider_config(config: dict[str, Any]) -> None:
    """Validoi palvelureitityksen rakenne ja salaisuuksien viittaustapa."""
    schema = json.loads(ROUTING_SCHEMA.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(schema)
    validator = jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker())
    errors = sorted(validator.iter_errors(config), key=lambda item: list(item.path))
    if errors:
        first = errors[0]
        raise ProviderContractError(f"Palvelureitityksen virhe kohdassa {list(first.path)}: {first.message}")
    ids = [item["provider_id"] for item in config["providers"]]
    if len(ids) != len(set(ids)):
        raise ProviderContractError("Palvelurekisterissä on duplikaatti provider_id.")
    known = {item["provider_id"]: item for item in config["providers"]}
    for module_id, route in config["routes"].items():
        _validate_route(module_id, route, known)
    if config["default_route"] is not None:
        _validate_route("default", config["default_route"], known)


def _validate_route(module_id: str, route: dict[str, Any], known: dict[str, dict[str, Any]]) -> None:
    for field, expected_type in (("ai_processor", "ai_processor"), ("research_provider", "research_provider")):
        provider_id = route[field]
        if provider_id is None:
            continue
        provider = known.get(provider_id)
        if provider is None:
            raise ProviderContractError(f"{module_id}: reitti viittaa tuntemattomaan palveluun {provider_id}.")
        if provider["provider_type"] != expected_type or not provider["enabled"]:
            raise ProviderContractError(f"{module_id}: palvelu {provider_id} ei ole käytettävissä tyypissä {expected_type}.")


def load_provider_config(path: Path = ROUTING_CONFIG) -> dict[str, Any]:
    """Lue ja validoi tekninen reitityskonfiguraatio."""
    config = json.loads(path.read_text(encoding="utf-8"))
    validate_provider_config(config)
    return config


class ProviderRouter:
    """Valitsee moduulille teknisen palvelun muuttamatta moduulimääritystä."""

    def __init__(
        self, config: dict[str, Any], *,
        ai_processors: list[AIProcessor], research_providers: list[ResearchProvider],
        sleep_fn: Callable[[float], None] = time.sleep,
    ):
        validate_provider_config(config)
        self.config = config
        self.ai_processors = {item.provider_id: item for item in ai_processors}
        self.research_providers = {item.provider_id: item for item in research_providers}
        if len(self.ai_processors) != len(ai_processors) or len(self.research_providers) != len(research_providers):
            raise ProviderContractError("Adapterrekisterissä on duplikaatti provider_id.")
        self.sleep_fn = sleep_fn
        self.audit_records: list[ProviderCallRecord] = []
        self._provider_configs = {item["provider_id"]: item for item in config["providers"]}
        for item in config["providers"]:
            if not item["enabled"]:
                continue
            adapters = self.ai_processors if item["provider_type"] == "ai_processor" else self.research_providers
            adapter = adapters.get(item["provider_id"])
            if adapter is None:
                raise ProviderContractError(f"Aktiiviselle palvelulle {item['provider_id']} ei ole rekisteröity adapteria.")
            if getattr(adapter, "adapter_id", None) != item["adapter_id"]:
                raise ProviderContractError(f"Palvelun {item['provider_id']} adapter_id ei vastaa rekisteröityä toteutusta.")

    def _resolve(self, module_id: str, provider_type: str, required: tuple[str, ...]):
        if provider_type not in {"ai_processor", "research_provider"}:
            raise ProviderContractError(f"Tuntematon palvelutyyppi: {provider_type}.")
        route = self.config["routes"].get(module_id, self.config["default_route"])
        if route is None:
            raise ProviderUnavailableError(f"Moduulille {module_id} ei ole määritelty palvelureittiä.")
        field = "ai_processor" if provider_type == "ai_processor" else "research_provider"
        provider_id = route[field]
        if provider_id is None:
            raise ProviderUnavailableError(f"Moduulille {module_id} ei ole määritelty palvelua {provider_type}.")
        config = self._provider_configs[provider_id]
        adapters = self.ai_processors if provider_type == "ai_processor" else self.research_providers
        adapter = adapters.get(provider_id)
        if adapter is None:
            raise ProviderUnavailableError(f"Palvelun {provider_id} adapteria ei ole rekisteröity tähän suoritusympäristöön.")
        if getattr(adapter, "adapter_id", None) != config["adapter_id"]:
            raise ProviderContractError(f"Palvelun {provider_id} adapteritunniste ei vastaa konfiguraatiota.")
        declared = set(config["capabilities"])
        actual = set(adapter.capabilities)
        if not set(required).issubset(declared) or not set(required).issubset(actual):
            raise ProviderContractError(f"Palvelu {provider_id} ei täytä moduulin vaatimia kyvykkyyksiä.")
        return config, adapter

    def budget_for(self, module_id: str, provider_type: str) -> CostBudget:
        """Luo palvelun teknisen per-ajon kustannusrajan mukaisen budjetin."""
        if provider_type not in {"ai_processor", "research_provider"}:
            raise ProviderContractError(f"Tuntematon palvelutyyppi: {provider_type}.")
        route = self.config["routes"].get(module_id, self.config["default_route"])
        if route is None:
            raise ProviderUnavailableError(f"Moduulille {module_id} ei ole määritelty palvelureittiä.")
        field = "ai_processor" if provider_type == "ai_processor" else "research_provider"
        provider_id = route[field]
        if provider_id is None:
            raise ProviderUnavailableError(f"Moduulille {module_id} ei ole määritelty palvelua {provider_type}.")
        limit = self._provider_configs[provider_id]["cost_limit"]["per_run"]
        return CostBudget(max_cost=limit)

    def _invoke(
        self, *, module_id: str, run_id: str, provider_type: str, provider_config: dict[str, Any],
        adapter: Any, operation: Callable[[], Any], estimate: float, budget: CostBudget,
        validator: Callable[[Any], None],
    ):
        attempts = 0
        started = time.monotonic()
        try:
            budget.ensure(estimate)
            policy_data = provider_config["retry_policy"]
            policy = RetryPolicy(**policy_data)

            def counted_operation():
                nonlocal attempts
                attempts += 1
                return operation()

            result = call_with_retry(counted_operation, policy, self.sleep_fn)
            validator(result)
            actual_cost = result.estimated_cost
            budget.charge(actual_cost)
            self.audit_records.append(ProviderCallRecord(
                module_id=module_id, run_id=run_id, provider_id=provider_config["provider_id"],
                provider_type=provider_type, status="succeeded", attempts=attempts,
                estimated_cost=actual_cost
            ))
            return result
        except Exception as exc:
            error_code = getattr(exc, "code", type(exc).__name__)
            self.audit_records.append(ProviderCallRecord(
                module_id=module_id, run_id=run_id, provider_id=provider_config["provider_id"],
                provider_type=provider_type, status="failed", attempts=attempts,
                estimated_cost=estimate, error_code=error_code
            ))
            raise

    def process_ai(self, request: AIRequest, *, budget: CostBudget) -> AIResult:
        """Käsittele pyyntö valitulla AI-adapterilla ja varmista lähdeviitteiden säilyminen."""
        if request.contract_version != "1.0.0" or not request.module_id or not request.run_id or not request.content.strip():
            raise ProviderContractError("AI-pyynnön sopimusversio tai sisältö on virheellinen.")
        config, adapter = self._resolve(request.module_id, "ai_processor", request.required_capabilities)
        estimate = adapter.estimate_cost(request)
        if not math.isfinite(estimate) or estimate < 0:
            raise ProviderContractError("AI-adapterin kustannusarvio on virheellinen.")

        def validate(result):
            if not isinstance(result, AIResult) or result.contract_version != "1.0.0":
                raise ProviderContractError("AI-adapteri palautti tuntemattoman vastaussopimuksen.")
            if not result.content or result.uncertainty not in {"low", "medium", "high", "unknown"}:
                raise ProviderContractError("AI-adapterin sisältö tai epävarmuusluokka on virheellinen.")
            if not set(request.source_refs).issubset(set(result.source_refs)):
                raise ProviderContractError("AI-adapteri kadotti pyynnön lähdeviitteitä.")
            if not math.isfinite(result.estimated_cost) or result.estimated_cost < 0:
                raise ProviderContractError("AI-adapterin kustannusarvio on virheellinen.")

        return self._invoke(
            module_id=request.module_id, run_id=request.run_id, provider_type="ai_processor",
            provider_config=config, adapter=adapter,
            operation=lambda: adapter.process(request, timeout_seconds=config["timeout_seconds"]),
            estimate=estimate, budget=budget, validator=validate
        )

    def search(self, query: ResearchQuery, *, budget: CostBudget) -> ResearchResult:
        """Hae lähteitä ja säilytä alkuperäiset lähdetunnisteet sekä epävarmuus."""
        if query.contract_version != "1.0.0" or not query.module_id or not query.run_id or not query.query_terms or query.max_results < 1:
            raise ProviderContractError("Tutkimuspyynnön sopimusversio, hakutermit tai tulosraja on virheellinen.")
        config, adapter = self._resolve(query.module_id, "research_provider", query.required_capabilities)
        estimate = adapter.estimate_search_cost(query)
        if not math.isfinite(estimate) or estimate < 0:
            raise ProviderContractError("Tutkimusadapterin kustannusarvio on virheellinen.")

        def validate(result):
            if not isinstance(result, ResearchResult) or result.contract_version != "1.0.0":
                raise ProviderContractError("Tutkimusadapteri palautti tuntemattoman vastaussopimuksen.")
            if len(result.sources) > query.max_results or not math.isfinite(result.estimated_cost) or result.estimated_cost < 0:
                raise ProviderContractError("Tutkimustuloksen määrä tai kustannusarvio on virheellinen.")
            if result.complete and result.failed_source_ids:
                raise ProviderContractError("Täydellisessä tutkimustuloksessa ei voi olla epäonnistuneita lähteitä.")
            if not result.complete and not result.failed_source_ids:
                raise ProviderContractError("Osittaisessa tutkimustuloksessa pitää nimetä epäonnistuneet lähteet.")
            source_ids = [source.source_id for source in result.sources]
            if len(source_ids) != len(set(source_ids)):
                raise ProviderContractError("Tutkimustulos sisältää saman lähteen useammin kuin kerran.")
            allowed = set(query.allowed_source_ids)
            for source in result.sources:
                if allowed and source.source_id not in allowed:
                    raise ProviderContractError(f"Tutkimusadapteri palautti rekisteröimättömän lähteen {source.source_id}.")
                if urlparse(source.url).scheme not in {"http", "https"} or not urlparse(source.url).netloc or not source.title:
                    raise ProviderContractError("Tutkimustuloksen lähdeviite tai URL ei ole kelvollinen.")
                if source.reliability_class not in {"A", "B", "C", "D"}:
                    raise ProviderContractError("Lähteen luotettavuusluokka ei ole A–D.")
                if source.claim_level not in {"officially_confirmed", "media_reported", "unconfirmed_rumor", "unknown"}:
                    raise ProviderContractError("Lähteen väitteen vahvistustaso on virheellinen.")
                _validate_datetime(source.checked_at, "checked_at")
                if source.published_at is not None:
                    _validate_datetime(source.published_at, "published_at")

        return self._invoke(
            module_id=query.module_id, run_id=query.run_id, provider_type="research_provider",
            provider_config=config, adapter=adapter,
            operation=lambda: adapter.search(query, timeout_seconds=config["timeout_seconds"]),
            estimate=estimate, budget=budget, validator=validate
        )

    def open_source(self, *, module_id: str, run_id: str, source_id: str, budget: CostBudget) -> ResearchSource:
        """Avaa lähde tunnisteellä; adapteri ei saa vaihtaa pyydettyä lähdettä."""
        required = ("research.open_source", "source.provenance")
        if not source_id:
            raise ProviderContractError("Lähteen tunniste puuttuu.")
        config, adapter = self._resolve(module_id, "research_provider", required)
        estimate = adapter.estimate_open_cost(source_id)
        if not math.isfinite(estimate) or estimate < 0:
            raise ProviderContractError("Lähteen avaamisen kustannusarvio on virheellinen.")

        def validate(source):
            if not isinstance(source, ResearchSource) or source.source_id != source_id:
                raise ProviderContractError("Avausadapteri palautti eri lähteen kuin pyydettiin.")
            if urlparse(source.url).scheme not in {"http", "https"} or not urlparse(source.url).netloc:
                raise ProviderContractError("Avatun lähteen URL ei ole kelvollinen.")
            if source.reliability_class not in {"A", "B", "C", "D"} or source.claim_level not in {"officially_confirmed", "media_reported", "unconfirmed_rumor", "unknown"}:
                raise ProviderContractError("Avatun lähteen luotettavuus- tai vahvistusluokka on virheellinen.")
            _validate_datetime(source.checked_at, "checked_at")
            if source.published_at is not None:
                _validate_datetime(source.published_at, "published_at")

        return self._invoke(
            module_id=module_id, run_id=run_id, provider_type="research_provider",
            provider_config=config, adapter=adapter,
            operation=lambda: adapter.open_source(source_id, timeout_seconds=config["timeout_seconds"]),
            estimate=estimate, budget=budget, validator=validate
        )
