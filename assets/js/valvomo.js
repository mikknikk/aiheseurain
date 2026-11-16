/**
 * Valvomon selainpuolen logiikka.
 *
 * Lukee vain repositorion julkisia JSON-tiedostoja ja GitHubin julkista
 * Actions-rajapintaa. Skripti ei kirjoita GitHubiin eikä tarvitse tunnuksia.
 * Automaatiokortit perustuvat ChatGPT-automaation seurantatietoon; GitHub
 * Actions -kortit kuvaavat erikseen repositorion teknisiä työnkulkuja.
 */

export const TASK_ORDER = [
  "tolkien",
  "taylor_swift",
  "gurmeet_ram_rahim_singh",
  "muumit",
  "wakaliwood",
  "euroviisut",
  "sompote_sands",
  "shakkidraamat",
  "intialaiset_elokuvat"
];

const TASK_NAMES = {
  tolkien: "J. R. R. Tolkien",
  taylor_swift: "Taylor Swift",
  gurmeet_ram_rahim_singh: "Gurmeet Ram Rahim Singh",
  muumit: "Muumit",
  wakaliwood: "Wakaliwood",
  euroviisut: "Euroviisut ja kansalliset karsinnat",
  sompote_sands: "Sompote Sands",
  shakkidraamat: "Shakkidraamat",
  intialaiset_elokuvat: "Intialaisen elokuvan uutisraportti"
};

const API_ROOT = "https://api.github.com/repos/mikknikk/uutiset";
const CACHE_TTL = 5 * 60 * 1000;

export function classifyFreshness(timestamp, maxAgeHours, now = Date.now()) {
  if (!timestamp) return { key: "unknown", label: "Tuntematon" };
  const parsed = Date.parse(timestamp);
  if (!Number.isFinite(parsed) || parsed > now + 5 * 60 * 1000) {
    return { key: "unknown", label: "Aika ei ole kelvollinen" };
  }
  if (now - parsed > maxAgeHours * 60 * 60 * 1000) {
    return { key: "warning", label: "Vanhentunut" };
  }
  return { key: "good", label: "Tuore" };
}

export function latestRotationTask(tasks) {
  return TASK_ORDER
    .map((id) => ({ id, task: tasks?.[id] }))
    .filter(({ task }) => task && task.last_successful_check && Number.isFinite(Date.parse(task.last_successful_check)))
    .sort((a, b) => Date.parse(b.task.last_successful_check) - Date.parse(a.task.last_successful_check))[0] || null;
}

export function validateStateShape(state) {
  if (!state || typeof state !== "object" || state.schema_version !== 1) return false;
  if (!state.rotation || !state.rotation.tasks || !TASK_ORDER.every((id) => state.rotation.tasks[id])) return false;
  if (!state.separate_screening_watch || !state.automation_instructions || !state.quality_check_instructions) return false;
  if (!state.updated_at || !Number.isFinite(Date.parse(state.updated_at))) return false;
  return true;
}

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, (character) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  })[character]);
}

function dateText(value) {
  if (!value) return "Ei kirjattu";
  const date = new Date(value);
  if (!Number.isFinite(date.getTime())) return "Aikaleima virheellinen";
  return new Intl.DateTimeFormat("fi-FI", {
    dateStyle: "medium", timeStyle: "short", timeZone: "Europe/Helsinki"
  }).format(date);
}

function detailRows(rows) {
  return rows.map(([label, value]) =>
    `<dt>${escapeHtml(label)}</dt><dd>${escapeHtml(value)}</dd>`
  ).join("");
}

function setStatus(id, status) {
  const element = document.getElementById(id);
  element.className = `status-line status-${status.key}`;
  element.textContent = status.label;
}

function addNotes(id, notes) {
  const target = document.getElementById(id);
  if (!notes.length) {
    target.replaceChildren();
    return;
  }
  target.innerHTML = `<ul class="card-notes">${notes.map((note) => `<li>${escapeHtml(note)}</li>`).join("")}</ul>`;
}

function errorsFrom(record) {
  return Array.isArray(record?.errors) ? record.errors.filter((item) => typeof item === "string" && item.trim()) : [];
}

function renderMain(state, sourceLog) {
  const tasks = state.rotation.tasks;
  const latest = latestRotationTask(tasks);
  const nextId = state.rotation.next_task;
  const latestTask = latest?.task;
  const freshness = classifyFreshness(latestTask?.last_successful_check, 36);
  let status = freshness;
  if (latestTask?.last_result === "failed") status = { key: "error", label: "Viimeisin aiheajo epäonnistui" };
  else if (latestTask?.last_result === "partial") status = { key: "warning", label: "Viimeisin aiheajo jäi osittaiseksi" };
  else if (latestTask?.last_result === "published" && freshness.key === "good") status = { key: "good", label: "Viimeisin onnistuminen on tuore" };
  setStatus("main-status", status);

  document.getElementById("main-details").innerHTML = detailRows([
    ["Viimeksi käsitelty aihe", latest ? (latest.task.name || TASK_NAMES[latest.id]) : "Ei onnistumista kirjattu"],
    ["Viimeisin onnistuminen", dateText(latestTask?.last_successful_check)],
    ["Seuraava aihe", TASK_NAMES[nextId] || "Tuntematon tehtävä"],
    ["Julkaistut itemit", latestTask?.published_items ?? "Ei tietoa"],
    ["Tarkistetut lähteet", latestTask?.sources_checked ?? "Ei tietoa"],
    ["Seurantajakso", latestTask?.last_period_start && latestTask?.last_period_end
      ? `${dateText(latestTask.last_period_start)} – ${dateText(latestTask.last_period_end)}`
      : "Ei kirjattu"]
  ]);

  const latestRun = (sourceLog?.runs || []).find((run) => run.task_id === latest?.id);
  const sourceNotes = [];
  if (latestRun?.status) sourceNotes.push(`Lähdetarkistuksen tulos: ${latestRun.status === "complete" ? "kattavuuden käsittely valmis" : latestRun.status}`);
  if (latestRun?.checked_source_ids?.length) sourceNotes.push(`Tarkistettuja lähteitä: ${latestRun.checked_source_ids.length}`);
  if (latestRun?.unchecked_sources?.length) sourceNotes.push(`Tarkistamatta jäi ${latestRun.unchecked_sources.length} lähdettä; tarkemmat syyt ovat huomioissa.`);
  addNotes("main-issues", [...errorsFrom(latestTask), ...sourceNotes]);
  renderRotation(state);
}

function renderScreening(state) {
  const watch = state.separate_screening_watch;
  const freshness = classifyFreshness(watch.last_successful_check, 36);
  let status = freshness;
  if (watch.last_result === "failed") status = { key: "error", label: "Viimeisin näytösvahtiajo epäonnistui" };
  else if (watch.last_result === "partial") status = { key: "warning", label: "Viimeisin näytösvahtiajo jäi osittaiseksi" };
  else if (watch.last_result === "success" && freshness.key === "good") status = { key: "good", label: "Viimeisin onnistuminen on tuore" };
  setStatus("screening-status", status);
  document.getElementById("screening-details").innerHTML = detailRows([
    ["Viimeisin onnistuminen", dateText(watch.last_successful_check)],
    ["Julkaistut itemit", watch.published_items ?? "Ei tietoa"],
    ["Tarkistetut lähteet", watch.sources_checked ?? "Ei tietoa"],
    ["Seurantajakso", watch.last_period_start && watch.last_period_end
      ? `${dateText(watch.last_period_start)} – ${dateText(watch.last_period_end)}`
      : "Ei kirjattu"],
    ["Ohjeversio", watch.automation_instructions?.current_version || "Ei tietoa"],
    ["Viimeksi käytetty versio", watch.automation_instructions?.last_successful_run_version || "Ei tietoa"]
  ]);
  addNotes("screening-issues", errorsFrom(watch));
}

function renderQuality(state) {
  const quality = state.quality_check_instructions;
  const freshness = classifyFreshness(quality.last_successful_run_at, 24 * 10);
  const versionMismatch = quality.current_version !== quality.last_successful_run_version;
  let status = freshness;
  if (versionMismatch && freshness.key === "good") status = { key: "warning", label: "Ajo onnistui, mutta käytti vanhempaa ohjeversiota" };
  else if (freshness.key === "good") status = { key: "good", label: "Viimeisin onnistuminen on tuore" };
  setStatus("quality-status", status);
  document.getElementById("quality-details").innerHTML = detailRows([
    ["Viimeisin onnistuminen", dateText(quality.last_successful_run_at)],
    ["Nykyinen ohjeversio", quality.current_version || "Ei tietoa"],
    ["Viimeksi käytetty versio", quality.last_successful_run_version || "Ei tietoa"],
    ["Käynnistyskehotteen tunniste", quality.startup_prompt_id || "Ei tietoa"]
  ]);
  addNotes("quality-issues", versionMismatch
    ? [`Viimeisin onnistunut ajo käytti versiota ${quality.last_successful_run_version}; nykyinen käsikirja on ${quality.current_version}.`]
    : []);
}

function renderRotation(state) {
  const nextId = state.rotation.next_task;
  const tasks = state.rotation.tasks;
  const latest = latestRotationTask(tasks);
  document.getElementById("next-task").textContent = `Seuraava aihe: ${TASK_NAMES[nextId] || "Tuntematon"}`;
  const list = TASK_ORDER.map((id) => {
    const task = tasks[id];
    const isNext = id === nextId;
    const hasRun = Boolean(task.last_successful_check);
    const last = hasRun ? dateText(task.last_successful_check) : "Ei onnistumista kirjattu";
    const result = task.last_result === "published" ? "Onnistui"
      : task.last_result === "partial" ? "Osittainen"
      : task.last_result === "failed" ? "Epäonnistui"
      : "Tuntematon";
    const completed = latest && latest.id === id;
    return `<li class="${isNext ? "is-next" : ""} ${completed ? "is-completed" : ""}">
      <span>${escapeHtml(TASK_NAMES[id])}</span>
      <span class="rotation-meta">${isNext ? "Seuraava vuoro · " : ""}${escapeHtml(result)} · ${escapeHtml(last)}</span>
    </li>`;
  }).join("");
  document.getElementById("rotation-list").innerHTML = list;
}

function renderAlerts(state, sourceLog) {
  const notices = [];
  for (const id of TASK_ORDER) {
    const task = state.rotation.tasks[id];
    for (const error of errorsFrom(task)) notices.push({ type: "error", title: TASK_NAMES[id], text: error });
  }
  for (const error of errorsFrom(state.separate_screening_watch)) notices.push({ type: "error", title: "Näytösvahti", text: error });
  if (state.quality_check_instructions.current_version !== state.quality_check_instructions.last_successful_run_version) {
    notices.push({
      type: "warning", title: "Laatutarkistus",
      text: `Viimeisin onnistunut ajo käytti ohjeversiota ${state.quality_check_instructions.last_successful_run_version}; nykyinen versio on ${state.quality_check_instructions.current_version}.`
    });
  }
  const latest = latestRotationTask(state.rotation.tasks);
  const latestRun = (sourceLog?.runs || []).find((run) => run.task_id === latest?.id);
  if (latestRun?.unchecked_sources?.length) {
    const sourceItems = latestRun.unchecked_sources.map((source) =>
      `<li><strong>${escapeHtml(source.source_id)}</strong>: ${escapeHtml(source.reason)}</li>`
    ).join("");
    notices.push({
      type: "warning", title: "Viimeisimmän aiheajon tarkistamatta jääneet lähteet",
      html: `<p>${latestRun.unchecked_sources.length} lähdettä jäi tarkistamatta. Niitä ei lasketa tarkistetuiksi.</p><details><summary>Näytä lähteet ja syyt</summary><ul>${sourceItems}</ul></details>`
    });
  }
  const target = document.getElementById("alerts-content");
  if (!notices.length) {
    target.innerHTML = '<p>Seurantatiedoissa ei ole kirjattuja virheitä tai varoituksia.</p>';
    return;
  }
  target.innerHTML = notices.map((notice) => `
    <article class="notice notice-${notice.type}">
      <h3>${escapeHtml(notice.title)}</h3>
      ${notice.html || `<p>${escapeHtml(notice.text)}</p>`}
    </article>`
  ).join("");
}

function workflowLabel(run) {
  if (run.status === "in_progress") return "Käynnissä";
  if (run.status === "queued") return "Jonossa";
  if (run.conclusion === "success") return "Onnistui";
  if (run.conclusion === "failure") return "Epäonnistui";
  if (run.conclusion === "cancelled") return "Peruutettu";
  return run.conclusion || run.status || "Tuntematon";
}

function safeGithubUrl(value) {
  try {
    const url = new URL(value);
    return url.protocol === "https:" && url.hostname === "github.com" ? url.href : null;
  } catch {
    return null;
  }
}

async function fetchJson(url) {
  const response = await fetch(url, {
    headers: { Accept: "application/vnd.github+json" },
    cache: "no-store"
  });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.json();
}

async function cachedJson(url) {
  try {
    const cached = sessionStorage.getItem(`uutisvahti:${url}`);
    if (cached) {
      const parsed = JSON.parse(cached);
      if (Date.now() - parsed.savedAt < CACHE_TTL) return parsed.value;
    }
  } catch {
    // Tallennustilan estyminen ei saa estää Valvomon käyttöä.
  }
  const value = await fetchJson(url);
  try {
    sessionStorage.setItem(`uutisvahti:${url}`, JSON.stringify({ savedAt: Date.now(), value }));
  } catch {
    // Selain voi estää sessionStorage-käytön; jatkamme ilman välimuistia.
  }
  return value;
}

async function renderActions() {
  const target = document.getElementById("actions-content");
  try {
    const data = await cachedJson(`${API_ROOT}/actions/runs?per_page=60`);
    const runs = Array.isArray(data.workflow_runs) ? data.workflow_runs : [];
    const wanted = [
      { label: "Pages-julkaisu", match: (name) => name.toLowerCase() === "pages build and deployment" },
      { label: "RSS- ja dokumentaatiotestit", match: (name) => name.toLowerCase().includes("rss- ja dokumentaatiotestit") },
      { label: "Viikoittainen linkkitarkistus", match: (name) => name.toLowerCase().includes("lähde- ja rss-linkkien viikoittainen tarkistus") }
    ];
    const selected = wanted.map((item) => ({
      label: item.label,
      run: runs.filter((run) => item.match(run.name || "")).sort((a, b) => Date.parse(b.updated_at) - Date.parse(a.updated_at))[0] || null
    }));
    const cards = await Promise.all(selected.map(async ({ label, run }) => {
      if (!run) return `<article class="actions-card"><h3>${escapeHtml(label)}</h3><p>Yhtään ajoa ei löytynyt.</p></article>`;
      let steps = "";
      if (typeof run.jobs_url === "string" && run.jobs_url.startsWith("https://api.github.com/repos/mikknikk/uutiset/actions/runs/")) {
        try {
          const jobsData = await cachedJson(run.jobs_url);
          const jobs = Array.isArray(jobsData.jobs) ? jobsData.jobs : [];
          steps = jobs.map((job) => `<li><strong>${escapeHtml(job.name)}</strong> — ${escapeHtml(workflowLabel(job))}
            ${Array.isArray(job.steps) && job.steps.length
              ? `<ul>${job.steps.map((step) => `<li class="step-status">${escapeHtml(step.name)}: ${escapeHtml(workflowLabel(step))}</li>`).join("")}</ul>`
              : ""}
          </li>`).join("");
        } catch {
          steps = "<li>Vaiheita ei voitu hakea GitHubin rajapinnasta.</li>";
        }
      }
      const link = safeGithubUrl(run.html_url);
      return `<article class="actions-card">
        <h3>${escapeHtml(label)}</h3>
        <p><strong>${escapeHtml(workflowLabel(run))}</strong></p>
        <p class="muted">Päivitetty: ${escapeHtml(dateText(run.updated_at))}</p>
        ${link ? `<p><a href="${escapeHtml(link)}">Avaa tämä Actions-ajo GitHubissa</a></p>` : ""}
        ${steps ? `<details><summary>Työvaiheet</summary><ul>${steps}</ul></details>` : ""}
      </article>`;
    }));
    target.innerHTML = cards.join("");
  } catch {
    target.innerHTML = '<p class="notice notice-warning">GitHub Actions -tilaa ei saatu haettua. Automaatioiden koneellinen seurantatieto toimii tästä rajapinnasta riippumatta. <a href="https://github.com/mikknikk/uutiset/actions">Avaa Actions GitHubissa</a>.</p>';
  }
}

async function loadDashboard() {
  const button = document.getElementById("refresh-button");
  button.disabled = true;
  button.textContent = "Päivitetään…";
  try {
    const [stateResponse, sourceResponse] = await Promise.allSettled([
      fetch("../data/seurantatila.json", { cache: "no-cache" }),
      fetch("../data/lahdetarkistukset.json", { cache: "no-cache" })
    ]);
    if (stateResponse.status !== "fulfilled" || !stateResponse.value.ok) {
      throw new Error("Seurantatiedoston lataus epäonnistui.");
    }
    const state = await stateResponse.value.json();
    if (!validateStateShape(state)) throw new Error("Seurantatiedosto ei vastaa Valvomon odottamaa rakennetta.");
    const sourceLog = sourceResponse.status === "fulfilled" && sourceResponse.value.ok
      ? await sourceResponse.value.json()
      : null;

    document.getElementById("data-updated").textContent = dateText(state.updated_at);
    const updatedAge = classifyFreshness(state.updated_at, 36);
    document.getElementById("data-age").textContent = updatedAge.key === "warning"
      ? "Tilatiedoston päivitys on vanhentunut."
      : "Seurantatiedoston viimeisin päivitysaika (ei sama asia kuin yksittäisen automaation viimeisin ajo).";

    renderMain(state, sourceLog);
    renderScreening(state);
    renderQuality(state);
    renderAlerts(state, sourceLog);
    if (!sourceLog) {
      document.getElementById("alerts-content").insertAdjacentHTML("beforeend",
        '<p class="notice notice-warning">Lähdetarkistusten yhteenvetoa ei voitu ladata. Automaatiokorttien perustiedot ovat erillisessä seurantatiedostossa.</p>');
    }
  } catch {
    document.getElementById("data-updated").textContent = "Tietoja ei voitu näyttää";
    document.getElementById("data-age").textContent = "Seurantatieto puuttuu, ei lataudu tai on virheellisessä muodossa.";
    for (const id of ["main-status", "screening-status", "quality-status"]) {
      setStatus(id, { key: "error", label: "Tilatieto ei käytettävissä" });
    }
    document.getElementById("alerts-content").innerHTML =
      '<p class="notice notice-error">Valvomo ei saanut kelvollista seurantatiedostoa. Vanhaa tietoa ei esitetä tuoreena.</p>';
    document.getElementById("rotation-list").innerHTML = "<li>Aihekiertoa ei voitu ladata.</li>";
  } finally {
    button.disabled = false;
    button.textContent = "Päivitä näkymä";
  }
}

if (typeof document !== "undefined") {
  document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("refresh-button")?.addEventListener("click", () => {
      loadDashboard();
      renderActions();
    });
    loadDashboard();
    renderActions();
  });
}
