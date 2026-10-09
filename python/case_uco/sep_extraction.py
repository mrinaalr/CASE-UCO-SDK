"""SEP source-versus-target derivation.

``benefit_source`` is this function. A hand-written label that disagrees
with the anatomy is a bug. Unfairness is not an input.

The rule is the one stated in mrinaalr/ThanosStateMachine issue 2 and
implemented in that repo's ``derive_benefit_source``: extraction is a
preexisting object that changes hands and keeps its value without the
victim. Destruction is a benefit that consists in the victim's absence.
"""

from __future__ import annotations


def benefit_source(
    transferred_object: str | None,
    preexisting: bool,
    value_survives_victim: bool,
) -> str:
    """Return victim_sourced, victim_targeted, or none."""
    if transferred_object is None:
        if value_survives_victim:
            return "none"
        return "victim_targeted"
    if preexisting and value_survives_victim:
        return "victim_sourced"
    return "victim_targeted"


def passes_extraction_test(status: str) -> bool:
    """True only when a goal-realizing edge was victim-sourced."""
    return status == "realized_sourced"
