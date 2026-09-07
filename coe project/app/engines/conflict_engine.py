"""
Schedule & Course Conflict Engine.
Detects:
1. Timeslot collisions among courses planned in the same term.
2. Term progression sequencing violations (e.g., taking Course B in Term 1 when prerequisite A is also in Term 1 or planned later).
3. Max course / credit overload per term.
4. Term availability mismatches (course not offered in target term).
"""

from typing import List, Dict, Any, Set, Optional
from collections import defaultdict
from app.engines.graph_engine import PrerequisiteGraphEngine

class ConflictEngine:
    def __init__(self, schedules: List[Dict[str, Any]] = None, graph_engine: Optional[PrerequisiteGraphEngine] = None):
        self.schedules = schedules or []
        self.graph_engine = graph_engine
        
        # Build lookup: (course_id, term) -> List[schedule]
        self.schedule_lookup: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        for s in self.schedules:
            key = f"{s['course_id']}:{s['term']}"
            self.schedule_lookup[key].append(s)

    def detect_schedule_conflicts(self, courses: List[Dict[str, Any]], term: str) -> List[Dict[str, Any]]:
        """
        Detects if any two courses planned in the same term share an overlapping timeslot.
        """
        conflicts = []
        n = len(courses)
        
        for i in range(n):
            c1 = courses[i]
            c1_id = c1.get("course_id")
            schedules_1 = self.schedule_lookup.get(f"{c1_id}:{term}", [])
            
            # If not scheduled in this term
            if not schedules_1:
                conflicts.append({
                    "conflict_type": "term_unavailability",
                    "severity": "hard_error",
                    "course_id": c1_id,
                    "title": c1.get("title", c1_id),
                    "message": f"Course {c1_id} is not offered in {term}."
                })
                continue

            for j in range(i + 1, n):
                c2 = courses[j]
                c2_id = c2.get("course_id")
                schedules_2 = self.schedule_lookup.get(f"{c2_id}:{term}", [])

                for s1 in schedules_1:
                    for s2 in schedules_2:
                        if s1["day_time_slot"] == s2["day_time_slot"]:
                            conflicts.append({
                                "conflict_type": "timeslot_collision",
                                "severity": "hard_error",
                                "course_a": c1_id,
                                "course_b": c2_id,
                                "timeslot": s1["day_time_slot"],
                                "message": f"Timeslot conflict: {c1_id} and {c2_id} both meet on {s1['day_time_slot']}."
                            })

        return conflicts

    def validate_plan(
        self,
        planned_terms: List[Dict[str, Any]],
        completed_courses: List[str],
        max_courses_per_term: int = 3
    ) -> Dict[str, Any]:
        """
        Validates an entire multi-term course plan.
        planned_terms: [
            {"term": "Fall 2026", "courses": [{"course_id": "CS201", "credits": 4}, ...]},
            {"term": "Spring 2027", "courses": [...]}
        ]
        """
        accumulated_completed = set(completed_courses)
        all_conflicts = []
        is_valid = True

        for term_data in planned_terms:
            term_name = term_data.get("term", "Current Term")
            courses_in_term = term_data.get("courses", [])
            course_ids = [c["course_id"] for c in courses_in_term]

            # 1. Check max courses overload
            if len(courses_in_term) > max_courses_per_term:
                is_valid = False
                all_conflicts.append({
                    "conflict_type": "overload",
                    "term": term_name,
                    "severity": "warning",
                    "message": f"Plan for {term_name} contains {len(courses_in_term)} courses, exceeding your maximum preference of {max_courses_per_term} courses/term."
                })

            # 2. Check timeslot collisions
            schedule_conflicts = self.detect_schedule_conflicts(courses_in_term, term_name.split()[0])
            if schedule_conflicts:
                is_valid = False
                for sc in schedule_conflicts:
                    sc["term"] = term_name
                    all_conflicts.append(sc)

            # 3. Check prerequisite readiness for each course in this term
            if self.graph_engine:
                for c in courses_in_term:
                    cid = c["course_id"]
                    eligibility = self.graph_engine.evaluate_student_eligibility(cid, list(accumulated_completed))
                    if not eligibility["is_eligible"]:
                        is_valid = False
                        missing_names = [p["course_id"] for p in eligibility["direct_missing_hard"]]
                        all_conflicts.append({
                            "conflict_type": "prerequisite_violation",
                            "term": term_name,
                            "course_id": cid,
                            "missing_prerequisites": eligibility["direct_missing_hard"],
                            "severity": "hard_error",
                            "message": f"Prerequisite violation: {cid} requires {', '.join(missing_names)} which are not yet completed before {term_name}."
                        })

            # After term concludes, add courses to accumulated completed
            accumulated_completed.update(course_ids)

        return {
            "is_valid": is_valid,
            "total_conflicts": len(all_conflicts),
            "conflicts": all_conflicts,
            "simulated_graduation_credits": sum(c.get("credits", 3) for t in planned_terms for c in t.get("courses", []))
        }
