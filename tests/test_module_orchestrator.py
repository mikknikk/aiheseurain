"""Testaa yhteisen moduuliorchestratorin elinkaari, varjotila ja tapahtumatyypit."""
from copy import deepcopy
from pathlib import Path
import json
import unittest

from scripts.module_registry import load_registry, ModuleResult, RegistryResult
from scripts.module_state import StateConflictError
from scripts.event_watch import empty_state
from scripts.module_orchestrator import (
    EventWatchModuleExecutor, ModuleExecutionOutput, ModuleOrchestrator,
    ModuleRunRequest, ObservationBatch, PublicationReceipt, QualityGateResult,
    ShadowComparison,
)

ROOT=Path(__file__).resolve().parents[1]
NOW="2026-11-18T23:00:00+02:00"
START="2026-11-18T00:00:00+02:00"
END="2026-11-18T22:59:59+02:00"


def definition(module_id="tolkien"):
    registry=load_registry(include_inactive=True)
    return next(item.definition for item in registry.modules if item.module_id==module_id)


def request(module_id="tolkien",mode="shadow",run_id="orchestrator-run-01",at=NOW):
    module=definition(module_id)
    return ModuleRunRequest(
        module_id=module_id,module_definition_version=module["definition_version"],
        contract_version=module["contract_version"],run_id=run_id,
        period_start=START,period_end=END,mode=mode,requested_at=at
    )


def output_for(req,status="succeeded",complete=True):
    return ModuleExecutionOutput(
        status=status,source_scan_complete=complete,checked_at=req.requested_at,
        period_start=req.period_start,period_end=req.period_end,
        report_content="Testiraportti",published_items=1,sources_checked=10,
        source_check_run_refs=("source-check-new",),artifacts={"example":{"value":1}}
    )


class FakeExecutor:
    def __init__(self,*,status="succeeded",complete=True,fail_modules=()):
        self.status=status
        self.complete=complete
        self.fail_modules=set(fail_modules)
        self.calls=[]
    def execute(self,definition,request,provider_router):
        self.calls.append((definition["module_id"],request.run_id,provider_router))
        if request.module_id in self.fail_modules:
            raise RuntimeError("simuloitu moduulivirhe")
        return output_for(request,self.status,self.complete)


class PassGate:
    def __init__(self,passed=True):
        self.passed=passed
        self.calls=0
    def validate(self,definition,request,output):
        self.calls+=1
        return QualityGateResult(self.passed,() if self.passed else ("sisältö ei täytä vaatimuksia",))


class FakeComparator:
    def __init__(self,equivalent=True):
        self.equivalent=equivalent
        self.calls=0
    def compare(self,definition,request,output):
        self.calls+=1
        return ShadowComparison(self.equivalent,"Testivertailu tehty.")


class FakeStateStore:
    def __init__(self,state,fail_save=False):
        self.state=deepcopy(state)
        self.sha="state-sha-1"
        self.saves=0
        self.loads=0
        self.fail_save=fail_save
    def load(self,module_id):
        self.loads+=1
        return deepcopy(self.state),self.sha
    def save(self,module_id,state,*,expected_sha):
        if self.fail_save or expected_sha!=self.sha:
            raise StateConflictError("testitilan SHA-konflikti")
        self.state=deepcopy(state)
        self.saves+=1
        self.sha=f"state-sha-{self.saves+1}"
        return self.sha


class FakeArtifactStore:
    def __init__(self):
        self.version="artifact-v1"
        self.commits={}
    def load_version(self,module_id):
        return self.version
    def commit(self,module_id,run_id,artifacts,*,expected_version):
        key=(module_id,run_id)
        if key in self.commits:
            return self.version
        if expected_version!=self.version:
            raise StateConflictError("testiartifaktin versioristiriita")
        self.commits[key]=deepcopy(artifacts)
        self.version=f"artifact-v{len(self.commits)+1}"
        return self.version


class FakePublisher:
    def __init__(self,verified=True):
        self.verified=verified
        self.receipts={}
        self.keys=[]
    def publish(self,module_id,run_id,report_content,*,idempotency_key):
        self.keys.append(idempotency_key)
        if idempotency_key not in self.receipts:
            self.receipts[idempotency_key]=PublicationReceipt(
                verified=self.verified,report_guid_refs=(f"guid-{run_id}",),published_items=1
            )
        return self.receipts[idempotency_key]
    def verify(self,receipt):
        return receipt.verified


def active_registry_loader(include_inactive=False):
    """Testissä yksi moduuli on aktiivinen; repositorion oikeaa rekisteriä ei muuteta."""
    result=load_registry(include_inactive=True)
    modules=[]
    for item in result.modules:
        if item.module_id=="tolkien":
            modules.append(ModuleResult(item.module_id,"active",item.path,item.definition))
        else:
            modules.append(item)
    return RegistryResult(tuple(modules))


class ModuleRegistryShadowTests(unittest.TestCase):
    def test_inactive_definitions_are_loaded_only_when_requested(self):
        """Oletuslataus ei aktivoi passiivista määritystä; varjotila voi lukea sen."""
        default=load_registry()
        shadow=load_registry(include_inactive=True)
        inactive_default=next(item for item in default.modules if item.module_id=="tolkien")
        inactive_shadow=next(item for item in shadow.modules if item.module_id=="tolkien")
        self.assertEqual(inactive_default.status,"inactive")
        self.assertIsNone(inactive_default.definition)
        self.assertEqual(inactive_shadow.status,"inactive")
        self.assertIsNotNone(inactive_shadow.definition)
        self.assertNotIn("tolkien",shadow.active_modules)


class ShadowModeTests(unittest.TestCase):
    def test_shadow_mode_compares_without_publishing_or_writing_state(self):
        """Varjotila ei kutsu tallennusta tai julkaisua eikä siirrä checkpointia."""
        executor=FakeExecutor()
        gate=PassGate()
        comparator=FakeComparator()
        publisher=FakePublisher()
        state_store=FakeStateStore(json.loads((ROOT/"data/module-state/tolkien.json").read_text(encoding="utf-8")))
        artifacts=FakeArtifactStore()
        orchestrator=ModuleOrchestrator(
            executor=executor,quality_gate=gate,state_store=state_store,
            artifact_store=artifacts,publisher=publisher,comparator=comparator
        )
        result=orchestrator.run(request())
        self.assertEqual(result.status,"succeeded")
        self.assertFalse(result.published)
        self.assertFalse(result.checkpoint_updated)
        self.assertTrue(result.comparison["equivalent"])
        self.assertEqual(publisher.keys,[])
        self.assertEqual(artifacts.commits,{})
        self.assertEqual(state_store.loads,0)
        self.assertEqual(state_store.saves,0)

    def test_production_requires_explicit_authorization_and_active_module(self):
        """Passiivinen moduuli tai puuttuva erillinen hyväksyntä estää tuotantoajon."""
        executor=FakeExecutor()
        orchestrator=ModuleOrchestrator(executor=executor,quality_gate=PassGate())
        no_approval=orchestrator.run(request(mode="production"),production_authorized=False)
        self.assertEqual(no_approval.status,"rejected")
        self.assertEqual(no_approval.error_code,"production_activation_required")
        approved_but_inactive=orchestrator.run(request(mode="production",run_id="orchestrator-run-02"),production_authorized=True)
        self.assertEqual(approved_but_inactive.status,"rejected")
        self.assertEqual(approved_but_inactive.error_code,"module_inactive")
        self.assertEqual(executor.calls,[])

    def test_run_result_contains_module_version_run_id_and_period(self):
        """Varjotilan tulos on jäljitettävissä moduuliin, versioon ja ajojaksoon."""
        orchestrator=ModuleOrchestrator(executor=FakeExecutor(),quality_gate=PassGate())
        req=request(run_id="trace-run-001")
        result=orchestrator.run(req)
        data=result.to_dict()
        self.assertEqual(data["module_id"],"tolkien")
        self.assertEqual(data["module_definition_version"],req.module_definition_version)
        self.assertEqual(data["run_id"],"trace-run-001")
        self.assertEqual(data["period"]["start"],START)
        self.assertEqual(data["period"]["end"],END)


class ProductionLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.state=json.loads((ROOT/"data/module-state/tolkien.json").read_text(encoding="utf-8"))
        self.state_store=FakeStateStore(self.state)
        self.artifacts=FakeArtifactStore()
        self.publisher=FakePublisher()
        self.executor=FakeExecutor()
        self.gate=PassGate()
        self.orchestrator=ModuleOrchestrator(
            executor=self.executor,quality_gate=self.gate,state_store=self.state_store,
            artifact_store=self.artifacts,publisher=self.publisher,
            registry_loader=active_registry_loader
        )

    def test_successful_production_run_publishes_persists_and_advances_checkpoint(self):
        """Täydellinen ja laadultaan hyväksytty ajo julkaistaan ennen checkpointin siirtoa."""
        result=self.orchestrator.run(request(mode="production",run_id="production-run-001"),production_authorized=True)
        self.assertEqual(result.status,"succeeded")
        self.assertTrue(result.published)
        self.assertTrue(result.checkpoint_updated)
        self.assertEqual(self.state_store.state["checkpoint"]["last_successful_run"]["run_id"],"production-run-001")
        self.assertEqual(len(self.artifacts.commits),1)
        self.assertEqual(self.publisher.keys,["tolkien:production-run-001"])

    def test_same_run_id_is_idempotent(self):
        """Saman run_id:n uusinta ei lisää checkpoint-historiaa tai toista julkaisuavainta."""
        req=request(mode="production",run_id="production-run-002")
        first=self.orchestrator.run(req,production_authorized=True)
        history_count=len(self.state_store.state["checkpoint_history"])
        second=self.orchestrator.run(req,production_authorized=True)
        self.assertEqual(first.status,"succeeded")
        self.assertEqual(second.status,"succeeded")
        self.assertEqual(len(self.state_store.state["checkpoint_history"]),history_count)
        self.assertEqual(len(set(self.publisher.keys)),1)

    def test_partial_source_scan_does_not_publish_or_advance_checkpoint(self):
        """Osittainen haku ei julkaise eikä muuta moduulin tilaa."""
        self.orchestrator.executor=FakeExecutor(status="partial",complete=False)
        result=self.orchestrator.run(request(mode="production",run_id="partial-run-001"),production_authorized=True)
        self.assertEqual(result.status,"partial")
        self.assertFalse(result.published)
        self.assertFalse(result.checkpoint_updated)
        self.assertEqual(self.publisher.keys,[])
        self.assertEqual(self.state_store.saves,0)
        self.assertEqual(self.artifacts.commits,{})

    def test_quality_gate_rejection_does_not_publish(self):
        """Yhteisen laadunvarmistusportin hylkäys pysäyttää julkaisun."""
        self.orchestrator.quality_gate=PassGate(passed=False)
        result=self.orchestrator.run(request(mode="production",run_id="quality-fail-001"),production_authorized=True)
        self.assertEqual(result.status,"failed")
        self.assertEqual(result.error_code,"quality_gate_rejected")
        self.assertFalse(result.published)
        self.assertEqual(self.publisher.keys,[])
        self.assertEqual(self.state_store.saves,0)

    def test_unverified_publication_does_not_advance_checkpoint(self):
        """Julkaisun takaisinlukutarkistuksen epäonnistuminen estää checkpointin."""
        self.orchestrator.publisher=FakePublisher(verified=False)
        result=self.orchestrator.run(request(mode="production",run_id="publish-fail-001"),production_authorized=True)
        self.assertEqual(result.status,"failed")
        self.assertEqual(result.error_code,"publication_unverified")
        self.assertFalse(result.checkpoint_updated)
        self.assertEqual(self.state_store.saves,0)

    def test_state_sha_conflict_after_publish_is_partial_and_traceable(self):
        """Julkaistu ajo ilman tilan tallennusta palautuu osittaisena eikä peitä konfliktia."""
        self.orchestrator.state_store=FakeStateStore(self.state,fail_save=True)
        result=self.orchestrator.run(request(mode="production",run_id="state-conflict-001"),production_authorized=True)
        self.assertEqual(result.status,"partial")
        self.assertTrue(result.published)
        self.assertFalse(result.checkpoint_updated)
        self.assertEqual(result.error_code,"state_conflict")


class ModuleIsolationTests(unittest.TestCase):
    def test_one_module_failure_does_not_block_the_next_module(self):
        """Yhden moduulin suoritusvirhe ei pysäytä saman erän muita moduuleja."""
        executor=FakeExecutor(fail_modules={"tolkien"})
        orchestrator=ModuleOrchestrator(executor=executor,quality_gate=PassGate())
        results=orchestrator.run_many([
            request("tolkien",run_id="isolated-run-001"),
            request("taylor-swift",run_id="isolated-run-002")
        ])
        self.assertEqual([result.status for result in results],["failed","succeeded"])
        self.assertEqual(len(executor.calls),1)
        self.assertEqual(results[0].module_id,"tolkien")
        self.assertEqual(results[1].module_id,"taylor-swift")


class GenericEventWatchTests(unittest.TestCase):
    """Sama tapahtumavahtisuorittaja lukee tyypin moduulin viitteestä."""

    class Observations:
        def __init__(self,event_type_id,attributes):
            self.event_type_id=event_type_id
            self.attributes=attributes
        def collect(self,definition,request,provider_router):
            source={"publisher":"Testijärjestäjä","url":"https://example.test/event",
                    "checked_at":NOW,"claim_level":"official"}
            observation={"event_type_id":self.event_type_id,"canonical_event_id":"event-1",
                         "attributes":self.attributes,"sources":[source],"observed_at":NOW}
            return ObservationBatch((observation,),True,(),1,("source-check-event-1",),NOW)

    def test_same_executor_supports_film_and_conference_event_types(self):
        """Elokuvanäytös ja konferenssiesitys käsitellään saman yleisen tapahtumaytimen kautta."""
        film_definition=definition("indian-film-screening-watch")
        conference_definition={
            "module_id":"conference-watch","module_type":"process",
            "process_extension":{"configuration":{"event_type_ref":"examples/event-types/conference-session.json"}}
        }
        cases=[
            (film_definition,"film-screening",{"title":"Testielokuva","venue":"Testisali","city":"Helsinki","starts_at":"2026-11-20T18:00:00+02:00","status":"scheduled"}),
            (conference_definition,"conference-session",{"title":"Esitys","conference":"Konferenssi","session_code":"A-01","starts_at":"2026-11-20T10:00:00+02:00","status":"scheduled"})
        ]
        for definition_value,event_type_id,attributes in cases:
            request_value=ModuleRunRequest(
                module_id=definition_value["module_id"],module_definition_version=definition_value.get("definition_version","1.0.0"),
                contract_version=definition_value.get("contract_version","1.0.0"),run_id=f"event-run-{event_type_id}",
                period_start=START,period_end=END,mode="shadow",requested_at=NOW
            )
            executor=EventWatchModuleExecutor(self.Observations(event_type_id,attributes))
            result=executor.execute(definition_value,request_value,None)
            state=result.artifacts["event_state"]
            self.assertEqual(state["event_type_id"],event_type_id)
            self.assertEqual(len(state["current_events"]),1)
            self.assertEqual(result.status,"succeeded")
            self.assertEqual(result.metadata["event_type_id"],event_type_id)

    def test_incomplete_event_scan_is_marked_partial(self):
        """Yhden lähteen epäonnistuminen näkyy osittaisena tapahtumahakuna."""
        class PartialObservations:
            def collect(self,definition,request,provider_router):
                return ObservationBatch((),False,("source-unavailable",),0,(),NOW)
        film_definition=definition("indian-film-screening-watch")
        req=request("indian-film-screening-watch",run_id="partial-event-run")
        result=EventWatchModuleExecutor(PartialObservations()).execute(film_definition,req,None)
        self.assertEqual(result.status,"partial")
        self.assertFalse(result.source_scan_complete)


if __name__=="__main__":
    unittest.main()
