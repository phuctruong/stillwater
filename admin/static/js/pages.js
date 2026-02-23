/**
 * Stillwater Multi-Page Dashboard Router
 * Handles page navigation, data loading, chart/table initialization
 *
 * Rung Target: 641
 * Version: 1.0.0
 */

// Global state
let currentPage = 'orchestration';
let pageData = {};
let dataTable = null;

/**
 * Main initialization on document ready
 */
document.addEventListener('DOMContentLoaded', async () => {
    console.log('Initializing Stillwater Dashboard...');

    try {
        // Load page list
        await loadPagesList();

        // Set up navigation click handlers
        setupNavigation();

        // Load and display initial page
        await loadPage('orchestration');

        // Set up periodic updates
        setInterval(() => {
            refreshPageMetrics();
        }, 30000); // Update every 30 seconds

        console.log('Dashboard ready');
    } catch (error) {
        console.error('Initialization error:', error);
        showNotification('Dashboard initialization failed: ' + error.message, 'error');
    }
});

/**
 * Fetch list of available pages
 */
async function loadPagesList() {
    try {
        const response = await fetch('/api/pages');
        if (!response.ok) throw new Error(`HTTP ${response.status}`);

        const data = await response.json();
        console.log('Pages loaded:', data.pages);
        return data.pages;
    } catch (error) {
        console.error('Error loading pages list:', error);
        throw error;
    }
}

/**
 * Set up navigation button click handlers
 */
function setupNavigation() {
    const navButtons = document.querySelectorAll('.nav-button');

    navButtons.forEach(button => {
        button.addEventListener('click', async (e) => {
            e.preventDefault();
            const pageName = button.getAttribute('data-page');

            // Update active button
            navButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');

            // Load page
            await loadPage(pageName);
        });
    });
}

/**
 * Load a specific page's data and render it
 */
async function loadPage(pageName) {
    try {
        console.log(`Loading page: ${pageName}`);

        // Update state
        currentPage = pageName;

        // Fetch page data from backend
        const response = await fetch(`/api/page/${pageName}/data`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);

        const data = await response.json();
        pageData = data;

        // Update page title
        document.getElementById('pageSubtitle').textContent = data.title;

        // Update chat prompt
        document.getElementById('chatPrompt').textContent = data.chat_prompt;
        document.getElementById('chatOutput').innerHTML = '<div class="chat-message system">Ready for input...</div>';
        document.getElementById('chatInput').value = '';

        // Render sections
        await renderReports(data.report_config);
        initializeDataTable(data.table_config.columns, data.table_config.data);
        renderMermaidDiagram(data.diagram_mermaid);
        populateInstructions(data.instructions);

        console.log(`Page loaded: ${pageName}`);
    } catch (error) {
        console.error(`Error loading page ${pageName}:`, error);
        showNotification(`Error loading page: ${error.message}`, 'error');
    }
}

/**
 * Render AmCharts reports
 */
async function renderReports(reportConfig) {
    const container = document.getElementById('reportsContainer');
    container.innerHTML = '';

    if (!reportConfig || !reportConfig.charts) {
        console.warn('No charts in report config');
        return;
    }

    // Apply AmCharts theme
    am4core.useTheme(am4themes_animated);

    reportConfig.charts.forEach((chartConfig, idx) => {
        const chartId = `chart-${currentPage}-${idx}`;
        const cardContainer = createChartContainer(chartId, chartConfig.title);
        container.appendChild(cardContainer);

        // Defer chart rendering to allow DOM to settle
        setTimeout(() => {
            renderChart(chartId, chartConfig);
        }, 100);
    });
}

/**
 * Render individual chart based on config
 */
function renderChart(containerId, chartConfig) {
    try {
        const container = document.getElementById(containerId);
        if (!container) {
            console.warn(`Container ${containerId} not found`);
            return;
        }

        const chart = am4core.create(containerId, am4charts.XYChart);

        // Configure chart based on type
        switch (chartConfig.type) {
            case 'pie':
                renderPieChart(containerId, chartConfig);
                break;
            case 'column':
                renderColumnChart(containerId, chartConfig);
                break;
            case 'line':
                renderLineChart(containerId, chartConfig);
                break;
            case 'area':
                renderAreaChart(containerId, chartConfig);
                break;
            case 'gauge':
                renderGaugeChart(containerId, chartConfig);
                break;
            default:
                console.warn(`Unknown chart type: ${chartConfig.type}`);
        }
    } catch (error) {
        console.error(`Error rendering chart ${containerId}:`, error);
    }
}

/**
 * Render pie chart
 */
function renderPieChart(containerId, config) {
    const chart = am4core.create(containerId, am4charts.PieChart);
    chart.data = config.data;

    const pieSeries = chart.series.push(new am4charts.PieSeries());
    pieSeries.dataFields.value = 'value';
    pieSeries.dataFields.category = 'name';

    pieSeries.slices.template.strokeWidth = 2;
    pieSeries.slices.template.stroke = am4core.color('#fff');

    // Add cursor
    chart.cursor = new am4charts.XYCursor();
    chart.cursor.behavior = 'zoomX';
}

/**
 * Render column chart
 */
function renderColumnChart(containerId, config) {
    const chart = am4core.create(containerId, am4charts.XYChart);
    chart.data = config.data;

    const categoryAxis = chart.xAxes.push(new am4charts.CategoryAxis());
    categoryAxis.dataFields.category = config.data[0] ? Object.keys(config.data[0])[0] : '';
    categoryAxis.renderer.tooltipLocation = 0.5;

    const valueAxis = chart.yAxes.push(new am4charts.ValueAxis());

    const series = chart.series.push(new am4charts.ColumnSeries());
    series.dataFields.valueY = config.data[0] ? Object.keys(config.data[0])[1] : '';
    series.dataFields.categoryX = categoryAxis.dataFields.category;
    series.columns.template.strokeWidth = 0;
    series.columns.template.raiseOnHover = true;

    // Add cursor
    chart.cursor = new am4charts.XYCursor();
}

/**
 * Render line chart
 */
function renderLineChart(containerId, config) {
    const chart = am4core.create(containerId, am4charts.XYChart);
    chart.data = config.data;

    const dateAxis = chart.xAxes.push(new am4charts.CategoryAxis());
    dateAxis.dataFields.category = config.data[0] ? Object.keys(config.data[0])[0] : '';
    dateAxis.renderer.tooltipLocation = 0.5;

    const valueAxis = chart.yAxes.push(new am4charts.ValueAxis());

    const series = chart.series.push(new am4charts.LineSeries());
    series.dataFields.valueY = config.data[0] ? Object.keys(config.data[0])[1] : '';
    series.dataFields.categoryX = dateAxis.dataFields.category;
    series.strokeWidth = 3;
    series.propertyFields.strokeDasharray = 'dashLength';

    // Add cursor
    chart.cursor = new am4charts.XYCursor();
    chart.cursor.behavior = 'zoomX';
}

/**
 * Render area chart
 */
function renderAreaChart(containerId, config) {
    const chart = am4core.create(containerId, am4charts.XYChart);
    chart.data = config.data;

    const dateAxis = chart.xAxes.push(new am4charts.CategoryAxis());
    dateAxis.dataFields.category = config.data[0] ? Object.keys(config.data[0])[0] : '';
    dateAxis.renderer.tooltipLocation = 0.5;

    const valueAxis = chart.yAxes.push(new am4charts.ValueAxis());

    const series = chart.series.push(new am4charts.LineSeries());
    series.dataFields.valueY = config.data[0] ? Object.keys(config.data[0])[1] : '';
    series.dataFields.categoryX = dateAxis.dataFields.category;
    series.fillOpacity = 0.3;
    series.strokeWidth = 2;

    // Add cursor
    chart.cursor = new am4charts.XYCursor();
    chart.cursor.behavior = 'zoomX';
}

/**
 * Render gauge chart
 */
function renderGaugeChart(containerId, config) {
    const chart = am4core.create(containerId, am4charts.GaugeChart);
    chart.innerRadius = am4core.percent(90);

    const axis = chart.xAxes.push(new am4charts.ValueAxis());
    axis.min = 0;
    axis.max = 100;
    axis.strictMinMax = true;

    const range = axis.axisRanges.create();
    range.value = config.value;
    range.grid.stroke = am4core.color('#e65100');
    range.grid.strokeOpacity = 1;

    const hand = chart.hands.push(new am4charts.ClockHand());
    hand.pin.disabled = true;
    hand.value = config.value;

    // Add text label
    const label = chart.createChild(am4core.Label);
    label.text = `${config.value}%`;
    label.fontSize = 24;
    label.fontWeight = 'bold';
    label.horizontalCenter = 'middle';
    label.verticalCenter = 'middle';
}

/**
 * Chat interface handler
 */
document.addEventListener('DOMContentLoaded', () => {
    const chatInput = document.getElementById('chatInput');
    const chatSendBtn = document.getElementById('chatSendBtn');
    const chatClearBtn = document.getElementById('chatClearBtn');

    if (chatSendBtn) {
        chatSendBtn.addEventListener('click', handleChatSend);
    }

    if (chatInput) {
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                handleChatSend();
            }
        });
    }

    if (chatClearBtn) {
        chatClearBtn.addEventListener('click', () => {
            document.getElementById('chatOutput').innerHTML = '<div class="chat-message system">Cleared. Ready for input...</div>';
            document.getElementById('chatInput').value = '';
        });
    }
});

/**
 * Handle chat message sending
 */
async function handleChatSend() {
    const input = document.getElementById('chatInput');
    const output = document.getElementById('chatOutput');
    const command = input.value.trim();

    if (!command) return;

    // Add user message to output
    const userMsg = document.createElement('div');
    userMsg.className = 'chat-message user';
    userMsg.textContent = command;
    output.appendChild(userMsg);

    // Clear input
    input.value = '';

    // Send to CLI API
    try {
        const response = await fetch('/api/cli/execute', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ command: command })
        });

        const result = await response.json();

        // Add bot response
        const botMsg = document.createElement('div');
        botMsg.className = 'chat-message bot';
        botMsg.textContent = result.output || result.error || '(no output)';
        output.appendChild(botMsg);

        // Auto-scroll to bottom
        output.scrollTop = output.scrollHeight;
    } catch (error) {
        const errorMsg = document.createElement('div');
        errorMsg.className = 'chat-message bot';
        errorMsg.textContent = `Error: ${error.message}`;
        output.appendChild(errorMsg);
    }
}

/**
 * Refresh page metrics (called periodically)
 */
async function refreshPageMetrics() {
    try {
        const response = await fetch(`/api/page/${currentPage}/metrics`);
        if (response.ok) {
            const data = await response.json();
            console.log('Metrics updated:', data.metrics);
            // Update UI with new metrics if needed
        }
    } catch (error) {
        console.warn('Error refreshing metrics:', error);
    }
}

/**
 * Show notification toast
 */
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    const bgColor = type === 'success' ? '#4caf50' : type === 'error' ? '#f44336' : '#2196f3';
    notification.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        padding: 1rem;
        background: ${bgColor};
        color: white;
        border-radius: 4px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        z-index: 1000;
        max-width: 300px;
    `;
    notification.textContent = message;
    document.body.appendChild(notification);

    setTimeout(() => {
        notification.remove();
    }, 3000);
}
