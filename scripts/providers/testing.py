"""Deterministiset testiadapterit palvelusopimusten ja reitityksen testaamiseen.

Nämä eivät ole tuotantopalveluja eivätkä käytä verkkoa tai tunnuksia. Ne palauttavat
kiinteitä testiaineistoja, joilla voidaan varmistaa adapterien vaihdettavuus.
"""
from __future__ import annotations

from scripts.provider_contracts import (
    AIRequest, AIResult, ProviderRateLimitError, ProviderTimeoutError,
    ProviderUnavailableError, ResearchQuery, ResearchResult, ResearchSource,
)


def _source(source_id: str, title: str, url: str, language: str, region: str) -> ResearchSource:
    return ResearchSource(
        source_id=source_id, url=url, title=title,
        snippet=f"Testilähteen {title} kuvaus.", language=language, region=region,
        reliability_class="A", claim_level="officially_confirmed",
        checked_at="2026-11-18T10:00:00+02:00",
        published_at="2026-11-17T09:00:00+02:00",
        metadata={"fixture": True},
    )


class FixtureAIProcessor:
    """Ensimmäinen deterministinen tekoälyadapteri."""
    provider_id = "fixture-ai"
    capabilities = frozenset({"ai.generate", "source.traceability", "uncertainty"})

    def __init__(self, *, fail_first: bool = False, estimated_cost: float = 0.01):
        self.fail_first = fail_first
        self.estimated_cost = estimated_cost
        self.calls = 0
        self.last_timeout = None

    def estimate_cost(self, request: AIRequest) -> float:
        return self.estimated_cost

    def process(self, request: AIRequest, *, timeout_seconds: float) -> AIResult:
        self.calls += 1
        self.last_timeout = timeout_seconds
        if self.fail_first and self.calls == 1:
            raise ProviderTimeoutError("Testiadapterin ensimmäinen pyyntö aikakatkaistiin.")
        return AIResult(
            content=f"Testiyhteenveto: {request.content}",
            source_refs=request.source_refs,
            uncertainty="medium",
            estimated_cost=self.estimated_cost,
            notes=("Deterministinen testitulos.",),
            metadata={"adapter":"fixture-ai"},
        )


class AlternateAIProcessor:
    """Toinen, eri toteutuksella toimiva tekoälyadapteri."""
    provider_id = "alternate-ai"
    capabilities = frozenset({"ai.generate", "source.traceability", "uncertainty"})

    def __init__(self, *, estimated_cost: float = 0.02):
        self.estimated_cost = estimated_cost
        self.calls = 0

    def estimate_cost(self, request: AIRequest) -> float:
        return self.estimated_cost

    def process(self, request: AIRequest, *, timeout_seconds: float) -> AIResult:
        self.calls += 1
        return AIResult(
            content=f"Vaihtoehtoinen tulos moduulille {request.module_id}.",
            source_refs=request.source_refs,
            uncertainty="low",
            estimated_cost=self.estimated_cost,
            metadata={"adapter":"alternate-ai"},
        )


class FixtureResearchProvider:
    """Ensimmäinen testihakupalvelu; voi simuloida yhden rate limit -virheen."""
    provider_id = "fixture-research"
    capabilities = frozenset({"research.search", "research.open_source", "source.provenance"})

    def __init__(self, *, rate_limit_first: bool = False, estimated_cost: float = 0.01):
        self.rate_limit_first = rate_limit_first
        self.estimated_cost = estimated_cost
        self.search_calls = 0
        self.open_calls = 0
        self.sources = {
            "source-a": _source("source-a","Ensisijainen testilähde","https://example.test/source-a","fi","FI"),
            "source-b": _source("source-b","Toimituksellinen testilähde","https://example.test/source-b","en","GLOBAL"),
        }

    def estimate_search_cost(self, query: ResearchQuery) -> float:
        return self.estimated_cost

    def search(self, query: ResearchQuery, *, timeout_seconds: float) -> ResearchResult:
        self.search_calls += 1
        if self.rate_limit_first and self.search_calls == 1:
            raise ProviderRateLimitError("Testikiintiö täynnä.", retry_after_seconds=0.1)
        allowed = set(query.allowed_source_ids)
        sources = tuple(
            source for source in self.sources.values()
            if not allowed or source.source_id in allowed
        )[:query.max_results]
        return ResearchResult(sources=sources, complete=True, estimated_cost=self.estimated_cost)

    def estimate_open_cost(self, source_id: str) -> float:
        return self.estimated_cost

    def open_source(self, source_id: str, *, timeout_seconds: float) -> ResearchSource:
        self.open_calls += 1
        try:
            return self.sources[source_id]
        except KeyError as exc:
            raise ProviderUnavailableError(f"Testilähdettä {source_id} ei löydy.") from exc


class AlternateResearchProvider:
    """Toinen testihakupalvelu, joka palauttaa eri lähdejoukon."""
    provider_id = "alternate-research"
    capabilities = frozenset({"research.search", "research.open_source", "source.provenance"})

    def __init__(self, *, estimated_cost: float = 0.015):
        self.estimated_cost = estimated_cost
        self.calls = 0
        self.sources = {
            "source-b": _source("source-b","Vaihtoehtoinen testilähde","https://example.test/alternate","en","GLOBAL")
        }

    def estimate_search_cost(self, query: ResearchQuery) -> float:
        return self.estimated_cost

    def search(self, query: ResearchQuery, *, timeout_seconds: float) -> ResearchResult:
        self.calls += 1
        source = self.sources["source-b"]
        if query.allowed_source_ids and source.source_id not in query.allowed_source_ids:
            return ResearchResult(sources=(), complete=True, estimated_cost=self.estimated_cost)
        return ResearchResult(sources=(source,), complete=True, estimated_cost=self.estimated_cost)

    def estimate_open_cost(self, source_id: str) -> float:
        return self.estimated_cost

    def open_source(self, source_id: str, *, timeout_seconds: float) -> ResearchSource:
        try:
            return self.sources[source_id]
        except KeyError as exc:
            raise ProviderUnavailableError(f"Testilähdettä {source_id} ei löydy.") from exc
