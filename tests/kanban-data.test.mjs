import test from "node:test";
import assert from "node:assert/strict";
import {
  publicIssue, buildIncrementalDataset, buildFullDataset, eventNameIsFullSync
} from "../scripts/build_kanban_data.mjs";

const issue = (number, extra = {}) => ({
  number, title: "Tehtävä " + number,
  html_url: "https://github.com/mikknikk/aiheseurain/issues/" + number,
  state: "open", labels: [{ name: "component:kehitysjono" }],
  updated_at: "2026-11-20T10:00:00Z", ...extra
});

const previous = () => ({
  schema_version: 1, generated_at: "2026-11-19T00:00:00.000Z",
  full_sync_at: "2026-11-18T00:00:00.000Z", status: "complete",
  issue_count: 2, dependency_relation_count: 1,
  issues: [issue(1), issue(2)],
  dependencies: [
    { issueNumber: 1, blockedBy: [] },
    { issueNumber: 2, blockedBy: [issue(1)] }
  ]
});

test("julkiseen aineistoon kopioidaan vain käyttöliittymän tarvitsemat kentät", () => {
  const result = publicIssue({ ...issue(4), body: "salainen ylimääräinen sisältö" });
  assert.equal(result.number, 4);
  assert.equal("body" in result, false);
  assert.deepEqual(result.labels, [{ name: "component:kehitysjono" }]);
});

test("inkrementaalinen päivitys muuttaa vain valitun tiketin ja sen riippuvuudet", () => {
  const result = buildIncrementalDataset({
    previous: previous(),
    issue: issue(2, { title: "Päivitetty tehtävä" }),
    dependencies: [issue(1)],
    now: new Date("2026-11-20T12:00:00Z")
  });
  assert.equal(result.issue_count, 2);
  assert.equal(result.issues.find((item) => item.number === 2).title, "Päivitetty tehtävä");
  assert.deepEqual(result.dependencies.find((item) => item.issueNumber === 2).blockedBy.map(x => x.number), [1]);
  assert.equal(result.full_sync_at, "2026-11-18T00:00:00.000Z");
  assert.equal(result.generated_at, "2026-11-20T12:00:00.000Z");
});

test("riippuvuuksien poistaminen päivittyy ilman koko aineiston hakua", () => {
  const result = buildIncrementalDataset({
    previous: previous(), issue: issue(2), dependencies: [],
    now: new Date("2026-11-20T12:00:00Z")
  });
  assert.equal(result.dependency_relation_count, 0);
  assert.deepEqual(result.dependencies.find((item) => item.issueNumber === 2).blockedBy, []);
});

test("poistettu issue poistuu myös muiden tikettien riippuvuuslistoilta", () => {
  const result = buildIncrementalDataset({
    previous: previous(), issue: issue(1), deleted: true,
    now: new Date("2026-11-20T12:00:00Z")
  });
  assert.deepEqual(result.issues.map(x => x.number), [2]);
  assert.deepEqual(result.dependencies, [{ issueNumber: 2, blockedBy: [] }]);
});

test("virheellinen tai puuttuva riippuvuustieto estää välimuistin muodostamisen", () => {
  assert.throws(() => buildIncrementalDataset({
    previous: previous(), issue: issue(2), dependencies: null
  }), /riippuvuuksia ei saatu/);
});

test("täysi täsmäytys käynnistyy ajastuksessa, manuaalisesti ja koodimuutoksissa", () => {
  assert.equal(eventNameIsFullSync({}, "schedule"), true);
  assert.equal(eventNameIsFullSync({}, "push"), true);
  assert.equal(eventNameIsFullSync({}, "workflow_dispatch"), true);
  assert.equal(eventNameIsFullSync({ inputs: { issue_number: "12" } }, "workflow_dispatch"), false);
  assert.equal(eventNameIsFullSync({ action: "edited" }, "issues"), false);
});

test("ensimmäinen täysi muodostus hakee issue-listan ja riippuvuudet", async () => {
  const calls = [];
  const fetchMock = async (url) => {
    calls.push(String(url));
    const parsed = new URL(url);
    if (parsed.pathname.endsWith("/issues")) return {
      ok: true, status: 200, json: async () => [issue(7)]
    };
    if (parsed.pathname.endsWith("/issues/7/dependencies/blocked_by")) return {
      ok: true, status: 200, json: async () => []
    };
    throw new Error("Odottamaton API-polku: " + parsed.pathname);
  };
  const result = await buildFullDataset({
    owner: "mikknikk", repo: "aiheseurain", token: "test-token",
    fetchImpl: fetchMock, now: new Date("2026-11-20T12:00:00Z")
  });
  assert.equal(calls.length, 2);
  assert.equal(result.status, "complete");
  assert.equal(result.issue_count, 1);
  assert.equal(result.full_sync_at, result.generated_at);
});
