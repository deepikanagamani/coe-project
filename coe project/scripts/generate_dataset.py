"""
Synthetic Dataset Generator for Prerequisite & Career-Consequence Explorer.
Generates deterministic, referentially-sound synthetic datasets for courses,
prerequisites, schedules, career pathways, student profiles, and historical outcomes.
Fixed seed ensures 100% reproducibility.
"""

import json
import csv
import random
import os
from typing import Dict, List, Any

SEED = 42
random.seed(SEED)

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)

# -------------------------------------------------------------------------
# 1. CAREER PATHWAYS (12 Pathways >= 10 required)
# -------------------------------------------------------------------------
PATHWAYS = [
    {
        "pathway_id": "PW_ML_ENG",
        "name": "Machine Learning Engineer",
        "description": "Design, deploy, and scale machine learning models into production distributed environments.",
        "primary_departments": ["CS", "AI", "MATH"],
        "target_competencies": ["Deep Learning", "Applied Statistics", "Model Serving", "MLOps"]
    },
    {
        "pathway_id": "PW_DATA_SCI",
        "name": "Data Scientist",
        "description": "Extract empirical insights and predictive models from large-scale structured and unstructured data.",
        "primary_departments": ["DATA", "MATH", "CS"],
        "target_competencies": ["Statistical Inference", "Data Wrangling", "Machine Learning", "Data Storytelling"]
    },
    {
        "pathway_id": "PW_CLOUD_DEVOPS",
        "name": "Cloud & DevOps Architect",
        "description": "Build automated infrastructure, distributed systems, CI/CD pipelines, and cloud platform resilience.",
        "primary_departments": ["CS", "SYS"],
        "target_competencies": ["Cloud Infrastructure", "Kubernetes", "Observability", "Site Reliability"]
    },
    {
        "pathway_id": "PW_CYBERSEC",
        "name": "Cybersecurity & Information Assurance",
        "description": "Protect computing assets, conduct vulnerability assessments, and implement zero-trust security postures.",
        "primary_departments": ["SEC", "CS", "NET"],
        "target_competencies": ["Cryptography", "Network Security", "Penetration Testing", "Threat Modeling"]
    },
    {
        "pathway_id": "PW_FULLSTACK",
        "name": "Full-Stack Software Engineer",
        "description": "Engineer modern web, mobile, and service-oriented applications from backend architecture to frontend interfaces.",
        "primary_departments": ["CS", "SE"],
        "target_competencies": ["Frontend Engineering", "API Design", "Database Modeling", "Distributed Architecture"]
    },
    {
        "pathway_id": "PW_PROD_MGR",
        "name": "Technical Product Manager",
        "description": "Define product strategy, technical roadmaps, metrics, and collaborate with engineering and design teams.",
        "primary_departments": ["PROD", "CS", "INFO"],
        "target_competencies": ["Product Discovery", "System Architecture for PMs", "Agile Execution", "User Analytics"]
    },
    {
        "pathway_id": "PW_SYS_ENG",
        "name": "Systems & Embedded Software Engineer",
        "description": "Program low-level hardware interfaces, real-time operating systems, and resource-constrained embedded systems.",
        "primary_departments": ["SYS", "CS", "EE"],
        "target_competencies": ["Kernel Architecture", "C/C++ Systems", "Real-Time OS", "Computer Architecture"]
    },
    {
        "pathway_id": "PW_AI_ETHICS",
        "name": "AI Safety & Responsible Tech Lead",
        "description": "Audit algorithmic fairness, establish regulatory compliance, and mitigate AI systemic bias.",
        "primary_departments": ["AI", "PHIL", "DATA"],
        "target_competencies": ["Algorithmic Fairness", "AI Governance", "Privacy-Preserving Computation", "Tech Policy"]
    },
    {
        "pathway_id": "PW_DATA_ENG",
        "name": "Data Systems Engineer",
        "description": "Architect high-throughput streaming pipelines, distributed data warehouses, and batch data processing engines.",
        "primary_departments": ["DATA", "CS", "SYS"],
        "target_competencies": ["Data Pipelines", "Lakehouse Architecture", "Stream Processing", "Distributed Query Engines"]
    },
    {
        "pathway_id": "PW_UX_ENG",
        "name": "Human-Computer Interaction & UX Engineer",
        "description": "Build accessible, responsive digital interfaces informed by cognitive psychology and usability engineering.",
        "primary_departments": ["HCI", "CS", "DES"],
        "target_competencies": ["Design Systems", "Web Accessibility (a11y)", "Usability Testing", "Interaction Design"]
    },
    {
        "pathway_id": "PW_FINTECH",
        "name": "FinTech & Quantitative Software Analyst",
        "description": "Develop algorithmic trading infrastructure, risk models, and blockchain transaction protocols.",
        "primary_departments": ["MATH", "CS", "FIN"],
        "target_competencies": ["Financial Modeling", "Low-Latency Code", "Stochastic Calculus", "Distributed Ledgers"]
    },
    {
        "pathway_id": "PW_BIOINFO",
        "name": "Computational Biology & Health Informatics",
        "description": "Apply algorithmic graph analysis and machine learning to genomic sequences and clinical healthcare records.",
        "primary_departments": ["BIO", "DATA", "CS"],
        "target_competencies": ["Genomic Data Processing", "Clinical NLP", "Bioinformatics Algorithms", "Biostatistics"]
    }
]

# -------------------------------------------------------------------------
# 2. COURSE CATALOG (68 Courses across 5 tiers >= 60 required)
# -------------------------------------------------------------------------
RAW_COURSES = [
    # Tier 1: Foundations (100-level)
    ("CS101", "Introduction to Computing & Python", "CS", 3, "Fundamental algorithmic thinking, data structures, and Python programming.", ["Fall", "Spring", "Summer"], "Introductory"),
    ("CS102", "Discrete Mathematics & Logic", "CS", 3, "Propositional logic, set theory, graph theory fundamentals, and proof techniques.", ["Fall", "Spring"], "Introductory"),
    ("MATH101", "Calculus I: Differential Foundations", "MATH", 4, "Limits, continuity, derivatives, and introduction to optimization.", ["Fall", "Spring", "Summer"], "Introductory"),
    ("DATA101", "Introduction to Data Science & Society", "DATA", 3, "Data exploration, tabular manipulation, ethical principles, and visualization.", ["Fall", "Spring"], "Introductory"),
    ("SYS101", "Digital Logic & Computer Organization", "SYS", 3, "Boolean algebra, combinational circuits, and von Neumann architecture.", ["Fall", "Spring"], "Introductory"),
    ("DES101", "Principles of Visual Design & Interface", "DES", 3, "Typography, color theory, layout hierarchy, and digital interface design.", ["Fall", "Spring"], "Introductory"),
    ("STAT101", "Descriptive & Applied Statistics", "MATH", 3, "Probability foundations, hypothesis testing, distributions, and variance.", ["Fall", "Spring", "Summer"], "Introductory"),

    # Tier 2: Core Fundamentals (200-level)
    ("CS201", "Data Structures & Algorithms", "CS", 4, "Trees, graphs, dynamic programming, asymptotic complexity analysis.", ["Fall", "Spring"], "Intermediate"),
    ("CS205", "Object-Oriented Design & Patterns", "CS", 3, "Polymorphism, SOLID principles, design patterns, and unit testing.", ["Fall", "Spring"], "Intermediate"),
    ("MATH201", "Multivariable Calculus", "MATH", 3, "Partial derivatives, multiple integrals, gradient descent vectors.", ["Fall", "Spring"], "Intermediate"),
    ("MATH205", "Linear Algebra for Computing", "MATH", 4, "Vector spaces, matrices, eigenvalues, eigenvectors, and SVD.", ["Fall", "Spring"], "Intermediate"),
    ("SYS201", "Computer Systems & C Programming", "SYS", 4, "Pointers, memory management, UNIX system calls, and assembly.", ["Fall", "Spring"], "Intermediate"),
    ("DATA201", "Relational Databases & SQL Modeling", "DATA", 3, "Relational calculus, SQL querying, indexing, and ACID transactions.", ["Fall", "Spring", "Summer"], "Intermediate"),
    ("WEB201", "Modern Client-Side Web Architecture", "SE", 3, "DOM manipulation, modern JavaScript/TypeScript, reactive UI components.", ["Fall", "Spring"], "Intermediate"),
    ("SEC201", "Fundamentals of Information Security", "SEC", 3, "Threat actors, symmetric/asymmetric encryption, authentication primitives.", ["Fall", "Spring"], "Intermediate"),
    ("STAT201", "Probability & Stochastic Processes", "MATH", 3, "Conditional probability, Bayes theorem, Markov chains, random walks.", ["Fall", "Spring"], "Intermediate"),
    ("PROD201", "Introduction to Product Management", "PROD", 3, "User research, product lifecycle, feature prioritization frameworks.", ["Fall", "Spring"], "Intermediate"),
    ("HCI201", "Foundations of Human-Computer Interaction", "HCI", 3, "Cognitive models, heuristic evaluation, and interaction principles.", ["Fall", "Spring"], "Intermediate"),

    # Tier 3: Intermediate Core & Electives (300-level)
    ("CS301", "Operating Systems Architecture", "SYS", 4, "Concurrency, process scheduling, virtual memory, filesystems, and deadlocks.", ["Fall", "Spring"], "Advanced"),
    ("CS303", "Computer Networks & Protocols", "SYS", 3, "OSI model, TCP/IP, routing algorithms, DNS, and TLS handshakes.", ["Fall", "Spring"], "Advanced"),
    ("CS305", "Introduction to Machine Learning", "AI", 4, "Supervised and unsupervised learning, regression, decision trees, neural nets.", ["Fall", "Spring"], "Advanced"),
    ("CS308", "Web Services & RESTful API Engineering", "SE", 3, "Microservice design, HTTP specifications, API caching, and middleware.", ["Fall", "Spring"], "Intermediate"),
    ("DATA301", "Data Warehousing & ETL Pipelines", "DATA", 3, "Star schema modeling, dbt transformations, batch workflows, and columnar stores.", ["Fall", "Spring"], "Intermediate"),
    ("DATA305", "Exploratory Data Analysis & Visualization", "DATA", 3, "Statistical graphics, interactive dashboards, narrative data presentation.", ["Fall", "Spring"], "Intermediate"),
    ("SYS305", "Parallel & Concurrent Programming", "SYS", 3, "Thread synchronization, race conditions, OpenMP, lock-free structures.", ["Fall", "Spring"], "Advanced"),
    ("SEC301", "Network Security & Applied Cryptography", "SEC", 3, "Zero-knowledge proofs, PKI, firewall architectures, and VPN protocols.", ["Fall", "Spring"], "Advanced"),
    ("SEC305", "Vulnerability Analysis & Secure Coding", "SEC", 3, "Buffer overflows, injection flaws, memory safety, and OWASP Top 10.", ["Fall", "Spring"], "Advanced"),
    ("AI301", "Natural Language Processing Foundations", "AI", 3, "Tokenization, n-grams, word embeddings, sequence models, and sentiment analysis.", ["Fall", "Spring"], "Advanced"),
    ("AI305", "Computer Vision Fundamentals", "AI", 3, "Image filtering, edge detection, convolutional feature extractors, optical flow.", ["Fall", "Spring"], "Advanced"),
    ("AI310", "Ethics & Governance in Artificial Intelligence", "AI", 3, "Sociotechnical systems, fairness metrics, auditing algorithmic systems.", ["Fall", "Spring"], "Intermediate"),
    ("CLOUD301", "Cloud Infrastructure & Virtualization", "SYS", 3, "IaaS, VPC networking, containers, Docker, and hypervisors.", ["Fall", "Spring"], "Intermediate"),
    ("SE301", "Software Testing & Quality Assurance", "SE", 3, "Integration testing, TDD, mutation testing, CI pipelines, and static analysis.", ["Fall", "Spring"], "Intermediate"),
    ("PROD301", "Data-Informed Technical Product Strategy", "PROD", 3, "A/B testing, North Star metrics, customer acquisition, and retention cohorts.", ["Fall", "Spring"], "Intermediate"),
    ("HCI301", "Accessible Web & Mobile Design (WCAG)", "HCI", 3, "Assistive technologies, ARIA specifications, screen-reader validation, color a11y.", ["Fall", "Spring"], "Intermediate"),
    ("FIN301", "Financial Computational Models", "FIN", 3, "Portfolio optimization, Black-Scholes model, Sharpe ratios, risk pricing.", ["Fall", "Spring"], "Advanced"),
    ("BIO301", "Computational Molecular Biology", "BIO", 3, "Sequence alignment, BLAST algorithms, phylogenetic trees, gene expression data.", ["Fall", "Spring"], "Advanced"),

    # Tier 4: Advanced Specializations (400-level)
    ("CS401", "Distributed Systems & Consensus", "SYS", 4, "Raft, Paxos, CAP theorem, eventual consistency, and distributed storage.", ["Fall", "Spring"], "Advanced"),
    ("CS405", "Deep Neural Networks & Representation Learning", "AI", 4, "Transformers, attention mechanisms, backprop optimization, autoencoders.", ["Fall", "Spring"], "Advanced"),
    ("CS410", "Production Machine Learning (MLOps)", "AI", 3, "Feature stores, model monitoring, drift detection, and automated retraining.", ["Fall", "Spring"], "Advanced"),
    ("CS415", "Distributed Cloud Native Architecture", "SYS", 3, "Kubernetes orchestration, service meshes, gRPC, and 12-factor microservices.", ["Fall", "Spring"], "Advanced"),
    ("CS420", "Compilers & Language Interpreters", "CS", 4, "Lexing, LL/LR parsing, abstract syntax trees, intermediate representations.", ["Fall"], "Advanced"),
    ("CS430", "Site Reliability Engineering & Observability", "SYS", 3, "SLIs/SLOs, distributed tracing, error budgets, incident post-mortems.", ["Spring"], "Advanced"),
    ("DATA401", "Large-Scale Streaming Systems (Kafka/Flink)", "DATA", 4, "Stream joins, sliding windows, exactly-once processing, event-driven pipes.", ["Fall", "Spring"], "Advanced"),
    ("DATA405", "Advanced Causal Inference & Econometrics", "DATA", 3, "Propensity score matching, instrumental variables, synthetic controls.", ["Spring"], "Advanced"),
    ("DATA410", "Data Governance & Compliance Architectures", "DATA", 3, "GDPR, data lineage, privacy budgets, and differential privacy.", ["Fall"], "Intermediate"),
    ("SEC401", "Cloud Security & Identity Architecture", "SEC", 3, "IAM policies, zero-trust microsegmentation, secrets management.", ["Fall"], "Advanced"),
    ("SEC405", "Penetration Testing & Red Teaming", "SEC", 4, "Exploit development, privilege escalation, lateral movement, MITRE ATT&CK.", ["Spring"], "Advanced"),
    ("AI401", "Large Language Model Engineering", "AI", 4, "Instruction tuning, RLHF, prompt chaining, vector databases, and RAG.", ["Fall", "Spring"], "Advanced"),
    ("AI405", "Reinforcement Learning & Decision Making", "AI", 4, "Markov decision processes, Q-learning, policy gradients, PPO, actor-critic.", ["Spring"], "Advanced"),
    ("AI410", "Responsible AI Auditing & Fairness Toolkits", "AI", 3, "Disparate impact analysis, counterfactual fairness, model cards.", ["Fall", "Spring"], "Intermediate"),
    ("SYS401", "Embedded Real-Time Operating Systems", "SYS", 4, "Interrupt handlers, deterministic scheduling, board bring-up, FreeRTOS.", ["Fall"], "Advanced"),
    ("SYS405", "Hardware-Software Co-Design & FPGAs", "SYS", 4, "Verilog HDL, memory hierarchies, custom accelerators, timing closure.", ["Spring"], "Advanced"),
    ("SE401", "Advanced Software System Design & Microfrontends", "SE", 3, "Domain-driven design, event sourcing, microfrontends, CQRS.", ["Fall", "Spring"], "Advanced"),
    ("SE405", "Mobile Systems Architecture (iOS & Android)", "SE", 3, "Native threading, offline-first sync, battery optimization, reactive state.", ["Fall", "Spring"], "Intermediate"),
    ("PROD401", "Technical Product Leadership & Capstone", "PROD", 4, "End-to-end product incubation, customer validation, executive reviews.", ["Spring"], "Advanced"),
    ("HCI401", "Advanced Interaction Techniques & AR/VR", "HCI", 4, "Spatial computing, haptics, gesture recognition, multimodal UI.", ["Spring"], "Advanced"),
    ("FIN401", "High-Frequency Trading & Low-Latency Engines", "FIN", 4, "Kernel bypass, order book matching, FPGA execution, FIX protocol.", ["Fall"], "Advanced"),
    ("BIO401", "Genomic Machine Learning & Drug Discovery", "BIO", 4, "Graph neural networks on molecules, protein folding models, biostats.", ["Spring"], "Advanced"),

    # Tier 5: Capstone & Advanced Seminars (500-level)
    ("CS500", "Master Senior Software Capstone", "CS", 4, "Cross-functional engineering project with external industry stakeholders.", ["Fall", "Spring"], "Advanced"),
    ("DATA500", "Applied Data Science Capstone", "DATA", 4, "End-to-end predictive analytics deliverable deployed to production.", ["Fall", "Spring"], "Advanced"),
    ("AI500", "Autonomous AI Systems Capstone", "AI", 4, "Full autonomous agent pipeline with ethical guardrails and safety bounds.", ["Fall", "Spring"], "Advanced"),
    ("SYS500", "High-Performance Systems Capstone", "SYS", 4, "Distributed compute cluster project delivering measurable throughput.", ["Fall", "Spring"], "Advanced"),
    ("SEC500", "Cybersecurity Defense & Incident Response Capstone", "SEC", 4, "Blue team incident mitigation and forensics investigation simulation.", ["Fall", "Spring"], "Advanced"),
    ("PROD500", "New Venture Product Launch Capstone", "PROD", 4, "Venture creation, beta cohort management, and live market deployment.", ["Fall", "Spring"], "Advanced"),
    ("HCI500", "Universal Accessibility Studio Capstone", "HCI", 4, "Public assistive technology deliverable certified against WCAG AAA.", ["Fall", "Spring"], "Advanced"),

    # Edge Case Seed Courses (Intentional curriculum anomalies)
    ("EDGE101", "Curriculum Evolution: Legacy Systems", "CS", 3, "Legacy procedural systems (intended for catalog drift tests).", ["Fall"], "Introductory"),
    ("EDGE201", "Circular Loop Anchor A", "CS", 3, "Diagnostic node for circular prerequisite graph detection.", ["Spring"], "Intermediate"),
    ("EDGE202", "Circular Loop Anchor B", "CS", 3, "Diagnostic reciprocal node for circular detection.", ["Spring"], "Intermediate")
]

COURSES = []
for c in RAW_COURSES:
    COURSES.append({
        "course_id": c[0],
        "title": c[1],
        "department": c[2],
        "credits": c[3],
        "description": c[4],
        "term_offered": c[5],
        "difficulty_level": c[6]
    })

# -------------------------------------------------------------------------
# 3. PREREQUISITES GRAPH
# -------------------------------------------------------------------------
# (course_id, prerequisite_course_id, requirement_type)
RAW_PREREQS = [
    # Tier 2 dependencies
    ("CS201", "CS101", "hard"),
    ("CS201", "CS102", "hard"),
    ("CS205", "CS101", "hard"),
    ("MATH201", "MATH101", "hard"),
    ("MATH205", "MATH101", "hard"),
    ("MATH205", "CS102", "recommended"),
    ("SYS201", "CS101", "hard"),
    ("SYS201", "SYS101", "hard"),
    ("DATA201", "CS101", "hard"),
    ("DATA201", "DATA101", "recommended"),
    ("WEB201", "CS101", "hard"),
    ("WEB201", "DES101", "recommended"),
    ("SEC201", "CS101", "hard"),
    ("STAT201", "STAT101", "hard"),
    ("STAT201", "MATH101", "hard"),
    ("PROD201", "DATA101", "recommended"),
    ("HCI201", "DES101", "hard"),
    ("HCI201", "CS101", "recommended"),

    # Tier 3 dependencies
    ("CS301", "SYS201", "hard"),
    ("CS301", "CS201", "hard"),
    ("CS303", "SYS201", "hard"),
    ("CS305", "CS201", "hard"),
    ("CS305", "MATH205", "hard"),
    ("CS305", "STAT201", "hard"),
    ("CS308", "WEB201", "hard"),
    ("CS308", "DATA201", "hard"),
    ("DATA301", "DATA201", "hard"),
    ("DATA301", "CS201", "hard"),
    ("DATA305", "DATA201", "hard"),
    ("DATA305", "STAT101", "hard"),
    ("SYS305", "SYS201", "hard"),
    ("SYS305", "CS201", "hard"),
    ("SEC301", "SEC201", "hard"),
    ("SEC301", "CS303", "hard"),
    ("SEC305", "SYS201", "hard"),
    ("SEC305", "CS201", "hard"),
    ("AI301", "CS201", "hard"),
    ("AI301", "MATH205", "recommended"),
    ("AI305", "CS201", "hard"),
    ("AI305", "MATH205", "hard"),
    ("AI310", "DATA101", "hard"),
    ("AI310", "CS101", "recommended"),
    ("CLOUD301", "SYS201", "hard"),
    ("CLOUD301", "CS303", "recommended"),
    ("SE301", "CS205", "hard"),
    ("PROD301", "PROD201", "hard"),
    ("PROD301", "DATA305", "recommended"),
    ("HCI301", "HCI201", "hard"),
    ("HCI301", "WEB201", "recommended"),
    ("FIN301", "MATH205", "hard"),
    ("FIN301", "STAT201", "hard"),
    ("BIO301", "CS201", "hard"),
    ("BIO301", "STAT201", "hard"),

    # Tier 4 dependencies
    ("CS401", "CS301", "hard"),
    ("CS401", "CS303", "hard"),
    ("CS405", "CS305", "hard"),
    ("CS405", "MATH201", "recommended"),
    ("CS410", "CS305", "hard"),
    ("CS410", "CLOUD301", "hard"),
    ("CS415", "CLOUD301", "hard"),
    ("CS415", "CS308", "hard"),
    ("CS420", "CS201", "hard"),
    ("CS420", "SYS201", "hard"),
    ("CS430", "CLOUD301", "hard"),
    ("CS430", "CS301", "recommended"),
    ("DATA401", "DATA301", "hard"),
    ("DATA401", "CS301", "recommended"),
    ("DATA405", "DATA305", "hard"),
    ("DATA405", "STAT201", "hard"),
    ("DATA410", "DATA301", "hard"),
    ("SEC401", "CLOUD301", "hard"),
    ("SEC401", "SEC301", "hard"),
    ("SEC405", "SEC305", "hard"),
    ("SEC405", "SEC301", "hard"),
    ("AI401", "CS405", "hard"),
    ("AI401", "AI301", "hard"),
    ("AI405", "CS305", "hard"),
    ("AI405", "STAT201", "hard"),
    ("AI410", "AI310", "hard"),
    ("AI410", "CS305", "recommended"),
    ("SYS401", "CS301", "hard"),
    ("SYS401", "SYS305", "hard"),
    ("SYS405", "SYS201", "hard"),
    ("SYS405", "SYS101", "hard"),
    ("SE401", "CS308", "hard"),
    ("SE401", "SE301", "hard"),
    ("SE405", "WEB201", "hard"),
    ("SE405", "CS205", "hard"),
    ("PROD401", "PROD301", "hard"),
    ("HCI401", "HCI301", "hard"),
    ("FIN401", "FIN301", "hard"),
    ("FIN401", "SYS305", "hard"),
    ("BIO401", "BIO301", "hard"),
    ("BIO401", "CS405", "recommended"),

    # Tier 5 Capstone dependencies
    ("CS500", "CS301", "hard"),
    ("CS500", "SE401", "hard"),
    ("DATA500", "DATA301", "hard"),
    ("DATA500", "DATA401", "hard"),
    ("AI500", "CS405", "hard"),
    ("AI500", "AI410", "hard"),
    ("SYS500", "CS401", "hard"),
    ("SEC500", "SEC405", "hard"),
    ("PROD500", "PROD401", "hard"),
    ("HCI500", "HCI401", "hard"),

    # Controlled Edge Case Seed: Intentional cycle in edge test courses
    ("EDGE201", "EDGE202", "hard"),
    ("EDGE202", "EDGE201", "hard")
]

PREREQUISITES = []
for p in RAW_PREREQS:
    PREREQUISITES.append({
        "course_id": p[0],
        "prerequisite_course_id": p[1],
        "requirement_type": p[2]
    })

# -------------------------------------------------------------------------
# 4. COURSE SCHEDULES & TIMESLOTS
# -------------------------------------------------------------------------
TIMESLOTS = [
    "Mon/Wed 08:30-10:00",
    "Mon/Wed 10:15-11:45",
    "Mon/Wed 13:00-14:30",
    "Mon/Wed 14:45-16:15",
    "Tue/Thu 09:00-10:30",
    "Tue/Thu 10:45-12:15",
    "Tue/Thu 13:30-15:00",
    "Tue/Thu 15:15-16:45",
    "Fri 09:00-12:00",
    "Fri 13:00-16:00"
]

ROOMS = ["Hall-A", "Hall-B", "Lab-101", "Lab-204", "Turing-301", "Hopper-102", "Lovelace-202", "Virtual-01"]

SCHEDULES = []
for c in COURSES:
    course_id = c["course_id"]
    for term in c["term_offered"]:
        # Deterministic slot assignment using hash of course + term
        slot_idx = (hash(course_id + term) + SEED) % len(TIMESLOTS)
        room_idx = (hash(course_id + term + "room") + SEED) % len(ROOMS)
        capacity = 45 if "Lab" in ROOMS[room_idx] else 120
        SCHEDULES.append({
            "course_id": course_id,
            "term": term,
            "day_time_slot": TIMESLOTS[slot_idx],
            "room": ROOMS[room_idx],
            "capacity": capacity
        })

# -------------------------------------------------------------------------
# 5. CAREER PATHWAYS CURRICULUM MAPPING (with weights and rationales)
# -------------------------------------------------------------------------
PATHWAY_COURSE_MAP = {
    "PW_ML_ENG": [
        ("CS101", 0.5, "Foundational programming required for ML scripts."),
        ("CS102", 0.5, "Discrete structures and graph representations."),
        ("MATH101", 0.6, "Differential calculus foundations for gradient descent."),
        ("STAT101", 0.6, "Introductory probability and empirical distributions."),
        ("CS201", 0.8, "Algorithms essential for complex tensor structures and graph processing."),
        ("MATH201", 0.7, "Multivariable calculus for vector derivatives and loss gradients."),
        ("MATH205", 0.9, "Vector algebra and matrix decomposition are mathematical core of deep learning."),
        ("STAT201", 0.9, "Probability theory necessary to understand generative models and loss distributions."),
        ("CS305", 1.0, "Core prerequisite covering classical machine learning paradigms."),
        ("CS405", 1.0, "State-of-the-art deep architectures and backpropagation optimization."),
        ("CS410", 0.9, "Production deployment, inference latency, and feature store architectures."),
        ("AI401", 0.8, "Modern generative foundation models and retrieval-augmented pipelines."),
        ("CLOUD301", 0.6, "Containerized model deployment in cloud environments."),
        ("AI500", 0.9, "Capstone verifying end-to-end ML engineering capability.")
    ],
    "PW_DATA_SCI": [
        ("DATA101", 0.8, "Introduction to exploratory analysis and data ethics."),
        ("STAT101", 0.8, "Foundational statistical hypothesis testing and descriptive inference."),
        ("CS101", 0.6, "Python programming for data wrangling scripts."),
        ("MATH101", 0.6, "Calculus for statistical density and continuous distributions."),
        ("DATA201", 0.9, "Relational data extraction, normalization, and complex querying."),
        ("CS201", 0.7, "Data structures for memory-efficient feature engineering."),
        ("MATH205", 0.8, "Linear algebra required for PCA and dimensional reduction."),
        ("STAT201", 0.9, "Bayesian estimation and stochastic distributions."),
        ("CS305", 0.9, "Predictive modeling and classification/regression algorithms."),
        ("DATA305", 0.9, "Statistical visual communication and exploratory charting."),
        ("DATA405", 0.9, "Causal inference and quasi-experimental econometric evaluation."),
        ("DATA500", 0.9, "Production capstone demonstrating predictive data science value.")
    ],
    "PW_CLOUD_DEVOPS": [
        ("CS101", 0.5, "Scripting for automation and cloud configuration."),
        ("SYS101", 0.6, "Computer organization and hardware architecture."),
        ("CS102", 0.5, "Logic gates and networking foundations."),
        ("SYS201", 0.8, "POSIX systems and memory interaction."),
        ("CS201", 0.7, "Data structures for distributed routing algorithms."),
        ("CS301", 0.9, "Process isolation, concurrency, and virtual memory underpinning containers."),
        ("CS303", 0.9, "Network routing, DNS, and TLS protocols essential for cloud routing."),
        ("CLOUD301", 1.0, "Core cloud infrastructure, virtual networks, and container engines."),
        ("CS401", 0.9, "Distributed consensus (Raft, Paxos) and cloud storage partitions."),
        ("CS415", 1.0, "Kubernetes microservices orchestration and cloud-native patterns."),
        ("CS430", 1.0, "Site reliability engineering, observability telemetry, and chaos engineering."),
        ("SEC401", 0.8, "Identity and access management (IAM) and cloud zero-trust."),
        ("SYS500", 0.9, "High-performance distributed cluster systems capstone.")
    ],
    "PW_CYBERSEC": [
        ("CS101", 0.5, "Scripting for automation and payload analysis."),
        ("SYS101", 0.6, "Logic architecture and hardware security foundations."),
        ("CS102", 0.5, "Discrete math and boolean logic for cryptosystems."),
        ("SYS201", 0.8, "Low-level memory layouts required to understand exploitation techniques."),
        ("CS201", 0.7, "Data structures for malware disassembly and graph modeling."),
        ("CS303", 0.9, "Network packets, firewalls, and cryptographic handshakes."),
        ("SEC201", 1.0, "Core security principles, threat modeling, and symmetric/asymmetric ciphers."),
        ("SEC301", 0.9, "Applied cryptography, public key infrastructure, and protocol security."),
        ("SEC305", 0.9, "Source code vulnerability assessment and memory corruption remediation."),
        ("SEC401", 0.9, "Cloud identity perimeter defense and infrastructure hardening."),
        ("SEC405", 1.0, "Penetration testing, exploitation methodologies, and red team defense."),
        ("SEC500", 1.0, "Defensive cyber range and forensic incident response capstone.")
    ],
    "PW_FULLSTACK": [
        ("CS101", 0.6, "Introductory programming logic."),
        ("CS102", 0.5, "Discrete mathematics and state machine logic."),
        ("DES101", 0.6, "Visual layout principles and typography for user interfaces."),
        ("DATA101", 0.5, "Data manipulation and storage concepts."),
        ("CS201", 0.8, "Data structures for fast client and server state processing."),
        ("CS205", 0.8, "Object-oriented design patterns for maintainable codebases."),
        ("DATA201", 0.8, "Relational schema modeling and transaction persistence."),
        ("WEB201", 1.0, "Modern reactive client architecture and browser rendering lifecycle."),
        ("CS308", 1.0, "REST/GraphQL API design and backend middleware engineering."),
        ("SE301", 0.8, "Automated unit, integration, and end-to-end regression testing."),
        ("SE401", 0.9, "Enterprise system architecture, CQRS, and domain-driven design."),
        ("CS500", 0.9, "Full-scale software engineering capstone.")
    ],
    "PW_PROD_MGR": [
        ("DATA101", 0.7, "Data literacy and quantitative decision framing."),
        ("DES101", 0.7, "Visual hierarchy and empathetic user experience foundations."),
        ("CS101", 0.6, "Technical literacy to converse with software engineering teams."),
        ("STAT101", 0.6, "Statistical hypothesis testing for feature experimentation."),
        ("PROD201", 1.0, "Core product lifecycle management, user research, and roadmapping."),
        ("DATA201", 0.7, "SQL querying to analyze user telemetry independently."),
        ("PROD301", 1.0, "A/B testing, cohort retention analytics, and metric architecture."),
        ("DATA305", 0.8, "Data storytelling for executive and customer presentations."),
        ("AI310", 0.8, "Responsible technology governance and regulatory compliance."),
        ("PROD401", 1.0, "End-to-end product incubation leadership and commercialization."),
        ("PROD500", 1.0, "Comprehensive venture launch capstone.")
    ],
    "PW_SYS_ENG": [
        ("SYS101", 0.8, "Hardware logic gates and register-transfer-level architecture."),
        ("CS101", 0.5, "Algorithmic foundation."),
        ("CS102", 0.5, "Boolean algebra and discrete logic circuits."),
        ("SYS201", 1.0, "C systems programming, pointers, and POSIX interface."),
        ("CS201", 0.8, "Memory-efficient data structures for constrained systems."),
        ("CS301", 1.0, "Operating system kernel internals and interrupt servicing."),
        ("SYS305", 0.9, "Hardware concurrency and lock-free thread synchronizations."),
        ("SYS401", 1.0, "Real-time operating systems (RTOS) and micro-controller scheduling."),
        ("SYS405", 0.9, "Hardware-software co-design and FPGA custom logic accelerators."),
        ("SYS500", 0.9, "High-performance systems engineering capstone.")
    ],
    "PW_AI_ETHICS": [
        ("DATA101", 0.8, "Societal impacts of data collection and privacy rights."),
        ("STAT101", 0.7, "Statistical foundations to understand population bias."),
        ("CS101", 0.6, "Algorithmic understanding for technical auditing."),
        ("DATA201", 0.6, "Data persistence and relational compliance schema."),
        ("AI310", 1.0, "Foundational AI ethics, governance models, and sociotechnical frameworks."),
        ("DATA301", 0.7, "Data lineage and ETL audit pipelines."),
        ("DATA410", 0.9, "Data compliance frameworks (GDPR) and differential privacy."),
        ("AI410", 1.0, "Algorithmic auditing toolkits, disparity metrics, and model cards."),
        ("CS305", 0.7, "Technical awareness of machine learning algorithms under audit."),
        ("AI500", 0.8, "Ethical autonomous systems capstone.")
    ],
    "PW_DATA_ENG": [
        ("CS101", 0.6, "Core programming for ETL automation."),
        ("CS102", 0.5, "Discrete graph structures for pipeline dependency DAGs."),
        ("DATA101", 0.6, "Introduction to exploratory data systems and tabular storage."),
        ("CS201", 0.8, "Tree and graph algorithms for DAG orchestrators."),
        ("DATA201", 1.0, "Relational databases, indexing, and SQL optimization."),
        ("SYS201", 0.7, "Systems programming and memory management for high-throughput batching."),
        ("DATA301", 1.0, "Data warehousing, star schemas, and batch pipelines."),
        ("CS301", 0.8, "Filesystem internals, buffer caching, and disk I/O management."),
        ("CLOUD301", 0.8, "Cloud compute and scalable storage layers (S3/blob)."),
        ("DATA401", 1.0, "Distributed streaming engines (Kafka/Flink) and real-time joins."),
        ("CS401", 0.9, "Distributed storage systems and consensus protocols."),
        ("DATA500", 0.9, "Enterprise data systems capstone.")
    ],
    "PW_UX_ENG": [
        ("DES101", 0.9, "Visual design, layout systems, and visual balance."),
        ("CS101", 0.6, "Coding foundations for dynamic interface logic."),
        ("HCI201", 1.0, "Cognitive interaction principles and usability heuristics."),
        ("WEB201", 1.0, "Interactive DOM components and responsive styling."),
        ("CS201", 0.7, "Data structures for rendering tree traversals."),
        ("CS205", 0.7, "Component-based object-oriented frontend patterns."),
        ("HCI301", 1.0, "Universal web accessibility (WCAG 2.1 AA/AAA) and assistive tools."),
        ("SE405", 0.8, "Mobile touch ergonomics and native UX behaviors."),
        ("HCI401", 0.9, "Spatial interfaces, AR/VR, and multimodal interaction."),
        ("HCI500", 1.0, "Universal accessibility studio capstone.")
    ],
    "PW_FINTECH": [
        ("MATH101", 0.7, "Calculus for continuous rate of return and derivatives."),
        ("STAT101", 0.7, "Descriptive statistics and variance measures."),
        ("CS101", 0.6, "Financial algorithmic logic and script execution."),
        ("SYS101", 0.5, "Hardware architecture and clock cycles for latency analysis."),
        ("MATH205", 0.8, "Linear algebra for covariance matrices."),
        ("STAT201", 0.9, "Stochastic processes and probability densities."),
        ("SYS201", 0.8, "Low-latency systems programming."),
        ("CS201", 0.7, "Order book queue and heap data structures."),
        ("FIN301", 1.0, "Computational finance models and portfolio optimization."),
        ("SYS305", 0.9, "Concurrent multi-core trade book processing."),
        ("FIN401", 1.0, "High-frequency trade execution and market microstructure."),
        ("CS401", 0.8, "Distributed ledgers and decentralized consensus.")
    ],
    "PW_BIOINFO": [
        ("CS101", 0.6, "Python scripting for FASTA and biological formats."),
        ("CS102", 0.5, "Discrete math for genomic sequence combinatorics."),
        ("STAT101", 0.7, "Biostatistical distributions and p-value significance."),
        ("CS201", 0.9, "Graph theory and string matching algorithms for DNA sequences."),
        ("STAT201", 0.8, "Biostatistical hypothesis testing and variance analysis."),
        ("DATA201", 0.7, "Relational databases for clinical trials and patient registries."),
        ("BIO301", 1.0, "Computational molecular biology algorithms (BLAST, Smith-Waterman)."),
        ("CS305", 0.8, "Machine learning for classification of biological phenotypes."),
        ("BIO401", 1.0, "Genomic machine learning, molecular GNNs, and drug discovery."),
        ("DATA301", 0.7, "Big data pipeline processing for high-throughput sequencing.")
    ]
}

# -------------------------------------------------------------------------
# 6. SYNTHETIC STUDENT PROFILES (320 Students >= 300 required)
# -------------------------------------------------------------------------
# Tier pools for realistic completed courses
TIER_1_COURSES = ["CS101", "CS102", "MATH101", "DATA101", "SYS101", "DES101", "STAT101"]
TIER_2_COURSES = ["CS201", "CS205", "MATH201", "MATH205", "SYS201", "DATA201", "WEB201", "SEC201", "STAT201", "PROD201", "HCI201"]
TIER_3_COURSES = ["CS301", "CS303", "CS305", "CS308", "DATA301", "DATA305", "SYS305", "SEC301", "SEC305", "AI301", "AI305", "AI310", "CLOUD301", "SE301", "PROD301", "HCI301", "FIN301", "BIO301"]

PATHWAY_IDS = [p["pathway_id"] for p in PATHWAYS]

STUDENTS = []
TOTAL_STUDENTS = 320

for i in range(1, TOTAL_STUDENTS + 1):
    student_id = f"STU_{i:04d}"
    
    # Progress distribution: 35% Year 1-2 (few completed), 45% Year 3 (intermediate), 20% Year 4 (near graduation)
    r = random.random()
    if r < 0.35:
        progress = "Year 1-2"
        # Has completed 1-3 Tier 1 courses
        k_t1 = random.randint(1, 3)
        completed = sorted(random.sample(TIER_1_COURSES, k_t1))
    elif r < 0.80:
        progress = "Year 3"
        # Completed 3-5 Tier 1 courses, 2-4 Tier 2 courses
        k_t1 = random.randint(3, 5)
        k_t2 = random.randint(2, 4)
        completed_t1 = random.sample(TIER_1_COURSES, k_t1)
        completed_t2 = random.sample(TIER_2_COURSES, k_t2)
        completed = sorted(list(set(completed_t1 + completed_t2)))
    else:
        progress = "Year 4"
        # Completed 5-6 Tier 1, 4-6 Tier 2, 2-4 Tier 3
        k_t1 = random.randint(5, 6)
        k_t2 = random.randint(4, 6)
        k_t3 = random.randint(2, 4)
        completed_t1 = random.sample(TIER_1_COURSES, k_t1)
        completed_t2 = random.sample(TIER_2_COURSES, k_t2)
        completed_t3 = random.sample(TIER_3_COURSES, k_t3)
        completed = sorted(list(set(completed_t1 + completed_t2 + completed_t3)))

    # Guarantee prerequisite validity in historical completions:
    # If CS201 is completed, ensure CS101 is also completed
    if "CS201" in completed and "CS101" not in completed:
        completed.append("CS101")
    if "SYS201" in completed and "SYS101" not in completed:
        completed.append("SYS101")
    completed = sorted(list(set(completed)))

    # Career goal assignment
    goal = random.choice(PATHWAY_IDS)

    # Edge cases seeded intentionally into student pool:
    # 1. Students 5 and 15: Missing stated goal (empty string / None)
    if i in [5, 15]:
        goal = ""
    # 2. Student 25: Stated goal invalid / deprecated pathway
    elif i == 25:
        goal = "PW_DEPRECATED_WEB3"

    max_courses = random.choice([2, 3, 4])
    lang = "es" if random.random() < 0.25 else "en"
    a11y = "screen_reader" if random.random() < 0.08 else ("high_contrast" if random.random() < 0.12 else "standard")

    STUDENTS.append({
        "student_id": student_id,
        "completed_courses": completed,
        "stated_goal_pathway": goal,
        "max_courses_per_term": max_courses,
        "term_progress": progress,
        "language_preference": lang,
        "accessibility_preference": a11y
    })

# -------------------------------------------------------------------------
# 7. HISTORICAL OUTCOMES LOG (1,000 Historical Enrollment Events)
# -------------------------------------------------------------------------
HISTORICAL_OUTCOMES = []
CONSEQUENCE_TYPES = ["completed_with_success", "prerequisite_violation_dropped", "schedule_conflict_dropped", "unaligned_pathway_switch"]

for i in range(1, 1001):
    event_id = f"EVT_{i:05d}"
    student_sample = random.choice(STUDENTS)
    course_sample = random.choice(COURSES)
    term_sample = random.choice(["Fall 2024", "Spring 2025", "Fall 2025", "Spring 2026"])
    
    # Realistic probability: 68% success, 16% prereq drop, 10% schedule clash, 6% goal misalignment
    p = random.random()
    if p < 0.68:
        outcome = "completed_with_success"
        notes = "Student satisfied all prerequisites and completed curriculum milestone."
    elif p < 0.84:
        outcome = "prerequisite_violation_dropped"
        notes = "Student enrolled without foundational course; dropped in Week 2."
    elif p < 0.94:
        outcome = "schedule_conflict_dropped"
        notes = "Overlapping timeslot with mandatory core course; dropped before census date."
    else:
        outcome = "unaligned_pathway_switch"
        notes = "Elective did not advance stated degree pathway; prompted major change."

    HISTORICAL_OUTCOMES.append({
        "event_id": event_id,
        "student_id": student_sample["student_id"],
        "course_id": course_sample["course_id"],
        "term": term_sample,
        "outcome": outcome,
        "notes": notes
    })


def main():
    print(f"Generating synthetic datasets in: {DATA_DIR}")

    # Write JSON files
    with open(os.path.join(DATA_DIR, "courses.json"), "w", encoding="utf-8") as f:
        json.dump(COURSES, f, indent=2)
    print(f"  -> Generated {len(COURSES)} courses in data/courses.json")

    with open(os.path.join(DATA_DIR, "prerequisites.json"), "w", encoding="utf-8") as f:
        json.dump(PREREQUISITES, f, indent=2)
    print(f"  -> Generated {len(PREREQUISITES)} prerequisite relationships in data/prerequisites.json")

    with open(os.path.join(DATA_DIR, "schedules.json"), "w", encoding="utf-8") as f:
        json.dump(SCHEDULES, f, indent=2)
    print(f"  -> Generated {len(SCHEDULES)} course schedule offerings in data/schedules.json")

    with open(os.path.join(DATA_DIR, "pathways.json"), "w", encoding="utf-8") as f:
        json.dump(PATHWAYS, f, indent=2)
    print(f"  -> Generated {len(PATHWAYS)} career pathways in data/pathways.json")

    # Serialize pathway course mappings
    pathway_mappings = []
    for pw_id, mapping in PATHWAY_COURSE_MAP.items():
        for course_id, weight, rationale in mapping:
            pathway_mappings.append({
                "pathway_id": pw_id,
                "course_id": course_id,
                "weight": weight,
                "rationale": rationale
            })
    with open(os.path.join(DATA_DIR, "pathway_courses.json"), "w", encoding="utf-8") as f:
        json.dump(pathway_mappings, f, indent=2)
    print(f"  -> Generated {len(pathway_mappings)} pathway-course associations in data/pathway_courses.json")

    with open(os.path.join(DATA_DIR, "students.json"), "w", encoding="utf-8") as f:
        json.dump(STUDENTS, f, indent=2)
    print(f"  -> Generated {len(STUDENTS)} synthetic student profiles in data/students.json")

    with open(os.path.join(DATA_DIR, "historical_outcomes.json"), "w", encoding="utf-8") as f:
        json.dump(HISTORICAL_OUTCOMES, f, indent=2)
    print(f"  -> Generated {len(HISTORICAL_OUTCOMES)} historical outcome logs in data/historical_outcomes.json")

    # Also export CSV files for easy tabular inspection
    def export_csv(filename: str, records: List[Dict[str, Any]]):
        if not records:
            return
        keys = list(records[0].keys())
        with open(os.path.join(DATA_DIR, filename), "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            for r in records:
                row = r.copy()
                for k, v in row.items():
                    if isinstance(v, list):
                        row[k] = ";".join(str(item) for item in v)
                writer.writerow(row)

    export_csv("courses.csv", COURSES)
    export_csv("prerequisites.csv", PREREQUISITES)
    export_csv("schedules.csv", SCHEDULES)
    export_csv("pathway_courses.csv", pathway_mappings)
    export_csv("students.csv", STUDENTS)
    export_csv("historical_outcomes.csv", HISTORICAL_OUTCOMES)
    print("  -> Exported CSV mirrors for all entities.")
    print("Dataset generation completed successfully!")


if __name__ == "__main__":
    main()
