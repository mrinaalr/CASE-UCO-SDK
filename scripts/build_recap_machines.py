#!/usr/bin/env python3
"""One v0.0.0 machine per RECAP case.

Reads court PDFs under collected/recap/{bulk,cyber,fraud,trafficking}.
Does not read PACER, press releases, or collected/recap/csea.

A machine is a traj:Trajectory. A state is emitted only when a controlled
cue appears in that case's text. State order is the vocabulary order, not
the indictment's chronology. Confidence is 40. No passage from the PDF is
copied into the graph.

Child-sexual-exploitation filings, sealed filings, and image-only PDFs are
counted in the manifest and do not get a phase graph.

Cases already modeled by hand in workbench/machines/v0.0.0/*.ttl are listed
and not generated again.

Usage:
    python scripts/build_recap_machines.py
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import uuid
from collections import defaultdict
from pathlib import Path

NS = uuid.UUID("6f0c1a2e-9b34-5d77-8e10-0c0a00000001")

COLLECTIONS = ("bulk", "cyber", "fraud", "trafficking")

HAND_MODELED = {
    "438504917": "workbench/machines/v0.0.0/alcedo-english-course.ttl",
    "449969604": "workbench/machines/v0.0.0/augustine-inheritance.ttl",
    "217799634": "workbench/machines/v0.0.0/obaseki-multi-scheme.ttl",
    "141451183": "workbench/machines/v0.0.0/cofer-insider-account.ttl",
    "442720807": "workbench/machines/v0.0.0/adepoju-phishing-w2.ttl",
    "385303248": "workbench/machines/v0.0.0/odus-bec-laundering.ttl",
    "432127749": "workbench/machines/v0.0.0/hunt-ppp-portal.ttl",
    "186541465": "workbench/machines/v0.0.0/matson-romance-recruiter.ttl",
    "437269300": "workbench/machines/v0.0.0/palafox-bitcoin-mlm.ttl",
    "442161436": "workbench/machines/v0.0.0/gugnin-evita-payments.ttl",
    "454395974": "workbench/machines/v0.0.0/pigbutcher-usdt-forfeiture.ttl",
    "385173671": "workbench/machines/v0.0.0/stormgain-wallet-backdoor.ttl",
    "458211891": "workbench/machines/v0.0.0/rojas-domestic-labor.ttl",
    "111384977": "workbench/machines/v0.0.0/gonzalez-ivm-labor.ttl",
    "6053810": "workbench/machines/v0.0.0/askarkhodjaev-visa-labor.ttl",
    "488069557": "workbench/machines/v0.0.0/taylor-call-center-labor.ttl",
}

# (state local name, cue). Descriptions are fixed. Match text is never stored.
SIGNALS: list[tuple[str, str, re.Pattern[str]]] = [
    ("Phone", "Telephone or a phone call appears in the filing.", re.compile(r"\b(telephone|phone call|cellular phone)\b", re.I)),
    ("Email", "Email appears as a channel in the filing.", re.compile(r"\be-?mails?\b", re.I)),
    ("MessagingApp", "A messaging app or text message appears in the filing.", re.compile(r"\b(whatsapp|telegram|text messages?)\b", re.I)),
    ("SocialOrDating", "A dating site or social-media service appears in the filing.", re.compile(r"\b(dating (?:website|site|app)|social media)\b", re.I)),
    ("Mail", "Mail or a commercial carrier appears in the filing.", re.compile(r"\b(u\.s\. mail|united states postal|priority mail|federal express|fedex)\b", re.I)),
    ("Impersonation", "Impersonation or a pretended identity appears in the filing.", re.compile(r"\b(impersonat\w*|purporting to be|pretended to be)\b", re.I)),
    ("Phishing", "Phishing appears in the filing.", re.compile(r"\bphish\w*\b", re.I)),
    ("Coercion", "Force, threats, or coercion appear in the filing.", re.compile(r"\b(threaten\w*|coerc\w*|physical force|forced labor)\b", re.I)),
    ("Recruit", "Recruitment appears in the filing.", re.compile(r"\brecruit\w*\b", re.I)),
    ("Transport", "Transport, harboring, or smuggling appears in the filing.", re.compile(r"\b(transport\w*|harbor(?:ing|ed)?|harbour(?:ing|ed)?|smuggl\w*)\b", re.I)),
    ("Labor", "Forced labor, involuntary servitude, or peonage appears in the filing.", re.compile(r"\b(forced labor|involuntary servitude|peonage)\b", re.I)),
    ("Debt", "A smuggling debt or debt bondage appears in the filing.", re.compile(r"\b(debt bondage|smuggling debt)\b", re.I)),
    ("Passport", "A passport, visa, or immigration document appears in the filing.", re.compile(r"\b(passport|immigration document)\b", re.I)),
    ("WireOrPayment", "A wire, money order, gift card, or money transmitter appears in the filing.", re.compile(r"\b(wire transfer|money order|gift cards?|western union|moneygram|cashier'?s checks?)\b", re.I)),
    ("Crypto", "Bitcoin or another virtual currency appears in the filing.", re.compile(r"\b(bitcoin|cryptocurrency|virtual currency)\b", re.I)),
    ("Account", "A bank account, payment card, or unauthorized access appears in the filing.", re.compile(r"\b(bank accounts?|debit cards?|credit cards?|unauthorized access)\b", re.I)),
    ("Mule", "A money mule appears in the filing.", re.compile(r"\bmoney mules?\b", re.I)),
    ("Romance", "A romance fiction appears in the filing.", re.compile(r"\bromance\b", re.I)),
    ("ProgramPortal", "A lending, benefits, or unemployment program appears in the filing.", re.compile(r"\b(paycheck protection|ppp loan|unemployment insurance)\b", re.I)),
    ("CommercialSexPurpose", "Commercial-sex charging language appears. The act is not described in this graph.", re.compile(r"\b(commercial sex|sex trafficking)\b", re.I)),
]

CHILD_SEX = re.compile(
    r"(18\s*U\.?\s*S\.?\s*C\.?\s*§?\s*(?:2251|2252A?|2253|2422|2423)\b)"
    r"|child pornography"
    r"|sexual exploitation of (?:a |the )?(?:child|minor)"
    r"|\bminor victim\b"
    r"|under the age of (?:1[0-7]|[1-9])\b"
    r"|(?:\bminor\b|\bchild\b).{0,80}\b(?:sex|traffick|pornograph)",
    re.I | re.S,
)

CASE_NO = re.compile(r"\b(\d{1,2}:\d{2}-[Cc][Rr]-?\d{2,6})\b")
FILED = re.compile(
    r"(?:Filed|Entered on \w+ Docket)\s+(\d{1,2})/(\d{1,2})/(\d{2,4})",
    re.I,
)
DOCKET_URL = re.compile(r"/docket/(\d+)/")


def iri(key: str) -> str:
    return f"<urn:uuid:{uuid.uuid5(NS, key)}>"


def turtle_string(value: str) -> str:
    escaped = (
        value.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\n", " ")
        .replace("\r", " ")
    )
    return f'"{escaped}"'


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def pdf_text(path: Path) -> str:
    proc = subprocess.run(
        ["pdftotext", "-q", "-layout", str(path), "-"],
        capture_output=True,
        check=False,
    )
    return proc.stdout.decode("utf-8", errors="replace")


def filing_day(text: str) -> str | None:
    match = FILED.search(text[:4000])
    if not match:
        return None
    month, day, year = (int(part) for part in match.groups())
    if year < 100:
        year += 2000
    if not (1 <= month <= 12 and 1 <= day <= 31 and 1990 <= year <= 2030):
        return None
    return f"{year:04d}-{month:02d}-{day:02d}T12:00:00Z"


def normalize_case(value: str) -> str:
    return re.sub(r"\s+", "", value).upper().replace("CR", "cr")


def is_sealed(text: str, description: str) -> bool:
    blob = f"{description}\n{text[:2500]}".lower()
    if "unseal" in blob:
        return False
    return "under seal" in blob or "sealed indictment" in blob or "indictment (sealed)" in blob


def is_child_sexual(text: str) -> bool:
    return CHILD_SEX.search(text) is not None


def load_fraud_lookup(root: Path) -> dict[str, dict]:
    path = root / "collected/public/fraud_court_lookup.jsonl"
    rows: dict[str, dict] = {}
    if not path.is_file():
        return rows
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        rows[str(row.get("document_id") or "")] = row
    return rows


def load_bulk_links(root: Path) -> dict[str, dict]:
    path = root / "collected/recap/bulk/manifests/recap_links.jsonl"
    rows: dict[str, dict] = {}
    if not path.is_file():
        return rows
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        name = Path(str(row.get("pdf") or "")).name
        if name:
            rows[name] = row
    return rows


def harvest_family(query: str) -> str:
    text = (query or "").lower()
    if "forced labor" in text or "involuntary servitude" in text:
        return "forced-labor"
    if "sex traffick" in text:
        return "sex-trafficking"
    if "labor traffick" in text:
        return "labor-trafficking"
    if "human traffick" in text or "trafficking" in text:
        return "trafficking"
    return "unspecified"


def signals_for(text: str) -> list[tuple[str, str]]:
    found = []
    for name, description, pattern in SIGNALS:
        if pattern.search(text):
            found.append((name, description))
    return found


def write_case(
    out,
    *,
    collection: str,
    case_key: str,
    title: str,
    paths: list[str],
    when: str,
    found: list[tuple[str, str]],
    family: str,
) -> None:
    base = f"{collection}:{case_key}"
    doc = iri("recap-doc:" + base)
    evidence = iri("recap-ev:" + base)
    interval = iri("recap-int:" + base)
    start = iri("recap-t0:" + base)
    end = iri("recap-t1:" + base)
    trajectory = iri("recap-traj:" + base)
    day = when[:10]
    path_list = "; ".join(paths)
    out.write(
        f"{doc} a uco-core:UcoObject ;\n"
        f"\tuco-core:name {turtle_string(title[:240])} ;\n"
        f"\tuco-core:description {turtle_string('RECAP v0.0.0 keyword machine. Sources: ' + path_list + '. Interval is the filing day parsed from the PDF header, not an offense window. NHSR: UMass HRPO NHSR #8252 (16 Sep 2026).')} ;\n"
        f"\tuco-core:tag \"machine:keyword\" , {turtle_string('family:' + family)} , {turtle_string('collection:' + collection)} .\n\n"
    )
    out.write(
        f"{evidence} a uco-core:UcoObject ;\n"
        f"\tuco-core:name {turtle_string('Cues present in ' + case_key)} ;\n"
        f"\tuco-core:description {turtle_string('States record that a controlled cue occurs in the filing. The matched sentence is not stored. Cues: ' + ', '.join(name for name, _ in found))} .\n\n"
    )
    out.write(
        f"{interval} a time:ProperInterval ;\n"
        f"\ttime:hasBeginning {start} ;\n"
        f"\ttime:hasEnd {end} .\n"
        f"{start} a time:Instant ; time:inXSDDateTimeStamp \"{day}T00:00:00Z\"^^xsd:dateTimeStamp .\n"
        f"{end} a time:Instant ; time:inXSDDateTimeStamp \"{day}T23:59:00Z\"^^xsd:dateTimeStamp .\n\n"
    )
    phase_iris = []
    for index, (name, description) in enumerate(found):
        state = iri(f"recap-state:{base}:{name}")
        phase = iri(f"recap-phase:{base}:{name}")
        facet = iri(f"recap-conf:{base}:{name}")
        phase_iris.append(phase)
        out.write(
            f"{state} a traj:State , skos:Concept ;\n"
            f"\tskos:prefLabel {turtle_string(name)} ;\n"
            f"\tuco-core:description {turtle_string(description)} .\n"
            f"{facet} a uco-core:ConfidenceFacet ; uco-core:confidence \"40\"^^xsd:nonNegativeInteger .\n"
            f"{phase} a traj:PhaseAssertion ;\n"
            f"\tuco-core:name {turtle_string(f'{name} occupancy')} ;\n"
            f"\tuco-core:description {turtle_string(description + ' Vocabulary order index ' + str(index) + '. Not the indictment chronology.')} ;\n"
            f"\ttraj:assertsState {state} ;\n"
            f"\ttraj:atInterval {interval} ;\n"
            f"\ttraj:sequenceIndex \"{index}\"^^xsd:nonNegativeInteger ;\n"
            f"\tprov:wasDerivedFrom {evidence} ;\n"
            f"\tuco-core:hasFacet {facet} .\n\n"
        )
    joined = " , ".join(phase_iris)
    out.write(
        f"{trajectory} a traj:Trajectory ;\n"
        f"\tuco-core:name {turtle_string(title[:180] + ' keyword trajectory')} ;\n"
        f"\tuco-core:description \"v0.0.0 keyword machine. Occupancy order is the controlled vocabulary, not a finding that the case moved in that order.\" ;\n"
        f"\ttraj:hasPhaseAssertion {joined} .\n\n"
    )


def main() -> None:
    repo = Path(__file__).resolve().parents[1]
    data = repo / "workbench/casenoesis-data"
    out_dir = repo / "workbench/machines/v0.0.0/recap"
    out_dir.mkdir(parents=True, exist_ok=True)
    fraud_lookup = load_fraud_lookup(data)
    bulk_links = load_bulk_links(data)
    recap = data / "collected/recap"

    csea_pdfs = sorted((recap / "csea").rglob("*.pdf")) if (recap / "csea").is_dir() else []
    manifest: dict = {
        "csea_withheld_without_reading": [p.relative_to(data).as_posix() for p in csea_pdfs],
        "collections": {},
    }

    for collection in COLLECTIONS:
        folder = recap / collection
        pdfs = sorted(folder.rglob("*.pdf")) if folder.is_dir() else []
        groups: dict[str, list[Path]] = defaultdict(list)
        meta: dict[str, dict] = {}
        for path in pdfs:
            stem = path.stem
            if collection == "fraud":
                row = fraud_lookup.get(stem, {})
                docket = normalize_case(str(row.get("docket_number") or ""))
                url_id = ""
                match = DOCKET_URL.search(str(row.get("absolute_url") or ""))
                if match:
                    url_id = match.group(1)
                key = f"case-{docket}" if docket else (f"cl-{url_id}" if url_id else f"doc-{stem}")
                title = str(row.get("case_name") or f"RECAP fraud document {stem}")
                family = str(row.get("bucket") or "fraud")
                sealed_hint = str(row.get("document_description") or "")
            elif collection == "bulk":
                row = bulk_links.get(path.name, {})
                match = DOCKET_URL.search(str(row.get("absolute_url") or ""))
                url_id = match.group(1) if match else stem
                key = f"cl-{url_id}"
                title = str(row.get("case_name") or f"RECAP bulk document {stem}")
                family = harvest_family(str(row.get("query") or ""))
                sealed_hint = title
            else:
                key = f"doc-{stem}"
                title = f"RECAP {collection} document {stem}"
                family = collection
                sealed_hint = ""
                row = {}
            groups[key].append(path)
            slot = meta.setdefault(
                key,
                {"title": title, "family": family, "sealed_hint": sealed_hint, "rows": []},
            )
            slot["rows"].append(stem)
            if len(title) > len(slot["title"]):
                slot["title"] = title

        counts = {
            "pdfs": len(pdfs),
            "cases": len(groups),
            "machines": 0,
            "hand_modeled": 0,
            "sealed": 0,
            "image_only": 0,
            "child_sexual_withheld": 0,
            "no_filing_date": 0,
            "no_cue": 0,
        }
        cases_out = []
        graph_path = out_dir / f"{collection}.ttl"
        with graph_path.open("w", encoding="utf-8") as out:
            out.write(
                f"""# RECAP {collection} keyword machines, v0.0.0.
# One traj:Trajectory per case whose text contained a controlled cue.
# Generated by scripts/build_recap_machines.py. Passages are not copied.

@prefix traj: <http://example.org/ontology/trajectories/> .
@prefix uco-core: <https://ontology.unifiedcyberontology.org/uco/core/> .
@prefix time: <http://www.w3.org/2006/time#> .
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

"""
            )
            for key, paths in sorted(groups.items()):
                rels = [p.relative_to(data).as_posix() for p in paths]
                stems = [p.stem for p in paths]
                hand = [HAND_MODELED[stem] for stem in stems if stem in HAND_MODELED]
                if hand:
                    counts["hand_modeled"] += 1
                    cases_out.append({"case": key, "status": "hand-modeled", "graphs": hand, "pdfs": rels})
                    continue
                seen_hash = set()
                texts = []
                readable_rels = []
                for path, rel in zip(paths, rels):
                    digest = sha256_file(path)
                    if digest in seen_hash:
                        continue
                    seen_hash.add(digest)
                    text = pdf_text(path)
                    if len(text.strip()) < 500:
                        continue
                    texts.append(text)
                    readable_rels.append(rel)
                blob = "\n".join(texts)
                record = {"case": key, "title": meta[key]["title"][:180], "pdfs": rels, "family": meta[key]["family"]}
                if is_sealed(blob, meta[key]["sealed_hint"]):
                    counts["sealed"] += 1
                    record["status"] = "sealed"
                    cases_out.append(record)
                    continue
                if not texts:
                    counts["image_only"] += 1
                    record["status"] = "image-only"
                    cases_out.append(record)
                    continue
                if is_child_sexual(blob):
                    counts["child_sexual_withheld"] += 1
                    record["status"] = "withheld-child-sexual-exploitation"
                    cases_out.append(record)
                    continue
                when = filing_day(blob)
                if when is None:
                    counts["no_filing_date"] += 1
                    record["status"] = "no-filing-date"
                    cases_out.append(record)
                    continue
                found = signals_for(blob)
                if not found:
                    counts["no_cue"] += 1
                    record["status"] = "no-cue"
                    cases_out.append(record)
                    continue
                write_case(
                    out,
                    collection=collection,
                    case_key=key,
                    title=meta[key]["title"],
                    paths=readable_rels,
                    when=when,
                    found=found,
                    family=meta[key]["family"],
                )
                counts["machines"] += 1
                record["status"] = "machine"
                record["cues"] = [name for name, _ in found]
                cases_out.append(record)
        counts["graph"] = str(graph_path.relative_to(repo))
        manifest["collections"][collection] = {"counts": counts, "cases": cases_out}
        print(collection, json.dumps(counts))

    manifest_path = out_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print("manifest", manifest_path)


if __name__ == "__main__":
    main()
