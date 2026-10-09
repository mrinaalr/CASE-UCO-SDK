# Elder-Fraud Exploitation State Machine Extension (`elder-fraud`)

Narrow, machine-only extension: contributes **only** what the
[trajectories](../trajectories/) Exploitation State Machine (ESM) needs to
run on a transnational grandparent-scam / elder-fraud offense — a phase
vocabulary and a small action catalog. It is not a domain ontology: no
class hierarchy beyond the `uco-action:Technique` metaclass pattern already
established by [attack-technique](../attack-technique/), and no bespoke
victim/instrument/role taxonomy.

## Case

**United States v. Oscar Manuel Castanos Garcia, et al.**, No.
1:24-cr-10138-LTS (D. Mass.) — a Dominican Republic call-center
"grandparent scam" enterprise; 400+ victims, average age 84, $5M+ in
losses. Both sources are public DOJ URLs — no PACER, nothing vendored
in-repo:

- USAO-MA press release, ["Operators of Transnational Elder Fraud Scheme
  Plead Guilty"](https://www.justice.gov/usao-ma/pr/operators-transnational-elder-fraud-scheme-plead-guilty)
  (2026-07-15) — cited as "PR" in the ontology/exemplar.
- Detention Affidavit, *USA v. Oscar Manuel Castanos Garcia, et al.*,
  publicly hosted at
  [justice.gov/usao-ma/media/1410886/dl](https://www.justice.gov/usao-ma/media/1410886/dl?inline)
  — cited as "Aff." Affiant identity and internal paragraph numbering are
  **not** asserted anywhere in this extension: they aren't traceable
  without fetching the PDF, which this extension does not vendor, so all
  citations are document-level ("Aff." vs "PR"), not pinpoint.

## Phases (`ef:PhaseScheme`)

| State | What it is |
|---|---|
| `ef:InitialContact` | "Opener" cold-calls the victim (VoIP + fixed script + isolation line) |
| `ef:Conditioning` | "Closer" impersonates attorney and directs cash payment |
| `ef:ExtractionInstruction` | Closer directs cash form + hand-off method (payment logistics) |
| `ef:ProceedsCollection` | A U.S.-based runner physically obtains the cash |
| `ef:Laundering` | Proceeds deposited into purported-business accounts, structured <$10k |
| `ef:Completed` | Terminal: cross-border transmission realizes the modeled endpoint |

Exogenous **pre-s₀** (not in S): victim-list purchase as `prov:Activity`
(`cg:activity-target-acquisition` in the exemplar), feeding
`InitialContact`.

## Actions (`uco-action:Technique` classes)

| Class | techniqueID | What it is |
|---|---|---|
| `ef:a_spoof` | `EF.T1` | Caller-ID / VoIP spoofing |
| `ef:a_script` | `EF.T2` | Fixed-script deployment |
| `ef:a_secrecy` | `EF.T3` | Isolation / secrecy instruction (opener script) |
| `ef:a_coopt` | `EF.T4` | Co-opting an unwitting intermediary |
| `ef:a_fakeid` | `EF.T5` | Purported-business bank account |
| `ef:a_deposit` | `EF.T6` | Deposit structuring <$10k |
| `ef:a_transmit` | `EF.T7` | Cross-border proceeds transmission |
| `ef:a_direct` | `EF.T8` | Payment-mechanism direction (Closer → cash hand-off) |

## Exemplar

`elder-fraud-exemplar.ttl` carries **two** real `traj:Trajectory` instances
over the same shared phase/transition/action vocabulary:

- `cg:trajectory-agawam-2023` — full run through `ef:Completed` (February
  2023 Agawam, MA rideshare pickup + laundering/transmit pipeline),
  `traj:terminalPolarity "completed"`.
- `cg:trajectory-attleboro-2022` — short run ending mid-chain at
  `ProceedsCollection` (Attleboro UPS Sept./Oct. 2022 arrest),
  `traj:terminalPolarity "disrupted"`.

### FACT CORRECTION (source overrides a prior ESM draft)

Aff. places the secrecy line — *"Please, promise that you will keep this
between us until i get out"* — in the **opener** script (grandchild
persona / `InitialContact`), **not** in the Closer/`Conditioning` phase.
Accordingly `a_secrecy` gates `InitialContact -> Conditioning` together
with `a_spoof` and `a_script`. `Conditioning -> ExtractionInstruction` is
gated by `a_direct` (Closer payment-mechanism direction). Update any
external ESM write-up that still puts `a_secrecy` on the
Conditioning→ExtractionInstruction edge.

### `traj:enactsAction` wiring (arriving-state; multi-valued edges)

| Transition | `enactsAction` | Produces |
|---|---|---|
| `InitialContact -> Conditioning` | `a_spoof`, `a_script`, `a_secrecy` | `Conditioning` |
| `Conditioning -> ExtractionInstruction` | `a_direct` | `ExtractionInstruction` |
| `ExtractionInstruction -> ProceedsCollection` | `a_coopt` | `ProceedsCollection` |
| `ProceedsCollection -> Laundering` | `a_fakeid`, `a_deposit` | `Laundering` |
| `Laundering -> Completed` | `a_transmit` | `Completed` |

Multi-action edges require multi-valued `traj:enactsAction` (trajectories
SHACL: no `sh:maxCount` on that property).

Aff. also states closers impersonated attorneys; that fact is carried in
`Conditioning` occupancy text only — structural `a_fakeid` is the
purported-business account on the laundering edge.

## Validation

```python
from case_uco.validation import validate_graph_file

validate_graph_file(
    "extensions/elder-fraud/elder-fraud-exemplar.ttl",
    extensions=["elder-fraud"],
    profiles=["time", "prov-o"],
    strict_concepts=True,
    force_rdfs_inference=True,
)
```

`depends_on: ["trajectories", "attack-technique"]` in `manifest.json` pulls
in both automatically.
