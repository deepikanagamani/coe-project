"""
Unit tests for CareerConsequenceEngine:
- Pathway alignment evaluation
- Plain-language rationale generation
- Consequence previews
- 'Why NOT' explainer
"""

import pytest
from app.engines.career_engine import CareerConsequenceEngine
from app.engines.graph_engine import PrerequisiteGraphEngine
from app.engines.conflict_engine import ConflictEngine

@pytest.fixture
def career_setup():
    pathways = [
        {"pathway_id": "PW_ML", "name": "Machine Learning", "description": "ML track", "primary_departments": ["CS"], "target_competencies": ["Deep Learning"]}
    ]
    pathway_courses = [
        {"pathway_id": "PW_ML", "course_id": "CS305", "weight": 1.0, "rationale": "Classical machine learning fundamentals."},
        {"pathway_id": "PW_ML", "course_id": "CS405", "weight": 1.0, "rationale": "Deep neural networks and optimization."}
    ]
    courses = [
        {"course_id": "CS101", "credits": 3},
        {"course_id": "CS201", "credits": 4},
        {"course_id": "CS305", "credits": 4},
        {"course_id": "CS405", "credits": 4},
        {"course_id": "HIST101", "credits": 3}
    ]
    prereqs = [
        {"course_id": "CS201", "prerequisite_course_id": "CS101", "requirement_type": "hard"},
        {"course_id": "CS305", "prerequisite_course_id": "CS201", "requirement_type": "hard"},
        {"course_id": "CS405", "prerequisite_course_id": "CS305", "requirement_type": "hard"}
    ]
    schedules = [
        {"course_id": "CS305", "term": "Fall", "day_time_slot": "Mon/Wed 08:30-10:00", "room": "Hall-A", "capacity": 100},
        {"course_id": "HIST101", "term": "Fall", "day_time_slot": "Mon/Wed 08:30-10:00", "room": "Hall-B", "capacity": 100}
    ]
    ge = PrerequisiteGraphEngine(prerequisites=prereqs, courses=courses)
    ce = ConflictEngine(schedules=schedules, graph_engine=ge)
    career_engine = CareerConsequenceEngine(pathways=pathways, pathway_courses=pathway_courses, graph_engine=ge, conflict_engine=ce)
    return career_engine

def test_course_alignment_advancing(career_setup):
    res = career_setup.evaluate_course_alignment("CS305", "PW_ML")
    assert res["status"] == "advancing"
    assert res["score"] == 1.0
    assert "Machine Learning" in res["rationale"]

def test_course_alignment_neutral(career_setup):
    res = career_setup.evaluate_course_alignment("HIST101", "PW_ML")
    assert res["status"] == "neutral"
    assert res["score"] <= 0.3
    assert "Neutral" in res["rationale"]

def test_why_not_missing_prerequisites(career_setup):
    res = career_setup.explain_why_not(
        course_id="CS405",
        completed_courses=["CS101"], # Missing CS201 and CS305
        current_planned_courses=[],
        term="Fall",
        pathway_id="PW_ML"
    )
    assert res["is_blocked"]
    assert any("prerequisite" in r.lower() for r in res["reasons"])

def test_consequence_preview_timeslot_clash(career_setup):
    preview = career_setup.preview_consequence(
        candidate_course_id="HIST101",
        current_planned_courses=[{"course_id": "CS305"}],
        completed_courses=["CS101", "CS201"],
        term="Fall",
        pathway_id="PW_ML"
    )
    assert preview["has_schedule_conflict"]
    assert not preview["can_proceed_safely"]
    assert "Schedule clash" in preview["plain_language_narrative"]
