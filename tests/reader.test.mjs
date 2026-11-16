import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { ALLOWED_TAGS, DROP_TAGS, isSafeArticleUrl, sanitizeArticleHtml } from "../assets/js/reader.js";

test("artikkelilinkit hyväksyvät vain täydelliset HTTP- ja HTTPS-osoitteet", () => {
  assert.equal(isSafeArticleUrl("https://example.com/article"), true);
  assert.equal(isSafeArticleUrl("http://example.com/article"), true);
  assert.equal(isSafeArticleUrl("javascript:alert(1)"), false);
  assert.equal(isSafeArticleUrl("data:text/html,hello"), false);
  assert.equal(isSafeArticleUrl("//example.com/path"), false);
  assert.equal(isSafeArticleUrl("/relative/path"), false);
  assert.equal(isSafeArticleUrl("https://user:pass@example.com/"), false);
  assert.equal(isSafeArticleUrl(""), false);
});

class FakeNode {
  constructor(type, tagName = "", value = "") {
    this.nodeType = type;
    this.tagName = tagName.toUpperCase();
    this.nodeValue = value;
    this.childNodes = [];
    this.attributes = {};
    this.parent = null;
  }
  appendChild(node) { node.parent = this; this.childNodes.push(node); return node; }
  setAttribute(name, value) { this.attributes[name] = value; }
  getAttribute(name) { return Object.hasOwn(this.attributes, name) ? this.attributes[name] : null; }
}
function fakeElement(tag, attrs = {}, children = []) {
  const node = new FakeNode(1, tag);
  node.attributes = { ...attrs };
  for (const child of children) node.appendChild(child);
  return node;
}

test("sanitointi pudottaa aktiiviset elementit ja tapahtumankäsittelijät", () => {
  const tree = fakeElement("div", {}, [
    new FakeNode(3, "", "Turvallinen teksti "),
    fakeElement("script", {}, [new FakeNode(3, "", "alert(1)")]),
    fakeElement("iframe", { src: "https://attacker.example/" }),
    fakeElement("p", { onclick: "alert(2)" }, [
      fakeElement("a", { href: "javascript:alert(3)", onclick: "alert(4)" }, [
        new FakeNode(3, "", "Vaarallinen linkki")
      ])
    ]),
    fakeElement("p", {}, [
      fakeElement("a", { href: "https://example.com/source", onclick: "alert(5)", style: "color:red" }, [
        new FakeNode(3, "", "Turvallinen lähde")
      ])
    ])
  ]);
  const oldParser = globalThis.DOMParser;
  const oldDocument = globalThis.document;
  globalThis.DOMParser = class { parseFromString() { return { body: { childNodes: [tree] } }; } };
  globalThis.document = {
    createDocumentFragment: () => new FakeNode(11),
    createTextNode: (value) => new FakeNode(3, "", value),
    createElement: (tag) => new FakeNode(1, tag)
  };
  try {
    const result = sanitizeArticleHtml("<div>ignored test source</div>");
    const text = JSON.stringify(result, (key, value) => key === "parent" ? undefined : value);
    assert.doesNotMatch(text, /alert|attacker|javascript|onclick|style/);
    assert.match(text, /Turvallinen teksti/);
    assert.match(text, /Turvallinen lähde/);
    assert.match(text, /https://example.com/source/);
    assert.equal(ALLOWED_TAGS.has("p"), true);
    assert.equal(DROP_TAGS.has("script"), true);
    assert.equal(DROP_TAGS.has("iframe"), true);
  } finally {
    globalThis.DOMParser = oldParser;
    globalThis.document = oldDocument;
  }
});

test("RSS-lukijan sivu ja navigaatio tarjoavat oman saavutettavan osion", () => {
  const page = readFileSync(new URL("../lukija/index.html", import.meta.url), "utf8");
  const header = readFileSync(new URL("../_includes/site-header.html", import.meta.url), "utf8");
  const layout = readFileSync(new URL("../_layouts/site.html", import.meta.url), "utf8");
  const script = readFileSync(new URL("../assets/js/reader.js", import.meta.url), "utf8");
  assert.match(page, /section: lukija/);
  assert.match(page, /for="feed-filter"/);
  assert.match(page, /aria-live="polite"/);
  assert.match(header, /\/lukija\//);
  assert.match(header, /page\.section == "lukija"/);
  assert.match(layout, /assets\/js\/reader\.js/);
  assert.doesNotMatch(script, /innerHTML\s*=/);
});
