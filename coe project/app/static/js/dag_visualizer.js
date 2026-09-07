/**
 * Interactive SVG-Based Directed Acyclic Graph (DAG) Visualizer
 * Provides:
 * - Topological layered layout
 * - Dual visual encoding (status color + distinct shape/symbol)
 * - Pan and zoom interaction
 * - Node inspection callbacks
 */

class DAGVisualizer {
  constructor(containerId, options = {}) {
    this.container = document.getElementById(containerId);
    this.options = Object.assign({
      nodeWidth: 150,
      nodeHeight: 64,
      layerGapX: 200,
      nodeGapY: 85,
      onNodeClick: null
    }, options);
    
    this.svg = null;
    this.g = null;
    this.scale = 1.0;
    this.panX = 40;
    this.panY = 40;
    this.isDragging = false;
    this.startX = 0;
    this.startY = 0;
  }

  render(dagData) {
    if (!this.container) return;
    this.container.innerHTML = "";

    const { nodes, edges, target_course_id } = dagData;
    if (!nodes || nodes.length === 0) {
      this.container.innerHTML = `<div class="empty-state">No prerequisite relationships found for this course.</div>`;
      return;
    }

    // Compute topological layers (X positions) and layout
    const nodeMap = new Map();
    nodes.forEach(n => nodeMap.set(n.id, { ...n, inDegree: 0, outDegree: 0, layer: 0 }));

    edges.forEach(e => {
      if (nodeMap.has(e.target) && nodeMap.has(e.source)) {
        nodeMap.get(e.target).inDegree++;
        nodeMap.get(e.source).outDegree++;
      }
    });

    // Assign layers via longest path from roots (sources)
    const adj = new Map();
    nodes.forEach(n => adj.set(n.id, []));
    edges.forEach(e => {
      if (adj.has(e.source)) adj.get(e.source).push(e.target);
    });

    // BFS layer assignment
    const queue = [];
    nodes.forEach(n => {
      if (nodeMap.get(n.id).inDegree === 0) {
        queue.push(n.id);
      }
    });

    while (queue.length > 0) {
      const curr = queue.shift();
      const currLayer = nodeMap.get(curr).layer;
      (adj.get(curr) || []).forEach(nextId => {
        const nextNode = nodeMap.get(nextId);
        if (nextNode) {
          if (currLayer + 1 > nextNode.layer) {
            nextNode.layer = currLayer + 1;
          }
          queue.push(nextId);
        }
      });
    }

    // Group nodes by layer
    const layers = new Map();
    nodeMap.forEach(node => {
      if (!layers.has(node.layer)) layers.set(node.layer, []);
      layers.get(node.layer).push(node);
    });

    // Assign pixel coordinates (X, Y)
    let maxLayer = 0;
    let maxRows = 0;
    layers.forEach((layerNodes, layerIndex) => {
      if (layerIndex > maxLayer) maxLayer = layerIndex;
      if (layerNodes.length > maxRows) maxRows = layerNodes.length;
      layerNodes.forEach((node, rowIndex) => {
        node.x = 60 + layerIndex * this.options.layerGapX;
        node.y = 50 + rowIndex * this.options.nodeGapY;
      });
    });

    const totalWidth = Math.max(750, (maxLayer + 1) * this.options.layerGapX + 220);
    const totalHeight = Math.max(380, maxRows * this.options.nodeGapY + 120);

    // Create SVG element
    const svgEl = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svgEl.setAttribute("width", "100%");
    svgEl.setAttribute("height", "100%");
    svgEl.setAttribute("viewBox", `0 0 ${totalWidth} ${totalHeight}`);
    svgEl.setAttribute("role", "graphics-document");
    svgEl.setAttribute("aria-label", "Interactive Course Prerequisite DAG diagram");

    // Defs for arrowheads and drop shadows
    const defs = document.createElementNS("http://www.w3.org/2000/svg", "defs");
    defs.innerHTML = `
      <marker id="arrow-hard" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
        <path d="M 0 0 L 8 4 L 0 8 Z" fill="#6366f1" />
      </marker>
      <marker id="arrow-recommended" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
        <path d="M 0 0 L 8 4 L 0 8 Z" fill="#94a3b8" />
      </marker>
      <marker id="arrow-satisfied" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
        <path d="M 0 0 L 8 4 L 0 8 Z" fill="#10b981" />
      </marker>
      <filter id="node-shadow" x="-10%" y="-10%" width="120%" height="130%">
        <feDropShadow dx="0" dy="3" stdDeviation="4" flood-color="#000000" flood-opacity="0.15" />
      </filter>
    `;
    svgEl.appendChild(defs);

    const gEl = document.createElementNS("http://www.w3.org/2000/svg", "g");
    gEl.setAttribute("id", "dag-viewport-group");
    svgEl.appendChild(gEl);

    // Render Edges (cubic bezier curves)
    edges.forEach(e => {
      const srcNode = nodeMap.get(e.source);
      const tgtNode = nodeMap.get(e.target);
      if (!srcNode || !tgtNode) return;

      const x1 = srcNode.x + this.options.nodeWidth;
      const y1 = srcNode.y + this.options.nodeHeight / 2;
      const x2 = tgtNode.x;
      const y2 = tgtNode.y + this.options.nodeHeight / 2;
      const cx = (x1 + x2) / 2;

      const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
      path.setAttribute("d", `M ${x1} ${y1} C ${cx} ${y1}, ${cx} ${y2}, ${x2} ${y2}`);
      
      let strokeColor = "#6366f1";
      let markerId = "arrow-hard";
      let strokeDash = "none";

      if (e.is_satisfied) {
        strokeColor = "#10b981";
        markerId = "arrow-satisfied";
      } else if (e.requirement_type === "recommended") {
        strokeColor = "#94a3b8";
        strokeDash = "4 4";
        markerId = "arrow-recommended";
      }

      path.setAttribute("stroke", strokeColor);
      path.setAttribute("stroke-width", "2.2");
      path.setAttribute("stroke-dasharray", strokeDash);
      path.setAttribute("fill", "none");
      path.setAttribute("marker-end", `url(#${markerId})`);
      path.setAttribute("class", "dag-edge");
      gEl.appendChild(path);
    });

    // Render Nodes
    nodeMap.forEach(node => {
      const nodeG = document.createElementNS("http://www.w3.org/2000/svg", "g");
      nodeG.setAttribute("class", `dag-node dag-node-${node.status}`);
      nodeG.setAttribute("transform", `translate(${node.x}, ${node.y})`);
      nodeG.setAttribute("tabindex", "0");
      nodeG.setAttribute("role", "button");
      nodeG.setAttribute("aria-label", `Course ${node.id}: ${node.title}. Status: ${node.status}`);

      // Background rect with pill/rounded corners
      const rect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
      rect.setAttribute("width", this.options.nodeWidth);
      rect.setAttribute("height", this.options.nodeHeight);
      rect.setAttribute("rx", "10");
      rect.setAttribute("ry", "10");
      rect.setAttribute("filter", "url(#node-shadow)");

      // Dual encoding status colors and icons
      let iconSymbol = "ℹ️";
      let badgeColor = "#64748b";

      if (node.status === "completed") {
        rect.setAttribute("fill", "#064e3b");
        rect.setAttribute("stroke", "#10b981");
        iconSymbol = "✓ Completed";
        badgeColor = "#10b981";
      } else if (node.status === "eligible") {
        rect.setAttribute("fill", "#1e1b4b");
        rect.setAttribute("stroke", "#6366f1");
        iconSymbol = "★ Eligible";
        badgeColor = "#818cf8";
      } else if (node.status === "locked") {
        rect.setAttribute("fill", "#451a03");
        rect.setAttribute("stroke", "#f59e0b");
        iconSymbol = "🔒 Locked";
        badgeColor = "#f59e0b";
      } else if (node.status === "target") {
        rect.setAttribute("fill", "#312e81");
        rect.setAttribute("stroke", "#a855f7");
        rect.setAttribute("stroke-width", "3");
        iconSymbol = "🎯 Target";
        badgeColor = "#c084fc";
      }

      rect.setAttribute("stroke-width", node.status === "target" ? "3" : "1.8");
      nodeG.appendChild(rect);

      // Course ID Text
      const textId = document.createElementNS("http://www.w3.org/2000/svg", "text");
      textId.setAttribute("x", "12");
      textId.setAttribute("y", "22");
      textId.setAttribute("font-weight", "700");
      textId.setAttribute("font-size", "14");
      textId.setAttribute("fill", "#ffffff");
      textId.textContent = node.id;
      nodeG.appendChild(textId);

      // Status Badge (Dual visual symbol)
      const textStatus = document.createElementNS("http://www.w3.org/2000/svg", "text");
      textStatus.setAttribute("x", this.options.nodeWidth - 10);
      textStatus.setAttribute("y", "20");
      textStatus.setAttribute("text-anchor", "end");
      textStatus.setAttribute("font-size", "10");
      textStatus.setAttribute("font-weight", "600");
      textStatus.setAttribute("fill", badgeColor);
      textStatus.textContent = iconSymbol;
      nodeG.appendChild(textStatus);

      // Course Title (truncated)
      const textTitle = document.createElementNS("http://www.w3.org/2000/svg", "text");
      textTitle.setAttribute("x", "12");
      textTitle.setAttribute("y", "42");
      textTitle.setAttribute("font-size", "11");
      textTitle.setAttribute("fill", "#cbd5e1");
      const truncatedTitle = node.title.length > 18 ? node.title.substring(0, 16) + "..." : node.title;
      textTitle.textContent = truncatedTitle;
      nodeG.appendChild(textTitle);

      // Credits & Department badge
      const textMeta = document.createElementNS("http://www.w3.org/2000/svg", "text");
      textMeta.setAttribute("x", "12");
      textMeta.setAttribute("y", "56");
      textMeta.setAttribute("font-size", "9.5");
      textMeta.setAttribute("fill", "#94a3b8");
      textMeta.textContent = `${node.department} • ${node.credits} cr`;
      nodeG.appendChild(textMeta);

      // Click event
      nodeG.addEventListener("click", () => {
        if (this.options.onNodeClick) {
          this.options.onNodeClick(node);
        }
      });
      nodeG.addEventListener("keydown", (evt) => {
        if (evt.key === "Enter" || evt.key === " ") {
          if (this.options.onNodeClick) this.options.onNodeClick(node);
        }
      });

      gEl.appendChild(nodeG);
    });

    this.svg = svgEl;
    this.g = gEl;
    this.container.appendChild(svgEl);

    this.setupInteractivity(svgEl, gEl);
  }

  setupInteractivity(svg, g) {
    let isPanning = false;
    let startPoint = { x: 0, y: 0 };
    let currentTranslate = { x: 0, y: 0 };

    svg.addEventListener("mousedown", (e) => {
      if (e.target.closest(".dag-node")) return;
      isPanning = true;
      startPoint = { x: e.clientX - currentTranslate.x, y: e.clientY - currentTranslate.y };
      svg.style.cursor = "grabbing";
    });

    window.addEventListener("mousemove", (e) => {
      if (!isPanning) return;
      currentTranslate.x = e.clientX - startPoint.x;
      currentTranslate.y = e.clientY - startPoint.y;
      g.setAttribute("transform", `translate(${currentTranslate.x}, ${currentTranslate.y}) scale(${this.scale})`);
    });

    window.addEventListener("mouseup", () => {
      if (isPanning) {
        isPanning = false;
        svg.style.cursor = "grab";
      }
    });

    svg.addEventListener("wheel", (e) => {
      e.preventDefault();
      const zoomFactor = e.deltaY < 0 ? 1.1 : 0.9;
      this.scale = Math.min(Math.max(0.5, this.scale * zoomFactor), 2.2);
      g.setAttribute("transform", `translate(${currentTranslate.x}, ${currentTranslate.y}) scale(${this.scale})`);
    });
  }

  zoomIn() {
    this.scale = Math.min(2.2, this.scale * 1.2);
    if (this.g) this.g.setAttribute("transform", `scale(${this.scale})`);
  }

  zoomOut() {
    this.scale = Math.max(0.5, this.scale * 0.8);
    if (this.g) this.g.setAttribute("transform", `scale(${this.scale})`);
  }

  resetZoom() {
    this.scale = 1.0;
    if (this.g) this.g.setAttribute("transform", `translate(0, 0) scale(1)`);
  }
}

window.DAGVisualizer = DAGVisualizer;
