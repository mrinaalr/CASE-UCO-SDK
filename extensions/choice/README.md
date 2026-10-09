# Offense choice set (`choice`)

Status: **candidate** · version **0.1.0**

The menu a `traj:Transition` was chosen from. `trajectories` records the edge that was walked. `layered` composes those edges into a case-level machine. This extension records the stable goal, the options at a state, the actor's capability to use an option, a constraint that removes an option, and an inferred friction reading.

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
