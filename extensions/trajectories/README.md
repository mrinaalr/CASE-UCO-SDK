# Trajectories Extension (`trajectories`)

Vocabulary-agnostic **state-machine** and **per-case trajectory** metamodel
for CASE/UCO investigation graphs. Status: **`candidate`**.

## Phase 1 gaps this fills

| Gap | What existed | What `traj` adds |
|---|---|---|
| (1) Typed state | Domain-fixed CAC/AEO phase *classes* | `traj:State` instances (optionally `skos:Concept`) |
| (2) Transition + trigger/guard | CAC `PhaseTransitionEvent` (investigation-only); referral triggers | `traj:Transition` with `fromState` / `toState` / `trigger` / optional `guard` |
| (3) Ordered case occupancy + interval + evidence + confidence | Timestamps + `ConfidenceFacet` + PROV available but not bundled | `traj:Trajectory` of `traj:PhaseAssertion` (owl-time + `prov:wasDerivedFrom` + `ConfidenceFacet`) |
| (4) Learned transition probabilities | Scalar `transitionLikelihood` on one CAC class; no model artifact | `traj:StateMachineModel` + `traj:TransitionEstimate` with `prov:wasGeneratedBy` |

It does **not** re-model CAC grooming taxonomy, RICO enterprises, kill-chains, or drugs/weapons content — only the trajectory machinery.

## Contents

| File | Purpose |
|---|---|
| `trajectories.ttl` | OWL T-Box |
| `trajectories-shapes.ttl` | SHACL observed≠inferred firewall |
| `trajectories-profile-gufo.ttl` | Optional gUFO bridge (`State rdf:type gufo:Phase` metaclass; `PhaseAssertion`⊆`gufo:Situation`) |
| `trajectories-exemplar.ttl` | CAC grooming trajectory + model |
| `trajectories-elder-fraud-exemplar.ttl` | Non-CAC elder-fraud trajectory (EDLA 2022-cr-00115) |
| `trajectories-invalid-exemplar.ttl` | Expected-invalid firewall fixture |
| `trajectories-expense-exemplar.ttl` | Benefit-at-expense pass and fail cases |
| `trajectories-expense-invalid-exemplar.ttl` | Expected-invalid expense fixture |

## Design choices

### Ordering idiom

`traj:sequenceIndex` (xsd:nonNegativeInteger) on each `PhaseAssertion`,
referenced from `Trajectory` via `hasPhaseAssertion`.

- Preferred over `rdf:List` (awkward in SHACL/SPARQL).
- Preferred over AEO `ArrayOfAction` (planned narrative actions, not
  observed occupancy).
- Complementary to CAC `EventSequence` (investigation events), not a
  replacement.

### Confidence

Reuse **`uco-core:ConfidenceFacet`** on the assertion via
`uco-core:hasFacet` — no `traj:confidence` mint. SHACL requires ≥1
`ConfidenceFacet` on every `PhaseAssertion`.

### Terminal polarity (v0.2.0)

`traj:isTerminal` (xsd:boolean) marks the PhaseAssertion that is the final
observed occupancy in a Trajectory; `traj:terminalPolarity` (xsd:string,
SHACL `sh:in ("completed" "disrupted")`) types its realized outcome —
`completed` (the modeled chain reached its endpoint; later arrest/prosecution
does **not** flip this) vs. `disrupted` (an intervention ended the trajectory
**mid-chain**, before the modeled endpoint). SHACL requires
`isTerminal true => terminalPolarity present`; `terminalPolarity` alone never
requires a second, opposite-polarity branch to exist — single-path
trajectories that assert only one polarity are conformant.

Deliberately a property pair, not `traj:State` subclasses
(`SuccessTerminal`/`DisruptedTerminal`), so a third outcome type is a
vocabulary-list edit, not a T-Box change.

### Enacted actions and the affordance/φ seam (v0.3.0)

`traj:enactsAction` (domain `traj:Transition`, range `uco-action:Action`,
SHACL `sh:class uco-action:Action`) names the concrete typed action(s) that
**constitute** a transition — distinct from `traj:trigger`, which may be any
`uco-core:UcoObject` the transition merely reacts to. It is additive (no
`sh:minCount`): a Transition with only a bare-`UcoObject` `traj:trigger` and
no `traj:enactsAction` remains fully conformant.

### Multi-valued `enactsAction` (v0.3.1)

**Multiple** `enactsAction` values are allowed when one directed edge is gated
by co-occurring techniques (affordance-labeled multi-action edges in an ESM).
SHACL `sh:maxCount` on `traj:enactsAction` was removed in **v0.3.1** so those
edges validate. The current extension version is **0.5.0** (`manifest.json`).

### Benefit-at-expense test (v0.5.0)

`traj:BenefitAnatomy` and `traj:ExploitationAssessment` are inferred.
They are `owl:disjointWith` `traj:PhaseAssertion` and must carry
`prov:wasGeneratedBy`. They do not change the observed occupancies.

The definition is Zwolinski, Ferguson & Wertheimer, "Exploitation,"
*Stanford Encyclopedia of Philosophy*: to exploit is to take unfair
advantage, and the benefit is at the other person's expense. Offense
names are not inputs. Fraud, forced labor, trafficking, and sexual
exploitation of a minor pass or fail from the same facts.
[ThanosStateMachine issue 2](https://github.com/mrinaalr/ThanosStateMachine/issues/2).

Facts on the transition:

- `suppliedByPerson` — an identified person, or a company the instrument names as the holder or the worker, supplies the gain. False for a program, a sanctions regime, a market, or a system.
- `personRetainsValue` — that person keeps the value.
- `requiresPresence` — the benefit requires them to be present and producing. False for a taken object, and false when the benefit is their absence.
- `transferredObject`, `preexisting`, `valueSurvivesVictim` — the object half. A product made from the person is an object that did not exist beforehand.
- `advantageDefect` — `deception`, `coercion`, `vulnerability`, `none_alleged`, or `not_in_instrument`. Vulnerability means the instrument alleges the person could not validly agree because of age, dependency, or incapacity.

`benefitSource` is derived: `not_from_person`, `retained`, `victim_sourced`, `person_activity`, `person_used`, `victim_targeted`, or `none`. `person_used` is use of that person, or a product made from that use. SHACL rejects a hand-set string.

`passesExploitationTest` is true only when the goal edge derives `victim_sourced`, `person_activity`, or `person_used` and the defect is `deception`, `coercion`, or `vulnerability`. `passesExtractionTest` is the preexisting-object half and is true only for `victim_sourced`. `exploitationOnset` is the interval of that goal edge's arriving phase, and it is present only on a pass. That interval is when the graph says the trajectory became exploitation. A shared conspiracy window means the instrument did not date the step more finely. A completed crime that is not at a person's expense fails, including a minor who is named but did not supply the gain. Use of a person with no alleged defect fails. Benefit from a person's absence fails. `not_realized` and `withheld_partial` have no goal edge and no onset. A false test is not a finding of lawfulness.

`trajectories-expense-exemplar.ttl` holds the pass and fail cases, including use of a minor and the three rejects that keep the test from passing on the word "child." `trajectories-expense-invalid-exemplar.ttl` must fail: a non-person gain marked as a pass, a taking marked as not exploitation, use of a minor marked as not exploitation, and a minor who is not the source marked as a pass.

### enactsAction convention: arriving state, not leaving state

A Transition has two endpoints, and a domain extension's action catalog
will often contain one action that characterizes the `fromState` and a
different one that characterizes the `toState`. **The rule: `enactsAction`
names the action that *produces* the `toState`, so it is wired to the
transition *arriving at* the phase that action characterizes** — not the
transition leaving the phase the action is associated with. All ESM domain
extensions (`elder-fraud`, `extortion`, `trafficking`) follow this one
convention; do not mix leaving-state and arriving-state wiring within or
across domains.

Two corollaries fall out of applying this rule consistently, rather than
being ad-hoc exceptions:

- **A transition with no cataloged producing action simply omits
  `enactsAction`.** `sh:minCount` is not set, so this is conformant, not
  a gap to be papered over by attaching a loosely-related action from an
  adjacent phase.
- **If several co-occurring techniques produce the same `toState`**, wire
  **all** of them as `traj:enactsAction` on that arriving edge (multi-valued).
  See `elder-fraud`'s `InitialContact -> Conditioning` (`a_spoof` +
  `a_script` + `a_secrecy`) and `ProceedsCollection -> Laundering`
  (`a_fakeid` + `a_deposit`).
- **s₀ techniques that also gate the first transition** are wired on that
  first arriving edge (they produce the second state), not left unwired.
  Exogenous pre-s₀ feeders (e.g. victim-list purchase) stay outside S as
  `prov:Activity` / evidence, not as `traj:enactsAction` on a phantom
  incoming edge to s₀.

The affordance (φ) an offense abuses at a transition is **not** a bespoke
`traj:` property. It is carried on the standard **`action:instrument`**
property of the `traj:enactsAction` instance — e.g.
`:action-1 a uco-action:Action ; uco-action:instrument :the-abused-affordance .`
No `traj:affordance` mint; reuse the UCO action facet as-is.

Action **categories** (the "kind of action" a transition enacts, e.g. a
spoofing technique or a structuring technique) are minted the same way
MITRE ATT&CK techniques are in `extensions/attack-technique`: an
`owl:Class` that is also an instance of the `uco-action:Technique`
metaclass, `rdfs:subClassOf uco-action:Action`, carrying
`uco-action:techniqueID`. See
[`extensions/attack-technique/README.md`](../attack-technique/README.md)
for the punning pattern — domain extensions that need their own action
catalog (e.g. `extensions/elder-fraud`) reuse that pattern rather than
inventing a parallel one.

`traj:initialState` (domain `traj:StateMachineModel`, range `traj:State`,
`sh:maxCount 1`) marks the model's s₀ at the machine level — a model with
no single natural start state simply omits it.

### Firewall (observed vs inferred)

- `PhaseAssertion` **owl:disjointWith** `StateMachineModel` /
  `TransitionEstimate`.
- Every `PhaseAssertion`: ≥1 `prov:wasDerivedFrom`, confidence facet,
  state, interval, sequence index.
- Every model / estimate: ≥1 `prov:wasGeneratedBy`.
- Trajectories reference **PhaseAssertions only**; models
  `traj:learnedFrom` trajectories (never the reverse).

### Mapping CAC `PhaseTransitionEvent` → `traj:Transition`

| CAC temporal | `traj` |
|---|---|
| `PhaseTransitionEvent` | `traj:Transition` (more general; not limited to investigation lifecycle) |
| `transitionsFrom` / `transitionsTo` | `fromState` / `toState` |
| begin/end timestamps on the event | Prefer intervals on **PhaseAssertions**; put trigger-time on the trigger Action if needed |
| Fixed investigation phases | Plug-in `traj:State` vocab (SKOS), not hard subclassing |

Keep using CAC temporal classes for **investigation** lifecycle; use `traj`
for **offense / engagement / fraud** occupancy histories and analytic models.

## Plug-in vocabulary pattern

Domain phases are **instances**, not T-Box dependencies:

```turtle
:InitialContact a traj:State , skos:Concept ;
    skos:inScheme :CACGroomingPhaseScheme ;
    skos:exactMatch <https://cacontology.projectvic.org/grooming#InitialContactPhase> .
```

No dependence on unmerged CAC PRs (#33 AffordanceMisuse, #39 ConditioningPhase).

### AEO CyberKillChain plug-in (do not modify AEO)

Wrap kill-chain phase actions the same way:

```turtle
:Reconnaissance a traj:State , skos:Concept ;
    skos:inScheme :AEOCyberKillChainScheme ;
    skos:exactMatch <https://ontology.adversaryengagement.org/ae/attack/…> ;
    uco-core:description "Corresponds to a CyberKillChain phase Action." .
```

`aeo:CyberKillChain` / `Storyline` remain for **planned** adversary-engagement
narratives; `traj:Trajectory` records **observed** occupancy.

## Validation

**Primary (SDK):** `from case_uco.validation import validate_graph_file`
(public API since v1.22.1) with `extensions=['trajectories']`,
`profiles=['time','prov-o']`, `strict_concepts=True`. That bundle loads
upper shapes `sh-time.ttl` / `sh-prov-o.ttl`. Add `'gufo'` to `profiles`
to load `trajectories-profile-gufo.ttl` + `sh-gufo.ttl`.

**Secondary (CLI):** `case_validate` with traj OWL/shapes plus upper
*ontology* TTL (`time.ttl` / `prov-o.ttl`) does **not** load upper
*shapes* or run concept coverage — do not treat CLI-alone SHACL green
as SDK green. See `VALIDATION.md` for exact commands and results.

Invalid exemplar must fail (observed≠inferred firewall).

## Status

Local candidate extension (`"status": "candidate"`, version **0.5.0**).
`example.org` namespace matches rico/drugs/weapons placeholders pending a
community IRI. Language bindings (`packages/case-uco-trajectories`) are
deferred.
