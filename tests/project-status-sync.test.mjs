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
