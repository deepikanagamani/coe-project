"""
Unit tests for ConflictEngine:
- Schedule timeslot collision detection
- Multi-term progression validation
- Credit overload enforcement
"""

import pytest
from app.engines.conflict_engine import ConflictEngine
from app.engines.graph_engine import PrerequisiteGraphEngine

@pytest.fixture
def conflict_setup():
    courses = [
        {"course_id": "CS101", "credits": 3},
        {"course_id": "CS201", "credits": 4},
        {"course_id": "CS301", "credits": 4}
    ]
    prereqs = [
        {"course_id": "CS201", "prerequisite_course_id": "CS101", "requirement_type": "hard"},
        {"course_id": "CS301", "prerequisite_course_id": "CS201", "requirement_type": "hard"}
    ]
    schedules = [
        {"course_id": "CS101", "term": "Fall", "day_time_slot": "Mon/Wed 08:30-10:00", "room": "Hall-A", "capacity": 100},
        {"course_id": "CS201", "term": "Fall", "day_time_slot": "Mon/Wed 08:30-10:00", "room": "Hall-B", "capacity": 100},
        {"course_id": "CS301", "term": "Fall", "day_time_slot": "Tue/Thu 13:30-15:00", "room": "Lab-101", "capacity": 45}
    ]
    graph_engine = PrerequisiteGraphEngine(prerequisites=prereqs, courses=courses)
    conflict_engine = ConflictEngine(schedules=schedules, graph_engine=graph_engine)
    return conflict_engine

def test_timeslot_collision_detected(conflict_setup):
    # CS101 and CS201 share Mon/Wed 08:30-10:00
    conflicts = conflict_setup.detect_schedule_conflicts(
        courses=[{"course_id": "CS101"}, {"course_id": "CS201"}],
        term="Fall"
    )
    assert len(conflicts) == 1
    assert conflicts[0]["conflict_type"] == "timeslot_collision"
    assert conflicts[0]["timeslot"] == "Mon/Wed 08:30-10:00"

def test_no_timeslot_collision_different_slots(conflict_setup):
    conflicts = conflict_setup.detect_schedule_conflicts(
        courses=[{"course_id": "CS101"}, {"course_id": "CS301"}],
        term="Fall"
    )
    assert len(conflicts) == 0

def test_plan_validation_progression_violation(conflict_setup):
    # Student attempts to take CS301 in Fall without CS201
    plan = [
        {"term": "Fall 2026", "courses": [{"course_id": "CS301", "credits": 4}]}
    ]
    res = conflict_setup.validate_plan(
        planned_terms=plan,
        completed_courses=["CS101"],
        max_courses_per_term=3
    )
    assert not res["is_valid"]
    assert any(c["conflict_type"] == "prerequisite_violation" for c in res["conflicts"])

def test_plan_validation_overload(conflict_setup):
    plan = [
        {"term": "Fall 2026", "courses": [
            {"course_id": "CS101", "credits": 3},
            {"course_id": "CS201", "credits": 4},
            {"course_id": "CS301", "credits": 4}
        ]}
    ]
    res = conflict_setup.validate_plan(
        planned_terms=plan,
        completed_courses=["CS101", "CS201"],
        max_courses_per_term=2  # Max pace is 2, but planned 3
    )
    assert not res["is_valid"]
    assert any(c["conflict_type"] == "overload" for c in res["conflicts"])
