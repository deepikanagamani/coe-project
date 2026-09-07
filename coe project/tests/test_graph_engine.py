"""
Unit tests for PrerequisiteGraphEngine:
- DAG cycle detection
- Shortest prerequisite path calculation
- Transitive closure resolution
- Student prerequisite eligibility
"""

import pytest
from app.engines.graph_engine import PrerequisiteGraphEngine

@pytest.fixture
def sample_curriculum():
    courses = [
        {"course_id": "CS101", "title": "Intro to CS", "department": "CS", "credits": 3},
        {"course_id": "CS201", "title": "Data Structures", "department": "CS", "credits": 4},
        {"course_id": "CS301", "title": "Operating Systems", "department": "CS", "credits": 4},
        {"course_id": "CS401", "title": "Distributed Systems", "department": "CS", "credits": 4},
        {"course_id": "MATH101", "title": "Calculus I", "department": "MATH", "credits": 4},
        {"course_id": "MATH205", "title": "Linear Algebra", "department": "MATH", "credits": 4}
    ]
    prereqs = [
        {"course_id": "CS201", "prerequisite_course_id": "CS101", "requirement_type": "hard"},
        {"course_id": "CS301", "prerequisite_course_id": "CS201", "requirement_type": "hard"},
        {"course_id": "CS401", "prerequisite_course_id": "CS301", "requirement_type": "hard"},
        {"course_id": "MATH205", "prerequisite_course_id": "MATH101", "requirement_type": "hard"},
        {"course_id": "CS401", "prerequisite_course_id": "MATH205", "requirement_type": "recommended"}
    ]
    return PrerequisiteGraphEngine(prerequisites=prereqs, courses=courses)

def test_transitive_closure(sample_curriculum):
    hard_closure = sample_curriculum.get_prerequisite_closure("CS401", hard_only=True)
    assert hard_closure == {"CS301", "CS201", "CS101"}

    all_closure = sample_curriculum.get_prerequisite_closure("CS401", hard_only=False)
    assert all_closure == {"CS301", "CS201", "CS101", "MATH205", "MATH101"}

def test_student_eligibility_unfulfilled(sample_curriculum):
    completed = ["CS101"]
    elig = sample_curriculum.evaluate_student_eligibility("CS301", completed)
    assert not elig["is_eligible"]
    assert elig["status"] in ["partially_satisfied", "locked"]
    assert len(elig["direct_missing_hard"]) == 1
    assert elig["direct_missing_hard"][0]["course_id"] == "CS201"

def test_student_eligibility_satisfied(sample_curriculum):
    completed = ["CS101", "CS201"]
    elig = sample_curriculum.evaluate_student_eligibility("CS301", completed)
    assert elig["is_eligible"]
    assert elig["status"] == "eligible"
    assert len(elig["direct_missing_hard"]) == 0

def test_shortest_prerequisite_path(sample_curriculum):
    completed = ["CS101"]
    stages = sample_curriculum.get_shortest_prerequisite_path("CS401", completed)
    # Target CS401 needs CS301 -> CS201 -> (CS101 completed)
    # Stage 1: CS201, Stage 2: CS301
    assert len(stages) == 2
    assert stages[0][0]["course_id"] == "CS201"
    assert stages[1][0]["course_id"] == "CS301"

def test_no_cycle_in_standard_curriculum(sample_curriculum):
    has_cycle, path = sample_curriculum.detect_cycles()
    assert not has_cycle
    assert len(path) == 0
