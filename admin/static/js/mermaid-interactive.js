/**
 * Stillwater Mermaid-Interactive Homepage
 * Orchestration diagram with click-to-explore node details
 */

let currentSelectedNode = "explorer";
let orchestrationData = null;

/**
 * Initialize Mermaid-Interactive homepage
 */
async function initMermaidInteractive() {
    console.log("Initializing Mermaid-Interactive...");

    try {
        // Load Mermaid library
        if (typeof mermaid === 'undefined') {
            console.error("Mermaid library not loaded");
            return;
        }

        // Initialize mermaid
        mermaid.initialize({ startOnLoad: true, theme: 'dark' });

        // Fetch orchestration mermaid diagram
        const mermaidResp = await fetch("/api/orchestration/mermaid");
        if (!mermaidResp.ok) {
            console.error("Failed to fetch orchestration mermaid");
            return;
        }

        const mermaidData = await mermaidResp.json();
        console.log("Orchestration data:", mermaidData);

        // Render diagram
        const diagramContainer = document.getElementById("mermaid-diagram");
        if (!diagramContainer) {
            console.error("Diagram container not found");
            return;
        }

        // Set diagram content
        diagramContainer.innerHTML = "";
        const diagramElement = document.createElement("div");
        diagramElement.className = "mermaid";
        diagramElement.textContent = mermaidData.mermaid;
        diagramContainer.appendChild(diagramElement);

        // Re-render mermaid
        await mermaid.contentLoaded();

        // Setup node click handlers after mermaid renders
        setupNodeClickHandlers(mermaidData.nodes);

        // Load initial node details (Explorer)
        await updateNodeDetails("explorer");

        // Setup CLI swarm selector
        setupCLISwarmSelector(mermaidData.nodes);

        console.log("Mermaid-Interactive initialized successfully");
    } catch (error) {
        console.error("Error initializing Mermaid-Interactive:", error);
    }
}

/**
 * Setup click handlers for diagram nodes
 */
function setupNodeClickHandlers(nodes) {
    nodes.forEach((nodeId) => {
        // Find the node element in the rendered SVG
        // Mermaid renders nodes as g elements with id <nodeId>
        const nodeElements = document.querySelectorAll(`[id="${nodeId}"]`);

        nodeElements.forEach((elem) => {
            // Make entire node clickable
            elem.style.cursor = "pointer";

            // Add click handler to the whole group
            elem.addEventListener("click", (e) => {
                e.stopPropagation();
                selectNode(nodeId);
            });

            // Add hover effects
            elem.addEventListener("mouseenter", () => {
                elem.style.opacity = "0.8";
                showNodeTooltip(nodeId, elem);
            });

            elem.addEventListener("mouseleave", () => {
                elem.style.opacity = "1";
                hideNodeTooltip();
            });
        });

        // Also add click to text label in mermaid
        const labelElements = document.querySelectorAll(`[data-id="${nodeId}"]`);
        labelElements.forEach((elem) => {
            elem.style.cursor = "pointer";
            elem.addEventListener("click", (e) => {
                e.stopPropagation();
                selectNode(nodeId);
            });
        });
    });
}

/**
 * Select a node and update details panel
 */
async function selectNode(nodeId) {
    console.log("Node selected:", nodeId);
    currentSelectedNode = nodeId;

    // Highlight selected node in diagram
    highlightNodeInDiagram(nodeId);

    // Update node details panel
    await updateNodeDetails(nodeId);

    // Update CLI swarm selector
    const selectorDropdown = document.getElementById("cli-swarm-selector");
    if (selectorDropdown) {
        selectorDropdown.value = nodeId;
    }
}

/**
 * Highlight selected node in diagram
 */
function highlightNodeInDiagram(nodeId) {
    // Remove highlight from all nodes
    const allNodes = document.querySelectorAll(".mermaid g");
    allNodes.forEach((node) => {
        if (node.style) {
            node.style.opacity = "0.5";
        }
    });

    // Highlight selected node
    const selectedNodes = document.querySelectorAll(`[id="${nodeId}"]`);
    selectedNodes.forEach((node) => {
        node.style.opacity = "1";
        node.style.filter = "drop-shadow(0 0 8px rgba(59, 130, 246, 0.5))";
    });
}

/**
 * Fetch and display node details
 */
async function updateNodeDetails(nodeId) {
    try {
        const response = await fetch(`/api/orchestration/node/${nodeId}`);
        if (!response.ok) {
            console.error("Failed to fetch node details");
            return;
        }

        const nodeDetails = await response.json();
        console.log("Node details:", nodeDetails);

        // Populate details panel
        const detailsPanel = document.getElementById("node-details-panel");
        if (!detailsPanel) {
            console.error("Details panel not found");
            return;
        }

        const html = `
            <div class="node-details">
                <h3 class="node-title">${nodeDetails.name} <span class="node-model">${nodeDetails.model}</span></h3>

                <div class="detail-section">
                    <h4>Role & Responsibility</h4>
                    <p><strong>Role:</strong> ${nodeDetails.role}</p>
                    <p><strong>Type:</strong> ${nodeDetails.type}</p>
                    <p><strong>Persona:</strong> ${nodeDetails.persona}</p>
                    <p><strong>Responsibility:</strong> ${nodeDetails.responsibility}</p>
                </div>

                <div class="detail-section">
                    <h4>Strengths</h4>
                    <ul class="strengths-list">
                        ${nodeDetails.strengths.map(s => `<li>${s}</li>`).join('')}
                    </ul>
                </div>

                <div class="detail-section">
                    <h4>Tools</h4>
                    <ul class="tools-list">
                        ${nodeDetails.tools.map(t => `<li class="tool-tag">${t}</li>`).join('')}
                    </ul>
                </div>

                <div class="detail-section">
                    <h4>Algorithm</h4>
                    <div id="node-algorithm-diagram" class="algorithm-diagram"></div>
                </div>

                <div class="detail-section">
                    <h4>Example Commands</h4>
                    <ul class="examples-list">
                        ${nodeDetails.examples.map(ex => `<li>${ex}</li>`).join('')}
                    </ul>
                </div>

                <div class="detail-section">
                    <h4>Configuration</h4>
                    <p><code>${nodeDetails.config_path}</code></p>
                    <p class="rung-info">Target Rung: <strong>${nodeDetails.rung_target}</strong></p>
                </div>
            </div>
        `;

        detailsPanel.innerHTML = html;

        // Render algorithm diagram
        if (nodeDetails.algorithm) {
            const algorithmDiv = document.getElementById("node-algorithm-diagram");
            if (algorithmDiv) {
                algorithmDiv.innerHTML = `<div class="mermaid">${nodeDetails.algorithm}</div>`;
                await mermaid.contentLoaded();
            }
        }
    } catch (error) {
        console.error("Error updating node details:", error);
    }
}

/**
 * Show tooltip on node hover
 */
function showNodeTooltip(nodeId, element) {
    // Create tooltip
    const tooltip = document.createElement("div");
    tooltip.className = "node-tooltip";
    tooltip.id = "node-tooltip";

    const nodeNameMap = {
        explorer: { role: "Scout", task: "Research & discovery" },
        builder: { role: "Coder", task: "Implementation & testing" },
        arbiter: { role: "Skeptic", task: "Verification & review" }
    };

    const info = nodeNameMap[nodeId] || { role: nodeId, task: "" };

    tooltip.innerHTML = `
        <div class="tooltip-content">
            <strong>${nodeId.charAt(0).toUpperCase() + nodeId.slice(1)}</strong><br/>
            ${info.role}<br/>
            <small>${info.task}</small>
        </div>
    `;

    document.body.appendChild(tooltip);

    // Position tooltip near element
    const rect = element.getBoundingClientRect();
    tooltip.style.position = "fixed";
    tooltip.style.left = (rect.left + rect.width / 2) + "px";
    tooltip.style.top = (rect.top - 60) + "px";
    tooltip.style.zIndex = "9999";
}

/**
 * Hide tooltip
 */
function hideNodeTooltip() {
    const tooltip = document.getElementById("node-tooltip");
    if (tooltip) {
        tooltip.remove();
    }
}

/**
 * Setup CLI swarm selector dropdown
 */
function setupCLISwarmSelector(nodes) {
    const selectorContainer = document.getElementById("cli-swarm-selector-container");
    if (!selectorContainer) {
        console.log("CLI swarm selector container not found, skipping");
        return;
    }

    // Create dropdown
    const select = document.createElement("select");
    select.id = "cli-swarm-selector";
    select.className = "swarm-selector";

    // Add options
    const options = [
        { value: "orchestration", label: "Orchestration" },
        ...nodes.map(nodeId => ({
            value: nodeId,
            label: nodeId.charAt(0).toUpperCase() + nodeId.slice(1)
        }))
    ];

    options.forEach((opt) => {
        const option = document.createElement("option");
        option.value = opt.value;
        option.textContent = opt.label;
        if (opt.value === "explorer") {
            option.selected = true;
        }
        select.appendChild(option);
    });

    // Add change handler
    select.addEventListener("change", (e) => {
        const selectedValue = e.target.value;
        if (selectedValue !== "orchestration") {
            selectNode(selectedValue);
        }
    });

    selectorContainer.appendChild(select);
}

/**
 * Initialize on DOM ready
 */
document.addEventListener("DOMContentLoaded", async () => {
    console.log("DOM loaded, initializing Mermaid-Interactive");
    await initMermaidInteractive();
});
