"""
FastAPI REST Application for Prerequisite & Career-Consequence Explorer.
Exposes high-performance, explainable endpoints for:
- Course catalog & prerequisite DAG pathfinding
- Plan conflict & progression verification
- Career consequence preview & 'why not' inspection
- Explainable elective recommendations (<500ms latency)
- Aggregate mentor bottleneck insights (zero individual surveillance)
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import os
import time

from app.database import (
    init_db,
    get_all_courses,
    get_course_by_id,
    get_all_prerequisites,
    get_prerequisites_for_course,
    get_schedules_for_course,
    get_all_pathways,
    get_pathway_by_id,
    get_all_students,
    get_student_by_id,
    get_historical_bottlenecks,
    get_db_connection
)
from app.engines.graph_engine import PrerequisiteGraphEngine
from app.engines.conflict_engine import ConflictEngine
from app.engines.career_engine import CareerConsequenceEngine
from app.engines.recommender import ExplainableRecommender

# Initialize SQLite database if needed
init_db()

app = FastAPI(
    title="Prerequisite & Career-Consequence Explorer API",
    description="Explainable, privacy-preserving curriculum planning and prerequisite explorer.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load in-memory engine instances
courses_data = get_all_courses()
prereqs_data = get_all_prerequisites()
pathways_data = get_all_pathways()

# Fetch raw pathway course associations
conn = get_db_connection()
pw_courses_raw = conn.execute("SELECT pathway_id, course_id, weight, rationale FROM pathway_courses").fetchall()
schedules_raw = conn.execute("SELECT course_id, term, day_time_slot, room, capacity FROM schedules").fetchall()
conn.close()

pw_courses_data = [dict(r) for r in pw_courses_raw]
schedules_data = [dict(r) for r in schedules_raw]

graph_engine = PrerequisiteGraphEngine(prereqs_data, courses_data)
conflict_engine = ConflictEngine(schedules_data, graph_engine)
career_engine = CareerConsequenceEngine(pathways_data, pw_courses_data, graph_engine, conflict_engine)
recommender = ExplainableRecommender(courses_data, graph_engine, conflict_engine, career_engine)

# -------------------------------------------------------------------------
# Request Models
# -------------------------------------------------------------------------
class ValidatePlanRequest(BaseModel):
    planned_terms: List[Dict[str, Any]] = Field(..., description="List of terms with courses")
    completed_courses: List[str] = Field(default_factory=list)
    max_courses_per_term: int = Field(default=3)

class RecommendationRequest(BaseModel):
    student_id: Optional[str] = None
    completed_courses: Optional[List[str]] = None
    stated_goal_pathway: Optional[str] = None
    term: str = "Fall"
    current_planned_courses: Optional[List[str]] = None
    limit: Optional[int] = 3

class ConsequencePreviewRequest(BaseModel):
    candidate_course_id: str
    current_planned_courses: List[Dict[str, Any]] = Field(default_factory=list)
    completed_courses: List[str] = Field(default_factory=list)
    term: str = "Fall"
    pathway_id: Optional[str] = None
    max_courses_per_term: int = 3

class WhyNotRequest(BaseModel):
    course_id: str
    completed_courses: List[str] = Field(default_factory=list)
    current_planned_courses: List[str] = Field(default_factory=list)
    term: str = "Fall"
    pathway_id: Optional[str] = None

# -------------------------------------------------------------------------
# API Endpoints
# -------------------------------------------------------------------------
@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "total_courses": len(courses_data),
        "total_pathways": len(pathways_data)
    }

@app.get("/api/courses")
def list_courses(
    department: Optional[str] = None,
    term: Optional[str] = None,
    search: Optional[str] = None
):
    results = courses_data
    if department:
        results = [c for c in results if c["department"].lower() == department.lower()]
    if term:
        results = [c for c in results if term in c["term_offered"]]
    if search:
        q = search.lower()
        results = [c for c in results if q in c["course_id"].lower() or q in c["title"].lower() or q in c["description"].lower()]
    return results

@app.get("/api/courses/{course_id}")
def get_course_detail(course_id: str):
    course = get_course_by_id(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    schedules = get_schedules_for_course(course_id)
    prereqs = get_prerequisites_for_course(course_id)
    return {
        **course,
        "schedules": schedules,
        "prerequisites": prereqs
    }

@app.get("/api/courses/{course_id}/prerequisites")
def get_prerequisite_dag(course_id: str, student_id: Optional[str] = None):
    course = get_course_by_id(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
        
    completed = []
    if student_id:
        student = get_student_by_id(student_id)
        if student:
            completed = student["completed_courses"]

    dag_payload = graph_engine.build_dag_visualization_payload(course_id, completed)
    shortest_path = graph_engine.get_shortest_prerequisite_path(course_id, completed)
    eligibility = graph_engine.evaluate_student_eligibility(course_id, completed)

    return {
        "course_id": course_id,
        "title": course["title"],
        "eligibility": eligibility,
        "shortest_prerequisite_path": shortest_path,
        "dag": dag_payload
    }

@app.get("/api/pathways")
def list_pathways():
    return pathways_data

@app.get("/api/pathways/{pathway_id}")
def get_pathway_detail(pathway_id: str):
    pw = get_pathway_by_id(pathway_id)
    if not pw:
        raise HTTPException(status_code=404, detail="Pathway not found")
    return pw

@app.get("/api/students")
def list_students(limit: int = 50):
    all_students = get_all_students()
    return all_students[:limit]

@app.get("/api/students/{student_id}")
def get_student(student_id: str):
    student = get_student_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@app.post("/api/plan/validate")
def validate_plan(req: ValidatePlanRequest):
    start = time.perf_counter()
    validation = conflict_engine.validate_plan(
        planned_terms=req.planned_terms,
        completed_courses=req.completed_courses,
        max_courses_per_term=req.max_courses_per_term
    )
    latency_ms = (time.perf_counter() - start) * 1000
    return {
        **validation,
        "latency_ms": round(latency_ms, 2)
    }

@app.post("/api/recommendations")
def get_recommendations(req: RecommendationRequest):
    start = time.perf_counter()
    student_profile = {}
    
    if req.student_id:
        s = get_student_by_id(req.student_id)
        if s:
            student_profile = s
            
    if req.completed_courses is not None:
        student_profile["completed_courses"] = req.completed_courses
    elif "completed_courses" not in student_profile:
        student_profile["completed_courses"] = []

    if req.stated_goal_pathway is not None:
        student_profile["stated_goal_pathway"] = req.stated_goal_pathway
    elif "stated_goal_pathway" not in student_profile:
        student_profile["stated_goal_pathway"] = ""

    recs = recommender.recommend(
        student=student_profile,
        term=req.term,
        current_planned_courses=req.current_planned_courses,
        limit=req.limit
    )
    
    latency_ms = (time.perf_counter() - start) * 1000
    
    return {
        "term": req.term,
        "stated_goal_pathway": student_profile.get("stated_goal_pathway"),
        "total_recommendations": len(recs),
        "latency_ms": round(latency_ms, 2),
        "recommendations": recs
    }

@app.post("/api/consequences/preview")
def preview_consequence(req: ConsequencePreviewRequest):
    start = time.perf_counter()
    preview = career_engine.preview_consequence(
        candidate_course_id=req.candidate_course_id,
        current_planned_courses=req.current_planned_courses,
        completed_courses=req.completed_courses,
        term=req.term,
        pathway_id=req.pathway_id,
        max_courses_per_term=req.max_courses_per_term
    )
    latency_ms = (time.perf_counter() - start) * 1000
    return {
        **preview,
        "latency_ms": round(latency_ms, 2)
    }

@app.post("/api/why-not")
def explain_why_not(req: WhyNotRequest):
    start = time.perf_counter()
    res = career_engine.explain_why_not(
        course_id=req.course_id,
        completed_courses=req.completed_courses,
        current_planned_courses=req.current_planned_courses,
        term=req.term,
        pathway_id=req.pathway_id
    )
    latency_ms = (time.perf_counter() - start) * 1000
    return {
        **res,
        "latency_ms": round(latency_ms, 2)
    }

@app.get("/api/mentor/bottlenecks")
def get_mentor_bottlenecks():
    """
    Lightweight, aggregate, non-punitive mentor view.
    Zero per-student tracking or behavioral risk scoring.
    Surfaces curriculum-level friction points across the cohort.
    """
    conn = get_db_connection()
    
    # 1. Prerequisite drop-offs in historical logs
    prereq_drops = conn.execute("""
        SELECT c.course_id, c.title, c.department, COUNT(*) as drop_count
        FROM historical_outcomes h
        JOIN courses c ON h.course_id = c.course_id
        WHERE h.outcome = 'prerequisite_violation_dropped'
        GROUP BY c.course_id
        ORDER BY drop_count DESC
        LIMIT 10
    """).fetchall()

    # 2. Schedule conflict drop-offs
    schedule_drops = conn.execute("""
        SELECT c.course_id, c.title, c.department, COUNT(*) as conflict_count
        FROM historical_outcomes h
        JOIN courses c ON h.course_id = c.course_id
        WHERE h.outcome = 'schedule_conflict_dropped'
        GROUP BY c.course_id
        ORDER BY conflict_count DESC
        LIMIT 10
    """).fetchall()

    # 3. Courses with highest downstream prerequisite dependencies
    downstream_impact = conn.execute("""
        SELECT p.prerequisite_course_id as course_id, c.title, c.department, COUNT(*) as dependent_courses_count
        FROM prerequisites p
        JOIN courses c ON p.prerequisite_course_id = c.course_id
        WHERE p.requirement_type = 'hard'
        GROUP BY p.prerequisite_course_id
        ORDER BY dependent_courses_count DESC
        LIMIT 10
    """).fetchall()

    # 4. Cohort summary counts
    total_students = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    total_enrollment_events = conn.execute("SELECT COUNT(*) FROM historical_outcomes").fetchone()[0]
    conn.close()

    return {
        "privacy_notice": "AGGREGATE METRICS ONLY. No individual student data, rankings, or surveillance flags are stored or displayed.",
        "cohort_summary": {
            "total_students": total_students,
            "total_enrollment_events_analyzed": total_enrollment_events,
            "top_bottleneck_course": prereq_drops[0]["course_id"] if prereq_drops else None
        },
        "top_prerequisite_bottlenecks": [dict(r) for r in prereq_drops],
        "top_schedule_conflict_courses": [dict(r) for r in schedule_drops],
        "top_downstream_dependency_gateways": [dict(r) for r in downstream_impact]
    }

# -------------------------------------------------------------------------
# Static Assets Mounting
# -------------------------------------------------------------------------
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(STATIC_DIR):
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
