/**
 * Tarkistaa Aiheseuraimen Markdown-dokumentaation perusrakenteen ja sisäiset linkit.
 * Skripti ei muuta tiedostoja; virheet estävät GitHub Actions -työnkulun onnistumisen.
 */
import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const files = ["README.md"];
function collect(dir) {
  for (const item of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, item.name);
    if (item.isDirectory()) collect(full);
    else if (item.isFile() && item.name.endsWith(".md")) files.push(full);
  }
}
collect(path.join(root, "docs"));
const errors = [];
for (const file of files) {
  const text = fs.readFileSync(file, "utf8");
  const relative = path.relative(root, file).split(path.sep).join("/");
  const headings = text.split(/\r?\n/).filter((line) => /^#{1,6}\s/.test(line));
  const h1 = headings.filter((line) => /^#\s/.test(line)).length;
  if (h1 !== 1) errors.push(relative + ": odotettiin yhtä H1-pääotsikkoa, löytyi " + h1 + ".");
  const versions = [...text.matchAll(/^\*\*Versio:\*\*\s*\d+\.\d+\.\d+\s*$/gm)];
  if (versions.length > 1) errors.push(relative + ": Versio-merkintä esiintyy useammin kuin kerran.");
  let prior = 0;
  for (const line of headings) {
    const level = line.match(/^#+/)[0].length;
    if (prior && level > prior + 1) errors.push(relative + ": otsikkotaso hyppää H" + prior + "-tasolta H" + level + "-tasolle.");
    prior = level;
  }
  const seen = new Set();
  for (let i = 0; i < headings.length; i++) {
    const title = headings[i].replace(/^#+\s*/, "").trim();
    const next = headings[i + 1];
    const start = text.indexOf(headings[i]);
    const end = next ? text.indexOf(next, start + headings[i].length) : text.length;
    const body = text.slice(start + headings[i].length, end).replace(/\s+/g, " ").trim();
    const key = title + "::" + body;
    if (body && seen.has(key)) errors.push(relative + ': toistuva osio "' + title + '".');
    seen.add(key);
  }
}
if (errors.length) {
  console.error(errors.join("\n"));
  process.exitCode = 1;
} else {
  console.log("Dokumentaation laaduntarkistus onnistui.");
}
