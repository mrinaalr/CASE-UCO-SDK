#!/usr/bin/env python3
"""Catalog the CaseNoesis workbench as one CASE/UCO graph.

Every file becomes an ObservableObject with a FileFacet and a SHA-256
ContentDataFacet. Deconfliction is in the graph:

- identical bytes share a ``duplicate-bytes`` Relationship onto one canonical path
- court-lookup rows that share a docket number point at one docket node

This does not invent exploitation state machines. It marks which files
already have a v0.0.0 machine, which charging instruments are candidates,
and which paths stay metadata-only so their narrative is not copied into
the catalog. Re-run after the workbench copy changes.

Usage:
    python scripts/catalog_workbench.py
    python scripts/catalog_workbench.py --data workbench/casenoesis-data --out workbench/catalog
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import uuid
from collections import defaultdict
from pathlib import Path

NS = uuid.UUID("6f0c1a2e-9b34-5d77-8e10-0c0a00000001")

def load_modeled_document_ids() -> dict[str, str]:
    """Same sixteen close reads the keyword builder refuses to regenerate."""
    path = Path(__file__).resolve().parent / "build_recap_machines.py"
    spec = importlib.util.spec_from_file_location("build_recap_machines", path)
    if spec is None or spec.loader is None:
        raise SystemExit(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return dict(module.HAND_MODELED)


MODELED_DOCUMENT_IDS = load_modeled_document_ids()

# PDF text previously read as under seal. The public docket line may not say so.
SEALED_DOCUMENT_IDS = {"460832126"}

CHARGING_KINDS = ("indictment", "complaint", "information", "plea", "factual", "superseding")

WITHHELD_PARTS = (
    "/csea/",
    "/csam/",
    "/enticement/",
    "/sextortion/",
    "/production/",
    "/ncmec",
    "/ceos",
    "cybertip",
)

COURT_PDF_DIRS = (
    "collected/recap/fraud/",
    "collected/recap/cyber/",
    "collected/recap/trafficking/",
    "collected/PACER/",
)


def iri_for(key: str) -> str:
    return f"<urn:uuid:{uuid.uuid5(NS, key)}>"


def turtle_string(value: str) -> str:
    escaped = (
        value.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\n", "\\n")
        .replace("\r", "\\r")
    )
    return f'"{escaped}"'


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def load_fraud_court_lookup(data_root: Path) -> dict[str, dict]:
    path = data_root / "collected/public/fraud_court_lookup.jsonl"
    rows: dict[str, dict] = {}
    if not path.is_file():
        return rows
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            document_id = str(row.get("document_id") or "").strip()
            if document_id:
                rows[document_id] = row
    return rows


def domain_for(rel: str) -> str:
    parts = rel.split("/")
    if len(parts) == 1:
        return "root"
    for name in ("fraud", "trafficking", "cyber", "csea"):
        if name in parts:
            return name
    if parts[0] == "collected" and len(parts) > 1:
        return parts[1]
    return parts[0]


def is_sealed(document_id: str, row: dict) -> bool:
    if document_id in SEALED_DOCUMENT_IDS:
        return True
    text = f"{row.get('case_name', '')} {row.get('document_description', '')}".lower()
    if "unseal" in text:
        return False
    return "sealed" in text or "under seal" in text


def withheld(rel: str) -> bool:
    lowered = f"/{rel.lower()}/"
    return any(part.lower() in lowered for part in WITHHELD_PARTS)


def machine_status(rel: str, document_id: str, document_kind: str, row: dict) -> str:
    if document_id in MODELED_DOCUMENT_IDS:
        return "modeled"
    if is_sealed(document_id, row):
        return "sealed"
    if withheld(rel):
        return "withheld"
    kind = document_kind.lower()
    if any(token in kind for token in CHARGING_KINDS):
        return "candidate"
    if rel.endswith(".pdf") and any(rel.startswith(prefix) for prefix in COURT_PDF_DIRS):
        if not rel.startswith("collected/PACER/BULK_FOLDER/"):
            return "candidate"
    return "catalog-only"


def role_for(rel: str) -> str:
    if "/press_releases/" in f"/{rel}/" and rel.endswith(".pdf"):
        return "press-pdf"
    if rel.endswith(".pdf"):
        return "court-pdf" if "/recap/" in f"/{rel}/" or "/PACER/" in f"/{rel}/" else "pdf"
    if rel.endswith((".jsonl", ".json", ".jsonld", ".csv", ".txt", ".md")):
        return "index"
    return "other"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=Path("workbench/casenoesis-data"))
    parser.add_argument("--out", type=Path, default=Path("workbench/catalog"))
    args = parser.parse_args()

    data_root = args.data.resolve()
    out_dir = args.out.resolve()
    if not data_root.is_dir():
        raise SystemExit(f"data directory missing: {data_root}")
    out_dir.mkdir(parents=True, exist_ok=True)

    lookup = load_fraud_court_lookup(data_root)
    files = sorted(path for path in data_root.rglob("*") if path.is_file() and path.name != ".DS_Store")

    records = []
    by_hash: dict[str, list[str]] = defaultdict(list)
    for path in files:
        rel = path.relative_to(data_root).as_posix()
        document_id = path.stem if path.suffix.lower() == ".pdf" and path.stem.isdigit() else ""
        row = lookup.get(document_id, {})
        digest = sha256_file(path)
        by_hash[digest].append(rel)
        records.append(
            {
                "rel": rel,
                "name": path.name,
                "suffix": path.suffix.lower().lstrip("."),
                "size": path.stat().st_size,
                "sha256": digest,
                "document_id": document_id,
                "row": row,
                "domain": str(row.get("domain") or domain_for(rel)),
                "status": machine_status(rel, document_id, str(row.get("document_kind") or ""), row),
                "role": role_for(rel),
            }
        )

    canonical = {digest: sorted(paths, key=lambda item: (len(item), item))[0] for digest, paths in by_hash.items()}

    graph_path = out_dir / "workbench.ttl"
    summary = {
        "files": len(records),
        "duplicate_clusters": sum(1 for paths in by_hash.values() if len(paths) > 1),
        "duplicate_extra_copies": sum(len(paths) - 1 for paths in by_hash.values() if len(paths) > 1),
        "by_status": {},
        "by_domain": {},
        "by_role": {},
        "modeled": [],
        "candidates": [],
    }
    dockets: dict[str, str] = {}
    docket_edges = 0
    duplicate_edges = 0

    with graph_path.open("w", encoding="utf-8") as out:
        out.write(
            """# CaseNoesis workbench catalog.
# Generated by scripts/catalog_workbench.py.
# Byte duplicates and shared docket numbers are Relationship nodes.
# machine:modeled files have a v0.0.0 state machine.
# machine:candidate files are charging-document PDFs not yet machined.
# machine:withheld files are cataloged as hashes and paths only.
# machine:sealed files stay in the catalog as public docket metadata. Do not extract the PDF.

@prefix uco-core: <https://ontology.unifiedcyberontology.org/uco/core/> .
@prefix uco-observable: <https://ontology.unifiedcyberontology.org/uco/observable/> .
@prefix uco-types: <https://ontology.unifiedcyberontology.org/uco/types/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

"""
        )
        catalog_iri = iri_for("catalog")
        out.write(
            f"{catalog_iri} a uco-core:UcoObject ;\n"
            f"\tuco-core:name \"CaseNoesis workbench catalog\" ;\n"
            f"\tuco-core:description {turtle_string('Provenance catalog of workbench/casenoesis-data. SHA-256 identifies duplicate bytes. Fraud court-lookup rows attach docket, document kind, and CourtListener URL. Exploitation state machines are separate graphs, linked by tag machine:modeled. Paths under csea, enticement, sextortion, production, ncmec, and ceos are metadata-only. NHSR: UMass HRPO NHSR #8252 (16 Sep 2026).')} ;\n"
            f"\tuco-core:tag \"catalog:workbench\" .\n\n"
        )

        for record in records:
            rel = record["rel"]
            file_iri = iri_for("file:" + rel)
            facet_iri = iri_for("file-facet:" + rel)
            content_iri = iri_for("content:" + rel)
            hash_iri = iri_for("hash:" + rel)
            row = record["row"]
            summary["by_status"][record["status"]] = summary["by_status"].get(record["status"], 0) + 1
            summary["by_domain"][record["domain"]] = summary["by_domain"].get(record["domain"], 0) + 1
            summary["by_role"][record["role"]] = summary["by_role"].get(record["role"], 0) + 1

            description_bits = [
                f"path={rel}",
                f"role={record['role']}",
                f"machine={record['status']}",
            ]
            if record["status"] == "modeled":
                description_bits.append(f"machine-graph={MODELED_DOCUMENT_IDS[record['document_id']]}")
                summary["modeled"].append({"path": rel, "graph": MODELED_DOCUMENT_IDS[record["document_id"]]})
            elif record["status"] == "candidate":
                summary["candidates"].append(rel)
            if record["status"] != "withheld":
                if row.get("case_name"):
                    description_bits.append(f"case={row['case_name']}")
                if row.get("docket_number"):
                    description_bits.append(f"docket={row['docket_number']}")
                if row.get("document_kind"):
                    description_bits.append(f"kind={row['document_kind']}")
                if row.get("absolute_url"):
                    description_bits.append(f"url={row['absolute_url']}")
                if row.get("document_description"):
                    description_bits.append(str(row["document_description"])[:400])
            else:
                description_bits.append("metadata-only; narrative not copied into this catalog")

            tags = [
                f"domain:{record['domain']}",
                f"role:{record['role']}",
                f"machine:{record['status']}",
            ]
            tag_lines = " ,\n\t\t".join(turtle_string(tag) for tag in tags)
            suffix = record["suffix"]
            extension_line = f"\tuco-observable:extension {turtle_string(suffix)} ;\n" if suffix else ""

            out.write(
                f"{file_iri} a uco-observable:ObservableObject ;\n"
                f"\tuco-core:name {turtle_string(record['name'])} ;\n"
                f"\tuco-core:description {turtle_string(' | '.join(description_bits))} ;\n"
                f"\tuco-core:tag {tag_lines} ;\n"
                f"\tuco-core:hasFacet {facet_iri} , {content_iri} .\n\n"
                f"{facet_iri} a uco-observable:FileFacet ;\n"
                f"\tuco-observable:fileName {turtle_string(record['name'])} ;\n"
                f"\tuco-observable:filePath {turtle_string(rel)} ;\n"
                f"{extension_line}"
                f"\tuco-observable:sizeInBytes \"{record['size']}\"^^xsd:integer .\n\n"
                f"{content_iri} a uco-observable:ContentDataFacet ;\n"
                f"\tuco-observable:hash {hash_iri} .\n\n"
                f"{hash_iri} a uco-types:Hash ;\n"
                f"\tuco-types:hashMethod \"SHA256\" ;\n"
                f"\tuco-types:hashValue \"{record['sha256']}\"^^xsd:hexBinary .\n\n"
            )

            docket = str(row.get("docket_number") or "").strip()
            if docket and record["status"] != "withheld":
                if docket not in dockets:
                    dockets[docket] = iri_for("docket:" + docket)
                    out.write(
                        f"{dockets[docket]} a uco-core:UcoObject ;\n"
                        f"\tuco-core:name {turtle_string('Docket ' + docket)} ;\n"
                        f"\tuco-core:description {turtle_string('Deconfliction hub for fraud court-lookup docket ' + docket + '.')} ;\n"
                        f"\tuco-core:tag \"deconfliction:docket\" .\n\n"
                    )
                edge = iri_for("docket-edge:" + rel)
                out.write(
                    f"{edge} a uco-core:Relationship ;\n"
                    f"\tuco-core:name {turtle_string('appears-on-docket ' + docket)} ;\n"
                    f"\tuco-core:kindOfRelationship \"appears-on-docket\" ;\n"
                    f"\tuco-core:isDirectional true ;\n"
                    f"\tuco-core:source {file_iri} ;\n"
                    f"\tuco-core:target {dockets[docket]} .\n\n"
                )
                docket_edges += 1

        for digest, paths in sorted(by_hash.items()):
            if len(paths) < 2:
                continue
            keep = canonical[digest]
            keep_iri = iri_for("file:" + keep)
            for rel in paths:
                if rel == keep:
                    continue
                edge = iri_for("dup:" + rel)
                out.write(
                    f"{edge} a uco-core:Relationship ;\n"
                    f"\tuco-core:name \"duplicate-bytes\" ;\n"
                    f"\tuco-core:description {turtle_string(rel + ' has the same SHA-256 as ' + keep)} ;\n"
                    f"\tuco-core:kindOfRelationship \"duplicate-bytes\" ;\n"
                    f"\tuco-core:isDirectional true ;\n"
                    f"\tuco-core:source {iri_for('file:' + rel)} ;\n"
                    f"\tuco-core:target {keep_iri} .\n\n"
                )
                duplicate_edges += 1

    summary["dockets"] = len(dockets)
    summary["docket_edges"] = docket_edges
    summary["duplicate_edges"] = duplicate_edges
    summary["graph"] = str(graph_path)
    summary_path = out_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: summary[k] for k in ("files", "duplicate_clusters", "duplicate_extra_copies", "dockets", "docket_edges", "duplicate_edges", "by_status")}, indent=2))


if __name__ == "__main__":
    main()
