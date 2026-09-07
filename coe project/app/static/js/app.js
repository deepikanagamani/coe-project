/**
 * Core Application Controller for Prerequisite & Career-Consequence Explorer
 * Manages reactive UI state, REST API calls, plan validation, consequence previews,
 * localization, and accessibility.
 */

(function () {
  "use strict";

  // Application State
  const state = {
    students: [],
    activeStudent: null,
    courses: [],
    coursesMap: new Map(),
    pathways: [],
    pathwaysMap: new Map(),
    plannedCourses: [], // [{course_id, title, credits, department, day_time_slot}]
    currentTerm: "Fall",
    currentLang: "en",
    explainMode: true,
    highContrast: false,
    theme: "dark",
    dagVisualizer: null,
    pendingCandidateCourse: null
  };

  // DOM Elements Cache
  const els = {
    appTitle: document.getElementById("lbl-app-title"),
    privacyBadge: document.getElementById("lbl-privacy-badge"),
    selectStudent: document.getElementById("select-student"),
    valCareerGoal: document.getElementById("val-career-goal"),
    valProgressStage: document.getElementById("val-progress-stage"),
    valCompletedCourses: document.getElementById("val-completed-courses"),
    valMaxPace: document.getElementById("val-max-pace"),
    
    // Tabs
    tabBtnPlanner: document.getElementById("tab-btn-planner"),
    tabBtnDag: document.getElementById("tab-btn-dag"),
    tabBtnPathways: document.getElementById("tab-btn-pathways"),
    tabBtnMentor: document.getElementById("tab-btn-mentor"),
    panePlanner: document.getElementById("pane-planner"),
    paneDag: document.getElementById("pane-dag"),
    panePathways: document.getElementById("pane-pathways"),
    paneMentor: document.getElementById("pane-mentor"),
    
    // Controls
    btnToggleExplain: document.getElementById("btn-toggle-explain"),
    btnToggleA11y: document.getElementById("btn-toggle-a11y"),
    btnToggleLang: document.getElementById("btn-toggle-lang"),
    btnToggleTheme: document.getElementById("btn-toggle-theme"),
    lblLangIndicator: document.getElementById("lbl-lang-indicator"),
    lblExplain: document.getElementById("lbl-explain"),
    
    // Planner
    selectPlanTerm: document.getElementById("select-plan-term"),
    btnClearPlan: document.getElementById("btn-clear-plan"),
    planConflictBanner: document.getElementById("plan-conflict-banner"),
    bannerTitle: document.getElementById("banner-title"),
    bannerDesc: document.getElementById("banner-desc"),
    planBasketItems: document.getElementById("plan-basket-items"),
    valTotalPlanCredits: document.getElementById("val-total-plan-credits"),
    btnValidateFullPlan: document.getElementById("btn-validate-full-plan"),
    
    // Recommendations & Catalog
    recommendationsContainer: document.getElementById("recommendations-container"),
    recLatencyVal: document.getElementById("rec-latency-val"),
    catalogContainer: document.getElementById("catalog-container"),
    filterDept: document.getElementById("filter-dept"),
    inputCatalogSearch: document.getElementById("input-catalog-search"),
    
    // DAG
    selectDagTarget: document.getElementById("select-dag-target"),
    dagContainer: document.getElementById("dag-container"),
    dagStagesContainer: document.getElementById("dag-stages-container"),
    btnAddShortestPath: document.getElementById("btn-add-shortest-path"),
    btnDagZoomIn: document.getElementById("btn-dag-zoom-in"),
    btnDagZoomOut: document.getElementById("btn-dag-zoom-out"),
    btnDagReset: document.getElementById("btn-dag-reset"),
    
    // Pathways
    pathwaysContainer: document.getElementById("pathways-container"),
    
    // Mentor View
    mentorStatStudents: document.getElementById("mentor-stat-students"),
    mentorStatEvents: document.getElementById("mentor-stat-events"),
    mentorStatBottleneck: document.getElementById("mentor-stat-bottleneck"),
    mentorBottlenecksBody: document.getElementById("mentor-bottlenecks-body"),
    mentorGatewaysBody: document.getElementById("mentor-gateways-body"),
    
    // Modals
    modalConsequence: document.getElementById("modal-consequence"),
    consequenceModalBody: document.getElementById("consequence-modal-body"),
    btnCloseConsequence: document.getElementById("btn-close-consequence"),
    btnDismissConsequence: document.getElementById("btn-dismiss-consequence"),
    btnConfirmAddConsequence: document.getElementById("btn-confirm-add-consequence"),
    
    modalWhyNot: document.getElementById("modal-whynot"),
    whynotModalBody: document.getElementById("whynot-modal-body"),
    btnCloseWhyNot: document.getElementById("btn-close-whynot"),
    btnDismissWhyNot: document.getElementById("btn-dismiss-whynot"),
    
    // Live announcements
    srAnnouncements: document.getElementById("sr-announcements")
  };

  // Helper: Screen reader announcement
  function announce(msg) {
    if (els.srAnnouncements) {
      els.srAnnouncements.textContent = msg;
    }
  }

  // Translation helper
  function t(key) {
    const dict = window.I18N[state.currentLang] || window.I18N["en"];
    return dict[key] || key;
  }

  // API Call Wrapper with Latency Measurement
  async function api(endpoint, options = {}) {
    try {
      const resp = await fetch(endpoint, {
        headers: { "Content-Type": "application/json" },
        ...options
      });
      if (!resp.ok) {
        const err = await resp.json();
        throw new Error(err.detail || "API request failed");
      }
      return await resp.json();
    } catch (e) {
      console.error("API error on", endpoint, e);
      throw e;
    }
  }

  // Initialize App
  async function init() {
    state.dagVisualizer = new DAGVisualizer("dag-container", {
      onNodeClick: (node) => {
        openDAGCourseDetail(node.id);
      }
    });

    setupEventListeners();

    // Fetch initial datasets in parallel
    const [courses, pathways, students] = await Promise.all([
      api("/api/courses"),
      api("/api/pathways"),
      api("/api/students?limit=40")
    ]);

    state.courses = courses;
    courses.forEach(c => state.coursesMap.set(c.course_id, c));
    
    state.pathways = pathways;
    pathways.forEach(p => state.pathwaysMap.set(p.pathway_id, p));

    state.students = students;

    // Populate Student Select Dropdown
    els.selectStudent.innerHTML = students.map(s => `
      <option value="${s.student_id}">
        ${s.student_id} (${s.term_progress} • Goal: ${s.stated_goal_pathway || "Undeclared"})
      </option>
    `).join("");

    // Populate DAG Course Select Dropdown
    els.selectDagTarget.innerHTML = courses.map(c => `
      <option value="${c.course_id}">${c.course_id}: ${c.title}</option>
    `).join("");
    els.selectDagTarget.value = "CS405"; // Default target

    // Set initial active student
    if (students.length > 0) {
      setActiveStudent(students[0]);
    }

    renderCatalog();
    renderPathways();
    loadMentorBottlenecks();
  }

  // Student Switch Handler
  function setActiveStudent(student) {
    state.activeStudent = student;
    state.plannedCourses = []; // Reset planned courses on switch
    
    // Update persona pills
    const goalInfo = state.pathwaysMap.get(student.stated_goal_pathway);
    els.valCareerGoal.textContent = goalInfo ? goalInfo.name : (student.stated_goal_pathway || "Undeclared / General");
    els.valProgressStage.textContent = student.term_progress;
    els.valCompletedCourses.textContent = `${student.completed_courses.length} courses`;
    els.valMaxPace.textContent = `${student.max_courses_per_term} courses/term`;

    // Refresh recommendations, planner basket, and DAG
    loadRecommendations();
    renderPlannedBasket();
    loadDAG();
    announce(`Switched profile to ${student.student_id}`);
  }

  // Load Explainable Recommendations
  async function loadRecommendations() {
    if (!state.activeStudent) return;
    
    els.recommendationsContainer.innerHTML = `<div style="grid-column: 1/-1; text-align: center; padding: 20px;">Computing recommendations...</div>`;

    try {
      const payload = {
        student_id: state.activeStudent.student_id,
        completed_courses: state.activeStudent.completed_courses,
        stated_goal_pathway: state.activeStudent.stated_goal_pathway,
        term: state.currentTerm,
        current_planned_courses: state.plannedCourses.map(c => c.course_id),
        limit: 6
      };

      const res = await api("/api/recommendations", {
        method: "POST",
        body: JSON.stringify(payload)
      });

      els.recLatencyVal.textContent = `${res.latency_ms} ms`;
      renderRecommendations(res.recommendations);
    } catch (e) {
      els.recommendationsContainer.innerHTML = `<div style="grid-column: 1/-1; color: var(--status-danger-text);">Failed to compute recommendations.</div>`;
    }
  }

  // Render Recommendation Cards
  function renderRecommendations(recs) {
    if (!recs || recs.length === 0) {
      els.recommendationsContainer.innerHTML = `
        <div style="grid-column: 1/-1; padding: 24px; text-align: center; color: var(--text-muted);">
          No further elective recommendations for this term. All prerequisites for current level completed or pace limit reached.
        </div>
      `;
      return;
    }

    els.recommendationsContainer.innerHTML = recs.map(rec => {
      const alignmentClass = rec.pathway_alignment;
      let badgeText = t("alignment_neutral");
      if (alignmentClass === "advancing") badgeText = t("alignment_advancing");
      else if (alignmentClass === "supportive") badgeText = t("alignment_supportive");

      return `
        <div class="rec-card ${alignmentClass}">
          <div>
            <div class="rec-header">
              <div>
                <span class="course-code">${rec.course_id}</span>
                <h3 style="font-size: 0.95rem; font-weight: 700; margin-top: 2px;">${rec.title}</h3>
              </div>
              <span class="rec-badge ${alignmentClass}">
                ${alignmentClass === 'advancing' ? '★' : '•'} ${badgeText}
              </span>
            </div>
            <div class="course-meta" style="margin-top: 6px;">
              ${rec.department} • ${rec.credits} credits • ${rec.difficulty_level}
            </div>
          </div>

          ${state.explainMode ? `
            <div class="rec-explanation">
              <strong>${t("why_recommended_label")}</strong>
              <p style="margin-top: 4px;">${rec.explanation}</p>
            </div>
          ` : ''}

          <div class="rec-actions">
            <button class="btn-primary btn-add-rec" data-id="${rec.course_id}">
              <span>+</span> ${t("add_to_plan_btn")}
            </button>
            <button class="btn-secondary btn-preview-rec" data-id="${rec.course_id}">
              ${t("preview_consequence_btn")}
            </button>
            <button class="btn-secondary btn-whynot-rec" data-id="${rec.course_id}">
              ${t("why_not_btn")}
            </button>
          </div>
        </div>
      `;
    }).join("");

    // Attach button events
    els.recommendationsContainer.querySelectorAll(".btn-add-rec").forEach(btn => {
      btn.addEventListener("click", () => handleAddCourseWithPreview(btn.dataset.id));
    });
    els.recommendationsContainer.querySelectorAll(".btn-preview-rec").forEach(btn => {
      btn.addEventListener("click", () => openConsequencePreviewModal(btn.dataset.id));
    });
    els.recommendationsContainer.querySelectorAll(".btn-whynot-rec").forEach(btn => {
      btn.addEventListener("click", () => openWhyNotModal(btn.dataset.id));
    });
  }

  // Course Addition with Consequence Check
  async function handleAddCourseWithPreview(courseId) {
    const course = state.coursesMap.get(courseId);
    if (!course) return;

    // Run consequence preview first
    const preview = await api("/api/consequences/preview", {
      method: "POST",
      body: JSON.stringify({
        candidate_course_id: courseId,
        current_planned_courses: state.plannedCourses,
        completed_courses: state.activeStudent ? state.activeStudent.completed_courses : [],
        term: state.currentTerm,
        pathway_id: state.activeStudent ? state.activeStudent.stated_goal_pathway : null,
        max_courses_per_term: state.activeStudent ? state.activeStudent.max_courses_per_term : 3
      })
    });

    // If there is a blocking prerequisite or schedule conflict, display consequence modal first!
    if (!preview.can_proceed_safely) {
      openConsequencePreviewModal(courseId, preview);
      return;
    }

    // Otherwise safe to add directly
    addCourseToPlan(course);
  }

  function addCourseToPlan(course) {
    if (state.plannedCourses.some(c => c.course_id === course.course_id)) {
      alert(`${course.course_id} is already in your planned schedule.`);
      return;
    }

    state.plannedCourses.push(course);
    renderPlannedBasket();
    validateLivePlan();
    loadRecommendations();
    announce(`${course.course_id} added to schedule`);
  }

  function removeCourseFromPlan(courseId) {
    state.plannedCourses = state.plannedCourses.filter(c => c.course_id !== courseId);
    renderPlannedBasket();
    validateLivePlan();
    loadRecommendations();
    announce(`${courseId} removed from schedule`);
  }

  // Render Planned Basket
  function renderPlannedBasket() {
    if (state.plannedCourses.length === 0) {
      els.planBasketItems.innerHTML = `
        <div style="text-align: center; padding: 24px 12px; color: var(--text-muted); font-size: 0.85rem;">
          ${t("no_courses_in_plan")}
        </div>
      `;
      els.valTotalPlanCredits.textContent = "0";
      return;
    }

    const totalCredits = state.plannedCourses.reduce((sum, c) => sum + (c.credits || 3), 0);
    els.valTotalPlanCredits.textContent = totalCredits;

    els.planBasketItems.innerHTML = state.plannedCourses.map(c => `
      <div class="plan-item" role="listitem">
        <div class="plan-item-info">
          <div class="plan-item-header">
            <span class="course-code">${c.course_id}</span>
            <span class="course-title">${c.title}</span>
          </div>
          <div class="course-meta">
            ${c.department} • ${c.credits} credits • ${state.currentTerm}
          </div>
        </div>
        <button class="btn-remove btn-remove-plan" data-id="${c.course_id}" title="Remove course" aria-label="Remove ${c.course_id}">
          ✕
        </button>
      </div>
    `).join("");

    els.planBasketItems.querySelectorAll(".btn-remove-plan").forEach(btn => {
      btn.addEventListener("click", () => removeCourseFromPlan(btn.dataset.id));
    });
  }

  // Live Plan Validation
  async function validateLivePlan() {
    if (state.plannedCourses.length === 0) {
      els.planConflictBanner.className = "conflict-banner ok";
      els.bannerTitle.textContent = t("schedule_ok");
      els.bannerDesc.textContent = t("schedule_ok_desc");
      return;
    }

    try {
      const payload = {
        planned_terms: [
          {
            term: state.currentTerm,
            courses: state.plannedCourses
          }
        ],
        completed_courses: state.activeStudent ? state.activeStudent.completed_courses : [],
        max_courses_per_term: state.activeStudent ? state.activeStudent.max_courses_per_term : 3
      };

      const res = await api("/api/plan/validate", {
        method: "POST",
        body: JSON.stringify(payload)
      });

      if (res.is_valid) {
        els.planConflictBanner.className = "conflict-banner ok";
        els.bannerTitle.textContent = t("schedule_ok");
        els.bannerDesc.textContent = `${res.simulated_graduation_credits} credits verified with zero prerequisite or timeslot clashes.`;
      } else {
        const firstErr = res.conflicts[0];
        const isHard = firstErr.severity === "hard_error";
        els.planConflictBanner.className = isHard ? "conflict-banner error" : "conflict-banner warning";
        els.bannerTitle.textContent = isHard ? "Integrity Violation Detected" : "Pace / Capacity Notice";
        els.bannerDesc.textContent = firstErr.message;
        announce(`Schedule alert: ${firstErr.message}`);
      }
    } catch (e) {
      console.error("Plan validation error:", e);
    }
  }

  // Render Catalog Explorer
  function renderCatalog() {
    const q = (els.inputCatalogSearch.value || "").toLowerCase();
    const dept = els.filterDept.value;

    const filtered = state.courses.filter(c => {
      if (dept && c.department !== dept) return false;
      if (q) {
        return c.course_id.toLowerCase().includes(q) ||
               c.title.toLowerCase().includes(q) ||
               c.description.toLowerCase().includes(q);
      }
      return true;
    });

    els.catalogContainer.innerHTML = filtered.slice(0, 30).map(c => `
      <div class="rec-card">
        <div>
          <div class="rec-header">
            <div>
              <span class="course-code">${c.course_id}</span>
              <h3 style="font-size: 0.92rem; font-weight: 700;">${c.title}</h3>
            </div>
            <span class="course-meta">${c.credits} cr</span>
          </div>
          <p style="font-size: 0.8rem; color: var(--text-secondary); margin-top: 6px; line-height: 1.4;">
            ${c.description}
          </p>
        </div>
        <div class="rec-actions">
          <button class="btn-primary btn-add-cat" data-id="${c.course_id}">
            <span>+</span> ${t("add_to_plan_btn")}
          </button>
          <button class="btn-secondary btn-dag-cat" data-id="${c.course_id}">
            🌲 ${t("inspect_dag_btn")}
          </button>
          <button class="btn-secondary btn-whynot-cat" data-id="${c.course_id}">
            ❓ ${t("why_not_btn")}
          </button>
        </div>
      </div>
    `).join("");

    els.catalogContainer.querySelectorAll(".btn-add-cat").forEach(btn => {
      btn.addEventListener("click", () => handleAddCourseWithPreview(btn.dataset.id));
    });
    els.catalogContainer.querySelectorAll(".btn-dag-cat").forEach(btn => {
      btn.addEventListener("click", () => {
        els.selectDagTarget.value = btn.dataset.id;
        switchTab("dag");
        loadDAG();
      });
    });
    els.catalogContainer.querySelectorAll(".btn-whynot-cat").forEach(btn => {
      btn.addEventListener("click", () => openWhyNotModal(btn.dataset.id));
    });
  }

  // Load and Render Interactive DAG
  async function loadDAG() {
    const targetCourseId = els.selectDagTarget.value || "CS405";
    const studentId = state.activeStudent ? state.activeStudent.student_id : null;

    try {
      const dagData = await api(`/api/courses/${targetCourseId}/prerequisites?student_id=${studentId}`);
      state.dagVisualizer.render(dagData.dag);

      // Render Shortest Path Stages Tray
      renderShortestPathTray(dagData.shortest_prerequisite_path);
    } catch (e) {
      els.dagContainer.innerHTML = `<div class="empty-state" style="color: var(--status-danger-text); padding: 30px; text-align: center;">Error loading DAG for ${targetCourseId}.</div>`;
    }
  }

  function renderShortestPathTray(stages) {
    if (!stages || stages.length === 0) {
      els.dagStagesContainer.innerHTML = `
        <div style="color: var(--status-success-text); font-size: 0.85rem; padding: 10px 0;">
          ✓ All prerequisites are already completed! You are eligible to take this course immediately.
        </div>
      `;
      els.btnAddShortestPath.style.display = "none";
      return;
    }

    els.btnAddShortestPath.style.display = "inline-flex";

    els.dagStagesContainer.innerHTML = stages.map((stage, idx) => `
      <div class="stage-block">
        <div class="stage-title">Term ${idx + 1} Needed</div>
        ${stage.map(c => `
          <div style="font-size: 0.85rem; font-weight: 600; color: var(--text-primary); margin-bottom: 4px;">
            ${c.course_id}
            <div style="font-size: 0.75rem; font-weight: 400; color: var(--text-muted);">${c.title}</div>
          </div>
        `).join("")}
      </div>
      ${idx < stages.length - 1 ? '<span class="stage-arrow">→</span>' : ''}
    `).join("");

    // Save current stages to button for 1-click addition
    els.btnAddShortestPath.onclick = () => {
      const allStageCourses = stages.flatMap(s => s);
      let addedCount = 0;
      for (const c of allStageCourses) {
        const fullCourse = state.coursesMap.get(c.course_id);
        if (fullCourse && !state.plannedCourses.some(p => p.course_id === c.course_id)) {
          state.plannedCourses.push(fullCourse);
          addedCount++;
        }
      }
      renderPlannedBasket();
      validateLivePlan();
      switchTab("planner");
      announce(`Added ${addedCount} prerequisite courses to schedule`);
    };
  }

  // Career Pathways Browser
  function renderPathways() {
    els.pathwaysContainer.innerHTML = state.pathways.map(pw => `
      <div class="rec-card" style="border-left: 4px solid var(--accent-secondary);">
        <div>
          <h3 style="font-size: 1.05rem; font-weight: 700; color: var(--text-primary);">${pw.name}</h3>
          <p style="font-size: 0.82rem; color: var(--text-secondary); margin-top: 6px;">${pw.description}</p>
          <div style="display: flex; gap: 6px; flex-wrap: wrap; margin-top: 10px;">
            ${pw.target_competencies.map(comp => `
              <span style="font-size: 0.72rem; padding: 2px 8px; border-radius: 4px; background: rgba(139, 92, 246, 0.15); border: 1px solid rgba(139, 92, 246, 0.3); color: #c084fc;">
                ${comp}
              </span>
            `).join("")}
          </div>
        </div>
        <div class="rec-actions">
          <button class="btn-primary btn-set-goal" data-id="${pw.pathway_id}">
            🎯 Set as My Career Goal
          </button>
        </div>
      </div>
    `).join("");

    els.pathwaysContainer.querySelectorAll(".btn-set-goal").forEach(btn => {
      btn.addEventListener("click", () => {
        if (state.activeStudent) {
          state.activeStudent.stated_goal_pathway = btn.dataset.id;
          const pwInfo = state.pathwaysMap.get(btn.dataset.id);
          els.valCareerGoal.textContent = pwInfo ? pwInfo.name : btn.dataset.id;
          switchTab("planner");
          loadRecommendations();
          announce(`Updated career goal to ${pwInfo ? pwInfo.name : btn.dataset.id}`);
        }
      });
    });
  }

  // Mentor Bottlenecks Dashboard
  async function loadMentorBottlenecks() {
    try {
      const data = await api("/api/mentor/bottlenecks");
      els.mentorStatStudents.textContent = data.cohort_summary.total_students;
      els.mentorStatEvents.textContent = data.cohort_summary.total_enrollment_events_analyzed;
      els.mentorStatBottleneck.textContent = data.cohort_summary.top_bottleneck_course || "CS201";

      els.mentorBottlenecksBody.innerHTML = data.top_prerequisite_bottlenecks.map(b => `
        <tr>
          <td><strong style="color: var(--accent-primary);">${b.course_id}</strong></td>
          <td>${b.title}</td>
          <td>${b.department}</td>
          <td>${b.drop_count} students</td>
          <td>
            <span style="display: inline-block; padding: 2px 8px; border-radius: 4px; background: rgba(244, 63, 94, 0.15); color: #fda4af; font-size: 0.75rem; font-weight: 700;">
              High Friction
            </span>
          </td>
        </tr>
      `).join("");

      els.mentorGatewaysBody.innerHTML = data.top_downstream_dependency_gateways.map(g => `
        <tr>
          <td><strong style="color: var(--accent-cyan);">${g.course_id}</strong></td>
          <td>${g.title}</td>
          <td>${g.department}</td>
          <td><strong>${g.dependent_courses_count}</strong> advanced courses require this</td>
        </tr>
      `).join("");
    } catch (e) {
      console.error("Mentor bottlenecks fetch failed:", e);
    }
  }

  // Consequence Preview Modal
  async function openConsequencePreviewModal(courseId, preloadedPreview = null) {
    state.pendingCandidateCourse = state.coursesMap.get(courseId);
    
    let preview = preloadedPreview;
    if (!preview) {
      preview = await api("/api/consequences/preview", {
        method: "POST",
        body: JSON.stringify({
          candidate_course_id: courseId,
          current_planned_courses: state.plannedCourses,
          completed_courses: state.activeStudent ? state.activeStudent.completed_courses : [],
          term: state.currentTerm,
          pathway_id: state.activeStudent ? state.activeStudent.stated_goal_pathway : null,
          max_courses_per_term: state.activeStudent ? state.activeStudent.max_courses_per_term : 3
        })
      });
    }

    const course = state.pendingCandidateCourse;
    els.consequenceModalBody.innerHTML = `
      <div style="border-bottom: 1px solid var(--border-subtle); padding-bottom: 12px;">
        <span class="course-code" style="font-size: 1.1rem;">${course.course_id}</span>
        <h4 style="font-size: 1.1rem; font-weight: 700; margin-top: 2px;">${course.title}</h4>
        <p style="font-size: 0.85rem; color: var(--text-muted);">${course.department} • ${course.credits} credits</p>
      </div>

      <div class="consequence-check-item">
        <span style="font-size: 1.25rem;">${preview.has_prerequisite_block ? '⚠️' : '✓'}</span>
        <div>
          <strong>${t("prereq_status_heading")}</strong>
          <p style="font-size: 0.85rem; color: ${preview.has_prerequisite_block ? 'var(--status-warning-text)' : 'var(--status-success-text)'};">
            ${preview.has_prerequisite_block ? 'Missing foundational prerequisites!' : 'All hard prerequisites fully satisfied.'}
          </p>
        </div>
      </div>

      <div class="consequence-check-item">
        <span style="font-size: 1.25rem;">${preview.has_schedule_conflict ? '❌' : '✓'}</span>
        <div>
          <strong>${t("schedule_status_heading")}</strong>
          <p style="font-size: 0.85rem; color: ${preview.has_schedule_conflict ? 'var(--status-danger-text)' : 'var(--status-success-text)'};">
            ${preview.has_schedule_conflict ? preview.schedule_conflicts[0].message : 'Zero timeslot collisions with current semester schedule.'}
          </p>
        </div>
      </div>

      <div class="consequence-check-item">
        <span style="font-size: 1.25rem;">🎯</span>
        <div>
          <strong>${t("career_impact_heading")}</strong>
          <p style="font-size: 0.85rem; color: var(--text-secondary);">
            ${preview.pathway_alignment.rationale}
          </p>
        </div>
      </div>

      <div style="background: rgba(0,0,0,0.25); border-left: 3px solid var(--accent-primary); border-radius: 4px; padding: 12px; margin-top: 6px;">
        <strong>${t("plain_narrative_heading")}</strong>
        <p style="font-size: 0.85rem; color: var(--text-primary); margin-top: 4px;">
          ${preview.plain_language_narrative}
        </p>
      </div>
    `;

    els.modalConsequence.classList.add("active");
  }

  // Why Not Modal
  async function openWhyNotModal(courseId) {
    const course = state.coursesMap.get(courseId);
    if (!course) return;

    const res = await api("/api/why-not", {
      method: "POST",
      body: JSON.stringify({
        course_id: courseId,
        completed_courses: state.activeStudent ? state.activeStudent.completed_courses : [],
        current_planned_courses: state.plannedCourses.map(c => c.course_id),
        term: state.currentTerm,
        pathway_id: state.activeStudent ? state.activeStudent.stated_goal_pathway : null
      })
    });

    els.whynotModalBody.innerHTML = `
      <div style="border-bottom: 1px solid var(--border-subtle); padding-bottom: 12px;">
        <span class="course-code">${course.course_id}</span>
        <h4 style="font-size: 1.05rem; font-weight: 700;">${course.title}</h4>
      </div>

      <div style="display: flex; flex-direction: column; gap: 10px; margin-top: 12px;">
        ${res.reasons.map(r => `
          <div style="display: flex; gap: 10px; align-items: flex-start; padding: 10px; border-radius: 6px; background: var(--bg-card); border: 1px solid var(--border-subtle);">
            <span style="color: var(--accent-primary); font-size: 1rem;">ℹ️</span>
            <span style="font-size: 0.88rem; color: var(--text-secondary);">${r}</span>
          </div>
        `).join("")}
      </div>
    `;

    els.modalWhyNot.classList.add("active");
  }

  // Tab Switching
  function switchTab(tabKey) {
    const tabs = [
      { key: "planner", btn: els.tabBtnPlanner, pane: els.panePlanner },
      { key: "dag", btn: els.tabBtnDag, pane: els.paneDag },
      { key: "pathways", btn: els.tabBtnPathways, pane: els.panePathways },
      { key: "mentor", btn: els.tabBtnMentor, pane: els.paneMentor }
    ];

    tabs.forEach(t => {
      const isActive = t.key === tabKey;
      t.btn.classList.toggle("active", isActive);
      t.btn.setAttribute("aria-selected", isActive);
      t.pane.classList.toggle("active", isActive);
    });

    if (tabKey === "dag") {
      loadDAG();
    }
  }

  // Language Switcher
  function toggleLanguage() {
    state.currentLang = state.currentLang === "en" ? "es" : "en";
    els.lblLangIndicator.textContent = state.currentLang.toUpperCase();
    applyTranslations();
    renderCatalog();
    renderPlannedBasket();
    loadRecommendations();
    announce(`Language switched to ${state.currentLang === "en" ? "English" : "Spanish"}`);
  }

  function applyTranslations() {
    els.appTitle.textContent = t("app_title");
    els.tabBtnPlanner.textContent = t("nav_planner");
    els.tabBtnDag.textContent = t("nav_dag");
    els.tabBtnPathways.textContent = t("nav_pathways");
    els.tabBtnMentor.textContent = t("nav_mentor");
    document.getElementById("lbl-select-student").textContent = t("active_learner") + ":";
    document.getElementById("lbl-career-goal").textContent = t("target_career_goal") + ":";
    document.getElementById("lbl-completed-count").textContent = t("completed_courses_label") + ":";
    document.getElementById("lbl-pace-pref").textContent = t("max_pace_label") + ":";
    document.getElementById("lbl-basket-title").textContent = t("planned_basket_title");
    document.getElementById("lbl-recs-title").textContent = t("recommended_electives_title");
    document.getElementById("lbl-recs-desc").textContent = t("recommended_subtitle");
    document.getElementById("lbl-catalog-title").textContent = t("catalog_title");
    document.getElementById("lbl-dag-header").textContent = t("dag_title");
    document.getElementById("lbl-dag-subheader").textContent = t("dag_subtitle");
  }

  // Setup Event Listeners
  function setupEventListeners() {
    // Navigation Tabs
    els.tabBtnPlanner.addEventListener("click", () => switchTab("planner"));
    els.tabBtnDag.addEventListener("click", () => switchTab("dag"));
    els.tabBtnPathways.addEventListener("click", () => switchTab("pathways"));
    els.tabBtnMentor.addEventListener("click", () => switchTab("mentor"));

    // Student Switch
    els.selectStudent.addEventListener("change", (e) => {
      const student = state.students.find(s => s.student_id === e.target.value);
      if (student) setActiveStudent(student);
    });

    // Term Switch
    els.selectPlanTerm.addEventListener("change", (e) => {
      state.currentTerm = e.target.value;
      loadRecommendations();
      validateLivePlan();
    });

    // Clear Basket
    els.btnClearPlan.addEventListener("click", () => {
      state.plannedCourses = [];
      renderPlannedBasket();
      validateLivePlan();
      loadRecommendations();
      announce("Schedule cleared");
    });

    // Validate Full Plan
    els.btnValidateFullPlan.addEventListener("click", () => {
      validateLivePlan();
      alert("Plan validation executed. See the status banner above for results.");
    });

    // DAG Target Course Switch
    els.selectDagTarget.addEventListener("change", () => loadDAG());

    // DAG Zoom Controls
    els.btnDagZoomIn.addEventListener("click", () => state.dagVisualizer && state.dagVisualizer.zoomIn());
    els.btnDagZoomOut.addEventListener("click", () => state.dagVisualizer && state.dagVisualizer.zoomOut());
    els.btnDagReset.addEventListener("click", () => state.dagVisualizer && state.dagVisualizer.resetZoom());

    // Catalog Search & Filter
    els.inputCatalogSearch.addEventListener("input", () => renderCatalog());
    els.filterDept.addEventListener("change", () => renderCatalog());

    // Settings & A11y Toggles
    els.btnToggleLang.addEventListener("click", toggleLanguage);

    els.btnToggleExplain.addEventListener("click", () => {
      state.explainMode = !state.explainMode;
      els.lblExplain.textContent = `Explain: ${state.explainMode ? 'ON' : 'OFF'}`;
      els.btnToggleExplain.setAttribute("aria-pressed", state.explainMode);
      loadRecommendations();
    });

    els.btnToggleA11y.addEventListener("click", () => {
      state.highContrast = !state.highContrast;
      document.body.classList.toggle("high-contrast", state.highContrast);
      els.btnToggleA11y.setAttribute("aria-pressed", state.highContrast);
    });

    els.btnToggleTheme.addEventListener("click", () => {
      state.theme = state.theme === "dark" ? "light" : "dark";
      document.body.classList.toggle("light-theme", state.theme === "light");
      document.getElementById("icon-theme").textContent = state.theme === "dark" ? "🌙" : "☀️";
    });

    // Modals
    els.btnCloseConsequence.addEventListener("click", () => els.modalConsequence.classList.remove("active"));
    els.btnDismissConsequence.addEventListener("click", () => els.modalConsequence.classList.remove("active"));
    els.btnConfirmAddConsequence.addEventListener("click", () => {
      if (state.pendingCandidateCourse) {
        addCourseToPlan(state.pendingCandidateCourse);
        els.modalConsequence.classList.remove("active");
      }
    });

    els.btnCloseWhyNot.addEventListener("click", () => els.modalWhyNot.classList.remove("active"));
    els.btnDismissWhyNot.addEventListener("click", () => els.modalWhyNot.classList.remove("active"));
  }

  // Boot the app
  window.addEventListener("DOMContentLoaded", init);

})();
