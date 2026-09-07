# Synthetic Dataset Documentation & Methodology

## 1. Dataset Overview & Purpose

This dataset is **entirely synthetic and locally generated** using fixed pseudo-random seeds (`SEED = 42`). It contains **no real personally identifiable information (PII)**, no proprietary course data, and no commercial learner telemetry.

The dataset serves as the benchmark foundation for:
1. Validating the **Prerequisite Graph Engine** (DAG pathfinding, cycle detection, topological sorting).
2. Benchmarking the **Schedule Conflict Engine** (timeslot overlaps and term progression feasibility).
3. Measuring the **Career-Consequence Explorer** against a baseline course selection model across 320 synthetic student personas.

---

## 2. Generation Methodology & Assumptions

### 2.1 Course Catalog & Prerequisite Hierarchy
- **Total Courses**: 68 courses spanning 5 tiers (Foundations 100-level to Advanced Capstones 500-level).
- **Departments**: Computer Science (`CS`), Data Science (`DATA`), Mathematics & Statistics (`MATH`), Systems Engineering (`SYS`), Cybersecurity (`SEC`), Artificial Intelligence (`AI`), Software Engineering (`SE`), Product Management (`PROD`), Human-Computer Interaction (`HCI`), Quantitative Finance (`FIN`), and Bioinformatics (`BIO`).
- **Prerequisite Topology**: Modeled as a Directed Acyclic Graph (DAG) with controlled branching depths (depth 1 to 4). Hard prerequisites are mandatory for enrollment; recommended prerequisites provide advisory context.
- **Intentional Anomaly Fixtures**:
  - `EDGE201` and `EDGE202`: Reciprocally dependent nodes forming a closed 2-cycle (`EDGE201 -> EDGE202 -> EDGE201`) to test cycle detection without crashing the primary curriculum.
  - `EDGE101`: Isolated legacy curriculum node designed to test catalog deprecation / drift scenarios.

### 2.2 Schedules & Timeslot Distribution
- Each course is offered across its designated terms (`Fall`, `Spring`, `Summer`).
- Each course section is deterministically mapped to one of 10 standard university timeslots (e.g., `Mon/Wed 08:30-10:00`, `Tue/Thu 13:30-15:00`, `Fri 09:00-12:00`) and a campus facility (`Hall-A`, `Lab-101`, `Turing-301`, etc.).
- Slot collisions occur naturally when students select courses mapped to identical day/time blocks.

### 2.3 Career Pathways & Relevance Weights
- **12 Defined Career Tracks**:
  - `PW_ML_ENG` (Machine Learning Engineer)
  - `PW_DATA_SCI` (Data Scientist)
  - `PW_CLOUD_DEVOPS` (Cloud & DevOps Architect)
  - `PW_CYBERSEC` (Cybersecurity & Info Assurance)
  - `PW_FULLSTACK` (Full-Stack Software Engineer)
  - `PW_PROD_MGR` (Technical Product Manager)
  - `PW_SYS_ENG` (Systems & Embedded Engineer)
  - `PW_AI_ETHICS` (AI Safety & Responsible Tech Lead)
  - `PW_DATA_ENG` (Data Systems Engineer)
  - `PW_UX_ENG` (HCI & Universal UX Engineer)
  - `PW_FINTECH` (FinTech & Quantitative Software Analyst)
  - `PW_BIOINFO` (Computational Biology & Health Informatics)
- Each pathway defines 7–10 supporting courses with:
  - **Relevance Weight** ($w \in [0.5, 1.0]$): Quantifies curriculum centrality.
  - **Plain-Language Rationale**: 1–2 sentences articulating why the course matters for that career.

### 2.4 Synthetic Student Cohort
- **Total Cohort Size**: 320 synthetic students.
- **Academic Progression Distribution**:
  - 35% Year 1–2 (Early stage; 1–3 introductory courses completed).
  - 45% Year 3 (Intermediate stage; 5–9 foundational courses completed).
  - 20% Year 4 (Senior stage; 11–16 courses completed, approaching capstone).
- **Referential Validity**: All historical completions satisfy prerequisite integrity (e.g., no student has completed `CS201` without `CS101`).
- **Intentional Edge Profiles**:
  - Students `STU_0005` and `STU_0015`: Blank stated goal (tests graceful fallback to general recommendations).
  - Student `STU_0025`: Deprecated goal `PW_DEPRECATED_WEB3` (tests unknown pathway handling).

---

## 3. Entity Schemas & File Manifest

| File | Format | Records | Schema Description |
| :--- | :--- | :--- | :--- |
| `data/courses.json` / `.csv` | JSON / CSV | 68 | `course_id, title, department, credits, description, term_offered[], difficulty_level` |
| `data/prerequisites.json` / `.csv` | JSON / CSV | 79 | `course_id, prerequisite_course_id, requirement_type` |
| `data/schedules.json` / `.csv` | JSON / CSV | 148 | `course_id, term, day_time_slot, room, capacity` |
| `data/pathways.json` | JSON | 12 | `pathway_id, name, description, primary_departments[], target_competencies[]` |
| `data/pathway_courses.json` / `.csv` | JSON / CSV | 108 | `pathway_id, course_id, weight, rationale` |
| `data/students.json` / `.csv` | JSON / CSV | 320 | `student_id, completed_courses[], stated_goal_pathway, max_courses_per_term, term_progress, language_preference, accessibility_preference` |
| `data/historical_outcomes.json` / `.csv` | JSON / CSV | 1,000 | `event_id, student_id, course_id, term, outcome, notes` |

---

## 4. Reproducibility Instructions

To regenerate and validate the entire dataset from scratch:

```powershell
# 1. Run generation script
python scripts/generate_dataset.py

# 2. Run integrity validation
python scripts/validate_dataset.py
```
