const authPanel = document.getElementById('authPanel');
const loginForm = document.getElementById('loginForm');
const registerForm = document.getElementById('registerForm');
const resetForm = document.getElementById('resetForm');
const authPage = document.getElementById('authPage');
const mainPage = document.getElementById('mainPage');
const dashboardPanel = document.getElementById('dashboardPanel');
const historyPanel = document.getElementById('historyPanel');
const assistantBadge = document.getElementById('assistantBadge');
const assistantCloseBtn = document.getElementById('assistantCloseBtn');

const emailInput = document.getElementById('emailInput');
const passwordInput = document.getElementById('passwordInput');
const loginBtn = document.getElementById('loginBtn');
const showRegisterBtn = document.getElementById('showRegisterBtn');
const showResetBtn = document.getElementById('showResetBtn');
const backToLoginBtn = document.getElementById('backToLoginBtn');
const backToLoginBtn2 = document.getElementById('backToLoginBtn2');
const registerBtn = document.getElementById('registerBtn');
const resetBtn = document.getElementById('resetBtn');
const logoutBtn = document.getElementById('logoutBtn');

const regNameInput = document.getElementById('regNameInput');
const regEmailInput = document.getElementById('regEmailInput');
const regPasswordInput = document.getElementById('regPasswordInput');
const resetEmailInput = document.getElementById('resetEmailInput');

const authMessage = document.getElementById('authMessage');
const registerMessage = document.getElementById('registerMessage');
const resetMessage = document.getElementById('resetMessage');
const uploadResult = document.getElementById('uploadResult');
const logList = document.getElementById('logList');
const jobList = document.getElementById('jobList');
const healthStatus = document.getElementById('healthStatus');
const assistantQuestion = document.getElementById('assistantQuestion');
const askBtn = document.getElementById('askBtn');
const assistantResponse = document.getElementById('assistantResponse');

const navDashboard = document.getElementById('navDashboard');
const navHistory = document.getElementById('navHistory');
const assistantClose = document.getElementById('assistantCloseBtn');

const pdfFiles = document.getElementById('pdfFiles');
const templateFile = document.getElementById('templateFile');
const uploadBtn = document.getElementById('uploadBtn');
const loadJobsBtn = document.getElementById('loadJobsBtn');


let authToken = null;
let currentUser = null;
let pollingId = null;

function showMessage(container, text, type = '') {
  container.textContent = text;
  container.className = `message ${type}`.trim();
}

function toJson(body) {
  return JSON.stringify(body);
}

async function fetchJson(url, options = {}) {
  const headers = new Headers(options.headers || {});
  if (authToken) {
    headers.set('Authorization', `Bearer ${authToken}`);
  }
  const opts = { ...options, headers };
  const response = await fetch(url, opts);
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const error = data.detail || data.message || response.statusText;
    throw new Error(error);
  }
  return data;
}

function setAuthView() {
  loginForm.classList.add('hidden');
  registerForm.classList.add('hidden');
  resetForm.classList.add('hidden');
}

function renderJobs(jobs) {
  if (!jobs || !jobs.length) {
    jobList.innerHTML = '<div class="job-card"><strong>No history</strong><div class="note">Upload a PDF and start an analysis job to see results here.</div></div>';
    return;
  }
  jobList.innerHTML = jobs.map(job => `
    <div class="job-card">
      <strong>${job.id}</strong>
      <div class="note">Status: ${job.status} • Updated: ${job.updated_at || job.created_at || 'n/a'}</div>
      <div class="note">Template: ${job.template || 'default'}</div>
      <div class="note">Files: ${JSON.parse(job.files || '[]').length} uploaded</div>
    </div>
  `).join('');
}

function updateHealth(status) {
  healthStatus.textContent = `${status.toUpperCase()} • Ready for procurement analytics`;
}

function showPage(pageId) {
  dashboardPanel.classList.toggle('hidden', pageId !== 'dashboard');
  historyPanel.classList.toggle('hidden', pageId !== 'history');
  navDashboard.classList.toggle('active', pageId === 'dashboard');
  navHistory.classList.toggle('active', pageId === 'history');
}

async function loadJobs() {
  try {
    const data = await fetchJson('/api/jobs');
    renderJobs(data.jobs || []);
    addLog('Loaded analysis history');
  } catch (err) {
    renderJobs([]);
    console.warn('History load failed', err);
    addLog(`History load failed: ${err.message}`);
  }
}

async function checkHealth() {
  try {
    const data = await fetchJson('/api/health');
    updateHealth(data.status);
  } catch (err) {
    healthStatus.textContent = 'Offline or unavailable';
    addLog('Health check failed');
  }
}

async function login() {
  showMessage(authMessage, 'Signing in...', '');
  try {
    const data = await fetchJson('/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: toJson({ email: emailInput.value.trim(), password: passwordInput.value.trim(), remember_me: true }),
    });
    authToken = data.access_token;
    currentUser = data.user;
    showMessage(authMessage, `Welcome back, ${currentUser.name}!`, 'success');
    authPage.classList.add('hidden');
    mainPage.classList.remove('hidden');
    showPage('dashboard');
    setAuthView();
    checkHealth();
    loadJobs();
    addLog('User logged in');
  } catch (err) {
    showMessage(authMessage, `Login failed: ${err.message}`, 'error');
  }
}

async function register() {
  showMessage(registerMessage, 'Creating account...', '');
  try {
    await fetchJson('/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: toJson({ name: regNameInput.value.trim(), email: regEmailInput.value.trim(), password: regPasswordInput.value.trim() }),
    });
    showMessage(registerMessage, 'Account created. You may now login.', 'success');
  } catch (err) {
    showMessage(registerMessage, `Registration failed: ${err.message}`, 'error');
  }
}

async function resetPassword() {
  showMessage(resetMessage, 'Sending reset request...', '');
  try {
    await fetchJson('/auth/forgot', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: toJson({ email: resetEmailInput.value.trim() }),
    });
    showMessage(resetMessage, 'Password reset requested. Check app storage/email logs.', 'success');
  } catch (err) {
    showMessage(resetMessage, `Request failed: ${err.message}`, 'error');
  }
}

async function uploadFiles() {
  if (!pdfFiles.files.length) {
    showMessage(uploadResult, 'Select at least one PDF file before uploading.', 'error');
    return;
  }
  const form = new FormData();
  for (const file of pdfFiles.files) {
    form.append('files', file);
  }
  if (templateFile.files.length) {
    form.append('template', templateFile.files[0]);
  }
  try {
    const data = await fetchJson('/api/upload', { method: 'POST', body: form });
    showMessage(uploadResult, `Upload complete. Job ID: ${data.job_id}`, 'success');
    addLog(`Uploaded files and created job ${data.job_id}`);
    loadJobs();
  } catch (err) {
    showMessage(uploadResult, `Upload failed: ${err.message}`, 'error');
    addLog(`Upload failed: ${err.message}`);
  }
}

function addLog(message) {
  const now = new Date().toLocaleString();
  const entry = document.createElement('div');
  entry.className = 'log-item';
  entry.innerHTML = `<strong>${now}</strong><div class="note">${message}</div>`;
  logList.prepend(entry);
}

function logout() {
  authToken = null;
  currentUser = null;
  mainPage.classList.add('hidden');
  authPage.classList.remove('hidden');
  setAuthView();
  loginForm.classList.remove('hidden');
  showMessage(authMessage, 'You have been logged out.', '');
}

assistantClose.addEventListener('click', () => assistantBadge.classList.toggle('hidden'));

navDashboard.addEventListener('click', () => showPage('dashboard'));
navHistory.addEventListener('click', () => showPage('history'));

async function askAssistant() {
  const question = assistantQuestion.value.trim();
  if (!question) {
    showMessage(assistantResponse, 'Enter a question for the AI assistant.', 'error');
    return;
  }
  showMessage(assistantResponse, 'Connecting to assistant...', '');
  try {
    const data = await fetchJson('/api/assistant', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: toJson({ question }),
    });
    showMessage(assistantResponse, data.answer, 'success');
    addLog(`Assistant answered: ${question}`);
  } catch (err) {
    showMessage(assistantResponse, `Assistant error: ${err.message}`, 'error');
    addLog(`Assistant error: ${err.message}`);
  }
}

loginBtn.addEventListener('click', login);
showRegisterBtn.addEventListener('click', () => {
  setAuthView();
  registerForm.classList.remove('hidden');
});
showResetBtn.addEventListener('click', () => {
  setAuthView();
  resetForm.classList.remove('hidden');
});
backToLoginBtn.addEventListener('click', () => {
  setAuthView();
  loginForm.classList.remove('hidden');
});
backToLoginBtn2.addEventListener('click', () => {
  setAuthView();
  loginForm.classList.remove('hidden');
});
registerBtn.addEventListener('click', register);
resetBtn.addEventListener('click', resetPassword);
logoutBtn.addEventListener('click', logout);
uploadBtn.addEventListener('click', uploadFiles);
loadJobsBtn.addEventListener('click', loadJobs);
askBtn.addEventListener('click', askAssistant);

setAuthView();
loginForm.classList.remove('hidden');
authPage.classList.remove('hidden');
mainPage.classList.add('hidden');
showPage('dashboard');
checkHealth();
