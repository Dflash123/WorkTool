/**
 * analysis.js - 분석 대시보드 페이지
 * Chart.js 4.x 사용
 */

let _analysisData = [];
let _chartFairness = null;
let _chartUnfair = null;
let _chartTiming = null;
let _chartRadar = null;

// ── 초기화 ────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
  loadAnalysis();
});

// ── 데이터 로드 ───────────────────────────────────

async function loadAnalysis() {
  try {
    const res = await api('/api/analysis', 'GET');
    _analysisData = res.data || [];

    renderSummaryCards(_analysisData);
    renderSummaryTable(_analysisData);
    renderFairnessChart(_analysisData);
    renderUnfairChart(_analysisData);
    renderRiskSections(_analysisData);
    populateDetailSelect(_analysisData);
  } catch (e) {
    document.getElementById('summaryCards').innerHTML =
      `<div class="alert alert-error">${escHtml(e.message)}</div>`;
  }
}

// ── 요약 카드 ─────────────────────────────────────

function renderSummaryCards(data) {
  const counts = { HIGH: 0, MEDIUM: 0, LOW: 0 };
  data.forEach(d => { counts[d.overall_risk] = (counts[d.overall_risk] || 0) + 1; });

  document.getElementById('summaryCards').innerHTML = `
    <div class="summary-card card-danger">
      <div class="sc-count">${counts.HIGH}</div>
      <div class="sc-label">HIGH 위험</div>
    </div>
    <div class="summary-card card-warning">
      <div class="sc-count">${counts.MEDIUM}</div>
      <div class="sc-label">MEDIUM</div>
    </div>
    <div class="summary-card card-safe">
      <div class="sc-count">${counts.LOW}</div>
      <div class="sc-label">LOW</div>
    </div>
    <div class="summary-card card-total">
      <div class="sc-count">${data.length}</div>
      <div class="sc-label">전체 스킬</div>
    </div>`;
}

// ── 요약 테이블 ───────────────────────────────────

function renderSummaryTable(data) {
  const tbody = document.getElementById('summaryTbody');
  if (!data.length) {
    tbody.innerHTML = '<tr><td colspan="9" style="text-align:center;color:#888">데이터 없음</td></tr>';
    return;
  }

  tbody.innerHTML = data.map(d => {
    const m = d.metrics || {};
    return `<tr>
      <td>${escHtml(d.monster_name)}</td>
      <td>${escHtml(d.skill_name)}</td>
      <td>${escHtml(d.version)}</td>
      <td>${(m['반응 여유 지수'] ?? 0).toFixed(0)}</td>
      <td>${(m['타이밍 공정성'] ?? 0).toFixed(0)}</td>
      <td>${(m['억까 가능성'] ?? 0).toFixed(0)}</td>
      <td>${(m['설계 의도 적중률'] ?? 0).toFixed(0)}</td>
      <td>${riskBadge(d.overall_risk)}</td>
      <td>${d.feedback_count}</td>
    </tr>`;
  }).join('');
}

// ── 차트 공통 옵션 ────────────────────────────────

const _chartDefaults = {
  plugins: {
    legend: { labels: { color: '#c0c0c0' } },
  },
  scales: {
    x: { ticks: { color: '#c0c0c0' }, grid: { color: '#2a2d3e' } },
    y: { ticks: { color: '#c0c0c0' }, grid: { color: '#2a2d3e' } },
  },
};

function _destroyChart(instance) {
  if (instance) {
    try { instance.destroy(); } catch {}
  }
  return null;
}

// ── 공정성 차트 ───────────────────────────────────

function renderFairnessChart(data) {
  _chartFairness = _destroyChart(_chartFairness);
  const ctx = document.getElementById('chartFairness');
  if (!ctx || !data.length) return;

  const labels = data.map(d => `${d.monster_name}\n${d.skill_name}`);
  const values = data.map(d => d.metrics?.['타이밍 공정성'] ?? 0);
  const bgColors = data.map(d =>
    d.overall_risk === 'HIGH' ? '#e74c3c' :
    d.overall_risk === 'MEDIUM' ? '#f39c12' : '#27ae60'
  );

  _chartFairness = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: '공정성 점수',
        data: values,
        backgroundColor: bgColors,
        borderRadius: 4,
      }],
    },
    options: {
      ..._chartDefaults,
      scales: {
        ..._chartDefaults.scales,
        y: { ..._chartDefaults.scales.y, min: 0, max: 100 },
      },
    },
  });
}

// ── 억까 가능성 차트 ──────────────────────────────

function renderUnfairChart(data) {
  _chartUnfair = _destroyChart(_chartUnfair);
  const ctx = document.getElementById('chartUnfair');
  if (!ctx || !data.length) return;

  const labels = data.map(d => `${d.monster_name}\n${d.skill_name}`);
  const values = data.map(d => d.metrics?.['억까 가능성'] ?? 0);

  _chartUnfair = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: '억까 가능성',
        data: values,
        backgroundColor: values.map(v =>
          v >= 70 ? '#e74c3c' : v >= 40 ? '#f39c12' : '#3498db'
        ),
        borderRadius: 4,
      }],
    },
    options: {
      ..._chartDefaults,
      scales: {
        ..._chartDefaults.scales,
        y: { ..._chartDefaults.scales.y, min: 0, max: 100 },
      },
    },
  });
}

// ── 탭 전환 ───────────────────────────────────────

function switchTab(name) {
  document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
  document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));

  const content = document.getElementById(`tab_${name}`);
  if (content) content.classList.remove('hidden');

  const btn = document.querySelector(`.tab-btn[onclick="switchTab('${name}')"]`);
  if (btn) btn.classList.add('active');
}

// ── 위험 패턴 섹션 ────────────────────────────────

function renderRiskSections(data) {
  const high   = data.filter(d => d.overall_risk === 'HIGH');
  const medium = data.filter(d => d.overall_risk === 'MEDIUM');
  const low    = data.filter(d => d.overall_risk === 'LOW');

  document.getElementById('riskHigh').innerHTML   = _riskGroup('🔴 즉시 검토 필요 (HIGH)', high,   'danger');
  document.getElementById('riskMedium').innerHTML = _riskGroup('🟡 개선 권고 (MEDIUM)',    medium, 'warning');
  document.getElementById('riskLow').innerHTML    = _riskGroup('🟢 양호 (LOW)',             low,    'safe');
}

function _riskGroup(title, items, cls) {
  const header = `<h3>${escHtml(title)} <small>(${items.length}개)</small></h3>`;
  if (!items.length) return header + `<p style="color:#888">해당 없음</p>`;

  const cards = items.map(d => {
    const flags = (d.danger_flags || []).map(f =>
      `<div class="risk-flag flag-danger">⚠ ${escHtml(f)}</div>`
    ).join('');
    const warns = (d.warnings || []).map(w =>
      `<div class="risk-flag flag-warning">⚡ ${escHtml(w)}</div>`
    ).join('');

    return `<div class="risk-item risk-item-${cls}">
      <div class="risk-item-header">
        <strong>${escHtml(d.monster_name)} - ${escHtml(d.skill_name)}</strong>
        <span>v${escHtml(d.version)}</span>
        ${riskBadge(d.overall_risk)}
      </div>
      ${flags}${warns}
    </div>`;
  }).join('');

  return header + cards;
}

// ── 스킬 상세 탭 ──────────────────────────────────

function populateDetailSelect(data) {
  const sel = document.getElementById('detailSkillSelect');
  if (!sel) return;

  sel.innerHTML = '<option value="">스킬 선택...</option>';
  data.forEach(d => {
    const opt = document.createElement('option');
    opt.value = d.skill_id;
    opt.textContent = `${d.monster_name} - ${d.skill_name} (v${d.version}) ${riskLabel(d.overall_risk)}`;
    sel.appendChild(opt);
  });
}

function riskLabel(risk) {
  return risk === 'HIGH' ? '[🔴]' : risk === 'MEDIUM' ? '[🟡]' : '[🟢]';
}

function loadSkillDetail() {
  const skillId = document.getElementById('detailSkillSelect').value;
  const content = document.getElementById('skillDetailContent');

  if (!skillId) {
    content.classList.add('hidden');
    return;
  }

  const d = _analysisData.find(x => x.skill_id === skillId);
  if (!d) return;

  content.classList.remove('hidden');

  // 지표 바
  const m = d.metrics || {};
  document.getElementById('detailMetrics').innerHTML =
    metricBar('반응 여유 지수', m['반응 여유 지수'] ?? 0) +
    metricBar('타이밍 공정성', m['타이밍 공정성'] ?? 0) +
    metricBar('억까 가능성', m['억까 가능성'] ?? 0) +
    metricBar('설계 의도 적중률', m['설계 의도 적중률'] ?? 0) +
    metricBar('학습 가능성', m['학습 가능성'] ?? 0);

  // 경고/위험 메시지
  const warnEl = document.getElementById('detailWarnings');
  const flags = (d.danger_flags || []).map(f =>
    `<div class="risk-flag flag-danger">⚠ ${escHtml(f)}</div>`
  );
  const warns = (d.warnings || []).map(w =>
    `<div class="risk-flag flag-warning">⚡ ${escHtml(w)}</div>`
  );
  warnEl.innerHTML = flags.length || warns.length
    ? `<h3>경고 항목</h3>${flags.join('')}${warns.join('')}`
    : `<h3>경고 항목</h3><p style="color:#888">이상 없음</p>`;

  // 체감 의견
  document.getElementById('detailOpinions').innerHTML =
    d.feedback_count
      ? _renderAvgScores(d.avg_scores)
      : '<p style="color:#888">아직 체감 평가가 없습니다.</p>';

  // 차트
  _renderTimingChart(d);
  _renderRadarChart(d);
}

function _renderAvgScores(avg) {
  if (!avg || !Object.keys(avg).length) return '<p style="color:#888">평균 점수 없음</p>';
  const labelMap = {
    reaction_sufficiency: '반응 충분성',
    hit_acceptance: '피격 납득도',
    guide_clarity: '가이드 명확성',
    learnability: '학습 가능성',
    stress: '스트레스',
  };
  return Object.entries(avg).map(([k, v]) =>
    metricBar(labelMap[k] ?? k, v, 5)
  ).join('');
}

function _renderTimingChart(d) {
  _chartTiming = _destroyChart(_chartTiming);
  const ctx = document.getElementById('chartTiming');
  if (!ctx) return;

  _chartTiming = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['선딜', '판정 지속', '후딜'],
      datasets: [{
        label: 'ms',
        data: [d.pre_delay_ms, d.active_duration_ms, d.post_delay_ms],
        backgroundColor: ['#3498db', '#e74c3c', '#95a5a6'],
        borderRadius: 4,
      }],
    },
    options: {
      indexAxis: 'y',
      plugins: { legend: { display: false } },
      scales: {
        x: { ticks: { color: '#c0c0c0' }, grid: { color: '#2a2d3e' } },
        y: { ticks: { color: '#c0c0c0' }, grid: { color: '#2a2d3e' } },
      },
    },
  });
}

function _renderRadarChart(d) {
  _chartRadar = _destroyChart(_chartRadar);
  const ctx = document.getElementById('chartRadar');
  if (!ctx) return;

  const m = d.metrics || {};
  const avg = d.avg_scores || {};

  _chartRadar = new Chart(ctx, {
    type: 'radar',
    data: {
      labels: ['반응 여유', '타이밍 공정성', '설계 의도', '학습 가능성', '체감 납득도'],
      datasets: [
        {
          label: '설계 지표',
          data: [
            m['반응 여유 지수'] ?? 0,
            m['타이밍 공정성'] ?? 0,
            m['설계 의도 적중률'] ?? 0,
            m['학습 가능성'] ?? 0,
            100 - (m['억까 가능성'] ?? 0),
          ],
          borderColor: '#7fa3d4',
          backgroundColor: 'rgba(127,163,212,0.2)',
          pointBackgroundColor: '#7fa3d4',
        },
        ...(Object.keys(avg).length ? [{
          label: '체감 평가',
          data: [
            (avg.reaction_sufficiency ?? 0) / 5 * 100,
            (avg.hit_acceptance ?? 0) / 5 * 100,
            0,
            (avg.learnability ?? 0) / 5 * 100,
            (avg.guide_clarity ?? 0) / 5 * 100,
          ],
          borderColor: '#27ae60',
          backgroundColor: 'rgba(39,174,96,0.2)',
          pointBackgroundColor: '#27ae60',
        }] : []),
      ],
    },
    options: {
      plugins: {
        legend: { labels: { color: '#c0c0c0' } },
      },
      scales: {
        r: {
          min: 0, max: 100,
          ticks: { color: '#c0c0c0', stepSize: 25, backdropColor: 'transparent' },
          grid: { color: '#2a2d3e' },
          pointLabels: { color: '#c0c0c0' },
        },
      },
    },
  });
}
