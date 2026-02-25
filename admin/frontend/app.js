/**
 * Stillwater Admin Dojo — app.js v2.0.0
 * Rewritten from first principles with Prime JavaScript patterns.
 *
 * Architecture: Single-file module with class-based services.
 * Merges: app.js + wizards.js + mermaid-handler.js
 *
 * Patterns:
 *   - Frozen CONFIG — no magic numbers anywhere
 *   - Structured Logger — prefixed, no raw console calls
 *   - Typed Errors — NetworkError extends AppError
 *   - APIClient — all fetch() calls go through one place
 *   - createState() — immutable, event-driven state
 *   - Pure DOM wiring — no inline onclick="" in HTML
 *   - mermaid.render() — not deprecated mermaid.contentLoaded()
 *   - Pure CSS modals — .show class, no Bootstrap dependency
 */

'use strict';

// ============================================================
// CONSTANTS (frozen — no magic numbers anywhere else)
// ============================================================

const CONFIG = Object.freeze({
  POLL_INTERVAL_MS:      5_000,
  ALERT_DISMISS_MS:      5_000,
  API_TIMEOUT_MS:        10_000,
  HEALTH_FAILURE_LIMIT:  3,
  GRAPH_TIMEOUT_MS:      10_000,
  SW_PATH:               '/sw.js',
  MERMAID_CDN_URL:       'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js',
  OFFLINE_GRAPH_MESSAGE: 'Start the server to view this diagram. Run: stillwater serve',
  MERMAID_SECURITY:      'antiscript',
  MERMAID_LOG_LEVEL:     'warn',
  TABS:                  ['dashboard', 'orchestration', 'skills', 'swarms', 'personas', 'recipes'],
  GRAPH_TABS:            ['orchestration', 'skills', 'swarms', 'personas', 'recipes'],
  STORAGE_KEY_TAB:       'sw-active-tab',
});

// ============================================================
// LOGGER (structured, prefixed — never use console directly)
// ============================================================

const Logger = Object.freeze({
  _prefix: '[Stillwater]',
  info(msg, ctx = {}) {
    console.log(
      `${this._prefix} ${msg}`,
      Object.keys(ctx).length ? ctx : ''
    );
  },
  warn(msg, ctx = {}) {
    console.warn(
      `${this._prefix} ${msg}`,
      Object.keys(ctx).length ? ctx : ''
    );
  },
  error(msg, err, ctx = {}) {
    console.error(
      `${this._prefix} ${msg}`,
      err,
      Object.keys(ctx).length ? ctx : ''
    );
  },
});

// ============================================================
// ERROR CLASSES (typed — never throw raw Error)
// ============================================================

class AppError extends Error {
  constructor(message, code = 'UNKNOWN', context = {}) {
    super(message);
    this.name = this.constructor.name;
    this.code = code;
    this.context = context;
  }
}

class NetworkError extends AppError {
  constructor(message, status, url) {
    super(message, 'NETWORK', { status, url });
    this.status = status;
    this.url = url;
  }
}

// ============================================================
// API CLIENT (all fetch() calls centralised here)
// ============================================================

class APIClient {
  constructor(baseURL = '') {
    this._baseURL = baseURL;
  }

  async get(path) {
    return this._request('GET', path, null);
  }

  async post(path, body) {
    return this._request('POST', path, body);
  }

  async _request(method, path, body) {
    const url = `${this._baseURL}${path}`;
    const controller = new AbortController();
    const timeoutId = setTimeout(
      () => controller.abort(),
      CONFIG.API_TIMEOUT_MS
    );

    try {
      const options = {
        method,
        signal: controller.signal,
        headers: {},
      };

      if (body !== null && body !== undefined) {
        options.headers['Content-Type'] = 'application/json';
        options.body = JSON.stringify(body);
      }

      const response = await fetch(url, options);
      clearTimeout(timeoutId);

      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        throw new NetworkError(
          data.error || data.detail || `HTTP ${response.status}`,
          response.status,
          url
        );
      }

      return data;
    } catch (err) {
      clearTimeout(timeoutId);
      if (err instanceof NetworkError) throw err;
      if (err.name === 'AbortError') {
        throw new NetworkError('Request timed out', 0, url);
      }
      throw new NetworkError(err.message, 0, url);
    }
  }
}

// ============================================================
// STATE MANAGER (immutable snapshots, event-driven)
// ============================================================

function createState(initial) {
  let _state = Object.freeze({ ...initial });
  const _listeners = [];

  return Object.freeze({
    get() {
      return _state;
    },
    set(updates) {
      _state = Object.freeze({ ..._state, ...updates });
      _listeners.forEach(fn => fn(_state));
      return _state;
    },
    subscribe(fn) {
      _listeners.push(fn);
      return function unsubscribe() {
        const idx = _listeners.indexOf(fn);
        if (idx !== -1) _listeners.splice(idx, 1);
      };
    },
  });
}

// ============================================================
// MODULE-LEVEL SINGLETONS
// ============================================================

const api = new APIClient();

const state = createState({
  activeTab:          'dashboard',
  serverOnline:       false,
  healthFailureCount: 0,
  isPolling:          false,
  llm:                null,
  solace:             null,
  skills:             null,
  swarms:             null,
  personas:           null,
  graphCache:         {},
});

const modalFocusState = {
  cleanupById: new Map(),
  triggerById: new Map(),
};

let _mermaidLoadPromise = null;
let _mermaidReady = false;

// ============================================================
// SERVER HEALTH
// ============================================================

async function checkHealth() {
  try {
    await api.get('/health');
    state.set({ serverOnline: true, healthFailureCount: 0 });
    renderServerStatus(true, 0);
    Logger.info('Server health OK');
  } catch (err) {
    const failureCount = state.get().healthFailureCount + 1;
    state.set({ serverOnline: false, healthFailureCount: failureCount });
    renderServerStatus(false, failureCount);
    Logger.warn('Server health check failed', {
      message: err.message,
      failureCount,
    });
  }
}

function renderServerStatus(online, failureCount = 0) {
  const el = document.getElementById('serverStatus');
  if (!el) return;

  if (online) {
    el.textContent = 'Server Online';
    el.classList.add('online');
    el.classList.remove('offline');
  } else {
    el.textContent = failureCount >= CONFIG.HEALTH_FAILURE_LIMIT
      ? 'Server Offline. Start stillwater with stillwater serve'
      : 'Connecting...';
    el.classList.add('offline');
    el.classList.remove('online');
    if (failureCount >= CONFIG.HEALTH_FAILURE_LIMIT) {
      renderOfflineUi();
    }
  }
}

async function retryHealth() {
  await Promise.all([
    checkHealth(),
    fetchStatus(),
  ]);
}

function isServerOffline() {
  const current = state.get();
  return !current.serverOnline && current.healthFailureCount >= CONFIG.HEALTH_FAILURE_LIMIT;
}

function renderOfflineUi() {
  const llmCard = document.getElementById('cardLLM');
  const llmStatus = document.getElementById('llmStatus');
  const llmDetail = document.getElementById('llmDetail');
  const solaceCard = document.getElementById('cardSolace');
  const solaceStatus = document.getElementById('solaceStatus');
  const solaceDetail = document.getElementById('solaceDetail');
  const skillsStatus = document.getElementById('skillsStatus');
  const skillsDetail = document.getElementById('skillsDetail');

  if (llmCard) llmCard.classList.remove('online');
  if (solaceCard) solaceCard.classList.remove('online');
  if (llmStatus) llmStatus.textContent = 'Unavailable — server offline';
  if (llmDetail) llmDetail.textContent = 'Start stillwater with stillwater serve';
  if (solaceStatus) solaceStatus.textContent = 'Unavailable — server offline';
  if (solaceDetail) solaceDetail.textContent = 'Start stillwater with stillwater serve';
  if (skillsStatus) skillsStatus.textContent = 'Unavailable — server offline';
  if (skillsDetail) skillsDetail.textContent = 'Start stillwater with stillwater serve';

  renderOfflineGraphStates();
}

function renderOfflineGraphStates() {
  CONFIG.GRAPH_TABS.forEach(name => {
    const container = document.getElementById(`mermaid-${name}`);
    if (!container) return;
    const hasRenderedGraph = !!container.querySelector('svg');
    if (!hasRenderedGraph) {
      container.innerHTML = `<p class="loading-text">${escapeHtml(CONFIG.OFFLINE_GRAPH_MESSAGE)}</p>`;
    }
  });
}

// ============================================================
// SYSTEM STATUS (sidebar cards)
// ============================================================

async function fetchStatus() {
  try {
    const [llm, solace, skills, swarms, personas] = await Promise.all([
      api.get('/api/llm/status').catch(err => {
        Logger.warn('LLM status unavailable', { message: err.message });
        return { online: false };
      }),
      api.get('/api/solace-agi/status').catch(err => {
        Logger.warn('Solace AGI status unavailable', { message: err.message });
        return { configured: false };
      }),
      api.get('/api/skills/list').catch(err => {
        Logger.warn('Skills status unavailable', { message: err.message });
        return { count: 0, skills: [] };
      }),
      api.get('/api/swarms/list').catch(err => {
        Logger.warn('Swarms status unavailable', { message: err.message });
        return { count: 0, skills: [] };
      }),
      api.get('/api/personas/list').catch(err => {
        Logger.warn('Personas status unavailable', { message: err.message });
        return { count: 0, skills: [] };
      }),
    ]);

    state.set({ llm, solace, skills, swarms, personas });
    renderStatus({ llm, solace, skills, swarms, personas });
  } catch (err) {
    Logger.error('Failed to fetch system status', err);
  }
}

function renderStatus({ llm, solace, skills, swarms, personas }) {
  if (isServerOffline()) {
    renderOfflineUi();
    renderHeroBadges({ skills, swarms, personas });
    return;
  }

  // --- LLM Portal card ---
  const llmCard   = document.getElementById('cardLLM');
  const llmStatus = document.getElementById('llmStatus');
  const llmDetail = document.getElementById('llmDetail');

  if (llm && llm.online) {
    llmCard.classList.add('online');
    llmStatus.textContent = 'Online';
    llmDetail.textContent = `Model: ${llm.default_model || 'Not set'}`;
  } else {
    llmCard.classList.remove('online');
    llmStatus.textContent = 'Not Configured';
    llmDetail.textContent = 'Click Configure to get started';
  }

  // --- Solace AGI card ---
  const solaceCard   = document.getElementById('cardSolace');
  const solaceStatus = document.getElementById('solaceStatus');
  const solaceDetail = document.getElementById('solaceDetail');

  if (solace && solace.configured) {
    solaceCard.classList.add('online');
    solaceStatus.textContent = 'Connected';
    solaceDetail.textContent = `Tier: ${solace.tier || 'Free'}`;
  } else {
    solaceCard.classList.remove('online');
    solaceStatus.textContent = 'Not Configured';
    solaceDetail.textContent = 'Optional cloud features';
  }

  // --- Skills Ecosystem card ---
  const skillsStatus = document.getElementById('skillsStatus');
  const skillsDetail = document.getElementById('skillsDetail');

  if (skills && skills.count > 0) {
    skillsStatus.textContent = `${skills.count} skills loaded`;
    skillsDetail.textContent = 'Ready to explore';
  } else {
    skillsStatus.textContent = 'Loading skills...';
    if (skillsDetail) skillsDetail.textContent = '';
  }

  renderHeroBadges({ skills, swarms, personas });
}

function renderHeroBadges({ skills, swarms, personas }) {
  const badgeSkills = document.getElementById('badgeSkillsCount');
  const badgeSwarms = document.getElementById('badgeSwarmsCount');
  const badgePersonas = document.getElementById('badgePersonasCount');

  if (isServerOffline()) {
    if (badgeSkills) badgeSkills.textContent = 'Skills: --';
    if (badgeSwarms) badgeSwarms.textContent = 'Swarms: --';
    if (badgePersonas) badgePersonas.textContent = 'Personas: --';
    return;
  }

  if (badgeSkills) {
    const count = Number(skills && skills.count);
    badgeSkills.textContent = Number.isFinite(count) ? `Skills: ${count}` : 'Skills: --';
  }

  if (badgeSwarms) {
    const count = Number(swarms && swarms.count);
    badgeSwarms.textContent = Number.isFinite(count) ? `Swarms: ${count}` : 'Swarms: --';
  }

  if (badgePersonas) {
    const count = Number(personas && personas.count);
    badgePersonas.textContent = Number.isFinite(count) ? `Personas: ${count}` : 'Personas: --';
  }
}

// ============================================================
// TAB NAVIGATION
// ============================================================

function setupTabs() {
  // Tab buttons
  document.querySelectorAll('[data-tab]').forEach(btn => {
    btn.addEventListener('click', () => switchTab(btn.dataset.tab));
  });

  // Hero cards with data-navigate
  document.querySelectorAll('[data-navigate]').forEach(card => {
    card.setAttribute('role', 'button');
    card.setAttribute('tabindex', '0');

    card.addEventListener('click', () => handleNavigate(card.dataset.navigate));

    card.addEventListener('keydown', e => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        handleNavigate(card.dataset.navigate);
      }
    });
  });

  // Restore saved tab
  const saved = localStorage.getItem(CONFIG.STORAGE_KEY_TAB);
  if (saved && CONFIG.TABS.includes(saved)) {
    switchTab(saved);
  }
}

function handleNavigate(target) {
  if (!target) return;
  if (target.startsWith('http')) {
    window.open(target, '_blank', 'noopener,noreferrer');
  } else if (CONFIG.TABS.includes(target)) {
    switchTab(target);
  }
}

function switchTab(name) {
  if (!CONFIG.TABS.includes(name)) return;

  document.querySelectorAll('[data-tab]').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.tab === name);
  });

  document.querySelectorAll('.tab-pane').forEach(pane => {
    pane.classList.toggle('active', pane.id === `tab-${name}`);
  });

  state.set({ activeTab: name });
  localStorage.setItem(CONFIG.STORAGE_KEY_TAB, name);

  if (CONFIG.GRAPH_TABS.includes(name)) {
    loadGraph(name);
  }

  Logger.info('Tab switched', { name });
}

// ============================================================
// MERMAID GRAPHS
// ============================================================

function initMermaid() {
  if (_mermaidReady) return true;
  if (typeof mermaid === 'undefined') return false;

  const css = getComputedStyle(document.documentElement);
  const token = name => css.getPropertyValue(name).trim();

  mermaid.initialize({
    startOnLoad:   false,
    theme:         'dark',
    securityLevel: CONFIG.MERMAID_SECURITY,
    logLevel:      CONFIG.MERMAID_LOG_LEVEL,
    themeVariables: {
      primaryColor:        token('--bg-medium'),
      primaryTextColor:    token('--text-primary'),
      primaryBorderColor:  token('--sw-teal'),
      lineColor:           token('--text-muted'),
      secondBkgColor:      token('--bg-dark'),
      tertiaryBkgColor:    token('--sw-dark-teal'),
      tertiaryTextColor:   token('--text-secondary'),
      noteBkgColor:        token('--sw-dark-teal'),
      noteBorderColor:     token('--sw-teal'),
      noteTextColor:       token('--text-primary'),
      mainBkg:             token('--bg-medium'),
      nodeBorder:          token('--sw-teal'),
      clusterBkg:          token('--bg-dark'),
      clusterBorder:       token('--sw-teal'),
      titleColor:          token('--sw-cyan'),
      edgeLabelBackground: token('--bg-medium'),
      actorBkg:            token('--bg-medium'),
      actorBorder:         token('--sw-teal'),
      actorTextColor:      token('--text-primary'),
      signalColor:         token('--sw-teal'),
    },
    flowchart: { useMaxWidth: true, curve: 'basis' },
  });

  _mermaidReady = true;
  Logger.info('Mermaid.js initialised (theme tokens from CSS)');
  return true;
}

async function loadMermaidIfNeeded() {
  if (_mermaidReady) return true;

  if (typeof mermaid !== 'undefined') {
    return initMermaid();
  }

  if (!_mermaidLoadPromise) {
    _mermaidLoadPromise = new Promise((resolve, reject) => {
      const script = document.createElement('script');
      script.src = CONFIG.MERMAID_CDN_URL;
      script.onload = resolve;
      script.onerror = reject;
      document.head.appendChild(script);
    });
  }

  try {
    await _mermaidLoadPromise;
    return initMermaid();
  } catch (err) {
    _mermaidLoadPromise = null;
    Logger.warn('Failed to load Mermaid.js from CDN', { message: err.message });
    return false;
  }
}

async function loadGraph(name) {
  const container = document.getElementById(`mermaid-${name}`);
  if (!container) return;
  clearCachedBadge(container);

  let timedOut = false;
  const loadingTimeout = setTimeout(() => {
    timedOut = true;
    showGraphError(container, 'Diagram loading timed out after 10 seconds. Please retry.');
  }, CONFIG.GRAPH_TIMEOUT_MS);

  try {
    const mermaidLoaded = await loadMermaidIfNeeded();
    if (!mermaidLoaded) {
      if (!timedOut) {
        showGraphError(container, 'Mermaid.js failed to load. Check your connection and retry.');
      }
      return;
    }

    // Serve from cache if available
    const cache = state.get().graphCache;
    if (cache[name]) {
      await renderMermaidInto(container, cache[name]);
      return;
    }

    const data = await api.get(`/api/mermaid/${name}`);
    if (timedOut) return;

    if (data && data.graph_syntax) {
      state.set({
        graphCache: { ...state.get().graphCache, [name]: data.graph_syntax },
      });
      await renderMermaidInto(container, data.graph_syntax);
      if (data._sw_cached) {
        showCachedBadge(container);
      }
    } else {
      showGraphError(container, `No diagram data returned for "${name}"`);
    }
  } catch (err) {
    Logger.warn(`Failed to load graph: ${name}`, { message: err.message });
    if (!timedOut) {
      showGraphError(
        container,
        isServerOffline()
          ? CONFIG.OFFLINE_GRAPH_MESSAGE
          : 'Failed to load diagram. Is the server running?'
      );
    }
  } finally {
    clearTimeout(loadingTimeout);
  }
}

async function renderMermaidInto(container, syntax) {
  if (typeof mermaid === 'undefined') {
    showGraphError(container, 'Mermaid.js not available');
    return;
  }

  // Unique ID prevents collisions on repeated renders
  const renderId = `mermaid-r-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`;

  try {
    const { svg } = await mermaid.render(renderId, syntax);
    container.innerHTML = svg;
  } catch (err) {
    Logger.warn('Mermaid render failed', { message: err.message });
    showGraphError(container, 'Diagram syntax error — check server logs');
  }
}

function showGraphError(container, message) {
  clearCachedBadge(container);
  container.innerHTML = `<p class="loading-text">${escapeHtml(message)}</p>`;
}

function showCachedBadge(container) {
  clearCachedBadge(container);
  const badge = document.createElement('span');
  badge.className = 'cache-badge';
  badge.textContent = 'Cached';
  container.appendChild(badge);
}

function clearCachedBadge(container) {
  container.querySelectorAll('.cache-badge').forEach(badge => badge.remove());
}

// ============================================================
// STATUS POLLING
// ============================================================

let _pollHandle = null;

function startPolling() {
  if (state.get().isPolling) return;
  state.set({ isPolling: true });

  _pollHandle = setInterval(async () => {
    if (document.hidden) return;
    try {
      await fetchStatus();
    } catch (err) {
      Logger.warn('Polling refresh failed', { message: err.message });
    }
  }, CONFIG.POLL_INTERVAL_MS);

  Logger.info('Polling started', { intervalMs: CONFIG.POLL_INTERVAL_MS });
}

function stopPolling() {
  if (_pollHandle !== null) {
    clearInterval(_pollHandle);
    _pollHandle = null;
  }
  state.set({ isPolling: false });
  Logger.info('Polling stopped');
}

function handleVisibilityChange() {
  if (!document.hidden && !state.get().isPolling) {
    startPolling();
  }
}

// ============================================================
// ALERTS
// ============================================================

function showAlert(type, message) {
  const el = document.createElement('div');
  el.className = `alert alert-${type}`;
  const text = document.createElement('span');
  text.className = 'alert-message';
  text.textContent = message;
  el.appendChild(text);

  // Insert into content area (above tab-bar if any)
  const content = document.querySelector('.content');
  if (content) {
    content.insertBefore(el, content.firstChild);
  }

  if (type === 'error') {
    const closeBtn = document.createElement('button');
    closeBtn.className = 'alert-close';
    closeBtn.type = 'button';
    closeBtn.setAttribute('aria-label', 'Dismiss error');
    closeBtn.textContent = '×';
    closeBtn.addEventListener('click', () => {
      if (el.parentNode) el.parentNode.removeChild(el);
    });
    el.appendChild(closeBtn);
    return;
  }

  setTimeout(() => {
    if (el.parentNode) el.parentNode.removeChild(el);
  }, CONFIG.ALERT_DISMISS_MS);
}

// ============================================================
// MODAL HELPERS (pure CSS — no Bootstrap)
// ============================================================

function getFocusableIn(modal) {
  return Array.from(modal.querySelectorAll(
    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
  )).filter(el => !el.disabled && el.offsetParent !== null);
}

function trapFocus(modal, id) {
  const onKeydown = event => {
    if (event.key !== 'Tab') return;
    const focusable = getFocusableIn(modal);
    if (focusable.length === 0) {
      event.preventDefault();
      modal.focus();
      return;
    }

    const first = focusable[0];
    const last = focusable[focusable.length - 1];

    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();
      return;
    }

    if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  };

  modal.addEventListener('keydown', onKeydown);
  modalFocusState.cleanupById.set(id, () => {
    modal.removeEventListener('keydown', onKeydown);
  });
}

function getModalNoticeEl(id) {
  const modal = document.getElementById(id);
  if (!modal) return null;
  return modal.querySelector('.modal-notice');
}

function clearModalNotice(id) {
  const notice = getModalNoticeEl(id);
  if (!notice) return;
  notice.className = 'modal-notice';
  notice.textContent = '';
}

function showModalNotice(id, type, message) {
  const notice = getModalNoticeEl(id);
  if (!notice) return;
  notice.className = `modal-notice modal-notice-${type}`;
  notice.textContent = message;
}

function openModal(id, triggerElement = document.activeElement) {
  const modal = document.getElementById(id);
  if (!modal) return;
  const existingCleanup = modalFocusState.cleanupById.get(id);
  if (existingCleanup) existingCleanup();
  clearModalNotice(id);

  if (triggerElement instanceof HTMLElement) {
    modalFocusState.triggerById.set(id, triggerElement);
  }

  modal.classList.add('show');
  modal.setAttribute('aria-hidden', 'false');
  trapFocus(modal, id);

  const focusable = getFocusableIn(modal);
  if (focusable.length > 0) {
    focusable[0].focus();
  } else {
    modal.focus();
  }
}

function closeModal(id) {
  const modal = document.getElementById(id);
  if (!modal) return;

  modal.classList.remove('show');
  modal.setAttribute('aria-hidden', 'true');

  const cleanup = modalFocusState.cleanupById.get(id);
  if (cleanup) {
    cleanup();
    modalFocusState.cleanupById.delete(id);
  }

  const trigger = modalFocusState.triggerById.get(id);
  if (trigger && document.contains(trigger)) {
    trigger.focus();
  }
  modalFocusState.triggerById.delete(id);
  clearModalNotice(id);
}

// Close modal on overlay background click
function setupModalBackdropClose(modalId) {
  const modal = document.getElementById(modalId);
  if (!modal) return;
  modal.addEventListener('click', e => {
    if (e.target === modal) closeModal(modalId);
  });
}

// ============================================================
// LLM WIZARD
// ============================================================

function openLLMWizard() {
  openModal('llmModal');
}

function closeLLMModal() {
  closeModal('llmModal');
}

async function saveLLMConfig() {
  const selected = document.querySelector('input[name="llmModel"]:checked');
  if (!selected) {
    showAlert('error', 'Please select a model before saving.');
    return;
  }
  const btn = document.getElementById('btnSaveLLM');
  if (btn && btn.disabled) return;
  const originalLabel = btn ? btn.textContent : 'Save Configuration';
  if (btn) {
    btn.disabled = true;
    btn.textContent = 'Saving...';
  }

  const autoStartEl = document.getElementById('autoStart');

  const payload = {
    default_model:          selected.value,
    claude_code_enabled:    true,
    auto_start_wrapper:     autoStartEl ? autoStartEl.checked : false,
  };

  try {
    await api.post('/api/llm/config', payload);
    showModalNotice('llmModal', 'success', 'Configuration saved. You can close this dialog when ready.');
    await fetchStatus();
  } catch (err) {
    Logger.error('Failed to save LLM config', err);
    showModalNotice('llmModal', 'error', `Save failed: ${err.message}`);
    showAlert('error', `Save failed: ${err.message}`);
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.textContent = originalLabel;
    }
  }
}

// ============================================================
// SOLACE AGI WIZARD
// ============================================================

function openSolaceWizard() {
  openModal('solaceModal');
}

function closeSolaceModal() {
  const input = document.getElementById('solaceApiKey');
  if (input) input.value = '';
  closeModal('solaceModal');
}

async function saveSolaceConfig() {
  const input = document.getElementById('solaceApiKey');
  const key = input ? input.value.trim() : '';

  if (key.length < 10) {
    showAlert('error', 'Please enter a valid API key (minimum 10 characters).');
    return;
  }
  const btn = document.getElementById('btnSaveSolace');
  if (btn && btn.disabled) return;
  const originalLabel = btn ? btn.textContent : 'Connect';
  if (btn) {
    btn.disabled = true;
    btn.textContent = 'Connecting...';
  }

  try {
    await api.post('/api/solace-agi/config', { api_key: key, auto_sync: true });
    if (input) input.value = '';
    showModalNotice('solaceModal', 'success', 'Connection saved. You can close this dialog when ready.');
    await fetchStatus();
  } catch (err) {
    Logger.error('Failed to save Solace AGI config', err);
    showModalNotice('solaceModal', 'error', `Connection failed: ${err.message}`);
    showAlert('error', `Connection failed: ${err.message}`);
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.textContent = originalLabel;
    }
  }
}

// ============================================================
// DOM WIRING (no inline onclick="" — all wired here)
// ============================================================

function wireDOMEvents() {
  const btnRetryHealth = document.getElementById('btnRetryHealth');
  if (btnRetryHealth) btnRetryHealth.addEventListener('click', retryHealth);

  // Sidebar configure buttons
  const btnConfigLLM    = document.getElementById('btnConfigLLM');
  const btnConfigSolace = document.getElementById('btnConfigSolace');
  if (btnConfigLLM)    btnConfigLLM.addEventListener('click', openLLMWizard);
  if (btnConfigSolace) btnConfigSolace.addEventListener('click', openSolaceWizard);

  // LLM modal buttons
  const btnCloseLLM  = document.getElementById('btnCloseLLM');
  const btnSaveLLM   = document.getElementById('btnSaveLLM');
  const btnCancelLLM = document.getElementById('btnCancelLLM');
  if (btnCloseLLM)  btnCloseLLM.addEventListener('click', closeLLMModal);
  if (btnSaveLLM)   btnSaveLLM.addEventListener('click', saveLLMConfig);
  if (btnCancelLLM) btnCancelLLM.addEventListener('click', closeLLMModal);

  // Solace modal buttons
  const btnCloseSolace  = document.getElementById('btnCloseSolace');
  const btnSaveSolace   = document.getElementById('btnSaveSolace');
  const btnCancelSolace = document.getElementById('btnCancelSolace');
  if (btnCloseSolace)  btnCloseSolace.addEventListener('click', closeSolaceModal);
  if (btnSaveSolace)   btnSaveSolace.addEventListener('click', saveSolaceConfig);
  if (btnCancelSolace) btnCancelSolace.addEventListener('click', closeSolaceModal);

  // Allow Enter key in Solace API key field
  const solaceApiKeyInput = document.getElementById('solaceApiKey');
  if (solaceApiKeyInput) {
    solaceApiKeyInput.addEventListener('keydown', e => {
      if (e.key === 'Enter') saveSolaceConfig();
    });
  }

  // Escape key closes any open modal
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape') {
      closeModal('llmModal');
      closeModal('solaceModal');
    }
  });

  // Backdrop click to close
  setupModalBackdropClose('llmModal');
  setupModalBackdropClose('solaceModal');

  Logger.info('DOM events wired');
}

// ============================================================
// UTILITY
// ============================================================

function escapeHtml(str) {
  if (!str) return '';
  const div = document.createElement('div');
  div.textContent = String(str);
  return div.innerHTML;
}

async function initServiceWorker() {
  if (!('serviceWorker' in navigator)) {
    Logger.warn('Service worker not supported');
    return;
  }

  try {
    const registration = await navigator.serviceWorker.register(CONFIG.SW_PATH);
    Logger.info('Service worker registered', {
      scope: registration.scope,
    });
  } catch (err) {
    Logger.warn('Service worker registration failed', {
      message: err.message,
    });
  }
}

// ============================================================
// INIT
// ============================================================

async function init() {
  Logger.info('Initialising Admin Dojo v2.0.0');

  try {
    initServiceWorker();
    wireDOMEvents();
    setupTabs();

    // Parallel: health + status (both non-blocking for UI)
    await Promise.all([
      checkHealth(),
      fetchStatus(),
    ]);

    startPolling();
    document.addEventListener('visibilitychange', handleVisibilityChange);
    Logger.info('Initialisation complete');
  } catch (err) {
    Logger.error('Initialisation failed', err);
    showAlert('error', 'Failed to initialise. Please refresh the page.');
  }
}

// Bootstrap
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}

window.addEventListener('unload', () => {
  document.removeEventListener('visibilitychange', handleVisibilityChange);
  stopPolling();
});
