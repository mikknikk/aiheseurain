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
