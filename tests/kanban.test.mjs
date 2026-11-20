import test from "node:test";
import assert from "node:assert/strict";
import {
  STATUS_COLUMNS, normalizeIssue, filterIssues, fetchPublishedDataset,
  buildDependencyGraph, summarizePredecessors
} from "../assets/js/kanban.js";

const makeIssue = (number, extra = {}) => ({
  number, title: "Tehtävä " + number,
  html_url: "https://github.com/mikknikk/aiheseurain/issues/" + number,
  state: "open",
  labels: [
    { name: "status:ready-for-development" },
    { name: "priority:P1" },
    { name: "component:kehitysjono" }
  ],
  updated_at: "2026-11-20T10:00:00Z",
  ...extra
});

test("Kehitysjonon tilasarakkeet vastaavat uusia status-labeleita", () => {
  assert.deepEqual(STATUS_COLUMNS.map(x => x.issueLabel), [
    "status:backlog", "status:ready-for-development", "status:in-progress", "status:done"
  ]);
});

test("issue luokitellaan komponentti-, prioriteetti- ja status-labeleilla", () => {
  const issue = normalizeIssue(makeIssue(10));
  assert.equal(issue.status, "ready");
  assert.equal(issue.priority, "P1");
  assert.equal(issue.component, "component:kehitysjono");
  assert.equal(issue.componentName, "kehitysjono");
});

test("ristiriitaisia labeleita ei arvata ja suljettu issue on valmis", () => {
  const ambiguous = normalizeIssue(makeIssue(10, {
    labels: [{ name: "status:backlog" }, { name: "status:in-progress" }, { name: "priority:P1" }]
  }));
  assert.equal(ambiguous.status, null);
  const closed = normalizeIssue(makeIssue(11, { state: "closed", labels: [] }));
  assert.equal(closed.status, "done");
});

test("haku ja prioriteetti- sekä komponenttisuodattimet toimivat yhdessä", () => {
  const issues = [
    normalizeIssue(makeIssue(10)),
    normalizeIssue(makeIssue(11, {
      title: "RSS-lukijan tehtävä",
      labels: [{ name: "status:backlog" }, { name: "priority:P2" }, { name: "component:lukija" }]
    }))
  ];
  assert.deepEqual(filterIssues(issues, {
    query: "RSS", priority: "P2", component: "component:lukija"
  }).map(x => x.number), [11]);
});

test("riippuvuusverkon käänteinen blocking-suunta johdetaan blocked_by-tiedosta", () => {
  const blocker = normalizeIssue(makeIssue(10));
  const blocked = normalizeIssue(makeIssue(11));
  const graph = buildDependencyGraph([blocker, blocked], [
    { issueNumber: 10, blockedBy: [] },
    { issueNumber: 11, blockedBy: [makeIssue(10)] }
  ]);
  assert.deepEqual(graph.byIssue[11].blockedBy.map(x => x.number), [10]);
  assert.deepEqual(graph.byIssue[10].blocking.map(x => x.number), [11]);
  assert.equal(graph.complete, true);
});

test("osittaista riippuvuusaineistoa ei esitetä täydellisenä", () => {
  const graph = buildDependencyGraph([normalizeIssue(makeIssue(10))], [], false);
  assert.equal(graph.complete, false);
  assert.match(summarizePredecessors([], false), /vähintään/);
});

test("julkaistu aineisto edellyttää myös täyden täsmäytyksen aikaleimaa", async () => {
  const dataset = {
    schema_version: 1, status: "complete",
    generated_at: "2026-11-20T10:00:00Z",
    full_sync_at: "2026-11-20T09:00:00Z",
    issue_count: 1, dependency_relation_count: 0,
    issues: [makeIssue(10)],
    dependencies: [{ issueNumber: 10, blockedBy: [] }]
  };
  const result = await fetchPublishedDataset(async () => ({
    ok: true, json: async () => dataset
  }), "/data/kehitysjono.json");
  assert.equal(result.full_sync_at, dataset.full_sync_at);
  await assert.rejects(fetchPublishedDataset(async () => ({
    ok: true, json: async () => ({ ...dataset, full_sync_at: undefined })
  }), "/data/kehitysjono.json"), /virheellinen tai puutteellinen/);
});
