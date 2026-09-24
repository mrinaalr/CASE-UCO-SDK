# Workbench

Local bench for UMass HRPO NHSR #8252, *On the Mechanics of Exploitation*. This branch has the close-read graphs, the keyword index, and the trajectories extension those graphs were written against. It does not include the court PDFs, the press corpus, or the catalog inventory of that copy.

The study question is how a fraud pathway changes as the technology changes. The pathway might start with a telephone script, purchased lists and paper mail, email and wires, a lender portal, a dating site used to recruit a mule, or a care relationship used to reach a bank account. The eight fraud machines are that study.

Eight more machines test the same method on forced labor and on cyber pathways. They are not the fraud study.

## Scale

Copy refreshed 23 September 2026, 11:44 PM ET, from the frozen CaseNoesis harvest (collector stopped 11:37 PM). About 1.4 GB. Press index is one row per URL.

| Layer | Count |
| --- | ---: |
| Files in the copy | 4,302 |
| PDFs | 2,976 |
| Distinct press URLs (`press_lookup.jsonl`) | 45,159 |
| Fraud press with full text, and the public fraud lookup | 40,958 |
| State press records | 50 |
| Public fraud court lookup | 264 documents, 210 dockets |
| Distinct RECAP documents | 793 |
| Cases | 721 |
| `recap/bulk` | 506 PDFs, 499 dockets |
| `recap/fraud` including `from_press` | 277 PDFs |
| `recap/csea` | 12 PDFs, 7 dockets, not read |

Press by domain: fraud 41,087, trafficking 3,140, CSEA 670, forced labor 197, cyber 65.

Cases, counted once: sex trafficking 341, forced labor 119, labor trafficking 22, named trafficking follow-ups 17, fraud 215, child-exploitation folder 7. Three fraud dockets also appear in the bulk harvest and are not counted again. Eight further fraud case numbers are PDFs that are not in the court lookup. The public fraud lookup is the same 40,958 releases as the full-text file, with the article body removed.

`recap/trafficking` is 55 copies of usable forced-labor and labor-trafficking charging instruments. Originals stay in `bulk`. The old civil filings in that folder were deleted. The 341-file `"sex trafficking" indictment` search stays in `bulk` only, because that query mixes adult sex trafficking with child-exploitation filings.

`recap/cyber` is 4 filings: Palafox and Gugnin (copies of the indictments in `fraud/from_press`) and two civil forfeiture complaints that state a crypto pathway. A trial transcript, a lawyer letter, warrants, and unread forfeiture complaints were removed.

## Close-read machines

Eighteen close-read Turtle files in `machines/v0.0.0/*.ttl`: sixteen from court instruments and two phase-label graphs, `production-2251.ttl` and `enticement-2422.ttl`. Four keyword graphs live under `recap/` and are not part of that eighteen. Each close read validates with trajectories, legal-process, time, and PROV-O. Adepoju, Cofer, Matson, and Obaseki also load the layered extension. Palafox, the pig-butchering complaint, and Stormgain load the cryptocurrency extension. Askarkhodjaev loads the RICO extension. The eighteen were revalidated for v0.0.2. All `Conforms: True`, zero violations.

A close read uses the trajectories extension. States are individuals of `traj:State` and `skos:Concept`, not new classes. Each step is a `PhaseAssertion` with its own confidence facet. Confidence **55** means the public instrument says so. A transition records the order the document states. The thing on `uco-action:instrument` is typed when CASE/UCO has the class: phone account, email, message, file, application, payment card, organization. Persons, organizations, locations, victim roles, and relationships are added only where the instrument names them. A `legalproc:ChargingInstrument` and `legalproc:FederalCharge` sit on the criminal cases. The two civil forfeitures are investigations and files, not charging instruments. `uco-core:tag "inference"` marks a label the instrument does not state. Where the instrument gives one conspiracy window, every occupancy shares that window. v0.0.1 of the machines dates the count tables and overt acts that were already in those PDFs. Augustine is the only one of the sixteen court instruments with a plea and sentencing memoranda on disk. Layered graphs are only for a case that runs more than one pathway at once.

The fraud eight are the study bench: Alcedo (phone and script), Augustine (lists and mail), Cofer (access in the room), Adepoju (executive-impersonation email), Odus (the laundering end of a business-email compromise), Obaseki (three pathways at once), Hunt (a lender portal), Matson (a warning stops one channel). Each close read carries the same benefit-at-expense test (trajectories v0.5.0). It passes when an identified person supplies the gain, does not keep it, and the instrument alleges deception, coercion, or vulnerability. The gain is their preexisting thing, their activity, or use of them. A preexisting object passes the narrower extraction half. Activity and use pass the expense test and fail that object half. A completed crime whose gain is not a person's, including Hunt's program funds and Gugnin's bank access, fails. Naming a minor is not a pass. Castanos Garcia is already the elder-fraud exemplar and was not rebuilt. The use-of-a-minor proof is a synthetic exemplar in `extensions/trajectories/`, not a graph of a withheld court PDF.

The other eight: Palafox (bitcoin multilevel marketing), Gugnin (a payments firm in front of U.S. banks; overview only), a pig-butchering sequence as a civil forfeiture complaint states it, one wallet-link thread in a second forfeiture complaint, Rojas (domestic labor), Gonzalez (panhandling and document servitude), Askarkhodjaev (visa labor leasing; partial, the indictment is 126 pages), Taylor (unpaid call-center labor only). Case names, dates, and what was not phased are in `machines/v0.0.0/README.md`.

## Keyword graphs

`machines/v0.0.0/recap/*.ttl` is a different object. A controlled cue becomes a state. Confidence **40**. Sequence is the order of the cue list in `scripts/build_recap_machines.py`, not time. The script does not store the sentence. A company name or a statute definition can trip a cue.

| Graph | PDFs | Cases | Keyword trajectories | Otherwise |
| --- | ---: | ---: | ---: | --- |
| `bulk.ttl` | 506 | 499 | 70 | 4 hand-modeled, sealed 94, image-only 87, child-sexual withheld 133, no filing date 21, no cue 90 |
| `fraud.ttl` | 277 | 156 | 67 | 10 hand-modeled, sealed 24, image-only 5, child-sexual withheld 9, no filing date 10, no cue 31 |
| `trafficking.ttl` | 55 | 55 | 44 | 4 hand-modeled, no filing date 5, no cue 2 |
| `cyber.ttl` | 4 | 4 | 0 | all 4 hand-modeled |
| `csea` | 12 | 12 | 0 | not read |

Per-case status is `recap/manifest.json`. These four graphs validate. Conforms: True. The eighteen close reads were not regenerated.

## Noise

Kept in the harvest, left out of the close reads: sealed filings, image-only PDFs, child-sexual-exploitation matches, defense memos, trial transcripts, and civil orders. Some fraud lookup names are docket blurbs. Hunt's lookup row says Patel. The same indictment sometimes appears twice (Obaseki, Odus, Gonzalez, Rojas).

The hash inventory of the PDF copy is not in this branch. On the machine that holds the copy it is 4,302 files, rebuilt 24 September 2026. Twenty-two PDF paths are tagged `machine:modeled`: the sixteen court-instrument close reads, plus extra copies of Palafox, Gugnin, Gonzalez, Rojas, Askarkhodjaev, and Taylor. The two phase-label graphs are not in that PDF count. `machine:sealed` is 41. `machine:withheld` is 794. `machine:candidate` is 317 court PDFs with no close read yet.

## Sharing

This branch is the graphs and the write-up. The eighteen close reads are `machines/v0.0.0/*.ttl`: sixteen from court instruments and two phase-label graphs, `production-2251.ttl` and `enticement-2422.ttl`. `machines/v0.0.0/recap/` is the keyword index, four graphs, not those close reads. The predicate is `extensions/trajectories`. Layered, cryptocurrency, and RICO graphs also use `extensions/layered`, `extensions/cryptoinv`, and `extensions/rico`, which are already in the SDK. The PDF copy, the press text, and the catalog inventory are not in this branch.