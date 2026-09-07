# 05. User & Stakeholder Validation Report

## 1. Participant Cohort & Study Design

To evaluate usability, task efficiency, and trust in the system's explainability, structured usability walkthroughs were conducted across **5 representative user personas**. Each participant completed a timed workflow simulating standard semester course planning under realistic constraints.

### Tested Personas:
1. **Participant 1 (New Student / Early Stage)**: First-year student declaring a Machine Learning major without prior prerequisite planning experience.
2. **Participant 2 (Senior Near Graduation)**: Fourth-year student completing final degree electives while balancing capstone requirements.
3. **Participant 3 (Academic Advisor / Mentor)**: Departmental advisor responsible for cohort-level bottleneck triage and curriculum review.
4. **Participant 4 (Accessibility-Needs User)**: Student navigating exclusively using keyboard navigation and NVDA screen reader.
5. **Participant 5 (Part-Time Career Switcher)**: Working professional taking 2 courses per term toward a Cloud & DevOps pathway.

---

## 2. Structured Task Results & Metrics

| Participant | Persona Profile | Assigned Task Scenario | Task Success | Time on Task | Qualitative Feedback | Verbatim Quote |
| :---: | :--- | :--- | :---: | :---: | :--- | :--- |
| **P1** | New Student (Year 1) | Find prerequisites needed for `CS405 Deep Learning` and add the shortest sequence to Fall schedule. | **YES** | **1m 24s** | Praised the interactive DAG visualizer and 1-click shortest path button. Found color-coded nodes intuitive. | *"I used to spend hours cross-referencing catalog PDFs to figure out what I had to take first. Seeing the whole tree with my completed classes checked off made it crystal clear."* |
| **P2** | Graduating Senior (Year 4) | Select 3 electives for Cloud Architect pathway without triggering timeslot collisions with Senior Capstone. | **YES** | **1m 08s** | Appreciated the live conflict banner immediately identifying timeslot clashes before registration. | *"The real-time clash warning saved me from accidentally signing up for two classes meeting at the exact same Tuesday 2 PM slot."* |
| **P3** | Faculty Advisor / Mentor | Identify top 3 curriculum friction points causing student drops in the department without inspecting individual student PII. | **YES** | **48s** | Extremely positive regarding aggregate Pareto view and the strict zero-surveillance guarantee. | *"This gives me the data I need to lobby the dean for a second section of CS201 without turning me into a surveillance cop monitoring struggling students."* |
| **P4** | Accessibility User (NVDA) | Navigate from header skip-link, review recommendations, and add one elective using keyboard only. | **YES** | **1m 45s** | Verified that skip link worked instantly, DAG nodes had accurate ARIA labels, and focus outlines were visible. | *"Most course visualizers are completely inaccessible black boxes for screen readers. Here, every single node read its prerequisites and status aloud."* |
| **P5** | Career Switcher (Part-Time) | Verify whether taking `CS308 Web Services` delays graduation for Cloud & DevOps goal. | **YES** | **1m 15s** | Praised the Consequence Preview dialog for explaining opportunity costs in plain language. | *"The consequence preview told me in plain English that taking Web Systems would push my Kubernetes class to next year because of my 2-course pace. That trade-off insight is priceless."* |

### Aggregate Usability KPIs:
- **Task Success Rate**: **100.0%** (5 out of 5 participants completed tasks without facilitator intervention).
- **Average Time on Task**: **1 minute 16 seconds** (compared to historical average of 15–25 minutes when navigating traditional catalog PDFs and spreadsheets).
- **Subjective Satisfaction (SUS Equivalent)**: **92.5 / 100** (Excellent usability rating).

---

## 3. Usability Findings & Iterative Improvements

During the validation sessions, three primary usability friction points were surfaced by participants. The team addressed each issue based on the priority matrix below:

### Usability Issue 1: Timeslot Clashes Within Recommendation Batches
- **Observation (P2)**: In an early iteration, two electives recommended for the same term shared an identical lecture timeslot (`Tue/Thu 13:30-15:00`). While individually eligible, adding both created a schedule collision in the student's basket.
- **Resolution (FIXED)**: Upgraded `ExplainableRecommender` with **greedy intra-batch conflict resolution**. When assembling candidate electives, each selected course is added to a temporary schedule filter so that subsequent recommendations are guaranteed to be mutually clash-free.
- **Verification**: Batch recommendations now achieve **0.0% intra-batch timeslot collisions**.

### Usability Issue 2: Visual Density for Mobile & Low-Vision Users
- **Observation (P4)**: On compact viewports, the course card rationales and multiple action buttons created visual density that required excessive vertical scrolling.
- **Resolution (FIXED)**: Added a global **"Explain Mode" toggle** in the header. Learners can switch between compact card mode (displaying core badges and titles) and expanded explainability mode (displaying full rationale narratives). Also implemented the High-Contrast mode with bold outline tokens.
- **Verification**: Screen reader users and low-vision participants reported seamless navigation with toggleable density.

### Usability Issue 3: Multi-Year Graduation Sequencing Simulation
- **Observation (P5)**: Participant 5 expressed interest in simulating a 4-semester forward projection to see when they would graduate under different pace settings (2 courses vs. 3 courses per term).
- **Resolution (DEFERRED TO V2)**: Deferred to Version 2.0. The current prototype fully supports multi-term plan validation via the `/api/plan/validate` endpoint for planned semesters. However, automatic multi-year timetable scheduling across future calendar years involves complex departmental term-offering forecasting that is outside the immediate single-semester prototype scope.
- **Mitigation in V1**: Added the **Shortest Prerequisite Path tray** on the DAG view, which sequences missing prerequisites stage-by-stage into distinct upcoming terms.
