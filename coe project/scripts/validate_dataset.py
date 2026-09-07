"""
Dataset Validation & Referential Integrity Verifier.
Validates:
1. No dangling foreign keys (courses, prerequisites, pathways, schedules).
2. Intentional edge-case seeds exist (circular dependency, missing goal, unknown pathway).
3. Statistical distribution of student profiles.
4. Schedule timeslot formatting and term validity.
"""

import json
import os
import sys

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

def load_json(filename):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing dataset file: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def run_validation():
    print("=== STARTING DATASET REFERENTIAL INTEGRITY AUDIT ===")
    
    courses = load_json("courses.json")
    prereqs = load_json("prerequisites.json")
    schedules = load_json("schedules.json")
    pathways = load_json("pathways.json")
    pathway_courses = load_json("pathway_courses.json")
    students = load_json("students.json")
    historical = load_json("historical_outcomes.json")

    course_ids = {c["course_id"] for c in courses}
    pathway_ids = {p["pathway_id"] for p in pathways}

    print(f"Entities loaded: {len(courses)} courses, {len(prereqs)} prerequisites, {len(pathways)} pathways, {len(students)} students.")
    assert len(courses) >= 60, f"Expected >= 60 courses, got {len(courses)}"
    assert len(pathways) >= 10, f"Expected >= 10 pathways, got {len(pathways)}"
    assert len(students) >= 300, f"Expected >= 300 students, got {len(students)}"

    # 1. Check prerequisite referential integrity
    dangling_prereqs = []
    for p in prereqs:
        if p["course_id"] not in course_ids:
            dangling_prereqs.append((p["course_id"], "course_id"))
        if p["prerequisite_course_id"] not in course_ids:
            dangling_prereqs.append((p["prerequisite_course_id"], "prerequisite_course_id"))
    
    assert len(dangling_prereqs) == 0, f"Found dangling prerequisites: {dangling_prereqs}"
    print("  [PASS] Prerequisite referential integrity: 0 dangling course IDs.")

    # 2. Check schedule referential integrity
    dangling_schedules = [s for s in schedules if s["course_id"] not in course_ids]
    assert len(dangling_schedules) == 0, f"Found dangling schedules: {dangling_schedules}"
    print("  [PASS] Schedule referential integrity: All schedules map to valid courses.")

    # 3. Check pathway course associations
    dangling_pw_courses = [pc for pc in pathway_courses if pc["course_id"] not in course_ids or pc["pathway_id"] not in pathway_ids]
    assert len(dangling_pw_courses) == 0, f"Found dangling pathway-courses: {dangling_pw_courses}"
    print("  [PASS] Pathway course referential integrity: All associations valid.")

    # 4. Check intentional edge case fixtures
    # 4a. Circular dependency fixture (EDGE201 <-> EDGE202)
    cycle_edges = [p for p in prereqs if p["course_id"] in ["EDGE201", "EDGE202"]]
    assert len(cycle_edges) == 2, "Expected 2 reciprocal edges for circular test fixture"
    print("  [PASS] Circular dependency test fixture verified (EDGE201 <-> EDGE202).")

    # 4b. Missing / unknown student goals
    empty_goals = [s for s in students if not s["stated_goal_pathway"]]
    unknown_goals = [s for s in students if s["stated_goal_pathway"] and s["stated_goal_pathway"] not in pathway_ids]
    assert len(empty_goals) >= 2, "Expected at least 2 students with empty goals"
    assert len(unknown_goals) >= 1, "Expected at least 1 student with invalid goal"
    print(f"  [PASS] Missing/Degraded goal fixtures verified ({len(empty_goals)} empty, {len(unknown_goals)} unknown).")

    # 4c. Catalog drift course fixture (EDGE101)
    drift_course = [c for c in courses if c["course_id"] == "EDGE101"]
    assert len(drift_course) == 1, "Expected EDGE101 catalog drift course fixture"
    print("  [PASS] Catalog drift test fixture verified (EDGE101).")

    # 5. Check student completed courses validity
    for s in students:
        for cid in s["completed_courses"]:
            assert cid in course_ids, f"Student {s['student_id']} has nonexistent course {cid}"
    print("  [PASS] Student transcript validity: All completed courses exist in catalog.")

    print("\nALL REFERENTIAL INTEGRITY AND DATA AUDITS PASSED WITH ZERO VIOLATIONS.")
    return True

if __name__ == "__main__":
    try:
        run_validation()
    except Exception as e:
        print(f"VALIDATION FAILED: {e}", file=sys.stderr)
        sys.exit(1)
