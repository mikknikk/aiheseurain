#!/usr/bin/env python3
"""Tallenna RSS-julkaisun ehdokas GitHub Deployment -historiaan ja varmista Pages-takaisinluku."""
from __future__ import annotations
import argparse, hashlib, json, os, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path
import urllib.error, urllib.request
import xml.etree.ElementTree as ET
import jsonschema

ROOT = Path(__file__).resolve().parents[1]
PAGES = "https://mikknikk.github.io/aiheseurain"
CATALOG = ROOT / "data/feed-catalog.json"
SCHEMA = ROOT / "schemas/rss-publication-manifest.schema.json"

class PublicationError(RuntimeError):
    """Julkaisumanifestin tai takaisinluvun virhe."""

def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def rss_metadata(data: bytes, label: str) -> tuple[list[str], int]:
    """Tarkista XML ja palauta yksilölliset GUIDit sekä item-määrä."""
    try:
        root = ET.fromstring(data)
    except ET.ParseError as exc:
        raise PublicationError(f"{label}: virheellinen RSS/XML: {exc}") from exc
    channel = root.find("channel")
    if root.tag != "rss" or channel is None:
        raise PublicationError(f"{label}: RSS channel puuttuu")
    guids = []
    for item in channel.findall("item"):
        guid = item.findtext("guid")
        if not guid or not guid.strip():
            raise PublicationError(f"{label}: itemiltä puuttuu GUID")
        guids.append(guid.strip())
    if len(guids) != len(set(guids)):
        raise PublicationError(f"{label}: GUID ei ole yksilöllinen")
    return guids, len(guids)

def api(method: str, path: str, payload: dict | None = None) -> dict:
    """Käytä GitHub APIa vain rajattuun deployment-historiaan."""
    token, repo = os.getenv("GITHUB_TOKEN"), os.getenv("GITHUB_REPOSITORY")
    if not token or not repo:
        raise PublicationError("GITHUB_TOKEN tai GITHUB_REPOSITORY puuttuu")
    body = json.dumps(payload).encode() if payload is not None else None
    request = urllib.request.Request(
        f"https://api.github.com/repos/{repo}/{path.lstrip('/')}",
        data=body, method=method, headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json",
            "User-Agent": "aiheseurain-rss-publication-verifier",
        })
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            raw = response.read()
        return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:800]
        raise PublicationError(f"GitHub API {method} {path}: {exc.code} {detail}") from exc
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise PublicationError(f"GitHub API -virhe: {exc}") from exc

def output(name: str, value: str) -> None:
    """Kirjoita GitHub Actions -stepin tulos."""
    if os.getenv("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as stream:
            stream.write(f"{name}={value}\n")

def prepare(args) -> None:
    """Valmistele kaikki kymmenen syötettä ennen Pages-julkaisua."""
    changed = subprocess.run(
        ["git", "diff", "--name-only", f"{args.base_ref}...HEAD"],
        cwd=ROOT, check=True, capture_output=True, text=True).stdout.splitlines()
    changed_feeds = {p for p in changed if p.startswith("feeds/") and p.endswith(".xml")}
    if not changed_feeds:
        print("RSS-syötemuutoksia ei ole; manifestia ei tarvita.")
        output("deployment_id", "")
        return
    reports = {}
    for path in changed:
        if path.startswith("reports/julkaisuportit/") and path.endswith(".json"):
            report_path = ROOT / path
            report = json.loads(report_path.read_text(encoding="utf-8"))
            feed = report.get("feed_path")
            if report.get("decision") != "approved" or feed in reports:
                raise PublicationError(f"{path}: hyväksyttyä yksilöllistä porttiraporttia ei ole")
            reports[feed] = {"run_id": report.get("run_id"), "path": path,
                             "sha256": digest(report_path.read_bytes())}
    if changed_feeds - reports.keys():
        raise PublicationError("Porttiraportti puuttuu: " + ", ".join(sorted(changed_feeds - reports.keys())))
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    feeds = []
    for entry in catalog["feeds"]:
        path = entry["path"]
        data = (ROOT / path).read_bytes()
        guids, count = rss_metadata(data, path)
        report = reports.get(path, {})
        feeds.append({
            "feed_id": entry["id"], "path": path, "public_url": f"{PAGES}/{path}",
            "sha256": digest(data), "size_bytes": len(data), "item_count": count,
            "guids": guids, "changed_in_commit": path in changed_feeds,
            "report_run_id": report.get("run_id"), "report_path": report.get("path"),
            "report_sha256": report.get("sha256"),
        })
    manifest = {
        "schema_version": 1, "manifest_type": "aiheseurain-rss-publication",
        "phase": "prepared", "workflow_run_id": os.getenv("GITHUB_RUN_ID", "local"),
        "workflow_attempt": os.getenv("GITHUB_RUN_ATTEMPT", "1"),
        "source_commit": os.environ["GITHUB_SHA"], "base_commit": args.base_ref,
        "prepared_at": now(), "pages_base_url": PAGES, "feeds": feeds,
    }
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(
        schema, format_checker=jsonschema.FormatChecker()
    ).validate(manifest)
    created = api("POST", "deployments", {
        "ref": manifest["source_commit"], "task": "deploy", "auto_merge": False,
        "required_contexts": [], "environment": "rss-publication-manifest",
        "description": "RSS-ehdokas valmis; odottaa Pages-takaisinlukua.",
        "transient_environment": False, "production_environment": False,
        "payload": manifest,
    })
    deployment_id = created.get("id")
    if not isinstance(deployment_id, int):
        raise PublicationError("GitHub ei palauttanut deployment-tunnistetta")
    output("deployment_id", str(deployment_id))
    print(f"RSS-manifesti {deployment_id} tallennettu ennen Pages-julkaisua.")

def check_current(args) -> None:
    """Estä vanhentuneen Pages-artifactin julkaiseminen."""
    current = api("GET", "git/ref/heads/main").get("object", {}).get("sha")
    is_current = current == args.source_commit
    output("is_current", "true" if is_current else "false")
    print("Build on nykyinen." if is_current else f"Vanhentunut build ohitetaan; main={current}")

def status(deployment_id: int, state: str, description: str) -> None:
    """Lisää uusi tilamerkintä; aiempaa deployment-historiaa ei muokata."""
    repo = os.environ["GITHUB_REPOSITORY"]
    run_url = os.getenv("GITHUB_SERVER_URL", "https://github.com") + f"/{repo}/actions/runs/" + os.getenv("GITHUB_RUN_ID", "")
    api("POST", f"deployments/{deployment_id}/statuses", {
        "state": state, "description": description[:140],
        "environment": "rss-publication-manifest", "log_url": run_url,
        "environment_url": PAGES + "/",
    })

def finalize(args) -> None:
    """Lue syötteet Pagesista takaisin ja kirjaa success vasta täsmäyksen jälkeen."""
    did = int(args.deployment_id)
    if args.is_current == "false":
        status(did, "inactive", "Build vanheni; uudempi main-commit ohitti julkaisun.")
        return
    if args.is_current != "true":
        status(did, "failure", "Main-haaran nykytilaa ei voitu varmistaa; julkaisu estettiin.")
        raise PublicationError("Main-haaran nykytilan tarkistus epäonnistui")
    if args.deploy_outcome != "success":
        status(did, "failure", "Pages-julkaisu epäonnistui; aiempi julkaisu säilyy.")
        raise PublicationError("Pages-julkaisu epäonnistui")
    manifest = api("GET", f"deployments/{did}").get("payload", {})
    if manifest.get("manifest_type") != "aiheseurain-rss-publication":
        raise PublicationError("Deploymentilta puuttuu RSS-manifesti")
    try:
        for feed in manifest["feeds"]:
            last_error = None
            for attempt in range(8):
                try:
                    request = urllib.request.Request(feed["public_url"], headers={
                        "Cache-Control": "no-cache", "Pragma": "no-cache",
                        "User-Agent": "aiheseurain-rss-publication-verifier"})
                    with urllib.request.urlopen(request, timeout=20) as response:
                        actual = response.read()
                    guids, count = rss_metadata(actual, feed["path"])
                    if digest(actual) != feed["sha256"] or guids != feed["guids"] or count != feed["item_count"]:
                        raise PublicationError(f"{feed['path']}: julkinen sisältö ei vastaa ehdokasta")
                    last_error = None
                    break
                except (urllib.error.URLError, TimeoutError, PublicationError) as exc:
                    last_error = exc
                    if attempt < 7:
                        time.sleep(min(5 * (attempt + 1), 20))
            if last_error:
                raise PublicationError(f"{feed['path']}: takaisinluku epäonnistui: {last_error}")
    except Exception as exc:
        status(did, "failure", f"Pages-takaisinluku epäonnistui: {exc}")
        raise
    status(did, "success", f"Kaikki {len(manifest['feeds'])} syötettä täsmäävät SHA/GUID/item-tasolla.")
    print(f"OK: kaikki {len(manifest['feeds'])} RSS-syötettä varmennettiin julkisista URL-osoitteista.")

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("prepare"); p.add_argument("--base-ref", required=True)
    c = sub.add_parser("check-current"); c.add_argument("--source-commit", required=True)
    f = sub.add_parser("finalize")
    f.add_argument("--deployment-id", required=True)
    f.add_argument("--deploy-outcome", required=True)
    f.add_argument("--is-current", required=True)
    args = parser.parse_args()
    try:
        {"prepare": prepare, "check-current": check_current, "finalize": finalize}[args.command](args)
    except (PublicationError, OSError, KeyError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"VIRHE: {exc}", file=sys.stderr)
        raise SystemExit(1)

if __name__ == "__main__":
    main()
