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

  const { label, option } = resolveStatusOption(
    issue.labels || [], config.project.options
  );
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
  return { issueNumber, label, status: option.name, itemId };
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
  if (!issue || issue.pull_request) {
    console.log("Ohitetaan tapahtuma, joka ei koske tavallista issuea.");
    return;
  }
  const config = JSON.parse(await readFile(CONFIG_PATH, "utf8"));
  const result = await syncIssueStatus({
    repository, issueNumber: issue.number,
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
