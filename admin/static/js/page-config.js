/**
 * Stillwater Multi-Page Configuration
 * Defines page structure, chart types, table columns, mermaid diagrams
 *
 * Rung Target: 641
 * Version: 1.0.0
 */

// Page configuration constants
const PAGE_CONFIG = {
    orchestration: {
        title: "Orchestration",
        subtitle: "Triple Twin: Explorer, Builder, Arbiter"
    },
    swarms: {
        title: "Swarm Nodes",
        subtitle: "Distributed task execution with Coder, Planner, Scout, Skeptic"
    },
    cpu: {
        title: "CPU Nodes",
        subtitle: "Algorithm performance, latency, throughput"
    },
    llm: {
        title: "LLM Settings",
        subtitle: "Model selection, token costs, provider uptime"
    },
    sync: {
        title: "Solace AGI Sync",
        subtitle: "Cloud backup, Firestore integration, data sync status"
    }
};

// AmCharts theme configuration
const AMCHARTS_CONFIG = {
    animated: true,
    theme: "animated",
    colors: [
        "#01579b", // Primary blue
        "#e65100", // Accent orange
        "#1b5e20", // Success green
        "#f57f17", // Warning yellow
        "#4a148c", // Purple
        "#c41c3b", // Red
        "#00838f", // Teal
        "#5d4037"  // Brown
    ]
};

// DataTables configuration defaults
const DATATABLE_CONFIG = {
    paging: true,
    pageLength: 10,
    searching: true,
    ordering: true,
    info: true,
    responsive: true,
    autoWidth: true,
    dom: '<"dataTables_wrapper"<"dataTables_filter"f><"dataTables_info"i><t><"dataTables_paginate"p>>'
};

/**
 * Initialize chart container with unique ID
 */
function createChartContainer(chartId, title) {
    const container = document.createElement('div');
    container.className = 'report-card';
    container.innerHTML = `
        <h3>${title}</h3>
        <div id="${chartId}" class="report-chart"></div>
    `;
    return container;
}

/**
 * Initialize DataTable from config
 */
function initializeDataTable(columns, data) {
    // Clear existing DataTable if present
    if ($.fn.dataTable.isDataTable('#dataTable')) {
        $('#dataTable').DataTable().destroy();
    }

    // Clear table header and body
    $('#dataTable thead tr').html('');
    $('#dataTable tbody').html('');

    // Add column headers
    const headerRow = $('#dataTable thead tr');
    columns.forEach(col => {
        headerRow.append(`<th>${col.title}</th>`);
    });

    // Add data rows
    const tbody = $('#dataTable tbody');
    data.forEach(row => {
        let rowHtml = '<tr>';
        columns.forEach(col => {
            const value = row[col.data] || '';
            rowHtml += `<td>${value}</td>`;
        });
        rowHtml += '</tr>';
        tbody.append(rowHtml);
    });

    // Initialize DataTable
    $('#dataTable').DataTable(DATATABLE_CONFIG);
}

/**
 * Render Mermaid diagram
 */
function renderMermaidDiagram(mermaidSyntax) {
    const container = document.getElementById('mermaidContainer');
    container.innerHTML = '';

    // Create mermaid div
    const mermaidDiv = document.createElement('div');
    mermaidDiv.className = 'mermaid';
    mermaidDiv.textContent = mermaidSyntax;
    container.appendChild(mermaidDiv);

    // Initialize Mermaid
    try {
        mermaid.contentLoaded();
        mermaid.run();
    } catch (e) {
        console.warn('Mermaid render warning:', e);
    }
}

/**
 * Populate instructions section
 */
function populateInstructions(instructions) {
    const container = document.getElementById('instructionsContainer');
    container.innerHTML = '';

    instructions.forEach((instr, idx) => {
        const card = document.createElement('div');
        card.className = 'instruction-card';

        let content = `<h4><span class="instruction-step">${instr.step}</span>${instr.title}</h4>`;

        if (instr.description) {
            content += `<p>${instr.description}</p>`;
        }

        if (instr.file) {
            content += `<div class="instruction-code">${instr.file}</div>`;
            content += `<button class="instruction-button" onclick="openInVSCode('${instr.file}')">🥋 ${instr.button}</button>`;
        }

        if (instr.command) {
            content += `<div class="instruction-code">$ ${instr.command}</div>`;
        }

        card.innerHTML = content;
        container.appendChild(card);
    });
}

/**
 * Open file in VSCode via API
 */
async function openInVSCode(filePath) {
    try {
        const response = await fetch('/api/vscode/open', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ file: filePath })
        });

        const result = await response.json();

        if (result.success) {
            console.log('VSCode opened:', result.message);
            // Show toast notification
            showNotification(result.message, 'success');
        } else {
            console.error('VSCode open failed:', result.message);
            showNotification(result.message, 'error');
        }
    } catch (error) {
        console.error('Error opening VSCode:', error);
        showNotification(`Error: ${error.message}`, 'error');
    }
}

/**
 * Show toast notification
 */
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        padding: 1rem;
        background: ${type === 'success' ? '#4caf50' : type === 'error' ? '#f44336' : '#2196f3'};
        color: white;
        border-radius: 4px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        z-index: 1000;
        animation: slideIn 0.3s ease;
    `;
    notification.textContent = message;
    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

/**
 * Format large numbers with comma separators
 */
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

/**
 * Format currency
 */
function formatCurrency(num) {
    return '$' + num.toFixed(2);
}

/**
 * Update clock display
 */
function updateClock() {
    const now = new Date();
    const timeStr = now.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
    const clock = document.getElementById('serverClock');
    if (clock) {
        clock.textContent = timeStr;
    }
}

// Update clock every second
setInterval(updateClock, 1000);
updateClock();
