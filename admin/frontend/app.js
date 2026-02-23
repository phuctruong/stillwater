/**
 * Stillwater Admin Dojo — Main Application Logic
 *
 * Handles:
 * - Page initialization and API calls
 * - Status dashboard updates
 * - Tab navigation
 * - Status polling
 * - Error handling and user feedback
 */

// ============================================================================
// GLOBAL STATE
// ============================================================================

let appState = {
    activeTab: 'dashboard',
    isPolling: false,
    pollInterval: 5000, // 5 seconds
    pollingHandle: null,
    statusData: {
        llm: null,
        solace: null,
        skills: null
    }
};

// ============================================================================
// INITIALIZATION
// ============================================================================

/**
 * Initialize the application on page load
 */
async function initializeApp() {
    console.log('🚀 Initializing Stillwater Admin Dojo...');

    try {
        // Check server health
        await checkServerHealth();

        // Fetch system status
        await fetchSystemStatus();

        // Setup tab navigation
        setupTabNavigation();

        // Initialize Mermaid graphs
        initializeMermaidGraphs();

        // Start polling
        startPolling();

        console.log('✓ Application initialized successfully');
    } catch (error) {
        console.error('✗ Initialization failed:', error);
        showError('Failed to initialize application. Please refresh the page.');
    }
}

/**
 * Check server health and update topbar status
 */
async function checkServerHealth() {
    try {
        const response = await fetch('/health', {
            method: 'GET',
            timeout: 5000
        });

        if (response.ok) {
            updateServerStatus('online');
            return true;
        } else {
            updateServerStatus('offline');
            return false;
        }
    } catch (error) {
        console.warn('Server health check failed:', error);
        updateServerStatus('offline');
        return false;
    }
}

/**
 * Update server status in topbar
 */
function updateServerStatus(status) {
    const statusEl = document.getElementById('serverStatus');
    if (!statusEl) return;

    if (status === 'online') {
        statusEl.textContent = '● Server Online';
        statusEl.parentElement.classList.add('online');
    } else {
        statusEl.textContent = '● Server Offline';
        statusEl.parentElement.classList.remove('online');
    }
}

// ============================================================================
// API CALLS
// ============================================================================

/**
 * Fetch system status from all endpoints
 */
async function fetchSystemStatus() {
    try {
        const [llmStatus, solaceStatus, skillsList] = await Promise.all([
            fetch('/api/llm/status').then(r => r.json()).catch(e => {
                console.warn('LLM status fetch failed:', e);
                return { online: false };
            }),
            fetch('/api/solace-agi/status').then(r => r.json()).catch(e => {
                console.warn('Solace status fetch failed:', e);
                return { configured: false };
            }),
            fetch('/api/skills/list').then(r => r.json()).catch(e => {
                console.warn('Skills list fetch failed:', e);
                return { count: 0, skills: [] };
            })
        ]);

        appState.statusData = {
            llm: llmStatus,
            solace: solaceStatus,
            skills: skillsList
        };

        renderStatusDashboard(appState.statusData);
        return appState.statusData;
    } catch (error) {
        console.error('Failed to fetch system status:', error);
        throw error;
    }
}

/**
 * Load Mermaid graph data for all tabs
 */
async function loadMermaidGraphs() {
    try {
        const graphs = await Promise.all([
            fetch('/api/mermaid/skills').then(r => r.json()).catch(e => ({ graph_syntax: '', nodes: [] })),
            fetch('/api/mermaid/recipes').then(r => r.json()).catch(e => ({ graph_syntax: '', nodes: [] })),
            fetch('/api/mermaid/swarms').then(r => r.json()).catch(e => ({ graph_syntax: '', nodes: [] })),
            fetch('/api/mermaid/personas').then(r => r.json()).catch(e => ({ graph_syntax: '', nodes: [] }))
        ]);

        return {
            skills: graphs[0],
            recipes: graphs[1],
            swarms: graphs[2],
            personas: graphs[3]
        };
    } catch (error) {
        console.error('Failed to load Mermaid graphs:', error);
        return {};
    }
}

// ============================================================================
// RENDERING
// ============================================================================

/**
 * Render status dashboard with current data
 */
function renderStatusDashboard(statusData) {
    // Render LLM Status Card
    const llmCard = document.getElementById('cardLLM');
    const llmStatus = document.getElementById('llmStatus');
    const llmDetail = document.getElementById('llmDetail');

    if (statusData.llm && statusData.llm.online) {
        llmCard.classList.add('online');
        llmStatus.textContent = `✓ Online`;
        llmDetail.textContent = `Model: ${statusData.llm.default_model || 'Not set'}`;
    } else {
        llmCard.classList.remove('online');
        llmStatus.textContent = '⚠ Not Configured';
        llmDetail.textContent = 'Click Configure to get started';
    }

    // Render Solace AGI Status Card
    const solaceCard = document.getElementById('cardSolace');
    const solaceStatus = document.getElementById('solaceStatus');
    const solaceDetail = document.getElementById('solaceDetail');

    if (statusData.solace && statusData.solace.configured) {
        solaceCard.classList.add('online');
        solaceStatus.textContent = '✓ Connected';
        solaceDetail.textContent = `Tier: ${statusData.solace.tier || 'Free'}`;
    } else {
        solaceCard.classList.remove('online');
        solaceStatus.textContent = '⚠ Not Configured';
        solaceDetail.textContent = 'Optional cloud features';
    }

    // Render Skills Status Card
    const skillsStatus = document.getElementById('skillsStatus');
    const skillsDetail = document.getElementById('skillsDetail');

    if (statusData.skills && statusData.skills.count > 0) {
        skillsStatus.textContent = `✓ ${statusData.skills.count} skills loaded`;
        skillsDetail.textContent = 'Ready to explore';
    } else {
        skillsStatus.textContent = '⏳ Loading skills...';
        skillsDetail.textContent = '';
    }
}

// ============================================================================
// TAB NAVIGATION
// ============================================================================

/**
 * Setup tab navigation handlers
 */
function setupTabNavigation() {
    const tabBtns = document.querySelectorAll('.tab-btn');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const tabName = this.getAttribute('data-tab');
            switchTab(tabName);
        });
    });

    // Restore active tab from localStorage
    const savedTab = localStorage.getItem('activeTab');
    if (savedTab) {
        switchTab(savedTab);
    }
}

/**
 * Switch to a specific tab
 */
function switchTab(tabName) {
    // Remove active class from all buttons and panes
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelectorAll('.tab-pane').forEach(pane => {
        pane.classList.remove('active');
    });

    // Add active class to clicked button and corresponding pane
    const activeBtn = document.querySelector(`[data-tab="${tabName}"]`);
    const activePane = document.getElementById(`tab-${tabName}`);

    if (activeBtn) activeBtn.classList.add('active');
    if (activePane) activePane.classList.add('active');

    appState.activeTab = tabName;
    localStorage.setItem('activeTab', tabName);

    // Load Mermaid graphs when switching to graph tabs
    if (['skills', 'recipes', 'swarms', 'personas'].includes(tabName)) {
        loadAndRenderMermaidGraph(tabName);
    }
}

/**
 * Load and render Mermaid graph for a tab
 */
async function loadAndRenderMermaidGraph(tabName) {
    const container = document.getElementById(`mermaid-${tabName}`);
    if (!container) return;

    try {
        const response = await fetch(`/api/mermaid/${tabName}`);
        const data = await response.json();

        if (data.graph_syntax) {
            container.innerHTML = `<pre class="mermaid">${data.graph_syntax}</pre>`;
            // Re-render Mermaid diagrams
            if (typeof mermaid !== 'undefined') {
                mermaid.contentLoaded();
            }
        }
    } catch (error) {
        console.warn(`Failed to load ${tabName} graph:`, error);
        container.innerHTML = `<p class="loading-text">Failed to load ${tabName} graph. Please refresh the page.</p>`;
    }
}

// ============================================================================
// MERMAID INITIALIZATION
// ============================================================================

/**
 * Initialize Mermaid.js library
 */
function initializeMermaidGraphs() {
    if (typeof mermaid === 'undefined') {
        console.warn('Mermaid.js not loaded from CDN');
        return;
    }

    mermaid.initialize({
        startOnLoad: true,
        theme: 'default',
        securityLevel: 'antiscript',
        logLevel: 'warn',
        flowchart: {
            useMaxWidth: true
        }
    });

    mermaid.contentLoaded();
}

// ============================================================================
// STATUS POLLING
// ============================================================================

/**
 * Start polling for status updates
 */
function startPolling() {
    if (appState.isPolling) return;

    appState.isPolling = true;
    console.log('📡 Status polling started (every 5 seconds)');

    // Initial poll
    pollStatusUpdates();

    // Set interval for polling
    appState.pollingHandle = setInterval(pollStatusUpdates, appState.pollInterval);

    // Stop polling when user tabs away
    document.addEventListener('visibilitychange', function() {
        if (document.hidden) {
            stopPolling();
        } else {
            startPolling();
        }
    });
}

/**
 * Stop polling for status updates
 */
function stopPolling() {
    if (!appState.isPolling) return;

    appState.isPolling = false;
    if (appState.pollingHandle) {
        clearInterval(appState.pollingHandle);
        appState.pollingHandle = null;
    }
    console.log('⏸ Status polling stopped');
}

/**
 * Poll status endpoints and update dashboard
 */
async function pollStatusUpdates() {
    if (document.hidden) return; // Don't poll if tab is not visible

    try {
        await fetchSystemStatus();
    } catch (error) {
        // Polling errors are non-critical, just log them
        console.debug('Polling error:', error);
    }
}

// ============================================================================
// ERROR HANDLING
// ============================================================================

/**
 * Show error message to user
 */
function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'alert alert-danger alert-dismissible fade show';
    errorDiv.role = 'alert';
    errorDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-dismiss="alert"></button>
    `;

    // Insert at top of main content
    const mainContent = document.querySelector('.main-content');
    if (mainContent) {
        mainContent.insertBefore(errorDiv, mainContent.firstChild);
    }

    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        errorDiv.remove();
    }, 5000);
}

/**
 * Show success message to user
 */
function showSuccess(message) {
    const successDiv = document.createElement('div');
    successDiv.className = 'alert alert-success alert-dismissible fade show';
    successDiv.role = 'alert';
    successDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-dismiss="alert"></button>
    `;

    // Insert at top of main content
    const mainContent = document.querySelector('.main-content');
    if (mainContent) {
        mainContent.insertBefore(successDiv, mainContent.firstChild);
    }

    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        successDiv.remove();
    }, 5000);
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Format timestamp for display
 */
function formatTime(isoString) {
    if (!isoString) return '';
    const date = new Date(isoString);
    return date.toLocaleTimeString();
}

/**
 * Fetch with timeout
 */
async function fetchWithTimeout(url, options = {}, timeout = 10000) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    try {
        const response = await fetch(url, {
            ...options,
            signal: controller.signal
        });
        clearTimeout(timeoutId);
        return response;
    } catch (error) {
        clearTimeout(timeoutId);
        throw error;
    }
}

// ============================================================================
// PAGE LIFECYCLE
// ============================================================================

// Initialize app when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeApp);
} else {
    initializeApp();
}

// Cleanup on page unload
window.addEventListener('unload', function() {
    stopPolling();
});
