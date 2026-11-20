import test from "node:test";
import assert from "node:assert/strict";
import { resolveStatusOption, resolvePriorityOption, resolveComponentOption } from "../.github/scripts/sync_project_status.mjs";

const options = {
  "status:backlog": { name: "Todo", id: "f75ad846" },
  "status:ready-for-development": { name: "Ready for Development", id: "4a70c3f4" },
  "status:in-progress": { name: "In Progress", id: "47fc9ee4" },
  "status:done": { name: "Done", id: "98236657" }
};

test("muuntaa Aiheseuraimen tilalabelit Projectin Status-vaihtoehdoiksi", () => {
  assert.equal(resolveStatusOption([{ name: "status:backlog" }], options).option.name, "Todo");
  assert.equal(resolveStatusOption(["status:ready-for-development"], options).option.name, "Ready for Development");
  assert.equal(resolveStatusOption([{ name: "status:in-progress" }], options).option.name, "In Progress");
  assert.equal(resolveStatusOption([{ name: "status:done" }], options).option.name, "Done");
});

test("hylkää puuttuvan tai useamman tilalabelin", () => {
  assert.throws(() => resolveStatusOption([], options), /täsmälleen yksi/);
  assert.throws(() => resolveStatusOption([
    { name: "status:backlog" }, { name: "status:done" }
  ], options), /täsmälleen yksi/);
});

test("hylkää tuntemattoman tilalabelin", () => {
  assert.throws(() => resolveStatusOption([{ name: "status:blocked" }], options), /Tuntematon tilalabel/);
});

test("ohittaa issuet, joilla ei ole kehityskomponentin labelia", async () => {
  const { syncIssueStatus } = await import("../.github/scripts/sync_project_status.mjs");
  let graphqlCalled = false;
  const fetchMock = async (url) => {
    assert.match(String(url), /\/repos\/mikknikk\/aiheseurain\/issues\/42$/);
    return {
      ok: true,
      status: 200,
      json: async () => ({
        number: 42,
        node_id: "I_test",
        labels: [{ name: "question" }]
      })
    };
  };
  const result = await syncIssueStatus({
    repository: "mikknikk/aiheseurain",
    issueNumber: 42,
    githubToken: "test",
    projectsToken: "test",
    config: {
      repository: "mikknikk/aiheseurain",
      project: { id: "P_test", status_field_id: "F_test", options }
    },
    fetchImpl: async (...args) => {
      if (String(args[0]).includes("/graphql")) graphqlCalled = true;
      return fetchMock(...args);
    }
  });
  assert.deepEqual(result, { skipped: "not_a_development_issue" });
  assert.equal(graphqlCalled, false);
});


test("muuntaa prioriteettilabelit Projectin Priority-vaihtoehdoiksi", async () => {
  const priorityOptions = {
    "priority:P0": { id: "e8877887" },
    "priority:P1": { id: "4eb95e26" },
    "priority:P2": { id: "024b8b15" },
    "priority:P3": { id: "6c5a768d" }
  };
  assert.equal(resolvePriorityOption([{ name: "priority:P0" }], priorityOptions).option.id, "e8877887");
  assert.equal(resolvePriorityOption(["priority:P1"], priorityOptions).option.id, "4eb95e26");
  assert.equal(resolvePriorityOption([{ name: "priority:P2" }], priorityOptions).option.id, "024b8b15");
  assert.equal(resolvePriorityOption([{ name: "priority:P3" }], priorityOptions).option.id, "6c5a768d");
  // Vaihtoehdon nimen muuttuminen ei vaikuta tunnisteeseen perustuvaan määritykseen.
  assert.equal(resolvePriorityOption(["priority:P1"], { "priority:P1": { id: "4eb95e26" } }).option.id, "4eb95e26");
});

test("hylkää puuttuvan, ristiriitaisen tai tuntemattoman prioriteettilabelin", async () => {
  const { resolvePriorityOption } = await import("../.github/scripts/sync_project_status.mjs");
  const options = [{ name: "P1", id: "p1" }];
  assert.throws(() => resolvePriorityOption([], options), /täsmälleen yksi/);
  assert.throws(() => resolvePriorityOption(["priority:P1", "priority:P2"], options), /täsmälleen yksi/);
  assert.throws(() => resolvePriorityOption(["priority:P9"], options), /Tuntematon prioriteettilabel/);
  assert.throws(() => resolvePriorityOption(["priority:P1"], {}), /ei ole määritetty Project-vaihtoehdon tunnistetta/);
});

test("prioriteettivaihtoehtojen määritys ei riipu kentän tai vaihtoehdon nimistä", () => {
  const config = JSON.parse('{"priority_field_id":"PVTSSF_lAHOACf60s4BsfD3zhqtqmU","priority_options":{"priority:P1":{"id":"4eb95e26"}}}');
  assert.equal(config.priority_field_id, "PVTSSF_lAHOACf60s4BsfD3zhqtqmU");
  assert.equal(config.priority_options["priority:P1"].id, "4eb95e26");
});

const componentOptions = {
  "component:automaatio": { id: "b27e01e4" },
  "component:valvomo": { id: "8bf95c0b" },
  "component:lukija": { id: "31835d81" },
  "component:etusivu": { id: "3318d8fa" }
};

test("muuntaa komponenttilabelit Projectin Component-vaihtoehtojen ID-tunnisteiksi", () => {
  assert.equal(resolveComponentOption(["component:automaatio"], componentOptions).option.id, "b27e01e4");
  assert.equal(resolveComponentOption([{ name: "component:valvomo" }], componentOptions).option.id, "8bf95c0b");
  assert.equal(resolveComponentOption(["component:lukija"], componentOptions).option.id, "31835d81");
  assert.equal(resolveComponentOption(["component:etusivu"], componentOptions).option.id, "3318d8fa");
});

test("komponenttivaihtoehtojen nimet eivät vaikuta ID-pohjaiseen synkronointiin", () => {
  const renamedOptions = { "component:automaatio": { id: "b27e01e4", name: "Uusi näkyvä nimi" } };
  assert.equal(resolveComponentOption(["component:automaatio"], renamedOptions).option.id, "b27e01e4");
});

test("hylkää puuttuvan, moninkertaisen tai tuntemattoman komponenttilabelin", () => {
  assert.throws(() => resolveComponentOption([], componentOptions), /täsmälleen yksi/);
  assert.throws(() => resolveComponentOption(["component:lukija", "component:valvomo"], componentOptions), /täsmälleen yksi/);
  assert.throws(() => resolveComponentOption(["component:virheellinen"], componentOptions), /ei ole määritetty Project-vaihtoehdon tunnistetta/);
  assert.throws(() => resolveComponentOption(["compontent:lukija"], componentOptions), /täsmälleen yksi/);
});
