/**
 * Aiheseuraimen RSS-lukijan selainpuolen toiminta.
 *
 * Lukija hakee RSS-syötteet GitHub Pagesista, yhdistää niiden artikkelit
 * aikajärjestykseen ja tarjoaa syötekohtaisen suodattimen. Ulkoinen HTML
 * jäsennetään erillään sivusta ja rakennetaan uudelleen sallittujen
 * elementtien avulla. Raakaa RSS-HTML:ää ei koskaan sijoiteta sivun DOMiin.
 * Lukija ei tallenna artikkeleita palvelimelle eikä tee ulkoisia kuvahakuja.
 */
const CATALOG_URL = new URL("../../data/feed-catalog.json", import.meta.url).href;

// Artikkelisisällössä sallitaan vain tavalliset tekstin ja rakenteen elementit.
// Kuvia, tyylejä, lomakkeita, upotuksia tai aktiivista sisältöä ei ladata.
export const ALLOWED_TAGS = new Set([
  "article", "section", "div", "p", "h1", "h2", "h3", "h4", "h5", "h6",
  "ul", "ol", "li", "strong", "b", "em", "i", "blockquote",
  "br", "hr", "a", "table", "thead", "tbody", "tr", "th", "td",
  "dl", "dt", "dd", "sup", "sub", "small", "code", "pre"
]);

// Näiden elementtien sisältökin poistetaan kokonaan.
export const DROP_TAGS = new Set([
  "script", "style", "iframe", "frame", "frameset", "object", "embed",
  "svg", "math", "form", "input", "button", "textarea", "select",
  "option", "video", "audio", "source", "track", "canvas", "template",
  "noscript", "link", "meta", "base"
]);

/**
 * Hyväksyy vain täydelliset HTTP- ja HTTPS-linkit.
 * Suhteelliset osoitteet ja käyttäjätunnuksia sisältävät osoitteet hylätään.
 */
export function isSafeArticleUrl(value) {
  if (typeof value !== "string" || !value.trim()) return false;
  try {
    const url = new URL(value);
    return (url.protocol === "https:" || url.protocol === "http:")
      && Boolean(url.hostname) && !url.username && !url.password;
  } catch {
    return false;
  }
}

/**
 * Kopioi RSS:n HTML-katkelman uuteen DocumentFragment-olioon.
 * Alkuperäisiä elementtejä tai attribuutteja ei siirretä sivulle. Tuntemattomat
 * tavalliset elementit puretaan tekstiksi; aktiiviset ja upotetut elementit
 * sekä niiden sisältö poistetaan kokonaan.
 */
function parseHtmlFragment(html) {
  // template-elementin sisältö on inerttiä: esimerkiksi RSS:n img- tai iframe-
  // elementit eivät käynnistä verkkopyyntöjä ennen kuin ne siirretään sivulle.
  // innerHTML-käsittely rajataan tähän irralliseen templateen, ei sivun DOMiin.
  const template = document.createElement("template");
  template.innerHTML = String(html || "");
  return template.content;
}

export function sanitizeArticleHtml(html) {
  const parsed = parseHtmlFragment(html);
  const fragment = document.createDocumentFragment();

  function copyNode(source, target) {
    if (source.nodeType === 3) {
      target.appendChild(document.createTextNode(source.nodeValue || ""));
      return;
    }
    if (source.nodeType !== 1) return;

    const tag = source.tagName.toLowerCase();
    if (DROP_TAGS.has(tag)) return;
    if (!ALLOWED_TAGS.has(tag)) {
      for (const child of source.childNodes) copyNode(child, target);
      return;
    }

    // Siirretään RSS-artikkelin kaikkia otsikoita yhden tason syvemmälle,
    // jotta ne eivät kilpaile lukijasivun oman H1-otsikon kanssa. HTML:ssä
    // ei ole H7-tasoa, joten alkuperäinen H6 säilyy H6-tasolla.
    const headingLevel = /^h[1-6]$/.test(tag) ? Number(tag.slice(1)) : null;
    const outputTag = headingLevel === null
      ? tag
      : "h" + Math.min(headingLevel + 1, 6);
    const clean = document.createElement(outputTag);
    if (tag === "a") {
      const href = source.getAttribute("href");
      if (isSafeArticleUrl(href)) {
        clean.setAttribute("href", href);
        clean.setAttribute("rel", "noopener noreferrer");
      }
      const title = source.getAttribute("title");
      if (title) clean.setAttribute("title", title);
    }
    for (const child of source.childNodes) copyNode(child, clean);
    target.appendChild(clean);
  }

  for (const child of parsed.childNodes) copyNode(child, fragment);
  return fragment;
}

/** Muotoilee RSS:n päiväyksen suomenkieliseen esitystapaan. */
function formatDate(value) {
  const date = new Date(value);
  if (!value || !Number.isFinite(date.getTime())) return "Päiväys puuttuu";
  return new Intl.DateTimeFormat("fi-FI", {
    dateStyle: "medium", timeStyle: "short", timeZone: "Europe/Helsinki"
  }).format(date);
}

/** Lukee XML-elementin tekstin turvallisesti, myös puuttuvan elementin. */
function childText(parent, tagName) {
  const element = parent.getElementsByTagName(tagName)[0];
  return element ? element.textContent || "" : "";
}

/**
 * Muuntaa yhden RSS-syötteen itemit artikkelitietueiksi.
 * Virheellinen XML hylätään kokonaisena; tyhjät syötteet palauttavat tyhjän listan.
 */
export function parseFeedXml(xmlText, feed) {
  const parsed = new DOMParser().parseFromString(xmlText, "application/xml");
  if (parsed.getElementsByTagName("parsererror").length) {
    throw new Error("RSS-tiedosto ei ole kelvollista XML:ää.");
  }
  return Array.from(parsed.getElementsByTagName("item")).map((item, index) => {
    const title = childText(item, "title").trim() || "Otsikko puuttuu";
    const description = childText(item, "description");
    const pubDate = childText(item, "pubDate").trim();
    const timestamp = Date.parse(pubDate);
    return {
      id: feed.id + ":" + (childText(item, "guid").trim() || String(index)),
      title, description,
      pubDate,
      timestamp: Number.isFinite(timestamp) ? timestamp : 0,
      feedId: feed.id,
      feedTitle: feed.title
    };
  });
}

/** Luo tekstielementin ilman HTML-merkkijonojen tulkintaa. */
function element(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

let allArticles = [];

/** Näyttää valitun syötteen artikkelit ja päivittää lukumäärän. */
function renderArticles() {
  const filter = document.getElementById("feed-filter").value;
  const target = document.getElementById("article-list");
  const count = document.getElementById("reader-count");
  const articles = allArticles
    .filter((article) => filter === "all" || article.feedId === filter)
    .sort((a, b) => b.timestamp - a.timestamp);

  target.replaceChildren();
  count.textContent = articles.length + (articles.length === 1 ? " artikkeli" : " artikkelia");
  if (!articles.length) {
    target.appendChild(element("p", "reader-empty",
      filter === "all" ? "Syötteissä ei tällä hetkellä ole artikkeleita."
        : "Tässä syötteessä ei tällä hetkellä ole artikkeleita."));
    return;
  }

  const list = document.createDocumentFragment();
  for (const article of articles) {
    const card = element("article", "reader-item");
    const details = document.createElement("details");
    const summary = document.createElement("summary");
    summary.append(
      element("span", "reader-item-title", article.title),
      element("span", "reader-item-meta", article.feedTitle + " · " + formatDate(article.pubDate))
    );
    details.appendChild(summary);
    const body = element("div", "reader-article-body");
    body.appendChild(sanitizeArticleHtml(article.description));
    details.appendChild(body);
    card.appendChild(details);
    list.appendChild(card);
  }
  target.appendChild(list);
}

/** Hakee katalogin ja kaikki syötteet; yhden syötteen virhe ei peitä muita. */
async function loadReader() {
  const filter = document.getElementById("feed-filter");
  const message = document.getElementById("reader-message");
  const list = document.getElementById("article-list");
  try {
    const catalogResponse = await fetch(CATALOG_URL, { cache: "no-cache" });
    if (!catalogResponse.ok) throw new Error("Syötekatalogin lataus epäonnistui.");
    const catalog = await catalogResponse.json();
    if (catalog.schema_version !== 1 || !Array.isArray(catalog.feeds) || catalog.feeds.length !== 10) {
      throw new Error("Syötekatalogin rakenne ei ole kelvollinen.");
    }

    for (const feed of catalog.feeds) {
      const option = document.createElement("option");
      option.value = feed.id;
      option.textContent = feed.title;
      filter.appendChild(option);
    }

    const results = await Promise.all(catalog.feeds.map(async (feed) => {
      try {
        const url = new URL("../../" + feed.path, import.meta.url).href;
        const response = await fetch(url, { cache: "no-cache" });
        if (!response.ok) throw new Error("HTTP " + response.status);
        return { feed, articles: parseFeedXml(await response.text(), feed), error: null };
      } catch (error) {
        return { feed, articles: [], error: error.message || "Syötteen lataus epäonnistui." };
      }
    }));

    allArticles = results.flatMap((result) => result.articles)
      .sort((a, b) => b.timestamp - a.timestamp);
    const errors = results.filter((result) => result.error);
    const emptyFeeds = results.filter((result) => !result.error && result.articles.length === 0);
    renderArticles();

    if (errors.length) {
      message.className = "reader-message reader-message-warning";
      message.textContent = errors.length + " syötettä ei voitu ladata. Muiden syötteiden artikkelit ovat käytettävissä.";
      const errorList = document.createElement("ul");
      for (const result of errors) {
        errorList.appendChild(element("li", "", result.feed.title + ": " + result.error));
      }
      message.appendChild(errorList);
    } else if (emptyFeeds.length) {
      message.className = "reader-message";
      message.textContent = "Kaikki kymmenen syötettä ladattiin. " + emptyFeeds.length
        + " syötettä on tällä hetkellä tyhjiä; niihin ei luoda keinotekoisia artikkeleita.";
    } else {
      message.className = "reader-message";
      message.textContent = "Kaikki kymmenen RSS-syötettä ladattiin onnistuneesti.";
    }
  } catch (error) {
    message.className = "reader-message reader-message-warning";
    message.textContent = error.message || "RSS-lukijan lataus epäonnistui.";
    list.replaceChildren(element("p", "", "Artikkeleita ei voitu ladata. Voit käyttää alkuperäisiä RSS-syötteitä Aiheseuraimen etusivulta."));
    document.getElementById("reader-count").textContent = "Tietoja ei saatavilla";
  }
}

if (typeof document !== "undefined") {
  document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("feed-filter").addEventListener("change", renderArticles);
    loadReader();
  }, { once: true });
}
