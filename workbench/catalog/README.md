# Workbench catalog

`scripts/catalog_workbench.py` writes `workbench.ttl`, a CASE/UCO graph of every file under `workbench/casenoesis-data/`.

Each file is an `ObservableObject` with a `FileFacet` (path, name, size) and a SHA-256 `ContentDataFacet`. Deconfliction is a `Relationship`:

- `duplicate-bytes` points an extra copy at the canonical path with the same hash
- `appears-on-docket` points a fraud court-lookup PDF at a shared docket node

Tags on each file:

| Tag | Meaning |
| --- | --- |
| `machine:modeled` | A v0.0.0 state machine already exists |
| `machine:candidate` | Court PDF worth a later machine. Not a machine yet |
| `machine:sealed` | Public docket line only. Do not extract the PDF |
| `machine:withheld` | CSEA, enticement, sextortion, production, NCMEC, or CEOS path. Hash and path only |
| `machine:catalog-only` | Indexed, including press releases. Not a charging-document machine |

The current MCP tools (`process_document_file`, `route_investigation_content`, `validate_graph`) run on one document. They do not emit exploitation state machines and they do not deconflict a corpus. This script is the scale step. Re-run it after the data copy changes, then validate:

```bash
python scripts/catalog_workbench.py
```

Counts are in `summary.json`. Rebuilt 24 September 2026 from the current `casenoesis-data` copy: 4,302 files. `machine:modeled` is 22 PDF paths, the sixteen close reads and their extra copies. The graph conforms.
