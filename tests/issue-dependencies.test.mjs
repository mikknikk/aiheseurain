import test from "node:test";
import assert from "node:assert/strict";
import {
  parseDependencyRequest, hasDependencyCycle, applyDependencyRequest,
  dispatchDatasetRefresh
} from "../.github/scripts/sync_issue_dependencies.mjs";

const marker = (value) => `<!-- aiheseurain-dependency-request
${JSON.stringify(value)}
-->`;

test("tunnistaa vain eksplisiittisen riippuvuuspyyntölohkon", () => {
  const parsed = parseDependencyRequest("Kuvaus\n\n" + marker({ blocked_by: [12, 13] }), 99);
  assert.deepEqual(parsed.additions, [12, 13]);
  assert.deepEqual(parsed.removals, []);
  assert.equal(parseDependencyRequest("Tavallinen maininta tiketistä #12", 99), null);
});

test("tunnistaa erikseen pyydetyn riippuvuuden poiston", () => {
  const parsed = parseDependencyRequest(marker({ remove_blocked_by: [12] }), 99);
  assert.deepEqual(parsed.removals, [12]);
});

test("hylkää epäselvän tai vaarallisen pyyntölohkon", () => {
  for (const request of [
    { blocked_by: [99] }, { blocked_by: [12, 12] },
    { blocked_by: ["12"] }, { blocked_by: [12], remove_blocked_by: [12] },
    { blocked_by: [] }, { blocked_by: [12], extra: true }
  ]) assert.throws(() => parseDependencyRequest(marker(request), 99));
  assert.throws(() => parseDependencyRequest(marker({ blocked_by: [12] }) + marker({ blocked_by: [13] }), 99));
});

test("havaitsee riippuvuussyklin ennen kirjoitusta", async () => {
  const graph = new Map([[12, [{ number: 11 }]], [11, [{ number: 99 }]], [99, []]]);
  assert.equal(await hasDependencyCycle(12, 99, async n => graph.get(n) || []), true);
  assert.equal(await hasDependencyCycle(11, 12, async n => graph.get(n) || []), false);
});

test("lisäys ja poisto ovat idempotentteja", async () => {
  const graph = new Map([[99, [{ number: 12 }]]]);
  const added = [];
  const removed = [];
  const result = await applyDependencyRequest({
    targetIssue: { id: 990, number: 99 },
    additions: [12, 13], removals: [12],
    fetchIssue: async number => ({ id: number * 10, number }),
    fetchBlockedBy: async number => graph.get(number) || [],
    addDependency: async (number, id) => { added.push([number, id]); graph.set(number, [...(graph.get(number) || []), { number: id / 10 }]); },
    removeDependency: async (number, id) => { removed.push([number, id]); graph.set(number, (graph.get(number) || []).filter(x => x.number !== id / 10)); }
  });
  assert.deepEqual(result.alreadyPresent, [12]);
  assert.deepEqual(result.added, [13]);
  assert.deepEqual(result.removed, [12]);
  assert.deepEqual(added, [[99, 130]]);
  assert.deepEqual(removed, [[99, 120]]);
});

test("hylkää puuttuvan issue-tiketin ja pull requestin", async () => {
  const common = {
    targetIssue: { id: 990, number: 99 }, additions: [12], removals: [],
    fetchBlockedBy: async () => [], addDependency: async () => assert.fail(),
    removeDependency: async () => {}
  };
  await assert.rejects(() => applyDependencyRequest({ ...common, fetchIssue: async () => null }), /ei ole olemassa/);
  await assert.rejects(() => applyDependencyRequest({
    ...common, fetchIssue: async () => ({ id: 120, number: 12, pull_request: {} })
  }), /ei ole olemassa/);
});

test("onnistunut riippuvuusmuutos käynnistää vain kohde-issuen välimuistipäivityksen", async () => {
  let request;
  await dispatchDatasetRefresh({
    owner: "mikknikk", repo: "aiheseurain", token: "test-token", issueNumber: 99,
    fetchImpl: async (url, options) => { request = { url, options }; return { ok: true, status: 204 }; }
  });
  assert.equal(request.url, "https://api.github.com/repos/mikknikk/aiheseurain/actions/workflows/update-kanban-data.yml/dispatches");
  assert.equal(request.options.method, "POST");
  assert.deepEqual(JSON.parse(request.options.body), { ref: "main", inputs: { issue_number: "99" } });
});
