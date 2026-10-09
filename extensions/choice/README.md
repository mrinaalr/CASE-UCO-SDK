# Offense choice set (`choice`)

Status: **candidate** · version **0.1.0**

Records the documented options for a goal at a `traj:State`, walked or not. `trajectories` records the edge that was walked. `layered` composes those edges into a case-level machine. This extension records the stable goal, the options at a state, the actor's capability to use an option, a constraint that removes an option, and an inferred friction reading.

It does not define a reward. `selectionRule "not_modeled"` is the value to use when the graph must not claim that the actor optimized.

| Class | Role |
|---|---|
| `choice:Goal` | Stable end. Not `traj:goalRealizingTransition`. |
| `choice:Option` | A means at a `traj:State`, walked or not. Cites `prov:wasDerivedFrom`. |
| `choice:OffenderCapability` | What this actor can do. Local stand-in for [UCO #682](https://github.com/ucoProject/UCO/issues/682). |
| `choice:Constraint` | Wall, guardian, or access denial. Removes an option. |
| `choice:OptionAssessment` | Inferred friction and feasibility. Cites `prov:wasGeneratedBy`. |
| `choice:Selection` | Inferred pick from a menu of at least two options. |

Friction levels are `low`, `moderate`, `high`, or `not_in_source`. Feasibility is `feasible` or `removed`. A high-friction option can remain feasible. A disrupted trajectory stays `traj:terminalPolarity "disrupted"` and is not restated here as a constraint.

`depends_on` is `trajectories` and `layered`. CAC `PlatformAffordance` remains the platform feature. Point `choice:usesInstrument` at it when the case is a CAC case. Do not put perceived ease on that class.

## Exemplar

`choice-exemplar.ttl` — United States v. Castanos Garcia (D. Mass.). One goal, move directed cash to the runners. Two options the affidavit names: rideshare (Agawam, February 2023, completed) and UPS (Attleboro, September–October 2022, disrupted). The ESM is `parallel` and `partial`: two independent realizations, not a claim they overlapped, and not the rest of the elder-fraud alphabet.

Friction levels in that file are an analyst reading. The file has no `choice:Selection`. The two options are separate realizations, not a menu the record says was chosen from.

## Synthetic stress test

`choice-synthetic-travel.ttl` is not a case. One fictional traveler, one goal (San Francisco to New York), one departure state, one window, four options. It conforms. Nothing in the vocabulary was changed to make it conform. What it exposed:

- `choice:OffenderCapability` is the class for a traveler who is not an offender. `possessedBy` accepts any `uco-core:UcoObject`, so the graph conforms. The class name is narrower than the ontology's domain-general claim.
- A stagecoach that no longer operates is `constraintKind "wall"`, the nearest of `wall`, `guardian`, and `access_denial`. The `wall` comment is a barrier in the current environment. None of the three values is a mode that has left the environment.
- `ex:selection-plane` conforms with `selectionRule "not_modeled"` and with no chooser and no decision window. The window is only on the phase assertion. That hole is [issue 5](https://github.com/mrinaalr/CASE-UCO-SDK/issues/5).
- The selection's menu includes the removed stagecoach and the private jet the traveler cannot use. The shapes do not require an `amongOptions` member to be feasible or enabled.
- The jet gap is the absence of `enablesOption`. The graph does not state that the traveler lacks a jet capability. The same absence also matches the stagecoach, which is removed by a constraint, so a missing `enablesOption` does not by itself mean a capability gap.
- The Castanos competency queries run on this graph without being rewritten. Questions 1 and 3 return no rows because they name the Castanos goal. Question 2 returns the one walked option. Question 4 returns all four assessments.
- The only state is the departure decision, so the walked transition leaves and returns to that state. New York is not a state in the graph.

## Validate

```python
from case_uco.validation import validate_graph_file

validate_graph_file(
    "extensions/choice/choice-exemplar.ttl",
    extensions=["choice"],
    profiles=["time", "prov-o"],
    strict_concepts=True,
    force_rdfs_inference=True,
)
```

`choice-invalid-exemplar.ttl` must not conform.
