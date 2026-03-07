/**
 * script.js — 공통 유틸리티
 * 모든 페이지에서 로드. API 호출, 유저 세션, 자동 동기화 담당.
 */

/* ── API ──────────────────────────────────────────────────────── */
const API = {
  async _fetch(url, options = {}) {
    const res = await fetch(url, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
    const json = await res.json();
    if (!json.success) throw new Error(json.error || "API error");
    return json.data;
  },
  get(url)         { return this._fetch(url); },
  post(url, body)  { return this._fetch(url, { method: "POST", body: JSON.stringify(body) }); },

  monsters:    ()       => API.get("/api/monsters"),
  patterns:    (id)     => API.get(`/api/patterns?id=${encodeURIComponent(id)}`),
  videos:      (id)     => API.get(`/api/videos?id=${encodeURIComponent(id)}`),
  comments:    (mid)    => API.get(`/api/comments?monster=${encodeURIComponent(mid)}`),
  addComment:  (body)   => API.post("/api/comments", body),
  votes:       (mid)    => API.get(`/api/votes?monster=${encodeURIComponent(mid)}`),
  addVote:     (body)   => API.post("/api/votes", body),
  ranking:     ()       => API.get("/api/ranking"),
};

/* ── User session ─────────────────────────────────────────────── */
const User = {
  get name() { return localStorage.getItem("wt_username") || ""; },
  set name(v) { localStorage.setItem("wt_username", v); },
  prompt() {
    const name = prompt("이름을 입력하세요 (팀원 식별용):", this.name);
    if (name && name.trim()) this.name = name.trim();
    return this.name;
  },
  require() {
    if (!this.name) return this.prompt();
    return this.name;
  },
};

/* ── Auto-sync ────────────────────────────────────────────────── */
const AUTO_SYNC_MS = 60 * 60 * 1000; // 1시간

function setupAutoSync(callback) {
  let syncTimer = setInterval(callback, AUTO_SYNC_MS);
  updateSyncLabel();
  setInterval(updateSyncLabel, 60000);
  window._syncStart = Date.now();

  function updateSyncLabel() {
    const el = document.getElementById("sync-label");
    if (!el) return;
    const elapsed = Math.floor((Date.now() - (window._syncStart || Date.now())) / 60000);
    const next = Math.max(0, 60 - elapsed);
    el.textContent = next > 0 ? `다음 동기화: ${next}분 후` : "동기화 중...";
  }
}

/* ── Nav active link ──────────────────────────────────────────── */
function setActiveNav() {
  const path = location.pathname;
  document.querySelectorAll(".nav-link").forEach(link => {
    const href = link.getAttribute("href");
    const isActive =
      (path === "/" && href === "/") ||
      (path !== "/" && href !== "/" && path.startsWith(href));
    link.classList.toggle("active", isActive);
  });
}

/* ── Helpers ──────────────────────────────────────────────────── */
function funAvg(funScoreObj) {
  if (!funScoreObj) return null;
  const vals = Object.values(funScoreObj).filter(v => v !== null);
  return vals.length ? (vals.reduce((a, b) => a + b, 0) / vals.length).toFixed(1) : null;
}

function patternTypeClass(type) {
  const map = {
    "AOE": "pt-aoe", "Puzzle": "pt-puzzle", "Wipe": "pt-wipe",
    "Movement": "pt-movement", "Mechanic": "pt-mechanic", "Target": "pt-target",
  };
  return map[type] || "pt-default";
}

function monsterTypeBadge(type) {
  const cls = { "Raid": "badge-raid", "Dungeon": "badge-dungeon", "Field": "badge-field", "Elite": "badge-elite" };
  return `<span class="badge ${cls[type] || ''}">${type || "-"}</span>`;
}

function formatDate(iso) {
  if (!iso) return "";
  return new Date(iso).toLocaleString("ko-KR", { month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit" });
}

function qs(param) {
  return new URLSearchParams(location.search).get(param);
}

function showError(containerId, msg) {
  const el = document.getElementById(containerId);
  if (el) el.innerHTML = `<div class="error-msg">${msg}</div>`;
}

/* ── Init ─────────────────────────────────────────────────────── */
document.addEventListener("DOMContentLoaded", setActiveNav);
