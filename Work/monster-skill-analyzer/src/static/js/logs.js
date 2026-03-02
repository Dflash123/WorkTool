/**
 * logs.js - 테스트 로그 페이지
 */

let _allSkillsForLog = [];

// ── 초기화 ────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
  // 오늘 날짜 기본 설정
  const today = new Date().toISOString().slice(0, 10);
  const dateEl = document.getElementById('l_test_date');
  if (dateEl) dateEl.value = today;

  Promise.all([loadLogs(), loadSkillOptions()]);
});

// ── 스킬 목록 로드 (드롭다운용) ───────────────────

async function loadSkillOptions() {
  try {
    const res = await api('/api/skills', 'GET');
    _allSkillsForLog = res.data || [];

    const sel = document.getElementById('l_skill_id');
    if (!sel) return;

    sel.innerHTML = '<option value="">스킬 선택...</option>';
    _allSkillsForLog.forEach(s => {
      const opt = document.createElement('option');
      opt.value = s.skill_id;
      opt.textContent = `${s.monster_name} - ${s.skill_name} (v${s.version})`;
      opt.dataset.monster = s.monster_name;
      opt.dataset.skill = s.skill_name;
      sel.appendChild(opt);
    });
  } catch (e) {
    console.error('스킬 목록 로드 실패:', e.message);
  }
}

// ── 스킬 선택 시 자동 버전 채우기 ─────────────────

function onSkillSelect() {
  const sel = document.getElementById('l_skill_id');
  const selected = sel.options[sel.selectedIndex];
  if (!selected || !selected.value) return;

  const skill = _allSkillsForLog.find(s => s.skill_id === selected.value);
  if (skill) {
    const verEl = document.getElementById('l_test_version');
    if (verEl && !verEl.value) {
      verEl.value = skill.version;
    }
  }
}

// ── 로그 목록 로드 ────────────────────────────────

async function loadLogs() {
  try {
    const res = await api('/api/logs', 'GET');
    renderLogs(res.data || []);
  } catch (e) {
    document.getElementById('logTbody').innerHTML =
      `<tr><td colspan="9" style="text-align:center;color:#e74c3c">${escHtml(e.message)}</td></tr>`;
  }
}

function renderLogs(logs) {
  const tbody = document.getElementById('logTbody');
  if (!logs.length) {
    tbody.innerHTML = '<tr><td colspan="9" style="text-align:center;color:#888">기록된 테스트 로그가 없습니다.</td></tr>';
    return;
  }

  const typeLabel = { internal: '내부', live: '라이브' };

  tbody.innerHTML = logs.map(l => `<tr>
    <td>${escHtml(fmtDate(l.test_date || l.created_at))}</td>
    <td>${escHtml(l.monster_name)}</td>
    <td>${escHtml(l.skill_name)}</td>
    <td>${escHtml(typeLabel[l.test_type] ?? l.test_type)}</td>
    <td>${escHtml(l.tester_name)}</td>
    <td>${escHtml(l.test_version)}</td>
    <td>${escHtml(l.test_environment)}</td>
    <td>${l.participant_count}명</td>
    <td class="notes-cell" title="${escHtml(l.notes)}">${escHtml(l.notes ? l.notes.slice(0, 30) + (l.notes.length > 30 ? '…' : '') : '-')}</td>
  </tr>`).join('');
}

// ── 모달 제어 ─────────────────────────────────────

function openLogModal() {
  document.getElementById('logFormErrors').className = 'alert alert-error hidden';
  document.getElementById('logModal').classList.remove('hidden');
}

function closeLogModal() {
  document.getElementById('logModal').classList.add('hidden');
  _resetLogForm();
}

function _resetLogForm() {
  document.getElementById('l_skill_id').value = '';
  document.getElementById('l_test_type').value = 'internal';
  document.getElementById('l_test_date').value = new Date().toISOString().slice(0, 10);
  document.getElementById('l_tester_name').value = '';
  document.getElementById('l_test_version').value = '';
  document.getElementById('l_test_environment').value = '로컬';
  document.getElementById('l_participant_count').value = 1;
  document.getElementById('l_notes').value = '';
}

// ── 로그 저장 ─────────────────────────────────────

async function submitLog() {
  const errEl = document.getElementById('logFormErrors');
  errEl.className = 'alert alert-error hidden';

  const skillId = document.getElementById('l_skill_id').value;
  const skill = _allSkillsForLog.find(s => s.skill_id === skillId);

  const payload = {
    skill_id: skillId,
    monster_name: skill?.monster_name ?? '',
    skill_name: skill?.skill_name ?? '',
    test_type: document.getElementById('l_test_type').value,
    test_date: document.getElementById('l_test_date').value,
    tester_name: document.getElementById('l_tester_name').value.trim(),
    test_version: document.getElementById('l_test_version').value.trim(),
    test_environment: document.getElementById('l_test_environment').value,
    participant_count: parseInt(document.getElementById('l_participant_count').value, 10) || 1,
    notes: document.getElementById('l_notes').value.trim(),
  };

  try {
    await api('/api/logs', 'POST', payload);
    closeLogModal();
    await loadLogs();
  } catch (e) {
    errEl.textContent = e.message;
    errEl.className = 'alert alert-error';
  }
}
