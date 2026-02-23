/**
 * Stillwater Admin Dojo — Mermaid Graph Handler
 *
 * Handles:
 * - Mermaid.js initialization
 * - Graph rendering and refresh
 * - Interactive node click handlers (Phase 1B+)
 * - Pan/zoom functionality (Phase 1B+)
 */

// ============================================================================
// MERMAID INITIALIZATION
// ============================================================================

/**
 * Initialize Mermaid.js library configuration
 * Called by app.js on page load
 */
function initializeMermaidGraphs() {
    if (typeof mermaid === 'undefined') {
        console.warn('⚠ Mermaid.js not loaded from CDN. Graphs will not render.');
        return;
    }

    console.log('🎨 Initializing Mermaid.js...');

    mermaid.initialize({
        // Core settings
        startOnLoad: false,      // Manual control for better UX
        theme: 'default',
        securityLevel: 'antiscript',
        logLevel: 'warn',

        // Diagram settings
        flowchart: {
            useMaxWidth: true,
            curve: 'linear',
            htmlLabels: true
        },
        stateDiagram: {
            useMaxWidth: true,
            htmlLabels: true
        },
        gantt: {
            useMaxWidth: true
        }
    });

    console.log('✓ Mermaid.js initialized');
}

/**
 * Render all Mermaid diagrams on page
 * Called after new HTML is inserted into DOM
 */
async function renderMermaidGraphs() {
    try {
        if (typeof mermaid === 'undefined') {
            console.warn('Mermaid.js not available');
            return;
        }

        // Find all unrendered Mermaid blocks
        const unrenderedBlocks = document.querySelectorAll('pre.mermaid:not([data-processed])');

        if (unrenderedBlocks.length === 0) {
            return;
        }

        console.log(`🎨 Rendering ${unrenderedBlocks.length} Mermaid diagram(s)`);

        // Use mermaid's built-in rendering
        await mermaid.contentLoaded();

        // Mark blocks as processed
        unrenderedBlocks.forEach(block => {
            block.setAttribute('data-processed', 'true');
        });

        console.log('✓ Mermaid diagrams rendered');
    } catch (error) {
        console.error('Failed to render Mermaid diagrams:', error);
    }
}

// ============================================================================
// GRAPH MANAGEMENT
// ============================================================================

/**
 * Store loaded graph data for reference
 */
let graphCache = {
    skills: null,
    recipes: null,
    swarms: null,
    personas: null
};

/**
 * Load and cache graph data from API
 */
async function loadGraphData(graphType) {
    if (graphCache[graphType]) {
        return graphCache[graphType];
    }

    try {
        const response = await fetch(`/api/mermaid/${graphType}`);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();
        graphCache[graphType] = data;
        return data;
    } catch (error) {
        console.error(`Failed to load ${graphType} graph:`, error);
        return null;
    }
}

/**
 * Render a specific Mermaid graph
 */
async function renderGraph(graphType) {
    const containerId = `mermaid-${graphType}`;
    const container = document.getElementById(containerId);

    if (!container) {
        console.warn(`Container #${containerId} not found`);
        return;
    }

    // Show loading state
    container.innerHTML = '<p class="loading-text">Loading ' + graphType + ' graph...</p>';

    try {
        const graphData = await loadGraphData(graphType);

        if (!graphData || !graphData.graph_syntax) {
            container.innerHTML = `<p class="loading-text">No data available for ${graphType}</p>`;
            return;
        }

        // Insert Mermaid syntax into container
        container.innerHTML = `<pre class="mermaid">${escapeHtml(graphData.graph_syntax)}</pre>`;

        // Render the Mermaid diagram
        await renderMermaidGraphs();

        // Register click handlers for nodes (Phase 1B+)
        // This is a placeholder for future implementation
        registerGraphClickHandlers(graphType, graphData);

    } catch (error) {
        console.error(`Failed to render ${graphType} graph:`, error);
        container.innerHTML = `<p class="loading-text">Failed to load graph. Please refresh the page.</p>`;
    }
}

/**
 * Register click handlers on graph nodes
 * Phase 1B feature: Click on skill node → show detail panel
 */
function registerGraphClickHandlers(graphType, graphData) {
    if (graphType !== 'skills') {
        return; // Only implement for skills graph in Phase 1B
    }

    const svg = document.querySelector(`#mermaid-${graphType} svg`);
    if (!svg) return;

    // Find all clickable text elements in the SVG
    const textElements = svg.querySelectorAll('text');

    textElements.forEach(textEl => {
        const text = textEl.textContent.trim();

        // Check if this text matches a skill node
        if (graphData.nodes && graphData.nodes.some(node => node.label.includes(text))) {
            textEl.style.cursor = 'pointer';
            textEl.addEventListener('click', function() {
                const skillId = text.split('\n')[0].toLowerCase().replace(/\s+/g, '-');
                console.log(`🔍 Clicked node: ${skillId}`);
                // Phase 1B: Implement showSkillDetail(skillId)
            });
        }
    });
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Escape HTML special characters
 */
function escapeHtml(unsafe) {
    if (!unsafe) return '';
    return unsafe
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

/**
 * Clear graph cache
 */
function clearGraphCache() {
    graphCache = {
        skills: null,
        recipes: null,
        swarms: null,
        personas: null
    };
}

/**
 * Refresh all graphs (useful for updates)
 */
async function refreshAllGraphs() {
    console.log('🔄 Refreshing all graphs...');
    clearGraphCache();

    // Reload visible graphs
    const activeTab = document.querySelector('.tab-pane.active');
    if (activeTab) {
        const tabId = activeTab.id.replace('tab-', '');
        if (['skills', 'recipes', 'swarms', 'personas'].includes(tabId)) {
            await renderGraph(tabId);
        }
    }
}

// ============================================================================
// PHASE 1B PLACEHOLDERS
// ============================================================================

/**
 * Show detail panel for a skill
 * Phase 1B feature: Click on skill in graph → show side panel
 */
function showSkillDetail(skillId) {
    console.log(`📚 Loading detail for skill: ${skillId}`);
    // Phase 1B: Fetch /api/skills/{skillId} and render in detail panel
}

/**
 * Hide detail panel
 */
function hideSkillDetail() {
    console.log('📚 Hiding detail panel');
    // Phase 1B: Hide the detail panel
}

/**
 * Enable pan and zoom on Mermaid diagrams
 * Phase 1B feature: Mouse wheel to zoom, drag to pan
 */
function enablePanZoom() {
    // Phase 1B: Implement using SVG pan/zoom library
    // Could use: https://github.com/ariutta/svg-pan-zoom
}

/**
 * Download graph as image
 * Phase 1B feature: Export graph as PNG
 */
function downloadGraphAsImage(graphType) {
    console.log(`📥 Downloading ${graphType} graph as image...`);
    // Phase 1B: Use html2canvas or similar to export SVG as PNG
}

// ============================================================================
// INITIALIZATION
// ============================================================================

// Mermaid is already initialized by app.js via initializeMermaidGraphs()
// This module just provides the rendering and interaction functions
