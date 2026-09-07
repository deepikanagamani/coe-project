"""
Explainable Recommendation Engine.
Produces rank-ordered elective suggestions combining:
1. Career Pathway alignment (advances stated goal)
2. Prerequisite eligibility (verified via DAG graph)
3. Schedule compatibility (no timeslot clashes)
4. Human-readable explainability (100% of recommendations include 1-2 sentence 'why')
5. Graceful fallback for missing or unknown goals
"""

from typing import List, Dict, Any, Optional
from app.engines.graph_engine import PrerequisiteGraphEngine
from app.engines.conflict_engine import ConflictEngine
from app.engines.career_engine import CareerConsequenceEngine

class ExplainableRecommender:
    def __init__(
        self,
        courses: List[Dict[str, Any]],
        graph_engine: PrerequisiteGraphEngine,
        conflict_engine: ConflictEngine,
        career_engine: CareerConsequenceEngine
    ):
        self.courses = courses
        self.courses_map = {c["course_id"]: c for c in courses}
        self.graph_engine = graph_engine
        self.conflict_engine = conflict_engine
        self.career_engine = career_engine

    def recommend(
        self,
        student: Dict[str, Any],
        term: str = "Fall",
        current_planned_courses: Optional[List[str]] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Recommends best-fitting electives for a student's upcoming term.
        Guarantees:
        - Prerequisite-checked (no unresolved prerequisite violations recommended)
        - Schedule-checked (no conflicting timeslots with existing plan)
        - Explainable (clear plain-language why)
        """
        completed = set(student.get("completed_courses", []))
        planned = set(current_planned_courses or [])
        goal_pathway = student.get("stated_goal_pathway") or ""
        max_courses = student.get("max_courses_per_term", 3)
        if limit is None:
            limit = max_courses

        # 1. Filter out already completed or planned courses and term unavailability
        candidate_courses = []
        for c in self.courses:
            cid = c["course_id"]
            if cid in completed or cid in planned:
                continue
            if term not in c.get("term_offered", []):
                continue
            
            # 2. Prerequisite Check (DAG)
            elig = self.graph_engine.evaluate_student_eligibility(cid, list(completed))
            if not elig["is_eligible"]:
                continue # Do not recommend courses with missing prerequisites!
                
            # 3. Schedule Check with already planned courses
            simulated_plan = [{"course_id": p} for p in planned] + [{"course_id": cid}]
            conflicts = self.conflict_engine.detect_schedule_conflicts(simulated_plan, term)
            if conflicts:
                continue # Skip courses that collide with student's existing schedule!

            # 4. Career Alignment & Explanation
            alignment = self.career_engine.evaluate_course_alignment(cid, goal_pathway)
            
            # Synthesize 1-2 sentence human-readable explanation
            if alignment["status"] in ["advancing", "supportive"]:
                why_text = f"Directly prepares you for your {alignment.get('pathway_name', 'career')} goal. {alignment['rationale']}"
            elif not goal_pathway:
                why_text = f"High-impact foundational elective ({c['department']} curriculum) providing versatile skills across multiple technical pathways."
            else:
                why_text = f"Solid cross-disciplinary course expanding your {c['department']} breadth with fully satisfied prerequisites."

            # Calculate composite ranking score
            # Strong priority for courses advancing or supporting the student's stated goal
            if alignment["status"] == "advancing":
                score = 100.0 + (alignment["score"] * 50.0) + (c.get("credits", 3) * 0.5)
            elif alignment["status"] == "supportive":
                score = 60.0 + (alignment["score"] * 20.0) + (c.get("credits", 3) * 0.5)
            elif not goal_pathway:
                # Versatile foundational courses for undeclared learners
                score = 20.0 + (c.get("credits", 3) * 1.0)
            else:
                # Neutral courses outside stated career pathway
                score = 2.0 + (c.get("credits", 3) * 0.2)
                
            candidate_courses.append({
                "course_id": cid,
                "title": c["title"],
                "department": c["department"],
                "credits": c["credits"],
                "difficulty_level": c.get("difficulty_level", "Intermediate"),
                "pathway_alignment": alignment["status"],
                "score": round(score, 2),
                "explanation": why_text,
                "prerequisites_checked": True,
                "schedule_checked": True
            })

        # Sort candidates by score descending
        candidate_courses.sort(key=lambda x: x["score"], reverse=True)

        # If student has a stated career goal, select strictly from advancing/supportive courses
        # (avoiding unaligned courses that distract from degree timeline)
        # If no advancing courses are immediately eligible, fallback to foundational candidates
        if goal_pathway:
            aligned_pool = [c for c in candidate_courses if c["pathway_alignment"] in ["advancing", "supportive"]]
            selection_pool = aligned_pool if len(aligned_pool) > 0 else candidate_courses
        else:
            selection_pool = candidate_courses

        # Greedy intra-batch conflict resolution:
        # Guarantee that recommended courses do not collide with each other in timeslots
        chosen_recommendations = []
        batch_planned = list(planned)

        for cand in selection_pool:
            sim_batch = [{"course_id": cid} for cid in batch_planned] + [{"course_id": cand["course_id"]}]
            conflicts = self.conflict_engine.detect_schedule_conflicts(sim_batch, term)
            if conflicts:
                continue # Skip if candidate clashes with another course already chosen in this batch!
            
            chosen_recommendations.append(cand)
            batch_planned.append(cand["course_id"])
            if len(chosen_recommendations) >= limit:
                break

        return chosen_recommendations
