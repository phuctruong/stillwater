/**
 * Stillwater CLI Chat Interface
 * Allows users to execute `stillwater cli` commands from the browser
 */

// State management
let commandHistory = [];
let historyIndex = -1;

/**
 * Initialize CLI Chat interface
 */
function initCLIChat() {
    const inputField = document.getElementById("cli-input");
    const sendButton = document.getElementById("cli-send-btn");
    const clearButton = document.getElementById("cli-clear-btn");

    if (!inputField || !sendButton) {
        console.log("CLI Chat elements not found, skipping initialization");
        return;
    }

    // Send button click
    sendButton.addEventListener("click", () => executeCLICommand());

    // Input field enter key
    inputField.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
            executeCLICommand();
        } else if (e.key === "ArrowUp") {
            e.preventDefault();
            navigateHistory(-1);
        } else if (e.key === "ArrowDown") {
            e.preventDefault();
            navigateHistory(1);
        }
    });

    // Clear button click
    if (clearButton) {
        clearButton.addEventListener("click", () => clearCLIOutput());
    }

    console.log("CLI Chat initialized");
}

/**
 * Execute CLI command via /api/cli/execute endpoint
 */
async function executeCLICommand() {
    const inputField = document.getElementById("cli-input");
    const outputDiv = document.getElementById("cli-output");

    if (!inputField || !outputDiv) {
        console.error("CLI elements not found");
        return;
    }

    const command = inputField.value.trim();
    if (!command) {
        return;
    }

    // Add to history
    commandHistory.push(command);
    historyIndex = -1;

    // Clear input
    inputField.value = "";
    inputField.focus();

    // Show command in output
    const commandLine = document.createElement("div");
    commandLine.className = "cli-command";
    commandLine.innerHTML = `<span class="cli-prompt">$</span> ${escapeHtml(command)}`;
    outputDiv.appendChild(commandLine);

    // Show loading state
    const loadingLine = document.createElement("div");
    loadingLine.className = "cli-loading";
    loadingLine.textContent = "Executing...";
    outputDiv.appendChild(loadingLine);

    try {
        const response = await fetch("/api/cli/execute", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                command: command,
                args: []
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();

        // Remove loading indicator
        outputDiv.removeChild(loadingLine);

        // Show output
        if (data.success) {
            const output = document.createElement("div");
            output.className = "cli-output";
            output.innerHTML = `<pre>${escapeHtml(data.output || "(no output)")}</pre>`;
            outputDiv.appendChild(output);
        } else {
            const error = document.createElement("div");
            error.className = "cli-error";
            error.innerHTML = `<pre>${escapeHtml(data.error || data.output || "Unknown error")}</pre>`;
            outputDiv.appendChild(error);
        }

        // Show status line
        const statusLine = document.createElement("div");
        statusLine.className = "cli-status";
        statusLine.textContent = `[${data.status}] ${data.duration_ms}ms`;
        outputDiv.appendChild(statusLine);

    } catch (error) {
        // Remove loading indicator
        if (outputDiv.contains(loadingLine)) {
            outputDiv.removeChild(loadingLine);
        }

        // Show error
        const errorLine = document.createElement("div");
        errorLine.className = "cli-error";
        errorLine.innerHTML = `<pre>Error: ${escapeHtml(error.message)}</pre>`;
        outputDiv.appendChild(errorLine);
    }

    // Scroll to bottom
    outputDiv.scrollTop = outputDiv.scrollHeight;
}

/**
 * Navigate through command history with arrow keys
 */
function navigateHistory(direction) {
    const inputField = document.getElementById("cli-input");
    if (!inputField || commandHistory.length === 0) {
        return;
    }

    historyIndex += direction;

    // Bounds checking
    if (historyIndex < -1) {
        historyIndex = -1;
    }
    if (historyIndex >= commandHistory.length) {
        historyIndex = commandHistory.length - 1;
    }

    // Update input field
    if (historyIndex === -1) {
        inputField.value = "";
    } else {
        inputField.value = commandHistory[commandHistory.length - 1 - historyIndex];
    }
}

/**
 * Clear CLI output
 */
function clearCLIOutput() {
    const outputDiv = document.getElementById("cli-output");
    if (outputDiv) {
        outputDiv.innerHTML = "";
    }
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

// Initialize when DOM is ready
if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initCLIChat);
} else {
    initCLIChat();
}
