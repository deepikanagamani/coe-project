"""
Measurable Experiment & Evaluation Runner.
Executes both Baseline and Prototype Recommenders against the 320 synthetic students.
Measures:
1. % of student plans with >= 1 unresolved prerequisite conflict
2. % of recommended electives aligned with stated career goal
3. Average number of prerequisite conflicts per student plan
4. Recommendation response latency (p50, p95, p99 in ms)
5. % of recommendations with a valid, non-empty explanation
Saves results to data/evaluation_results.json.
"""

import json
import os
import sys
import time
from typing import List, Dict, Any

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from baseline.naive_recommender import NaiveBaselineRecommender
from app.database import (
    get_all_courses,
    get_all_prerequisites,
    get_all_pathways,
    get_all_students,
    get_db_connection
)
from app.engines.graph_engine import PrerequisiteGraphEngine
from app.engines.conflict_engine import ConflictEngine
from app.engines.career_engine import CareerConsequenceEngine
from app.engines.recommender import ExplainableRecommender

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

def evaluate():
    print("=== EXECUTING COMPARATIVE EVALUATION EXPERIMENT ===")
    
    # Load test environment
    courses = get_all_courses()
    prereqs = get_all_prerequisites()
    pathways = get_all_pathways()
    students = get_all_students()
    
    conn = get_db_connection()
    pw_courses = [dict(r) for r in conn.execute("SELECT * FROM pathway_courses").fetchall()]
    schedules = [dict(r) for r in conn.execute("SELECT * FROM schedules").fetchall()]
    conn.close()

    # Initialize Baseline and Prototype
    baseline_engine = NaiveBaselineRecommender(DATA_DIR)
    
    graph_engine = PrerequisiteGraphEngine(prereqs, courses)
    conflict_engine = ConflictEngine(schedules, graph_engine)
    career_engine = CareerConsequenceEngine(pathways, pw_courses, graph_engine, conflict_engine)
    prototype_engine = ExplainableRecommender(courses, graph_engine, conflict_engine, career_engine)

    # Pathway course lookup set for alignment scoring: (pathway_id, course_id)
    pathway_supported = {(pc["pathway_id"], pc["course_id"]) for pc in pw_courses}

    # -------------------------------------------------------------------------
    # 1. EVALUATE BASELINE
    # -------------------------------------------------------------------------
    print(f"Running Baseline across {len(students)} students...")
    b_plans_with_conflicts = 0
    b_total_conflicts = 0
    b_total_recs = 0
    b_aligned_recs = 0
    b_explained_recs = 0
    b_latencies = []
    
    b_failure_breakdown = {
        "prerequisite_violations": 0,
        "schedule_collisions": 0,
        "unaligned_goal": 0,
        "missing_goal": 0
    }

    for s in students:
        completed = s["completed_courses"]
        goal = s["stated_goal_pathway"]
        
        t0 = time.perf_counter()
        recs = baseline_engine.recommend(s, term="Fall")
        b_latencies.append((time.perf_counter() - t0) * 1000)

        plan_has_conflict = False
        plan_conflicts_count = 0

        # Check schedule timeslot collisions within recommended batch
        simulated_plan = [{"course_id": r["course_id"]} for r in recs]
        schedule_conflicts = conflict_engine.detect_schedule_conflicts(simulated_plan, "Fall")
        if schedule_conflicts:
            plan_has_conflict = True
            plan_conflicts_count += len(schedule_conflicts)
            b_failure_breakdown["schedule_collisions"] += len(schedule_conflicts)

        for r in recs:
            b_total_recs += 1
            cid = r["course_id"]
            
            # Prerequisite check
            elig = graph_engine.evaluate_student_eligibility(cid, completed)
            if not elig["is_eligible"]:
                plan_has_conflict = True
                plan_conflicts_count += len(elig["direct_missing_hard"])
                b_failure_breakdown["prerequisite_violations"] += len(elig["direct_missing_hard"])

            # Career alignment check
            if not goal:
                b_failure_breakdown["missing_goal"] += 1
            elif (goal, cid) in pathway_supported:
                b_aligned_recs += 1
            else:
                b_failure_breakdown["unaligned_goal"] += 1

            # Explainability check
            if r.get("explanation") and len(r["explanation"].strip()) > 5:
                b_explained_recs += 1

        if plan_has_conflict:
            b_plans_with_conflicts += 1
        b_total_conflicts += plan_conflicts_count

    # -------------------------------------------------------------------------
    # 2. EVALUATE PROTOTYPE
    # -------------------------------------------------------------------------
    print(f"Running Prototype across {len(students)} students...")
    p_plans_with_conflicts = 0
    p_total_conflicts = 0
    p_total_recs = 0
    p_aligned_recs = 0
    p_explained_recs = 0
    p_latencies = []
    
    p_failure_breakdown = {
        "prerequisite_violations": 0,
        "schedule_collisions": 0,
        "unaligned_goal": 0,
        "missing_goal": 0
    }

    for s in students:
        completed = s["completed_courses"]
        goal = s["stated_goal_pathway"]
        
        t0 = time.perf_counter()
        recs = prototype_engine.recommend(s, term="Fall")
        p_latencies.append((time.perf_counter() - t0) * 1000)

        plan_has_conflict = False
        plan_conflicts_count = 0

        # Check schedule timeslot collisions within recommended batch
        simulated_plan = [{"course_id": r["course_id"]} for r in recs]
        schedule_conflicts = conflict_engine.detect_schedule_conflicts(simulated_plan, "Fall")
        if schedule_conflicts:
            plan_has_conflict = True
            plan_conflicts_count += len(schedule_conflicts)
            p_failure_breakdown["schedule_collisions"] += len(schedule_conflicts)

        for r in recs:
            p_total_recs += 1
            cid = r["course_id"]
            
            # Prerequisite check
            elig = graph_engine.evaluate_student_eligibility(cid, completed)
            if not elig["is_eligible"]:
                plan_has_conflict = True
                plan_conflicts_count += len(elig["direct_missing_hard"])
                p_failure_breakdown["prerequisite_violations"] += len(elig["direct_missing_hard"])

            # Career alignment check
            if not goal:
                p_failure_breakdown["missing_goal"] += 1
            elif (goal, cid) in pathway_supported:
                p_aligned_recs += 1
            else:
                p_failure_breakdown["unaligned_goal"] += 1

            # Explainability check
            if r.get("explanation") and len(r["explanation"].strip()) > 5:
                p_explained_recs += 1

        if plan_has_conflict:
            p_plans_with_conflicts += 1
        p_total_conflicts += plan_conflicts_count

    # -------------------------------------------------------------------------
    # 3. METRIC CALCULATIONS
    # -------------------------------------------------------------------------
    n_students = len(students)
    
    b_pct_conflict_plans = (b_plans_with_conflicts / n_students) * 100.0
    p_pct_conflict_plans = (p_plans_with_conflicts / n_students) * 100.0
    conflict_reduction_pct = ((b_pct_conflict_plans - p_pct_conflict_plans) / b_pct_conflict_plans) * 100.0

    b_pct_aligned = (b_aligned_recs / b_total_recs) * 100.0 if b_total_recs else 0.0
    p_pct_aligned = (p_aligned_recs / p_total_recs) * 100.0 if p_total_recs else 0.0

    b_avg_conflicts = b_total_conflicts / n_students
    p_avg_conflicts = p_total_conflicts / n_students
    avg_conflict_reduction_pct = ((b_avg_conflicts - p_avg_conflicts) / b_avg_conflicts) * 100.0 if b_avg_conflicts else 0.0

    b_pct_explained = (b_explained_recs / b_total_recs) * 100.0 if b_total_recs else 0.0
    p_pct_explained = (p_explained_recs / p_total_recs) * 100.0 if p_total_recs else 0.0

    p_sorted_lat = sorted(p_latencies)
    p_lat_p50 = p_sorted_lat[int(len(p_sorted_lat) * 0.50)]
    p_lat_p95 = p_sorted_lat[int(len(p_sorted_lat) * 0.95)]
    p_lat_p99 = p_sorted_lat[int(len(p_sorted_lat) * 0.99)]
    p_lat_avg = sum(p_latencies) / len(p_latencies)

    results = {
        "evaluation_timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "total_students": n_students,
        "metrics": {
            "pct_plans_with_conflicts": {
                "metric_name": "% of student course plans with >= 1 unresolved prerequisite conflict",
                "baseline": round(b_pct_conflict_plans, 2),
                "target": "<= 25.0% (reduce by >= 50% vs baseline)",
                "measured_prototype": round(p_pct_conflict_plans, 2),
                "reduction_achieved_pct": round(conflict_reduction_pct, 2),
                "passed": conflict_reduction_pct >= 50.0
            },
            "pct_aligned_recommendations": {
                "metric_name": "% of recommended electives rated aligned with stated goal",
                "baseline": round(b_pct_aligned, 2),
                "target": ">= 80.0%",
                "measured_prototype": round(p_pct_aligned, 2),
                "passed": p_pct_aligned >= 80.0
            },
            "avg_conflicts_per_plan": {
                "metric_name": "Avg. number of prerequisite conflicts per student plan",
                "baseline": round(b_avg_conflicts, 2),
                "target": "reduce by >= 50%",
                "measured_prototype": round(p_avg_conflicts, 2),
                "reduction_achieved_pct": round(avg_conflict_reduction_pct, 2),
                "passed": avg_conflict_reduction_pct >= 50.0
            },
            "recommendation_latency_ms": {
                "metric_name": "Recommendation response latency (ms)",
                "baseline": "n/a",
                "target": "< 500ms",
                "measured_prototype_avg": round(p_lat_avg, 2),
                "measured_prototype_p50": round(p_lat_p50, 2),
                "measured_prototype_p95": round(p_lat_p95, 2),
                "measured_prototype_p99": round(p_lat_p99, 2),
                "passed": p_lat_p95 < 500.0
            },
            "pct_explained_recommendations": {
                "metric_name": "% of recommendations with a valid, non-empty explanation",
                "baseline": round(b_pct_explained, 2),
                "target": "100.0%",
                "measured_prototype": round(p_pct_explained, 2),
                "passed": p_pct_explained == 100.0
            }
        },
        "baseline_failures": b_failure_breakdown,
        "prototype_failures": p_failure_breakdown
    }

    out_file = os.path.join(DATA_DIR, "evaluation_results.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"\nSaved evaluation results to: {out_file}")
    print("\n" + "="*70)
    print("COMPARATIVE EVALUATION SUMMARY (ACTUAL MEASURED NUMBERS)")
    print("="*70)
    for k, m in results["metrics"].items():
        print(f"Metric: {m['metric_name']}")
        print(f"  - Baseline: {m['baseline']}")
        print(f"  - Target:   {m['target']}")
        if "measured_prototype" in m:
            print(f"  - Prototype: {m['measured_prototype']} [{'PASS' if m['passed'] else 'FAIL'}]")
        else:
            print(f"  - Prototype p95: {m['measured_prototype_p95']} ms [{'PASS' if m['passed'] else 'FAIL'}]")
        print("-" * 70)

    return results

if __name__ == "__main__":
    evaluate()
