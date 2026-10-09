# Sex-Trafficking Exploitation State Machine Extension (`trafficking`)

Narrow, machine-only extension: contributes **only** what the
[trajectories](../trajectories/) Exploitation State Machine (ESM) needs to
run on an individual-operator, online-advertisement-based adult
sex-trafficking offense — a victim-journey phase vocabulary and a small
action catalog. No class hierarchy beyond the `uco-action:Technique`
metaclass pattern from [attack-technique](../attack-technique/).

**No CAC crosswalk.** All classes are minted fresh. This extension does
not `skos:exactMatch` any CAC (`cacontology.projectvic.org`) trafficking
class: the vendored CAC ontology (`ontology/cac`) is grooming/CSAM-focused
(child victims), while the source case is an adult-victim,
individual-operator prosecution with no child-exploitation allegation —
no CAC class is a defensible exact match. Flagged for sign-off; revisit
only if a genuine CAC exact-match candidate is identified later.

## Case

**United States v. Chase Anthony Young** (N.D. Tex.). Source: USAO-NDTX
press release "Dallas Man Sentenced to 30 Years in Federal Prison for Sex
Trafficking" (2026-06-15) — the only source document available (no plea
agreement or affidavit text); the exemplar is calibrated to exactly what
that press release states, with no invented phases, actions, amounts, or
affordances. Recruitment method for the three victims of the admitted
conduct is not described in the source, so the `Recruitment` phase
assertion is scoped strictly to the one sourced organizational-duration
fact and carries a correspondingly lower confidence value (55, vs. 88-90
for the other three phases).

## Phases (`traf:PhaseScheme`)

| State | What it is |
|---|---|
| `traf:Recruitment` | Onset of the trafficking organization (method not specified in source) |
| `traf:Control` | Victims compelled by force, threats, fraud, or coercion; pricing/rules set |
| `traf:Exploitation` | Online ads placed; hotel rooms rented for commercial sex acts |
| `traf:EarningsCollection` | Offender takes all proceeds from the commercial sex acts |

## Actions (`uco-action:Technique` classes)

| Class | techniqueID | What it is |
|---|---|---|
| `traf:a_coerce` | `TRAF.T1` | Force / fraud / coercion |
| `traf:a_advertise` | `TRAF.T2` | Online-ad placement (online-ad affordance) |
| `traf:a_collect_earnings` | `TRAF.T3` | Proceeds collection |

## Exemplar

`trafficking-exemplar.ttl` carries one real `traj:Trajectory`
(`trfx:trajectory-three-victims`), terminal `traj:terminalPolarity
"completed"` — the modeled victim-journey chain finished at earnings
collection in the source. Later prosecution/sentencing is outside the
machine and does not count as mid-chain `disrupted`.

### `traj:enactsAction` wiring

Follows the arriving-state convention documented in
[`trajectories/README.md`](../trajectories/README.md#enactsaction-convention-arriving-state-not-leaving-state):
each transition's `enactsAction` is the action that *produces* its
`toState`.

| Transition | `enactsAction` | Produces |
|---|---|---|
| `Recruitment -> Control` | `traf:a_coerce` | `Control` |
| `Control -> Exploitation` | `traf:a_advertise` | `Exploitation` |
| `Exploitation -> EarningsCollection` | `traf:a_collect_earnings` | `EarningsCollection` |

`traf:Recruitment` has no cataloged producing technique (the source is
silent on recruitment method for the three admitted victims), so — like
other domains' s₀ actions — there is no `enactsAction` on an incoming
edge because there is no incoming edge to attach one to.

## Validation

```python
from case_uco.validation import validate_graph_file

validate_graph_file(
    "extensions/trafficking/trafficking-exemplar.ttl",
    extensions=["trafficking"],
    profiles=["time", "prov-o"],
    strict_concepts=True,
    force_rdfs_inference=True,
)
```
