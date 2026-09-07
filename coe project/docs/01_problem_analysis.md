# 01. Problem Analysis & System Framing

## 1. Executive Summary

Online learning platforms and higher education institutions face an asymmetric operational challenge: student enrollments scale to tens of thousands of active learners, whereas qualified human academic mentors and advisors scale linearly or remain fixed at single-digit staffing levels. 

In traditional elective selection workflows, learners make self-directed course selections from dense, disconnected course catalogs without dynamic structural guidance. This results in three pervasive systemic failures:
1. **Hidden Prerequisite Violations**: Students select advanced or cross-disciplinary electives unaware that foundational prerequisites are missing or sequenced out of order.
2. **Career Pathway Drift & Opaque Consequences**: Students pick electives based on popularity or immediate interest without understanding how those choices either open or permanently foreclose future professional pathways (e.g., Data Science, Distributed Systems, Product Engineering).
3. **Schedule & Term Deadlocks**: Students enroll in courses with conflicting lecture/lab timeslots or select prerequisite chains that cannot be completed within their remaining degree or certificate timeline.

The **Prerequisite & Career-Consequence Explorer** is designed to solve this at scale through deterministic graph traversal, scheduling conflict verification, and explainable pathway mapping. The system operates as a transparent self-service tool rather than an opaque black-box recommender, prioritizing student agency, privacy, and explainability.

---

## 2. Stakeholder Ecosystem Analysis

| Stakeholder Persona | Core Objectives | Current Pain Points | System Value Proposition |
| :--- | :--- | :--- | :--- |
| **Learner (e.g., Career Switcher, Continuing Student)** | - Complete degree/certificate on time.<br/>- Maximize career readiness.<br/>- Avoid schedule collisions. | - Catalog descriptions lack prerequisite graph awareness.<br/>- Course selection interface gives no early feedback on schedule or pathway deadlocks.<br/>- Fear of delayed graduation. | - Interactive prerequisite DAG with instant pathfinding.<br/>- "Consequence preview" before enrollment.<br/>- Clear, plain-language "Why" and "Why Not" explanations for every recommendation. |
| **Academic Mentor / Advisor** | - Ensure students meet core graduation requirements.<br/>- Support high-need students rather than answering repetitive catalog queries. | - Overwhelmed by routine prerequisite checks and scheduling conflict escalations.<br/>- No time for deep career mentorship. | - Routine validation is offloaded to self-service student tooling.<br/>- Mentor view highlights cohort-level bottlenecks without administrative burden. |
| **Platform Administrator / Curriculum Designer** | - Optimize course capacity and term scheduling.<br/>- Identify curriculum bottlenecks and high-friction prerequisite rules. | - Lack of visibility into which courses cause aggregate prerequisite drop-offs or scheduling deadlocks. | - Anonymized aggregate dashboard exposing bottleneck courses, unmet demand, and structural friction points. |

---

## 3. Hard Constraints & Architectural Invariants

The design and implementation of the Explorer are governed by four non-negotiable architectural constraints:

### 3.1 Non-Punitive & Privacy-Preserving Operation
- **Zero Surveillance**: The system does not maintain behavioral scores, engagement drop-off tracking, or hidden "at-risk" flags.
- **Local Agency**: Prerequisite violations and schedule collisions are visible solely to the student navigating their plan. Mentors and administrators cannot access individual student planning sessions unless a student explicitly exports and shares their plan for an advising session.
- **No Commercial Exploitation**: Synthetic and real student profiles remain strictly partitioned; no data is shared or sold to external third parties.

### 3.2 Computational & Infrastructure Efficiency
- **Zero Cloud / Zero Paid API Dependencies**: The platform executes entirely on modest local infrastructure using a lightweight relational SQLite database and an in-memory graph engine.
- **Sub-500ms Query Latency**: All prerequisite DAG pathfinding, schedule conflict scans, and career pathway scoring algorithms execute in under 500ms on a standard single-core commodity machine.
- **Deterministic Explainability**: Recommendations are derived from explicit rule-based graph walks and weighted pathway mappings. No probabilistic black-box ML models are used for elective approvals, ensuring 100% human-auditable rationales.

### 3.3 Universal Accessibility (WCAG 2.1 AA)
- Full keyboard navigation with explicit focus styling across all interactive elements.
- Dual visual encoding: all conflict, success, and warning states pair color styling with unambiguous iconography and semantic ARIA text (no color-only signaling).
- High-contrast color palette meeting minimum 4.5:1 text contrast and 3:1 graphical component contrast.
- End-to-end multi-language localization (English and Spanish) without unlocalized fallback strings.

---

## 4. Measurable Success Criteria & Target KPIs

| Metric | Current State (Baseline / Manual) | Target Threshold (Explorer Prototype) | Verification Method |
| :--- | :--- | :--- | :--- |
| **Unresolved Prerequisite Conflicts** | > 45% of naive elective plans contain >= 1 missing prerequisite. | **< 5%** (reduction of >= 50% vs baseline). | Automated evaluation script running 300 synthetic student profiles. |
| **Goal Pathway Alignment** | < 35% of chosen electives materially advance the student's stated career goal. | **>= 80%** of recommended electives align with goal pathway. | Pathway relevance scoring across 10 career tracks. |
| **Average Prerequisite Conflicts per Plan** | > 1.2 conflicts per student plan. | **< 0.3 conflicts per plan** (>= 50% reduction). | Aggregate conflict counter across simulated student cohort. |
| **Recommendation Engine Latency** | Manual catalog browsing: 10–30 minutes per student. | **< 500ms** end-to-end API response time. | Automated performance benchmarks (p50, p95, p99). |
| **Explainability Coverage** | 0% (standard course catalog provides zero automated rationale). | **100%** of recommendations include valid plain-language rationale. | String validation & semantic clarity audit across test sample. |
| **Accessibility Compliance** | Standard web forms frequently fail WCAG AA contrast and keyboard traps. | **100% pass** on WCAG 2.1 AA automated and manual audit. | Accessibility report and screen-reader keyboard audit. |
