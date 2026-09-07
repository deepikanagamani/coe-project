"""
Integration tests for FastAPI REST API endpoints using TestClient.
"""

import pytest
from starlette.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check_endpoint():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["total_courses"] >= 60

def test_list_courses_filtering():
    res = client.get("/api/courses?department=CS")
    assert res.status_code == 200
    courses = res.json()
    assert len(courses) > 0
    assert all(c["department"] == "CS" for c in courses)

def test_course_prerequisite_dag():
    res = client.get("/api/courses/CS405/prerequisites?student_id=STU_0001")
    assert res.status_code == 200
    data = res.json()
    assert data["course_id"] == "CS405"
    assert "dag" in data
    assert "nodes" in data["dag"]
    assert "edges" in data["dag"]
    assert len(data["dag"]["nodes"]) > 0

def test_recommendations_endpoint_latency_and_explainability():
    req_body = {
        "student_id": "STU_0001",
        "term": "Fall",
        "limit": 3
    }
    res = client.post("/api/recommendations", json=req_body)
    assert res.status_code == 200
    data = res.json()
    assert data["latency_ms"] < 500.0
    assert len(data["recommendations"]) > 0
    # Assert 100% explainability coverage
    for rec in data["recommendations"]:
        assert rec["explanation"] is not None
        assert len(rec["explanation"].strip()) > 10

def test_consequence_preview_endpoint():
    req_body = {
        "candidate_course_id": "CS405",
        "current_planned_courses": [],
        "completed_courses": ["CS101"],
        "term": "Fall",
        "pathway_id": "PW_ML_ENG",
        "max_courses_per_term": 3
    }
    res = client.post("/api/consequences/preview", json=req_body)
    assert res.status_code == 200
    data = res.json()
    assert data["candidate_course_id"] == "CS405"
    assert "plain_language_narrative" in data
    assert len(data["plain_language_narrative"]) > 0

def test_mentor_bottlenecks_endpoint_privacy():
    res = client.get("/api/mentor/bottlenecks")
    assert res.status_code == 200
    data = res.json()
    assert "privacy_notice" in data
    assert "top_prerequisite_bottlenecks" in data
    # Assert NO student PII is exposed
    assert "students" not in data
    assert "individual_transcripts" not in data
