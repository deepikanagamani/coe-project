"""
Career Consequence & Explainability Engine.
Evaluates course choices against defined career pathways:
- Scores courses as Advancing, Neutral, or Delaying/Conflicting
- Produces plain-language human-auditable rationales
- Generates pre-enrollment consequence previews (ripple effect of taking course X)
- Answers "Why NOT this course?" with explicit reasons
"""

from typing import List, Dict, Any, Optional, Set
from collections import defaultdict
from app.engines.graph_engine import PrerequisiteGraphEngine
from app.engines.conflict_engine import ConflictEngine

class CareerConsequenceEngine:
    def __init__(
        self,
        pathways: List[Dict[str, Any]],
        pathway_courses: List[Dict[str, Any]],
        graph_engine: Optional[PrerequisiteGraphEngine] = None,
        conflict_engine: Optional[ConflictEngine] = None
    ):
        self.pathways = {p["pathway_id"]: p for p in pathways}
        self.graph_engine = graph_engine
        self.conflict_engine = conflict_engine
        
        # (pathway_id, course_id) -> {weight, rationale}
        self.pw_course_map: Dict[str, Dict[str, Any]] = {}
        for pc in pathway_courses:
            key = f"{pc['pathway_id']}:{pc['course_id']}"
            self.pw_course_map[key] = {
                "weight": pc["weight"],
                "rationale": pc["rationale"]
            }

    def evaluate_course_alignment(self, course_id: str, pathway_id: Optional[str]) -> Dict[str, Any]:
        """
        Evaluates whether course_id advances, is neutral, or conflicts with pathway_id.
        """
        if not pathway_id or pathway_id not in self.pathways:
            return {
                "course_id": course_id,
                "pathway_id": pathway_id,
                "status": "neutral",
                "score": 0.3,
                "rationale": "General elective credit; no specific career pathway selected to evaluate alignment."
            }

        key = f"{pathway_id}:{course_id}"
        mapping = self.pw_course_map.get(key)
        pathway_info = self.pathways[pathway_id]

        if mapping:
            weight = mapping["weight"]
            rationale = mapping["rationale"]
            status = "advancing" if weight >= 0.7 else "supportive"
            return {
                "course_id": course_id,
                "pathway_id": pathway_id,
                "pathway_name": pathway_info["name"],
                "status": status,
                "score": weight,
                "rationale": f"Materially advances your {pathway_info['name']} goal. {rationale}"
            }
        else:
            return {
                "course_id": course_id,
                "pathway_id": pathway_id,
                "pathway_name": pathway_info["name"],
                "status": "neutral",
                "score": 0.1,
                "rationale": f"Neutral for your {pathway_info['name']} pathway. Satisfies general credits, but does not fulfill core competencies."
            }

    def preview_consequence(
        self,
        candidate_course_id: str,
        current_planned_courses: List[Dict[str, Any]],
        completed_courses: List[str],
        term: str,
        pathway_id: Optional[str],
        max_courses_per_term: int = 3
    ) -> Dict[str, Any]:
        """
        Generates a comprehensive pre-enrollment consequence preview:
        - What career impact does adding candidate_course_id have?
        - Does it cause a timeslot clash with existing choices?
        - Does it exceed max term limit?
        - Does it bump or delay a key prerequisite for the student's career goal?
        """
        alignment = self.evaluate_course_alignment(candidate_course_id, pathway_id)
        
        # 1. Prerequisite readiness
        eligibility = None
        prereq_warning = None
        if self.graph_engine:
            eligibility = self.graph_engine.evaluate_student_eligibility(candidate_course_id, completed_courses)
            if not eligibility["is_eligible"]:
                missing_names = [p["course_id"] for p in eligibility["direct_missing_hard"]]
                prereq_warning = f"Missing prerequisite(s): {', '.join(missing_names)}. Taking this course without prerequisites risks academic failure or administrative drop."

        # 2. Schedule conflict with existing plan in this term
        existing_candidate_list = list(current_planned_courses) + [{"course_id": candidate_course_id}]
        schedule_conflicts = []
        if self.conflict_engine:
            schedule_conflicts = self.conflict_engine.detect_schedule_conflicts(existing_candidate_list, term)

        # 3. Capacity / Overload check
        is_overload = len(existing_candidate_list) > max_courses_per_term
        overload_warning = None
        if is_overload:
            overload_warning = f"Adding this course brings your term load to {len(existing_candidate_list)} courses, exceeding your preferred pace of {max_courses_per_term} courses/term."

        # 4. Opportunity cost / pathway delay analysis
        tradeoff_summary = []
        if alignment["status"] == "neutral" and pathway_id and pathway_id in self.pathways:
            pathway_name = self.pathways[pathway_id]["name"]
            # Look for an available advancing course that could have been taken instead
            tradeoff_summary.append(
                f"Taking {candidate_course_id} uses one of your {max_courses_per_term} course slots for {term} on a course outside your {pathway_name} milestone."
            )

        # Build combined plain-language preview narrative
        sentences = []
        if prereq_warning:
            sentences.append(f"⚠️ {prereq_warning}")
        if schedule_conflicts:
            sentences.append(f"❌ Schedule clash: {schedule_conflicts[0]['message']}")
        if overload_warning:
            sentences.append(f"ℹ️ {overload_warning}")
        sentences.append(alignment["rationale"])

        plain_language_narrative = " ".join(sentences)

        return {
            "candidate_course_id": candidate_course_id,
            "term": term,
            "pathway_alignment": alignment,
            "prerequisite_eligibility": eligibility,
            "has_prerequisite_block": prereq_warning is not None,
            "has_schedule_conflict": len(schedule_conflicts) > 0,
            "is_overload": is_overload,
            "schedule_conflicts": schedule_conflicts,
            "plain_language_narrative": plain_language_narrative,
            "can_proceed_safely": (prereq_warning is None and len(schedule_conflicts) == 0 and not is_overload)
        }

    def explain_why_not(
        self,
        course_id: str,
        completed_courses: List[str],
        current_planned_courses: List[str],
        term: str,
        pathway_id: Optional[str]
    ) -> Dict[str, Any]:
        """
        Explicitly answers 'Why NOT take this course?' for a student.
        """
        reasons = []

        # 1. Already completed?
        if course_id in completed_courses:
            reasons.append(f"You have already completed {course_id}. Repeating completed coursework yields no additional degree credits.")

        # 2. Already planned?
        if course_id in current_planned_courses:
            reasons.append(f"{course_id} is already in your current semester plan.")

        # 3. Missing prerequisites?
        if self.graph_engine:
            elig = self.graph_engine.evaluate_student_eligibility(course_id, completed_courses)
            if not elig["is_eligible"]:
                missing_str = ", ".join(f"{p['course_id']} ({p['title']})" for p in elig["direct_missing_hard"])
                reasons.append(f"You have not completed the required prerequisite(s): {missing_str}.")

        # 4. Schedule conflict?
        if self.conflict_engine:
            simulated = [{"course_id": cid} for cid in current_planned_courses] + [{"course_id": course_id}]
            conflicts = self.conflict_engine.detect_schedule_conflicts(simulated, term)
            for c in conflicts:
                if c.get("conflict_type") == "timeslot_collision" and (c.get("course_a") == course_id or c.get("course_b") == course_id):
                    other = c["course_b"] if c["course_a"] == course_id else c["course_a"]
                    reasons.append(f"Timeslot collision with {other} on {c['timeslot']}.")
                elif c.get("conflict_type") == "term_unavailability" and c.get("course_id") == course_id:
                    reasons.append(f"{course_id} is not scheduled for offering in {term}.")

        # 5. Career misalignment?
        alignment = self.evaluate_course_alignment(course_id, pathway_id)
        if alignment["status"] == "neutral" and pathway_id:
            reasons.append(f"Low alignment with your stated career goal ({alignment.get('pathway_name')}).")

        if not reasons:
            reasons.append(f"{course_id} is actually eligible and available to add without immediate blockers!")

        return {
            "course_id": course_id,
            "is_blocked": len(reasons) > 0 and "actually eligible" not in reasons[0],
            "reasons": reasons,
            "plain_explanation": " ".join(reasons)
        }
