import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { filterIssues, normalizeIssue, normalizeIssues, STATUS_COLUMNS, fetchAllIssues } from "../assets/js/kanban.js";

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

test("API-haku hakee seuraavan sivun, jos ensimmäinen sivu on täynnä", async () => {
  const calls = [];
  const fetchMock = async (url) => {
    calls.push(String(url));
    const page = new URL(url).searchParams.get("page");
    const items = page === "1"
      ? Array.from({ length: 100 }, (_, index) => makeIssue({ number: index + 1 }))
      : [makeIssue({ number: 101 })];
    return { ok: true, json: async () => items };
  };
  const issues = await fetchAllIssues(fetchMock);
  assert.equal(calls.length, 2);
  assert.equal(issues.length, 101);
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
  assert.match(header, /\/kehitysjono\//);
  assert.match(header, /page\.section == "kehitysjono"/);
  assert.match(layout, /assets\/js\/kanban\.js/);
  assert.doesNotMatch(script, /POST|PATCH|DELETE|Authorization|token/i);
});
