#!/usr/bin/env python3
"""Read-only audit of Aiheseurain's historical Pages RSS publication evidence."""
from __future__ import annotations
import argparse, hashlib, html, json, os, re, sys, urllib.error, urllib.parse, urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

REPO = "mikknikk/aiheseurain"
ENVIRONMENT = "rss-publication-manifest"
FEED_ID = "taylor-swift"
FEED_PATH = "feeds/taylor-swift.xml"
FEED_URL = "https://mikknikk.github.io/aiheseurain/feeds/taylor-swift.xml"
API_BASE = f"https://api.github.com/repos/{REPO}"

class AuditError(RuntimeError):
    """Julkaisuhistorian lukeminen tai tulkinta epäonnistui."""

class TextExtractor(HTMLParser):
    """Poimi RSS-kuvauksesta luettava teksti ilman HTML-merkintöjä."""
    def __init__(self):
        super().__init__()
        self.parts = []
    def handle_data(self, data):
        self.parts.append(data)
    def text(self):
        return " ".join(x.strip() for x in self.parts if x.strip())

def parse_time(value: str, field: str) -> datetime:
    """Vaadi aikavyöhykkeellinen ISO 8601 -aika."""
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, TypeError, ValueError) as exc:
        raise AuditError(f"{field}: virheellinen ISO 8601 -aikaleima") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise AuditError(f"{field}: aikavyöhyke puuttuu")
    return parsed

def request_bytes(url: str, token: str | None = None) -> bytes:
    """Lue URL; älä koskaan lähetä GitHub-tunnusta api.github.com-osoitteen ulkopuolelle."""
    headers = {"User-Agent": "aiheseurain-pages-history-audit", "Cache-Control": "no-cache"}
    if token:
        if urllib.parse.urlparse(url).hostname != "api.github.com":
            raise AuditError("GitHub-tunnusta ei lähetetä api.github.com-osoitteen ulkopuolelle")
        headers.update({"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json",
                        "X-GitHub-Api-Version": "2022-11-28"})
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=30) as response:
            return response.read()
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
        raise AuditError(f"HTTP-luvun virhe osoitteessa {url}: {exc}") from exc

def api_json(path: str, token: str) -> Any:
    """Hae JSON-tietoa GitHubin rajapinnasta."""
    try:
        return json.loads(request_bytes(f"{API_BASE}/{path.lstrip('/')}", token))
    except json.JSONDecodeError as exc:
        raise AuditError(f"GitHub API palautti virheellistä JSONia: {path}") from exc

def paginated(path: str, token: str) -> list[dict]:
    """Lue kaikki sivut; keskeytä sen sijaan, että osittaista historiaa pidettäisiin täydellisenä."""
    output, page = [], 1
    while True:
        separator = "&" if "?" in path else "?"
        rows = api_json(f"{path}{separator}per_page=100&page={page}", token)
        if not isinstance(rows, list):
            raise AuditError(f"GitHub API ei palauttanut listaa: {path}")
        output.extend(x for x in rows if isinstance(x, dict))
        if len(rows) < 100:
            return output
        page += 1
        if page > 100:
            raise AuditError("Historia ylittää 10 000 tietuetta; tarkistus keskeytetään turvallisesti")

def deployment_manifest(row: dict) -> dict | None:
    """Hyväksy vain tunnetun RSS-julkaisumanifestin sisältö."""
    payload = row.get("payload")
    if isinstance(payload, str):
        try:
            payload = json.loads(payload)
        except json.JSONDecodeError:
            return None
    if isinstance(payload, dict) and payload.get("manifest_type") == "aiheseurain-rss-publication":
        return payload
    return None

def status_for(deployment_id: int, token: str) -> dict:
    """Lue deploymentin viimeisin tilamerkintä."""
    statuses = paginated(f"deployments/{deployment_id}/statuses", token)
    if not statuses:
        return {"state": "no_status", "description": None, "created_at": None}
    latest = max(statuses, key=lambda x: x.get("created_at", ""))
    # Deployment voidaan myöhemmin merkitä inactive-tilaan, kun uudempi
    # julkaisu korvaa sen. Tämä ei peruuta sitä, että aiempi RSS-sisältö
    # ehti jo onnistuneesti julkiseksi. Siksi säilytämme sekä viimeisimmän
    # tilan että tiedon siitä, esiintyikö historiassa success-tila.
    return {
        **{k: latest.get(k) for k in ("state", "description", "created_at")},
        "ever_successful": any(row.get("state") == "success" for row in statuses),
        "status_count": len(statuses),
    }

def report_period_matches(item: ET.Element, start: datetime, end: datetime) -> bool:
    """Tunnista vain raportin eksplisiittinen seurantajakso; pubDate ei yksin riitä."""
    extractor = TextExtractor()
    extractor.feed(item.findtext("description") or "")
    text = html.unescape(extractor.text())
    if "Seurantajakso" not in text:
        return False
    dates = set(re.findall(r"\b20\d{2}-\d{2}-\d{2}\b", text))
    for day, month, year in re.findall(r"\b(\d{1,2})\.(\d{1,2})\.(20\d{2})\b", text):
        dates.add(f"{int(year):04d}-{int(month):02d}-{int(day):02d}")
    required = {start.date().isoformat(), end.date().isoformat()}
    return required.issubset(dates)

def rss_items_for_commit(sha: str, start: datetime, end: datetime) -> list[dict]:
    """Lue täsmälleen manifestin lähdecommitin RSS-tiedosto."""
    url = f"https://raw.githubusercontent.com/{REPO}/{sha}/{FEED_PATH}"
    try:
        root = ET.fromstring(request_bytes(url))
    except ET.ParseError as exc:
        raise AuditError(f"RSS/XML on virheellinen commitissa {sha[:12]}") from exc
    channel = root.find("channel")
    if root.tag != "rss" or channel is None:
        raise AuditError(f"RSS channel puuttuu commitista {sha[:12]}")
    matches = []
    for item in channel.findall("item"):
        guid = (item.findtext("guid") or "").strip()
        if guid and report_period_matches(item, start, end):
            matches.append({"guid": guid, "title": (item.findtext("title") or "").strip()})
    return matches

def audit_deployments(start: datetime, end: datetime, token: str) -> dict:
    """Tutki RSS-manifestit ja varmista, sisältääkö onnistunut julkaisu tämän jakson."""
    rows = paginated(f"deployments?environment={urllib.parse.quote(ENVIRONMENT)}", token)
    matches, examined = [], 0
    for row in rows:
        manifest = deployment_manifest(row)
        if not manifest:
            continue
        feed = next((x for x in manifest.get("feeds", [])
                     if isinstance(x, dict) and x.get("feed_id") == FEED_ID), None)
        if not feed:
            continue
        examined += 1
        sha, deployment_id = manifest.get("source_commit"), row.get("id")
        if not isinstance(sha, str) or not re.fullmatch(r"[0-9a-f]{40}", sha):
            continue
        items = rss_items_for_commit(sha, start, end)
        manifest_guids = set(feed.get("guids", []))
        items = [item for item in items if item["guid"] in manifest_guids]
        if not items:
            continue
        status = status_for(deployment_id, token) if isinstance(deployment_id, int) else {"state": "unknown"}
        matches.append({
            "deployment_id": deployment_id, "created_at": row.get("created_at"),
            "source_commit": sha, "workflow_run_id": manifest.get("workflow_run_id"),
            "manifest_guids": feed.get("guids", []), "period_items_in_source_commit": items,
            "deployment_status": status,
            "successful_pages_publication": status.get("ever_successful") is True,
        })
    proven = any(x["successful_pages_publication"] for x in matches)
    return {
        "environment": ENVIRONMENT, "deployment_records_read": len(rows),
        "rss_manifests_examined": examined, "period_matching_manifests": matches,
        "historical_pages_publication": "published" if proven else "unknown",
        "historical_pages_publication_reason": (
            "An RSS manifest containing the period report has a successful Pages deployment."
            if proven else
            "No successful Pages deployment manifest containing the period report was found. "
            "Missing manifests do not prove non-publication."
        ),
    }

def audit_workflow_runs(start: datetime, end: datetime, token: str) -> dict:
    """Listaa Pages-työnkulun ajot sekä niiden job- ja step-tulokset."""
    created = urllib.parse.quote(
        f"{start.astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}..{end.astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}", safe=":"
    )
    runs = paginated(f"actions/workflows/publish-pages.yml/runs?created={created}", token)
    output = []
    for run in runs:
        run_id = run.get("id")
        if not isinstance(run_id, int):
            continue
        data = api_json(f"actions/runs/{run_id}/jobs?per_page=100", token)
        jobs = data.get("jobs", []) if isinstance(data, dict) else []
        output.append({
            "run_id": run_id, "run_number": run.get("run_number"), "created_at": run.get("created_at"),
            "event": run.get("event"), "head_branch": run.get("head_branch"), "head_sha": run.get("head_sha"),
            "conclusion": run.get("conclusion"), "url": run.get("html_url"),
            "jobs": [{"name": job.get("name"), "conclusion": job.get("conclusion"),
                      "steps": [{"name": step.get("name"), "conclusion": step.get("conclusion")}
                                for step in (job.get("steps") or [])]}
                     for job in jobs],
        })
    return {"workflow": ".github/workflows/publish-pages.yml", "runs": output}

def audit_current_pages(start: datetime, end: datetime) -> dict:
    """Lue nykyinen julkinen RSS, mutta älä tulkitse sitä historialliseksi snapshotiksi."""
    raw = request_bytes(FEED_URL)
    try:
        root = ET.fromstring(raw)
    except ET.ParseError as exc:
        raise AuditError(f"Julkinen RSS/XML on virheellinen: {exc}") from exc
    channel = root.find("channel")
    if root.tag != "rss" or channel is None:
        raise AuditError("Julkisesta RSS:stä puuttuu channel")
    items = []
    for item in channel.findall("item"):
        guid = (item.findtext("guid") or "").strip()
        if guid and report_period_matches(item, start, end):
            items.append({"guid": guid, "title": (item.findtext("title") or "").strip()})
    return {"url": FEED_URL, "read_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "sha256": hashlib.sha256(raw).hexdigest(), "size_bytes": len(raw),
            "period_items_currently_visible": items,
            "historical_limit": "Current RSS content alone does not prove historical publication state."}

def write_outputs(result: dict, path: Path) -> None:
    """Tallenna JSON-raportti ja tiivis Actions-yhteenveto."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    pages, current = result["pages_deployments"], result["current_pages"]
    lines = [
        "# Pages-julkaisuhistorian tarkistus", "",
        f"- Syöte: {FEED_ID}",
        f"- Jakso: {result['period']['start']} – {result['period']['end']}",
        f"- Historiallinen Pages-tila: **{pages['historical_pages_publication']}**",
        f"- Tarkistetut RSS-manifestit: {pages['rss_manifests_examined']}",
        f"- Pages-ajot jaksolla: {len(result['pages_workflow_runs']['runs'])}",
        f"- Nykyisen RSS:n SHA-256: `{current['sha256']}`", "",
        pages["historical_pages_publication_reason"], "",
        "Puuttuvista manifesteista ei päätellä julkaisemattomuutta. Nykyinen RSS on vain nykytilan havainto.", "",
        f"Täysi JSON-raportti: `{path.as_posix()}`",
    ]
    summary = os.getenv("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as stream:
            stream.write("\n".join(lines) + "\n")

def validate_period(start: datetime, end: datetime) -> None:
    """Varmista, että annettu seurantajakso on aikajärjestyksessä."""
    if start > end:
        raise AuditError("Seurantajakson alku on loppua myöhempi")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--period-start", required=True)
    parser.add_argument("--period-end", required=True)
    parser.add_argument("--output", default="artifacts/pages-history-audit.json")
    args = parser.parse_args()
    start, end = parse_time(args.period_start, "period-start"), parse_time(args.period_end, "period-end")
    validate_period(start, end)
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise AuditError("GITHUB_TOKEN puuttuu")
    result = {
        "schema_version": 1, "audit_type": "aiheseurain-pages-rss-history", "repository": REPO,
        "feed_id": FEED_ID, "period": {"start": args.period_start, "end": args.period_end},
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "pages_deployments": audit_deployments(start, end, token),
        "pages_workflow_runs": audit_workflow_runs(start, end, token),
        "current_pages": audit_current_pages(start, end),
        "limitations": [
            "Manifests exist only for publishing runs that changed RSS files.",
            "Missing manifests or a missing runtime branch do not prove non-publication.",
            "The current public RSS is not a historical snapshot.",
            "The checker does not modify deployments, branches, RSS, checkpoints, runtime state, or automations.",
        ],
    }
    write_outputs(result, Path(args.output))
    print(json.dumps({"historical_pages_publication": result["pages_deployments"]["historical_pages_publication"],
                      "manifest_count": result["pages_deployments"]["rss_manifests_examined"],
                      "workflow_run_count": len(result["pages_workflow_runs"]["runs"]),
                      "output": args.output}, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AuditError as exc:
        print(f"Pages history audit stopped safely: {exc}", file=sys.stderr)
        raise SystemExit(2)
