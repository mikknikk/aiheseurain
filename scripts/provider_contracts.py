"""Versioidut sopimukset tekoäly- ja tutkimuspalvelujen adaptereille.

Sopimukset eivät sido aihemoduuleja tiettyyn palveluntarjoajaan. Pyynnöt voivat
sisältää toimituksellista aineistoa, joten niitä tai tunnuksia ei kirjoiteta
auditointilokiin.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable, Protocol


CONTRACT_VERSION = "1.0.0"


@dataclass(frozen=True)
class AIRequest:
    """Tekoälyadapterille annettava käsittelypyyntö."""
    module_id: str
    run_id: str
    content: str
    source_refs: tuple[str, ...] = ()
    output_language: str = "fi"
    required_capabilities: tuple[str, ...] = ("ai.generate", "source.traceability", "uncertainty")
    metadata: dict[str, Any] = field(default_factory=dict)
    contract_version: str = CONTRACT_VERSION


@dataclass(frozen=True)
class AIResult:
    """Tekoälyadapterin normalisoitu vastaus."""
    content: str
    source_refs: tuple[str, ...]
    uncertainty: str
    estimated_cost: float = 0.0
    notes: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)
    contract_version: str = CONTRACT_VERSION


@dataclass(frozen=True)
class ResearchQuery:
    """Tutkimusadapterille annettava hakupyyntö."""
    module_id: str
    run_id: str
    query_terms: tuple[str, ...]
    languages: tuple[str, ...] = ()
    regions: tuple[str, ...] = ()
    allowed_source_ids: tuple[str, ...] = ()
    max_results: int = 20
    required_capabilities: tuple[str, ...] = ("research.search", "source.provenance")
    contract_version: str = CONTRACT_VERSION


@dataclass(frozen=True)
class ResearchSource:
    """Yhden löydetyn lähteen normalisoidut tiedot."""
    source_id: str
    url: str
    title: str
    snippet: str
    language: str
    region: str
    reliability_class: str
    claim_level: str
    checked_at: str
    published_at: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ResearchResult:
    """Tutkimushaun tulos ja sen kattavuustieto."""
    sources: tuple[ResearchSource, ...]
    complete: bool
    failed_source_ids: tuple[str, ...] = ()
    estimated_cost: float = 0.0
    contract_version: str = CONTRACT_VERSION


class ProviderError(RuntimeError):
    """Palveluntarjoajan yleinen virhe."""
    code = "provider_error"
    retryable = False


class ProviderTimeoutError(ProviderError):
    """Palveluntarjoaja ei vastannut määräajassa."""
    code = "timeout"
    retryable = True


class ProviderUnavailableError(ProviderError):
    """Palvelu ei ole tilapäisesti käytettävissä."""
    code = "unavailable"
    retryable = True


class ProviderRateLimitError(ProviderError):
    """Palvelun pyyntökiintiö täyttyi."""
    code = "rate_limited"
    retryable = True

    def __init__(self, message: str = "Rate limit", retry_after_seconds: float = 0.0):
        super().__init__(message)
        self.retry_after_seconds = max(0.0, retry_after_seconds)


class ProviderAuthenticationError(ProviderError):
    """Tunnistautuminen epäonnistui; automaattista uusintaa ei tehdä."""
    code = "authentication"
    retryable = False


class ProviderContractError(ProviderError):
    """Adapteri rikkoi yhteistä tietosopimusta."""
    code = "contract_violation"
    retryable = False


class ProviderCostLimitError(ProviderError):
    """Ajon kustannusraja ylittyisi."""
    code = "cost_limit"
    retryable = False


@dataclass(frozen=True)
class RetryPolicy:
    """Rajattu uusintakäytäntö tilapäisille palveluvirheille."""
    max_attempts: int = 2
    base_delay_seconds: float = 0.25
    max_delay_seconds: float = 2.0

    def __post_init__(self):
        if not 1 <= self.max_attempts <= 5:
            raise ValueError("max_attempts pitää olla välillä 1–5.")
        if self.base_delay_seconds < 0 or self.max_delay_seconds < 0:
            raise ValueError("Uusintaviive ei voi olla negatiivinen.")


@dataclass
class CostBudget:
    """Yhden moduuliajon yhteinen kustannusraja."""
    max_cost: float | None
    spent: float = 0.0

    def ensure(self, estimate: float) -> None:
        if estimate < 0:
            raise ProviderContractError("Kustannusarvio ei voi olla negatiivinen.")
        if self.max_cost is not None and self.spent + estimate > self.max_cost:
            raise ProviderCostLimitError("Ajon kustannusraja ylittyisi.")

    def charge(self, actual: float) -> None:
        if actual < 0:
            raise ProviderContractError("Toteutunut kustannus ei voi olla negatiivinen.")
        if self.max_cost is not None and self.spent + actual > self.max_cost:
            raise ProviderCostLimitError("Palvelun ilmoittama kustannus ylitti ajon kustannusrajan.")
        self.spent += actual


@dataclass(frozen=True)
class ProviderCallRecord:
    """Tietoturvallinen auditointimerkintä ilman pyyntötekstiä tai tunnuksia."""
    module_id: str
    run_id: str
    provider_id: str
    provider_type: str
    status: str
    attempts: int
    estimated_cost: float
    error_code: str | None = None


class AIProcessor(Protocol):
    """Vaihdettavan tekoälykäsittelijän sopimus."""
    provider_id: str
    capabilities: frozenset[str]

    def estimate_cost(self, request: AIRequest) -> float: ...
    def process(self, request: AIRequest, *, timeout_seconds: float) -> AIResult: ...


class ResearchProvider(Protocol):
    """Vaihdettavan tutkimus- ja lähdehaun sopimus."""
    provider_id: str
    capabilities: frozenset[str]

    def estimate_search_cost(self, query: ResearchQuery) -> float: ...
    def search(self, query: ResearchQuery, *, timeout_seconds: float) -> ResearchResult: ...
    def estimate_open_cost(self, source_id: str) -> float: ...
    def open_source(self, source_id: str, *, timeout_seconds: float) -> ResearchSource: ...


def call_with_retry(
    operation: Callable[[], Any], policy: RetryPolicy,
    sleep_fn: Callable[[float], None],
) -> Any:
    """Uusi vain timeout-, saatavuus- ja rate limit -virheitä rajatusti."""
    attempt = 0
    while True:
        attempt += 1
        try:
            return operation()
        except ProviderRateLimitError as exc:
            if attempt >= policy.max_attempts or exc.retry_after_seconds > policy.max_delay_seconds:
                raise
            delay = max(policy.base_delay_seconds * (2 ** (attempt - 1)), exc.retry_after_seconds)
            sleep_fn(min(delay, policy.max_delay_seconds))
        except (ProviderTimeoutError, ProviderUnavailableError):
            if attempt >= policy.max_attempts:
                raise
            delay = min(policy.base_delay_seconds * (2 ** (attempt - 1)), policy.max_delay_seconds)
            sleep_fn(delay)
