/**
 * Tarkistaa Aiheseuraimen README.md- ja docs/-hakemiston Markdown-dokumentaation.
 * Skripti ei muuta tiedostoja. Virheet estävät GitHub Actions -työnkulun onnistumisen.
 */
import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const files = ["README.md"];
const errors = [];

function collectMarkdown(directory) {
  for (const item of fs.readdirSync(directory, { withFileTypes: true })) {
    const full = path.join(directory, item.name);
    if (item.isDirectory()) collectMarkdown(full);
    else if (item.isFile() && item.name.toLowerCase().endsWith(".md")) files.push(path.relative(root, full));
  }
}

// Koodilohkojen sisältöä ei tulkita otsikoiksi tai Markdown-linkeiksi.
function visibleLines(markdown) {
  let inFence = false;
  return markdown.split(/\r?\n/).map((line) => {
    if (/^\s*(?:`{3,}|~{3,})/.test(line)) { inFence = !inFence; return ""; }
    return inFence ? "" : line;
  });
}

function slug(heading) {
  return heading.toLocaleLowerCase("en")
    .replace(/[\x60*_~]/g, "")
    .replace(/[^\p{L}\p{N}\s-]/gu, "")
    .trim().replace(/\s+/g, "-");
}

function versionOf(markdown) {
  const versions = [...markdown.matchAll(/^\*\*Versio:\*\*\s*(\d+\.\d+\.\d+)\s*$/gm)];
  return { value: versions[0]?.[1] ?? null, count: versions.length };
}

collectMarkdown(path.join(root, "docs"));

for (const relative of files) {
  const absolute = path.join(root, relative);
  if (!fs.existsSync(absolute)) { errors.push(relative + ": tiedostoa ei löydy."); continue; }
  const markdown = fs.readFileSync(absolute, "utf8");
  const lines = visibleLines(markdown);
  const headingLines = lines.filter((line) => /^#{1,6}\s/.test(line));
  const h1Count = headingLines.filter((line) => /^#\s/.test(line)).length;
  if (h1Count !== 1) errors.push(relative + ": dokumentissa pitää olla täsmälleen yksi H1-pääotsikko (nyt " + h1Count + ").");

  let previousLevel = 0;
  for (const line of headingLines) {
    const level = line.match(/^#+/)[0].length;
    if (previousLevel && level > previousLevel + 1) {
      errors.push(relative + ": otsikkotaso hyppää H" + previousLevel + "-tasolta H" + level + "-tasolle.");
    }
    previousLevel = level;
  }

  const version = versionOf(markdown);
  if (version.count > 1) errors.push(relative + ": **Versio:**-merkintä esiintyy useammin kuin kerran.");

  // Täsmälleen saman otsikon ja sisältöosion toistuminen on todennäköinen kopiointivirhe.
  const seenSections = new Set();
  for (let index = 0; index < lines.length; index++) {
    const heading = lines[index].match(/^(#{1,6})\s+(.+?)\s*#*\s*$/);
    if (!heading) continue;
    const level = heading[1].length;
    let end = lines.length;
    for (let next = index + 1; next < lines.length; next++) {
      const nextHeading = lines[next].match(/^(#{1,6})\s+/);
      if (nextHeading && nextHeading[1].length <= level) { end = next; break; }
    }
    const body = lines.slice(index + 1, end).join(" ").replace(/\s+/g, " ").trim();
    const signature = level + ":" + heading[2].trim() + ":" + body;
    if (body && seenSections.has(signature)) errors.push(relative + ': otsikko-osio "' + heading[2].trim() + '" ja sisältö toistuvat.');
    seenSections.add(signature);
  }

  // Tarkista suhteellisten Markdown-linkkien tiedostot ja Markdown-otsikkoankkurit.
  const linkPattern = /(?<!!)\[[^\]]+\]\(([^)\s]+)(?:\s+"[^"]*")?\)/g;
  for (const match of lines.join("\n").matchAll(linkPattern)) {
    const target = match[1];
    if (/^(?:[a-z][a-z0-9+.-]*:|\/\/)/i.test(target)) continue;
    const [filePart, fragment = ""] = decodeURIComponent(target).split("#", 2);
    const cleanFile = (filePart || "").split("?")[0];
    const targetFile = cleanFile
      ? path.resolve(root, path.dirname(relative), cleanFile)
      : absolute;
    if (!fs.existsSync(targetFile)) {
      errors.push(relative + ": sisäisen linkin kohdetta ei löydy: " + target);
    } else if (fragment && path.extname(targetFile).toLowerCase() === ".md") {
      const targetLines = visibleLines(fs.readFileSync(targetFile, "utf8"));
      const targetHeadings = targetLines.flatMap((line) => {
        const found = line.match(/^#{1,6}\s+(.+?)\s*#*\s*$/);
        return found ? [slug(found[1])] : [];
      });
      if (!targetHeadings.includes(fragment)) errors.push(relative + ": otsikkoankkuria ei löydy kohteesta " + target + ".");
    }
  }
}

// README:n versionumeron pitää vastata siihen linkitetyn versionhallittavan dokumentin versiota.
const readme = fs.readFileSync(path.join(root, "README.md"), "utf8");
const readmeLinks = /\[([^\]]+)\]\(([^)]+\.md)\)/g;
for (const match of readme.matchAll(readmeLinks)) {
  const target = path.resolve(root, match[2].split("#")[0]);
  if (!fs.existsSync(target) || !fs.statSync(target).isFile()) continue;
  const expected = versionOf(fs.readFileSync(target, "utf8")).value;
  if (!expected) continue;
  const actual = match[1].match(/\b(\d+\.\d+\.\d+)\b/)?.[1] ?? null;
  if (actual !== expected) errors.push("README.md: linkin " + match[2] + " versionumero (" + (actual ?? "puuttuu") + ") ei vastaa dokumentin versiota (" + expected + ").");
}

if (errors.length) {
  console.error("Dokumentaation laaduntarkistus epäonnistui:");
  for (const error of errors) console.error("- " + error);
  process.exitCode = 1;
} else {
  console.log("Dokumentaation laaduntarkistus onnistui.");
}
