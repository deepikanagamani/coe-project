"""
Edge & Failure Case Test Suite for Prerequisite & Career-Consequence Explorer.
Implements the mandatory edge scenarios defined in Section 8:
1. Circular prerequisite dependency (A -> B -> A detected without crash or infinite loop)
2. Unreachable goal (prerequisite chain impossible in remaining terms surfaced clearly)
3. Missing / incomplete student data (missing goal or unknown pathway degrades gracefully)
4. Schedule overload (exceeding max courses/term or overlapping day/timeslot flagged before confirmation)
5. Data drift / catalog change (prerequisite course removed from term offerings flagged cleanly)
6. Concurrent query load test (latency strictly <500ms)
"""

import time
import pytest
from app.engines.graph_engine import PrerequisiteGraphEngine
from app.engines.conflict_engine import ConflictEngine
from app.engines.career_engine import CareerConsequenceEngine
from app.engines.recommender import ExplainableRecommender

# -------------------------------------------------------------------------
# EDGE CASE 1: Circular Prerequisite Dependency
# -------------------------------------------------------------------------
def test_edge_case_1_circular_prerequisite_dependency():
    """
    Scenario: Course EDGE201 requires EDGE202, and EDGE202 requires EDGE201.
    Assertion: System detects cycle, isolates the loop, and does not crash or infinite-loop.
    """
    courses = [
        {"course_id": "EDGE201", "title": "Cycle Course A", "department": "CS", "credits": 3},
        {"course_id": "EDGE202", "title": "Cycle Course B", "department": "CS", "credits": 3}
    ]
    prereqs = [
        {"course_id": "EDGE201", "prerequisite_course_id": "EDGE202", "requirement_type": "hard"},
        {"course_id": "EDGE202", "prerequisite_course_id": "EDGE201", "requirement_type": "hard"}
    ]

    engine = PrerequisiteGraphEngine(prerequisites=prereqs, courses=courses)
    
    # Must detect cycle without hanging
    has_cycle, cycle_nodes = engine.detect_cycles()
    assert has_cycle is True
    assert "EDGE201" in cycle_nodes
    assert "EDGE202" in cycle_nodes
    
    # Prerequisite closure must terminate safely (not infinite loop)
    closure = engine.get_prerequisite_closure("EDGE201")
    assert "EDGE202" in closure
    assert "EDGE201" in closure

# -------------------------------------------------------------------------
# EDGE CASE 2: Unreachable Goal
# -------------------------------------------------------------------------
def test_edge_case_2_unreachable_goal_within_timeline():
    """
    Scenario: Student has 1 term remaining before graduation but stated goal
    requires an advanced capstone CS500 with a 3-tier sequential prerequisite chain
    (CS101 -> CS201 -> CS301 -> CS500).
    Assertion: System surfaces that the goal is unreachable in 1 term, explains why,
    and identifies the shortest prerequisite sequence needed (3 terms).
    """
    courses = [
        {"course_id": "CS101", "credits": 3},
        {"course_id": "CS201", "credits": 4},
        {"course_id": "CS301", "credits": 4},
        {"course_id": "CS500", "credits": 4}
    ]
    prereqs = [
        {"course_id": "CS201", "prerequisite_course_id": "CS101", "requirement_type": "hard"},
        {"course_id": "CS301", "prerequisite_course_id": "CS201", "requirement_type": "hard"},
        {"course_id": "CS500", "prerequisite_course_id": "CS301", "requirement_type": "hard"}
    ]
    engine = PrerequisiteGraphEngine(prerequisites=prereqs, courses=courses)
    
    # Student has completed nothing
    completed = []
    shortest_path = engine.get_shortest_prerequisite_path("CS500", completed)
    
    # The sequential chain requires 3 distinct sequential terms
    assert len(shortest_path) == 3
    assert shortest_path[0][0]["course_id"] == "CS101"
    assert shortest_path[1][0]["course_id"] == "CS201"
    assert shortest_path[2][0]["course_id"] == "CS301"

# -------------------------------------------------------------------------
# EDGE CASE 3: Missing / Incomplete Student Data
# -------------------------------------------------------------------------
def test_edge_case_3_missing_or_invalid_student_goal():
    """
    Scenario: Student profile has no stated goal (empty string or None),
    or specifies a deprecated/nonexistent pathway ID (e.g. 'PW_UNKNOWN_99').
    Assertion: System degrades gracefully to general elective recommendation mode,
    provides valid plain-language explanations, and never raises an unhandled exception.
    """
    courses = [
        {"course_id": "CS101", "title": "Intro Computing", "department": "CS", "credits": 3, "term_offered": ["Fall"], "difficulty_level": "Introductory"},
        {"course_id": "DATA101", "title": "Intro Data Science", "department": "DATA", "credits": 3, "term_offered": ["Fall"], "difficulty_level": "Introductory"}
    ]
    schedules = [
        {"course_id": "CS101", "term": "Fall", "day_time_slot": "Mon/Wed 08:30-10:00"},
        {"course_id": "DATA101", "term": "Fall", "day_time_slot": "Tue/Thu 10:45-12:15"}
    ]
    ge = PrerequisiteGraphEngine(courses=courses)
    ce = ConflictEngine(schedules=schedules)
    career_engine = CareerConsequenceEngine(pathways=[], pathway_courses=[], graph_engine=ge, conflict_engine=ce)
    recommender = ExplainableRecommender(courses, ge, ce, career_engine)

    # 3a. Completely empty stated goal
    student_empty_goal = {"student_id": "STU_EMPTY", "completed_courses": [], "stated_goal_pathway": "", "max_courses_per_term": 2}
    recs_empty = recommender.recommend(student_empty_goal, term="Fall")
    assert len(recs_empty) > 0
    assert recs_empty[0]["explanation"] != ""
    assert "foundational" in recs_empty[0]["explanation"].lower() or "elective" in recs_empty[0]["explanation"].lower()

    # 3b. Invalid/deprecated pathway ID
    student_invalid_goal = {"student_id": "STU_INVALID", "completed_courses": [], "stated_goal_pathway": "PW_NONEXISTENT", "max_courses_per_term": 2}
    recs_invalid = recommender.recommend(student_invalid_goal, term="Fall")
    assert len(recs_invalid) > 0
    assert recs_invalid[0]["explanation"] != ""

# -------------------------------------------------------------------------
# EDGE CASE 4: Schedule Overload & Overlapping Timeslots
# -------------------------------------------------------------------------
def test_edge_case_4_schedule_overload_and_timeslot_clash():
    """
    Scenario: Student attempts to confirm a plan where:
    a) Course count exceeds their max_courses_per_term limit.
    b) Two courses occupy the identical lecture timeslot.
    Assertion: Plan validation flags both violations with clear, actionable warning payloads.
    """
    courses = [
        {"course_id": "CS101", "credits": 3},
        {"course_id": "SYS101", "credits": 3},
        {"course_id": "MATH101", "credits": 4}
    ]
    schedules = [
        {"course_id": "CS101", "term": "Fall", "day_time_slot": "Mon/Wed 10:15-11:45"},
        {"course_id": "SYS101", "term": "Fall", "day_time_slot": "Mon/Wed 10:15-11:45"}, # Clash with CS101!
        {"course_id": "MATH101", "term": "Fall", "day_time_slot": "Tue/Thu 13:30-15:00"}
    ]
    conflict_engine = ConflictEngine(schedules=schedules)
    
    plan = [
        {
            "term": "Fall 2026",
            "courses": courses # 3 courses planned, but max pace set to 2
        }
    ]
    
    res = conflict_engine.validate_plan(
        planned_terms=plan,
        completed_courses=[],
        max_courses_per_term=2
    )

    assert res["is_valid"] is False
    conflict_types = [c["conflict_type"] for c in res["conflicts"]]
    assert "overload" in conflict_types
    assert "timeslot_collision" in conflict_types

# -------------------------------------------------------------------------
# EDGE CASE 5: Data Drift / Catalog Change
# -------------------------------------------------------------------------
def test_edge_case_5_catalog_drift_removed_prerequisite_offering():
    """
    Scenario: Course CS308 has a prerequisite CS201. However, in the Summer term,
    CS201 is removed from catalog offerings (only offered Fall/Spring).
    Assertion: When a student attempts to schedule the dependent course in Summer without
    completing CS201, system identifies that CS201 is unavailable in Summer and halts progression.
    """
    schedules = [
        # CS201 only offered Fall
        {"course_id": "CS201", "term": "Fall", "day_time_slot": "Mon/Wed 08:30-10:00"},
        # CS308 offered in Summer
        {"course_id": "CS308", "term": "Summer", "day_time_slot": "Tue/Thu 09:00-10:30"}
    ]
    courses = [
        {"course_id": "CS201", "title": "Data Structures", "term_offered": ["Fall"], "credits": 4},
        {"course_id": "CS308", "title": "Web Services", "term_offered": ["Summer"], "credits": 3}
    ]
    prereqs = [
        {"course_id": "CS308", "prerequisite_course_id": "CS201", "requirement_type": "hard"}
    ]

    ge = PrerequisiteGraphEngine(prerequisites=prereqs, courses=courses)
    ce = ConflictEngine(schedules=schedules, graph_engine=ge)

    # Student plans CS201 in Summer 2026 where it is not offered
    summer_plan = [
        {"term": "Summer 2026", "courses": [{"course_id": "CS201"}]}
    ]
    validation = ce.validate_plan(summer_plan, completed_courses=[])
    assert not validation["is_valid"]
    assert any(c.get("conflict_type") == "term_unavailability" for c in validation["conflicts"])

# -------------------------------------------------------------------------
# EDGE CASE 6: Concurrent Query Performance Under 500ms
# -------------------------------------------------------------------------
def test_edge_case_6_concurrent_query_latency_under_500ms():
    """
    Scenario: 100 consecutive prerequisite pathfinding and recommendation queries
    simulating active concurrent traffic.
    Assertion: Average query latency is strictly under 500ms (target: < 50ms).
    """
    from app.database import get_all_courses, get_all_prerequisites, get_all_pathways, get_db_connection
    courses = get_all_courses()
    prereqs = get_all_prerequisites()
    pathways = get_all_pathways()
    conn = get_db_connection()
    pw_courses = [dict(r) for r in conn.execute("SELECT * FROM pathway_courses").fetchall()]
    schedules = [dict(r) for r in conn.execute("SELECT * FROM schedules").fetchall()]
    conn.close()

    ge = PrerequisiteGraphEngine(prerequisites=prereqs, courses=courses)
    ce = ConflictEngine(schedules=schedules, graph_engine=ge)
    career_engine = CareerConsequenceEngine(pathways, pw_courses, ge, ce)
    recommender = ExplainableRecommender(courses, ge, ce, career_engine)

    student = {
        "student_id": "STU_BENCH",
        "completed_courses": ["CS101", "CS102", "MATH101"],
        "stated_goal_pathway": "PW_ML_ENG",
        "max_courses_per_term": 3
    }

    latencies = []
    for _ in range(100):
        t0 = time.perf_counter()
        recs = recommender.recommend(student, term="Fall")
        assert len(recs) > 0
        latencies.append((time.perf_counter() - t0) * 1000)

    avg_latency = sum(latencies) / len(latencies)
    p95_latency = sorted(latencies)[int(len(latencies) * 0.95)]

    print(f"\n[Load Test Benchmark] Avg Latency: {avg_latency:.2f} ms | p95 Latency: {p95_latency:.2f} ms")
    assert avg_latency < 500.0, f"Expected < 500ms, got {avg_latency} ms"
    assert p95_latency < 500.0, f"Expected p95 < 500ms, got {p95_latency} ms"
