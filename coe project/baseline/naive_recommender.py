"""
Naive Baseline Course Recommender.
Represents the status-quo workflow: students search a flat course catalog
using keyword matching or popularity, with ZERO prerequisite graph checking,
ZERO schedule collision detection, and ZERO explainability.
"""

import json
import os
from typing import List, Dict, Any

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

class NaiveBaselineRecommender:
    def __init__(self, data_dir: str = DATA_DIR):
        self.data_dir = data_dir
        with open(os.path.join(data_dir, "courses.json"), "r", encoding="utf-8") as f:
            self.courses = json.load(f)
        with open(os.path.join(data_dir, "pathways.json"), "r", encoding="utf-8") as f:
            self.pathways = json.load(f)
        
        # Build keyword lookup map based on pathway names/descriptions
        self.pathway_keywords: Dict[str, List[str]] = {}
        for pw in self.pathways:
            keywords = [pw["name"].lower()]
            keywords.extend([c.lower() for c in pw.get("target_competencies", [])])
            for d in pw.get("primary_departments", []):
                keywords.append(d.lower())
            self.pathway_keywords[pw["pathway_id"]] = keywords

    def recommend(self, student: Dict[str, Any], term: str = "Fall", limit: int = None) -> List[Dict[str, Any]]:
        """
        Naive recommendation logic:
        1. Filters out already completed courses.
        2. If student has a stated goal, finds courses whose title or description matches keywords in that goal.
        3. If no goal or no keyword matches, falls back to catalog order (flat alphabetical or ID listing).
        4. Does NOT check prerequisites (leads to prerequisite violations!).
        5. Does NOT check schedule timeslot clashes (leads to time conflicts!).
        6. Provides NO plain-language rationale (0% explainability).
        """
        if limit is None:
            limit = student.get("max_courses_per_term", 3)
            
        completed = set(student.get("completed_courses", []))
        stated_goal = student.get("stated_goal_pathway", "")
        
        # Available courses in target term (uncompleted)
        candidates = [c for c in self.courses if c["course_id"] not in completed and term in c.get("term_offered", [])]
        
        # Keyword scoring
        keywords = self.pathway_keywords.get(stated_goal, [])
        scored_candidates = []
        for c in candidates:
            score = 0
            text = f"{c['title']} {c['description']} {c['department']}".lower()
            for kw in keywords:
                if kw in text:
                    score += 1
            scored_candidates.append((score, c))
            
        # Sort by keyword score descending, then by course_id
        scored_candidates.sort(key=lambda x: (x[0], -int(x[1]["credits"])), reverse=True)
        
        recommendations = []
        for score, course in scored_candidates[:limit]:
            recommendations.append({
                "course_id": course["course_id"],
                "title": course["title"],
                "department": course["department"],
                "credits": course["credits"],
                "keyword_match_score": score,
                "explanation": "",  # Baseline has ZERO explainability
                "prerequisites_checked": False,
                "schedule_checked": False
            })
            
        return recommendations


def main():
    recommender = NaiveBaselineRecommender()
    sample_student = {
        "student_id": "STU_TEST",
        "completed_courses": ["CS101"],
        "stated_goal_pathway": "PW_ML_ENG",
        "max_courses_per_term": 3
    }
    recs = recommender.recommend(sample_student, term="Fall")
    print("Baseline Sample Output for ML Engineer goal:")
    for r in recs:
        print(f"  - {r['course_id']}: {r['title']} (Keyword score: {r['keyword_match_score']}, Explanation: '{r['explanation']}')")

if __name__ == "__main__":
    main()
