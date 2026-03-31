"""
app.py — FitSearch AI Platform
Complete backend with ALL routes required by the frontend.
"""

from flask import Flask, request, jsonify, session, send_from_directory
from flask_cors import CORS
import sqlite3
import os
import hashlib
import sys
import time
from functools import wraps

# ── Paths ─────────────────────────────────────────────────────────────────

CURRENT_DIR  = os.path.dirname(os.path.abspath(__file__))
BASE_DIR     = os.path.dirname(CURRENT_DIR)
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
DB_DIR       = os.path.join(BASE_DIR, "database")
DB_PATH      = os.path.join(DB_DIR, "users.db")
UPLOAD_DIR   = os.path.join(BASE_DIR, "uploads")

os.makedirs(DB_DIR,     exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ── Backend imports ────────────────────────────────────────────────────────

sys.path.insert(0, BASE_DIR)
sys.path.insert(0, CURRENT_DIR)

from backend.search_ai import search_knowledge, get_recommendations
from backend.diet_ai   import generate_diet
from backend.calorie_ai import calculate_calories
from backend.cycle_ai  import generate_cycle
from backend.medical_ai import analyze_medical

# ── Flask ──────────────────────────────────────────────────────────────────

app = Flask(__name__, static_folder=os.path.join(BASE_DIR, "static"))
app.secret_key = os.environ.get("SECRET_KEY", "fitsearch-secret-key-2024")

CORS(app, supports_credentials=True)

# ── Database ───────────────────────────────────────────────────────────────

def init_db():
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

init_db()

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ── Auth helpers ───────────────────────────────────────────────────────────

def hash_password(pw):
    return hashlib.sha256(pw.encode("utf-8")).hexdigest()

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "Login required"}), 401
        return f(*args, **kwargs)
    return decorated

def uid():
    return session.get("user_id")

def user_row_to_dict(user):
    return {
        "id":               user["id"],
        "name":             user["name"],
        "email":            user["email"],
        "experience_level": user["experience_level"],
        "goal":             user["goal"],
        "weight":           user["weight"],
        "height":           user["height"],
        "age":              user["age"],
        "sex":              user["sex"],
        "activity_level":   user["activity_level"],
        "tier":             user["tier"],
    }

# ═══════════════════════════════════════════════════════════════════════════
# FRONTEND — serve the SPA
# ═══════════════════════════════════════════════════════════════════════════

@app.route("/")
def home():
    return send_from_directory(FRONTEND_DIR, "index.html")

@app.route("/<path:path>")
def catch_all(path):
    fp = os.path.join(FRONTEND_DIR, path)
    if os.path.isfile(fp):
        return send_from_directory(FRONTEND_DIR, path)
    return send_from_directory(FRONTEND_DIR, "index.html")

# ═══════════════════════════════════════════════════════════════════════════
# AUTH
# ═══════════════════════════════════════════════════════════════════════════

@app.route("/register", methods=["POST"])
def register():
    try:
        data = request.get_json(force=True) or {}
        if not data.get("email") or not data.get("password"):
            return jsonify({"error": "Email and password required"}), 400
        if len(data["password"]) < 6:
            return jsonify({"error": "Password must be at least 6 characters"}), 400
        with get_db() as conn:
            conn.execute(
                """INSERT INTO users
                   (name,email,password_hash,experience_level,goal,weight,height,age,sex,activity_level)
                   VALUES (?,?,?,?,?,?,?,?,?,?)""",
                (
                    data.get("name", "User").strip(),
                    data["email"].strip().lower(),
                    hash_password(data["password"]),
                    data.get("experience_level", "beginner"),
                    data.get("goal", "muscle_gain"),
                    data.get("weight") or None,
                    data.get("height") or None,
                    data.get("age") or None,
                    data.get("sex", "male"),
                    data.get("activity_level", "moderate"),
                )
            )
        return jsonify({"status": "registered"})
    except sqlite3.IntegrityError:
        return jsonify({"error": "Email already registered — please sign in"}), 409
    except Exception as e:
        print("Register error:", e)
        return jsonify({"error": "Server error"}), 500

@app.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json(force=True) or {}
        if not data.get("email") or not data.get("password"):
            return jsonify({"error": "Email and password required"}), 400
        with get_db() as conn:
            user = conn.execute(
                "SELECT * FROM users WHERE email=? AND password_hash=?",
                (data["email"].strip().lower(), hash_password(data["password"]))
            ).fetchone()
        if not user:
            return jsonify({"error": "Invalid email or password"}), 401
        session["user_id"] = user["id"]
        return jsonify({"status": "success", "user": user_row_to_dict(user)})
    except Exception as e:
        print("Login error:", e)
        return jsonify({"error": "Server error"}), 500

@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"status": "ok"})

@app.route("/me", methods=["GET"])
@login_required
def me():
    with get_db() as conn:
        user = conn.execute("SELECT * FROM users WHERE id=?", (uid(),)).fetchone()
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user_row_to_dict(user))

@app.route("/profile", methods=["PUT"])
@login_required
def update_profile():
    data = request.get_json(force=True) or {}
    allowed = ["name", "experience_level", "goal", "weight", "height", "age", "sex", "activity_level"]
    updates = {k: v for k, v in data.items() if k in allowed and v is not None}
    if not updates:
        return jsonify({"error": "No valid fields"}), 400
    set_clause = ", ".join(f"{k}=?" for k in updates)
    with get_db() as conn:
        conn.execute(f"UPDATE users SET {set_clause} WHERE id=?", (*updates.values(), uid()))
    with get_db() as conn:
        user = conn.execute("SELECT * FROM users WHERE id=?", (uid(),)).fetchone()
    return jsonify(user_row_to_dict(user))

# ═══════════════════════════════════════════════════════════════════════════
# SEARCH & HISTORY
# ═══════════════════════════════════════════════════════════════════════════

@app.route("/search", methods=["POST"])
@login_required
def search():
    try:
        data    = request.get_json(force=True) or {}
        query   = (data.get("query") or "").strip()
        filters = data.get("filters") or []
        if not query:
            return jsonify({"query": "", "results": [], "count": 0})
        results = search_knowledge(query, filters)
        with get_db() as conn:
            conn.execute(
                "INSERT INTO search_history(user_id,query,results_count) VALUES (?,?,?)",
                (uid(), query, len(results))
            )
        return jsonify({"query": query, "results": results, "count": len(results)})
    except Exception as e:
        print("Search error:", e)
        return jsonify({"query": "", "results": [], "count": 0, "error": str(e)}), 500

@app.route("/history", methods=["GET"])
@login_required
def history():
    limit = min(int(request.args.get("limit", 50)), 200)
    with get_db() as conn:
        rows = conn.execute(
            "SELECT id,query,results_count,searched_at FROM search_history "
            "WHERE user_id=? ORDER BY searched_at DESC LIMIT ?",
            (uid(), limit)
        ).fetchall()
    return jsonify([dict(r) for r in rows])

@app.route("/history/clear", methods=["DELETE"])
@login_required
def clear_history():
    with get_db() as conn:
        conn.execute("DELETE FROM search_history WHERE user_id=?", (uid(),))
    return jsonify({"status": "cleared"})

@app.route("/history/<int:hid>", methods=["DELETE"])
@login_required
def delete_history_item(hid):
    with get_db() as conn:
        conn.execute("DELETE FROM search_history WHERE id=? AND user_id=?", (hid, uid()))
    return jsonify({"status": "deleted"})

@app.route("/recommendations", methods=["GET"])
@login_required
def recommendations():
    with get_db() as conn:
        user = dict(conn.execute("SELECT * FROM users WHERE id=?", (uid(),)).fetchone())
        rows = conn.execute(
            "SELECT query FROM search_history WHERE user_id=? "
            "ORDER BY searched_at DESC LIMIT 20", (uid(),)
        ).fetchall()
    queries = [r["query"] for r in rows]
    recs    = get_recommendations(queries, user)
    return jsonify(recs)

# ═══════════════════════════════════════════════════════════════════════════
# DIET GENERATOR (with optional BCA file upload)
# ═══════════════════════════════════════════════════════════════════════════

@app.route("/diet", methods=["POST"])
@login_required
def diet():
    try:
        data = request.get_json(force=True) or {}
        with get_db() as conn:
            user = dict(conn.execute("SELECT * FROM users WHERE id=?", (uid(),)).fetchone())
        # Merge user profile with request data (request overrides profile)
        merged = {**user, **{k: v for k, v in data.items() if v is not None and v != ""}}
        calories = calculate_calories(merged)
        plan     = generate_diet(merged, calories)
        import json
        with get_db() as conn:
            conn.execute(
                "INSERT INTO diet_plans(user_id,plan_data,goal,calories) VALUES (?,?,?,?)",
                (uid(), json.dumps(plan), merged.get("goal"), calories)
            )
        return jsonify({"calories": calories, "diet": plan, "macros": plan.get("macros", {})})
    except Exception as e:
        print("Diet error:", e)
        return jsonify({"error": str(e)}), 500

@app.route("/upload_bca", methods=["POST"])
@login_required
def upload_bca():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    f     = request.files["file"]
    fname = f"{uid()}_bca_{int(time.time())}_{f.filename}"
    f.save(os.path.join(UPLOAD_DIR, fname))
    return jsonify({"status": "uploaded", "file": fname})

# ═══════════════════════════════════════════════════════════════════════════
# CYCLE PLANNER (with optional medical report upload)
# ═══════════════════════════════════════════════════════════════════════════

@app.route("/cycle", methods=["POST"])
@login_required
def cycle():
    try:
        data = request.get_json(force=True) or {}
        with get_db() as conn:
            user = dict(conn.execute("SELECT * FROM users WHERE id=?", (uid(),)).fetchone())
        merged = {**user, **{k: v for k, v in data.items() if v is not None and v != ""}}
        result = generate_cycle(merged)
        import json
        with get_db() as conn:
            conn.execute(
                "INSERT INTO cycle_logs(user_id,cycle_name,cycle_data) VALUES (?,?,?)",
                (uid(), result.get("cycle_name", "Custom cycle"), json.dumps(result))
            )
        return jsonify(result)
    except Exception as e:
        print("Cycle error:", e)
        return jsonify({"error": str(e)}), 500

@app.route("/upload_medical", methods=["POST"])
@login_required
def upload_medical():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    f     = request.files["file"]
    fname = f"{uid()}_medical_{int(time.time())}_{f.filename}"
    f.save(os.path.join(UPLOAD_DIR, fname))
    return jsonify({"status": "uploaded", "file": fname})

# ═══════════════════════════════════════════════════════════════════════════
# MEDICAL SCREEN
# ═══════════════════════════════════════════════════════════════════════════

@app.route("/medical", methods=["POST"])
@login_required
def medical():
    try:
        data = request.get_json(force=True) or {}
        with get_db() as conn:
            user = dict(conn.execute("SELECT * FROM users WHERE id=?", (uid(),)).fetchone())
        result = analyze_medical({**user, **data})
        return jsonify(result)
    except Exception as e:
        print("Medical error:", e)
        return jsonify({"error": str(e)}), 500

# ═══════════════════════════════════════════════════════════════════════════
# PHYSIQUE UPLOAD
# ═══════════════════════════════════════════════════════════════════════════

@app.route("/upload_physique", methods=["POST"])
@login_required
def upload_physique():
    files    = request.files.getlist("files")
    uploaded = []
    for f in files:
        fname = f"{uid()}_physique_{int(time.time())}_{f.filename}"
        f.save(os.path.join(UPLOAD_DIR, fname))
        uploaded.append(fname)
    return jsonify({"uploaded": uploaded, "count": len(uploaded)})

# ═══════════════════════════════════════════════════════════════════════════
# HEALTH CHECK
# ═══════════════════════════════════════════════════════════════════════════

@app.route("/health")
def health():
    return jsonify({"status": "ok", "version": "4.1"})

# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)

# ═══════════════════════════════════════════════════════════════════════════
# CACHE STATS  (new endpoint)
# ═══════════════════════════════════════════════════════════════════════════

@app.route("/cache/stats", methods=["GET"])
def cache_stats():
    from backend.search_ai import _cache_stats
    return jsonify(_cache_stats())

@app.route("/cache/clear", methods=["DELETE"])
@login_required
def cache_clear():
    import sqlite3 as _sq
    from backend.search_ai import CACHE_DB
    with _sq.connect(CACHE_DB) as conn:
        conn.execute("DELETE FROM report_cache")
    return jsonify({"status": "cleared"})
