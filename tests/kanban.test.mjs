import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { filterIssues, normalizeIssue, normalizeIssues, STATUS_COLUMNS, fetchPublishedDataset, buildDependencyGraph } from "../assets/js/kanban.js";

const makeIssue = (overrides = {}) => ({
  number: 12,
  title: "Testitehtävä",
  html_url: "https://github.com/mikknikk/aiheseurain/issues/12",
  state: "open",
  labels: [{ name: "tila:ready" }, { name: "P1" }, { name: "aihe:valvomo" }],
  updated_at: "2026-11-16T12:00:00Z",
  ...overrides
});

test("tilasarakkeet noudattavat sovittua järjestystä", () => {
  assert.deepEqual(STATUS_COLUMNS.map((column) => column.id),
    ["backlog", "ready", "in-progress", "blocked", "done"]);
});

test("issue luokitellaan tila-, prioriteetti- ja aihealue-labelien perusteella", () => {
  const issue = normalizeIssue(makeIssue());
  assert.equal(issue.status, "ready");
  assert.equal(issue.priority, "P1");
  assert.equal(issue.area, "aihe:valvomo");
  assert.equal(issue.areaName, "valvomo");
});

test("suljettu issue näkyy valmiina vanhasta tilalabelista huolimatta", () => {
  const issue = normalizeIssue(makeIssue({ state: "closed", labels: [{ name: "tila:blocked" }] }));
  assert.equal(issue.status, "done");
});

test("ristiriitaisia tila- tai prioriteettilabeleita ei arvata", () => {
  const issue = normalizeIssue(makeIssue({
    labels: [{ name: "tila:ready" }, { name: "tila:blocked" }, { name: "P1" }, { name: "P2" }]
  }));
  assert.equal(issue.status, null);
  assert.equal(issue.priority, null);
});

test("pull requestit suodatetaan pois ja tavalliset issuet säilyvät", () => {
  const issues = normalizeIssues([makeIssue(), makeIssue({
    number: 13,
    pull_request: { url: "https://api.github.com/..." }
  })]);
  assert.equal(issues.length, 1);
  assert.equal(issues[0].number, 12);
});

test("haku ja prioriteetti- sekä aihealue-suodattimet toimivat yhdessä", () => {
  const issues = [
    normalizeIssue(makeIssue()),
    normalizeIssue(makeIssue({
      number: 13, title: "RSS-lukijan jatkokehitys",
      labels: [{ name: "tila:backlog" }, { name: "P2" }, { name: "aihe:rss" }]
    }))
  ];
  assert.deepEqual(filterIssues(issues, { query: "RSS", priority: "P2", area: "aihe:rss" })
    .map((issue) => issue.number), [13]);
  assert.deepEqual(filterIssues(issues, { query: "12" }).map((issue) => issue.number), [12]);
});

test("Kehitysjono-sivu ja navigaatio tarjoavat saavutettavan vain luku -osion", () => {
  const page = readFileSync(new URL("../kehitysjono/index.html", import.meta.url), "utf8");
  const header = readFileSync(new URL("../_includes/site-header.html", import.meta.url), "utf8");
  const layout = readFileSync(new URL("../_layouts/site.html", import.meta.url), "utf8");
  const script = readFileSync(new URL("../assets/js/kanban.js", import.meta.url), "utf8");
  assert.match(page, /section: kehitysjono/);
  assert.match(page, /aria-labelledby="filters-title"/);
  assert.match(page, /aria-pressed="true"/);
  assert.match(page, /kanban-table/);
  assert.match(page, /kanban-refresh/);
  assert.match(page, /kanban-dependency-details/);
  assert.match(script, /dependencies\/blocked_by/);
  assert.match(script, /data-issue-number/);
  assert.doesNotMatch(script, /api\\.github\\.com\\/repos|dependencies\\/blocked_by/);
  assert.match(header, /\/kehitysjono\//);
  assert.match(header, /page\.section == "kehitysjono"/);
  assert.match(layout, /assets\/js\/kanban\.js/);
  assert.doesNotMatch(script, /Authorization\s*:|Bearer\s+[A-Za-z0-9_-]+|method\s*:\s*[\"'](?:POST|PATCH|DELETE)[\"']/i);
});


test("julkaistun täydellisen aineiston haku hyväksyy versionoidun JSONin", async () => {
  const dataset = {
    schema_version: 1, status: "complete", generated_at: "2026-11-17T10:00:00.000Z",
    issue_count: 1, issues: [makeIssue()], dependencies: [{ issueNumber: 12, blockedBy: [] }]
  };
  const calls = [];
  const result = await fetchPublishedDataset(async (url, options) => {
    calls.push({ url, options });
    return { ok: true, json: async () => dataset };
  }, "/data/kehitysjono.json");
  assert.equal(result.issue_count, 1);
  assert.equal(calls.length, 1);
  assert.equal(calls[0].url, "/data/kehitysjono.json");
  assert.equal(calls[0].options.cache, "no-store");
});

test("puutteellista tai väärin versioitua julkaistua aineistoa ei hyväksytä", async () => {
  const incomplete = {
    schema_version: 1, status: "partial", generated_at: "2026-11-17T10:00:00.000Z",
    issue_count: 0, issues: [], dependencies: []
  };
  await assert.rejects(
    fetchPublishedDataset(async () => ({ ok: true, json: async () => incomplete }), "/data.json"),
    /virheellinen tai puutteellinen/
  );
});

test("riippuvuusverkko johtaa käänteiset estävät suhteet samasta GitHub-tiedosta", () => {
  const first = normalizeIssue(makeIssue({ number: 12, title: "Edeltävä työ" }));
  const second = normalizeIssue(makeIssue({ number: 13, title: "Seuraava työ" }));
  const graph = buildDependencyGraph([first, second], [
    { issueNumber: 13, blockedBy: [{ number: 12, title: "Edeltävä työ",
      html_url: first.url, state: "open", labels: [{ name: "tila:ready" }] }] }
  ]);
  assert.deepEqual(graph.byIssue[13].blockedBy.map((issue) => issue.number), [12]);
  assert.deepEqual(graph.byIssue[12].blocking.map((issue) => issue.number), [13]);
  assert.equal(graph.complete, true);
});

test("osittaiset riippuvuustiedot säilyvät osittaisina", () => {
  const issue = normalizeIssue(makeIssue());
  const graph = buildDependencyGraph([issue], [], false);
  assert.equal(graph.complete, false);
  assert.deepEqual(graph.byIssue[12].blockedBy, []);
});


