# Offense choice set

> See [Recipe Index](INDEX.md). Extension: [`extensions/choice/`](../../extensions/choice/).

Record the menu a walked `traj:Transition` was chosen from. Use this when one stable goal has more than one instrument, and the graph needs to say which one was walked without claiming the actor optimized.

## When to use

| Need | Class |
|---|---|
| Stable end, shared by several means | `choice:Goal` |
| A means at a state, walked or only available | `choice:Option` |
| What this actor can actually use | `choice:OffenderCapability` |
| A wall, guardian, or access denial | `choice:Constraint` |
| Analyst friction and feasibility | `choice:OptionAssessment` |
| Which option was treated as chosen | `choice:Selection` |

Leave the walked technique on `traj:enactsAction` and the affordance on `uco-action:instrument`. Point `choice:usesInstrument` at that same object. Put the goal on the case machine with `lay:hasFactor` when several layers realize it.

`selectionRule` is `not_modeled`, `satisficing`, `discrete_choice`, or `opportunistic`. Use `not_modeled` unless a rule is actually being claimed. Do not store a reward here. Do not store ease on `traj:guard` or on `traj:transitionProbability`.

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

Worked case: [`choice-exemplar.ttl`](../../extensions/choice/choice-exemplar.ttl).
