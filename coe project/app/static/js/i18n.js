/**
 * Internationalization (i18n) Dictionary for Prerequisite & Career Explorer
 * Complete bilingual support: English ('en') and Spanish ('es')
 */

const I18N = {
  en: {
    app_title: "Prerequisite & Career-Consequence Explorer",
    app_tagline: "Transparent, explainable curriculum planning for self-directed learners",
    nav_planner: "Elective Planner",
    nav_dag: "Prerequisite DAG",
    nav_pathways: "Career Pathways",
    nav_mentor: "Mentor Insights (Cohort)",
    privacy_badge: "Zero-Surveillance Architecture",
    toggle_explain: "Explainability Mode",
    toggle_high_contrast: "High Contrast",
    theme_dark: "Dark Theme",
    theme_light: "Light Theme",
    
    // Student Persona Bar
    active_learner: "Active Learner Profile",
    select_student: "Switch Learner Profile...",
    target_career_goal: "Target Career Pathway",
    completed_courses_label: "Completed Courses",
    max_pace_label: "Term Pace Preference",
    credits_completed: "credits earned",
    status_year1: "Year 1-2 (Early Stage)",
    status_year3: "Year 3 (Core Stage)",
    status_year4: "Year 4 (Senior Stage)",
    
    // Planner Section
    planned_basket_title: "Proposed Semester Schedule",
    term_selector_label: "Select Term",
    validate_plan_btn: "Validate Schedule Integrity",
    clear_plan_btn: "Clear Schedule",
    no_courses_in_plan: "No courses currently in your schedule. Select recommended electives below or browse the catalog.",
    schedule_ok: "Schedule Fully Verified",
    schedule_ok_desc: "All prerequisites are satisfied, timeslots are clash-free, and pace is within your limit.",
    conflicts_detected: "Integrity Warnings Detected",
    
    // Recommendations Section
    recommended_electives_title: "Recommended Electives For You",
    recommended_subtitle: "Ranked by career alignment, verified prerequisite eligibility, and timeslot compatibility.",
    why_recommended_label: "Why this is recommended:",
    add_to_plan_btn: "Add to Schedule",
    why_not_btn: "Why NOT this?",
    preview_consequence_btn: "Preview Impact",
    alignment_advancing: "Directly Advancing Goal",
    alignment_supportive: "Supportive Competency",
    alignment_neutral: "General Credit (Neutral)",

    // Catalog Section
    catalog_title: "Course Catalog Explorer",
    search_placeholder: "Search by course code, title, or keywords...",
    filter_dept: "All Departments",
    filter_difficulty: "All Levels",
    inspect_dag_btn: "Explore Prerequisite DAG",
    
    // DAG Explorer
    dag_title: "Interactive Prerequisite Graph (DAG)",
    dag_subtitle: "Explore prerequisite trees, find the shortest path to graduation, and detect curriculum cycles.",
    select_target_course: "Select Target Elective:",
    node_completed: "Completed",
    node_eligible: "Eligible Now",
    node_locked: "Locked (Prereq Missing)",
    node_target: "Target Elective",
    shortest_path_title: "Shortest Prerequisite Path",
    add_shortest_path_btn: "Add Prerequisite Chain to Plan",
    cycle_detected_warning: "Critical: Circular dependency detected in course curriculum!",
    
    // Consequence Preview Modal
    modal_consequence_title: "Career & Schedule Consequence Preview",
    modal_consequence_subtitle: "Evaluating the downstream ripple effect of enrolling in",
    career_impact_heading: "Career Pathway Alignment",
    prereq_status_heading: "Prerequisite Verification",
    schedule_status_heading: "Timeslot & Capacity Verification",
    plain_narrative_heading: "Plain-Language Summary",
    confirm_add_anyway: "Add to Schedule Anyway",
    close_btn: "Close",

    // Why Not Modal
    why_not_title: "Why Not Take This Course?",
    why_not_subtitle: "System rationale explaining trade-offs or eligibility blocks for",
    
    // Mentor View
    mentor_title: "Mentor & Institutional Cohort Bottleneck Analytics",
    mentor_notice: "PRIVACY GUARANTEE: This dashboard aggregates cohort curriculum friction points anonymously. No individual student profiles, rankings, or risk flags are visible.",
    metric_students: "Total Learners Supported",
    metric_events: "Historical Registrations Analyzed",
    metric_top_block: "Primary Curriculum Bottleneck",
    tab_prereq_bottlenecks: "Top Prerequisite Drop-Offs",
    tab_schedule_clashes: "Top Timeslot Collisions",
    tab_dependency_gateways: "Key Gateway Courses",
    col_course: "Course",
    col_title: "Title",
    col_dept: "Department",
    col_count: "Affected Students",
    col_dependents: "Downstream Dependent Courses",
    
    // Accessibility & Alerts
    sr_alert_conflict: "Alert: Schedule conflict detected.",
    sr_plan_cleared: "Semester plan has been cleared.",
    sr_course_added: "Course added to your proposed plan."
  },
  
  es: {
    app_title: "Explorador de Prerrequisitos y Consecuencias de Carrera",
    app_tagline: "Planificación curricular transparente y explicable para estudiantes autodirigidos",
    nav_planner: "Planificador de Electivas",
    nav_dag: "Grafo DAG de Prerrequisitos",
    nav_pathways: "Trayectorias Profesionales",
    nav_mentor: "Panel de Mentoría (Cohorte)",
    privacy_badge: "Arquitectura Sin Vigilancia",
    toggle_explain: "Modo Explicativo",
    toggle_high_contrast: "Alto Contraste",
    theme_dark: "Tema Oscuro",
    theme_light: "Tema Claro",
    
    // Student Persona Bar
    active_learner: "Perfil del Estudiante Activo",
    select_student: "Cambiar Perfil de Estudiante...",
    target_career_goal: "Trayectoria Profesional Objetivo",
    completed_courses_label: "Cursos Completados",
    max_pace_label: "Preferencia de Carga por Término",
    credits_completed: "créditos obtenidos",
    status_year1: "Año 1-2 (Etapa Inicial)",
    status_year3: "Año 3 (Etapa Intermedia)",
    status_year4: "Año 4 (Etapa Final)",
    
    // Planner Section
    planned_basket_title: "Horario Semestral Propuesto",
    term_selector_label: "Seleccionar Término",
    validate_plan_btn: "Validar Integridad del Horario",
    clear_plan_btn: "Limpiar Horario",
    no_courses_in_plan: "No hay cursos en tu horario actual. Selecciona electivas recomendadas abajo o explora el catálogo.",
    schedule_ok: "Horario Totalmente Verificado",
    schedule_ok_desc: "Todos los prerrequisitos están cumplidos, sin colisiones de horarios y dentro de tu ritmo de créditos.",
    conflicts_detected: "Advertencias de Integridad Detectadas",
    
    // Recommendations Section
    recommended_electives_title: "Electivas Recomendadas Para Ti",
    recommended_subtitle: "Clasificadas por alineación profesional, elegibilidad de prerrequisitos y compatibilidad horaria.",
    why_recommended_label: "Por qué se recomienda:",
    add_to_plan_btn: "Agregar al Horario",
    why_not_btn: "¿Por qué NO esta?",
    preview_consequence_btn: "Previsualizar Impacto",
    alignment_advancing: "Avanza Directamente tu Meta",
    alignment_supportive: "Competencia de Apoyo",
    alignment_neutral: "Crédito General (Neutral)",

    // Catalog Section
    catalog_title: "Explorador del Catálogo de Cursos",
    search_placeholder: "Buscar por código, título o palabras clave...",
    filter_dept: "Todos los Departamentos",
    filter_difficulty: "Todos los Niveles",
    inspect_dag_btn: "Explorar Grafo DAG",
    
    // DAG Explorer
    dag_title: "Grafo Interactivo de Prerrequisitos (DAG)",
    dag_subtitle: "Explora árboles de requisitos, encuentra la ruta más corta a graduación y detecta ciclos curriculares.",
    select_target_course: "Seleccionar Curso Objetivo:",
    node_completed: "Completado",
    node_eligible: "Disponible Ahora",
    node_locked: "Bloqueado (Falta Prerrequisito)",
    node_target: "Electiva Objetivo",
    shortest_path_title: "Ruta Más Corta de Prerrequisitos",
    add_shortest_path_btn: "Agregar Cadena de Requisitos al Plan",
    cycle_detected_warning: "¡Crítico: Se detectó una dependencia circular en el currículo!",
    
    // Consequence Preview Modal
    modal_consequence_title: "Previsualización de Consecuencias Profesionales y Horarias",
    modal_consequence_subtitle: "Evaluando el efecto secundario de matricular",
    career_impact_heading: "Alineación con Trayectoria Profesional",
    prereq_status_heading: "Verificación de Prerrequisitos",
    schedule_status_heading: "Verificación de Horarios y Capacidad",
    plain_narrative_heading: "Resumen en Lenguaje Sencillo",
    confirm_add_anyway: "Agregar al Horario de Todos Modos",
    close_btn: "Cerrar",

    // Why Not Modal
    why_not_title: "¿Por Qué No Tomar Este Curso?",
    why_not_subtitle: "Razonamiento del sistema explicando compensaciones o bloqueos para",
    
    // Mentor View
    mentor_title: "Análisis Institucional de Cuellos de Botella de Cohorte",
    mentor_notice: "GARANTÍA DE PRIVACIDAD: Este panel agrega puntos de fricción curricular de forma anónima. No se muestran perfiles individuales ni banderas de riesgo.",
    metric_students: "Total de Estudiantes Apoyados",
    metric_events: "Matrículas Históricas Analizadas",
    metric_top_block: "Principal Cuello de Botella",
    tab_prereq_bottlenecks: "Mayores Abandonos por Prerrequisitos",
    tab_schedule_clashes: "Mayores Conflictos de Horario",
    tab_dependency_gateways: "Cursos Puerta de Enlace",
    col_course: "Curso",
    col_title: "Título",
    col_dept: "Departamento",
    col_count: "Estudiantes Afectados",
    col_dependents: "Cursos Dependientes Posteriores",
    
    // Accessibility & Alerts
    sr_alert_conflict: "Alerta: Conflicto de horario detectado.",
    sr_plan_cleared: "El plan semestral ha sido limpiado.",
    sr_course_added: "Curso agregado a tu plan propuesto."
  }
};

window.I18N = I18N;
