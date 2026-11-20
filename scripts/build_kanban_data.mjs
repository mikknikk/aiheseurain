#!/usr/bin/env node
/**
 * Päivittää Kehitysjonon julkaistavan JSON-aineiston GitHubin kanonisista tiedoista.
 *
 * Tavallisissa issue-tapahtumissa päivitetään vain muuttunut tiketti ja sen
 * blocked_by-suhteet. Päivittäinen täsmäytys hakee koko issue-listan ja kaikki
 * riippuvuudet, jotta myös GitHubin käyttöliittymässä tehdyt muutokset löytyvät.
 * Aineisto tallennetaan repositorioon, jolloin seuraava Actions-ajo voi käyttää
 * edellistä versiota välimuistina. Selain lukee vain valmista JSON-tiedostoa.
 */

import { mkdir, readFile, rename, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { pathToFileURL } from "node:url";

const API_ROOT = "https://api.github.com";
const API_VERSION = "2022-11-28";
const PER_PAGE = 100;
const MAX_PAGES = 100;
const CONCURRENCY = 4;
const DEFAULT_OUTPUT = "data/kehitysjono.json";

/** Rajaa API:n issue-oliosta julkiseen näkymään vain tarpeelliset kentät. */
export function publicIssue(issue) {
  if (!issue || !Number.isSafeInteger(Number(issue.number)) || !issue.title || !issue.html_url) {
    throw new Error("GitHub palautti issue-tietueen, josta puuttuu pakollisia kenttiä.");
  }
  return {
    number: Number(issue.number),
    title: String(issue.title),
    html_url: String(issue.html_url),
    state: issue.state === "closed" ? "closed" : "open",
    labels: (Array.isArray(issue.labels) ? issue.labels : [])
      .map((label) => typeof label === "string" ? label : label?.name)
      .filter((name) => typeof name === "string" && name.length > 0)
      .map((name) => ({ name })),
    updated_at: issue.updated_at || null
  };
}

/** Tekee GitHub API -pyynnön ja antaa virheestä turvallisen, lyhyen ilmoituksen. */
export async function requestJson(url, token, fetchImpl = fetch) {
  const response = await fetchImpl(url, {
    headers: {
      Accept: "application/vnd.github+json",
      Authorization: "Bearer " + token,
      "X-GitHub-Api-Version": API_VERSION
    }
  });
  if (!response.ok) {
    throw new Error(response.status === 403 || response.status === 429
      ? "GitHub API rajoitti Kehitysjonon päivitystä (HTTP " + response.status + ")."
      : "GitHub API -haku epäonnistui (HTTP " + response.status + ").");
  }
  return response.json();
}

/** Hakee kaikki issue-sivut; pull requestit eivät kuulu Kehitysjonoon. */
export async function fetchAllIssues(owner, repo, token, fetchImpl = fetch) {
  const result = [];
  for (let page = 1; page <= MAX_PAGES; page += 1) {
    const url = new URL(API_ROOT + "/repos/" + owner + "/" + repo + "/issues");
    url.search = new URLSearchParams({
      state: "all", per_page: String(PER_PAGE), page: String(page),
      sort: "updated", direction: "desc"
    }).toString();
    const items = await requestJson(url, token, fetchImpl);
    if (!Array.isArray(items)) throw new Error("GitHub palautti virheellisen issue-listan.");
    result.push(...items.filter((item) => item && !item.pull_request).map(publicIssue));
    if (items.length < PER_PAGE) {
      return [...new Map(result.map((issue) => [issue.number, issue])).values()]
        .sort((a, b) => a.number - b.number);
    }
  }
  throw new Error("Issue-haku ylitti 10 000 tietueen turvarajan; välimuistia ei julkaista.");
}

/** Hakee yhden tiketin kaikki edeltävät työt sivutuksineen. */
export async function fetchIssueDependencies(owner, repo, issueNumber, token, fetchImpl = fetch) {
  const blockedBy = [];
  for (let page = 1; page <= MAX_PAGES; page += 1) {
    const url = new URL(API_ROOT + "/repos/" + owner + "/" + repo
      + "/issues/" + issueNumber + "/dependencies/blocked_by");
    url.search = new URLSearchParams({ per_page: String(PER_PAGE), page: String(page) }).toString();
    const items = await requestJson(url, token, fetchImpl);
    if (!Array.isArray(items)) {
      throw new Error("Tiketin #" + issueNumber + " riippuvuusvastaus ei ollut lista.");
    }
    blockedBy.push(...items.map(publicIssue));
    if (items.length < PER_PAGE) {
      return { issueNumber: Number(issueNumber), blockedBy };
    }
  }
  throw new Error("Tiketin #" + issueNumber + " riippuvuushaku ylitti sivutusrajan.");
}

/** Rajoittaa samanaikaiset riippuvuushaut neljään API-työntekijään. */
export async function fetchAllDependencies(owner, repo, issues, token, fetchImpl = fetch) {
  const result = new Array(issues.length);
  let nextIndex = 0;
  async function worker() {
    while (nextIndex < issues.length) {
      const index = nextIndex++;
      result[index] = await fetchIssueDependencies(
        owner, repo, issues[index].number, token, fetchImpl
      );
    }
  }
  await Promise.all(Array.from(
    { length: Math.min(CONCURRENCY, Math.max(1, issues.length)) }, worker
  ));
  return result;
}

/** Tarkistaa, että välimuisti on aiemman skeeman mukainen ja käyttökelpoinen. */
export function validatePreviousDataset(dataset) {
  if (!dataset || dataset.schema_version !== 1 || dataset.status !== "complete"
      || !Array.isArray(dataset.issues) || !Array.isArray(dataset.dependencies)
      || dataset.issue_count !== dataset.issues.length
      || dataset.dependencies.length !== dataset.issues.length) {
    throw new Error("Aiempi Kehitysjonon välimuisti on virheellinen; tehdään täysi muodostus.");
  }
  return dataset;
}

/** Muodostaa täydellisen aineiston, jota käytetään myös ensimmäisessä käynnistyksessä. */
export async function buildFullDataset({ owner, repo, token, fetchImpl = fetch, now = new Date() }) {
  const issues = await fetchAllIssues(owner, repo, token, fetchImpl);
  const dependencies = await fetchAllDependencies(owner, repo, issues, token, fetchImpl);
  return assembleDataset(issues, dependencies, now, now);
}

/** Päivittää vain yhden issue-tietueen ja sen riippuvuudet aiempaan välimuistiin. */
export function buildIncrementalDataset({ previous, issue, deleted = false, dependencies = null, now = new Date() }) {
  validatePreviousDataset(previous);
  const issuesByNumber = new Map(previous.issues.map((item) => [item.number, item]));
  const dependenciesByNumber = new Map(previous.dependencies.map((item) => [item.issueNumber, item]));

  if (deleted) {
    issuesByNumber.delete(Number(issue.number));
    dependenciesByNumber.delete(Number(issue.number));
    // Poistettu tiketti poistetaan myös muiden tikettien edeltäjälistoilta.
    for (const relation of dependenciesByNumber.values()) {
      relation.blockedBy = relation.blockedBy.filter((item) => item.number !== Number(issue.number));
    }
  } else {
    const normalized = publicIssue(issue);
    issuesByNumber.set(normalized.number, normalized);
    if (!Array.isArray(dependencies)) {
      throw new Error("Muuttuneen tiketin riippuvuuksia ei saatu; vanhaa välimuistia ei korvata.");
    }
    dependenciesByNumber.set(normalized.number, {
      issueNumber: normalized.number,
      blockedBy: dependencies.map(publicIssue)
    });
  }

  const issues = [...issuesByNumber.values()].sort((a, b) => a.number - b.number);
  const relations = [...dependenciesByNumber.values()]
    .filter((item) => issuesByNumber.has(item.issueNumber))
    .sort((a, b) => a.issueNumber - b.issueNumber);
  return assembleDataset(issues, relations, now, previous.full_sync_at || previous.generated_at);
}

/** Tarkistaa rivimäärät ja muodostaa yhden täydellisen julkaisuasiakirjan. */
export function assembleDataset(issues, dependencies, now = new Date(), fullSyncAt = now) {
  const issueNumbers = new Set(issues.map((issue) => issue.number));
  if (issueNumbers.size !== issues.length || dependencies.length !== issues.length) {
    throw new Error("Issue- ja riippuvuustietueiden määrät eivät täsmää.");
  }
  for (const relation of dependencies) {
    if (!issueNumbers.has(relation.issueNumber) || !Array.isArray(relation.blockedBy)) {
      throw new Error("Riippuvuusaineisto on puutteellinen.");
    }
    for (const blocker of relation.blockedBy) {
      if (!Number.isSafeInteger(blocker.number)) throw new Error("Riippuvuudessa on virheellinen issue-numero.");
    }
  }
  return {
    schema_version: 1,
    generated_at: now.toISOString(),
    full_sync_at: new Date(fullSyncAt).toISOString(),
    status: "complete",
    issue_count: issues.length,
    dependency_relation_count: dependencies.reduce((sum, item) => sum + item.blockedBy.length, 0),
    issues,
    dependencies
  };
}

/** Lukee edellisen onnistuneen JSONin; puuttuva tiedosto tarkoittaa ensikäynnistystä. */
export async function readPreviousDataset(path) {
  try {
    return validatePreviousDataset(JSON.parse(await readFile(path, "utf8")));
  } catch (error) {
    if (error?.code === "ENOENT") return null;
    throw error;
  }
}

/** Kirjoittaa ensin väliaikaistiedoston ja vaihtaa sen vasta valmiin JSONin tilalle. */
export async function writeDataset(dataset, outputPath) {
  const destination = resolve(outputPath);
  const temporary = destination + ".tmp";
  await mkdir(dirname(destination), { recursive: true });
  await writeFile(temporary, JSON.stringify(dataset, null, 2) + "\n", "utf8");
  await rename(temporary, destination);
}

/** Valitsee täyden tai yhden tiketin päivityksen Actions-tapahtuman perusteella. */
async function main() {
  const [owner, repo] = String(process.env.GITHUB_REPOSITORY || "").split("/");
  const token = process.env.GITHUB_TOKEN;
  const eventPath = process.env.GITHUB_EVENT_PATH;
  const outputPath = resolve(process.env.KANBAN_DATA_PATH || DEFAULT_OUTPUT);
  if (!owner || !repo || !token || !eventPath) {
    throw new Error("GitHub Actions -ympäristöstä puuttuu tarvittava käynnistystieto.");
  }

  const event = JSON.parse(await readFile(eventPath, "utf8"));
  const eventName = process.env.GITHUB_EVENT_NAME || "";
  const previous = await readPreviousDataset(outputPath);
  const fetchImpl = fetch;
  let dataset;

  if (!previous || eventNameIsFullSync(event, eventName)) {
    dataset = await buildFullDataset({ owner, repo, token, fetchImpl });
  } else {
    let issue = event.issue || null;
    const requestedNumber = Number(event.inputs?.issue_number || 0);
    if (!issue && requestedNumber > 0) {
      issue = await requestJson(
        API_ROOT + "/repos/" + owner + "/" + repo + "/issues/" + requestedNumber,
        token, fetchImpl
      );
    }
    if (!issue || issue.pull_request || !Number.isSafeInteger(Number(issue.number))) {
      throw new Error("Yhden tiketin päivitys ei sisältänyt kelvollista GitHub-issuea.");
    }
    const deleted = event.action === "deleted";
    const dependencies = deleted ? null
      : (await fetchIssueDependencies(owner, repo, issue.number, token, fetchImpl)).blockedBy;
    dataset = buildIncrementalDataset({ previous, issue, deleted, dependencies, now: new Date() });
  }

  await writeDataset(dataset, outputPath);
  process.stdout.write(
    "Kehitysjonon JSON päivitetty (" + (eventNameIsFullSync(event, eventName) ? "täysi täsmäytys" : "muutos") + "): "
    + dataset.issue_count + " tikettiä, " + dataset.dependency_relation_count + " riippuvuussuhdetta.\n"
  );
}

/** Täysi muodostus tehdään ajastuksessa, manuaalisessa ajossa ja ylläpitokoodin muutoksissa. */
export function eventNameIsFullSync(event, eventName) {
  return eventName === "schedule" || eventName === "push"
    || (eventName === "workflow_dispatch" && !event?.inputs?.issue_number);
}

if (process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) {
  main().catch((error) => {
    process.stderr.write("Kehitysjonon JSON-päivitys epäonnistui: "
      + (error instanceof Error ? error.message : "tuntematon virhe") + "\n");
    process.exitCode = 1;
  });
}
