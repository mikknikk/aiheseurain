import { readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import path from "node:path";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const CONFIG_PATH = path.join(ROOT, ".github/project-status-sync.json");

export function resolveStatusOption(labels, options) {
  const statusLabels = labels
    .map((label) => typeof label === "string" ? label : label?.name)
    .filter((name) => typeof name === "string" && name.startsWith("status:"));
  if (statusLabels.length !== 1) {
    throw new Error(`Issuella pitää olla täsmälleen yksi status:-label; löytyi ${statusLabels.length}.`);
  }
  const option = options[statusLabels[0]];
  if (!option?.id) {
    throw new Error(`Tuntematon tilalabel: ${statusLabels[0]}.`);
  }
  return { label: statusLabels[0], option };
}


/**
 * Muuntaa issue-tiketin yhden priority:-labelin Projectin Priority-vaihtoehdoksi.
 * Sallii vaihtoehdon nimen perässä selitteen, esimerkiksi "P1 – Korkea".
 */
export function resolvePriorityOption(labels, options) {
  const priorityLabels = labels
    .map((label) => typeof label === "string" ? label : label?.name)
    .filter((name) => typeof name === "string" && name.startsWith("priority:"));
  if (priorityLabels.length !== 1) {
    throw new Error(`Issuella pitää olla täsmälleen yksi priority:-label; löytyi ${priorityLabels.length}.`);
  }
  const match = priorityLabels[0].match(/^priority:(P[0-3])$/);
  if (!match) throw new Error(`Tuntematon prioriteettilabel: ${priorityLabels[0]}.`);
  const code = match[1];
  const candidates = options.filter((option) =>
    option.name === code || option.name.startsWith(`${code} –`) ||
    option.name.startsWith(`${code} -`) || option.name.startsWith(`${code} —`)
  );
  if (candidates.length !== 1 || !candidates[0].id) {
    throw new Error(`Projectin Priority-kentästä pitää löytyä täsmälleen yksi vaihtoehto tunnukselle ${code}; löytyi ${candidates.length}.`);
  }
  return { label: priorityLabels[0], code, option: candidates[0] };
}

/**
 * Hakee Priority-kentän tunnisteen ja vaihtoehdot suoraan projektista.
 * Näin kentän luomisen yhteydessä syntyviä GitHub-tunnisteita ei tarvitse arvata
 * tai kopioida käsin repositorion asetuksiin.
 */
export async function findProjectSingleSelectField({
  token, projectId, fieldName, fetchImpl = fetch
}) {
  const query = `
    query($projectId: ID!) {
      node(id: $projectId) {
        ... on ProjectV2 {
          fields(first: 100) {
            nodes {
              ... on ProjectV2SingleSelectField {
                id
                name
                options { id name }
              }
            }
          }
        }
      }
    }`;
  const data = await graphql(token, query, { projectId }, fetchImpl);
  const fields = data.node?.fields?.nodes || [];
  const matches = fields.filter((field) => field?.name === fieldName && field.id);
  if (matches.length !== 1) {
    throw new Error(`Projectista pitää löytyä täsmälleen yksi Single select -kenttä nimeltä "${fieldName}"; löytyi ${matches.length}.`);
  }
  return matches[0];
}

/**
 * Päivittää yhden Projectin Single select -kentän ja lukee arvon takaisin.
 * Takaisinluku varmistaa, ettei pelkkää onnistunutta API-vastausta tulkita
 * virheellisesti oikeaksi lopputulokseksi.
 */
export async function updateProjectSingleSelectField({
  token, projectId, fieldId, fieldName, optionId, itemId, fetchImpl = fetch
}) {
  const mutation = `
    mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $optionId: String!) {
      updateProjectV2ItemFieldValue(input: {
        projectId: $projectId,
        itemId: $itemId,
        fieldId: $fieldId,
        value: { singleSelectOptionId: $optionId }
      }) {
        projectV2Item { id }
      }
    }`;
  const data = await graphql(token, mutation, {
    projectId, itemId, fieldId, optionId
  }, fetchImpl);
  if (!data.updateProjectV2ItemFieldValue?.projectV2Item?.id) {
    throw new Error(`GitHub Projectin ${fieldName}-kentän päivitys ei palauttanut onnistunutta tulosta.`);
  }
  const verifyQuery = `
    query($itemId: ID!, $fieldName: String!) {
      node(id: $itemId) {
        ... on ProjectV2Item {
          fieldValueByName(name: $fieldName) {
            ... on ProjectV2ItemFieldSingleSelectValue {
              name
              optionId
            }
          }
        }
      }
    }`;
  const verified = await graphql(token, verifyQuery, { itemId, fieldName }, fetchImpl);
  const actual = verified.node?.fieldValueByName;
  if (actual?.optionId !== optionId) {
    throw new Error(`Projectin ${fieldName}-varmistus epäonnistui: odotettiin ${optionId}, saatiin ${actual?.optionId ?? "ei arvoa"}.`);
  }
}

async function responseJson(response, context) {
  const body = await response.json();
  if (!response.ok) {
    throw new Error(`${context}: HTTP ${response.status}: ${JSON.stringify(body)}`);
  }
  return body;
}

export async function graphql(token, query, variables = {}, fetchImpl = fetch) {
  const response = await fetchImpl("https://api.github.com/graphql", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      Accept: "application/vnd.github+json",
      "Content-Type": "application/json",
      "X-GitHub-Api-Version": "2022-11-28"
    },
    body: JSON.stringify({ query, variables })
  });
  const body = await responseJson(response, "GitHub GraphQL");
  if (body.errors?.length) {
    throw new Error(`GitHub GraphQL -virhe: ${body.errors.map((error) => error.message).join("; ")}`);
  }
  return body.data;
}

export async function findProjectItem({
  token, projectId, issueNodeId, fetchImpl = fetch
}) {
  const query = `
    query($projectId: ID!, $after: String) {
      node(id: $projectId) {
        ... on ProjectV2 {
          items(first: 100, after: $after) {
            nodes {
              id
              content {
                ... on Issue { id }
              }
            }
            pageInfo { hasNextPage endCursor }
          }
        }
      }
    }`;
  let after = null;
  do {
    const data = await graphql(token, query, { projectId, after }, fetchImpl);
    const project = data.node;
    if (!project) throw new Error("GitHub Projectia ei löytynyt annetulla PROJECT_ID-tunnisteella.");
    const item = project.items.nodes.find((candidate) => candidate.content?.id === issueNodeId);
    if (item) return item.id;
    const page = project.items.pageInfo;
    after = page.hasNextPage ? page.endCursor : null;
  } while (after);
  return null;
}

export async function ensureProjectItem({
  token, projectId, issueNodeId, fetchImpl = fetch
}) {
  let itemId = await findProjectItem({ token, projectId, issueNodeId, fetchImpl });
  if (itemId) return itemId;

  const mutation = `
    mutation($projectId: ID!, $contentId: ID!) {
      addProjectV2ItemById(input: { projectId: $projectId, contentId: $contentId }) {
        item { id }
      }
    }`;
  try {
    const data = await graphql(token, mutation, { projectId, contentId: issueNodeId }, fetchImpl);
    itemId = data.addProjectV2ItemById?.item?.id;
    if (itemId) return itemId;
  } catch (error) {
    // Projectin oma automaattinen lisäys voi ehtiä lisätä kortin samanaikaisesti.
    const concurrentlyAdded = await findProjectItem({
      token, projectId, issueNodeId, fetchImpl
    });
    if (concurrentlyAdded) return concurrentlyAdded;
    throw error;
  }
  throw new Error("Issuen lisääminen GitHub Projectiin ei palauttanut kortin tunnistetta.");
}

export async function updateProjectStatus({
  token, projectId, fieldId, optionId, itemId, fetchImpl = fetch
}) {
  const mutation = `
    mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $optionId: String!) {
      updateProjectV2ItemFieldValue(input: {
        projectId: $projectId,
        itemId: $itemId,
        fieldId: $fieldId,
        value: { singleSelectOptionId: $optionId }
      }) {
        projectV2Item { id }
      }
    }`;
  const data = await graphql(token, mutation, {
    projectId, itemId, fieldId, optionId
  }, fetchImpl);
  if (!data.updateProjectV2ItemFieldValue?.projectV2Item?.id) {
    throw new Error("GitHub Projectin Status-kentän päivitys ei palauttanut onnistunutta tulosta.");
  }

  // Lue arvo takaisin: onnistunut mutaatio ei yksin todista oikeaa lopputilaa.
  const verifyQuery = `
    query($itemId: ID!) {
      node(id: $itemId) {
        ... on ProjectV2Item {
          fieldValueByName(name: "Status") {
            ... on ProjectV2ItemFieldSingleSelectValue {
              name
              optionId
            }
          }
        }
      }
    }`;
  const verified = await graphql(token, verifyQuery, { itemId }, fetchImpl);
  const actual = verified.node?.fieldValueByName;
  if (actual?.optionId !== optionId) {
    throw new Error(`Projectin Status-varmistus epäonnistui: odotettiin ${optionId}, saatiin ${actual?.optionId ?? "ei arvoa"}.`);
  }
}

export async function syncIssueStatus({
  repository, issueNumber, githubToken, projectsToken, config, fetchImpl = fetch
}) {
  if (repository !== config.repository) {
    throw new Error(`Repository ei vastaa Project-määritystä: ${repository}`);
  }
  const issueResponse = await fetchImpl(
    `https://api.github.com/repos/${repository}/issues/${issueNumber}`,
    {
      headers: {
        Authorization: `Bearer ${githubToken}`,
        Accept: "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
      }
    }
  );
  const issue = await responseJson(issueResponse, "Issuen nykyisten tietojen haku");
  if (issue.pull_request) return { skipped: "pull_request" };

  // Projektiin kuuluvat vain kehityskomponentilla merkityt issuet.
  const componentLabels = (issue.labels || [])
    .map((label) => typeof label === "string" ? label : label?.name)
    .filter((name) => typeof name === "string" && name.startsWith("component:"));
  if (componentLabels.length === 0) return { skipped: "not_a_development_issue" };
  if (componentLabels.length !== 1) {
    throw new Error(`Issuella pitää olla täsmälleen yksi component:-label; löytyi ${componentLabels.length}.`);
  }

  const { label, option } = resolveStatusOption(
    issue.labels || [], config.project.options
  );
  const priorityField = await findProjectSingleSelectField({
    token: projectsToken, projectId: config.project.id,
    fieldName: config.project.priority_field_name || "Priority", fetchImpl
  });
  const priority = resolvePriorityOption(issue.labels || [], priorityField.options);
  const project = config.project;
  const itemId = await ensureProjectItem({
    token: projectsToken, projectId: project.id,
    issueNodeId: issue.node_id, fetchImpl
  });
  await updateProjectStatus({
    token: projectsToken, projectId: project.id,
    fieldId: project.status_field_id, optionId: option.id,
    itemId, fetchImpl
  });
  await updateProjectSingleSelectField({
    token: projectsToken, projectId: project.id,
    fieldId: priorityField.id, fieldName: priorityField.name,
    optionId: priority.option.id, itemId, fetchImpl
  });
  return {
    issueNumber, statusLabel: label, status: option.name,
    priorityLabel: priority.label, priority: priority.code, itemId
  };
}

async function main() {
  const eventPath = process.env.GITHUB_EVENT_PATH;
  const repository = process.env.GITHUB_REPOSITORY;
  const githubToken = process.env.GITHUB_TOKEN;
  const projectsToken = process.env.PROJECTS_TOKEN;
  if (!eventPath || !repository || !githubToken || !projectsToken) {
    throw new Error("Ympäristöstä puuttuu GITHUB_EVENT_PATH, GITHUB_REPOSITORY, GITHUB_TOKEN tai PROJECTS_TOKEN.");
  }
  const event = JSON.parse(await readFile(eventPath, "utf8"));
  const issue = event.issue;
  // Tavallisen issue-tapahtuman lisäksi yksittäisen issuen voi täsmäyttää
  // käsin workflow_dispatch-ajolla antamalla issue_number-syötteen.
  const issueNumber = issue?.number ?? Number(event.inputs?.issue_number);
  if (!Number.isInteger(issueNumber) || issueNumber < 1 || issue?.pull_request) {
    console.log("Ohitetaan tapahtuma, josta ei saada kelvollista tavallisen issuen numeroa.");
    return;
  }
  const config = JSON.parse(await readFile(CONFIG_PATH, "utf8"));
  const result = await syncIssueStatus({
    repository, issueNumber,
    githubToken, projectsToken, config
  });
  console.log(JSON.stringify(result));
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  main().catch((error) => {
    console.error(error);
    process.exitCode = 1;
  });
}
