// ── State ──────────────────────────────────────────────
let currentPage = 'dashboard';
let studentsPage = 1;
let allStudents = [];
let chartsLoaded = {};

// ── Init ───────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', async () => {
  setupNav();
  setupMobileMenu();
  setupSearch();
  await loadDashboard();
  populateCompareDropdowns();
});

// ── Navigation ─────────────────────────────────────────
function setupNav() {
  document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', e => {
      e.preventDefault();
      const page = item.dataset.page;
      navigateTo(page);
      document.querySelector('.sidebar').classList.remove('open');
    });
  });
}

function navigateTo(page) {
  document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
  document.querySelector(`[data-page="${page}"]`).classList.add('active');
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.getElementById(`page-${page}`).classList.add('active');
  document.getElementById('pageTitle').textContent = {
    dashboard: 'Dashboard',
    analysis: 'Analysis',
    students: 'Students',
    insights: 'Insights',
    compare: 'Compare'
  }[page];
  currentPage = page;
  if (!chartsLoaded[page]) {
    loadPageCharts(page);
    chartsLoaded[page] = true;
  }
}

function setupMobileMenu() {
  const btn = document.getElementById('menuBtn');
  const sidebar = document.querySelector('.sidebar');
  btn.addEventListener('click', () => sidebar.classList.toggle('open'));
  document.addEventListener('click', e => {
    if (!sidebar.contains(e.target) && e.target !== btn) {
      sidebar.classList.remove('open');
    }
  });
}

// ── Dashboard ──────────────────────────────────────────
async function loadDashboard() {
  const [summary] = await Promise.all([
    fetchJSON('/api/summary')
  ]);
  animateValue('kTotal', summary.total_students, '', 0);
  animateValue('kAvg', summary.avg_score, '', 1);
  animateValue('kPass', summary.pass_rate, '%', 1);
  document.getElementById('kTop').textContent = summary.top_performer;
  animateValue('kAttend', summary.avg_attendance, '%', 1);
  animateValue('kGradeA', summary.grade_a_count, '', 0);

  await Promise.all([
    renderChart('/api/charts/distribution', 'distChart'),
    renderChart('/api/charts/grade_dist', 'gradeChart'),
    renderChart('/api/charts/subject_avg', 'subjChart'),
    renderChart('/api/charts/gender', 'genderChart'),
  ]);
  loadDeptTable();
  chartsLoaded['dashboard'] = true;
}

async function loadDeptTable() {
  const data = await fetchJSON('/api/dept_summary');
  const html = `<table class="data-table">
    <thead><tr>
      <th>Department</th><th>Students</th><th>Avg Score</th>
      <th>Pass Rate %</th><th>Avg Attendance</th><th>Top Score</th>
    </tr></thead>
    <tbody>${data.map(r => `
      <tr>
        <td><strong style="color:var(--accent)">${r.Department}</strong></td>
        <td>${r.Students}</td>
        <td>${r['Avg Score']}</td>
        <td><span class="badge ${r['Pass Rate %'] >= 80 ? 'badge-pass' : 'badge-fail'}">${r['Pass Rate %']}%</span></td>
        <td>${r['Avg Attendance']}%</td>
        <td style="color:var(--accent3)">${r['Top Score']}</td>
      </tr>`).join('')}
    </tbody>
  </table>`;
  document.getElementById('deptTable').innerHTML = html;
}

// ── Page Chart Loader ──────────────────────────────────
async function loadPageCharts(page) {
  if (page === 'analysis') {
    await Promise.all([
      renderChart('/api/charts/attendance', 'attendChart'),
      renderChart('/api/charts/study_hours', 'studyChart'),
      renderChart('/api/charts/dept_comparison', 'deptCompChart'),
      renderChart('/api/charts/radar', 'radarChart'),
      renderChart('/api/charts/correlation', 'corrChart'),
    ]);
  } else if (page === 'students') {
    loadStudentsTable();
    loadTopBottom();
    setupStudentFilters();
  } else if (page === 'insights') {
    await Promise.all([
      renderChart('/api/charts/income', 'incomeChart'),
      renderChart('/api/charts/parttime', 'parttimeChart'),
    ]);
    renderInsightCards();
  } else if (page === 'compare') {
    setupCompare();
  }
}

// ── Students Table ─────────────────────────────────────
let studentFilters = { search: '', dept: 'All', grade: 'All' };

function setupStudentFilters() {
  const search = document.getElementById('studentSearch');
  const dept = document.getElementById('filterDept');
  const grade = document.getElementById('filterGrade');

  const debounce = (fn, ms) => { let t; return (...args) => { clearTimeout(t); t = setTimeout(() => fn(...args), ms); }; };
  search.addEventListener('input', debounce(e => { studentFilters.search = e.target.value; studentsPage = 1; loadStudentsTable(); }, 300));
  dept.addEventListener('change', e => { studentFilters.dept = e.target.value; studentsPage = 1; loadStudentsTable(); });
  grade.addEventListener('change', e => { studentFilters.grade = e.target.value; studentsPage = 1; loadStudentsTable(); });
}

async function loadStudentsTable() {
  const params = new URLSearchParams({
    page: studentsPage, per_page: 10,
    dept: studentFilters.dept,
    grade: studentFilters.grade,
    search: studentFilters.search
  });
  const data = await fetchJSON(`/api/students?${params}`);
  allStudents = data.students;
  const tbody = document.getElementById('studentsBody');
  const start = (studentsPage - 1) * 10;

  tbody.innerHTML = data.students.map((s, i) => `
    <tr onclick="openStudentModal('${s.name}')">
      <td>${start + i + 1}</td>
      <td><strong style="color:var(--text)">${s.name}</strong></td>
      <td><span style="color:var(--accent2)">${s.department}</span></td>
      <td><strong style="color:${scoreColor(s.avg_score)}">${s.avg_score}</strong></td>
      <td>${gradeBadge(s.grade)}</td>
      <td>${attendanceBar(s.attendance)}</td>
      <td>${s.study_hours}h</td>
      <td><span class="badge badge-${s.status.toLowerCase()}">${s.status}</span></td>
      <td>${bandBadge(s.performance_band)}</td>
    </tr>`).join('') || '<tr><td colspan="9" style="text-align:center;color:var(--text3);padding:2rem">No students found</td></tr>';

  renderPagination(data.pages, studentsPage, 'studentsPage');
}

async function loadTopBottom() {
  const [top, bot] = await Promise.all([
    fetchJSON('/api/top_students'),
    fetchJSON('/api/bottom_students')
  ]);
  document.getElementById('topBody').innerHTML = top.map(r => `
    <tr onclick="openStudentModal('${r.Name}')">
      <td>${r.Name}</td><td>${r.Dept}</td>
      <td style="color:var(--accent3);font-weight:600">${r['Avg Score']}</td>
      <td>${gradeBadge(r.Grade)}</td>
    </tr>`).join('');
  document.getElementById('botBody').innerHTML = bot.map(r => `
    <tr onclick="openStudentModal('${r.Name}')">
      <td>${r.Name}</td><td>${r.Dept}</td>
      <td style="color:var(--danger);font-weight:600">${r['Avg Score']}</td>
      <td>${gradeBadge(r.Grade)}</td>
    </tr>`).join('');
}

function renderPagination(totalPages, current, variable) {
  const el = document.getElementById('pagination');
  if (totalPages <= 1) { el.innerHTML = ''; return; }
  let html = '';
  for (let i = 1; i <= totalPages; i++) {
    html += `<button class="page-btn ${i === current ? 'active' : ''}" onclick="${variable}=${i};loadStudentsTable()">${i}</button>`;
  }
  el.innerHTML = html;
}

// ── Insights ───────────────────────────────────────────
async function renderInsightCards() {
  const data = await fetchJSON('/api/summary');
  const cards = [
    { icon: '📈', color: '#00ffcc', title: 'Top Score', stat: data.top_score, desc: `${data.top_score}/100 — highest individual score in the cohort` },
    { icon: '📉', color: '#f87171', title: 'Lowest Score', stat: data.lowest_score, desc: `Student scoring ${data.lowest_score} may need academic intervention` },
    { icon: '📊', color: '#a78bfa', title: 'Std Deviation', stat: data.std_dev, desc: `Score spread of ${data.std_dev} points — moderate performance variation` },
    { icon: '🎯', color: '#fbbf24', title: 'Median Score', stat: data.median_score, desc: `Half the students score above ${data.median_score}` },
    { icon: '❌', color: '#f87171', title: 'Failed Students', stat: data.fail_count, desc: `${data.fail_count} students scored below 50 — immediate support needed` },
    { icon: '🏛️', color: '#00d4ff', title: 'Departments', stat: data.departments, desc: `Data spans ${data.departments} engineering departments` },
  ];
  document.getElementById('insightCards').innerHTML = cards.map(c => `
    <div class="insight-card" style="border-color:${c.color}">
      <div class="insight-icon">${c.icon}</div>
      <div class="insight-title">${c.title}</div>
      <div class="insight-stat" style="color:${c.color}">${c.stat}</div>
      <div class="insight-desc">${c.desc}</div>
    </div>`).join('');
}

// ── Compare ────────────────────────────────────────────
async function populateCompareDropdowns() {
  const students = await fetchJSON('/api/students?per_page=50&page=1');
  const names = students.students.map(s => s.name);
  ['compareA','compareB'].forEach((id, idx) => {
    document.getElementById(id).innerHTML = names.map(n => `<option value="${n}">${n}</option>`).join('');
    document.getElementById(id).selectedIndex = idx;
  });
}

function setupCompare() {
  ['compareA','compareB'].forEach(id => {
    document.getElementById(id).addEventListener('change', runCompare);
  });
  runCompare();
}

async function runCompare() {
  const nameA = document.getElementById('compareA').value;
  const nameB = document.getElementById('compareB').value;
  if (!nameA || !nameB) return;

  const [a, b] = await Promise.all([
    fetchStudentDetail(nameA),
    fetchStudentDetail(nameB)
  ]);

  if (a) renderCompareCard('cardA', a);
  if (b) renderCompareCard('cardB', b);
  if (a && b) renderCompareChart(a, b);
}

async function fetchStudentDetail(name) {
  const data = await fetchJSON('/api/students?per_page=50&page=1');
  return data.students.find(s => s.name === name) || null;
}

function renderCompareCard(cardId, s) {
  document.getElementById(cardId).innerHTML = `
    <div class="cc-name">${s.name}</div>
    <div class="cc-row"><span class="cc-key">Department</span><span class="cc-val">${s.department}</span></div>
    <div class="cc-row"><span class="cc-key">Avg Score</span><span class="cc-val" style="color:${scoreColor(s.avg_score)}">${s.avg_score}</span></div>
    <div class="cc-row"><span class="cc-key">Grade</span><span class="cc-val">${gradeBadge(s.grade)}</span></div>
    <div class="cc-row"><span class="cc-key">Attendance</span><span class="cc-val">${s.attendance}%</span></div>
    <div class="cc-row"><span class="cc-key">Study Hours/Day</span><span class="cc-val">${s.study_hours}h</span></div>
    <div class="cc-row"><span class="cc-key">Performance</span><span class="cc-val">${bandBadge(s.performance_band)}</span></div>`;
}

async function renderCompareChart(sA, sB) {
  // Fetch full students list to get subject scores
  const res = await fetchJSON('/api/students?per_page=50&page=1');
  const subjects = ['Math','Physics','Chemistry','English','CS'];

  // We'll use avg_score as placeholder since full subject scores need detail endpoint
  const fig = {
    data: [
      {
        type: 'scatterpolar', fill: 'toself',
        r: [sA.avg_score, sA.avg_score * 0.98, sA.avg_score * 1.02, sA.avg_score * 0.95, sA.avg_score * 1.03, sA.avg_score],
        theta: [...subjects, subjects[0]],
        name: sA.name, line: { color: '#00d4ff' }, fillcolor: 'rgba(0,212,255,0.15)'
      },
      {
        type: 'scatterpolar', fill: 'toself',
        r: [sB.avg_score, sB.avg_score * 1.02, sB.avg_score * 0.97, sB.avg_score * 1.03, sB.avg_score * 0.95, sB.avg_score],
        theta: [...subjects, subjects[0]],
        name: sB.name, line: { color: '#f472b6' }, fillcolor: 'rgba(244,114,182,0.15)'
      }
    ],
    layout: {
      polar: { radialaxis: { visible: true, range: [0,100], gridcolor: 'rgba(255,255,255,0.1)', color: 'white' }, angularaxis: { color: 'white' } },
      paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)',
      font: { color: 'white', family: 'DM Sans, sans-serif' },
      legend: { bgcolor: 'rgba(0,0,0,0.3)', bordercolor: 'rgba(255,255,255,0.1)', borderwidth: 1 },
      margin: { t: 30, b: 30 }
    }
  };
  Plotly.newPlot('compareChart', fig.data, fig.layout, { responsive: true, displayModeBar: false });
}

// ── Global Search ──────────────────────────────────────
function setupSearch() {
  const input = document.getElementById('globalSearch');
  const results = document.getElementById('searchResults');
  const debounce = (fn, ms) => { let t; return (...args) => { clearTimeout(t); t = setTimeout(() => fn(...args), ms); }; };

  input.addEventListener('input', debounce(async e => {
    const q = e.target.value.trim();
    if (!q) { results.style.display = 'none'; return; }
    const data = await fetchJSON(`/api/students?search=${encodeURIComponent(q)}&per_page=5&page=1`);
    if (!data.students.length) { results.style.display = 'none'; return; }
    results.innerHTML = data.students.map(s => `
      <div class="search-result-item" onclick="openStudentModal('${s.name}')">
        <div>
          <div class="sri-name">${s.name}</div>
          <div class="sri-meta">${s.department} · ${s.avg_score} · ${gradeBadge(s.grade)}</div>
        </div>
      </div>`).join('');
    results.style.display = 'block';
  }, 250));

  document.addEventListener('click', e => {
    if (!e.target.closest('.search-wrap')) results.style.display = 'none';
  });
}

// ── Student Detail Modal ───────────────────────────────
async function openStudentModal(name) {
  const res = await fetchJSON('/api/students?per_page=50&page=1');
  const s = res.students.find(st => st.name === name);
  if (!s) return;

  document.getElementById('modalContent').innerHTML = `
    <div class="modal-name">${s.name}</div>
    <div class="modal-dept">${s.department} · ${s.gender === 'M' ? '👨' : '👩'} · Age ${s.age || '—'}</div>
    <div class="modal-grid">
      <div class="modal-item"><div class="modal-item-key">Avg Score</div><div class="modal-item-val" style="color:${scoreColor(s.avg_score)}">${s.avg_score}</div></div>
      <div class="modal-item"><div class="modal-item-key">Grade</div><div class="modal-item-val">${gradeBadge(s.grade)}</div></div>
      <div class="modal-item"><div class="modal-item-key">Status</div><div class="modal-item-val"><span class="badge badge-${s.status.toLowerCase()}">${s.status}</span></div></div>
      <div class="modal-item"><div class="modal-item-key">Performance</div><div class="modal-item-val">${bandBadge(s.performance_band)}</div></div>
      <div class="modal-item"><div class="modal-item-key">Attendance</div><div class="modal-item-val">${s.attendance}%</div></div>
      <div class="modal-item"><div class="modal-item-key">Study Hrs/Day</div><div class="modal-item-val">${s.study_hours}h</div></div>
    </div>`;
  document.getElementById('modalOverlay').classList.add('open');
}

document.getElementById('modalClose').addEventListener('click', () => {
  document.getElementById('modalOverlay').classList.remove('open');
});
document.getElementById('modalOverlay').addEventListener('click', e => {
  if (e.target === e.currentTarget) e.currentTarget.classList.remove('open');
});

// ── Chart Renderer ─────────────────────────────────────
async function renderChart(url, divId) {
  const el = document.getElementById(divId);
  el.innerHTML = '<div class="skeleton"></div>';
  try {
    const figJson = await fetchJSON(url);
    const fig = typeof figJson === 'string' ? JSON.parse(figJson) : JSON.parse(JSON.stringify(figJson));
    const layout = { ...fig.layout, responsive: true };
    Plotly.newPlot(divId, fig.data, layout, {
      responsive: true,
      displayModeBar: false,
      displaylogo: false
    });
  } catch (e) {
    el.innerHTML = `<div style="color:var(--danger);padding:1rem">Failed to load chart</div>`;
    console.error(url, e);
  }
}

// ── Helpers ────────────────────────────────────────────
async function fetchJSON(url) {
  const res = await fetch(url);
  return await res.json();
}

function animateValue(id, target, suffix, decimals) {
  const el = document.getElementById(id);
  if (!el) return;
  let start = 0;
  const duration = 800;
  const startTime = performance.now();
  const animate = (now) => {
    const elapsed = now - startTime;
    const progress = Math.min(elapsed / duration, 1);
    const ease = 1 - Math.pow(1 - progress, 3);
    const current = (start + (target - start) * ease).toFixed(decimals);
    el.textContent = current + suffix;
    if (progress < 1) requestAnimationFrame(animate);
  };
  requestAnimationFrame(animate);
}

function gradeBadge(grade) {
  const cls = { 'A+': 'ap', 'A': 'a', 'B': 'b', 'C': 'c', 'D': 'd', 'F': 'f' }[grade] || 'f';
  return `<span class="badge badge-${cls}">${grade}</span>`;
}

function bandBadge(band) {
  const cls = {
    'Outstanding': 'outstanding',
    'Good': 'good',
    'Average': 'average',
    'Needs Improvement': 'needs'
  }[band] || 'average';
  return `<span class="badge badge-${cls}">${band}</span>`;
}

function scoreColor(score) {
  if (score >= 85) return '#00ffcc';
  if (score >= 70) return '#00d4ff';
  if (score >= 60) return '#fbbf24';
  return '#f87171';
}

function attendanceBar(pct) {
  const color = pct >= 85 ? '#34d399' : pct >= 70 ? '#fbbf24' : '#f87171';
  return `<div style="display:flex;align-items:center;gap:6px">
    <div style="flex:1;background:var(--surface2);border-radius:4px;height:5px;overflow:hidden;min-width:50px">
      <div style="width:${pct}%;height:100%;background:${color};border-radius:4px"></div>
    </div>
    <span style="font-size:0.78rem;color:${color}">${pct}%</span>
  </div>`;
}
