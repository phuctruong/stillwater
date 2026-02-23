const state = {
  catalog: null,
  group: null,
  activePath: "",
  user: null,
  idToken: null,
};

// Firebase initialization (lazy-loaded)
let auth = null;
let firebaseConfig = null;

async function initializeFirebase() {
  if (auth) return; // Already initialized

  try {
    const configResp = await fetch("/config");
    const config = await configResp.json();
    firebaseConfig = config.firebase;

    firebase.initializeApp(firebaseConfig);
    auth = firebase.auth();
    auth.onAuthStateChanged(handleAuthStateChanged);
    logLine("[Firebase] Initialized with project: " + firebaseConfig.projectId);
  } catch (e) {
    logLine("[Firebase] Initialization warning: " + e.message, "err");
  }
}

const PRIMARY_GROUP_IDS = ["root_skills", "swarms", "root_recipes", "papers", "recipes", "skills", "personas", "identity"];

function logLine(msg, kind = "ok") {
  const box = document.getElementById("logBox");
  const stamp = new Date().toISOString();
  const line = `[${stamp}] ${msg}\n`;
  box.textContent += line;
  box.scrollTop = box.scrollHeight;
  if (kind === "err") {
    console.error(msg);
  } else {
    console.log(msg);
  }
}

async function api(path, method = "GET", body = null) {
  const opts = { method, headers: {} };
  if (body !== null) {
    opts.headers["Content-Type"] = "application/json";
    opts.body = JSON.stringify(body);
  }
  const resp = await fetch(path, opts);
  const data = await resp.json().catch(() => ({}));
  if (!resp.ok || data.ok === false) {
    const err = data.error || `${resp.status} ${resp.statusText}`;
    throw new Error(err);
  }
  return data;
}

function setClock() {
  const el = document.getElementById("serverClock");
  el.textContent = new Date().toLocaleTimeString();
}

function catalogGroupById(id) {
  if (!state.catalog) return null;
  return state.catalog.groups.find((row) => row.id === id) || null;
}

function primaryGroups() {
  if (!state.catalog) return [];
  const byId = new Map(state.catalog.groups.map((g) => [g.id, g]));
  return PRIMARY_GROUP_IDS.map((id) => byId.get(id)).filter(Boolean);
}

function overflowGroups() {
  if (!state.catalog) return [];
  return state.catalog.groups.filter((g) => !PRIMARY_GROUP_IDS.includes(g.id));
}

function ensureValidGroupSelection() {
  const groups = primaryGroups();
  if (groups.length === 0) {
    state.group = null;
    return;
  }
  if (!state.group || !groups.find((g) => g.id === state.group)) {
    state.group = groups[0].id;
  }
}

function currentGroupFiles() {
  const g = catalogGroupById(state.group);
  return g ? g.files : [];
}

function renderGroupTabs() {
  const tabs = document.getElementById("groupTabs");
  tabs.innerHTML = "";
  const groups = primaryGroups();
  for (const group of groups) {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "tab-btn";
    if (group.id === state.group) btn.classList.add("active");
    btn.textContent = `${group.title} (${group.count})`;
    btn.onclick = () => {
      state.group = group.id;
      renderGroupTabs();
      renderFileList();
    };
    tabs.appendChild(btn);
  }
}

function renderFileList() {
  const ul = document.getElementById("fileList");
  ul.innerHTML = "";
  for (const row of currentGroupFiles()) {
    const li = document.createElement("li");
    li.textContent = row.path;
    li.dataset.path = row.path;
    if (row.path === state.activePath) li.classList.add("active");
    li.onclick = () => openFile(row.path);
    ul.appendChild(li);
  }
}

function renderExtraList() {
  const ul = document.getElementById("extraList");
  ul.innerHTML = "";
  if (!state.catalog) return;

  const rows = [];
  for (const group of overflowGroups()) {
    for (const file of group.files) {
      rows.push({
        path: file.path,
        label: `[${group.title}] ${file.path}`,
      });
    }
  }
  for (const extra of state.catalog.extras || []) {
    rows.push({
      path: extra.path,
      label: `[Quick] ${extra.path}`,
    });
  }
  for (const row of rows) {
    const li = document.createElement("li");
    li.textContent = row.label;
    li.dataset.path = row.path;
    if (row.path === state.activePath) li.classList.add("active");
    li.onclick = () => openFile(row.path);
    ul.appendChild(li);
  }
}

async function refreshCatalog() {
  const data = await api("/api/catalog");
  state.catalog = data;
  ensureValidGroupSelection();
  renderGroupTabs();
  renderFileList();
  renderExtraList();
  logLine("Catalog refreshed.");
}

async function openFile(path) {
  const data = await api(`/api/file?path=${encodeURIComponent(path)}`);
  state.activePath = data.path;
  document.getElementById("activePath").textContent = data.path;
  document.getElementById("fileEditor").value = data.content;
  renderFileList();
  renderExtraList();
  logLine(`Opened ${path}`);
}

async function saveFile() {
  if (!state.activePath) {
    logLine("No file selected.", "err");
    return;
  }
  const content = document.getElementById("fileEditor").value;
  await api("/api/file/save", "POST", { path: state.activePath, content });
  logLine(`Saved ${state.activePath}`);
}

async function createFile() {
  const group = state.group;
  const filename = document.getElementById("newFilename").value.trim();
  if (!group) {
    logLine("No tab group selected.", "err");
    return;
  }
  if (!filename) {
    logLine("Filename is required.", "err");
    return;
  }
  const data = await api("/api/file/create", "POST", { group, filename });
  logLine(`Created ${data.path}`);
  document.getElementById("newFilename").value = "";
  await refreshCatalog();
  await openFile(data.path);
}

function formatLlmStatus(status) {
  const lines = [];
  lines.push(`provider: ${status.provider || "-"}`);
  lines.push(`provider_name: ${status.provider_name || "-"}`);
  lines.push(`provider_url: ${status.provider_url || "-"}`);
  lines.push(`provider_model: ${status.provider_model || "-"}`);
  lines.push(`setup: ${status.setup_ok ? "OK" : "WARN"} (${status.setup_msg || "-"})`);
  lines.push(`ollama_installed: ${status.ollama_installed ? "yes" : "no"}`);
  lines.push(`preferred_ollama_url: ${status.preferred_ollama_url || "-"}`);
  lines.push(`models: ${(status.models || []).join(", ") || "-"}`);
  return lines.join("\n");
}

async function refreshLlmStatus() {
  const data = await api("/api/llm/status");
  document.getElementById("llmSummary").textContent = formatLlmStatus(data.status || {});
  document.getElementById("providerInput").value = data.status.provider || "";
  document.getElementById("ollamaUrlInput").value = data.status.preferred_ollama_url || data.status.provider_url || "";
  document.getElementById("ollamaModelInput").value = data.status.provider_model || "";
  logLine("LLM status refreshed.");
}

async function saveLlmConfig() {
  const provider = document.getElementById("providerInput").value;
  const ollama_url = document.getElementById("ollamaUrlInput").value;
  const ollama_model = document.getElementById("ollamaModelInput").value;
  const data = await api("/api/llm/config", "POST", { provider, ollama_url, ollama_model });
  document.getElementById("llmSummary").textContent = formatLlmStatus(data.status || {});
  logLine("LLM config saved.");
}

async function installOllama() {
  const sudo_password = document.getElementById("installSudoPwd").value;
  if (!sudo_password) {
    logLine("Sudo password required for install.", "err");
    return;
  }
  logLine("Installing Ollama. This can take a while...");
  const data = await api("/api/system/install-ollama", "POST", { sudo_password });
  logLine(`Install result: ${data.message} (rc=${data.returncode})`);
  if (data.stdout) logLine(`install stdout:\n${data.stdout}`);
  if (data.stderr) logLine(`install stderr:\n${data.stderr}`);
  document.getElementById("installSudoPwd").value = "";
  await refreshLlmStatus();
}

async function pullModel() {
  const model = document.getElementById("pullModelInput").value.trim();
  const ollama_url = document.getElementById("ollamaUrlInput").value.trim();
  if (!model) {
    logLine("Model is required.", "err");
    return;
  }
  logLine(`Pulling model ${model}...`);
  const data = await api("/api/ollama/pull", "POST", { model, ollama_url });
  logLine(`Model pull: ${data.message} (rc=${data.returncode})`);
  if (data.stdout) logLine(`pull stdout:\n${data.stdout}`);
  if (data.stderr) logLine(`pull stderr:\n${data.stderr}`);
  await refreshLlmStatus();
}

function formatCommunity(c) {
  const lines = [];
  lines.push(`linked: ${c.linked ? "yes" : "no"}`);
  lines.push(`email: ${c.email || "-"}`);
  lines.push(`api_key: ${c.api_key || "-"}`);
  lines.push(`status: ${c.link_status || "-"}`);
  lines.push(`login_link_stub: ${c.login_link_stub || "-"}`);
  lines.push(`sync_events: ${c.sync_events ?? 0}`);
  return lines.join("\n");
}

async function refreshCommunity() {
  const data = await api("/api/community/status");
  document.getElementById("communitySummary").textContent = formatCommunity(data.community || {});
  if (data.community && data.community.email) {
    document.getElementById("communityEmail").value = data.community.email;
  }
}

async function linkCommunity() {
  const email = document.getElementById("communityEmail").value.trim();
  if (!email) {
    logLine("Email is required.", "err");
    return;
  }
  const data = await api("/api/community/link", "POST", { email });
  logLine(`Community magic link stub generated for ${data.link.email}`);
  await refreshCommunity();
}

async function syncCommunity() {
  const direction = document.getElementById("syncDirection").value;
  const data = await api("/api/community/sync", "POST", { direction });
  const up = data.sync.uploaded || {};
  logLine(`Community sync complete: direction=${data.sync.direction}, recipes=${up.recipes ?? 0} (cli=${up.cli_recipes ?? 0} root=${up.root_recipes ?? 0}), skills=${up.skills ?? 0}`);
  await refreshCommunity();
}

async function runCliCommand() {
  const command = document.getElementById("cliCommand").value;
  logLine(`Running CLI command: ${command}...`);
  const data = await api("/api/cli/run", "POST", { command });
  const r = data.result || {};
  const out = [
    `command: ${r.command}`,
    `returncode: ${r.returncode}`,
    r.stdout ? `stdout:\n${r.stdout}` : "",
    r.stderr ? `stderr:\n${r.stderr}` : "",
  ].filter(Boolean).join("\n");
  document.getElementById("cliOutput").textContent = out;
  logLine(`CLI ${command}: ${data.ok ? "OK" : "FAIL"} (rc=${r.returncode})`);
}

// ============= Firebase Auth Functions =============

async function handleAuthStateChanged(user) {
  state.user = user;
  updateAuthUI();

  if (user) {
    try {
      state.idToken = await user.getIdToken();
      logLine(`[Auth] Logged in as ${user.email}`);
    } catch (e) {
      logLine(`[Auth] Failed to get ID token: ${e.message}`, "err");
    }
  }
}

function updateAuthUI() {
  const loginBtn = document.getElementById("loginBtn");
  const userMenu = document.getElementById("userMenu");
  const userEmail = document.getElementById("userEmail");

  if (state.user) {
    loginBtn.style.display = "none";
    userMenu.style.display = "flex";
    userEmail.textContent = state.user.email;
  } else {
    loginBtn.style.display = "block";
    userMenu.style.display = "none";
  }
}

function openAuthModal() {
  const modal = document.getElementById("authModal");
  modal.classList.add("active");
}

function closeAuthModal() {
  const modal = document.getElementById("authModal");
  modal.classList.remove("active");
}

async function loginWithGoogle() {
  if (!auth) await initializeFirebase();
  if (!auth) {
    logLine("Firebase not available", "err");
    return;
  }
  try {
    const provider = new firebase.auth.GoogleAuthProvider();
    provider.addScope("profile");
    provider.addScope("email");
    await auth.signInWithPopup(provider);
    closeAuthModal();
  } catch (e) {
    logLine(`[Auth] Google login failed: ${e.message}`, "err");
  }
}

async function loginWithGitHub() {
  if (!auth) await initializeFirebase();
  if (!auth) {
    logLine("Firebase not available", "err");
    return;
  }
  try {
    const provider = new firebase.auth.GithubAuthProvider();
    await auth.signInWithPopup(provider);
    closeAuthModal();
  } catch (e) {
    logLine(`[Auth] GitHub login failed: ${e.message}`, "err");
  }
}

async function logout() {
  try {
    await auth.signOut();
    state.idToken = null;
    logLine("[Auth] Logged out");
  } catch (e) {
    logLine(`[Auth] Logout failed: ${e.message}`, "err");
  }
}

// ============= API Key Generation Functions =============

function openApiKeyModal() {
  const modal = document.getElementById("apiKeyModal");
  modal.classList.add("active");
  resetApiKeyFlow();
}

function closeApiKeyModal() {
  const modal = document.getElementById("apiKeyModal");
  modal.classList.remove("active");
  resetApiKeyFlow();
}

function resetApiKeyFlow() {
  document.getElementById("verificationStep").style.display = "block";
  document.getElementById("socialVerifyStep").style.display = "none";
  document.getElementById("apiKeyStep").style.display = "none";
  document.getElementById("verifySocial").checked = false;
  document.getElementById("verifyPaid").checked = true;
  document.getElementById("socialPostUrl").value = "";
}

function showSocialVerifyStep() {
  document.getElementById("verificationStep").style.display = "none";
  document.getElementById("socialVerifyStep").style.display = "block";
}

function backToVerifyMethod() {
  document.getElementById("verificationStep").style.display = "block";
  document.getElementById("socialVerifyStep").style.display = "none";
}

async function proceedWithVerification() {
  const method = document.querySelector('input[name="verifyMethod"]:checked').value;

  if (method === "social") {
    showSocialVerifyStep();
  } else if (method === "paid") {
    // For MVP: assume paid account, skip validation and generate key
    await generateApiKeyAfterVerification();
  }
}

async function verifySocialPost() {
  const url = document.getElementById("socialPostUrl").value.trim();
  if (!url) {
    logLine("Please enter a URL", "err");
    return;
  }

  try {
    logLine("Verifying social post...");
    // Call backend to verify social post
    const response = await api("/api/verify/social", "POST", { url }, state.idToken);
    logLine(`Social post verification: ${response.status}`);
    await generateApiKeyAfterVerification();
  } catch (e) {
    logLine(`Verification failed: ${e.message}`, "err");
  }
}

async function generateApiKeyAfterVerification() {
  if (!state.idToken) {
    logLine("Not authenticated", "err");
    return;
  }

  try {
    logLine("Generating API key...");
    const response = await api("/api/keys/generate", "POST", {}, state.idToken);

    // Show API key
    document.getElementById("verificationStep").style.display = "none";
    document.getElementById("socialVerifyStep").style.display = "none";
    document.getElementById("apiKeyStep").style.display = "block";

    document.getElementById("apiKeyValue").textContent = response.api_key;
    document.getElementById("keyIdValue").textContent = response.key_id;
    document.getElementById("keyCreatedValue").textContent = new Date(response.created_at).toLocaleString();

    logLine(`[API Key] Generated key: ${response.key_prefix}...`);
  } catch (e) {
    logLine(`Failed to generate API key: ${e.message}`, "err");
  }
}

function copyApiKey() {
  const apiKey = document.getElementById("apiKeyValue").textContent;
  navigator.clipboard.writeText(apiKey).then(() => {
    logLine("API key copied to clipboard");
    document.getElementById("copyApiKeyBtn").textContent = "✓ Copied!";
    setTimeout(() => {
      document.getElementById("copyApiKeyBtn").textContent = "📋 Copy";
    }, 2000);
  });
}

// ============= Updated API helper with auth =============

async function api(path, method = "GET", body = null, idToken = null) {
  const opts = { method, headers: {} };

  if (idToken) {
    opts.headers["Authorization"] = `Bearer ${idToken}`;
  }

  if (body !== null && Object.keys(body).length > 0) {
    opts.headers["Content-Type"] = "application/json";
    opts.body = JSON.stringify(body);
  }

  const resp = await fetch(path, opts);
  const data = await resp.json().catch(() => ({}));

  if (!resp.ok || data.ok === false) {
    const err = data.error || data.detail || `${resp.status} ${resp.statusText}`;
    throw new Error(err);
  }

  return data;
}

function bindEvents() {
  document.getElementById("refreshCatalogBtn").onclick = () => run(refreshCatalog);
  document.getElementById("saveFileBtn").onclick = () => run(saveFile);
  document.getElementById("createFileBtn").onclick = () => run(createFile);

  document.getElementById("refreshLlmBtn").onclick = () => run(refreshLlmStatus);
  document.getElementById("saveLlmConfigBtn").onclick = () => run(saveLlmConfig);
  document.getElementById("installOllamaBtn").onclick = () => run(installOllama);
  document.getElementById("pullModelBtn").onclick = () => run(pullModel);

  document.getElementById("linkCommunityBtn").onclick = () => run(linkCommunity);
  document.getElementById("syncCommunityBtn").onclick = () => run(syncCommunity);
  document.getElementById("runCliBtn").onclick = () => run(runCliCommand);

  // Auth UI events
  document.getElementById("loginBtn").onclick = openAuthModal;
  document.getElementById("googleLoginBtn").onclick = loginWithGoogle;
  document.getElementById("githubLoginBtn").onclick = loginWithGitHub;
  document.getElementById("logoutBtn").onclick = logout;

  // API Key events
  document.getElementById("getApiKeyBtn").onclick = openApiKeyModal;
  document.getElementById("proceedVerifyBtn").onclick = proceedWithVerification;
  document.getElementById("verifySocialBtn").onclick = verifySocialPost;
  document.getElementById("backToMethodBtn").onclick = backToVerifyMethod;
  document.getElementById("copyApiKeyBtn").onclick = copyApiKey;
  document.getElementById("doneKeyBtn").onclick = closeApiKeyModal;
}

async function run(fn) {
  try {
    await fn();
  } catch (err) {
    logLine(`ERROR: ${err.message || err}`, "err");
  }
}

// Close modals when clicking outside
document.addEventListener("click", (e) => {
  const authModal = document.getElementById("authModal");
  const apiKeyModal = document.getElementById("apiKeyModal");

  if (e.target === authModal) {
    closeAuthModal();
  }
  if (e.target === apiKeyModal) {
    closeApiKeyModal();
  }
});

async function boot() {
  setClock();
  setInterval(setClock, 1000);
  bindEvents();

  // Initialize Firebase in background
  await run(initializeFirebase);
  updateAuthUI();

  await run(refreshCatalog);
  await run(refreshLlmStatus);
  await run(refreshCommunity);
  await run(async () => {
    const data = await api("/api/cli/commands");
    const sel = document.getElementById("cliCommand");
    sel.innerHTML = "";
    for (const cmd of (data.commands || [])) {
      const opt = document.createElement("option");
      opt.value = cmd;
      opt.textContent = cmd;
      sel.appendChild(opt);
    }
  });
  logLine("Stillwater Admin Dojo v0.2 ready.");
  if (auth) {
    logLine("Click 'Login with Google' in the header to connect your solaceagi.com account.");
  }
}

boot();
