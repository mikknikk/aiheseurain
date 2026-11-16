import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { classifyFreshness, latestRotationTask, validateStateShape, TASK_ORDER } from "../assets/js/valvomo.js";

test("tuoreus erottaa tuoreen, vanhentuneen ja tuntemattoman ajan", () => {
  const now = Date.parse("2026-11-16T20:00:00+02:00");
  assert.equal(classifyFreshness("2026-11-16T19:00:00+02:00", 36, now).key, "good");
  assert.equal(classifyFreshness("2026-11-14T07:00:00+02:00", 36, now).key, "warning");
  assert.equal(classifyFreshness(null, 36, now).key, "unknown");
  assert.equal(classifyFreshness("not-a-date", 36, now).key, "unknown");
});

test("viimeisin aiheajo valitaan onnistumisajan perusteella", () => {
  const tasks = {
    tolkien: { last_successful_check: "2026-11-16T18:00:00+02:00" },
    taylor_swift: { last_successful_check: null },
    gurmeet_ram_rahim_singh: { last_successful_check: "2026-11-15T18:00:00+02:00" }
  };
  assert.equal(latestRotationTask(tasks).id, "tolkien");
  assert.equal(latestRotationTask({}), null);
});

test("seurantatiedon rakenteen tarkistus edellyttää kaikkia yhdeksää kiertotehtävää", () => {
  const state = {
    schema_version: 1,
    updated_at: "2026-11-16T18:00:00+02:00",
    rotation: { tasks: Object.fromEntries(TASK_ORDER.map((id) => [id, {}])) },
    separate_screening_watch: {},
    automation_instructions: {},
    quality_check_instructions: {}
  };
  assert.equal(validateStateShape(state), true);
  delete state.rotation.tasks.sompote_sands;
  assert.equal(validateStateShape(state), false);
});

test("Valvomon sivupohja sisältää saavutettavat perusrakenteet", () => {
  const layout = readFileSync(new URL("../_layouts/site.html", import.meta.url), "utf8");
  const page = readFileSync(new URL("../index.html", import.meta.url), "utf8");
  assert.match(layout, /<html lang="fi">/);
  assert.match(layout, /href="#main"/);
  assert.match(layout, /<nav aria-label="Päänavigaatio">/);
  assert.match(layout, /<main id="main"/);
  assert.match(layout, /<footer/);
  assert.match(page, /id="rotation-list"/);
  assert.match(page, /id="actions-content"/);
});
