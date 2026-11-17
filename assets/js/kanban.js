/**
 * Aiheseuraimen Kehitysjonon selainpuolen toiminta.
 *
 * Lukee GitHub Actionsin muodostaman täydellisen, GitHub Pagesissa julkaistun JSON-aineiston.
 * Selain ei kutsu GitHubin issue- tai riippuvuusrajapintoja eikä käytä tunnuksia.
 * GitHub Issues ja natiivit riippuvuudet säilyvät kanonisina tietolähteinä.
 */

export const STATUS_COLUMNS = [
  { id: "backlog", label: "Backlog", issueLabel: "tila:backlog" },
  { id: "ready", label: "Valmis työn alle", issueLabel: "tila:ready" },
  { id: "in-progress", label: "Työn alla", issueLabel: "tila:in-progress" },
  { id: "blocked", label: "Estynyt", issueLabel: "tila:blocked" },
  { id: "done", label: "Valmis", issueLabel: "tila:done" }
];

export const PRIORITIES = ["P0", "P1", "P2", "P3"];
const CACHE_KEY = "aiheseurain.kanban.cache.v1";
const STALE_AFTER_MS = 30 * 60 * 60 * 1000;

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

/** Jättää aineistoon mahdollisesti päätyneet pull requestit pois. */
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

/** Hakee vain täydellisen, Actionsissa muodostetun Pages-aineiston. */
export async function fetchPublishedDataset(fetchImpl = fetch, url = null) {
  const configuredUrl = url || (typeof document !== "undefined"
    ? document.querySelector("[data-kanban-data-url]")?.dataset.kanbanDataUrl
    : null);
  if (!configuredUrl) throw new Error("Kehitysjonon julkaistun aineiston osoite puuttuu.");
  const response = await fetchImpl(configuredUrl, {
    headers: { Accept: "application/json" },
    cache: "no-store"
  });
  if (!response.ok) {
    throw new Error("Kehitysjonon julkaistun aineiston haku epäonnistui (HTTP " + response.status + ").");
  }
  const dataset = await response.json();
  if (!dataset || dataset.schema_version !== 1 || dataset.status !== "complete"
      || !Array.isArray(dataset.issues) || !Array.isArray(dataset.dependencies)
      || dataset.issue_count !== dataset.issues.length
      || dataset.dependencies.length !== dataset.issues.length
      || !Number.isFinite(Date.parse(dataset.generated_at))) {
    throw new Error("Kehitysjonon aineisto on virheellinen tai puutteellinen; sitä ei käytetä.");
  }
  const issueNumbers = new Set(dataset.issues.map((issue) => Number(issue.number)));
  const dependencyNumbers = new Set(dataset.dependencies.map((item) => Number(item.issueNumber)));
  const relationCount = dataset.dependencies.reduce((sum, item) =>
    sum + (Array.isArray(item.blockedBy) ? item.blockedBy.length : 0), 0);
  if (issueNumbers.size !== dataset.issues.length
      || dependencyNumbers.size !== dataset.dependencies.length
      || dependencyNumbers.size !== issueNumbers.size
      || relationCount !== dataset.dependency_relation_count
      || dataset.dependencies.some((item) => !issueNumbers.has(Number(item.issueNumber))
        || !Array.isArray(item.blockedBy))) {
    throw new Error("Kehitysjonon aineiston tiketti- tai riippuvuustiedot eivät täsmää.");
  }
  return dataset;
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
          (dependencyGraph.complete ? "Edeltäjiä: " : "Edeltäjiä vähintään: ") + relations.blockedBy.length +
          (dependencyGraph.complete ? " · Estää: " : " · Estää vähintään: ") + relations.blocking.length));
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
        (dependencyGraph.complete ? "Edeltäjiä: " : "Edeltäjiä vähintään: ") + relations.blockedBy.length +
        (dependencyGraph.complete ? "; estää: " : "; estää vähintään: ") + relations.blocking.length + ". "));
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
    if (!group.items.length) list.appendChild(makeElement("li", "", dependencyGraph.complete
      ? "GitHubiin ei ole kirjattu tähän suuntaan riippuvuuksia."
      : "Tämän suunnan riippuvuustietoja ei saatu kokonaan haettua."));
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
  dependencyGraph = cache.dependencies && typeof cache.dependencies.byIssue === "object"
    ? cache.dependencies : null;
  dependencySavedAt = Number.isFinite(cache.dependenciesSavedAt)
    ? cache.dependenciesSavedAt : null;
  populateAreaFilter();
  render();
  const age = Number.isFinite(cache.savedAt) ? Date.now() - cache.savedAt : Infinity;
  const stale = age > STALE_AFTER_MS;
  updateFreshness(
    (isError ? "Julkaistun aineiston haku epäonnistui. " : "")
      + (stale ? "Vanhentunut paikallinen välimuistitieto. " : "Paikallinen välimuistitieto. ")
      + "Viimeisin onnistunut aineisto muodostettiin "
      + formatDate(cache.savedAt) + " (" + formatAge(cache.savedAt) + ").",
    "warning"
  );
  updateDependencyStatus(dependencyGraph
    ? "Riippuvuudet ovat paikalliseen välimuistiin tallennetusta aineistosta ("
      + formatDate(dependencySavedAt || cache.savedAt) + ")."
    : "Välimuistissa ei ole riippuvuustietoja.", true);
}

async function refreshIssues() {
  const button = document.getElementById("kanban-refresh");
  button.disabled = true;
  button.textContent = "Haetaan aineistoa…";
  try {
    const dataset = await fetchPublishedDataset();
    const issues = normalizeIssues(dataset.issues);
    if (issues.length !== dataset.issue_count) {
      throw new Error("Julkaistun aineiston issue-määrä ei vastaa sen sisältöä.");
    }
    const graph = buildDependencyGraph(issues, dataset.dependencies, true);
    const generatedAt = Date.parse(dataset.generated_at);
    allIssues = issues;
    savedAt = generatedAt;
    dependencyGraph = graph;
    dependencySavedAt = generatedAt;
    selectedDependencyIssue = null;
    safeWriteCache(issues, generatedAt, graph, generatedAt);
    populateAreaFilter();
    render();
    document.getElementById("kanban-api-error").hidden = true;
    // Riippuvuuksien lataustila näkyy jo yläpuolen aineiston päivitystiedossa.
    updateDependencyStatus("");
    const stale = Date.now() - generatedAt > STALE_AFTER_MS;
    updateFreshness((stale ? "Julkaistu aineisto on vanhentunut. " : "Julkaistu aineisto on käytössä. ")
      + "Aineisto muodostettiin " + formatDate(generatedAt) + " ("
      + formatAge(generatedAt) + ").", stale ? "warning" : "info");
  } catch (error) {
    const cache = safeReadCache();
    if (cache) showCachedData(cache, true);
    const message = error instanceof Error ? error.message : "Julkaistun aineiston haku epäonnistui.";
    const errorPanel = document.getElementById("kanban-api-error");
    errorPanel.hidden = false;
    errorPanel.textContent = message + (cache
      ? " Näytämme erikseen merkityn paikallisen välimuistin."
      : " Käyttökelpoista välimuistia ei ole saatavilla.");
    if (!cache) {
      allIssues = [];
      dependencyGraph = null;
      render();
      document.getElementById("kanban-empty").hidden = false;
      document.getElementById("kanban-empty").textContent =
        "Tikettejä ei voitu ladata. Yritä hakea julkaistu aineisto uudelleen.";
      updateFreshness("Päivitys ei onnistunut; tietojen ajantasaisuutta ei voida vahvistaa.", "warning");
      updateDependencyStatus("Riippuvuustietoja ei ole käytettävissä.", true);
    }
  } finally {
    button.disabled = false;
    button.textContent = "Päivitä aineisto";
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
