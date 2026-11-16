import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { classifyFreshness, latestRotationTask, validateStateShape, TASK_ORDER, loadDashboard } from "../assets/js/valvomo.js";

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
    rotation: { next_task: "taylor_swift", tasks: Object.fromEntries(TASK_ORDER.map((id) => [id, {}])) },
    separate_screening_watch: {},
    automation_instructions: {},
    quality_check_instructions: {}
  };
  assert.equal(validateStateShape(state), true);
  delete state.rotation.tasks.sompote_sands;
  assert.equal(validateStateShape(state), false);
  state.rotation.tasks.sompote_sands = {};
  state.rotation.next_task = "not-a-task";
  assert.equal(validateStateShape(state), false);
});

test("Valvomon sivupohja sisältää saavutettavat perusrakenteet", () => {
  const layout = readFileSync(new URL("../_layouts/site.html", import.meta.url), "utf8");
  const header = readFileSync(new URL("../_includes/site-header.html", import.meta.url), "utf8");
  const footer = readFileSync(new URL("../_includes/site-footer.html", import.meta.url), "utf8");
  const page = readFileSync(new URL("../valvomo/index.html", import.meta.url), "utf8");
  const home = readFileSync(new URL("../index.html", import.meta.url), "utf8");
  const script = readFileSync(new URL("../assets/js/valvomo.js", import.meta.url), "utf8");
  assert.match(layout, /<html lang="fi">/);
  assert.match(layout, /href="#main"/);
  assert.match(header, /<nav aria-label="Päänavigaatio">/);
  assert.match(layout, /<main id="main"/);
  assert.match(footer, /<footer/);
  assert.match(page, /id="rotation-list"/);
  assert.match(page, /id="actions-content"/);
  assert.match(page, /section: valvomo/);
  assert.match(home, /section: home/);
  assert.match(home, /\/valvomo\//);
  assert.match(header, /\/valvomo\//);
  assert.match(script, /new URL\("\.\.\/\.\.\/data\/seurantatila\.json", import\.meta\.url\)/);
  assert.match(script, /new URL\("\.\.\/\.\.\/data\/lahdetarkistukset\.json", import\.meta\.url\)/);
});

function fakeDom() {
  const elements = new Map();
  return {
    elements,
    getElementById(id) {
      if (!elements.has(id)) {
        elements.set(id, {
          textContent: "",
          innerHTML: "",
          className: "",
          disabled: false,
          replaceChildren() { this.innerHTML = ""; },
          insertAdjacentHTML(_position, html) { this.innerHTML += html; }
        });
      }
      return elements.get(id);
    }
  };
}

function sampleState() {
  const tasks = Object.fromEntries(TASK_ORDER.map((id) => [id, { last_result: "not_recorded" }]));
  tasks.tolkien = {
    name: "J. R. R. Tolkien",
    last_result: "published",
    last_successful_check: "2026-11-16T18:00:00+02:00",
    last_period_start: "2026-11-15T00:00:00+02:00",
    last_period_end: "2026-11-16T18:00:00+02:00",
    published_items: 2,
    sources_checked: 8
  };
  return {
    schema_version: 1,
    updated_at: "2026-11-16T18:00:00+02:00",
    rotation: { next_task: "taylor_swift", tasks },
    automation_instructions: { current_version: "1.2.1", last_successful_run_version: "1.0.4" },
    separate_screening_watch: {
      last_result: "success",
      last_successful_check: "2026-11-16T17:00:00+02:00",
      automation_instructions: { current_version: "1.4.1", last_successful_run_version: "1.0.0" }
    },
    quality_check_instructions: {
      current_version: "1.0.4",
      last_successful_run_version: "1.0.1",
      last_successful_run_at: "2026-11-16T19:00:00+02:00",
      startup_prompt_id: "quality-check-test"
    }
  };
}

test("Valvomo näyttää kolme automaatiota erillään ja ilmoittaa ohjeversioiden eroista", async () => {
  const oldDocument = globalThis.document;
  const oldFetch = globalThis.fetch;
  const dom = fakeDom();
  const state = sampleState();
  globalThis.document = dom;
  globalThis.fetch = async (url) => ({
    ok: true,
    async json() {
      if (url.includes("seurantatila")) return state;
      return {
        runs: [{
          task_id: "tolkien",
          status: "complete",
          checked_source_ids: ["source-a"],
          unchecked_sources: [{ source_id: "source-b", reason: "Palvelin ei vastannut" }]
        }]
      };
    }
  });
  try {
    await loadDashboard();
    assert.match(dom.getElementById("main-status").textContent, /aiempaa ohjeversiota/);
    assert.match(dom.getElementById("screening-status").textContent, /aiempaa ohjeversiota/);
    assert.match(dom.getElementById("quality-status").textContent, /vanhempaa ohjeversiota/);
    assert.match(dom.getElementById("main-details").innerHTML, /Ajovaiheet/);
    assert.match(dom.getElementById("rotation-list").innerHTML, /Taylor Swift/);
    assert.match(dom.getElementById("alerts-content").innerHTML, /source-b/);
    assert.equal(dom.getElementById("refresh-button").disabled, false);
  } finally {
    globalThis.document = oldDocument;
    globalThis.fetch = oldFetch;
  }
});

test("Valvomo näyttää virhetilan, jos ensisijainen seurantatiedosto ei lataudu", async () => {
  const oldDocument = globalThis.document;
  const oldFetch = globalThis.fetch;
  const dom = fakeDom();
  globalThis.document = dom;
  globalThis.fetch = async () => ({ ok: false, async json() { return {}; } });
  try {
    await loadDashboard();
    assert.equal(dom.getElementById("main-status").textContent, "Tilatieto ei käytettävissä");
    assert.match(dom.getElementById("alerts-content").innerHTML, /ei saanut kelvollista seurantatiedostoa/);
  } finally {
    globalThis.document = oldDocument;
    globalThis.fetch = oldFetch;
  }
});

test("lähdetarkistuslokin virhe ei piilota automaatioiden tilatietoja", async () => {
  const oldDocument = globalThis.document;
  const oldFetch = globalThis.fetch;
  const dom = fakeDom();
  globalThis.document = dom;
  globalThis.fetch = async (url) => url.includes("seurantatila")
    ? { ok: true, async json() { return sampleState(); } }
    : { ok: true, async json() { throw new Error("Virheellinen JSON"); } };
  try {
    await loadDashboard();
    assert.match(dom.getElementById("main-status").textContent, /aiempaa ohjeversiota/);
    assert.match(dom.getElementById("alerts-content").innerHTML, /Lähdetarkistusten yhteenvetoa ei voitu ladata/);
  } finally {
    globalThis.document = oldDocument;
    globalThis.fetch = oldFetch;
  }
});
