const uploadBtn = document.getElementById('uploadBtn');
const analyzeBtn = document.getElementById('analyzeBtn');
const statusBtn = document.getElementById('statusBtn');
const downloadBtn = document.getElementById('downloadBtn');
const pdfFiles = document.getElementById('pdfFiles');
const uploadResult = document.getElementById('uploadResult');
const jobResult = document.getElementById('jobResult');
const logOutput = document.getElementById('logOutput');
const jobIdInput = document.getElementById('jobIdInput');
let pollingId = null;

function log(message, error = false) {
  const prefix = error ? 'ERROR: ' : '';
  logOutput.value += `${prefix}${message}\n`;
  logOutput.scrollTop = logOutput.scrollHeight;
}

function showMessage(container, html) {
  container.innerHTML = html;
}

async function fetchJson(url, options = {}) {
  const res = await fetch(url, options);
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const detail = data.detail || res.statusText;
    throw new Error(detail);
  }
  return data;
}

function formatStatus(data) {
  let html = `<strong>Status:</strong> ${data.status}`;
  if (data.output) {
    html += `<br/><strong>Output:</strong> ${data.output}`;
    html += `<br/><a class="link" href="${data.download_url}" target="_blank">Download result</a>`;
  }
  return html;
}

async function checkStatus(jobId) {
  const status = await fetchJson(`/status/${encodeURIComponent(jobId)}`);
  showMessage(jobResult, formatStatus(status));
  log(`Status ${jobId}: ${status.status}`);
  return status;
}

uploadBtn.addEventListener('click', async () => {
  if (!pdfFiles.files.length) {
    showMessage(uploadResult, '<span class="error">Choose at least one PDF file.</span>');
    return;
  }

  const formData = new FormData();
  for (const file of pdfFiles.files) {
    formData.append('files', file);
  }

  try {
    const data = await fetchJson('/upload', { method: 'POST', body: formData });
    showMessage(uploadResult, `<span class="success">Uploaded ${data.files.length} file(s). Job ID: ${data.job_id}</span>`);
    jobIdInput.value = data.job_id;
    log(`Uploaded files for job ${data.job_id}`);
  } catch (err) {
    showMessage(uploadResult, `<span class="error">Upload failed: ${err.message}</span>`);
    log(`Upload failed: ${err.message}`, true);
  }
});

analyzeBtn.addEventListener('click', async () => {
  const jobId = jobIdInput.value.trim();
  if (!jobId) {
    showMessage(jobResult, '<span class="error">Enter a job ID first.</span>');
    return;
  }

  try {
    const data = await fetchJson(`/analyze?job_id=${encodeURIComponent(jobId)}`, { method: 'POST' });
    showMessage(jobResult, `<span class="success">Analysis started for job ${data.job_id}.</span>`);
    log(`Analysis requested for job ${data.job_id}`);

    if (pollingId) {
      clearInterval(pollingId);
    }
    pollingId = setInterval(async () => {
      try {
        const status = await checkStatus(jobId);
        if (!['running', 'queued'].includes(status.status)) {
          clearInterval(pollingId);
          pollingId = null;
        }
      } catch (err) {
        clearInterval(pollingId);
        pollingId = null;
      }
    }, 4000);
  } catch (err) {
    showMessage(jobResult, `<span class="error">Analyze failed: ${err.message}</span>`);
    log(`Analyze failed: ${err.message}`, true);
  }
});

statusBtn.addEventListener('click', async () => {
  const jobId = jobIdInput.value.trim();
  if (!jobId) {
    showMessage(jobResult, '<span class="error">Enter a job ID first.</span>');
    return;
  }
  try {
    await checkStatus(jobId);
  } catch (err) {
    showMessage(jobResult, `<span class="error">Status check failed: ${err.message}</span>`);
    log(`Status check error: ${err.message}`, true);
  }
});

downloadBtn.addEventListener('click', () => {
  const jobId = jobIdInput.value.trim();
  if (!jobId) {
    showMessage(jobResult, '<span class="error">Enter a job ID first.</span>');
    return;
  }
  window.location.href = `/download/${encodeURIComponent(jobId)}`;
});
