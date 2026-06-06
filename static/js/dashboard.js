const state = {
  atsAnalysisId: null,
  interviewSessionId: null,
  studyPlanText: '',
  videoStream: null,
  mediaRecorder: null,
  recordedChunks: [],
};

const savedTheme = localStorage.getItem('careerprep-theme');
if (savedTheme === 'dark') {
  document.body.classList.add('dark');
}

function pretty(data) {
  return JSON.stringify(data, null, 2);
}

function escapeHtml(value) {
  return String(value ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}

function setOutput(id, data) {
  const element = document.getElementById(id);
  element.classList.remove('error-box');
  element.classList.remove('loading');
  element.textContent = typeof data === 'string' ? data : pretty(data);
}

function setLoading(id, message) {
  const element = document.getElementById(id);
  element.classList.remove('error-box');
  element.classList.add('loading');
  element.textContent = message;
}

function clearOutput(id) {
  const element = document.getElementById(id);
  element.classList.remove('error-box');
  element.classList.remove('loading');
  element.innerHTML = '';
}

function renderList(items, warning = false) {
  if (!items || !items.length) return '<span class="chip">None</span>';
  return items.map((item) => `<span class="chip${warning ? ' warning' : ''}">${escapeHtml(item)}</span>`).join('');
}

function renderBulletList(items) {
  if (!items || !items.length) return '<p>No issues found.</p>';
  return `<ul class="mini-list">${items.map((item) => `<li>${escapeHtml(item)}</li>`).join('')}</ul>`;
}

function renderDetailedReport(items) {
  if (!items || !items.length) return '<p>No detailed mistakes found yet.</p>';
  return `
    <div class="report-grid">
      ${items.map((item) => `
        <article class="report-item">
          <strong>${escapeHtml(item.area || 'Improvement area')}</strong>
          <dl>
            <dt>Mistake</dt>
            <dd>${escapeHtml(item.mistake || 'Needs more detail.')}</dd>
            <dt>Why it matters</dt>
            <dd>${escapeHtml(item.why_it_matters || 'This affects recruiter or interviewer confidence.')}</dd>
            <dt>What to change</dt>
            <dd>${escapeHtml(item.what_to_change || 'Make the answer more specific and evidence-based.')}</dd>
            <dt>Example fix</dt>
            <dd>${escapeHtml(item.example_fix || 'Add a concrete project example with measurable results.')}</dd>
          </dl>
        </article>
      `).join('')}
    </div>
  `;
}

function showError(id, result) {
  const element = document.getElementById(id);
  element.classList.remove('loading');
  element.classList.add('error-box');
  element.textContent = result.message || 'Something went wrong.';
}

function updateProgress() {
  const steps = [
    ['stepAts', Boolean(state.atsAnalysisId)],
    ['stepInterview', Boolean(state.interviewSessionId && document.getElementById('interviewScore').textContent !== '--')],
    ['stepPlan', Boolean(state.studyPlanText)],
  ];
  const done = steps.filter(([, value]) => value).length;
  steps.forEach(([id, value]) => document.getElementById(id).classList.toggle('done', value));
  document.getElementById('progressBar').style.width = `${Math.round((done / steps.length) * 100)}%`;
  document.getElementById('progressLabel').textContent = `${Math.round((done / steps.length) * 100)}%`;
}

function renderAtsResult(result) {
  const data = result.data;
  clearOutput('atsOutput');
  document.getElementById('atsOutput').innerHTML = `
    <div class="result-card">
      <div class="score-band">
        <div class="score-circle" style="--score:${data.score}"><span>${data.score}</span></div>
        <div>
          <h3>${escapeHtml(data.target_role)} resume match</h3>
          <p>Matched ${data.matched_keywords.length} keywords and found ${data.missing_keywords.length} priority gaps.</p>
        </div>
      </div>
      <h3>Matched keywords</h3>
      <div class="chip-row">${renderList(data.matched_keywords)}</div>
    </div>
    <div class="result-card">
      <h3>Missing keywords</h3>
      <div class="chip-row">${renderList(data.missing_keywords, true)}</div>
      <h3>Suggestions</h3>
      ${renderBulletList(data.improvement_suggestions)}
    </div>
    <div class="result-card">
      <h3>Detailed resume report</h3>
      ${renderDetailedReport(data.detailed_report)}
    </div>
  `;
}

function renderInterviewResult(result) {
  const data = result.data;
  clearOutput('interviewOutput');
  document.getElementById('interviewOutput').innerHTML = `
    <div class="result-card">
      <div class="score-band">
        <div class="score-circle" style="--score:${data.score}"><span>${data.score}</span></div>
        <div>
          <h3>${escapeHtml(data.role)} interview feedback</h3>
          <p>${escapeHtml(data.difficulty)} session with ${data.question_count} questions.</p>
        </div>
      </div>
      <div class="chip-row">
        <span class="chip">Communication ${data.feedback.communication_score || 0}</span>
        <span class="chip">Correctness ${data.feedback.correctness_score || 0}</span>
        <span class="chip">Confidence ${data.feedback.confidence_score || 0}</span>
      </div>
    </div>
    <div class="result-card">
      <h3>Improve next</h3>
      <div class="chip-row">${renderList(data.feedback.next_practice_topics || [], true)}</div>
      ${renderBulletList(data.feedback.improvements || [])}
    </div>
    <div class="result-card">
      <h3>Detailed interview report</h3>
      ${renderDetailedReport(data.feedback.detailed_report || data.feedback.per_question)}
    </div>
    <div class="result-card">
      <h3>Video interview tips</h3>
      ${renderBulletList(data.feedback.video_tips || [])}
    </div>
  `;
}

function renderPlanResult(result) {
  const data = result.data;
  const days = data.plan.days || [];
  state.studyPlanText = `${data.target_role} roadmap\n\n${days.map((day) => (
    `Day ${day.day}: ${day.title}\n${(day.tasks || []).map((task) => `- ${task}`).join('\n')}`
  )).join('\n\n')}`;
  clearOutput('planOutput');
  document.getElementById('planOutput').innerHTML = `
    <div class="result-card">
      <h3>${escapeHtml(data.target_role)} roadmap</h3>
      <p>${escapeHtml(data.plan.focus_summary || 'Personalized preparation plan generated.')}</p>
      <div class="chip-row">${renderList(data.weak_topics, true)}</div>
    </div>
    <div class="plan-list">
      ${days.map((day) => `
        <article class="day-card">
          <strong>Day ${day.day}: ${escapeHtml(day.title)}</strong>
          <small>${day.practice_minutes} minutes</small>
          ${renderBulletList(day.tasks || [])}
        </article>
      `).join('')}
    </div>
  `;
  updateProgress();
}

function formatDate(value) {
  if (!value) return 'Saved';
  return new Intl.DateTimeFormat(undefined, { month: 'short', day: 'numeric' }).format(new Date(value));
}

function activateTab(tabId) {
  document.querySelectorAll('.tab').forEach((item) => item.classList.toggle('active', item.dataset.tab === tabId));
  document.querySelectorAll('.panel').forEach((item) => item.classList.toggle('active', item.id === tabId));
}

function renderHistoryList(id, items, type, getTitle, getMeta, emptyText) {
  const container = document.getElementById(id);
  if (!items || !items.length) {
    container.innerHTML = `<p>${escapeHtml(emptyText)}</p>`;
    return;
  }
  container.innerHTML = items.map((item) => `
    <button class="history-item" data-history-type="${type}" data-history-id="${item.id}" type="button">
      <strong>${escapeHtml(getTitle(item))}</strong>
      <span>${escapeHtml(getMeta(item))}</span>
    </button>
  `).join('');
}

async function loadHistory() {
  const response = await fetch('/api/reports/history/');
  const result = await response.json();
  if (!result.success) return;
  renderHistoryList(
    'atsHistory',
    result.data.ats,
    'ats',
    (item) => item.target_role,
    (item) => `${item.score} score · ${formatDate(item.created_at)}`,
    'No saved resume scans yet.',
  );
  renderHistoryList(
    'interviewHistory',
    result.data.interviews,
    'interview',
    (item) => item.role,
    (item) => `${item.score} score · ${formatDate(item.created_at)}`,
    'No saved interviews yet.',
  );
  renderHistoryList(
    'planHistory',
    result.data.plans,
    'plan',
    (item) => item.target_role,
    (item) => `${(item.plan.days || []).length} days · ${formatDate(item.created_at)}`,
    'No saved study plans yet.',
  );
}

async function loadHistoryItem(type, id) {
  const endpoints = {
    ats: `/api/ats/analyses/${id}/`,
    interview: `/api/interview/sessions/${id}/`,
    plan: `/api/study-plan/plans/${id}/`,
  };
  const response = await fetch(endpoints[type]);
  const result = await response.json();
  if (!result.success) return;

  if (type === 'ats') {
    activateTab('ats');
    renderAtsResult(result);
    state.atsAnalysisId = result.data.id;
    document.getElementById('atsScore').textContent = result.data.score;
    document.getElementById('targetRole').value = result.data.target_role;
    document.getElementById('planRole').value = result.data.target_role;
  }

  if (type === 'interview') {
    activateTab('interview');
    renderInterviewResult(result);
    state.interviewSessionId = result.data.id;
    document.getElementById('interviewScore').textContent = result.data.score;
    document.getElementById('interviewRole').value = result.data.role;
    renderQuestions(result.data.questions || []);
  }

  if (type === 'plan') {
    activateTab('plan');
    renderPlanResult(result);
    document.getElementById('planRole').value = result.data.target_role;
  }

  updateProgress();
}

function renderQuestions(questions) {
  const container = document.getElementById('questions');
  container.innerHTML = '';
  questions.forEach((item) => {
    const wrapper = document.createElement('div');
    const prompt = document.createElement('p');
    const answer = document.createElement('textarea');

    wrapper.className = 'question-item';
    prompt.textContent = `${item.id}. ${item.question}`;
    answer.dataset.questionId = item.id;
    answer.placeholder = 'Type your answer';

    wrapper.append(prompt, answer);
    container.appendChild(wrapper);
  });
}

document.querySelectorAll('.tab').forEach((button) => {
  button.addEventListener('click', () => {
    activateTab(button.dataset.tab);
  });
});

document.querySelector('.history-panel').addEventListener('click', (event) => {
  const button = event.target.closest('[data-history-type]');
  if (!button) return;
  loadHistoryItem(button.dataset.historyType, button.dataset.historyId);
});

document.getElementById('refreshHistory').addEventListener('click', loadHistory);

document.querySelectorAll('.role-chip').forEach((button) => {
  button.addEventListener('click', () => {
    document.querySelectorAll('.role-chip').forEach((item) => item.classList.remove('active'));
    button.classList.add('active');
    const role = button.dataset.role;
    document.getElementById('targetRole').value = role;
    document.getElementById('interviewRole').value = role;
    document.getElementById('planRole').value = role;
  });
});

document.getElementById('themeToggle').addEventListener('click', () => {
  document.body.classList.toggle('dark');
  const isDark = document.body.classList.contains('dark');
  localStorage.setItem('careerprep-theme', isDark ? 'dark' : 'light');
  document.getElementById('themeToggle').textContent = isDark ? 'Light mode' : 'Dark mode';
});

document.getElementById('resumeFile').addEventListener('change', (event) => {
  const file = event.target.files[0];
  document.getElementById('fileName').textContent = file ? file.name : 'Optional. Pasted text gives the most accurate local analysis.';
});

document.getElementById('enableCamera').addEventListener('click', async () => {
  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    document.getElementById('videoStatus').textContent = 'Camera not supported';
    return;
  }
  try {
    state.videoStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
    document.getElementById('videoPreview').srcObject = state.videoStream;
    document.getElementById('videoStatus').textContent = 'Camera ready';
    document.getElementById('recordVideo').disabled = false;
  } catch (error) {
    document.getElementById('videoStatus').textContent = 'Camera permission blocked';
  }
});

document.getElementById('recordVideo').addEventListener('click', () => {
  if (!state.videoStream) return;
  const recordButton = document.getElementById('recordVideo');
  const status = document.getElementById('videoStatus');

  if (state.mediaRecorder && state.mediaRecorder.state === 'recording') {
    state.mediaRecorder.stop();
    recordButton.textContent = 'Start Recording';
    status.textContent = 'Recording saved';
    return;
  }

  state.recordedChunks = [];
  state.mediaRecorder = new MediaRecorder(state.videoStream);
  state.mediaRecorder.ondataavailable = (event) => {
    if (event.data.size > 0) state.recordedChunks.push(event.data);
  };
  state.mediaRecorder.onstop = () => {
    const blob = new Blob(state.recordedChunks, { type: 'video/webm' });
    const url = URL.createObjectURL(blob);
    const link = document.getElementById('downloadRecording');
    link.href = url;
    link.download = 'careerprep-video-interview.webm';
    link.hidden = false;
  };
  state.mediaRecorder.start();
  recordButton.textContent = 'Stop Recording';
  status.textContent = 'Recording...';
});

document.getElementById('runAts').addEventListener('click', async () => {
  const form = new FormData();
  form.append('target_role', document.getElementById('targetRole').value);
  form.append('candidate_name', document.getElementById('candidateName').value);
  form.append('resume_text', document.getElementById('resumeText').value);
  form.append('job_description', document.getElementById('jobDescription').value);
  const resumeFile = document.getElementById('resumeFile').files[0];
  if (resumeFile) form.append('resume', resumeFile);

  setLoading('atsOutput', 'Analyzing resume and job description...');
  const response = await fetch('/api/ats/analyze/', { method: 'POST', body: form });
  const result = await response.json();
  if (!result.success) {
    showError('atsOutput', result);
    return;
  }
  renderAtsResult(result);
  if (result.success) {
    state.atsAnalysisId = result.data.id;
    document.getElementById('atsScore').textContent = result.data.score;
    document.getElementById('planRole').value = result.data.target_role;
    updateProgress();
    loadHistory();
  }
});

document.getElementById('startInterview').addEventListener('click', async () => {
  const payload = {
    role: document.getElementById('interviewRole').value,
    difficulty: document.getElementById('difficulty').value,
    question_count: Number(document.getElementById('questionCount').value),
  };
  setLoading('interviewOutput', 'Generating interview questions...');
  const response = await fetch('/api/interview/start/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  const result = await response.json();
  if (!result.success) {
    showError('interviewOutput', result);
    return;
  }
  setOutput('interviewOutput', 'Questions ready. Submit your answers when finished.');

  state.interviewSessionId = result.data.id;
  document.getElementById('planRole').value = result.data.role;
  renderQuestions(result.data.questions);
  updateProgress();
  loadHistory();
});

document.getElementById('submitInterview').addEventListener('click', async () => {
  if (!state.interviewSessionId) {
    setOutput('interviewOutput', 'Start an interview first.');
    return;
  }
  const answers = Array.from(document.querySelectorAll('[data-question-id]')).map((field) => ({
    question_id: Number(field.dataset.questionId),
    answer: field.value,
  }));
  setLoading('interviewOutput', 'Evaluating your answers...');
  const response = await fetch(`/api/interview/sessions/${state.interviewSessionId}/submit/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ answers }),
  });
  const result = await response.json();
  if (!result.success) {
    showError('interviewOutput', result);
    return;
  }
  renderInterviewResult(result);
  if (result.success) {
    document.getElementById('interviewScore').textContent = result.data.score;
    updateProgress();
    loadHistory();
  }
});

document.getElementById('generatePlan').addEventListener('click', async () => {
  const payload = {
    target_role: document.getElementById('planRole').value,
    ats_analysis_id: state.atsAnalysisId,
    interview_session_id: state.interviewSessionId,
    days: Number(document.getElementById('planDays').value),
  };
  setLoading('planOutput', 'Building your study roadmap...');
  const response = await fetch('/api/study-plan/generate/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  const result = await response.json();
  if (!result.success) {
    showError('planOutput', result);
    return;
  }
  renderPlanResult(result);
  loadHistory();
});

document.getElementById('copyPlan').addEventListener('click', async () => {
  if (!state.studyPlanText) {
    setOutput('planOutput', 'Generate a plan first, then copy it.');
    return;
  }
  if (navigator.clipboard) {
    await navigator.clipboard.writeText(state.studyPlanText);
  } else {
    const textArea = document.createElement('textarea');
    textArea.value = state.studyPlanText;
    document.body.appendChild(textArea);
    textArea.select();
    document.execCommand('copy');
    textArea.remove();
  }
  const copyButton = document.getElementById('copyPlan');
  copyButton.textContent = 'Copied';
  setTimeout(() => {
    copyButton.textContent = 'Copy Plan';
  }, 1200);
});

updateProgress();
loadHistory();
document.getElementById('themeToggle').textContent = document.body.classList.contains('dark') ? 'Light mode' : 'Dark mode';
