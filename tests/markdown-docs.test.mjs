import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const script = fileURLToPath(new URL("../.github/scripts/check_markdown_docs.mjs", import.meta.url));

function runFixture(document, readmeVersion = "1.0.0") {
  // Luo erillisen väliaikaisen repositorion, jotta virheelliset testit eivät koske oikeita tiedostoja.
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "aiheseurain-docs-"));
  fs.mkdirSync(path.join(root, "docs"));
  fs.writeFileSync(path.join(root, "README.md"), "# Testirepo\n\n[Ohje](docs/guide.md) (" + readmeVersion + ")\n");
  fs.writeFileSync(path.join(root, "docs/guide.md"), document);
  const result = spawnSync(process.execPath, [script], { cwd: root, encoding: "utf8" });
  fs.rmSync(root, { recursive: true, force: true });
  return result;
}

test("hyväksyy ehjän dokumentin ja README:n täsmäävän version", () => {
  const result = runFixture("# Ohje\n\n**Versio:** 1.0.0\n\n## Osa\n\nSisältö.\n");
  assert.equal(result.status, 0, result.stderr);
});

test("hylkää dokumentin, jossa ei ole täsmälleen yhtä H1-pääotsikkoa", () => {
  const result = runFixture("## Alaotsikko\n");
  assert.equal(result.status, 1);
  assert.match(result.stderr, /täsmälleen yksi H1/);
});

test("hylkää otsikkotason ohittamisen", () => {
  const result = runFixture("# Ohje\n\n### Hyppy\n");
  assert.equal(result.status, 1);
  assert.match(result.stderr, /otsikkotaso hyppää/);
});

test("hylkää useamman versionumeromerkinnän", () => {
  const result = runFixture("# Ohje\n\n**Versio:** 1.0.0\n\n**Versio:** 1.0.1\n");
  assert.equal(result.status, 1);
  assert.match(result.stderr, /Versio.*useammin kuin kerran/);
});

test("hylkää README:n ja dokumentin ristiriitaiset versionumerot", () => {
  const result = runFixture("# Ohje\n\n**Versio:** 1.0.1\n", "1.0.0");
  assert.equal(result.status, 1);
  assert.match(result.stderr, /ei vastaa dokumentin versiota/);
});

test("havaitsee kokonaisen osion kopioitumisen", () => {
  const result = runFixture("# Ohje\n\n## Sama osa\n\nSama teksti.\n\n## Sama osa\n\nSama teksti.\n");
  assert.equal(result.status, 1);
  assert.match(result.stderr, /toistuvat/);
});

test("hylkää puuttuvan sisäisen linkin kohteen", () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "aiheseurain-docs-"));
  fs.mkdirSync(path.join(root, "docs"));
  fs.writeFileSync(path.join(root, "README.md"), "# Testirepo\n");
  fs.writeFileSync(path.join(root, "docs/guide.md"), "# Ohje\n\n[Puuttuva](missing.md)\n");
  const result = spawnSync(process.execPath, [script], { cwd: root, encoding: "utf8" });
  fs.rmSync(root, { recursive: true, force: true });
  assert.equal(result.status, 1);
  assert.match(result.stderr, /sisäisen linkin kohdetta ei löydy/);
});
