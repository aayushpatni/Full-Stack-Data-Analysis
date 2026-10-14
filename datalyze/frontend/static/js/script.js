// ── STATE ─────────────────────────────────────────────────────────────────────
let currentUser = null;
let analysisData = null;
let timerInterval = null;
let timerSeconds = 0;

// ── INIT ──────────────────────────────────────────────────────────────────────
async function init() {
  try {
    const res = await fetch('/api/me');
    const data = await res.json();
    if (data.authenticated) {
      currentUser = data.user;
      showDashboard();
    }
  } catch(e) {}
}

init();

// ── AUTH TABS ─────────────────────────────────────────────────────────────────
function switchTab(tab) {
  document.querySelectorAll('.tab-btn').forEach((b, i) => {
    b.classList.toggle('active', (tab === 'login' && i === 0) || (tab === 'register' && i === 1));
  });
  document.getElementById('login-form').style.display = tab === 'login' ? '' : 'none';
  document.getElementById('register-form').style.display = tab === 'register' ? '' : 'none';
}

// ── REGISTER ──────────────────────────────────────────────────────────────────
async function doRegister() {
  const name = document.getElementById('r-name').value.trim();
  const email = document.getElementById('r-email').value.trim();
  const password = document.getElementById('r-password').value;
  const msg = document.getElementById('reg-msg');

  if (!name || !email || !password) return showMsg(msg, 'All fields required', 'error');
  if (password.length < 6) return showMsg(msg, 'Password must be at least 6 characters', 'error');

  showMsg(msg, '<span class="spin"></span> Sending OTP…', 'info');
  try {
    const res = await fetch('/api/register', {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({name, email, password})
    });
    const data = await res.json();
    if (data.success) {
      document.getElementById('reg-email-display').textContent = email;
      document.getElementById('reg-step-1').style.display = 'none';
      document.getElementById('reg-step-2').style.display = '';
      if (data.demo_otp) {
        document.getElementById('r-otp').value = data.demo_otp;
      }
      showMsg(msg, data.message, 'success');
    } else {
      showMsg(msg, data.message, 'error');
    }
  } catch(e) { showMsg(msg, 'Network error', 'error'); }
}

async function doVerifyOtp() {
  const email = document.getElementById('r-email').value.trim();
  const otp = document.getElementById('r-otp').value.trim();
  const msg = document.getElementById('reg-msg');
  if (otp.length !== 6) return showMsg(msg, 'Enter the 6-digit OTP', 'error');

  showMsg(msg, '<span class="spin"></span> Verifying…', 'info');
  try {
    const res = await fetch('/api/verify-otp', {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({email, otp})
    });
    const data = await res.json();
    if (data.success) {
      currentUser = data.user;
      showMsg(msg, '✅ Account created!', 'success');
      setTimeout(showDashboard, 800);
    } else {
      showMsg(msg, data.message, 'error');
    }
  } catch(e) { showMsg(msg, 'Network error', 'error'); }
}

// ── LOGIN ─────────────────────────────────────────────────────────────────────
async function doLogin() {
  const email = document.getElementById('l-email').value.trim();
  const password = document.getElementById('l-password').value;
  const msg = document.getElementById('login-msg');
  if (!email || !password) return showMsg(msg, 'Please fill all fields', 'error');

  showMsg(msg, '<span class="spin"></span> Sending OTP…', 'info');
  try {
    const res = await fetch('/api/login', {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({email, password})
    });
    const data = await res.json();
    if (data.success) {
      document.getElementById('login-email-display').textContent = email;
      document.getElementById('login-step-1').style.display = 'none';
      document.getElementById('login-step-2').style.display = '';
      if (data.demo_otp) {
        document.getElementById('l-otp').value = data.demo_otp;
      }
      showMsg(msg, data.message, 'success');
    } else {
      showMsg(msg, data.message, 'error');
    }
  } catch(e) { showMsg(msg, 'Network error', 'error'); }
}

async function doLoginVerify() {
  const email = document.getElementById('l-email').value.trim();
  const otp = document.getElementById('l-otp').value.trim();
  const msg = document.getElementById('login-msg');
  if (otp.length !== 6) return showMsg(msg, 'Enter the 6-digit OTP', 'error');

  showMsg(msg, '<span class="spin"></span> Verifying…', 'info');
  try {
    const res = await fetch('/api/login-verify', {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({email, otp})
    });
    const data = await res.json();
    if (data.success) {
      currentUser = data.user;
      showMsg(msg, '✅ Logged in!', 'success');
      setTimeout(showDashboard, 600);
    } else {
      showMsg(msg, data.message, 'error');
    }
  } catch(e) { showMsg(msg, 'Network error', 'error'); }
}

async function doLogout() {
  await fetch('/api/logout', {method: 'POST'});
  currentUser = null;
  analysisData = null;
  showPage('auth-page');
  resetLoginForms();
}

function resetLoginForms() {
  document.getElementById('login-step-1').style.display = '';
  document.getElementById('login-step-2').style.display = 'none';
  document.getElementById('reg-step-1').style.display = '';
  document.getElementById('reg-step-2').style.display = 'none';
  ['l-email','l-password','l-otp','r-name','r-email','r-password','r-otp']
    .forEach(id => { const el = document.getElementById(id); if(el) el.value = ''; });
  document.getElementById('login-msg').style.display = 'none';
  document.getElementById('reg-msg').style.display = 'none';
  switchTab('login');
}

// ── DASHBOARD ─────────────────────────────────────────────────────────────────
function showDashboard() {
  showPage('dashboard-page');
  updateUserUI();
  resetToUpload();
}

function updateUserUI() {
  if (!currentUser) return;
  document.getElementById('streak-count').textContent = currentUser.streak;
  document.getElementById('dd-name').textContent = currentUser.name;
  document.getElementById('dd-email').textContent = currentUser.email;
  document.getElementById('dd-streak').textContent = currentUser.streak;
  document.getElementById('modal-streak').textContent = currentUser.streak;
}

function showPage(id) {
  document.querySelectorAll('.page').forEach(p => {
    p.classList.remove('active');
    p.style.display = 'none';
  });
  const target = document.getElementById(id);
  if (target) {
    target.classList.add('active');
    target.style.display = (id === 'auth-page') ? 'flex' : 'block';
  }
  window.scrollTo(0, 0);
}

function toggleDropdown() {
  document.getElementById('user-dropdown').classList.toggle('open');
}

document.addEventListener('click', (e) => {
  if (!e.target.closest('.user-menu-wrapper'))
    document.getElementById('user-dropdown').classList.remove('open');
});

// ── FILE UPLOAD ────────────────────────────────────────────────────────────────
function dragOver(e) { e.preventDefault(); document.getElementById('upload-zone').classList.add('drag-over'); }
function dragLeave(e) { document.getElementById('upload-zone').classList.remove('drag-over'); }
function dropFile(e) {
  e.preventDefault();
  document.getElementById('upload-zone').classList.remove('drag-over');
  const f = e.dataTransfer.files[0];
  if (f) uploadFile(f);
}

function handleFile(e) {
  const f = e.target.files[0];
  if (f) uploadFile(f);
}

async function uploadFile(file) {
  const allowed = ['csv','xlsx','xls','json'];
  const ext = file.name.split('.').pop().toLowerCase();
  if (!allowed.includes(ext)) {
    alert('Please upload a CSV, Excel, or JSON file');
    return;
  }

  startTimer();

  const fd = new FormData();
  fd.append('file', file);

  try {
    const res = await fetch('/api/upload', {method: 'POST', body: fd});
    const data = await res.json();
    stopTimer();

    if (data.success) {
      analysisData = data;
      currentUser.streak = data.streak;
      updateUserUI();
      showResults(data);
      if (data.streak > 0) setTimeout(showStreakModal, 800);
    } else {
      alert('Error: ' + data.message);
    }
  } catch(e) {
    stopTimer();
    alert('Upload failed. Is the server running?');
  }
}

// ── TIMER ─────────────────────────────────────────────────────────────────────
function startTimer() {
  timerSeconds = 0;
  document.getElementById('timer-overlay').classList.add('show');
  setStepActive(0);

  timerInterval = setInterval(() => {
    timerSeconds++;
    document.getElementById('timer-number').textContent = timerSeconds + 's';
    // Animate progress (cap at 95% while loading)
    const pct = Math.min(timerSeconds / 30, 0.95);
    const offset = 502 - (502 * pct);
    document.getElementById('progress-circle').style.strokeDashoffset = offset;
    // Step progression
    if (timerSeconds === 2) setStepActive(1);
    if (timerSeconds === 5) setStepActive(2);
  }, 1000);
}

function stopTimer() {
  clearInterval(timerInterval);
  document.getElementById('progress-circle').style.strokeDashoffset = 0;
  setStepDone(3);
  setTimeout(() => {
    document.getElementById('timer-overlay').classList.remove('show');
  }, 700);
}

function setStepActive(i) {
  const steps = document.querySelectorAll('.timer-step');
  steps.forEach((s, idx) => {
    if (idx < i) s.className = 'timer-step done';
    else if (idx === i) s.className = 'timer-step active';
    else s.className = 'timer-step';
  });
}

function setStepDone(upTo) {
  document.querySelectorAll('.timer-step').forEach((s, i) => {
    s.className = i <= upTo ? 'timer-step done' : 'timer-step';
  });
}

// ── RESULTS ───────────────────────────────────────────────────────────────────
function showResults(data) {
  document.getElementById('upload-section').style.display = 'none';
  const rs = document.getElementById('results-section');
  rs.classList.add('show');

  const s = data.summary;
  document.getElementById('results-title').textContent = `📊 ${s.filename} — Analysis`;

  // Stat cards
  const sg = document.getElementById('stats-grid');
  sg.innerHTML = '';
  const cards = [
    {v: s.rows.toLocaleString(), l: 'Total Rows'},
    {v: s.columns, l: 'Columns'},
    {v: s.numeric_cols, l: 'Numeric'},
    {v: s.categorical_cols, l: 'Categorical'},
    {v: s.missing_pct + '%', l: 'Missing Data'},
    {v: s.duplicates, l: 'Duplicates'},
    {v: s.memory_kb + ' KB', l: 'Memory'},
    {v: data.analysis_time + 's', l: 'Analysis Time'},
  ];
  cards.forEach((c, i) => {
    const d = document.createElement('div');
    d.className = 'stat-card';
    d.style.animationDelay = (i * 0.05) + 's';
    d.innerHTML = `<div class="s-value">${c.v}</div><div class="s-label">${c.l}</div>`;
    sg.appendChild(d);
  });

  // Insights
  const il = document.getElementById('insights-list');
  il.innerHTML = '';
  data.insights.forEach((ins, i) => {
    const d = document.createElement('div');
    d.className = 'insight-item';
    d.style.animationDelay = (i * 0.06) + 's';
    d.textContent = ins;
    il.appendChild(d);
  });

  // Charts
  const cg = document.getElementById('charts-grid');
  cg.innerHTML = '';
  data.charts.forEach((ch, i) => {
    const card = document.createElement('div');
    card.className = 'chart-card';
    card.style.animationDelay = (i * 0.08) + 's';
    card.innerHTML = `
      <div class="chart-card-header">
        <h4>${ch.title}</h4>
        <span class="chart-type-badge">${ch.type}</span>
      </div>
      <img src="data:image/png;base64,${ch.img}" alt="${ch.title}" loading="lazy"/>
    `;
    cg.appendChild(card);
  });

  // Stats table
  const tbl = document.getElementById('stats-table');
  tbl.innerHTML = '';
  const stats = data.stats;
  const statKeys = Object.keys(stats);
  if (statKeys.length > 0) {
    const rows = Object.keys(stats[statKeys[0]]);
    const thead = document.createElement('thead');
    thead.innerHTML = `<tr><th>Metric</th>${statKeys.map(k => `<th>${k}</th>`).join('')}</tr>`;
    tbl.appendChild(thead);
    const tbody = document.createElement('tbody');
    rows.forEach(row => {
      const tr = document.createElement('tr');
      tr.innerHTML = `<td>${row}</td>` + statKeys.map(k => {
        const v = stats[k][row];
        return `<td>${typeof v === 'number' ? v.toLocaleString(undefined,{maximumFractionDigits:4}) : v ?? '—'}</td>`;
      }).join('');
      tbody.appendChild(tr);
    });
    tbl.appendChild(tbody);
    document.getElementById('stats-table-section').style.display = '';
  } else {
    document.getElementById('stats-table-section').style.display = 'none';
  }
}

function resetToUpload() {
  document.getElementById('upload-section').style.display = '';
  document.getElementById('results-section').classList.remove('show');
  document.getElementById('file-input').value = '';
  analysisData = null;
}

// ── REPORT DOWNLOAD ────────────────────────────────────────────────────────────
async function downloadReport() {
  if (!analysisData) return;
  const btn = document.querySelector('.btn-download');
  btn.innerHTML = '<span class="spin"></span> Generating PDF…';
  btn.disabled = true;

  try {
    const res = await fetch('/api/report', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        summary: analysisData.summary,
        insights: analysisData.insights,
        charts: analysisData.charts
      })
    });
    if (!res.ok) throw new Error('Report failed');
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `datalyze_report_${Date.now()}.pdf`;
    a.click();
    URL.revokeObjectURL(url);
  } catch(e) {
    alert('Could not generate report: ' + e.message);
  } finally {
    btn.innerHTML = '⬇ Download PDF Report';
    btn.disabled = false;
  }
}

// ── STREAK MODAL ──────────────────────────────────────────────────────────────
function showStreakModal() {
  document.getElementById('modal-streak').textContent = currentUser.streak;
  document.getElementById('streak-modal').classList.add('show');
}

function closeStreakModal() {
  document.getElementById('streak-modal').classList.remove('show');
}

// ── EBOOK PORTAL ──────────────────────────────────────────────────────────────
const EBOOKS_DB = [
  { id: 1, title: 'Python for Data Analysis', author: 'Wes McKinney', cover: '📘' },
  { id: 2, title: 'Hands-On Machine Learning', author: 'Aurélien Géron', cover: '📙' },
  { id: 3, title: 'Data Science from Scratch', author: 'Joel Grus', cover: '📗' },
  { id: 4, title: 'Storytelling with Data', author: 'Cole Nussbaumer Knaflic', cover: '📕' },
  { id: 5, title: 'Deep Learning', author: 'Ian Goodfellow', cover: '📓' }
];

function showEbookPortal() {
  showPage('ebook-page');
  renderEbooks();
}

function renderEbooks() {
  const grid = document.getElementById('ebooks-grid');
  grid.innerHTML = '';
  
  const streak = currentUser ? currentUser.streak : 0;
  const unlockedCount = Math.floor(streak / 10);
  
  EBOOKS_DB.forEach((book, index) => {
    const isUnlocked = index < unlockedCount;
    const requiredStreak = (index + 1) * 10;
    
    const card = document.createElement('div');
    card.className = `ebook-card ${isUnlocked ? 'unlocked' : 'locked'}`;
    
    card.innerHTML = `
      <div class="book-cover">${book.cover}</div>
      <div class="book-info">
        <h4>${book.title}</h4>
        <p>${book.author}</p>
        ${isUnlocked 
          ? `<button class="btn-primary" style="margin-top:12px; padding:6px 12px; font-size:12px;">Read Book</button>`
          : `<div class="locked-status">🔒 Unlocks at ${requiredStreak} streak</div>`
        }
      </div>
    `;
    grid.appendChild(card);
  });
}

// ── UTILS ─────────────────────────────────────────────────────────────────────
function showMsg(el, html, type) {
  el.innerHTML = html;
  el.className = `auth-msg ${type}`;
  el.style.display = 'block';
}

// Enter key support
document.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') {
    const activeTab = document.querySelector('.tab-btn.active');
    if (!activeTab) return;
    if (activeTab.textContent.includes('Sign In')) {
      const step2 = document.getElementById('login-step-2');
      step2.style.display !== 'none' ? doLoginVerify() : doLogin();
    } else {
      const step2 = document.getElementById('reg-step-2');
      step2.style.display !== 'none' ? doVerifyOtp() : doRegister();
    }
  }
});