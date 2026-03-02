/**
 * skills.js - 스킬 입력 페이지
 */

let _allSkills = [];
let _editingId = null;

// ── 초기화 ────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
  loadSkills();
  updateCalc();
  toggleGuide();
});

// ── 스킬 목록 ─────────────────────────────────────

async function loadSkills() {
  try {
    const res = await api('/api/skills', 'GET');
    _allSkills = res.data || [];
    renderSkills(_allSkills);
  } catch (e) {
    document.getElementById('skillTbody').innerHTML =
      `<tr><td colspan="9" style="text-align:center;color:#e74c3c">${escHtml(e.message)}</td></tr>`;
  }
}

function renderSkills(skills) {
  const tbody = document.getElementById('skillTbody');
  if (!skills.length) {
    tbody.innerHTML = '<tr><td colspan="9" style="text-align:center;color:#888">등록된 스킬이 없습니다.</td></tr>';
    return;
  }

  tbody.innerHTML = skills.map(s => {
    const guideText = s.guide_exists ? '✅' : '—';
    const reactionMs = s.reaction_window_ms ?? 0;
    return `<tr>
      <td>${escHtml(s.monster_name)}</td>
      <td>
        <a href="#" onclick="showDetail('${escHtml(s.skill_id)}');return false;"
           style="color:#7fa3d4;text-decoration:none;">${escHtml(s.skill_name)}</a>
      </td>
      <td>${escHtml(s.version)}</td>
      <td>${s.pre_delay_ms}ms</td>
      <td>${s.active_duration_ms}ms</td>
      <td class="${reactionMs < 250 ? 'text-danger' : ''}">${reactionMs}ms</td>
      <td>${guideText}</td>
      <td>${riskBadge(s._risk ?? 'LOW')}</td>
      <td>
        <button class="btn btn-sm" onclick="openSkillModal('${escHtml(s.skill_id)}')">수정</button>
        <button class="btn btn-sm btn-danger" onclick="deleteSkill('${escHtml(s.skill_id)}', '${escHtml(s.skill_name)}')">삭제</button>
      </td>
    </tr>`;
  }).join('');
}

function filterSkills() {
  const query = document.getElementById('searchInput').value.toLowerCase();
  const riskVal = document.getElementById('riskFilter').value;

  const filtered = _allSkills.filter(s => {
    const matchText = !query ||
      s.monster_name.toLowerCase().includes(query) ||
      s.skill_name.toLowerCase().includes(query);
    const matchRisk = !riskVal || (s._risk ?? 'LOW') === riskVal;
    return matchText && matchRisk;
  });
  renderSkills(filtered);
}

// ── 스킬 등록/수정 모달 ────────────────────────────

function openSkillModal(skillId) {
  _editingId = skillId || null;
  const modal = document.getElementById('skillModal');
  const title = document.getElementById('modalTitle');
  document.getElementById('formErrors').className = 'alert alert-error hidden';

  if (_editingId) {
    const s = _allSkills.find(x => x.skill_id === _editingId);
    if (!s) return;
    title.textContent = '스킬 수정';
    _fillForm(s);
  } else {
    title.textContent = '스킬 등록';
    _resetForm();
  }

  modal.classList.remove('hidden');
  updateCalc();
  toggleGuide();
}

function closeSkillModal() {
  document.getElementById('skillModal').classList.add('hidden');
  _editingId = null;
}

function _resetForm() {
  document.getElementById('f_skill_id').value = '';
  document.getElementById('f_monster_name').value = '';
  document.getElementById('f_skill_name').value = '';
  document.getElementById('f_version').value = '1.0.0';
  document.getElementById('f_skill_type').value = 'attack';
  document.getElementById('f_targeting_type').value = 'area';
  document.getElementById('f_pre_delay').value = 500;
  document.getElementById('f_active_duration').value = 300;
  document.getElementById('f_post_delay').value = 400;
  document.getElementById('f_dodge_start').value = 200;
  document.getElementById('f_dodge_end').value = 600;
  document.getElementById('f_guide_exists').checked = true;
  document.getElementById('f_guide_start').value = 0;
  document.getElementById('f_guide_duration').value = 500;
  document.getElementById('f_guide_type').value = 'visual';
  document.getElementById('f_guide_intensity').value = 3;
  document.getElementById('f_guide_visibility').value = 3;
  document.getElementById('f_guide_match').checked = true;
  document.getElementById('guide_intensity_val').textContent = '3';
  document.getElementById('guide_visibility_val').textContent = '3';
  document.getElementById('f_design_intent').value = '';
  document.getElementById('previewBars').innerHTML = '';
}

function _fillForm(s) {
  document.getElementById('f_skill_id').value = s.skill_id;
  document.getElementById('f_monster_name').value = s.monster_name;
  document.getElementById('f_skill_name').value = s.skill_name;
  document.getElementById('f_version').value = s.version;
  document.getElementById('f_skill_type').value = s.skill_type;
  document.getElementById('f_targeting_type').value = s.targeting_type;
  document.getElementById('f_pre_delay').value = s.pre_delay_ms;
  document.getElementById('f_active_duration').value = s.active_duration_ms;
  document.getElementById('f_post_delay').value = s.post_delay_ms;
  document.getElementById('f_dodge_start').value = s.dodge_start_ms;
  document.getElementById('f_dodge_end').value = s.dodge_end_ms;
  document.getElementById('f_guide_exists').checked = s.guide_exists;
  document.getElementById('f_guide_start').value = s.guide_start_ms;
  document.getElementById('f_guide_duration').value = s.guide_duration_ms;
  document.getElementById('f_guide_type').value = s.guide_type || 'visual';
  document.getElementById('f_guide_intensity').value = s.guide_intensity;
  document.getElementById('f_guide_visibility').value = s.guide_visibility;
  document.getElementById('f_guide_match').checked = s.guide_match;
  document.getElementById('guide_intensity_val').textContent = s.guide_intensity;
  document.getElementById('guide_visibility_val').textContent = s.guide_visibility;
  document.getElementById('f_design_intent').value = s.design_intent || '';
}

// ── 가이드 필드 토글 ──────────────────────────────

function toggleGuide() {
  const exists = document.getElementById('f_guide_exists').checked;
  document.getElementById('guideFields').style.display = exists ? '' : 'none';
}

// ── 타이밍 계산 + 시각화 ──────────────────────────

function updateCalc() {
  const pre = parseInt(document.getElementById('f_pre_delay').value, 10) || 0;
  const active = parseInt(document.getElementById('f_active_duration').value, 10) || 0;
  const post = parseInt(document.getElementById('f_post_delay').value, 10) || 0;
  const dodgeStart = parseInt(document.getElementById('f_dodge_start').value, 10) || 0;
  const dodgeEnd = parseInt(document.getElementById('f_dodge_end').value, 10) || 0;

  const total = pre + active + post;
  const reaction = Math.max(0, dodgeEnd - dodgeStart);

  document.getElementById('calc_total').textContent = `${total}ms`;
  document.getElementById('calc_reaction').textContent = `${reaction}ms`;

  _renderTimingBar(pre, active, post, dodgeStart, dodgeEnd);
  _renderPreview(pre, active, post, dodgeStart, dodgeEnd);
}

function _renderTimingBar(pre, active, post, dodgeStart, dodgeEnd) {
  const total = pre + active + post;
  const bar = document.getElementById('timingBar');
  if (total === 0 || !bar) return;

  const pPre = (pre / total * 100).toFixed(1);
  const pActive = (active / total * 100).toFixed(1);
  const pPost = (post / total * 100).toFixed(1);
  const pDodgeLeft = (dodgeStart / total * 100).toFixed(1);
  const pDodgeW = (Math.max(0, dodgeEnd - dodgeStart) / total * 100).toFixed(1);

  bar.innerHTML = `
    <div class="tb-track">
      <div class="tb-seg tb-pre" style="width:${pPre}%">
        <span class="tb-label">${pre > 0 ? '선딜 ' + pre + 'ms' : ''}</span>
      </div>
      <div class="tb-seg tb-active" style="width:${pActive}%">
        <span class="tb-label">${active > 0 ? '판정 ' + active + 'ms' : ''}</span>
      </div>
      <div class="tb-seg tb-post" style="width:${pPost}%">
        <span class="tb-label">${post > 0 ? '후딜 ' + post + 'ms' : ''}</span>
      </div>
      ${parseFloat(pDodgeW) > 0 ? `
        <div class="tb-dodge" style="left:${pDodgeLeft}%;width:${pDodgeW}%">
          <span class="tb-label">회피가능</span>
        </div>` : ''}
    </div>`;
}

function _renderPreview(pre, active, post, dodgeStart, dodgeEnd) {
  const refMs = 800;
  const reactionWindow = Math.max(0, dodgeEnd - dodgeStart);
  const reactionMargin = Math.min(reactionWindow / refMs, 1) * 100;

  const guideExists = document.getElementById('f_guide_exists').checked;
  const guideIntensity = parseInt(document.getElementById('f_guide_intensity').value, 10) || 0;
  const guideMatch = document.getElementById('f_guide_match').checked;

  const guideScore = guideExists ? (guideIntensity / 5) * 100 : 0;
  const matchBonus = guideMatch ? 20 : 0;
  const fairness = Math.min(reactionMargin * 0.5 + guideScore * 0.3 + matchBonus, 100);
  const unfair = 100 - fairness;

  const container = document.getElementById('previewBars');
  container.innerHTML =
    metricBar('반응 여유 지수', reactionMargin) +
    metricBar('타이밍 공정성', fairness) +
    metricBar('억까 가능성', unfair);
}

// ── 스킬 저장 ─────────────────────────────────────

async function submitSkill() {
  const errEl = document.getElementById('formErrors');
  errEl.className = 'alert alert-error hidden';

  const payload = {
    skill_id: document.getElementById('f_skill_id').value,
    monster_name: document.getElementById('f_monster_name').value.trim(),
    skill_name: document.getElementById('f_skill_name').value.trim(),
    version: document.getElementById('f_version').value.trim(),
    skill_type: document.getElementById('f_skill_type').value,
    targeting_type: document.getElementById('f_targeting_type').value,
    pre_delay_ms: parseInt(document.getElementById('f_pre_delay').value, 10),
    active_duration_ms: parseInt(document.getElementById('f_active_duration').value, 10),
    post_delay_ms: parseInt(document.getElementById('f_post_delay').value, 10),
    dodge_start_ms: parseInt(document.getElementById('f_dodge_start').value, 10),
    dodge_end_ms: parseInt(document.getElementById('f_dodge_end').value, 10),
    guide_exists: document.getElementById('f_guide_exists').checked,
    guide_start_ms: parseInt(document.getElementById('f_guide_start').value, 10) || 0,
    guide_duration_ms: parseInt(document.getElementById('f_guide_duration').value, 10) || 0,
    guide_type: document.getElementById('f_guide_type').value,
    guide_intensity: parseInt(document.getElementById('f_guide_intensity').value, 10),
    guide_visibility: parseInt(document.getElementById('f_guide_visibility').value, 10),
    guide_match: document.getElementById('f_guide_match').checked,
    design_intent: document.getElementById('f_design_intent').value.trim(),
  };

  try {
    await api('/api/skills', 'POST', payload);
    closeSkillModal();
    await loadSkills();
  } catch (e) {
    errEl.textContent = e.message;
    errEl.className = 'alert alert-error';
  }
}

// ── 스킬 삭제 ─────────────────────────────────────

async function deleteSkill(id, name) {
  if (!confirm(`"${name}" 스킬을 삭제하시겠습니까?\n관련 로그/체감 평가 데이터는 유지됩니다.`)) return;
  try {
    await api(`/api/skills/${encodeURIComponent(id)}`, 'DELETE');
    await loadSkills();
  } catch (e) {
    alert('삭제 실패: ' + e.message);
  }
}

// ── 스킬 상세 모달 ─────────────────────────────────

function showDetail(skillId) {
  const s = _allSkills.find(x => x.skill_id === skillId);
  if (!s) return;

  document.getElementById('detailTitle').textContent = `${s.monster_name} - ${s.skill_name}`;

  const body = document.getElementById('detailBody');
  body.innerHTML = `
    <div class="detail-grid">
      <div class="detail-item"><span class="detail-key">버전</span><span>${escHtml(s.version)}</span></div>
      <div class="detail-item"><span class="detail-key">유형</span><span>${escHtml(s.skill_type)}</span></div>
      <div class="detail-item"><span class="detail-key">타겟팅</span><span>${escHtml(s.targeting_type)}</span></div>
      <div class="detail-item"><span class="detail-key">선딜</span><span>${s.pre_delay_ms}ms</span></div>
      <div class="detail-item"><span class="detail-key">판정 지속</span><span>${s.active_duration_ms}ms</span></div>
      <div class="detail-item"><span class="detail-key">후딜</span><span>${s.post_delay_ms}ms</span></div>
      <div class="detail-item"><span class="detail-key">총 시간</span><span>${s.total_duration_ms ?? (s.pre_delay_ms + s.active_duration_ms + s.post_delay_ms)}ms</span></div>
      <div class="detail-item"><span class="detail-key">반응 가능 구간</span><span>${s.reaction_window_ms}ms (${s.dodge_start_ms}~${s.dodge_end_ms}ms)</span></div>
      <div class="detail-item"><span class="detail-key">가이드</span><span>${s.guide_exists ? '있음 (' + escHtml(s.guide_type) + ')' : '없음'}</span></div>
      ${s.guide_exists ? `
      <div class="detail-item"><span class="detail-key">가이드 강도</span><span>${s.guide_intensity}/5</span></div>
      <div class="detail-item"><span class="detail-key">가이드 가시성</span><span>${s.guide_visibility}/5</span></div>
      <div class="detail-item"><span class="detail-key">판정 범위 일치</span><span>${s.guide_match ? '✅ 일치' : '❌ 불일치'}</span></div>` : ''}
    </div>
    ${s.design_intent ? `<div class="detail-intent"><strong>설계 의도:</strong> ${escHtml(s.design_intent)}</div>` : ''}
    <div class="detail-section-label">타이밍 시각화</div>
    <div id="detailTimingBar"></div>
    <div class="detail-actions">
      <button class="btn btn-primary" onclick="closeDetailModal();openSkillModal('${escHtml(s.skill_id)}')">수정하기</button>
    </div>`;

  _renderDetailTimingBar(s);
  document.getElementById('detailModal').classList.remove('hidden');
}

function _renderDetailTimingBar(s) {
  const pre = s.pre_delay_ms, active = s.active_duration_ms, post = s.post_delay_ms;
  const total = pre + active + post;
  const bar = document.getElementById('detailTimingBar');
  if (!bar || total === 0) return;

  const pPre = (pre / total * 100).toFixed(1);
  const pActive = (active / total * 100).toFixed(1);
  const pPost = (post / total * 100).toFixed(1);
  const pDodgeLeft = (s.dodge_start_ms / total * 100).toFixed(1);
  const pDodgeW = (Math.max(0, s.dodge_end_ms - s.dodge_start_ms) / total * 100).toFixed(1);

  bar.innerHTML = `
    <div class="tb-track">
      <div class="tb-seg tb-pre" style="width:${pPre}%"><span class="tb-label">선딜 ${pre}ms</span></div>
      <div class="tb-seg tb-active" style="width:${pActive}%"><span class="tb-label">판정 ${active}ms</span></div>
      <div class="tb-seg tb-post" style="width:${pPost}%"><span class="tb-label">후딜 ${post}ms</span></div>
      ${parseFloat(pDodgeW) > 0 ? `<div class="tb-dodge" style="left:${pDodgeLeft}%;width:${pDodgeW}%"><span class="tb-label">회피가능</span></div>` : ''}
    </div>`;
}

function closeDetailModal() {
  document.getElementById('detailModal').classList.add('hidden');
}
