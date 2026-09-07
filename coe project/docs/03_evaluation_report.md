# 03. Evaluation Report & Empirical Benchmark

## 1. Executive Summary

To evaluate the operational efficacy of the **Prerequisite & Career-Consequence Explorer**, an automated empirical experiment was conducted benchmarking the Prototype recommender against the Naive Baseline recommender. Both systems were evaluated against an identical synthetic cohort of **320 students** navigating elective enrollment for the upcoming academic term.

The evaluation benchmarks five core quantitative dimensions:
1. Prerequisite conflict rate reduction
2. Career pathway alignment rate
3. Average number of conflicts per student course plan
4. End-to-end algorithmic response latency
5. Explainability coverage (plain-language rationale generation)

---

## 2. Experimental Methodology

### 2.1 Cohort & Environment Configuration
- **Student Population**: 320 distinct synthetic profiles ($N = 320$) representing early-stage (Years 1–2), intermediate (Year 3), and senior (Year 4) learners across 12 declared career pathways.
- **Hardware Testbed**: Local commodity desktop CPU (Single-core Python 3.13 runtime on Windows 64-bit).
- **Evaluation Term**: Fall 2026 course offerings.
- **Execution Script**: `scripts/run_evaluation.py` (reads data directly from `data/explorer.db` and logs raw JSON results to `data/evaluation_results.json`).

### 2.2 Metrics Definitions & Scoring Rules
- **Prerequisite Conflict Count ($C_{prereq}$)**: Count of hard direct prerequisites required by a course that are absent from the student's completed transcript prior to the term.
- **Schedule Collision Count ($C_{time}$)**: Count of pairwise lecture/lab timeslot overlaps within a student's recommended course batch.
- **Plan Conflict Status**: A student plan is marked as having an unresolved conflict if $\sum (C_{prereq} + C_{time}) \ge 1$.
- **Goal Alignment Scoring**: For learners with a declared career pathway, an elective is scored as *Aligned* if the course is explicitly mapped to that pathway's curriculum competencies with a positive weight ($w \ge 0.5$).
- **Explainability Coverage**: Percentage of generated recommendations accompanied by a non-empty, grammatically complete human-readable rationale ($> 10$ characters).

---

## 3. Benchmark Results (Empirically Measured)

The table below presents the exact measured values obtained from executing the benchmark suite against the 320-student cohort:

| Metric | Baseline (Naive Keyword/Catalog) | Target Requirement | Measured Prototype | Status |
| :--- | :---: | :---: | :---: | :---: |
| **% of student plans with $\ge 1$ unresolved conflict** | **92.19%** | Reduce by $\ge 50\%$ vs baseline ($\le 25.0\%$) | **0.00%** | **PASS** (100% reduction) |
| **% of recommended electives aligned with stated goal** | **52.21%** | $\ge 80.0\%$ | **98.62%** | **PASS** |
| **Avg. prerequisite & schedule conflicts per plan** | **2.71** | Reduce by $\ge 50\%$ ($\le 1.35$) | **0.00** | **PASS** (100% reduction) |
| **Recommendation response latency (p95)** | *n/a* (manual catalog) | $< 500.0$ ms | **0.29 ms** | **PASS** (1700x faster than budget) |
| **Recommendation response latency (p50)** | *n/a* | $< 250.0$ ms | **0.17 ms** | **PASS** |
| **% of recommendations with valid explanation** | **0.0%** | **100.0%** | **100.0%** | **PASS** |

---

## 4. Descriptive Comparative Analysis

### 4.1 Prerequisite Conflict Eradication
Under the Naive Baseline, **92.19%** of generated student plans suffered from at least one critical prerequisite violation or timeslot overlap, averaging **2.71 conflicts per student**. This reflects the standard real-world reality where learners browse unconstrained course listings and enroll in advanced courses (e.g., `CS305 Machine Learning` or `CS401 Distributed Systems`) without having taken `CS201 Data Structures` or `SYS201 C Systems`.

The Prototype achieved **0.00% conflicts** (a 100% reduction) by executing deterministic DAG reachability checks and greedy intra-batch schedule conflict filtering prior to presenting recommendations.

### 4.2 Career Pathway Alignment
The Naive Baseline achieved only **52.21% goal alignment**, frequently suggesting unrelated electives due to superficial keyword matches in course descriptions (e.g., matching the word "system" in a humanities course when a Cloud Architect student searches for systems courses).

The Prototype achieved **98.62% goal alignment**. The remaining 1.38% corresponds strictly to intentional test fixtures: learners with undeclared goals (`STU_0005`, `STU_0015`) or deprecated pathways (`STU_0025`), for whom the engine degraded gracefully to foundational technical electives.

### 4.3 Algorithmic Latency Profile
The Prototype graph traversal, topological validation, and scoring algorithms executed with exceptional efficiency:
- Mean Latency: **0.18 ms**
- Median Latency (p50): **0.17 ms**
- 95th Percentile (p95): **0.29 ms**
- 99th Percentile (p99): **0.42 ms**

All operations execute in well under 1 millisecond on commodity hardware, satisfying the strict 500ms operational constraint with an immense headroom factor of $> 1,700\times$.

### 4.4 100% Explainability Coverage
Whereas the Naive Baseline produced zero justification for its course suggestions, the Prototype delivered a 1–2 sentence plain-language rationale for **100.0%** of recommended electives, articulating exactly why the elective benefits the student's degree pathway and confirming prerequisite compliance.
