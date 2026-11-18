#!/usr/bin/env python3
"""Tallenna RSS-julkaisun ehdokas GitHub Deployment -historiaan ja varmista Pages-takaisinluku."""
from __future__ import annotations
import argparse, hashlib, json, os, shutil, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path
import urllib.error, urllib.request
import xml.etree.ElementTree as ET

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

def git_changed_files(base_ref: str) -> set[str]:
    """Selvitä lähdecommitin muuttamat tiedostot vertailucommitista."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", f"{base_ref}...HEAD"],
            cwd=ROOT, check=True, capture_output=True, text=True,
        )
    except subprocess.CalledProcessError as exc:
        raise PublicationError(f"Git-diff epäonnistui: {exc.stderr}") from exc
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}

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


def snapshot_live_feeds(feeds: list[dict]) -> list[dict]:
    """Tallenna nykyisten julkisten RSS-syötteiden täsmälliset tavut palautusta varten."""
    folder = ROOT / "_rollback_snapshot" / "feeds"
    folder.mkdir(parents=True, exist_ok=True)
    saved = []
    for feed in feeds:
        request = urllib.request.Request(feed["public_url"], headers={
            "Cache-Control": "no-cache", "Pragma": "no-cache",
            "User-Agent": "aiheseurain-rss-rollback-snapshot"})
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                data = response.read()
        except (urllib.error.URLError, TimeoutError) as exc:
            raise PublicationError(f"{feed['path']}: aiemman syötteen varmistus epäonnistui: {exc}") from exc
        guids, count = rss_metadata(data, feed["path"])
        (folder / Path(feed["path"]).name).write_bytes(data)
        saved.append({"feed_id": feed["feed_id"], "path": feed["path"],
                      "public_url": feed["public_url"], "sha256": digest(data),
                      "size_bytes": len(data), "item_count": count, "guids": guids})
    if len(saved) != len(feeds):
        raise PublicationError("Kaikkia syötteitä ei saatu palautusvarmistukseen")
    return saved


def assemble_rollback(args) -> None:
    """Kokoa vanhan sivuston lähde ja korvaa RSS-tiedostot ennen julkaisua talteen otetuilla."""
    source, destination = Path(args.source_dir), Path(args.destination_dir)
    folder = ROOT / "_rollback_snapshot" / "feeds"
    if not source.is_dir() or not folder.is_dir():
        raise PublicationError("Palautussivuston lähde tai RSS-varmistus puuttuu")
    shutil.copytree(source, destination, dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns(".git", "_site", ".jekyll-cache"))
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    for feed in catalog["feeds"]:
        saved = folder / Path(feed["path"]).name
        if not saved.is_file():
            raise PublicationError(f"Palautusvarmistus puuttuu: {feed['path']}")
        data = saved.read_bytes()
        rss_metadata(data, feed["path"])
        target = destination / feed["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)


def verify_feeds(feeds: list[dict]) -> None:
    """Vertaa julkisia syötteitä odotettuun versioon ja sietää CDN:n päivitysviiveen."""
    for feed in feeds:
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
                    raise PublicationError(f"{feed['path']}: julkinen sisältö ei vastaa odotettua versiota")
                last_error = None
                break
            except (urllib.error.URLError, TimeoutError, PublicationError) as exc:
                last_error = exc
                if attempt < 7:
                    time.sleep(min(5 * (attempt + 1), 20))
        if last_error:
            raise PublicationError(f"{feed['path']}: takaisinluku epäonnistui: {last_error}")


def load_manifest(deployment_id: str) -> dict:
    """Lue muuttumaton GitHub Deployment -manifesti."""
    value = api("GET", f"deployments/{int(deployment_id)}").get("payload", {})
    if value.get("manifest_type") != "aiheseurain-rss-publication":
        raise PublicationError("Deploymentilta puuttuu RSS-manifesti")
    return value


def verify_candidate(args) -> None:
    """Tarkista ehdokasjulkaisu; virhe käynnistää työnkulussa palautusvaiheen."""
    try:
        verify_feeds(load_manifest(args.deployment_id)["feeds"])
        output("candidate_verified", "true")
    except Exception as exc:
        output("candidate_verified", "false")
        print(f"Uuden julkaisun takaisinluku epäonnistui: {exc}")


def verify_rollback(args) -> None:
    """Varmista palautetut syötteet ennen kuin palautus merkitään onnistuneeksi."""
    try:
        verify_feeds(load_manifest(args.deployment_id)["rollback_feeds"])
        output("rollback_verified", "true")
    except Exception as exc:
        output("rollback_verified", "false")
        print(f"Palautuksen takaisinluku epäonnistui: {exc}")

def build_manifest(base_ref: str, source_commit: str,
                   workflow_run_id: str, workflow_attempt: str) -> dict | None:
    """Muodosta muuttumaton ehdokas kaikista syötteistä ennen Pages-kirjoitusta."""
    changed = git_changed_files(base_ref)
    changed_feeds = {path for path in changed if path.startswith("feeds/") and path.endswith(".xml")}
    if not changed_feeds:
        return None

    # Jokaiselle muuttuneelle RSS-syötteelle on löydyttävä saman muutoksen hyväksytty porttiraportti.
    reports = {}
    for path in changed:
        if path.startswith("reports/julkaisuportit/") and path.endswith(".json"):
            report_path = ROOT / path
            try:
                report = json.loads(report_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                raise PublicationError(f"{path}: porttiraporttia ei voi lukea: {exc}") from exc
            feed = report.get("feed_path")
            if report.get("decision") != "approved" or feed in reports:
                raise PublicationError(f"{path}: hyväksyttyä yksilöllistä porttiraporttia ei ole")
            reports[feed] = {"run_id": report.get("run_id"), "path": path,
                             "sha256": digest(report_path.read_bytes())}
    missing = changed_feeds - reports.keys()
    if missing:
        raise PublicationError("Porttiraportti puuttuu: " + ", ".join(sorted(missing)))

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
    return {
        "schema_version": 1, "manifest_type": "aiheseurain-rss-publication",
        "phase": "prepared", "workflow_run_id": str(workflow_run_id),
        "workflow_attempt": str(workflow_attempt), "source_commit": source_commit,
        "base_commit": base_ref, "prepared_at": now(), "pages_base_url": PAGES,
        "feeds": feeds,
        "rollback_feeds": [],
    }


def prepare(args) -> None:
    """Validoi ja tallenna ehdokasmanifesti ennen Pages-julkaisua."""
    manifest = build_manifest(
        args.base_ref, os.environ["GITHUB_SHA"],
        os.getenv("GITHUB_RUN_ID", "local"), os.getenv("GITHUB_RUN_ATTEMPT", "1"))
    if manifest is None:
        print("RSS-syötemuutoksia ei ole; manifestia ei tarvita.")
        output("deployment_id", "")
        return
    # Varmista aiemmin julkinen tila ennen ehdokkaan julkaisemista.
    manifest["rollback_feeds"] = snapshot_live_feeds(manifest["feeds"])
    import jsonschema

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
    """Kirjaa success vasta varmennetun ehdokkaan jälkeen; muuten varmista palautus."""
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
    latest_main = api("GET", "git/ref/heads/main").get("object", {}).get("sha")
    if latest_main != os.getenv("GITHUB_SHA"):
        status(did, "inactive", "Main-haara eteni deployn aikana; uudempi julkaisu korvaa tämän.")
        return
    manifest = load_manifest(args.deployment_id)
    if args.candidate_verified == "true":
        status(did, "success", f"Kaikki {len(manifest['feeds'])} syötettä täsmäävät SHA/GUID/item-tasolla.")
        return
    if args.rollback_outcome == "success" and args.rollback_verified == "true":
        status(did, "failure", "Ehdokas hylättiin; aiempi varmennettu RSS-versio palautettiin.")
        raise PublicationError("Ehdokas hylättiin; aiempi RSS-versio palautettiin.")
    status(did, "failure", "Takaisinluku epäonnistui eikä aiemman RSS-version palautusta voitu varmentaa.")
    raise PublicationError("Julkaisun takaisinluku ja/tai automaattinen palautus epäonnistui.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("prepare"); p.add_argument("--base-ref", required=True)
    c = sub.add_parser("check-current"); c.add_argument("--source-commit", required=True)
    f = sub.add_parser("finalize")
    f.add_argument("--deployment-id", required=True)
    f.add_argument("--deploy-outcome", required=True)
    f.add_argument("--is-current", required=True)
    f.add_argument("--candidate-verified", default="false")
    f.add_argument("--rollback-outcome", default="skipped")
    f.add_argument("--rollback-verified", default="false")
    v = sub.add_parser("verify-candidate"); v.add_argument("--deployment-id", required=True)
    r = sub.add_parser("verify-rollback"); r.add_argument("--deployment-id", required=True)
    a = sub.add_parser("assemble-rollback")
    a.add_argument("--source-dir", required=True); a.add_argument("--destination-dir", required=True)
    args = parser.parse_args()
    try:
        {"prepare": prepare, "check-current": check_current, "finalize": finalize,
         "verify-candidate": verify_candidate, "verify-rollback": verify_rollback,
         "assemble-rollback": assemble_rollback}[args.command](args)
    except (PublicationError, OSError, KeyError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"VIRHE: {exc}", file=sys.stderr)
        raise SystemExit(1)

if __name__ == "__main__":
    main()
