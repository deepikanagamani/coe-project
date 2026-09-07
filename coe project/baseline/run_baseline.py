"""
Stand-alone runner for the Naive Baseline Recommender across the synthetic student dataset.
Outputs baseline course selections to data/baseline_results.json.
"""

import json
import os
import time
from baseline.naive_recommender import NaiveBaselineRecommender

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

def run_baseline_evaluation():
    print("=== EXECUTING NAIVE BASELINE RECOMMENDER ACROSS SYNTHETIC COHORT ===")
    recommender = NaiveBaselineRecommender(DATA_DIR)
    
    with open(os.path.join(DATA_DIR, "students.json"), "r", encoding="utf-8") as f:
        students = json.load(f)
        
    start_time = time.perf_counter()
    results = []
    
    for s in students:
        recs = recommender.recommend(s, term="Fall")
        results.append({
            "student_id": s["student_id"],
            "stated_goal_pathway": s["stated_goal_pathway"],
            "max_courses_per_term": s["max_courses_per_term"],
            "recommended_courses": [r["course_id"] for r in recs],
            "recommendation_details": recs
        })
        
    total_time = (time.perf_counter() - start_time) * 1000 # ms
    avg_latency = total_time / len(students)
    
    out_path = os.path.join(DATA_DIR, "baseline_results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({
            "total_students_evaluated": len(students),
            "average_latency_ms": round(avg_latency, 3),
            "results": results
        }, f, indent=2)
        
    print(f"Generated baseline recommendations for {len(students)} students.")
    print(f"Average latency per student: {avg_latency:.3f} ms.")
    print(f"Saved results to: {out_path}")

if __name__ == "__main__":
    run_baseline_evaluation()
