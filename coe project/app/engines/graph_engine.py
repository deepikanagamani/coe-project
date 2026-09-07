"""
Prerequisite Graph Engine.
Models course prerequisites as a Directed Acyclic Graph (DAG).
Provides:
- Cycle detection (Tarjan's/DFS algorithm) surfacing exact circular dependencies
- Topological sorting for term curriculum progression
- Prerequisite transitive closure resolver ("What do I need before taking X?")
- Missing prerequisite identification based on student's completed transcript
- Shortest-path prerequisite satisfaction calculation
"""

from typing import List, Dict, Set, Tuple, Optional, Any
from collections import deque, defaultdict
import os
import json

class PrerequisiteGraphEngine:
    def __init__(self, prerequisites: List[Dict[str, Any]] = None, courses: List[Dict[str, Any]] = None):
        self.adj_list: Dict[str, List[Tuple[str, str]]] = defaultdict(list) # course -> [(prereq, req_type)]
        self.reverse_adj: Dict[str, List[Tuple[str, str]]] = defaultdict(list) # prereq -> [(course, req_type)]
        self.courses_map: Dict[str, Dict[str, Any]] = {}
        
        if courses:
            for c in courses:
                self.courses_map[c["course_id"]] = c
                
        if prerequisites:
            for p in prerequisites:
                cid = p["course_id"]
                pid = p["prerequisite_course_id"]
                req = p["requirement_type"]
                self.adj_list[cid].append((pid, req))
                self.reverse_adj[pid].append((cid, req))

    def detect_cycles(self) -> Tuple[bool, List[str]]:
        """
        Detects cycles in the prerequisite graph using 3-color DFS.
        Returns (has_cycle: bool, cycle_path: List[str]).
        """
        # Colors: 0 = unvisited (WHITE), 1 = visiting (GRAY), 2 = visited (BLACK)
        color: Dict[str, int] = defaultdict(int)
        parent: Dict[str, Optional[str]] = {}
        cycle_path: List[str] = []

        nodes = list(self.adj_list.keys())

        def dfs(u: str) -> bool:
            color[u] = 1 # GRAY
            for v, _ in self.adj_list.get(u, []):
                if color[v] == 1: # Found a back-edge => cycle!
                    # Reconstruct cycle
                    curr = u
                    cycle_path.append(v)
                    while curr != v and curr is not None:
                        cycle_path.append(curr)
                        curr = parent.get(curr)
                    cycle_path.append(v)
                    cycle_path.reverse()
                    return True
                elif color[v] == 0:
                    parent[v] = u
                    if dfs(v):
                        return True
            color[u] = 2 # BLACK
            return False

        for node in nodes:
            if color[node] == 0:
                if dfs(node):
                    return True, cycle_path

        return False, []

    def get_prerequisite_closure(self, course_id: str, hard_only: bool = True) -> Set[str]:
        """
        Computes the complete transitive closure of all prerequisites needed for course_id.
        """
        visited = set()
        queue = deque([course_id])

        while queue:
            curr = queue.popleft()
            for prereq, req_type in self.adj_list.get(curr, []):
                if hard_only and req_type != "hard":
                    continue
                if prereq not in visited:
                    visited.add(prereq)
                    queue.append(prereq)

        return visited

    def evaluate_student_eligibility(self, course_id: str, completed_courses: List[str]) -> Dict[str, Any]:
        """
        Determines if a student can take course_id given their completed courses.
        Returns satisfaction status, missing hard prereqs, and missing recommended prereqs.
        """
        completed_set = set(completed_courses)
        direct_prereqs = self.adj_list.get(course_id, [])

        missing_hard = []
        missing_recommended = []
        satisfied_prereqs = []

        for prereq_id, req_type in direct_prereqs:
            course_info = self.courses_map.get(prereq_id, {"title": prereq_id, "department": "", "credits": 3})
            prereq_data = {
                "course_id": prereq_id,
                "title": course_info.get("title", prereq_id),
                "requirement_type": req_type
            }
            if prereq_id in completed_set:
                satisfied_prereqs.append(prereq_data)
            else:
                if req_type == "hard":
                    missing_hard.append(prereq_data)
                else:
                    missing_recommended.append(prereq_data)

        # Full recursive missing hard prerequisites
        all_hard_prereqs = self.get_prerequisite_closure(course_id, hard_only=True)
        all_missing_hard = sorted(list(all_hard_prereqs - completed_set))

        if len(missing_hard) == 0:
            status = "eligible"
        elif len(satisfied_prereqs) > 0:
            status = "partially_satisfied"
        else:
            status = "locked"

        return {
            "course_id": course_id,
            "status": status,
            "is_eligible": len(missing_hard) == 0,
            "direct_missing_hard": missing_hard,
            "direct_missing_recommended": missing_recommended,
            "satisfied_prereqs": satisfied_prereqs,
            "all_transitive_missing_hard": all_missing_hard
        }

    def get_shortest_prerequisite_path(self, target_course_id: str, completed_courses: List[str]) -> List[List[Dict[str, Any]]]:
        """
        Computes the shortest sequence of terms/stages required to satisfy all hard prerequisites
        for target_course_id starting from the student's completed courses.
        Returns a list of stages (terms), each containing courses that can be taken concurrently.
        """
        completed_set = set(completed_courses)
        all_missing = self.get_prerequisite_closure(target_course_id, hard_only=True) - completed_set

        if not all_missing:
            return []

        # Build in-degree map among the missing courses
        in_degree: Dict[str, int] = defaultdict(int)
        local_adj: Dict[str, List[str]] = defaultdict(list) # prereq -> dependent

        for c in all_missing:
            in_degree[c] = 0

        for c in all_missing:
            for prereq, req_type in self.adj_list.get(c, []):
                if req_type == "hard" and prereq in all_missing:
                    local_adj[prereq].append(c)
                    in_degree[c] += 1

        # Multi-stage BFS / Kahn's algorithm
        stages = []
        current_layer = [c for c in all_missing if in_degree[c] == 0]

        while current_layer:
            layer_courses = []
            for c in sorted(current_layer):
                c_info = self.courses_map.get(c, {"title": c, "department": "", "credits": 3})
                layer_courses.append({
                    "course_id": c,
                    "title": c_info.get("title", c),
                    "department": c_info.get("department", ""),
                    "credits": c_info.get("credits", 3)
                })
            stages.append(layer_courses)

            next_layer = []
            for u in current_layer:
                for v in local_adj[u]:
                    in_degree[v] -= 1
                    if in_degree[v] == 0:
                        next_layer.append(v)
            current_layer = next_layer

        return stages

    def build_dag_visualization_payload(self, target_course_id: str, completed_courses: List[str]) -> Dict[str, Any]:
        """
        Generates nodes and edges formatted for interactive graph visualizers.
        Includes node statuses: 'completed', 'eligible', 'locked', 'target'.
        """
        completed_set = set(completed_courses)
        transitive_prereqs = self.get_prerequisite_closure(target_course_id, hard_only=False)
        relevant_nodes = transitive_prereqs.union({target_course_id})

        nodes = []
        for nid in sorted(relevant_nodes):
            c_info = self.courses_map.get(nid, {})
            if nid == target_course_id:
                status = "target"
            elif nid in completed_set:
                status = "completed"
            else:
                # Check direct hard prereqs
                direct_hard = [p for p, r in self.adj_list.get(nid, []) if r == "hard"]
                if all(p in completed_set for p in direct_hard):
                    status = "eligible"
                else:
                    status = "locked"

            nodes.append({
                "id": nid,
                "title": c_info.get("title", nid),
                "department": c_info.get("department", ""),
                "credits": c_info.get("credits", 3),
                "status": status,
                "difficulty": c_info.get("difficulty_level", "Intermediate")
            })

        edges = []
        for nid in relevant_nodes:
            for prereq, req_type in self.adj_list.get(nid, []):
                if prereq in relevant_nodes:
                    edges.append({
                        "source": prereq,
                        "target": nid,
                        "requirement_type": req_type,
                        "is_satisfied": prereq in completed_set
                    })

        return {
            "target_course_id": target_course_id,
            "nodes": nodes,
            "edges": edges,
            "total_nodes": len(nodes),
            "total_edges": len(edges)
        }
