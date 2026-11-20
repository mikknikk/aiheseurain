import test from "node:test";
import assert from "node:assert/strict";
import { buildDataset, fetchAllIssues, fetchAllDependencies } from "../scripts/build_kanban_data.mjs";

const makeIssue = (number, extra = {}) => ({
  number, title: "Tehtävä " + number,
  html_url: "https://github.com/mikknikk/aiheseurain/issues/" + number,
  state: "open", labels: [{ name: "tila:ready" }],
  updated_at: "2026-11-17T10:00:00Z", ...extra
});

function response(items, status = 200) {
  return { ok: status >= 200 && status < 300, status, json: async () => items };
}

test("kaikki issue-sivut haetaan ja pull requestit suodatetaan pois", async () => {
  const calls = [];
  const fetchMock = async (url) => {
    calls.push(String(url));
    const page = Number(new URL(url).searchParams.get("page"));
    if (page === 1) return response([
      ...Array.from({ length: 100 }, (_, index) => makeIssue(index + 1)),
      { ...makeIssue(101), pull_request: { url: "https://api.github.com/pulls/101" } }
    ]);
    return response([makeIssue(102)]);
  };
  const issues = await fetchAllIssues("mikknikk", "aiheseurain", "test-token", fetchMock);
  assert.equal(calls.length, 2);
  assert.equal(issues.length, 101);
  assert.equal(issues.at(-1).number, 102);
});

test("riippuvuuksien kaikki sivut haetaan ja sivutus säilyy", async () => {
  const calls = [];
  const fetchMock = async (url) => {
    calls.push(String(url));
    const page = Number(new URL(url).searchParams.get("page"));
    return page === 1
      ? response(Array.from({ length: 100 }, (_, index) => makeIssue(index + 200)))
      : response([makeIssue(400)]);
  };
  const result = await fetchAllDependencies("mikknikk", "aiheseurain", [
    makeIssue(12)
  ], "test-token", fetchMock);
  assert.equal(calls.length, 2);
  assert.equal(result[0].blockedBy.length, 101);
});

test("julkaistava aineisto sisältää täydellisyystilan, aikaleiman ja riippuvuudet", async () => {
  const calls = [];
  const fetchMock = async (url) => {
    calls.push(String(url));
    const parsed = new URL(url);
    if (parsed.pathname.endsWith("/issues")) return response([makeIssue(12), makeIssue(13)]);
    if (parsed.pathname.endsWith("/issues/12/dependencies/blocked_by")) return response([makeIssue(11)]);
    if (parsed.pathname.endsWith("/issues/13/dependencies/blocked_by")) return response([]);
    throw new Error("Odottamaton API-polku: " + parsed.pathname);
  };
  const dataset = await buildDataset({
    owner: "mikknikk", repo: "aiheseurain", token: "test-token",
    fetchImpl: fetchMock, now: new Date("2026-11-17T12:00:00Z")
  });
  assert.equal(dataset.schema_version, 1);
  assert.equal(dataset.status, "complete");
  assert.equal(dataset.generated_at, "2026-11-17T12:00:00.000Z");
  assert.equal(dataset.issue_count, 2);
  assert.equal(dataset.dependency_relation_count, 1);
  assert.equal(dataset.dependencies.length, 2);
  assert.equal(calls.length, 3);
});

test("riippuvuushakuvirhe keskeyttää muodostuksen eikä tuota osittaista aineistoa", async () => {
  const fetchMock = async (url) => {
    const parsed = new URL(url);
    if (parsed.pathname.endsWith("/issues")) return response([makeIssue(12)]);
    return response({ message: "rate limit" }, 403);
  };
  await assert.rejects(
    buildDataset({ owner: "mikknikk", repo: "aiheseurain", token: "test-token", fetchImpl: fetchMock }),
    /rajoitti/
  );
});
