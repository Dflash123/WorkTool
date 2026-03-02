/**
 * feedback.js - 체감 평가 페이지
 */

const LIKERT_ITEMS = [
  { field: 'reaction_sufficiency', label: '반응 시간 충분성', hint: '회피/대응할 시간이 충분했나요?' },
  { field: 'hit_acceptance',       label: '피격 납득도',     hint: '맞은 것이 납득되었나요?' },
  { field: 'guide_clarity',        label: '가이드 명확성',   hint: '공격 범위 안내가 명확했나요?' },
  { field: 'attack_readability',   label: '공격 가독성',     hint: '언제 공격이 오는지 읽혔나요?' },
  { field: 'learnability',         label: '학습 가능성',     hint: '반복 플레이 시 나아질 것 같나요?' },
  { field: 'stress',               label: '스트레스',        hint: '⚠ 높을수록 부정적 (1=낮음, 5=매우 높음)' },
  { field: 'retry_intent',         label: '재도전 의사',     hint: '실패 후 다시 도전하고 싶었나요?' },
];

let _scores = {};
let _allSkillsForFb = [];
let _allLogs = [];

// ── 초기화 ────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
  initLikert();
  Promise.all([loadSkillOptions(), loadFeedbackList(), loadLogs()]);
});

function initLikert() {
  _scores = {};
  LIKERT_ITEMS.forEach(item => {
    _scores[item.field] = 3; // 기본값
  });

  const container = document.getElementById('likertList');
  container.innerHTML = LIKERT_ITEMS.map(item => `
    <div class="likert-item">
      <div class="likert-header">
        <span class="likert-label">${escHtml(item.label)}</span>
        <span class="likert-hint">${escHtml(item.hint)}</span>
      </div>
      <div class="likert-buttons" id="likert_${item.field}">
        ${[1,2,3,4,5].map(v => `
          <button class="likert-btn${v === 3 ? ' active' : ''}"
                  onclick="setScore('${item.field}', ${v})">${v}</button>
        `).join('')}
      </div>
    </div>`).join('');
}

function setScore(field, value) {
  _scores[field] = value;
  const group = document.getElementById(`likert_${field}`);
  if (!group) return;
  group.querySelectorAll('.likert-btn').forEach((btn, idx) => {
    btn.classList.toggle('active', idx + 1 === value);
  });
}

// ── 스킬 드롭다운 ─────────────────────────────────

async function loadSkillOptions() {
  try {
    const res = await api('/api/skills', 'GET');
    _allSkillsForFb = res.data || [];

    const selects = [
      document.getElementById('fb_skill_id'),
      document.getElementById('fb_filter_skill'),
    ];

    selects.forEach((sel, i) => {
      if (!sel) return;
      sel.innerHTML = i === 0
        ? '<option value="">스킬 선택...</option>'
        : '<option value="">전체 스킬</option>';

      _allSkillsForFb.forEach(s => {
        const opt = document.createElement('option');
        opt.value = s.skill_id;
        opt.textContent = `${s.monster_name} - ${s.skill_name} (v${s.version})`;
        sel.appendChild(opt);
      });
    });
  } catch (e) {
    console.error('스킬 목록 로드 실패:', e.message);
  }
}

// ── 테스트 로그 드롭다운 ──────────────────────────

async function loadLogs() {
  try {
    const res = await api('/api/logs', 'GET');
    _allLogs = res.data || [];

    const sel = document.getElementById('fb_log_id');
    if (!sel) return;
    sel.innerHTML = '<option value="none">없음</option>';
    _allLogs.forEach(l => {
      const opt = document.createElement('option');
      opt.value = l.log_id;
      opt.textContent = `${fmtDate(l.test_date)} | ${l.monster_name} - ${l.skill_name} (${l.tester_name})`;
      sel.appendChild(opt);
    });
  } catch (e) {
    console.error('로그 목록 로드 실패:', e.message);
  }
}

// ── 평가 이력 목록 ────────────────────────────────

async function loadFeedbackList() {
  try {
    const res = await api('/api/feedback', 'GET');
    renderFeedbackList(res.data || []);
  } catch (e) {
    document.getElementById('fbList').innerHTML =
      `<div class="alert alert-error">${escHtml(e.message)}</div>`;
  }
}

function renderFeedbackList(all) {
  const filterSkillId = document.getElementById('fb_filter_skill')?.value ?? '';
  const list = filterSkillId
    ? all.filter(f => f.skill_id === filterSkillId)
    : all;

  const container = document.getElementById('fbList');
  if (!list.length) {
    container.innerHTML = '<p style="color:#888;text-align:center">평가 기록이 없습니다.</p>';
    return;
  }

  // 스킬명 찾기 헬퍼
  const skillName = (id) => {
    const s = _allSkillsForFb.find(x => x.skill_id === id);
    return s ? `${s.monster_name} - ${s.skill_name}` : id;
  };

  container.innerHTML = list.slice().reverse().map(f => {
    const avgPositive = (
      (f.reaction_sufficiency + f.hit_acceptance + f.guide_clarity +
       f.attack_readability + f.learnability + f.retry_intent) / 6
    ).toFixed(1);

    return `<div class="fb-card">
      <div class="fb-meta">
        <span class="fb-skill">${escHtml(skillName(f.skill_id))}</span>
        <span class="fb-tester">${escHtml(f.tester_name)}</span>
        <span class="fb-date">${fmtDate(f.created_at)}</span>
      </div>
      <div class="fb-scores">
        ${_miniScore('반응', f.reaction_sufficiency)}
        ${_miniScore('납득', f.hit_acceptance)}
        ${_miniScore('가이드', f.guide_clarity)}
        ${_miniScore('가독', f.attack_readability)}
        ${_miniScore('학습', f.learnability)}
        ${_miniScore('스트레스', f.stress, true)}
        ${_miniScore('재도전', f.retry_intent)}
        <span class="fb-avg">종합 ${avgPositive}</span>
      </div>
      ${f.opinion ? `<div class="fb-opinion">${escHtml(f.opinion)}</div>` : ''}
    </div>`;
  }).join('');
}

function _miniScore(label, val, inverse = false) {
  const cls = inverse
    ? (val >= 4 ? 'score-bad' : val <= 2 ? 'score-good' : 'score-mid')
    : (val >= 4 ? 'score-good' : val <= 2 ? 'score-bad' : 'score-mid');
  return `<span class="mini-score ${cls}">${escHtml(label)} ${val}</span>`;
}

// ── 평가 저장 ─────────────────────────────────────

async function submitFeedback() {
  const errEl = document.getElementById('fbErrors');
  errEl.className = 'alert alert-error hidden';

  const payload = {
    skill_id: document.getElementById('fb_skill_id').value,
    tester_name: document.getElementById('fb_tester_name').value.trim(),
    log_id: document.getElementById('fb_log_id').value || 'none',
    opinion: document.getElementById('fb_opinion').value.trim(),
    ..._scores,
  };

  try {
    await api('/api/feedback', 'POST', payload);

    // 리셋
    document.getElementById('fb_skill_id').value = '';
    document.getElementById('fb_tester_name').value = '';
    document.getElementById('fb_log_id').value = 'none';
    document.getElementById('fb_opinion').value = '';
    initLikert();

    await loadFeedbackList();
  } catch (e) {
    errEl.textContent = e.message;
    errEl.className = 'alert alert-error';
  }
}
