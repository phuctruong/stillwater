/**
 * Stillwater Admin Dojo — Wizard Form Handlers
 *
 * Handles:
 * - LLM Configuration Wizard (4 steps)
 * - Solace AGI Configuration Wizard (5 steps)
 * - Form validation (client-side)
 * - API submission and response handling
 */

// ============================================================================
// LLM WIZARD
// ============================================================================

/**
 * Open LLM Configuration Wizard
 */
function openLLMWizard() {
    const modal = document.getElementById('llmModal');
    if (!modal) return;

    // Reset wizard state
    goToLLMStep(1);

    // Show modal
    const bootstrapModal = new bootstrap.Modal(modal);
    bootstrapModal.show();
}

/**
 * Close LLM Wizard
 */
function closeLLMModal() {
    const modal = document.getElementById('llmModal');
    if (!modal) return;

    const bootstrapModal = bootstrap.Modal.getInstance(modal);
    if (bootstrapModal) {
        bootstrapModal.hide();
    }
}

/**
 * Navigate to a specific step in LLM wizard
 */
function goToLLMStep(stepNumber) {
    // Hide all steps
    document.querySelectorAll('#llmWizardSteps .wizard-step').forEach(step => {
        step.classList.remove('active');
    });

    // Show target step
    const targetStep = document.getElementById(`llmStep${stepNumber}`);
    if (targetStep) {
        targetStep.classList.add('active');

        // Update review screen if showing step 3
        if (stepNumber === 3) {
            updateLLMReview();
        }
    }
}

/**
 * Update LLM review screen with selected values
 */
function updateLLMReview() {
    const model = document.querySelector('input[name="model"]:checked')?.value || 'haiku';
    const autoStart = document.getElementById('autoStart')?.checked ? 'Enabled' : 'Disabled';

    document.getElementById('reviewModel').textContent = capitalizeFirst(model);
    document.getElementById('reviewAutoStart').textContent = autoStart;
}

/**
 * Save LLM configuration
 */
async function saveLLMConfig() {
    const model = document.querySelector('input[name="model"]:checked')?.value || 'haiku';
    const autoStart = document.getElementById('autoStart')?.checked || false;

    // Validate
    if (!model) {
        showError('Please select a model');
        return;
    }

    const btn = document.getElementById('btnSaveLLM');
    if (btn) {
        btn.disabled = true;
        btn.textContent = 'Saving...';
    }

    try {
        const response = await fetch('/api/llm/config', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                default_model: model,
                claude_code_enabled: true,
                auto_start_wrapper: autoStart
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const result = await response.json();

        // Show success step
        goToLLMStep(4);

        // Auto-close wizard after 2 seconds
        setTimeout(() => {
            closeLLMModal();
            // Refresh status dashboard
            fetchSystemStatus();
        }, 2000);

        showSuccess('✓ LLM configuration saved successfully');
    } catch (error) {
        console.error('Failed to save LLM config:', error);
        showError(`Failed to save configuration: ${error.message}`);

        if (btn) {
            btn.disabled = false;
            btn.textContent = 'Save Configuration';
        }
    }
}

// ============================================================================
// SOLACE AGI WIZARD
// ============================================================================

/**
 * Open Solace AGI Configuration Wizard
 */
function openSolaceWizard() {
    const modal = document.getElementById('solaceModal');
    if (!modal) return;

    // Reset wizard state
    goToSolaceStep(1);

    // Show modal
    const bootstrapModal = new bootstrap.Modal(modal);
    bootstrapModal.show();
}

/**
 * Close Solace AGI Wizard
 */
function closeSolaceModal() {
    const modal = document.getElementById('solaceModal');
    if (!modal) return;

    // Clear API key input for security
    const apiKeyInput = document.getElementById('apiKeyInput');
    if (apiKeyInput) {
        apiKeyInput.value = '';
    }

    const bootstrapModal = bootstrap.Modal.getInstance(modal);
    if (bootstrapModal) {
        bootstrapModal.hide();
    }
}

/**
 * Navigate to a specific step in Solace AGI wizard
 */
function goToSolaceStep(stepNumber) {
    // Hide all steps
    document.querySelectorAll('#solaceWizardSteps .wizard-step').forEach(step => {
        step.classList.remove('active');
    });

    // Show target step
    const targetStep = document.getElementById(`solaceStep${stepNumber}`);
    if (targetStep) {
        targetStep.classList.add('active');

        // Auto-trigger test on step 4
        if (stepNumber === 4) {
            testSolaceConnection();
        }
    }
}

/**
 * Test Solace AGI connection
 */
async function testSolaceConnection() {
    const apiKey = document.getElementById('apiKeyInput')?.value || '';

    // Validate API key format
    if (!apiKey || apiKey.length < 10) {
        showError('Please enter a valid API key');
        goToSolaceStep(3);
        return;
    }

    const resultsDiv = document.getElementById('testResults');
    const testMessage = document.getElementById('testMessage');
    const testButtons = document.getElementById('testButtons');

    if (resultsDiv) {
        resultsDiv.innerHTML = '<p class="text-muted">Testing connection...</p>';
    }
    if (testMessage) {
        testMessage.textContent = 'Testing Solace AGI connection...';
    }
    if (testButtons) {
        testButtons.style.display = 'none';
    }

    try {
        const response = await fetch('/api/solace-agi/test', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ api_key: apiKey })
        });

        const result = await response.json();

        if (response.ok) {
            // Success
            const testsHTML = `
                <div class="test-result-item">
                    <span class="test-result-icon success">✓</span>
                    <span>API key format valid</span>
                </div>
                <div class="test-result-item">
                    <span class="test-result-icon success">✓</span>
                    <span>Solace AGI connection successful</span>
                </div>
                <div class="test-result-item">
                    <span class="test-result-icon success">✓</span>
                    <span>All checks passed</span>
                </div>
            `;
            if (resultsDiv) {
                resultsDiv.innerHTML = testsHTML;
            }
            if (testMessage) {
                testMessage.textContent = '✓ All tests passed!';
            }

            // Store API key in session for next step
            sessionStorage.setItem('tempApiKey', apiKey);

            // Update review
            document.getElementById('reviewApiKey').textContent = '••••••••••';
        } else {
            // Error
            const errorMsg = result.error || result.detail || 'Connection test failed';
            const testsHTML = `
                <div class="test-result-item">
                    <span class="test-result-icon error">✗</span>
                    <span>${errorMsg}</span>
                </div>
            `;
            if (resultsDiv) {
                resultsDiv.innerHTML = testsHTML;
            }
            if (testMessage) {
                testMessage.textContent = '✗ Test failed. Please try again.';
            }
        }
    } catch (error) {
        console.error('Test failed:', error);
        const errorMsg = error.message || 'Network error or timeout';
        const testsHTML = `
            <div class="test-result-item">
                <span class="test-result-icon error">✗</span>
                <span>${errorMsg}</span>
            </div>
        `;
        if (resultsDiv) {
            resultsDiv.innerHTML = testsHTML;
        }
        if (testMessage) {
            testMessage.textContent = '✗ Connection failed. Please check your network.';
        }
    } finally {
        if (testButtons) {
            testButtons.style.display = 'flex';
        }
    }
}

/**
 * Save Solace AGI configuration
 */
async function saveSolaceConfig() {
    const apiKey = sessionStorage.getItem('tempApiKey') || document.getElementById('apiKeyInput')?.value || '';

    // Validate
    if (!apiKey || apiKey.length < 10) {
        showError('API key is missing or invalid');
        return;
    }

    const btn = document.getElementById('btnSaveSolace');
    if (btn) {
        btn.disabled = true;
        btn.textContent = 'Saving...';
    }

    try {
        const response = await fetch('/api/solace-agi/config', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                api_key: apiKey,
                auto_sync: true
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const result = await response.json();

        // Clear sensitive data from memory
        sessionStorage.removeItem('tempApiKey');
        document.getElementById('apiKeyInput').value = '';

        // Show success step
        goToSolaceStep(6);

        // Auto-close wizard after 2 seconds
        setTimeout(() => {
            closeSolaceModal();
            // Refresh status dashboard
            fetchSystemStatus();
        }, 2000);

        showSuccess('✓ Solace AGI configuration saved successfully');
    } catch (error) {
        console.error('Failed to save Solace config:', error);
        showError(`Failed to save configuration: ${error.message}`);

        if (btn) {
            btn.disabled = false;
            btn.textContent = 'Save Configuration';
        }
    }
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Capitalize first letter of string
 */
function capitalizeFirst(str) {
    if (!str) return '';
    return str.charAt(0).toUpperCase() + str.slice(1);
}

/**
 * Validate email format
 */
function isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

/**
 * Validate API key format (basic)
 */
function isValidApiKey(key) {
    return key && key.length >= 10;
}
