/**
 * Aiheseuraimen Kehitysjonon selainpuolen toiminta.
 *
 * Lukee tämän repositorion julkiset GitHub Issues -tiketit vain luku -tilassa.
 * Selain ei käytä tunnuksia, tokeneita eikä GitHubin kirjoitusrajapintoja.
 * GitHub Issues säilyy tehtävien ainoana ensisijaisena tietolähteenä.
 */

export const STATUS_COLUMNS = [
  { id: "backlog", label: "Backlog", issueLabel: "tila:backlog" },
  { id: "ready", label: "Valmis työn alle", issueLabel: "tila:ready" },
  { id: "in-progress", label: "Työn alla", issueLabel: "tila:in-progress" },
  { id: "blocked", label: "Estynyt", issueLabel: "tila:blocked" },
  { id: "done", label: "Valmis", issueLabel: "tila:done" }
];

export const PRIORITIES = ["P0", "P1", "P2", "P3"];
const API_URL = "https://api.github.com/repos/mikknikk/aiheseurain/issues";
const CACHE_KEY = "aiheseurain.kanban.cache.v1";
const STALE_AFTER_MS = 60 * 60 * 1000;
const MAX_PAGES = 10;

function labelNames(issue) {
  return (Array.isArray(issue?.labels) ? issue.labels : [])
    .map((label) => typeof label === "string" ? label : label?.name)
    .filter((name) => typeof name === "string" && name.length > 0);
}

/** Muuntaa yhden GitHub-issuen kanbanissa käytettäväksi tietueeksi. */
export function normalizeIssue(issue) {
  const labels = labelNames(issue);
  const statusLabels = STATUS_COLUMNS.filter((column) => labels.includes(column.issueLabel));
  const priorityLabels = PRIORITIES.filter((priority) => labels.includes(priority));
  const areaLabels = labels.filter((label) => /^aihe:/i.test(label));

  // Suljettu issue on aina valmis, vaikka sen tilatunniste olisi vanhentunut.
  const status = issue.state === "closed"
    ? "done"
    : statusLabels.length === 1 ? statusLabels[0].id : null;

  return {
    number: Number(issue.number),
    title: String(issue.title || "Otsikko puuttuu"),
    url: String(issue.html_url || ""),
    state: issue.state,
    status,
    priority: priorityLabels.length === 1 ? priorityLabels[0] : null,
    area: areaLabels.length === 1 ? areaLabels[0] : null,
    areaName: areaLabels.length === 1
      ? areaLabels[0].replace(/^aihe:/i, "").replace(/[-_]/g, " ")
      : null,
    labels,
    updatedAt: issue.updated_at || null
  };
}

/** Jättää GitHubin issues-rajapinnan palauttamat pull requestit pois. */
export function normalizeIssues(payload) {
  if (!Array.isArray(payload)) throw new Error("GitHub palautti odottamattoman vastausrakenteen.");
  return payload
    .filter((issue) => issue && !issue.pull_request && Number.isInteger(Number(issue.number)))
    .map(normalizeIssue)
    .filter((issue) => issue.url && issue.title);
}

/** Suodattaa tiketit hakutekstin, prioriteetin ja aihealueen perusteella. */
export function filterIssues(issues, filters = {}) {
  const query = String(filters.query || "").trim().toLocaleLowerCase("fi");
  return issues.filter((issue) => {
    const matchesQuery = !query
      || issue.title.toLocaleLowerCase("fi").includes(query)
      || String(issue.number).includes(query);
    const matchesPriority = !filters.priority || filters.priority === "all"
      || (filters.priority === "none" ? !issue.priority : issue.priority === filters.priority);
    const matchesArea = !filters.area || filters.area === "all"
      || (filters.area === "none" ? !issue.area : issue.area === filters.area);
    return matchesQuery && matchesPriority && matchesArea;
  });
}

/** Muodostaa riippuvuusverkon GitHubin blocked_by-suhteista. */
export function buildDependencyGraph(issues, payloads, complete = true) {
  const directory = new Map(issues.map((issue) => [issue.number, issue]));
  const relations = new Map();
  for (const payload of payloads) {
    const number = Number(payload.issueNumber);
    const blockers = (Array.isArray(payload.blockedBy) ? payload.blockedBy : [])
      .filter((item) => item && Number.isInteger(Number(item.number)))
      .map(normalizeIssue);
    relations.set(number, { blockedBy: blockers, blocking: [] });
    for (const blocker of blockers) if (!directory.has(blocker.number)) directory.set(blocker.number, blocker);
  }
  for (const issue of directory.values()) {
    if (!relations.has(issue.number)) relations.set(issue.number, { blockedBy: [], blocking: [] });
  }
  for (const [number, value] of relations) {
    for (const blocker of value.blockedBy) relations.get(blocker.number).blocking.push(directory.get(number));
  }
  return {
    byIssue: Object.fromEntries([...relations].map(([number, value]) => [number, {
      blockedBy: value.blockedBy.sort((a, b) => a.number - b.number),
      blocking: value.blocking.filter(Boolean).sort((a, b) => a.number - b.number)
    }])),
    issueDirectory: Object.fromEntries(directory),
    complete
  };
}

/** Hakee kunkin tiketin edeltävät riippuvuudet GitHubin julkisesta luku-APIsta. */
export async function fetchAllDependencies(issues, fetchImpl = fetch, concurrency = 4) {
  const results = new Array(issues.length);
  let next = 0;
  let complete = true;
  async function fetchOne(issue) {
    const blockers = [];
    for (let page = 1; page <= 10; page += 1) {
      const url = new URL(API_URL + "/" + issue.number + "/dependencies/blocked_by");
      url.search = new URLSearchParams({ per_page: "100", page: String(page) }).toString();
      const response = await fetchImpl(url, {
        headers: { Accept: "application/vnd.github+json" }, cache: "no-store"
      });
      if (!response.ok) {
        if (response.status === 403 || response.status === 429) throw new Error("GitHub API rajoitti riippuvuustietojen hakua.");
        throw new Error("Tiketin #" + issue.number + " riippuvuuksien haku epäonnistui (HTTP " + response.status + ").");
      }
      const items = await response.json();
      if (!Array.isArray(items)) throw new Error("GitHub palautti virheellisen riippuvuusvastauksen.");
      blockers.push(...items);
      if (items.length < 100) return { issueNumber: issue.number, blockedBy: blockers };
    }
    throw new Error("Tiketin #" + issue.number + " riippuvuuksia on odotettua enemmän.");
  }
  async function worker() {
    while (next < issues.length) {
      const index = next++;
      try { results[index] = await fetchOne(issues[index]); }
      catch (error) {
        complete = false;
        results[index] = { issueNumber: issues[index].number, blockedBy: [],
          error: error instanceof Error ? error.message : "Riippuvuuksien haku epäonnistui." };
      }
    }
  }
  await Promise.all(Array.from({ length: Math.max(1, Math.min(concurrency, issues.length || 1)) }, worker));
  return { payloads: results, complete };
}

function safeReadCache() {
  try {
    const raw = globalThis.localStorage?.getItem(CACHE_KEY);
    if (!raw) return null;
    const value = JSON.parse(raw);
    if (!value || !Array.isArray(value.issues) || !Number.isFinite(value.savedAt)) return null;
    return value;
  } catch {
    // Yksityisen selaustilan tai estettyjen evästeiden tallennusvirhe ei estä käyttöä.
    return null;
  }
}

function safeWriteCache(issues, savedAt, dependencies = dependencyGraph, dependenciesSavedAt = dependencySavedAt) {
  try {
    globalThis.localStorage?.setItem(CACHE_KEY, JSON.stringify({ issues, savedAt, dependencies, dependenciesSavedAt }));
  } catch {
    // Välimuisti on vain käyttömukavuutta varten; API-haku toimii ilman sitä.
  }
}

function formatDate(timestamp) {
  return new Intl.DateTimeFormat("fi-FI", {
    dateStyle: "medium",
    timeStyle: "short",
    timeZone: "Europe/Helsinki"
  }).format(new Date(timestamp));
}

function formatAge(timestamp, now = Date.now()) {
  const minutes = Math.max(0, Math.floor((now - timestamp) / 60000));
  if (minutes < 1) return "juuri äsken";
  if (minutes < 60) return minutes + " min sitten";
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return hours + (hours === 1 ? " tunti sitten" : " tuntia sitten");
  const days = Math.floor(hours / 24);
  return days + (days === 1 ? " päivä sitten" : " päivää sitten");
}

/** Hakee kaikki sivut, jotta myös vanhemmat ja suljetut tiketit tulevat mukaan. */
export async function fetchAllIssues(fetchImpl = fetch) {
  const all = [];
  for (let page = 1; page <= MAX_PAGES; page += 1) {
    const url = new URL(API_URL);
    url.search = new URLSearchParams({
      state: "all",
      per_page: "100",
      sort: "updated",
      direction: "desc",
      page: String(page)
    }).toString();

    const response = await fetchImpl(url, {
      headers: { Accept: "application/vnd.github+json" },
      cache: "no-store"
    });
    if (!response.ok) {
      if (response.status === 403 || response.status === 429) {
        throw new Error("GitHub API rajoitti pyyntöä. Yritä myöhemmin uudelleen.");
      }
      throw new Error("GitHub Issues -tietojen haku epäonnistui (HTTP " + response.status + ").");
    }
    const pageItems = await response.json();
    if (!Array.isArray(pageItems)) throw new Error("GitHub palautti odottamattoman vastausrakenteen.");
    all.push(...pageItems);
    if (pageItems.length < 100) return normalizeIssues(all);
  }
  throw new Error("Tikettejä on yli 1 000. Näkymä keskeytettiin, jotta tuloksia ei esitettäisi täydellisinä.");
}

function makeElement(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

let allIssues = [];
let savedAt = null;
let dependencyGraph = null;
let dependencySavedAt = null;
let selectedDependencyIssue = null;
let activeView = "board";

function currentFilters() {
  return {
    query: document.getElementById("kanban-search").value,
    priority: document.getElementById("kanban-priority").value,
    area: document.getElementById("kanban-area").value
  };
}

function priorityRank(priority) {
  const index = PRIORITIES.indexOf(priority);
  return index < 0 ? PRIORITIES.length : index;
}

function sortedIssues(issues) {
  return [...issues].sort((a, b) =>
    priorityRank(a.priority) - priorityRank(b.priority) || a.number - b.number
  );
}

function renderBoard(issues) {
  const target = document.getElementById("kanban-board");
  target.replaceChildren();

  for (const column of STATUS_COLUMNS) {
    const section = makeElement("section", "kanban-column");
    section.setAttribute("aria-labelledby", "column-" + column.id);
    const heading = makeElement("h3", "kanban-column-heading");
    heading.id = "column-" + column.id;
    heading.append(
      makeElement("span", "", column.label),
      makeElement("span", "kanban-column-count",
        String(issues.filter((issue) => issue.status === column.id).length))
    );
    section.appendChild(heading);

    const cards = makeElement("ul", "kanban-cards");
    const columnIssues = sortedIssues(issues.filter((issue) => issue.status === column.id));
    if (!columnIssues.length) {
      cards.appendChild(makeElement("li", "kanban-empty", "Ei tikettejä."));
    }
    for (const issue of columnIssues) {
      const item = makeElement("li", "kanban-card");
      const number = makeElement("a", "kanban-number", "#" + issue.number);
      number.href = issue.url;
      number.rel = "noopener noreferrer";
      const title = makeElement("a", "kanban-card-title", issue.title);
      title.href = issue.url;
      title.rel = "noopener noreferrer";
      const meta = makeElement("p", "kanban-card-meta");
      meta.appendChild(makeElement("span", "kanban-priority",
        issue.priority || "Prioriteetti puuttuu"));
      meta.appendChild(makeElement("span", "kanban-area",
        issue.areaName || "Aihealuetta ei merkitty"));
      item.append(number, title, meta);
      if (dependencyGraph) {
        const relations = dependencyGraph.byIssue[issue.number] || { blockedBy: [], blocking: [] };
        item.appendChild(makeElement("p", "kanban-dependency-summary",
          "Edeltäjiä: " + relations.blockedBy.length + " · Estää: " + relations.blocking.length));
        const detailButton = makeElement("button", "kanban-dependency-button", "Avaa riippuvuudet");
        detailButton.type = "button";
        detailButton.dataset.issueNumber = String(issue.number);
        detailButton.setAttribute("aria-label", "Näytä tiketin #" + issue.number + " riippuvuudet");
        item.appendChild(detailButton);
      }
      cards.appendChild(item);
    }
    section.appendChild(cards);
    target.appendChild(section);
  }
}

function renderTable(issues) {
  const target = document.getElementById("kanban-table-body");
  target.replaceChildren();
  for (const issue of sortedIssues(issues)) {
    const row = document.createElement("tr");
    const numberCell = document.createElement("td");
    const numberLink = makeElement("a", "", "#" + issue.number);
    numberLink.href = issue.url;
    numberLink.rel = "noopener noreferrer";
    numberCell.appendChild(numberLink);
    const titleCell = document.createElement("th");
    titleCell.scope = "row";
    const titleLink = makeElement("a", "", issue.title);
    titleLink.href = issue.url;
    titleLink.rel = "noopener noreferrer";
    titleCell.appendChild(titleLink);
    const dependencyCell = document.createElement("td");
    if (dependencyGraph) {
      const relations = dependencyGraph.byIssue[issue.number] || { blockedBy: [], blocking: [] };
      dependencyCell.appendChild(makeElement("span", "",
        "Edeltäjiä: " + relations.blockedBy.length + "; estää: " + relations.blocking.length + ". "));
      const detailButton = makeElement("button", "kanban-dependency-button", "Avaa");
      detailButton.type = "button";
      detailButton.dataset.issueNumber = String(issue.number);
      detailButton.setAttribute("aria-label", "Näytä tiketin #" + issue.number + " riippuvuudet");
      dependencyCell.appendChild(detailButton);
    } else dependencyCell.textContent = "Ei ladattu";
    row.append(
      numberCell, titleCell,
      makeElement("td", "", issue.priority || "Ei määritelty"),
      makeElement("td", "", issue.areaName || "Ei merkitty"),
      makeElement("td", "", STATUS_COLUMNS.find((column) => column.id === issue.status)?.label || "Tila puuttuu"),
      dependencyCell
    );
    target.appendChild(row);
  }
}


function dependencyStatus(issue) {
  if (issue.state === "closed") return "Valmis (suljettu)";
  return STATUS_COLUMNS.find((column) => column.id === issue.status)?.label || "Tila puuttuu";
}
function renderDependencyPanel() {
  const target = document.getElementById("kanban-dependency-details");
  target.replaceChildren();
  if (!dependencyGraph || !selectedDependencyIssue) { target.hidden = true; return; }
  const issue = dependencyGraph.issueDirectory[selectedDependencyIssue];
  if (!issue) { target.hidden = true; return; }
  const relations = dependencyGraph.byIssue[selectedDependencyIssue] || { blockedBy: [], blocking: [] };
  target.append(
    makeElement("h3", "", "Tiketin #" + issue.number + " riippuvuudet"),
    makeElement("p", "", "Edeltävä työ = tiketti, jonka valmistumista tämä työ odottaa. Estää = tiketti, jonka etenemistä tämä työ estää.")
  );
  if (!dependencyGraph.complete) target.appendChild(makeElement("p", "kanban-dependency-warning",
    "Riippuvuustietojen haku jäi osittaiseksi. Alla näkyvät vain onnistuneesti haetut suhteet; lukumäärät voivat olla puutteellisia."));
  for (const group of [
    { title: "Edeltävä työ (tämä tiketti odottaa näitä)", items: relations.blockedBy },
    { title: "Tämä tiketti estää seuraavia töitä", items: relations.blocking }
  ]) {
    const list = document.createElement("ul");
    if (!group.items.length) list.appendChild(makeElement("li", "", "GitHubiin ei ole kirjattu tähän suuntaan riippuvuuksia."));
    for (const related of group.items) {
      const item = document.createElement("li");
      const link = makeElement("a", "", "#" + related.number + " – " + related.title);
      link.href = related.url || ("https://github.com/mikknikk/aiheseurain/issues/" + related.number);
      link.rel = "noopener noreferrer";
      item.append(link, document.createTextNode(" (" + dependencyStatus(related) + ")"));
      list.appendChild(item);
    }
    target.append(makeElement("h4", "", group.title), list);
  }
  target.hidden = false;
}
function updateDependencyStatus(message, warning = false) {
  const status = document.getElementById("kanban-dependency-status");
  status.textContent = message;
  status.className = warning ? "kanban-dependency-status kanban-dependency-warning" : "kanban-dependency-status";
}
async function loadDependencies() {
  const button = document.getElementById("kanban-dependencies");
  button.disabled = true;
  button.textContent = "Haetaan riippuvuuksia…";
  updateDependencyStatus("Haetaan GitHubin riippuvuustietoja. Yksi lukupyyntö tehdään kutakin tikettiä kohti.");
  try {
    const result = await fetchAllDependencies(allIssues);
    dependencyGraph = buildDependencyGraph(allIssues, result.payloads, result.complete);
    dependencySavedAt = Date.now();
    selectedDependencyIssue = null;
    safeWriteCache(allIssues, savedAt, dependencyGraph, dependencySavedAt);
    render();
    const failed = result.payloads.filter((item) => item.error).length;
    updateDependencyStatus(result.complete
      ? "Riippuvuustiedot päivitetty " + formatDate(dependencySavedAt) + "."
      : "Riippuvuustiedot ovat osittaiset: " + failed + " tiketin tietoja ei saatu haettua.", !result.complete);
  } catch (error) {
    updateDependencyStatus(error instanceof Error ? error.message : "Riippuvuuksien haku epäonnistui.", true);
  } finally {
    button.disabled = false;
    button.textContent = dependencyGraph ? "Päivitä riippuvuudet" : "Yritä riippuvuuksia uudelleen";
  }
}
function showIssueDependencies(issueNumber) {
  if (!dependencyGraph) return;
  selectedDependencyIssue = Number(issueNumber);
  renderDependencyPanel();
  document.getElementById("kanban-dependency-details").scrollIntoView?.({ block: "nearest" });
}

function render() {
  const filtered = filterIssues(allIssues, currentFilters());
  renderBoard(filtered);
  renderTable(filtered);
  document.getElementById("kanban-count").textContent =
    filtered.length + (filtered.length === 1 ? " tiketti" : " tikettiä") + " / " + allIssues.length;

  const unclassified = filtered.filter((issue) => !issue.status);
  const warning = document.getElementById("kanban-classification-warning");
  warning.hidden = unclassified.length === 0;
  warning.textContent = unclassified.length
    ? unclassified.length + " tikettiä ei näy tilasarakkeissa, koska niiltä puuttuu yksiselitteinen tila. Ne näkyvät listanäkymässä."
    : "";

  document.getElementById("kanban-empty").hidden = filtered.length > 0;
  renderDependencyPanel();
  document.getElementById("kanban-board").hidden = activeView !== "board";
  document.getElementById("kanban-list-view").hidden = activeView !== "list";
  document.getElementById("view-board").setAttribute("aria-pressed", String(activeView === "board"));
  document.getElementById("view-list").setAttribute("aria-pressed", String(activeView === "list"));
}

function populateAreaFilter() {
  const select = document.getElementById("kanban-area");
  const selected = select.value;
  const areas = [...new Set(allIssues.map((issue) => issue.area).filter(Boolean))].sort();
  select.replaceChildren(new Option("Kaikki aihealueet", "all"));
  select.appendChild(new Option("Ei aihealuetta merkitty", "none"));
  for (const area of areas) {
    const issue = allIssues.find((item) => item.area === area);
    select.appendChild(new Option(issue?.areaName || area, area));
  }
  if ([...select.options].some((option) => option.value === selected)) select.value = selected;
}

function updateFreshness(message, kind = "info") {
  const status = document.getElementById("kanban-freshness");
  status.className = "kanban-freshness" + (kind === "warning" ? " kanban-freshness-warning" : "");
  status.textContent = message;
}

function showCachedData(cache, isError = false) {
  allIssues = cache.issues;
  savedAt = cache.savedAt;
  dependencyGraph = cache.dependencies && typeof cache.dependencies.byIssue === "object" ? cache.dependencies : null;
  dependencySavedAt = Number.isFinite(cache.dependenciesSavedAt) ? cache.dependenciesSavedAt : null;
  document.getElementById("kanban-dependencies").textContent = dependencyGraph ? "Päivitä riippuvuudet" : "Näytä riippuvuudet";
  updateDependencyStatus(dependencyGraph ? "Välimuistissa olevat riippuvuustiedot: " + formatDate(dependencySavedAt || cache.savedAt) + "." : "Riippuvuuksia ei ole vielä haettu.");
  populateAreaFilter();
  render();
  const age = Date.now() - cache.savedAt;
  const stale = age > STALE_AFTER_MS;
  const prefix = stale ? "Vanhentunut välimuistitieto" : "Välimuistissa oleva tieto";
  updateFreshness(prefix + ". Viimeisin onnistunut päivitys " +
    formatDate(cache.savedAt) + " (" + formatAge(cache.savedAt) + ")." +
    (isError ? " Uutta tietoa ei saatu haettua." : " Tarkistetaan GitHubista uusinta tilaa."),
    stale || isError ? "warning" : "info");
}

async function refreshIssues() {
  const button = document.getElementById("kanban-refresh");
  button.disabled = true;
  button.textContent = "Päivitetään…";
  try {
    const issues = await fetchAllIssues();
    allIssues = issues;
    savedAt = Date.now();
    dependencyGraph = null;
    dependencySavedAt = null;
    selectedDependencyIssue = null;
    safeWriteCache(issues, savedAt, null, null);
    document.getElementById("kanban-dependencies").textContent = "Näytä riippuvuudet";
    updateDependencyStatus("Riippuvuuksia ei ole vielä haettu.");
    populateAreaFilter();
    render();
    updateFreshness("Päivitetty onnistuneesti " + formatDate(savedAt) + ".");
    document.getElementById("kanban-api-error").hidden = true;
  } catch (error) {
    const cache = safeReadCache();
    if (cache) {
      showCachedData(cache, true);
    }
    const message = error instanceof Error ? error.message : "GitHub API -päivitys epäonnistui.";
    const errorPanel = document.getElementById("kanban-api-error");
    errorPanel.hidden = false;
    errorPanel.textContent = message + (cache
      ? " Näytämme erikseen merkittyä välimuistitietoa."
      : " Tikettejä ei voida näyttää ilman onnistunutta hakua.");
    if (!cache) {
      allIssues = [];
      render();
      document.getElementById("kanban-empty").hidden = false;
      document.getElementById("kanban-empty").textContent = "Tikettejä ei voitu ladata. Yritä päivittää näkymä uudelleen.";
      updateFreshness("Päivitys ei ole onnistunut; tietojen ajantasaisuutta ei voida vahvistaa.", "warning");
    }
  } finally {
    button.disabled = false;
    button.textContent = "Päivitä tiketit";
  }
}

function initializeKanban() {
  const cache = safeReadCache();
  if (cache) showCachedData(cache);
  document.getElementById("kanban-search").addEventListener("input", render);
  document.getElementById("kanban-priority").addEventListener("change", render);
  document.getElementById("kanban-area").addEventListener("change", render);
  document.getElementById("view-board").addEventListener("click", () => {
    activeView = "board";
    render();
  });
  document.getElementById("view-list").addEventListener("click", () => {
    activeView = "list";
    render();
  });
  document.getElementById("kanban-refresh").addEventListener("click", refreshIssues);
  document.getElementById("kanban-dependencies").addEventListener("click", loadDependencies);
  document.getElementById("kanban-board").addEventListener("click", (event) => {
    const button = event.target.closest("[data-issue-number]");
    if (button) showIssueDependencies(button.dataset.issueNumber);
  });
  document.getElementById("kanban-table-body").addEventListener("click", (event) => {
    const button = event.target.closest("[data-issue-number]");
    if (button) showIssueDependencies(button.dataset.issueNumber);
  });
  refreshIssues();
}

if (typeof document !== "undefined") {
  document.addEventListener("DOMContentLoaded", initializeKanban, { once: true });
}
