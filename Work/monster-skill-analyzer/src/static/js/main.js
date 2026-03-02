/**
 * main.js - 공통 유틸리티
 * 모든 페이지에서 base.html을 통해 로드됩니다.
 */

const _csrfToken = (() => {
  const el = document.querySelector('meta[name="csrf-token"]');
  return el ? el.content : '';
})();

/**
 * 보안 API 호출 래퍼
 * - CSRF 토큰 자동 첨부
 * - ok=false 또는 HTTP 오류 시 throw
 */
async function api(url, method = 'GET', data = null) {
  const opts = {
    method,
    credentials: 'same-origin',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': _csrfToken,
    },
  };
  if (data !== null) {
    opts.body = JSON.stringify(data);
  }

  const res = await fetch(url, opts);
  let json;
  try {
    json = await res.json();
  } catch {
    throw new Error(`HTTP ${res.status} - 응답 파싱 실패`);
  }

  if (!res.ok || json.ok === false) {
    const errors = json.errors ? json.errors.join('\n') : '';
    throw new Error(errors || json.error || `HTTP ${res.status}`);
  }
  return json;
}

/**
 * XSS 방지 HTML 이스케이프
 */
function escHtml(str) {
  return String(str ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

/**
 * 알림 메시지 표시
 * @param {HTMLElement} el - 알림을 표시할 엘리먼트
 * @param {string} text - 메시지
 * @param {'success'|'error'|'warning'} type
 */
function showMsg(el, text, type) {
  el.textContent = text;
  el.className = `alert alert-${type}`;
}

/**
 * ms → 사람이 읽기 쉬운 문자열
 * 예) 1200 → "1200ms (1.2s)"
 */
function formatMs(ms) {
  const n = parseInt(ms, 10);
  if (isNaN(n)) return '0ms';
  if (n >= 1000) return `${n}ms (${(n / 1000).toFixed(1)}s)`;
  return `${n}ms`;
}

/**
 * 위험도 badge HTML 반환
 */
function riskBadge(risk) {
  const map = { HIGH: 'danger', MEDIUM: 'warning', LOW: 'safe' };
  const cls = map[risk] ?? 'safe';
  return `<span class="risk-badge risk-${cls}">${escHtml(risk)}</span>`;
}

/**
 * 점수 → 퍼센트 바 HTML 반환
 */
function metricBar(label, value, max = 100) {
  const pct = Math.min(100, Math.max(0, (value / max) * 100));
  const cls = pct >= 70 ? 'good' : pct >= 40 ? 'mid' : 'bad';
  return `
    <div class="metric-row">
      <div class="metric-label">${escHtml(label)}</div>
      <div class="metric-track">
        <div class="metric-fill metric-${cls}" style="width:${pct.toFixed(1)}%"></div>
      </div>
      <div class="metric-val">${value.toFixed(1)}</div>
    </div>`;
}

/**
 * 날짜 포맷 (ISO → YYYY-MM-DD)
 */
function fmtDate(str) {
  if (!str) return '-';
  return str.slice(0, 10);
}
