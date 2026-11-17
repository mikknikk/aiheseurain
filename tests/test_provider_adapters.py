"""Testaa AIProcessor- ja ResearchProvider-sopimukset, reititys ja virheenkäsittely."""
from pathlib import Path
import json
import unittest

from scripts.provider_contracts import (
    AIRequest, ResearchQuery, CostBudget, ProviderAuthenticationError,
    ProviderContractError, ProviderCostLimitError, ProviderRateLimitError,
)
from scripts.provider_router import ProviderRouter, load_provider_config, validate_provider_config
from scripts.providers.testing import (
    FixtureAIProcessor, AlternateAIProcessor,
    FixtureResearchProvider, AlternateResearchProvider,
)


ROOT = Path(__file__).resolve().parents[1]
AI_CAPS = ["ai.generate", "source.traceability", "uncertainty"]
RESEARCH_CAPS = ["research.open_source", "research.search", "source.provenance"]


def provider(provider_id, provider_type, adapter_id, capabilities):
    return {
        "provider_id":provider_id,"provider_type":provider_type,"adapter_id":adapter_id,
        "capabilities":capabilities,"credential_env":[],
        "timeout_seconds":3,
        "retry_policy":{"max_attempts":2,"base_delay_seconds":0.01,"max_delay_seconds":0.5},
        "cost_limit":{"per_run":0.5},"enabled":True
    }


def test_config():
    return {
        "schema_version":1,
        "providers":[
            provider("fixture-ai","ai_processor","fixture-ai-v1",AI_CAPS),
            provider("alternate-ai","ai_processor","alternate-ai-v1",AI_CAPS),
            provider("fixture-research","research_provider","fixture-research-v1",RESEARCH_CAPS),
            provider("alternate-research","research_provider","alternate-research-v1",RESEARCH_CAPS),
        ],
        "routes":{
            "tolkien":{"ai_processor":"fixture-ai","research_provider":"fixture-research"},
            "taylor-swift":{"ai_processor":"alternate-ai","research_provider":"alternate-research"}
        },
        "default_route":None
    }


def router(config=None, *, ai=None, research=None, sleep_fn=lambda delay: None):
    return ProviderRouter(
        config or test_config(),
        ai_processors=ai or [FixtureAIProcessor(),AlternateAIProcessor()],
        research_providers=research or [FixtureResearchProvider(),AlternateResearchProvider()],
        sleep_fn=sleep_fn
    )


class ProviderContractTests(unittest.TestCase):
    """Molemmat testiadapterit täyttävät saman normalisoidun sopimuksen."""

    def test_two_ai_adapters_return_same_contract_shape(self):
        first=FixtureAIProcessor()
        second=AlternateAIProcessor()
        request=AIRequest(module_id="tolkien",run_id="test-ai",content="Tarkista Tolkien-uutinen.",source_refs=("source-a",))
        for adapter in (first,second):
            result=adapter.process(request,timeout_seconds=3)
            self.assertEqual(result.contract_version,"1.0.0")
            self.assertIn("source-a",result.source_refs)
            self.assertIn(result.uncertainty,{"low","medium","high","unknown"})
            self.assertGreaterEqual(result.estimated_cost,0)

    def test_two_research_adapters_return_same_contract_shape(self):
        query=ResearchQuery(module_id="tolkien",run_id="test-search",query_terms=("Tolkien",),allowed_source_ids=("source-a","source-b"))
        for adapter in (FixtureResearchProvider(),AlternateResearchProvider()):
            result=adapter.search(query,timeout_seconds=3)
            self.assertEqual(result.contract_version,"1.0.0")
            self.assertTrue(result.complete)
            for source in result.sources:
                self.assertIn(source.source_id,query.allowed_source_ids)
                self.assertTrue(source.url.startswith("https://"))
                self.assertIn(source.reliability_class,{"A","B","C","D"})

    def test_production_configuration_is_empty_and_valid(self):
        config=load_provider_config()
        self.assertEqual(config["providers"],[])
        self.assertEqual(config["routes"],{})
        self.assertIsNone(config["default_route"])

    def test_secret_values_are_not_accepted_in_configuration(self):
        config=test_config()
        config["providers"][0]["api_key"]="do-not-store"
        with self.assertRaises(ProviderContractError):
            validate_provider_config(config)
        config=test_config()
        config["providers"][0]["credential_env"]=["sk-this-is-a-secret-value"]
        with self.assertRaises(ProviderContractError):
            validate_provider_config(config)


class ProviderRoutingTests(unittest.TestCase):
    """Palvelu voidaan vaihtaa moduulireitityksessä muuttamatta moduulia."""

    def test_module_specific_ai_routes_select_different_adapters(self):
        first=FixtureAIProcessor()
        second=AlternateAIProcessor()
        service=router(ai=[first,second])
        request1=AIRequest(module_id="tolkien",run_id="run-a",content="Tolkien",source_refs=("source-a",))
        request2=AIRequest(module_id="taylor-swift",run_id="run-b",content="Taylor Swift",source_refs=("source-a",))
        result1=service.process_ai(request1,budget=service.budget_for("tolkien","ai_processor"))
        result2=service.process_ai(request2,budget=service.budget_for("taylor-swift","ai_processor"))
        self.assertTrue(result1.content.startswith("Testiyhteenveto"))
        self.assertTrue(result2.content.startswith("Vaihtoehtoinen tulos"))
        self.assertEqual([x.provider_id for x in service.audit_records],["fixture-ai","alternate-ai"])

    def test_module_specific_research_routes_select_different_adapters(self):
        first=FixtureResearchProvider()
        second=AlternateResearchProvider()
        service=router(research=[first,second])
        query=ResearchQuery(module_id="tolkien",run_id="run-a",query_terms=("Tolkien",),allowed_source_ids=("source-a","source-b"))
        query2=ResearchQuery(module_id="taylor-swift",run_id="run-b",query_terms=("Taylor Swift",),allowed_source_ids=("source-a","source-b"))
        result1=service.search(query,budget=service.budget_for("tolkien","research_provider"))
        result2=service.search(query2,budget=service.budget_for("taylor-swift","research_provider"))
        self.assertEqual([s.source_id for s in result1.sources],["source-a","source-b"])
        self.assertEqual([s.source_id for s in result2.sources],["source-b"])
        self.assertEqual([x.provider_id for x in service.audit_records],["fixture-research","alternate-research"])

    def test_open_source_preserves_requested_source_id(self):
        service=router()
        source=service.open_source(module_id="tolkien",run_id="run-open",source_id="source-a",budget=service.budget_for("tolkien","research_provider"))
        self.assertEqual(source.source_id,"source-a")
        self.assertEqual(service.audit_records[-1].status,"succeeded")

    def test_route_does_not_modify_module_definition_or_state(self):
        module_path=ROOT/"modules/topics/tolkien/module.json"
        state_path=ROOT/"data/module-state/tolkien.json"
        before_module=module_path.read_bytes()
        before_state=state_path.read_bytes()
        service=router()
        service.process_ai(AIRequest(module_id="tolkien",run_id="run-x",content="Test",source_refs=("source-a",)),budget=service.budget_for("tolkien","ai_processor"))
        self.assertEqual(module_path.read_bytes(),before_module)
        self.assertEqual(state_path.read_bytes(),before_state)

    def test_missing_route_or_capability_fails_closed(self):
        config=test_config()
        config["routes"]={}
        service=router(config)
        with self.assertRaises(Exception):
            service.process_ai(AIRequest(module_id="unknown-topic",run_id="r",content="x"),budget=CostBudget(1))
        config=test_config()
        config["providers"][0]["capabilities"]=["ai.generate"]
        service=router(config)
        with self.assertRaises(ProviderContractError):
            service.process_ai(AIRequest(module_id="tolkien",run_id="r",content="x"),budget=CostBudget(1))


class ReliabilityAndSafetyTests(unittest.TestCase):
    """Aikakatkaisut, kiintiöt, kustannukset ja auditointi käsitellään rajatusti."""

    def test_timeout_is_retried_and_timeout_limit_is_passed_to_adapter(self):
        adapter=FixtureAIProcessor(fail_first=True)
        sleeps=[]
        service=router(ai=[adapter,AlternateAIProcessor()],sleep_fn=sleeps.append)
        request=AIRequest(module_id="tolkien",run_id="retry-ai",content="Private prompt",source_refs=("source-a",))
        service.process_ai(request,budget=service.budget_for("tolkien","ai_processor"))
        self.assertEqual(adapter.calls,2)
        self.assertEqual(adapter.last_timeout,3)
        self.assertEqual(len(sleeps),1)
        self.assertEqual(service.audit_records[-1].attempts,2)

    def test_rate_limit_is_retried_using_retry_after(self):
        adapter=FixtureResearchProvider(rate_limit_first=True)
        sleeps=[]
        service=router(research=[adapter,AlternateResearchProvider()],sleep_fn=sleeps.append)
        query=ResearchQuery(module_id="tolkien",run_id="retry-search",query_terms=("Tolkien",),allowed_source_ids=("source-a",))
        service.search(query,budget=service.budget_for("tolkien","research_provider"))
        self.assertEqual(adapter.search_calls,2)
        self.assertEqual(sleeps,[0.1])
        self.assertEqual(service.audit_records[-1].attempts,2)

    def test_cost_budget_blocks_call_before_provider_invocation(self):
        adapter=FixtureAIProcessor()
        service=router(ai=[adapter,AlternateAIProcessor()])
        request=AIRequest(module_id="tolkien",run_id="cost",content="test")
        with self.assertRaises(ProviderCostLimitError):
            service.process_ai(request,budget=CostBudget(max_cost=0.001))
        self.assertEqual(adapter.calls,0)
        self.assertEqual(service.audit_records[-1].attempts,0)

    def test_authentication_error_is_not_retried(self):
        class AuthFailureAI(FixtureAIProcessor):
            def process(self, request, *, timeout_seconds):
                self.calls+=1
                raise ProviderAuthenticationError("Tunnistus epäonnistui.")
        adapter=AuthFailureAI()
        service=router(ai=[adapter,AlternateAIProcessor()])
        request=AIRequest(module_id="tolkien",run_id="auth",content="test")
        with self.assertRaises(ProviderAuthenticationError):
            service.process_ai(request,budget=service.budget_for("tolkien","ai_processor"))
        self.assertEqual(adapter.calls,1)
        self.assertEqual(service.audit_records[-1].error_code,"authentication")

    def test_audit_record_contains_no_prompt_or_secret(self):
        service=router()
        request=AIRequest(module_id="tolkien",run_id="audit",content="private prompt secret-value")
        service.process_ai(request,budget=service.budget_for("tolkien","ai_processor"))
        audit=repr(service.audit_records)
        self.assertNotIn("private prompt",audit)
        self.assertNotIn("secret-value",audit)
        self.assertNotIn("content",service.audit_records[-1].__dict__)

    def test_rate_limit_beyond_retry_cap_is_not_retried(self):
        adapter=FixtureResearchProvider(rate_limit_first=True)
        config=test_config()
        for item in config["providers"]:
            if item["provider_id"]=="fixture-research":
                item["retry_policy"]["max_delay_seconds"]=0.01
        service=router(config,research=[adapter,AlternateResearchProvider()])
        query=ResearchQuery(module_id="tolkien",run_id="retry-cap",query_terms=("Tolkien",))
        with self.assertRaises(ProviderRateLimitError):
            service.search(query,budget=service.budget_for("tolkien","research_provider"))
        self.assertEqual(adapter.search_calls,1)


if __name__ == "__main__":
    unittest.main()
