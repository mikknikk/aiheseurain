import test from "node:test";
import assert from "node:assert/strict";
import { resolveStatusOption } from "../.github/scripts/sync_project_status.mjs";

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
  const { resolvePriorityOption } = await import("../.github/scripts/sync_project_status.mjs");
  const priorityOptions = [
    { name: "P0 Kriittinen", id: "p0" },
    { name: "P1 Korkea", id: "p1" },
    { name: "P2 Normaali", id: "p2" },
    { name: "P3 Matala", id: "p3" }
  ];
  assert.equal(resolvePriorityOption([{ name: "priority:P0" }], priorityOptions).option.id, "p0");
  assert.equal(resolvePriorityOption(["priority:P1"], priorityOptions).option.id, "p1");
  assert.equal(resolvePriorityOption([{ name: "priority:P2" }], priorityOptions).option.id, "p2");
  assert.equal(resolvePriorityOption([{ name: "priority:P3" }], priorityOptions).option.id, "p3");
  // Vastaa täsmälleen käyttäjän Aiheseurain-Projectissa olevia vaihtoehtoja.
  assert.equal(resolvePriorityOption(["priority:P1"], [
    { name: "P0 Kriittinen", id: "e8877887" },
    { name: "P1 Korkea", id: "4eb95e26" },
    { name: "P2 Normaali", id: "024b8b15" },
    { name: "P3 Matala", id: "6c5a768d" }
  ]).option.id, "4eb95e26");
});

test("hylkää puuttuvan, ristiriitaisen tai tuntemattoman prioriteettilabelin", async () => {
  const { resolvePriorityOption } = await import("../.github/scripts/sync_project_status.mjs");
  const options = [{ name: "P1", id: "p1" }];
  assert.throws(() => resolvePriorityOption([], options), /täsmälleen yksi/);
  assert.throws(() => resolvePriorityOption(["priority:P1", "priority:P2"], options), /täsmälleen yksi/);
  assert.throws(() => resolvePriorityOption(["priority:P9"], options), /Tuntematon prioriteettilabel/);
  assert.throws(() => resolvePriorityOption(["priority:P1"], []), /täsmälleen yksi vaihtoehto/);
});

test("löytää Projectin Priority-kentän ja sen vaihtoehdot kentän nimen perusteella", async () => {
  const { findProjectSingleSelectField } = await import("../.github/scripts/sync_project_status.mjs");
  const fetchMock = async (url, options) => {
    assert.equal(url, "https://api.github.com/graphql");
    const request = JSON.parse(options.body);
    assert.match(request.query, /ProjectV2SingleSelectField/);
    return {
      ok: true, status: 200,
      json: async () => ({ data: { node: { fields: { nodes: [
        { id: "F_priority", name: "Priority", options: [{ id: "p1", name: "P1" }] }
      ] } } } })
    };
  };
  const field = await findProjectSingleSelectField({
    token: "test", projectId: "P_test", fieldName: "Priority", fetchImpl: fetchMock
  });
  assert.equal(field.id, "F_priority");
  assert.equal(field.options[0].id, "p1");
});
