#!/usr/bin/env python3
"""Synthetic public-record capture exemplar for the capture recipe.

This is not the SI collection. The SI collection graph is built by
si_graphs/graphs/build_si_graph.py. This file is the small graph the recipe
snippet is copied from.
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "python"))

from case_uco import CASEGraph
from case_uco.case.investigation import Investigation, InvestigativeAction, ProvenanceRecord
from case_uco.uco.action import ActionArgumentFacet
from case_uco.uco.core import Annotation, UcoObject
from case_uco.uco.observable import ContentDataFacet, FileFacet, ObservableObject, URL, URLFacet
from case_uco.uco.types import Hash

OUT = Path(__file__).with_name("capture.jsonld")


def main() -> None:
    graph = CASEGraph(kb_prefix="https://example.org/kb/")
    digest = Hash(hash_method="SHA256", hash_value="ab" * 32)
    graph.add(digest, id="kb:hash-example")
    file_facet = FileFacet(
        file_name=["order.html"],
        file_path=["data/order.html"],
        extension="html",
        size_in_bytes=128,
    )
    content_facet = ContentDataFacet(
        hash=[digest],
        mime_type=["text/html"],
        size_in_bytes=128,
    )
    graph.add(file_facet, id="kb:file-facet-order")
    graph.add(content_facet, id="kb:content-facet-order")
    captured = ObservableObject(
        name="Example order HTML",
        has_facet=[file_facet, content_facet],
    )
    graph.add(captured, id="kb:file-order-html")
    url_facet = URLFacet(
        full_value="https://example.test/order",
        scheme="https",
        path="/order",
    )
    graph.add(url_facet, id="kb:url-facet-order")
    url = URL(name="https://example.test/order", has_facet=[url_facet])
    graph.add(url, id="kb:url-order")
    http_ok = ActionArgumentFacet(argument_name="http_status", value="200")
    graph.add(http_ok, id="kb:arg-http-order")
    fetch = InvestigativeAction(
        name="HTTP GET data/order.html",
        end_time=datetime(2026, 10, 7, 22, 32, 51, tzinfo=timezone.utc),
        action_status="Success",
        has_facet=[http_ok],
    )
    graph.add(fetch, id="kb:fetch-order")
    graph.add_property("kb:fetch-order", "uco-action:object", {"@id": "kb:url-order"})
    graph.add_property("kb:fetch-order", "uco-action:result", {"@id": "kb:file-order-html"})
    work = UcoObject(
        name="Example Order 1",
        description=[
            "Typed as uco-core:UcoObject because CASE/UCO has no executive-order class. "
            "A published signing date of 2026-09-29 is date-only and is not written to startTime."
        ],
    )
    graph.add(work, id="kb:work-order-1")
    graph.create_relationship(
        "kb:file-order-html",
        "kb:work-order-1",
        "Characterizes",
        description="The captured HTML is a rendition of the order. The vocabulary has no rendition kind.",
    )
    other = UcoObject(name="Example memorandum")
    graph.add(other, id="kb:work-memo")
    graph.create_relationship(
        "kb:work-order-1",
        "kb:work-memo",
        "Related_To",
        description="Verified substring in the order text: Memorandum M-1. The vocabulary has no Cites kind.",
    )
    note = Annotation(
        name="Curator label",
        statement=[
            "Collector see_also is a curator label. It is an Annotation, not a Relationship."
        ],
        object=[work],
    )
    graph.add(note, id="kb:note-curator")
    http_fail = ActionArgumentFacet(argument_name="http_status", value="HTTP 403")
    graph.add(http_fail, id="kb:arg-http-missing")
    failed = InvestigativeAction(
        name="HTTP GET missing-release",
        action_status="Fail",
        description=["No content file was stored."],
        has_facet=[http_fail],
    )
    graph.add(failed, id="kb:fetch-missing")
    record = ProvenanceRecord(
        name="Example capture provenance",
        exhibit_number="EXAMPLE",
        object=[fetch, captured],
    )
    graph.add(record, id="kb:provenance-example")
    investigation = Investigation(
        name="Example public-record capture",
        object=[captured, url, work, other, fetch, failed, note, record],
    )
    graph.add(investigation, id="kb:investigation-example")
    graph.write(str(OUT))
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
