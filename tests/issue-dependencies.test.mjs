import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { readFileSync } from "node:fs";
import {
  parseDependencyRequest,
  hasDependencyCycle,
  applyDependencyRequest,
  dispatchPublication
} from "../.github/scripts/sync_issue_dependencies.mjs";

const marker = (json) => `<!-- aiheseurain-dependency-request
${JSON.stringify(json)}
-->`;

test("tunnistaa yksiselitteisen lisäyspyynnön", () => {
  const parsed = parseDependencyRequest(`Kuvaus\n\n${marker({ blocked_by: [26, 27] })}`, 79);
  assert.deepEqual(parsed.additions, [26, 27]);
  assert.deepEqual(parsed.removals, []);
});

test("tunnistaa erikseen pyydetyn poiston", () => {
  const parsed = parseDependencyRequest(marker({ remove_blocked_by: [26] }), 79);
  assert.deepEqual(parsed.removals, [26]);
});

test("ei tee mitään ilman pyyntölohkoa", () => {
  assert.equal(parseDependencyRequest("Tavallinen viittaus tikettiin #26.", 79), null);
});

test("hylkää epäselvät, virheelliset ja itseensä viittaavat pyynnöt", () => {
  for (const value of [
    { blocked_by: [79] },
    { blocked_by: [26, 26] },
    { blocked_by: ["26"] },
    { blocked_by: [26], remove_blocked_by: [26] },
    { blocked_by: [] },
    { blocked_by: [26], extra: true }
  ]) {
    assert.throws(() => parseDependencyRequest(marker(value), 79));
  }
  assert.throws(() => parseDependencyRequest(
    "<!-- aiheseurain-dependency-request {rikki} -->", 79));
});

test("havaitsee suoran ja monivaiheisen riippuvuussyklin", async () => {
  const graph = new Map([[12, [13]], [13, [14]], [14, []]]);
  const fetchBlockedBy = async (number) => (graph.get(number) ?? []).map((n) => ({ number: n }));
  assert.equal(await hasDependencyCycle(12, 14, fetchBlockedBy), true);
  assert.equal(await hasDependencyCycle(14, 12, fetchBlockedBy), false);
});

test("lisää uuden riippuvuuden vain kerran ja jättää olemassa olevan ennalleen", async () => {
  const graph = new Map([[79, [{ number: 26 }]], [26, []], [27, []]]);
  const added = [];
  const result = await applyDependencyRequest({
    targetIssue: { id: 790, number: 79 },
    additions: [26, 27],
    removals: [],
    fetchIssue: async (number) => ({ id: number * 10, number }),
    fetchBlockedBy: async (number) => graph.get(number) ?? [],
    addDependency: async (number, id) => {
      added.push([number, id]);
      graph.get(number).push({ number: id / 10 });
    },
    removeDependency: async () => assert.fail("Poistoa ei pyydetty")
  });
  assert.deepEqual(result.alreadyPresent, [26]);
  assert.deepEqual(result.added, [27]);
  assert.deepEqual(added, [[79, 270]]);
});

test("poistaa vain nimenomaisesti pyydetyn olemassa olevan riippuvuuden", async () => {
  const graph = new Map([[79, [{ number: 26 }]]]);
  const removed = [];
  const result = await applyDependencyRequest({
    targetIssue: { id: 790, number: 79 },
    additions: [],
    removals: [26, 27],
    fetchIssue: async (number) => ({ id: number * 10, number }),
    fetchBlockedBy: async (number) => graph.get(number) ?? [],
    addDependency: async () => assert.fail("Lisäystä ei pyydetty"),
    removeDependency: async (number, id) => {
      removed.push([number, id]);
      graph.set(number, graph.get(number).filter((item) => item.number !== id / 10));
    }
  });
  assert.deepEqual(result.removed, [26]);
  assert.deepEqual(result.alreadyAbsent, [27]);
  assert.deepEqual(removed, [[79, 260]]);
});

test("hylkää riippuvuussyklin ennen kirjoitusta", async () => {
  const graph = new Map([[79, []], [26, [{ number: 79 }]]]);
  let writes = 0;
  await assert.rejects(() => applyDependencyRequest({
    targetIssue: { id: 790, number: 79 },
    additions: [26],
    removals: [],
    fetchIssue: async (number) => ({ id: number * 10, number }),
    fetchBlockedBy: async (number) => graph.get(number) ?? [],
    addDependency: async () => { writes += 1; },
    removeDependency: async () => {}
  }), /syklin/);
  assert.equal(writes, 0);
});

test("hylkää puuttuvan tiketin ja pull requestin", async () => {
  const common = {
    targetIssue: { id: 790, number: 79 },
    additions: [26],
    removals: [],
    fetchBlockedBy: async () => [],
    addDependency: async () => assert.fail("Kirjoitusta ei saa tehdä"),
    removeDependency: async () => {}
  };
  await assert.rejects(() => applyDependencyRequest({
    ...common, fetchIssue: async () => null
  }), /ei ole olemassa/);
  await assert.rejects(() => applyDependencyRequest({
    ...common, fetchIssue: async () => ({ id: 260, number: 26, pull_request: {} })
  }), /ei ole olemassa/);
});


test("julkaisutyönkulku varmistetaan päivittäin eikä 15 minuutin välein", async () => {
  const workflow = readFileSync(new URL("../.github/workflows/publish-pages.yml", import.meta.url), "utf8");
  assert.match(workflow, /cron: "17 3 \\* \\* \\*"/);
  assert.doesNotMatch(workflow, /cron: "\\*\\/15 \\* \\* \\* \\*"/);
});

test("onnistunut riippuvuuksien välitys käynnistää Pages-julkaisun workflow_dispatchilla", async () => {
  const workflow = readFileSync(new URL("../.github/workflows/sync-issue-dependencies.yml", import.meta.url), "utf8");
  const scriptSource = readFileSync(new URL("../.github/scripts/sync_issue_dependencies.mjs", import.meta.url), "utf8");
  assert.match(workflow, /actions: write/);
  assert.ok(scriptSource.includes("/actions/workflows/publish-pages.yml/dispatches"));
  let request;
  await dispatchPublication({
    owner: "mikknikk", repo: "aiheseurain", token: "test-token",
    fetchImpl: async (url, options) => {
      request = { url, options };
      return { ok: true, status: 204 };
    }
  });
  assert.equal(request.url, "https://api.github.com/repos/mikknikk/aiheseurain/actions/workflows/publish-pages.yml/dispatches");
  assert.equal(request.options.method, "POST");
  assert.deepEqual(JSON.parse(request.options.body), { ref: "main" });
});
