"""
app.py — FitSearch AI Platform v6
==================================
Production-grade Flask backend with:
- Full auth (session-based)
- AI-powered search with Claude API
- Knowledge base + PubMed integration
- Diet, cycle, medical, BCA tools
- Proper error handling & caching
"""

from __future__ import annotations
import os, sys, json, hashlib, time, sqlite3
from functools import wraps

from flask import Flask, request, jsonify, session, send_from_directory
from flask_cors import CORS

# ── Paths ─────────────────────────────────────────────────────────────────
CURRENT_DIR  = os.path.dirname(os.path.abspath(__file__))
BASE_DIR     = os.path.dirname(CURRENT_DIR)
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
DB_DIR       = os.path.join(BASE_DIR, "database")
DB_PATH      = os.path.join(DB_DIR, "users.db")
UPLOAD_DIR   = os.path.join(BASE_DIR, "uploads")
STATIC_DIR   = os.path.join(BASE_DIR, "static")

os.makedirs(DB_DIR,     exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)

sys.path.insert(0, BASE_DIR)
sys.path.insert(0, CURRENT_DIR)

# ── Lazy imports ─────────────────────────────────────────────────────────
def _safe_import(module_name, attr=None):
    try:
        import importlib
        mod = importlib.import_module(f"backend.{module_name}")
        return getattr(mod, attr) if attr else mod
    except Exception as e:
        print(f"[Import] backend.{module_name}: {e}")
        return None

_search_knowledge   = _safe_import("search_ai", "search_knowledge")
_get_recs           = _safe_import("search_ai", "get_recommendations")
_generate_diet      = _safe_import("diet_ai", "generate_diet")
_calculate_calories = _safe_import("calorie_ai", "calculate_calories")
_generate_cycle     = _safe_import("cycle_ai", "generate_cycle")
_analyze_medical    = _safe_import("medical_ai", "analyze_medical")

def search_knowledge(q, f):
    return _search_knowledge(q, f) if _search_knowledge else []

def get_recommendations(queries, user):
    return _get_recs(queries, user) if _get_recs else []

def generate_diet(user, cals):
    return _generate_diet(user, cals) if _generate_diet else {"error": "Module unavailable"}

def calculate_calories(user):
    return _calculate_calories(user) if _calculate_calories else 2000

def generate_cycle(user):
    return _generate_cycle(user) if _generate_cycle else {"error": "Module unavailable"}

def analyze_medical(data):
    return _analyze_medical(data) if _analyze_medical else {"error": "Module unavailable"}


# ── Flask ─────────────────────────────────────────────────────────────────
app = Flask(__name__, static_folder=STATIC_DIR)
app.secret_key = os.environ.get("NEW_SECRET", os.environ.get("SECRET_KEY", "11962aa111ff110443986c5edfa42c0d"))
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

CORS(app, supports_credentials=True, origins="*")


# ═══════════════════════════════════════════════════════════════════════════
# DATABASE
# ═══════════════════════════════════════════════════════════════════════════

def init_db():
    if os.path.exists(DB_PATH):
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.execute("PRAGMA schema_version;")
            conn.close()
        except Exception:
            print("[DB] Recreating database")
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
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id       INTEGER NOT NULL,
        query         TEXT    NOT NULL,
        results_count INTEGER DEFAULT 0,
        searched_at   TEXT    DEFAULT (datetime('now')),
        FOREIGN KEY(user_id) REFERENCES users(id)
    );
    CREATE TABLE IF NOT EXISTS saved_items (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id    INTEGER NOT NULL,
        item_type  TEXT    NOT NULL,
        item_name  TEXT    NOT NULL,
        item_data  TEXT,
        saved_at   TEXT    DEFAULT (datetime('now')),
        FOREIGN KEY(user_id) REFERENCES users(id)
    );
    CREATE TABLE IF NOT EXISTS diet_plans (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id    INTEGER NOT NULL,
        plan_data  TEXT,
        goal       TEXT,
        calories   INTEGER,
        created_at TEXT    DEFAULT (datetime('now')),
        FOREIGN KEY(user_id) REFERENCES users(id)
    );
    CREATE TABLE IF NOT EXISTS cycle_logs (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id    INTEGER NOT NULL,
        cycle_name TEXT,
        cycle_data TEXT,
        created_at TEXT    DEFAULT (datetime('now')),
        FOREIGN KEY(user_id) REFERENCES users(id)
    );
    CREATE INDEX IF NOT EXISTS idx_sh_user ON search_history(user_id);
    CREATE INDEX IF NOT EXISTS idx_sh_time ON search_history(searched_at);
    """)
    conn.commit()
    conn.close()

init_db()


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ═══════════════════════════════════════════════════════════════════════════
# AUTH HELPERS
# ═══════════════════════════════════════════════════════════════════════════

def hash_password(pw):
    return hashlib.sha256(pw.encode("utf-8")).hexdigest()

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "Authentication required"}), 401
        return f(*args, **kwargs)
    return decorated

def uid():
    return session.get("user_id")

def user_to_dict(user):
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
        "created_at":       user["created_at"],
    }


# ═══════════════════════════════════════════════════════════════════════════
# STATIC / SPA
# ═══════════════════════════════════════════════════════════════════════════

@app.route("/")
def home():
    return send_from_directory(FRONTEND_DIR, "index.html")

@app.route("/<path:path>")
def catch_all(path):
    fp = os.path.join(FRONTEND_DIR, path)
    if os.path.isfile(fp):
        return send_from_directory(FRONTEND_DIR, path)
    static_fp = os.path.join(STATIC_DIR, path)
    if os.path.isfile(static_fp):
        return send_from_directory(STATIC_DIR, path)
    return send_from_directory(FRONTEND_DIR, "index.html")


# ═══════════════════════════════════════════════════════════════════════════
# AUTH
# ═══════════════════════════════════════════════════════════════════════════

@app.route("/register", methods=["POST"])
def register():
    try:
        data  = request.get_json(force=True) or {}
        email = (data.get("email") or "").strip().lower()
        pw    = data.get("password") or ""
        name  = (data.get("name") or "User").strip()
        if not email or "@" not in email:
            return jsonify({"error": "Valid email required"}), 400
        if not pw or len(pw) < 6:
            return jsonify({"error": "Password must be at least 6 characters"}), 400
        with get_db() as conn:
            conn.execute(
                "INSERT INTO users (name,email,password_hash,experience_level,goal,weight,height,age,sex,activity_level) VALUES (?,?,?,?,?,?,?,?,?,?)",
                (name, email, hash_password(pw),
                 data.get("experience_level","beginner"),
                 data.get("goal","muscle_gain"),
                 data.get("weight") or None,
                 data.get("height") or None,
                 data.get("age") or None,
                 data.get("sex","male"),
                 data.get("activity_level","moderate"))
            )
        return jsonify({"status": "registered"})
    except sqlite3.IntegrityError:
        return jsonify({"error": "Email already registered — please sign in"}), 409
    except Exception as e:
        print(f"[Register] {e}")
        return jsonify({"error": "Server error"}), 500


@app.route("/login", methods=["POST"])
def login():
    try:
        data  = request.get_json(force=True) or {}
        email = (data.get("email") or "").strip().lower()
        pw    = data.get("password") or ""
        if not email or not pw:
            return jsonify({"error": "Email and password required"}), 400
        with get_db() as conn:
            user = conn.execute(
                "SELECT * FROM users WHERE email=? AND password_hash=?",
                (email, hash_password(pw))
            ).fetchone()
        if not user:
            return jsonify({"error": "Invalid email or password"}), 401
        session["user_id"] = user["id"]
        session.permanent = True
        return jsonify({"status": "success", "user": user_to_dict(user)})
    except Exception as e:
        print(f"[Login] {e}")
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
        session.clear()
        return jsonify({"error": "User not found"}), 404
    return jsonify(user_to_dict(user))


@app.route("/profile", methods=["PUT"])
@login_required
def update_profile():
    data = request.get_json(force=True) or {}
    allowed = ["name","experience_level","goal","weight","height","age","sex","activity_level"]
    updates = {k: v for k, v in data.items() if k in allowed and v is not None}
    if not updates:
        return jsonify({"error": "No valid fields"}), 400
    set_clause = ", ".join(f"{k}=?" for k in updates)
    with get_db() as conn:
        conn.execute(f"UPDATE users SET {set_clause} WHERE id=?", (*updates.values(), uid()))
    with get_db() as conn:
        user = conn.execute("SELECT * FROM users WHERE id=?", (uid(),)).fetchone()
    return jsonify(user_to_dict(user))


# ═══════════════════════════════════════════════════════════════════════════
# SEARCH
# ═══════════════════════════════════════════════════════════════════════════

@app.route("/search", methods=["POST"])
@login_required
def search():
    try:
        data    = request.get_json(force=True) or {}
        query   = (data.get("query") or "").strip()[:500]
        filters = data.get("filters") or []
        if not query:
            return jsonify({"query":"","results":[],"count":0})
        results = search_knowledge(query, filters)
        try:
            with get_db() as conn:
                conn.execute(
                    "INSERT INTO search_history(user_id,query,results_count) VALUES (?,?,?)",
                    (uid(), query, len(results))
                )
        except Exception:
            pass
        return jsonify({"query":query,"results":results,"count":len(results),"filters":filters})
    except Exception as e:
        print(f"[Search] {e}")
        return jsonify({"query":"","results":[],"count":0,"error":"Search temporarily unavailable"}), 500


@app.route("/search/suggestions", methods=["GET"])
def search_suggestions():
    prefix = (request.args.get("q") or "").lower().strip()
    if len(prefix) < 2:
        return jsonify([])
    suggestions = [
        "What is RAD140?","Testosterone enanthate cycle",
        "Best supplements for muscle gain","Creatine monohydrate guide",
        "BPC-157 injury healing","Fat loss exercises for women",
        "Beginner workout plan","Ostarine MK-2866 dosage",
        "LGD-4033 cycle protocol","HGH human growth hormone",
        "Pre workout supplement stack","Whey protein guide",
        "HIIT cardio fat loss","Anavar oxandrolone cutting",
        "MK-677 ibutamoren dosage","Nandrolone deca durabolin",
        "Vitamin D3 testosterone","Omega-3 fish oil benefits",
        "High protein diet plan","Strength training program",
        "Peptides for fat loss","SARMs beginner guide",
    ]
    return jsonify([s for s in suggestions if prefix in s.lower()][:6])


# ═══════════════════════════════════════════════════════════════════════════
# HISTORY
# ═══════════════════════════════════════════════════════════════════════════

@app.route("/history", methods=["GET"])
@login_required
def history():
    limit = min(int(request.args.get("limit",50)), 500)
    with get_db() as conn:
        rows = conn.execute(
            "SELECT id,query,results_count,searched_at FROM search_history WHERE user_id=? ORDER BY searched_at DESC LIMIT ?",
            (uid(), limit)
        ).fetchall()
    return jsonify([dict(r) for r in rows])


@app.route("/history/clear", methods=["DELETE"])
@login_required
def clear_history():
    with get_db() as conn:
        conn.execute("DELETE FROM search_history WHERE user_id=?", (uid(),))
    return jsonify({"status":"cleared"})


@app.route("/history/<int:hid>", methods=["DELETE"])
@login_required
def delete_history_item(hid):
    with get_db() as conn:
        conn.execute("DELETE FROM search_history WHERE id=? AND user_id=?", (hid, uid()))
    return jsonify({"status":"deleted"})


@app.route("/recommendations", methods=["GET"])
@login_required
def recommendations():
    with get_db() as conn:
        user = dict(conn.execute("SELECT * FROM users WHERE id=?", (uid(),)).fetchone())
        rows = conn.execute(
            "SELECT query FROM search_history WHERE user_id=? ORDER BY searched_at DESC LIMIT 20",
            (uid(),)
        ).fetchall()
    queries = [r["query"] for r in rows]
    return jsonify(get_recommendations(queries, user))


# ═══════════════════════════════════════════════════════════════════════════
# SAVED ITEMS
# ═══════════════════════════════════════════════════════════════════════════

@app.route("/saved", methods=["GET"])
@login_required
def get_saved():
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM saved_items WHERE user_id=? ORDER BY saved_at DESC",
            (uid(),)
        ).fetchall()
    return jsonify([dict(r) for r in rows])


@app.route("/saved", methods=["POST"])
@login_required
def save_item():
    data = request.get_json(force=True) or {}
    name = data.get("name","")
    if not name:
        return jsonify({"error":"Item name required"}), 400
    with get_db() as conn:
        conn.execute(
            "INSERT INTO saved_items(user_id,item_type,item_name,item_data) VALUES (?,?,?,?)",
            (uid(), data.get("type","search"), name, json.dumps(data.get("data",{})))
        )
    return jsonify({"status":"saved"})


@app.route("/saved/<int:sid>", methods=["DELETE"])
@login_required
def delete_saved(sid):
    with get_db() as conn:
        conn.execute("DELETE FROM saved_items WHERE id=? AND user_id=?", (sid, uid()))
    return jsonify({"status":"deleted"})


# ═══════════════════════════════════════════════════════════════════════════
# DIET
# ═══════════════════════════════════════════════════════════════════════════

@app.route("/diet", methods=["POST"])
@login_required
def diet():
    try:
        data = request.get_json(force=True) or {}
        with get_db() as conn:
            user = dict(conn.execute("SELECT * FROM users WHERE id=?", (uid(),)).fetchone())
        merged   = {**user, **{k:v for k,v in data.items() if v is not None and v != ""}}
        calories = calculate_calories(merged)
        plan     = generate_diet(merged, calories)
        with get_db() as conn:
            conn.execute(
                "INSERT INTO diet_plans(user_id,plan_data,goal,calories) VALUES (?,?,?,?)",
                (uid(), json.dumps(plan), merged.get("goal"), calories)
            )
        return jsonify({"calories":calories,"diet":plan,"macros":plan.get("macros",{})})
    except Exception as e:
        print(f"[Diet] {e}")
        return jsonify({"error":str(e)}), 500


@app.route("/upload_bca", methods=["POST"])
@login_required
def upload_bca():
    if "file" not in request.files:
        return jsonify({"error":"No file"}), 400
    f = request.files["file"]
    fname = f"{uid()}_bca_{int(time.time())}_{f.filename}"
    f.save(os.path.join(UPLOAD_DIR, fname))
    return jsonify({"status":"uploaded","file":fname})


# ═══════════════════════════════════════════════════════════════════════════
# CYCLE
# ═══════════════════════════════════════════════════════════════════════════

@app.route("/cycle", methods=["POST"])
@login_required
def cycle():
    try:
        data = request.get_json(force=True) or {}
        with get_db() as conn:
            user = dict(conn.execute("SELECT * FROM users WHERE id=?", (uid(),)).fetchone())
        merged = {**user, **{k:v for k,v in data.items() if v is not None and v != ""}}
        result = generate_cycle(merged)
        with get_db() as conn:
            conn.execute(
                "INSERT INTO cycle_logs(user_id,cycle_name,cycle_data) VALUES (?,?,?)",
                (uid(), result.get("cycle_name","Custom cycle"), json.dumps(result))
            )
        return jsonify(result)
    except Exception as e:
        print(f"[Cycle] {e}")
        return jsonify({"error":str(e)}), 500


@app.route("/upload_medical", methods=["POST"])
@login_required
def upload_medical():
    if "file" not in request.files:
        return jsonify({"error":"No file"}), 400
    f = request.files["file"]
    fname = f"{uid()}_medical_{int(time.time())}_{f.filename}"
    f.save(os.path.join(UPLOAD_DIR, fname))
    return jsonify({"status":"uploaded","file":fname})


# ═══════════════════════════════════════════════════════════════════════════
# MEDICAL
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
        print(f"[Medical] {e}")
        return jsonify({"error":str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════
# UPLOADS
# ═══════════════════════════════════════════════════════════════════════════

@app.route("/upload_physique", methods=["POST"])
@login_required
def upload_physique():
    files    = request.files.getlist("files")
    uploaded = []
    for f in files:
        if not f.filename: continue
        fname = f"{uid()}_physique_{int(time.time())}_{f.filename}"
        f.save(os.path.join(UPLOAD_DIR, fname))
        uploaded.append(fname)
    return jsonify({"uploaded":uploaded,"count":len(uploaded)})


# ═══════════════════════════════════════════════════════════════════════════
# CACHE & HEALTH
# ═══════════════════════════════════════════════════════════════════════════

@app.route("/cache/stats", methods=["GET"])
def cache_stats():
    try:
        from backend.search_ai import _cache_stats
        return jsonify(_cache_stats())
    except Exception:
        return jsonify({"total":0,"fresh":0})


@app.route("/cache/clear", methods=["DELETE"])
@login_required
def cache_clear():
    try:
        from backend.search_ai import CACHE_DB
        with sqlite3.connect(CACHE_DB) as conn:
            conn.execute("DELETE FROM report_cache")
        return jsonify({"status":"cleared"})
    except Exception as e:
        return jsonify({"error":str(e)}), 500


@app.route("/health")
def health():
    return jsonify({
        "status":  "ok",
        "version": "6.0",
        "ai":      bool(os.environ.get("ANTHROPIC_API_KEY")),
        "pubmed":  bool(os.environ.get("PUBMED_API_KEY")),
    })


# ─── Error handlers ───────────────────────────────────────────────────────
@app.errorhandler(404)
def not_found(e):
    if request.path.startswith(("/search","/history","/diet","/cycle","/medical","/me","/profile","/register","/login","/saved","/cache")):
        return jsonify({"error":"Not found"}), 404
    try:
        return send_from_directory(FRONTEND_DIR, "index.html")
    except Exception:
        return "Not found", 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error":"Internal server error"}), 500


if __name__ == "__main__":
    port  = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG","0") == "1"
    print(f"[FitSearch AI v6] Port={port} | AI={'✓' if os.environ.get('ANTHROPIC_API_KEY') else '✗'}")
    app.run(host="0.0.0.0", port=port, debug=debug)
