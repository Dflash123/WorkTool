"""
web_tool - Flask API Server
Monster Pattern Analysis Web Tool

소유 파일: app.py, frontend/, data/comments.json, data/votes.json
수정 금지: collector/, timeline_extractor/, scheduler/, run_collector.py
          data/monsters.json, data/patterns.json, data/videos.json
"""
import json
import uuid
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__, static_folder="frontend")
DATA_DIR = Path(__file__).parent / "data"

VALID_VOTE_TYPES = {"fun", "difficulty", "design_reference"}


# ─── JSON helpers ──────────────────────────────────────────────────────────────

def read_json(filename):
    path = DATA_DIR / filename
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(filename, data):
    path = DATA_DIR / filename
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def ok(data):
    return jsonify({"success": True, "data": data, "error": None})


def err(msg, status=400):
    return jsonify({"success": False, "data": None, "error": msg}), status


# ─── Page routes ───────────────────────────────────────────────────────────────

@app.route("/")
def page_index():
    return send_from_directory("frontend", "index.html")


@app.route("/monster")
def page_monster():
    return send_from_directory("frontend", "monster.html")


@app.route("/ranking")
def page_ranking():
    return send_from_directory("frontend", "ranking.html")


@app.route("/dashboard")
def page_dashboard():
    return send_from_directory("frontend", "dashboard.html")


# ─── Read-only API (monsters, patterns, videos) ────────────────────────────────

@app.route("/api/monsters")
def api_monsters():
    monsters = read_json("monsters.json")
    if monsters is None:
        return err("monsters.json not found", 404)
    return ok(monsters)


@app.route("/api/patterns")
def api_patterns():
    patterns = read_json("patterns.json")
    if patterns is None:
        return err("patterns.json not found", 404)
    monster_id = request.args.get("id")
    if monster_id:
        patterns = [p for p in patterns if p.get("monster_id") == monster_id]
    return ok(patterns)


@app.route("/api/videos")
def api_videos():
    videos = read_json("videos.json")
    if videos is None:
        return err("videos.json not found", 404)
    monster_id = request.args.get("id")
    if monster_id:
        videos = [v for v in videos if v.get("monster_id") == monster_id]
    return ok(videos)


# ─── Comments API ──────────────────────────────────────────────────────────────

@app.route("/api/comments")
def api_comments_get():
    data = read_json("comments.json") or {"comments": []}
    comments = data.get("comments", [])
    monster_id = request.args.get("monster")
    if monster_id:
        comments = [c for c in comments if c.get("monster_id") == monster_id]
    return ok(sorted(comments, key=lambda c: c["date"], reverse=True))


@app.route("/api/comments", methods=["POST"])
def api_comments_post():
    body = request.get_json()
    if not body:
        return err("Request body required")

    monster_id = str(body.get("monster_id", "")).strip()
    user_name  = str(body.get("user_name", "")).strip()
    comment    = str(body.get("comment", "")).strip()

    if not monster_id or not user_name or not comment:
        return err("monster_id, user_name, comment are required")
    if len(user_name) > 50:
        return err("user_name too long (max 50)")
    if len(comment) > 500:
        return err("comment too long (max 500)")

    data = read_json("comments.json") or {"comments": []}
    new_item = {
        "id": str(uuid.uuid4()),
        "monster_id": monster_id,
        "user_name": user_name,
        "comment": comment,
        "date": datetime.now().isoformat(),
    }
    data["comments"].append(new_item)
    write_json("comments.json", data)
    return ok(new_item), 201


# ─── Votes API ─────────────────────────────────────────────────────────────────

@app.route("/api/votes")
def api_votes_get():
    data = read_json("votes.json") or {"votes": []}
    votes = data.get("votes", [])
    monster_id = request.args.get("monster")
    if monster_id:
        votes = [v for v in votes if v.get("monster_id") == monster_id]
    return ok(votes)


@app.route("/api/votes", methods=["POST"])
def api_votes_post():
    body = request.get_json()
    if not body:
        return err("Request body required")

    monster_id = str(body.get("monster_id", "")).strip()
    user_name  = str(body.get("user_name", "")).strip()
    vote_type  = str(body.get("vote_type", "")).strip()

    if not monster_id or not user_name or not vote_type:
        return err("monster_id, user_name, vote_type are required")
    if vote_type not in VALID_VOTE_TYPES:
        return err(f"vote_type must be one of: {', '.join(sorted(VALID_VOTE_TYPES))}")
    if len(user_name) > 50:
        return err("user_name too long (max 50)")

    data = read_json("votes.json") or {"votes": []}
    votes = data.get("votes", [])

    already = any(
        v["monster_id"] == monster_id
        and v["user_name"] == user_name
        and v["vote_type"] == vote_type
        for v in votes
    )
    if already:
        return err("Already voted"), 409

    new_item = {
        "id": str(uuid.uuid4()),
        "monster_id": monster_id,
        "user_name": user_name,
        "vote_type": vote_type,
        "date": datetime.now().isoformat(),
    }
    data["votes"].append(new_item)
    write_json("votes.json", data)
    return ok(new_item), 201


# ─── Ranking API ───────────────────────────────────────────────────────────────

def _fun_avg(monster):
    scores = monster.get("fun_factor_score") or {}
    vals = [v for v in scores.values() if v is not None]
    return sum(vals) / len(vals) if vals else 0


def _unique_mechanic_count(monster_id, patterns_by_id):
    entry = patterns_by_id.get(monster_id, {})
    timeline = entry.get("timeline", [])
    return len(set(t.get("pattern_type", "") for t in timeline))


def _total_views(monster_id, videos_by_id):
    return sum(v.get("view_count", 0) for v in videos_by_id.get(monster_id, []))


@app.route("/api/ranking")
def api_ranking():
    monsters = read_json("monsters.json") or []
    patterns = read_json("patterns.json") or []
    videos   = read_json("videos.json") or []

    patterns_by_id = {p["monster_id"]: p for p in patterns}
    videos_by_id = {}
    for v in videos:
        videos_by_id.setdefault(v.get("monster_id"), []).append(v)

    top = 10

    most_difficult = sorted(
        monsters,
        key=lambda m: m.get("mechanic_complexity") or 0,
        reverse=True,
    )[:top]

    most_fun = sorted(monsters, key=_fun_avg, reverse=True)[:top]

    most_unique = sorted(
        monsters,
        key=lambda m: _unique_mechanic_count(m["id"], patterns_by_id),
        reverse=True,
    )[:top]

    most_viewed = sorted(
        monsters,
        key=lambda m: _total_views(m["id"], videos_by_id),
        reverse=True,
    )[:top]

    return ok({
        "most_difficult":      most_difficult,
        "most_fun":            most_fun,
        "most_unique_mechanic": most_unique,
        "most_viewed":         most_viewed,
    })


# ─── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("web_tool running → http://localhost:5000")
    print("LAN access      → http://<your-ip>:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
