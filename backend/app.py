"""
app.py — FitSearch AI Platform (Optimized for Modern UI)
"""

import os
import sys
import time
import json
import hashlib
import sqlite3
from functools import wraps
from flask import Flask, request, jsonify, session, send_from_directory
from flask_cors import CORS

# ── Paths ──────────────────────────────────────────────
CURRENT_DIR  = os.path.dirname(os.path.abspath(__file__))
BASE_DIR     = os.path.dirname(CURRENT_DIR)
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
DB_DIR       = os.path.join(BASE_DIR, "database")
DB_PATH      = os.path.join(DB_DIR, "users.db")
UPLOAD_DIR   = os.path.join(BASE_DIR, "uploads")

BCA_DIR      = os.path.join(UPLOAD_DIR, "bca")
MEDICAL_DIR  = os.path.join(UPLOAD_DIR, "medical")
PHYSIQUE_DIR = os.path.join(UPLOAD_DIR, "physique")

for d in [DB_DIR, UPLOAD_DIR, BCA_DIR, MEDICAL_DIR, PHYSIQUE_DIR]:
    os.makedirs(d, exist_ok=True)

sys.path.insert(0, BASE_DIR)
sys.path.insert(0, CURRENT_DIR)

from backend.search_ai import search_knowledge, get_recommendations, _cache_stats, CACHE_DB
from backend.diet_ai import generate_diet
from backend.calorie_ai import calculate_calories
from backend.cycle_ai import generate_cycle
from backend.medical_ai import analyze_medical

# ── Flask App ─────────────────────────────────────────
app = Flask(__name__, static_folder=os.path.join(BASE_DIR, "static"))
app.secret_key = os.environ.get("SECRET_KEY", "fitsearch-secret-key-2026")
CORS(app, supports_credentials=True)

# ── Database Helpers ──────────────────────────────────
def init_db():
    """Initialize DB and tables if not exist"""
    if os.path.exists(DB_PATH):
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.execute("PRAGMA schema_version;")
            conn.close()
        except Exception:
            print("Corrupt DB — recreating")
            os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id               INTEGER PRIMARY KEY AUTOINCREMENT,
        name             TEXT    NOT NULL DEFAULT 'User',
        email            TEXT    UNIQUE NOT NULL,
        password_hash    TEXT    NOT NULL,
        experience_level TEXT    DEFAULT 'beginner',
        goal             TEXT    DEFAULT 'muscle_gain',
        weight           REAL,
        height           REAL,
        age              INTEGER,
        sex              TEXT    DEFAULT 'male',
        activity_level   TEXT    DEFAULT 'moderate',
        tier             TEXT    DEFAULT 'free',
        created_at       TEXT    DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS search_history (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id      INTEGER NOT NULL,
        query        TEXT    NOT NULL,
        results_count INTEGER DEFAULT 0,
        searched_at  TEXT    DEFAULT (datetime('now')),
        FOREIGN KEY(user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS saved_items (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id    INTEGER NOT NULL,
        item_type  TEXT    NOT NULL,
        item_name  TEXT    NOT NULL,
        saved_at   TEXT    DEFAULT (datetime('now')),
        FOREIGN KEY(user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS diet_plans (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id    INTEGER NOT NULL,
        plan_data  TEXT,
        goal       TEXT,
        calories   INTEGER,
        bca_file   TEXT,
        created_at TEXT    DEFAULT (datetime('now')),
        FOREIGN KEY(user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS cycle_logs (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id      INTEGER NOT NULL,
        cycle_name   TEXT,
        cycle_data   TEXT,
        medical_file TEXT,
        created_at   TEXT    DEFAULT (datetime('now')),
        FOREIGN KEY(user_id) REFERENCES users(id)
    );
    """)
    conn.commit()
    conn.close()

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

init_db()

# ── Auth & Helpers ────────────────────────────────────
def hash_password(pw: str) -> str:
    return hashlib.sha256(pw.encode("utf-8")).hexdigest()

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "Login required"}), 401
        return f(*args, **kwargs)
    return decorated

def get_current_user():
    with get_db() as conn:
        user = conn.execute("SELECT * FROM users WHERE id=?", (session.get("user_id"),)).fetchone()
    return dict(user) if user else None

def user_row_to_dict(user):
    return {
        "id": user["id"],
        "name": user["name"],
        "email": user["email"],
        "experience_level": user["experience_level"],
        "goal": user["goal"],
        "weight": user["weight"],
        "height": user["height"],
        "age": user["age"],
        "sex": user["sex"],
        "activity_level": user["activity_level"],
        "tier": user["tier"]
    }

def save_file(f, folder, prefix):
    filename = f"{session.get('user_id')}_{prefix}_{int(time.time())}_{f.filename}"
    path = os.path.join(folder, filename)
    f.save(path)
    return filename

# ── FRONTEND ─────────────────────────────────────────
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def frontend(path):
    fp = os.path.join(FRONTEND_DIR, path)
    if path and os.path.isfile(fp):
        return send_from_directory(FRONTEND_DIR, path)
    return send_from_directory(FRONTEND_DIR, "index.html")

# ── AUTH ROUTES ──────────────────────────────────────
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json(force=True) or {}
    email, password = data.get("email"), data.get("password")
    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400
    try:
        with get_db() as conn:
            conn.execute(
                """INSERT INTO users
                (name,email,password_hash,experience_level,goal,weight,height,age,sex,activity_level)
                VALUES (?,?,?,?,?,?,?,?,?,?)""",
                (
                    data.get("name", "User").strip(),
                    email.strip().lower(),
                    hash_password(password),
                    data.get("experience_level", "beginner"),
                    data.get("goal", "muscle_gain"),
                    data.get("weight") or None,
                    data.get("height") or None,
                    data.get("age") or None,
                    data.get("sex", "male"),
                    data.get("activity_level", "moderate")
                )
            )
        return jsonify({"status": "registered"})
    except sqlite3.IntegrityError:
        return jsonify({"error": "Email already registered"}), 409
    except Exception as e:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Register error: {e}")
        return jsonify({"error": "Server error"}), 500

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json(force=True) or {}
    email, password = data.get("email"), data.get("password")
    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400
    try:
        with get_db() as conn:
            user = conn.execute(
                "SELECT * FROM users WHERE email=? AND password_hash=?",
                (email.strip().lower(), hash_password(password))
            ).fetchone()
        if not user:
            return jsonify({"error": "Invalid email or password"}), 401
        session["user_id"] = user["id"]
        return jsonify({"status": "success", "user": user_row_to_dict(user)})
    except Exception as e:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Login error: {e}")
        return jsonify({"error": "Server error"}), 500

@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"status": "ok"})

@app.route("/me", methods=["GET"])
@login_required
def me():
    user = get_current_user()
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user_row_to_dict(user))

@app.route("/profile", methods=["PUT"])
@login_required
def update_profile():
    data = request.get_json(force=True) or {}
    allowed = ["name","experience_level","goal","weight","height","age","sex","activity_level"]
    updates = {k:v for k,v in data.items() if k in allowed and v is not None}
    if not updates:
        return jsonify({"error": "No valid fields"}), 400
    set_clause = ", ".join(f"{k}=?" for k in updates)
    with get_db() as conn:
        conn.execute(f"UPDATE users SET {set_clause} WHERE id=?", (*updates.values(), session["user_id"]))
        user = conn.execute("SELECT * FROM users WHERE id=?", (session["user_id"],)).fetchone()
    return jsonify(user_row_to_dict(user))

# ── SEARCH & HISTORY ──────────────────────────────────
@app.route("/search", methods=["POST"])
@login_required
def search():
    data = request.get_json(force=True) or {}
    query, filters = (data.get("query") or "").strip(), data.get("filters") or []
    if not query:
        return jsonify({"query": "", "results": [], "count": 0})
    try:
        results = search_knowledge(query, filters)
        with get_db() as conn:
            conn.execute("INSERT INTO search_history(user_id,query,results_count) VALUES (?,?,?)",
                         (session["user_id"], query, len(results)))
        # UI-friendly structure: grouped by type if available
        results_structured = [{"title": r.get("title"), "summary": r.get("summary"), "type": r.get("type"), "link": r.get("link")} for r in results]
        return jsonify({"query": query, "results": results_structured, "count": len(results_structured)})
    except Exception as e:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Search error: {e}")
        return jsonify({"query": query, "results": [], "count": 0, "error": str(e)}), 500

@app.route("/history", methods=["GET"])
@login_required
def history():
    limit = min(int(request.args.get("limit", 50)), 200)
    with get_db() as conn:
        rows = conn.execute(
            "SELECT id,query,results_count,searched_at FROM search_history "
            "WHERE user_id=? ORDER BY searched_at DESC LIMIT ?",
            (session["user_id"], limit)
        ).fetchall()
    return jsonify([dict(r) for r in rows])

@app.route("/history/clear", methods=["DELETE"])
@login_required
def clear_history():
    with get_db() as conn:
        conn.execute("DELETE FROM search_history WHERE user_id=?", (session["user_id"],))
    return jsonify({"status": "cleared"})

@app.route("/history/<int:hid>", methods=["DELETE"])
@login_required
def delete_history_item(hid):
    with get_db() as conn:
        conn.execute("DELETE FROM search_history WHERE id=? AND user_id=?", (hid, session["user_id"]))
    return jsonify({"status": "deleted"})

@app.route("/recommendations", methods=["GET"])
@login_required
def recommendations():
    with get_db() as conn:
        user = dict(conn.execute("SELECT * FROM users WHERE id=?", (session["user_id"],)).fetchone())
        rows = conn.execute(
            "SELECT query FROM search_history WHERE user_id=? ORDER BY searched_at DESC LIMIT 20",
            (session["user_id"],)
        ).fetchall()
    queries = [r["query"] for r in rows]
    recs = get_recommendations(queries, user)
    return jsonify(recs)

# ── DIET GENERATOR ───────────────────────────────────
@app.route("/diet", methods=["POST"])
@login_required
def diet():
    try:
        user = get_current_user()
        data = request.get_json(force=True) or {}
        merged = {**user, **{k:v for k,v in data.items() if v not in [None,""]}}
        calories = calculate_calories(merged)
        plan = generate_diet(merged, calories)
        with get_db() as conn:
            conn.execute("INSERT INTO diet_plans(user_id,plan_data,goal,calories) VALUES (?,?,?,?)",
                         (session["user_id"], json.dumps(plan), merged.get("goal"), calories))
        return jsonify({"calories": calories, "diet": plan, "macros": plan.get("macros", {})})
    except Exception as e:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Diet error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/upload_bca", methods=["POST"])
@login_required
def upload_bca():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    fname = save_file(request.files["file"], BCA_DIR, "bca")
    return jsonify({"status": "uploaded", "file": fname})

# ── CYCLE PLANNER ───────────────────────────────────
@app.route("/cycle", methods=["POST"])
@login_required
def cycle():
    try:
        user = get_current_user()
        data = request.get_json(force=True) or {}
        merged = {**user, **{k:v for k,v in data.items() if v not in [None,""]}}
        result = generate_cycle(merged)
        with get_db() as conn:
            conn.execute("INSERT INTO cycle_logs(user_id,cycle_name,cycle_data) VALUES (?,?,?)",
                         (session["user_id"], result.get("cycle_name","Custom cycle"), json.dumps(result)))
        return jsonify(result)
    except Exception as e:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Cycle error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/upload_medical", methods=["POST"])
@login_required
def upload_medical():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    fname = save_file(request.files["file"], MEDICAL_DIR, "medical")
    return jsonify({"status": "uploaded", "file": fname})

# ── MEDICAL SCREEN ───────────────────────────────────
@app.route("/medical", methods=["POST"])
@login_required
def medical():
    try:
        user = get_current_user()
        data = request.get_json(force=True) or {}
        result = analyze_medical({**user, **data})
        return jsonify(result)
    except Exception as e:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Medical error: {e}")
        return jsonify({"error": str(e)}), 500

# ── PHYSIQUE UPLOAD ──────────────────────────────────
@app.route("/upload_physique", methods=["POST"])
@login_required
def upload_physique():
    files = request.files.getlist("files")
    uploaded = [save_file(f, PHYSIQUE_DIR, "physique") for f in files]
    return jsonify({"uploaded": uploaded, "count": len(uploaded)})

# ── HEALTH CHECK ────────────────────────────────────
@app.route("/health")
def health():
    return jsonify({"status": "ok", "version": "4.2"})

# ── CACHE MANAGEMENT ─────────────────────────────────
@app.route("/cache/stats", methods=["GET"])
def cache_stats():
    return jsonify(_cache_stats())

@app.route("/cache/clear", methods=["DELETE"])
@login_required
def cache_clear():
    import sqlite3 as _sq
    with _sq.connect(CACHE_DB) as conn:
        conn.execute("DELETE FROM report_cache")
    return jsonify({"status": "cleared"})

# ── RUN APP ─────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
