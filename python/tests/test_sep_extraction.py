"""The fraud close reads must carry a derived SEP extraction test."""

from __future__ import annotations

from pathlib import Path

import pytest
from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import RDF

from case_uco.sep_extraction import benefit_source, passes_extraction_test

TRAJ = Namespace("http://example.org/ontology/trajectories/")
ROOT = Path(__file__).resolve().parents[2]
FRAUD = [
    "alcedo-english-course.ttl",
    "augustine-inheritance.ttl",
    "cofer-insider-account.ttl",
    "adepoju-phishing-w2.ttl",
    "odus-bec-laundering.ttl",
    "obaseki-multi-scheme.ttl",
    "hunt-ppp-portal.ttl",
    "matson-romance-recruiter.ttl",
]


def test_derivation_matches_the_boundary_cases():
    # Mind Stone: the taking kills Vision, and the stone still works if he had lived.
    assert benefit_source("Mind Stone", True, True) == "victim_sourced"
    # Snap: nothing passes, and the benefit is the victims' absence.
    assert benefit_source(None, False, False) == "victim_targeted"
    # No victim-linked benefit.
    assert benefit_source(None, True, True) == "none"
    # An object whose value does not survive the victim is not extraction.
    assert benefit_source("a life priced as the benefit", True, False) == "victim_targeted"


def test_pass_bit_follows_status():
    assert passes_extraction_test("realized_sourced") is True
    assert passes_extraction_test("realized_other") is False
    assert passes_extraction_test("not_realized") is False
    assert passes_extraction_test("withheld_partial") is False


def _literal_bool(graph: Graph, subject: URIRef, predicate: URIRef) -> bool:
    value = graph.value(subject, predicate)
    assert value is not None, f"{predicate} missing on {subject}"
    return bool(value)


@pytest.mark.parametrize("name", FRAUD)
def test_fraud_graph_derives_its_own_labels(name: str):
    graph = Graph()
    graph.parse(ROOT / "workbench" / "machines" / "v0.0.0" / name)
    anatomies = list(graph.subjects(RDF.type, TRAJ.BenefitAnatomy))
    assert anatomies, name
    for anatomy in anatomies:
        raw = graph.value(anatomy, TRAJ.transferredObject)
        transferred = None if raw is None else str(raw)
        derived = benefit_source(
            transferred,
            _literal_bool(graph, anatomy, TRAJ.preexisting),
            _literal_bool(graph, anatomy, TRAJ.valueSurvivesVictim),
        )
        assert str(graph.value(anatomy, TRAJ.benefitSource)) == derived

    assessments = list(graph.subjects(RDF.type, TRAJ.ExploitationAssessment))
    assert assessments, name
    for assessment in assessments:
        status = str(graph.value(assessment, TRAJ.extractionTestStatus))
        passed = _literal_bool(graph, assessment, TRAJ.passesExtractionTest)
        assert passed is passes_extraction_test(status)
        goal = graph.value(assessment, TRAJ.goalRealizingTransition)
        if status in {"realized_sourced", "realized_other"}:
            assert isinstance(goal, URIRef)
        else:
            assert goal is None
        if status == "realized_sourced":
            sources = {
                str(graph.value(anatomy, TRAJ.benefitSource))
                for anatomy in graph.objects(assessment, TRAJ.hasBenefitAnatomy)
                if graph.value(anatomy, TRAJ.onTransition) == goal
            }
            assert "victim_sourced" in sources
