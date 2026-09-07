"""
SQLite Database Initializer and Data Access Layer for Prerequisite Explorer.
Loads and indexes the synthetic dataset into a high-performance local SQLite database.
"""

import sqlite3
import json
import os
from typing import List, Dict, Any, Optional

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "explorer.db")

def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(force: bool = False) -> None:
    if os.path.exists(DB_PATH) and not force:
        return

    print(f"Initializing SQLite database at: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Create tables
    cur.executescript("""
        DROP TABLE IF EXISTS courses;
        DROP TABLE IF EXISTS prerequisites;
        DROP TABLE IF EXISTS schedules;
        DROP TABLE IF EXISTS pathways;
        DROP TABLE IF EXISTS pathway_courses;
        DROP TABLE IF EXISTS students;
        DROP TABLE IF EXISTS historical_outcomes;

        CREATE TABLE courses (
            course_id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            department TEXT NOT NULL,
            credits INTEGER NOT NULL,
            description TEXT NOT NULL,
            term_offered TEXT NOT NULL,
            difficulty_level TEXT NOT NULL
        );

        CREATE TABLE prerequisites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id TEXT NOT NULL,
            prerequisite_course_id TEXT NOT NULL,
            requirement_type TEXT NOT NULL,
            FOREIGN KEY (course_id) REFERENCES courses(course_id),
            FOREIGN KEY (prerequisite_course_id) REFERENCES courses(course_id)
        );

        CREATE TABLE schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id TEXT NOT NULL,
            term TEXT NOT NULL,
            day_time_slot TEXT NOT NULL,
            room TEXT NOT NULL,
            capacity INTEGER NOT NULL,
            FOREIGN KEY (course_id) REFERENCES courses(course_id)
        );

        CREATE TABLE pathways (
            pathway_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            primary_departments TEXT NOT NULL,
            target_competencies TEXT NOT NULL
        );

        CREATE TABLE pathway_courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pathway_id TEXT NOT NULL,
            course_id TEXT NOT NULL,
            weight REAL NOT NULL,
            rationale TEXT NOT NULL,
            FOREIGN KEY (pathway_id) REFERENCES pathways(pathway_id),
            FOREIGN KEY (course_id) REFERENCES courses(course_id)
        );

        CREATE TABLE students (
            student_id TEXT PRIMARY KEY,
            completed_courses TEXT NOT NULL,
            stated_goal_pathway TEXT,
            max_courses_per_term INTEGER NOT NULL,
            term_progress TEXT NOT NULL,
            language_preference TEXT NOT NULL,
            accessibility_preference TEXT NOT NULL
        );

        CREATE TABLE historical_outcomes (
            event_id TEXT PRIMARY KEY,
            student_id TEXT NOT NULL,
            course_id TEXT NOT NULL,
            term TEXT NOT NULL,
            outcome TEXT NOT NULL,
            notes TEXT
        );

        -- Performance Indexes
        CREATE INDEX idx_prereq_course ON prerequisites(course_id);
        CREATE INDEX idx_prereq_target ON prerequisites(prerequisite_course_id);
        CREATE INDEX idx_schedules_course_term ON schedules(course_id, term);
        CREATE INDEX idx_pathway_courses_pw ON pathway_courses(pathway_id);
        CREATE INDEX idx_historical_course ON historical_outcomes(course_id);
    """)

    # Populate from JSON files
    with open(os.path.join(DATA_DIR, "courses.json"), "r", encoding="utf-8") as f:
        courses = json.load(f)
        for c in courses:
            cur.execute("""
                INSERT INTO courses (course_id, title, department, credits, description, term_offered, difficulty_level)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (c["course_id"], c["title"], c["department"], c["credits"], c["description"], json.dumps(c["term_offered"]), c["difficulty_level"]))

    with open(os.path.join(DATA_DIR, "prerequisites.json"), "r", encoding="utf-8") as f:
        prereqs = json.load(f)
        for p in prereqs:
            cur.execute("""
                INSERT INTO prerequisites (course_id, prerequisite_course_id, requirement_type)
                VALUES (?, ?, ?)
            """, (p["course_id"], p["prerequisite_course_id"], p["requirement_type"]))

    with open(os.path.join(DATA_DIR, "schedules.json"), "r", encoding="utf-8") as f:
        schedules = json.load(f)
        for s in schedules:
            cur.execute("""
                INSERT INTO schedules (course_id, term, day_time_slot, room, capacity)
                VALUES (?, ?, ?, ?, ?)
            """, (s["course_id"], s["term"], s["day_time_slot"], s["room"], s["capacity"]))

    with open(os.path.join(DATA_DIR, "pathways.json"), "r", encoding="utf-8") as f:
        pathways = json.load(f)
        for pw in pathways:
            cur.execute("""
                INSERT INTO pathways (pathway_id, name, description, primary_departments, target_competencies)
                VALUES (?, ?, ?, ?, ?)
            """, (pw["pathway_id"], pw["name"], pw["description"], json.dumps(pw["primary_departments"]), json.dumps(pw["target_competencies"])))

    with open(os.path.join(DATA_DIR, "pathway_courses.json"), "r", encoding="utf-8") as f:
        pw_courses = json.load(f)
        for pc in pw_courses:
            cur.execute("""
                INSERT INTO pathway_courses (pathway_id, course_id, weight, rationale)
                VALUES (?, ?, ?, ?)
            """, (pc["pathway_id"], pc["course_id"], pc["weight"], pc["rationale"]))

    with open(os.path.join(DATA_DIR, "students.json"), "r", encoding="utf-8") as f:
        students = json.load(f)
        for s in students:
            cur.execute("""
                INSERT INTO students (student_id, completed_courses, stated_goal_pathway, max_courses_per_term, term_progress, language_preference, accessibility_preference)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (s["student_id"], json.dumps(s["completed_courses"]), s["stated_goal_pathway"], s["max_courses_per_term"], s["term_progress"], s["language_preference"], s["accessibility_preference"]))

    with open(os.path.join(DATA_DIR, "historical_outcomes.json"), "r", encoding="utf-8") as f:
        outcomes = json.load(f)
        for o in outcomes:
            cur.execute("""
                INSERT INTO historical_outcomes (event_id, student_id, course_id, term, outcome, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (o["event_id"], o["student_id"], o["course_id"], o["term"], o["outcome"], o["notes"]))

    conn.commit()
    conn.close()
    print("Database initialization complete.")

# Data Access Functions
def get_all_courses() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM courses ORDER BY course_id").fetchall()
    conn.close()
    result = []
    for r in rows:
        d = dict(r)
        d["term_offered"] = json.loads(d["term_offered"])
        result.append(d)
    return result

def get_course_by_id(course_id: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM courses WHERE course_id = ?", (course_id,)).fetchone()
    conn.close()
    if not row:
        return None
    d = dict(row)
    d["term_offered"] = json.loads(d["term_offered"])
    return d

def get_prerequisites_for_course(course_id: str) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT p.course_id, p.prerequisite_course_id, p.requirement_type, c.title, c.department, c.credits
        FROM prerequisites p
        JOIN courses c ON p.prerequisite_course_id = c.course_id
        WHERE p.course_id = ?
    """, (course_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_all_prerequisites() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    rows = conn.execute("SELECT course_id, prerequisite_course_id, requirement_type FROM prerequisites").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_schedules_for_course(course_id: str, term: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    if term:
        rows = conn.execute("SELECT * FROM schedules WHERE course_id = ? AND term = ?", (course_id, term)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM schedules WHERE course_id = ?", (course_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_all_pathways() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM pathways").fetchall()
    conn.close()
    res = []
    for r in rows:
        d = dict(r)
        d["primary_departments"] = json.loads(d["primary_departments"])
        d["target_competencies"] = json.loads(d["target_competencies"])
        res.append(d)
    return res

def get_pathway_by_id(pathway_id: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM pathways WHERE pathway_id = ?", (pathway_id,)).fetchone()
    if not row:
        conn.close()
        return None
    d = dict(row)
    d["primary_departments"] = json.loads(d["primary_departments"])
    d["target_competencies"] = json.loads(d["target_competencies"])
    # Fetch supporting courses
    courses_rows = conn.execute("""
        SELECT pc.course_id, pc.weight, pc.rationale, c.title, c.department, c.credits
        FROM pathway_courses pc
        JOIN courses c ON pc.course_id = c.course_id
        WHERE pc.pathway_id = ?
        ORDER BY pc.weight DESC
    """, (pathway_id,)).fetchall()
    conn.close()
    d["supporting_courses"] = [dict(r) for r in courses_rows]
    return d

def get_student_by_id(student_id: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM students WHERE student_id = ?", (student_id,)).fetchone()
    conn.close()
    if not row:
        return None
    d = dict(row)
    d["completed_courses"] = json.loads(d["completed_courses"])
    return d

def get_all_students() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM students").fetchall()
    conn.close()
    res = []
    for r in rows:
        d = dict(r)
        d["completed_courses"] = json.loads(d["completed_courses"])
        res.append(d)
    return res

def get_historical_bottlenecks() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT course_id, outcome, COUNT(*) as count
        FROM historical_outcomes
        GROUP BY course_id, outcome
        ORDER BY count DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]

if __name__ == "__main__":
    init_db(force=True)
