/**
 * Käsittelee GitHub-issueen kirjoitetun, yksiselitteisen riippuvuuspyynnön.
 *
 * Skripti käyttää GitHubin natiivia blocked_by-rajapintaa. Se ei ylläpidä
 * omaa riippuvuustietokantaa eikä muuta tikettien tiloja tai muita tunnisteita.
 * Pyyntö merkitään issue-kuvaukseen HTML-kommentilla, jotta tavallinen teksti
 * tai pelkkä tikettiviittaus ei koskaan käynnistä riippuvuuden muutosta.
 */

import { readFileSync } from "node:fs";

const API_VERSION = "2022-11-28";
const MARKER_PATTERN = /<!--\s*aiheseurain-dependency-request\s*([\s\S]*?)-->/g;

/**
 * Etsii tiketin kuvauksesta täsmälleen yhden koneellisen pyyntölohkon.
 * Pyyntölohkon JSON hyväksyy vain eksplisiittiset lisäys- ja poistamislistat.
 */
export function parseDependencyRequest(body, currentIssueNumber) {
  const matches = [...String(body ?? "").matchAll(MARKER_PATTERN)];
  if (matches.length === 0) return null;
  if (matches.length !== 1) {
    throw new Error("Tiketissä pitää olla enintään yksi riippuvuuspyyntölohko.");
  }

  const marker = matches[0][0];
  let request;
  try {
    request = JSON.parse(matches[0][1].trim());
  } catch {
    throw new Error("Riippuvuuspyyntölohkon JSON ei ole kelvollinen.");
  }

  if (!request || typeof request !== "object" || Array.isArray(request)) {
    throw new Error("Riippuvuuspyynnön pitää olla JSON-olio.");
  }
  const allowedKeys = new Set(["blocked_by", "remove_blocked_by"]);
  if (Object.keys(request).some((key) => !allowedKeys.has(key))) {
    throw new Error("Riippuvuuspyynnössä on tuntematon kenttä.");
  }

  const additions = request.blocked_by ?? [];
  const removals = request.remove_blocked_by ?? [];
  for (const [name, values] of [["blocked_by", additions], ["remove_blocked_by", removals]]) {
    if (!Array.isArray(values) || values.length > 10 ||
        values.some((value) => !Number.isSafeInteger(value) || value < 1)) {
      throw new Error(`Kentän ${name} pitää olla enintään 10 positiivisen issue-numeron lista.`);
    }
    if (new Set(values).size !== values.length) {
      throw new Error(`Kentässä ${name} on sama issue-numero useammin kuin kerran.`);
    }
    if (values.includes(currentIssueNumber)) {
      throw new Error("Tiketti ei voi olla riippuvainen itsestään.");
    }
  }

  if (additions.length === 0 && removals.length === 0) {
    throw new Error("Riippuvuuspyyntö ei sisällä lisäystä eikä poistoa.");
  }
  if (additions.some((number) => removals.includes(number))) {
    throw new Error("Samaa riippuvuutta ei voi lisätä ja poistaa samassa pyynnössä.");
  }

  return { additions, removals, marker };
}

/**
 * Tarkistaa, johtaisiko uuden suhteen lisääminen riippuvuussykliin.
 *
 * Jos kohdeissue odottaa blocker-issueä, kuljemme blockerista sen omiin
 * edeltäviin töihin. Jos kohde löytyy tältä polulta, uuden suhteen lisääminen
 * muodostaisi kehän. Rajattu solmumäärä estää poikkeuksellisen suuren verkon
 * käsittelyn loputtomasti; rajan ylittyessä pyyntö hylätään turvallisesti.
 */
export async function hasDependencyCycle(blockerNumber, targetNumber, fetchBlockedBy) {
  const pending = [blockerNumber];
  const visited = new Set();

  while (pending.length > 0) {
    const current = pending.shift();
    if (current === targetNumber) return true;
    if (visited.has(current)) continue;
    visited.add(current);
    if (visited.size > 1000) {
      throw new Error("Riippuvuusverkko on liian suuri syklitarkistukseen; muutosta ei tehty.");
    }
    const blockers = await fetchBlockedBy(current);
    for (const blocker of blockers) {
      if (Number.isSafeInteger(blocker.number) && !visited.has(blocker.number)) {
        pending.push(blocker.number);
      }
    }
  }
  return false;
}

/**
 * Tarkistaa tiketit ja toteuttaa pyydetyt lisäykset/poistot idempotentisti.
 * Riippuvuuden suunta on aina: targetIssue blocked_by blockerIssue.
 */
export async function applyDependencyRequest({
  targetIssue, additions, removals, fetchIssue, fetchBlockedBy,
  addDependency, removeDependency
}) {
  const result = { added: [], alreadyPresent: [], removed: [], alreadyAbsent: [] };

  for (const blockerNumber of additions) {
    const blocker = await fetchIssue(blockerNumber);
    if (!blocker || blocker.pull_request) {
      throw new Error(`#${blockerNumber} ei ole olemassa oleva saman repositorion issue.`);
    }

    const current = await fetchBlockedBy(targetIssue.number);
    if (current.some((item) => item.number === blockerNumber)) {
      result.alreadyPresent.push(blockerNumber);
      continue;
    }

    if (await hasDependencyCycle(blockerNumber, targetIssue.number, fetchBlockedBy)) {
      throw new Error(`Riippuvuus #${targetIssue.number} → #${blockerNumber} muodostaisi syklin.`);
    }
    await addDependency(targetIssue.number, blocker.id);
    result.added.push(blockerNumber);
  }

  for (const blockerNumber of removals) {
    const blocker = await fetchIssue(blockerNumber);
    if (!blocker || blocker.pull_request) {
      throw new Error(`#${blockerNumber} ei ole olemassa oleva saman repositorion issue.`);
    }
    const current = await fetchBlockedBy(targetIssue.number);
    if (!current.some((item) => item.number === blockerNumber)) {
      result.alreadyAbsent.push(blockerNumber);
      continue;
    }
    await removeDependency(targetIssue.number, blocker.id);
    result.removed.push(blockerNumber);
  }

  return result;
}

/** Suorittaa GitHub REST -pyynnön ja muuntaa API-virheet ymmärrettäviksi. */
async function githubRequest(urlOrPath, token, options = {}) {
  const url = urlOrPath.startsWith("https://")
    ? urlOrPath
    : `https://api.github.com${urlOrPath}`;
  const response = await fetch(url, {
    ...options,
    headers: {
      Accept: "application/vnd.github+json",
      Authorization: `Bearer ${token}`,
      "X-GitHub-Api-Version": API_VERSION,
      ...(options.body ? { "Content-Type": "application/json" } : {}),
      ...options.headers
    }
  });
  const text = await response.text();
  let data = null;
  try { data = text ? JSON.parse(text) : null; } catch { /* Säilytä virheviesti tekstinä. */ }
  if (!response.ok) {
    const message = data?.message || `HTTP ${response.status}`;
    throw new Error(`GitHub API hylkäsi pyynnön (${response.status}): ${message}`);
  }
  return { data, headers: response.headers };
}

/** Hakee kaikki sivut esimerkiksi blocked_by-listasta. */
async function githubPaginate(path, token) {
  const results = [];
  let next = `https://api.github.com${path}?per_page=100`;
  while (next) {
    const response = await githubRequest(next, token);
    if (!Array.isArray(response.data)) {
      throw new Error("GitHubin riippuvuusrajapinta palautti odottamattoman vastauksen.");
    }
    results.push(...response.data);
    const link = response.headers.get("link") || "";
    const nextMatch = link.split(",").map((part) => part.trim())
      .find((part) => /rel="next"/.test(part));
    next = nextMatch?.match(/<([^>]+)>/)?.[1] ?? null;
  }
  return results;
}

/** Muotoilee käyttäjälle näkyvän yhteenvedon ilman tarpeettomia API-yksityiskohtia. */
function formatResult(result) {
  const lines = ["Aiheseurain käsitteli GitHubin natiivit tikettiriippuvuudet:"];
  if (result.added.length) lines.push(`- Lisätty: ${result.added.map((n) => `#${n}`).join(", ")}`);
  if (result.alreadyPresent.length) lines.push(`- Oli jo olemassa: ${result.alreadyPresent.map((n) => `#${n}`).join(", ")}`);
  if (result.removed.length) lines.push(`- Poistettu pyynnöstä: ${result.removed.map((n) => `#${n}`).join(", ")}`);
  if (result.alreadyAbsent.length) lines.push(`- Oli jo poissa: ${result.alreadyAbsent.map((n) => `#${n}`).join(", ")}`);
  return lines.join("\n");
}

/** GitHub Actions -käynnistyspiste. */
async function main() {
  const token = process.env.GITHUB_TOKEN;
  const repository = process.env.GITHUB_REPOSITORY;
  const eventPath = process.env.GITHUB_EVENT_PATH;
  if (!token || !repository || !eventPath) {
    throw new Error("GitHub Actions -ympäristöstä puuttuu tarvittava käynnistystieto.");
  }

  const event = JSON.parse(readFileSync(eventPath, "utf8"));
  if (event.action !== "edited" || !event.issue || event.issue.pull_request ||
      event.sender?.login === "github-actions[bot]") return;

  const [owner, repo] = repository.split("/");
  if (!owner || !repo) throw new Error("GITHUB_REPOSITORY ei ole muodossa omistaja/repositorio.");
  const issueNumber = event.issue.number;
  const issuePath = `/repos/${owner}/${repo}/issues/${issueNumber}`;
  const fetchIssue = async (number) =>
    (await githubRequest(`/repos/${owner}/${repo}/issues/${number}`, token)).data;
  const fetchBlockedBy = (number) =>
    githubPaginate(`/repos/${owner}/${repo}/issues/${number}/dependencies/blocked_by`, token);
  const addDependency = (number, issueId) =>
    githubRequest(`/repos/${owner}/${repo}/issues/${number}/dependencies/blocked_by`, token, {
      method: "POST", body: JSON.stringify({ issue_id: issueId })
    });
  const removeDependency = (number, issueId) =>
    githubRequest(`/repos/${owner}/${repo}/issues/${number}/dependencies/blocked_by/${issueId}`, token, {
      method: "DELETE"
    });

  try {
    const initial = await githubRequest(issuePath, token);
    const request = parseDependencyRequest(initial.data.body, issueNumber);
    if (!request) return;
    const targetIssue = await fetchIssue(issueNumber);
    if (!targetIssue || targetIssue.pull_request) {
      throw new Error("Kohde ei ole olemassa oleva GitHub-issue.");
    }
    const result = await applyDependencyRequest({
      targetIssue,
      additions: request.additions,
      removals: request.removals,
      fetchIssue,
      fetchBlockedBy,
      addDependency,
      removeDependency
    });

    // Hae kuvaus uudelleen ennen markerin poistoa, jotta väliin tullut käyttäjän
    // muokkaus ei yliaja tuoreempaa sisältöä. Poista vain täsmälleen käsitelty pyyntö.
    const latest = await githubRequest(issuePath, token);
    const latestRequest = parseDependencyRequest(latest.data.body, issueNumber);
    if (latestRequest?.marker === request.marker) {
      const updatedBody = String(latest.data.body ?? "").replace(request.marker, "").trimEnd();
      await githubRequest(issuePath, token, {
        method: "PATCH", body: JSON.stringify({ body: updatedBody })
      });
    }

    const summary = formatResult(result);
    await githubRequest(`/repos/${owner}/${repo}/issues/${issueNumber}/comments`, token, {
      method: "POST", body: JSON.stringify({ body: summary })
    });
    console.log(summary);
  } catch (error) {
    const message = error instanceof Error ? error.message : "Tuntematon virhe.";
    console.error(message);
    try {
      await githubRequest(`/repos/${owner}/${repo}/issues/${issueNumber}/comments`, token, {
        method: "POST",
        body: JSON.stringify({
          body: `Riippuvuuspyyntöä ei voitu käsitellä. Pyyntölohko säilytettiin uudelleenyritystä varten. Syy: ${message}`
        })
      });
    } catch (commentError) {
      console.error("Virheestä ei saatu lisättyä kommenttia:", commentError);
    }
    process.exitCode = 1;
  }
}

if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch((error) => {
    console.error(error instanceof Error ? error.message : error);
    process.exitCode = 1;
  });
}
