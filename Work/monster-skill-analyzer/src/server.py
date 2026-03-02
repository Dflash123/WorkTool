"""
Monster Skill Analyzer - Flask 서버
- Google OAuth 인증 필수
- CSRF 보호
- 서버사이드 입력 검증
"""
from __future__ import annotations
import os
import sys
import secrets
import json
import functools
from pathlib import Path
from datetime import datetime, timedelta

from flask import (
    Flask, render_template, request, jsonify,
    session, redirect, url_for, abort, g
)
from flask_wtf.csrf import CSRFProtect

# 프로젝트 루트를 path에 추가
_root = Path(__file__).parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from src.config.settings import settings
from src.modules.data_models import (
    SkillDefinition, TestLog, PlayerFeedback, BalanceHistory
)
from src.modules.metrics_calculator import calculator
from src.services.auth_service import auth_service
from src.services.sheets_service_qt import sheets_service

# ── Flask 앱 초기화 ──────────────────────────────
app = Flask(
    __name__,
    template_folder=str(Path(__file__).parent / "templates"),
    static_folder=str(Path(__file__).parent / "static"),
)

# 세션 암호화 키 (실행 시마다 생성 → 서버 재시작 시 세션 만료)
_secret_key_file = _root / "credentials" / ".secret_key"
if _secret_key_file.exists():
    app.secret_key = _secret_key_file.read_bytes()
else:
    key = secrets.token_bytes(32)
    _secret_key_file.parent.mkdir(exist_ok=True)
    _secret_key_file.write_bytes(key)
    app.secret_key = key

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,   # JS에서 쿠키 접근 불가
    SESSION_COOKIE_SAMESITE="Lax",  # CSRF 방어
    PERMANENT_SESSION_LIFETIME=timedelta(hours=8),
    WTF_CSRF_TIME_LIMIT=3600,       # CSRF 토큰 1시간 유효
)

csrf = CSRFProtect(app)

# ── 인증 데코레이터 ────────────────────────────────
def login_required(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("auth_login"))
        # 세션 만료 체크
        logged_at = session.get("logged_at")
        if logged_at:
            elapsed = datetime.now() - datetime.fromisoformat(logged_at)
            if elapsed > timedelta(hours=8):
                session.clear()
                return redirect(url_for("auth_login"))
        return f(*args, **kwargs)
    return decorated

def _sheets_required(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        if not sheets_service.is_connected:
            ok, msg = sheets_service.connect()
            if not ok:
                return jsonify({"ok": False, "error": msg}), 503
        return f(*args, **kwargs)
    return decorated

# ── 입력 검증 헬퍼 ────────────────────────────────
def _validate_int(val, name: str, min_val=0, max_val=30000) -> tuple[int, str]:
    try:
        v = int(val)
        if not (min_val <= v <= max_val):
            return None, f"{name}: {min_val}~{max_val} 범위여야 합니다."
        return v, ""
    except (TypeError, ValueError):
        return None, f"{name}: 숫자여야 합니다."

def _validate_str(val, name: str, max_len=200) -> tuple[str, str]:
    if not val or not str(val).strip():
        return None, f"{name}: 필수 항목입니다."
    v = str(val).strip()[:max_len]
    return v, ""

def _validate_likert(val, name: str) -> tuple[int, str]:
    return _validate_int(val, name, min_val=1, max_val=5)

# ── 페이지 라우트 ──────────────────────────────────
@app.route("/")
@login_required
def index():
    return redirect(url_for("skills_page"))

@app.route("/skills")
@login_required
def skills_page():
    return render_template("skills.html")

@app.route("/logs")
@login_required
def logs_page():
    return render_template("logs.html")

@app.route("/feedback")
@login_required
def feedback_page():
    return render_template("feedback.html")

@app.route("/analysis")
@login_required
def analysis_page():
    return render_template("analysis.html")

@app.route("/settings")
@login_required
def settings_page():
    return render_template("settings.html", settings=settings)

# ── 인증 라우트 ────────────────────────────────────
@app.route("/auth/login")
def auth_login():
    return render_template("login.html")

@app.route("/auth/google")
def auth_google():
    """Google OAuth 시작"""
    if not auth_service.has_client_secret():
        return render_template("login.html", error=(
            "client_secret.json 파일이 없습니다. "
            "설정 가이드를 확인하세요."
        ))
    # 저장된 토큰으로 자동 로그인 시도
    if auth_service.has_saved_token() and auth_service.auto_login():
        session["logged_in"] = True
        session["logged_at"] = datetime.now().isoformat()
        session.permanent = True
        return redirect(url_for("index"))
    # 브라우저 OAuth 플로우
    ok, msg = auth_service.login_with_browser()
    if ok:
        session["logged_in"] = True
        session["logged_at"] = datetime.now().isoformat()
        session.permanent = True
        return redirect(url_for("index"))
    return render_template("login.html", error=msg)

@app.route("/auth/logout")
def auth_logout():
    session.clear()
    return redirect(url_for("auth_login"))

# ── API: 스킬 ──────────────────────────────────────
@app.route("/api/skills", methods=["GET"])
@login_required
@_sheets_required
def api_get_skills():
    skills = sheets_service.get_all_skills()
    result = []
    for s in skills:
        d = s.__dict__.copy()
        d["_risk"] = calculator.calculate(s).overall_risk
        result.append(d)
    return jsonify({"ok": True, "data": result})

@app.route("/api/skills", methods=["POST"])
@login_required
@_sheets_required
def api_save_skill():
    d = request.get_json(silent=True) or {}
    errors = []

    monster_name, e = _validate_str(d.get("monster_name"), "몬스터명")
    if e: errors.append(e)
    skill_name, e = _validate_str(d.get("skill_name"), "스킬명")
    if e: errors.append(e)
    version, e = _validate_str(d.get("version"), "버전", max_len=20)
    if e: errors.append(e)

    pre_delay, e = _validate_int(d.get("pre_delay_ms"), "선딜")
    if e: errors.append(e)
    active_dur, e = _validate_int(d.get("active_duration_ms"), "판정 지속")
    if e: errors.append(e)
    post_delay, e = _validate_int(d.get("post_delay_ms"), "후딜")
    if e: errors.append(e)
    dodge_start, e = _validate_int(d.get("dodge_start_ms"), "회피 시작")
    if e: errors.append(e)
    dodge_end, e = _validate_int(d.get("dodge_end_ms"), "회피 종료")
    if e: errors.append(e)

    if errors:
        return jsonify({"ok": False, "errors": errors}), 400

    skill_type = str(d.get("skill_type", "attack"))[:20]
    targeting = str(d.get("targeting_type", "area"))[:20]
    guide_exists = bool(d.get("guide_exists", False))
    guide_intensity = max(0, min(5, int(d.get("guide_intensity", 0) or 0)))
    guide_visibility = max(0, min(5, int(d.get("guide_visibility", 0) or 0)))

    skill = SkillDefinition(
        monster_name=monster_name, skill_name=skill_name,
        skill_type=skill_type, version=version,
        pre_delay_ms=pre_delay, active_duration_ms=active_dur,
        post_delay_ms=post_delay, dodge_start_ms=dodge_start,
        dodge_end_ms=dodge_end, targeting_type=targeting,
        guide_exists=guide_exists,
        guide_start_ms=int(d.get("guide_start_ms") or 0),
        guide_duration_ms=int(d.get("guide_duration_ms") or 0),
        guide_type=str(d.get("guide_type", "none"))[:20],
        guide_intensity=guide_intensity, guide_visibility=guide_visibility,
        guide_match=bool(d.get("guide_match", True)),
        guide_offset_ms=int(d.get("guide_offset_ms") or 0),
        design_intent=str(d.get("design_intent", ""))[:500],
    )

    # 수정인지 신규인지 확인
    skill_id = d.get("skill_id", "")
    if skill_id:
        skill.skill_id = skill_id
        ok, msg = sheets_service.update_skill(skill)
    else:
        ok, msg = sheets_service.add_skill(skill)

    if not ok:
        return jsonify({"ok": False, "error": msg}), 500

    # 지표 계산
    result = calculator.calculate(skill)
    return jsonify({"ok": True, "message": msg, "metrics": result.to_dict()})

@app.route("/api/skills/<skill_id>", methods=["DELETE"])
@login_required
@_sheets_required
def api_delete_skill(skill_id: str):
    if not skill_id or len(skill_id) > 50:
        abort(400)
    ok, msg = sheets_service.delete_skill(skill_id)
    return jsonify({"ok": ok, "message": msg})

# ── API: 테스트 로그 ───────────────────────────────
@app.route("/api/logs", methods=["GET"])
@login_required
@_sheets_required
def api_get_logs():
    logs = sheets_service.get_all_test_logs()
    return jsonify({"ok": True, "data": [l.__dict__ for l in logs]})

@app.route("/api/logs", methods=["POST"])
@login_required
@_sheets_required
def api_save_log():
    d = request.get_json(silent=True) or {}
    errors = []

    skill_id, e = _validate_str(d.get("skill_id"), "스킬 ID", max_len=50)
    if e: errors.append(e)
    tester_name, e = _validate_str(d.get("tester_name"), "담당자명")
    if e: errors.append(e)
    test_version, e = _validate_str(d.get("test_version"), "버전", max_len=20)
    if e: errors.append(e)

    if errors:
        return jsonify({"ok": False, "errors": errors}), 400

    log = TestLog(
        skill_id=skill_id,
        monster_name=str(d.get("monster_name", ""))[:100],
        skill_name=str(d.get("skill_name", ""))[:100],
        test_type=str(d.get("test_type", "internal"))[:20],
        test_date=str(d.get("test_date", ""))[:20],
        tester_name=tester_name, test_version=test_version,
        test_environment=str(d.get("test_environment", "로컬"))[:50],
        participant_count=max(1, min(1000, int(d.get("participant_count", 1) or 1))),
        notes=str(d.get("notes", ""))[:500],
    )
    ok, msg = sheets_service.add_test_log(log)
    return jsonify({"ok": ok, "message": msg, "log_id": log.log_id})

# ── API: 체감 평가 ─────────────────────────────────
@app.route("/api/feedback", methods=["GET"])
@login_required
@_sheets_required
def api_get_feedback():
    data = sheets_service.get_all_feedbacks()
    return jsonify({"ok": True, "data": [f.__dict__ for f in data]})

@app.route("/api/feedback", methods=["POST"])
@login_required
@_sheets_required
def api_save_feedback():
    d = request.get_json(silent=True) or {}
    errors = []

    skill_id, e = _validate_str(d.get("skill_id"), "스킬 ID", max_len=50)
    if e: errors.append(e)
    tester_name, e = _validate_str(d.get("tester_name"), "평가자명")
    if e: errors.append(e)

    scores = {}
    for field in ["reaction_sufficiency", "hit_acceptance", "guide_clarity",
                  "attack_readability", "learnability", "stress", "retry_intent"]:
        v, e = _validate_likert(d.get(field), field)
        if e: errors.append(e)
        else: scores[field] = v

    if errors:
        return jsonify({"ok": False, "errors": errors}), 400

    fb = PlayerFeedback(
        skill_id=skill_id,
        log_id=str(d.get("log_id", "none"))[:50],
        tester_name=tester_name,
        opinion=str(d.get("opinion", ""))[:1000],
        **scores,
    )
    ok, msg = sheets_service.add_feedback(fb)
    return jsonify({"ok": ok, "message": msg})

# ── API: 분석 데이터 ───────────────────────────────
@app.route("/api/analysis", methods=["GET"])
@login_required
@_sheets_required
def api_analysis():
    skills = sheets_service.get_all_skills()
    feedbacks = sheets_service.get_all_feedbacks()

    fb_by_skill: dict = {}
    for fb in feedbacks:
        fb_by_skill.setdefault(fb.skill_id, []).append(fb)

    result = []
    for skill in skills:
        fbs = fb_by_skill.get(skill.skill_id, [])
        metrics = calculator.calculate(skill, fbs if fbs else None)
        result.append({
            "skill_id": skill.skill_id,
            "monster_name": skill.monster_name,
            "skill_name": skill.skill_name,
            "version": skill.version,
            "pre_delay_ms": skill.pre_delay_ms,
            "active_duration_ms": skill.active_duration_ms,
            "post_delay_ms": skill.post_delay_ms,
            "reaction_window_ms": skill.reaction_window_ms,
            "guide_exists": skill.guide_exists,
            "metrics": metrics.to_dict(),
            "overall_risk": metrics.overall_risk,
            "danger_flags": metrics.danger_flags,
            "warnings": metrics.warnings,
            "feedback_count": len(fbs),
            "avg_scores": {
                "reaction_sufficiency": round(sum(f.reaction_sufficiency for f in fbs) / len(fbs), 1) if fbs else 0,
                "hit_acceptance": round(sum(f.hit_acceptance for f in fbs) / len(fbs), 1) if fbs else 0,
                "guide_clarity": round(sum(f.guide_clarity for f in fbs) / len(fbs), 1) if fbs else 0,
                "learnability": round(sum(f.learnability for f in fbs) / len(fbs), 1) if fbs else 0,
                "stress": round(sum(f.stress for f in fbs) / len(fbs), 1) if fbs else 0,
            } if fbs else {},
        })

    return jsonify({"ok": True, "data": result})

# ── API: 설정 저장 ─────────────────────────────────
@app.route("/api/settings", methods=["POST"])
@login_required
def api_save_settings():
    import yaml
    from src.config.settings import CONFIG_PATH
    d = request.get_json(silent=True) or {}

    spreadsheet_id = str(d.get("spreadsheet_id", "")).strip()[:200]
    if not spreadsheet_id:
        return jsonify({"ok": False, "error": "Spreadsheet ID를 입력하세요."}), 400

    with open(CONFIG_PATH, encoding="utf-8") as f:
        config = yaml.safe_load(f)

    config["google_sheets"]["spreadsheet_id"] = spreadsheet_id

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        yaml.dump(config, f, allow_unicode=True, default_flow_style=False)

    settings.reload()
    sheets_service._spreadsheet = None  # 재연결 강제
    return jsonify({"ok": True, "message": "설정 저장 완료"})


def create_app() -> Flask:
    return app


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
