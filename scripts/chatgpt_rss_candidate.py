"""Rakenna yhden topic-ajon useat kohderaportit yhteen RSS-syötteeseen."""
from __future__ import annotations

from datetime import datetime
from email.utils import format_datetime
import json
from pathlib import Path
from typing import Any
import uuid
import xml.etree.ElementTree as ET

import jsonschema

from scripts.github_module_adapters import GitHubAdapterError, PublicationCandidate
from scripts.module_registry import load_registry
from scripts.target_execution import load_module_targets

ROOT = Path(__file__).resolve().parents[1]


class ChatGPTRssCandidateBuilder:
    """Muodosta RSS-ehdokas ja nykyisen julkaisulaatuportin raportti.

    Kohderaportit yhdistetään moduulin yhteen topic-syötteeseen. GUID on
    deterministinen moduuli-/ajo-/kohdetunnisteesta, joten uusinta ei luo
    kaksoiskappaleita eikä muuta jo julkaistua sisältöä.
    """

    def __init__(self, *, root: Path = ROOT):
        self.root = Path(root).resolve()

    @staticmethod
    def _checked_at(value: str) -> datetime:
        """Lue aikavyöhykkeellinen ISO-aikaleima RSS:n pubDate-kenttää varten."""
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except (AttributeError, TypeError, ValueError) as exc:
            raise GitHubAdapterError("Kohderaportin checked_at ei ole kelvollinen.") from exc
        if parsed.tzinfo is None or parsed.utcoffset() is None:
            raise GitHubAdapterError("Kohderaportin checked_at tarvitsee aikavyöhykkeen.")
        return parsed

    def __call__(
        self, module_id: str, run_id: str, report_content: str, *,
        target_reports: list[dict[str, Any]] | None = None,
        publication_id: str | None = None,
        publication_metadata: dict[str, Any] | None = None,
        expected_feed_path: str | None = None,
        expected_public_url: str | None = None,
        target_id: str | None = None,
    ) -> PublicationCandidate:
        """Palauta publisherille täsmälleen yksi topic-syöte ja porttiraportti."""
        if not target_reports:
            raise GitHubAdapterError("Tuotantojulkaisussa vaaditaan kohdekohtaiset raportit.")
        if not publication_id or not expected_feed_path or not expected_public_url:
            raise GitHubAdapterError("Julkaisureitin kohde tai julkinen URL puuttuu.")
        if ":" in run_id or len(run_id) > 100:
            raise GitHubAdapterError("run_id ei sovi julkaisulaadun porttiraportin tunnisteeksi.")

        registry = load_registry(root=self.root, include_inactive=True)
        module = registry.modules.get(module_id)
        if module is None or module.definition.get("module_type") != "topic":
            raise GitHubAdapterError("RSS-ehdokas voidaan rakentaa vain topic-moduulille.")
        targets = load_module_targets(module.definition, root=self.root, require_active=False)
        target_by_id = {target["target_id"]: target for target in targets}

        feed_catalog = json.loads((self.root / "data/feed-catalog.json").read_text(encoding="utf-8"))
        feed_matches = [
            item for item in feed_catalog.get("feeds", [])
            if item.get("path") == expected_feed_path and item.get("type") == "topic"
        ]
        if len(feed_matches) != 1:
            raise GitHubAdapterError("Julkaisureitin syötepolku ei vastaa yhtä topic-syötettä.")
        feed_id = feed_matches[0]["id"]

        feed_file = (self.root / expected_feed_path).resolve()
        if not feed_file.is_relative_to(self.root) or not feed_file.is_file():
            raise GitHubAdapterError("RSS-syötteen lähtötiedostoa ei löydy repositoriosta.")
        try:
            tree = ET.parse(feed_file)
        except ET.ParseError as exc:
            raise GitHubAdapterError("Nykyinen RSS-syöte ei ole kelvollista XML:ää.") from exc
        rss_root = tree.getroot()
        if rss_root.tag != "rss":
            raise GitHubAdapterError("Nykyisen RSS-tiedoston juurielementti ei ole rss.")
        channel = rss_root.find("channel")
        if channel is None:
            raise GitHubAdapterError("RSS-syötteestä puuttuu channel-elementti.")

        existing: dict[str, ET.Element] = {}
        for item in channel.findall("item"):
            guid_element = item.find("guid")
            if guid_element is None or not (guid_element.text or "").strip():
                raise GitHubAdapterError("Nykyisessä RSS-syötteessä on GUIDiton item.")
            guid = (guid_element.text or "").strip()
            if guid in existing:
                raise GitHubAdapterError("Nykyisessä RSS-syötteessä on kaksois-GUID.")
            existing[guid] = item

        new_items: list[tuple[str, ET.Element]] = []
        report_guids: list[str] = []
        checked_times: list[datetime] = []
        seen_targets: set[str] = set()
        for report in target_reports:
            target_id_value = report.get("target_id")
            target = target_by_id.get(target_id_value)
            if target is None or target_id_value in seen_targets:
                raise GitHubAdapterError("Kohderaportti on tuntematon tai esiintyy useammin kuin kerran.")
            seen_targets.add(target_id_value)
            if report.get("target_version") != target["target_version"]:
                raise GitHubAdapterError("Kohderaportin versio ei vastaa seurantakohteen rekisteriä.")
            content = report.get("report_content")
            if not isinstance(content, str) or not content.strip():
                raise GitHubAdapterError("Kohderaportin sisältö on tyhjä.")
            period = report.get("period")
            if not isinstance(period, dict) or not period.get("start") or not period.get("end"):
                raise GitHubAdapterError("Kohderaportin seurantajakso puuttuu.")
            checked_at = self._checked_at(report.get("checked_at"))
            checked_times.append(checked_at)
            date_key = checked_at.date().isoformat()
            stable_id = uuid.uuid5(
                uuid.NAMESPACE_URL, f"aiheseurain:{module_id}:{run_id}:{target_id_value}"
            )
            guid = f"urn:aiheseurain:{feed_id}:{date_key}:{stable_id}"
            report_guids.append(guid)

            if guid in existing:
                old_content = existing[guid].findtext("description", default="")
                if old_content != content:
                    raise GitHubAdapterError("Saman run_id:n RSS-GUID on jo käytössä eri raporttisisällölle.")
                continue

            item = ET.Element("item")
            title = ET.SubElement(item, "title")
            title.text = f"{target['name']} – seurantaraportti {date_key}"
            description = ET.SubElement(item, "description")
            description.text = content
            pub_date = ET.SubElement(item, "pubDate")
            pub_date.text = format_datetime(checked_at)
            guid_element = ET.SubElement(item, "guid", {"isPermaLink": "false"})
            guid_element.text = guid
            new_items.append((guid, item))

        if not report_guids:
            raise GitHubAdapterError("RSS-ehdokkaaseen ei muodostunut raporttiviitteitä.")
        first_item = channel.find("item")
        insert_at = channel.index(first_item) if first_item is not None else len(channel)
        for offset, (_guid, item) in enumerate(new_items):
            channel.insert(insert_at + offset, item)

        feed_bytes = ET.tostring(rss_root, encoding="utf-8", xml_declaration=True)
        assessment = (publication_metadata or {}).get("publication_assessment")
        if not isinstance(assessment, dict):
            raise GitHubAdapterError("ChatGPT-tuloksesta puuttuu publication_assessment.")
        latest_checked = max(checked_times).isoformat()
        gate_report = {
            "schema_version": 2,
            "run_id": run_id,
            "task_id": feed_id,
            "feed_path": expected_feed_path,
            "checked_at": latest_checked,
            "checklist": assessment["checklist"],
            "decision": assessment["decision"],
            "reviewer_notes": assessment["reviewer_notes"],
            "claim_assessments": assessment["claim_assessments"],
        }
        gate_schema = json.loads((self.root / "schemas/julkaisuportti.schema.json").read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator.check_schema(gate_schema)
        jsonschema.Draft202012Validator(
            gate_schema, format_checker=jsonschema.FormatChecker()
        ).validate(gate_report)
        if gate_report["decision"] != "approved":
            raise GitHubAdapterError("Julkaisulaadun porttiraportti ei hyväksy julkaisua.")

        gate_path = f"reports/julkaisuportit/{run_id}.json"
        files = {
            expected_feed_path: feed_bytes.decode("utf-8"),
            gate_path: json.dumps(gate_report, ensure_ascii=False, indent=2) + "\n",
        }
        return PublicationCandidate(
            files=files,
            feed_path=expected_feed_path,
            public_url=expected_public_url,
            report_guid_refs=tuple(report_guids),
        )
