#!/usr/bin/env node
/**
 * Muodostaa Kehitysjonon julkisen JSON-aineiston GitHubin kanonisista issueista.
 *
 * Skripti ajetaan GitHub Actionsissa, jossa sillä on vain luku -oikeus
 * repositorion issueihin. Se hakee kaikki avoimet ja suljetut tiketit sekä
 * niiden natiivien riippuvuuksien edeltäjät. Tiedosto kirjoitetaan vasta,
 * kun kaikki haut ja rakennetarkistukset ovat onnistuneet.
 */

import { mkdir, rename, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { pathToFileURL } from "node:url";

const API_ROOT = "https://api.github.com";
const PER_PAGE = 100;
const MAX_PAGES = 100;
const CONCURRENCY = 4;

/** Muuntaa API:n issue-olion julkiseen aineistoon tarvittaviksi kentiksi. */
export function publicIssue(issue) {
  if (!issue || !Number.isInteger(Number(issue.number)) || !issue.title || !issue.html_url) {
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

/** Tekee rajatun GitHub API -pyynnön ja käsittelee virheet paljastamatta raakavastauksia. */
async function requestJson(url, token, fetchImpl) {
  const response = await fetchImpl(url, {
    headers: {
      Accept: "application/vnd.github+json",
      Authorization: "Bearer " + token,
      "X-GitHub-Api-Version": "2022-11-28"
    }
  });
  if (!response.ok) {
    const rateLimited = response.status === 403 || response.status === 429;
    throw new Error(rateLimited
      ? "GitHub API rajoitti aineiston muodostamista (HTTP " + response.status + ")."
      : "GitHub API -haku epäonnistui (HTTP " + response.status + ").");
  }
  return response.json();
}

/** Hakee kaikki avoimet ja suljetut issue-sivut; pull requestit jätetään pois. */
export async function fetchAllIssues(owner, repo, token, fetchImpl = fetch) {
  const issues = [];
  for (let page = 1; page <= MAX_PAGES; page += 1) {
    const url = new URL(API_ROOT + "/repos/" + owner + "/" + repo + "/issues");
    url.search = new URLSearchParams({
      state: "all", per_page: String(PER_PAGE), page: String(page),
      sort: "updated", direction: "desc"
    }).toString();
    const items = await requestJson(url, token, fetchImpl);
    if (!Array.isArray(items)) throw new Error("GitHub palautti virheellisen issue-listan.");
    issues.push(...items.filter((item) => item && !item.pull_request).map(publicIssue));
    if (items.length < PER_PAGE) {
      const unique = new Map(issues.map((issue) => [issue.number, issue]));
      return [...unique.values()].sort((a, b) => a.number - b.number);
    }
  }
  throw new Error("Issue-haku ylitti 10 000 tietueen turvarajan; aineistoa ei julkaista.");
}

/** Hakee yhden tiketin kaikki edeltävät riippuvuudet sivutuksineen. */
async function fetchIssueDependencies(owner, repo, issueNumber, token, fetchImpl) {
  const blockedBy = [];
  for (let page = 1; page <= MAX_PAGES; page += 1) {
    const url = new URL(API_ROOT + "/repos/" + owner + "/" + repo
      + "/issues/" + issueNumber + "/dependencies/blocked_by");
    url.search = new URLSearchParams({ per_page: String(PER_PAGE), page: String(page) }).toString();
    const items = await requestJson(url, token, fetchImpl);
    if (!Array.isArray(items)) throw new Error("Tiketin #" + issueNumber + " riippuvuusvastaus ei ollut lista.");
    blockedBy.push(...items.map(publicIssue));
    if (items.length < PER_PAGE) return { issueNumber, blockedBy };
  }
  throw new Error("Tiketin #" + issueNumber + " riippuvuushaku ylitti sivutusrajan.");
}

/** Hakee riippuvuudet neljän rinnakkaisen työntekijän rajatulla kuormalla. */
export async function fetchAllDependencies(owner, repo, issues, token, fetchImpl = fetch) {
  const results = new Array(issues.length);
  let nextIndex = 0;
  async function worker() {
    while (nextIndex < issues.length) {
      const index = nextIndex++;
      results[index] = await fetchIssueDependencies(
        owner, repo, issues[index].number, token, fetchImpl
      );
    }
  }
  const workers = Array.from(
    { length: Math.min(CONCURRENCY, Math.max(1, issues.length)) }, worker
  );
  await Promise.all(workers);
  return results;
}

/** Muodostaa vain täydellisen ja yksiselitteisesti versioidun julkaisuasiakirjan. */
export async function buildDataset({ owner, repo, token, fetchImpl = fetch, now = new Date() }) {
  if (!owner || !repo || !token) throw new Error("GitHub-omistaja, repositorio ja tunniste ovat pakollisia.");
  const issues = await fetchAllIssues(owner, repo, token, fetchImpl);
  const dependencies = await fetchAllDependencies(owner, repo, issues, token, fetchImpl);
  if (dependencies.length !== issues.length) {
    throw new Error("Riippuvuustietueiden määrä ei vastaa issueiden määrää.");
  }
  const issueNumbers = new Set(issues.map((issue) => issue.number));
  for (const relation of dependencies) {
    if (!issueNumbers.has(relation.issueNumber)) {
      throw new Error("Riippuvuustietue viittaa aineistosta puuttuvaan tikettiin.");
    }
    for (const blocker of relation.blockedBy) {
      if (!Number.isInteger(blocker.number)) {
        throw new Error("Riippuvuustietue sisältää virheellisen edeltäjän.");
      }
    }
  }
  return {
    schema_version: 1,
    generated_at: now.toISOString(),
    status: "complete",
    issue_count: issues.length,
    dependency_relation_count: dependencies.reduce((sum, item) => sum + item.blockedBy.length, 0),
    issues,
    dependencies
  };
}

/** Korvaa kohdetiedoston vasta täydellisen muodostuksen jälkeen atomisella nimenvaihdolla. */
export async function writeDataset(dataset, outputPath) {
  const destination = resolve(outputPath);
  const temporary = destination + ".tmp";
  await mkdir(dirname(destination), { recursive: true });
  await writeFile(temporary, JSON.stringify(dataset, null, 2) + "\n", "utf8");
  await rename(temporary, destination);
}

/** Käynnistää muodostuksen Actions-ympäristössä; virhe pysäyttää koko Pages-julkaisun. */
async function main() {
  const [owner, repo] = String(process.env.GITHUB_REPOSITORY || "").split("/");
  const token = process.env.GITHUB_TOKEN;
  const outputPath = resolve(process.env.KANBAN_DATA_PATH || "data/kehitysjono.json");
  const dataset = await buildDataset({ owner, repo, token });
  await writeDataset(dataset, outputPath);
  process.stdout.write(
    "Kehitysjonon aineisto muodostettu: " + dataset.issue_count + " tikettiä, "
    + dataset.dependency_relation_count + " riippuvuussuhdetta.\n"
  );
}

if (process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) {
  main().catch((error) => {
    process.stderr.write("Kehitysjonon aineiston muodostus epäonnistui: "
      + (error instanceof Error ? error.message : "tuntematon virhe") + "\n");
    process.exitCode = 1;
  });
}
