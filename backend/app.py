from flask import Flask, request, jsonify, session
from flask_cors import CORS
import sqlite3, os, hashlib, json, time, sys
from functools import wraps
from datetime import datetime

# Fix module import path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.diet_ai import generate_diet
from backend.calorie_ai import calculate_calories
from backend.grocery_ai import grocery_list
from backend.cycle_ai import generate_cycle
from backend.medical_ai import analyze_medical
from backend.search_ai import search_knowledge, get_recommendations
from backend.supplement_ai import compare_supplements

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-me-in-production-please")
CORS(app, supports_credentials=True)

UPLOAD_FOLDER = "uploads"
DB_PATH = "database/users.db"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ── DB helpers ──────────────────────────────────────────────────────────────

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Ensure database folder exists
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)


# Ensure database folder exists
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)


def init_db():
    try:
        with get_db() as conn:
            conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                experience_level TEXT DEFAULT 'beginner',
                goal TEXT DEFAULT 'muscle_gain',
                weight REAL,
                height REAL,
                age INTEGER,
                tier TEXT DEFAULT 'free',
                created_at TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS search_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                query TEXT NOT NULL,
                filters TEXT,
                results_count INTEGER,
                searched_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY(user_id) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS saved_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                item_type TEXT NOT NULL,
                item_name TEXT NOT NULL,
                item_data TEXT,
                saved_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY(user_id) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS diet_plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                plan_data TEXT NOT NULL,
                goal TEXT,
                calories INTEGER,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY(user_id) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS cycle_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                cycle_name TEXT,
                cycle_data TEXT NOT NULL,
                week_number INTEGER DEFAULT 1,
                notes TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY(user_id) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS comparisons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                compounds TEXT NOT NULL,
                result_data TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY(user_id) REFERENCES users(id)
            );
            """)

    except sqlite3.DatabaseError:
        print("Database corrupted. Recreating...")

        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)

        with get_db() as conn:
            conn.executescript("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                experience_level TEXT DEFAULT 'beginner',
                goal TEXT DEFAULT 'muscle_gain',
                weight REAL,
                height REAL,
                age INTEGER,
                tier TEXT DEFAULT 'free',
                created_at TEXT DEFAULT (datetime('now'))
            );
            """)


init_db()


# ── Auth helpers ─────────────────────────────────────────────────────────────

def hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "Authentication required"}), 401
        return f(*args, **kwargs)
    return decorated

def current_user_id():
    return session.get("user_id")

# ── Auth routes ──────────────────────────────────────────────────────────────

@app.route("/")
def home():
    return jsonify({"status": "FitSearch AI Platform v4 Running", "version": "4.0"})

@app.route("/register", methods=["POST"])
def register():
    data = request.json or {}
    required = ["name", "email", "password"]
    if not all(k in data for k in required):
        return jsonify({"error": "Name, email and password are required"}), 400
    if len(data["password"]) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400
    try:
        with get_db() as conn:
            conn.execute(
                "INSERT INTO users(name,email,password_hash,experience_level,goal,weight,height,age) VALUES (?,?,?,?,?,?,?,?)",
                (
                    data["name"], data["email"], hash_password(data["password"]),
                    data.get("experience_level", "beginner"),
                    data.get("goal", "muscle_gain"),
                    data.get("weight"), data.get("height"), data.get("age")
                )
            )
        return jsonify({"status": "registered", "message": "Account created successfully"})
    except sqlite3.IntegrityError:
        return jsonify({"error": "Email already registered"}), 409

@app.route("/login", methods=["POST"])
def login():
    data = request.json or {}
    if not data.get("email") or not data.get("password"):
        return jsonify({"error": "Email and password required"}), 400
    with get_db() as conn:
        user = conn.execute(
            "SELECT * FROM users WHERE email=? AND password_hash=?",
            (data["email"], hash_password(data["password"]))
        ).fetchone()
    if user:
        session["user_id"] = user["id"]
        session["user_email"] = user["email"]
        return jsonify({
            "status": "success",
            "user": {
                "id": user["id"], "name": user["name"], "email": user["email"],
                "experience_level": user["experience_level"], "goal": user["goal"],
                "tier": user["tier"], "weight": user["weight"],
                "height": user["height"], "age": user["age"]
            }
        })
    return jsonify({"error": "Invalid email or password"}), 401

@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"status": "logged out"})

@app.route("/me", methods=["GET"])
@login_required
def me():
    with get_db() as conn:
        user = conn.execute("SELECT * FROM users WHERE id=?", (current_user_id(),)).fetchone()
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({
        "id": user["id"], "name": user["name"], "email": user["email"],
        "experience_level": user["experience_level"], "goal": user["goal"],
        "tier": user["tier"], "weight": user["weight"],
        "height": user["height"], "age": user["age"],
        "created_at": user["created_at"]
    })

@app.route("/profile", methods=["PUT"])
@login_required
def update_profile():
    data = request.json or {}
    allowed = ["name", "experience_level", "goal", "weight", "height", "age"]
    updates = {k: v for k, v in data.items() if k in allowed}
    if not updates:
        return jsonify({"error": "No valid fields to update"}), 400
    set_clause = ", ".join(f"{k}=?" for k in updates)
    with get_db() as conn:
        conn.execute(
            f"UPDATE users SET {set_clause} WHERE id=?",
            (*updates.values(), current_user_id())
        )
    return jsonify({"status": "updated"})

# ── Search & history ──────────────────────────────────────────────────────────

@app.route("/search", methods=["POST"])
@login_required
def search():
    data = request.json or {}
    query = data.get("query", "").strip()
    filters = data.get("filters", [])
    if not query:
        return jsonify({"error": "Query is required"}), 400

    results = search_knowledge(query, filters)

    with get_db() as conn:
        conn.execute(
            "INSERT INTO search_history(user_id,query,filters,results_count) VALUES (?,?,?,?)",
            (current_user_id(), query, json.dumps(filters), len(results))
        )
    return jsonify({"query": query, "results": results, "count": len(results)})

@app.route("/history", methods=["GET"])
@login_required
def history():
    limit = min(int(request.args.get("limit", 50)), 100)
    with get_db() as conn:
        rows = conn.execute(
            "SELECT id,query,filters,results_count,searched_at FROM search_history WHERE user_id=? ORDER BY searched_at DESC LIMIT ?",
            (current_user_id(), limit)
        ).fetchall()
    return jsonify([dict(r) for r in rows])

@app.route("/history/<int:hid>", methods=["DELETE"])
@login_required
def delete_history_item(hid):
    with get_db() as conn:
        conn.execute("DELETE FROM search_history WHERE id=? AND user_id=?", (hid, current_user_id()))
    return jsonify({"status": "deleted"})

@app.route("/history/clear", methods=["DELETE"])
@login_required
def clear_history():
    with get_db() as conn:
        conn.execute("DELETE FROM search_history WHERE user_id=?", (current_user_id(),))
    return jsonify({"status": "cleared"})

# ── Recommendations ───────────────────────────────────────────────────────────

@app.route("/recommendations", methods=["GET"])
@login_required
def recommendations():
    with get_db() as conn:
        user = conn.execute("SELECT * FROM users WHERE id=?", (current_user_id(),)).fetchone()
        recent_queries = conn.execute(
            "SELECT query FROM search_history WHERE user_id=? ORDER BY searched_at DESC LIMIT 20",
            (current_user_id(),)
        ).fetchall()
    queries = [r["query"] for r in recent_queries]
    recs = get_recommendations(queries, dict(user))
    return jsonify(recs)

# ── Saved items ───────────────────────────────────────────────────────────────

@app.route("/saved", methods=["GET"])
@login_required
def get_saved():
    item_type = request.args.get("type")
    query = "SELECT * FROM saved_items WHERE user_id=?"
    params = [current_user_id()]
    if item_type:
        query += " AND item_type=?"
        params.append(item_type)
    query += " ORDER BY saved_at DESC"
    with get_db() as conn:
        rows = conn.execute(query, params).fetchall()
    return jsonify([dict(r) for r in rows])

@app.route("/saved", methods=["POST"])
@login_required
def save_item():
    data = request.json or {}
    with get_db() as conn:
        conn.execute(
            "INSERT INTO saved_items(user_id,item_type,item_name,item_data) VALUES (?,?,?,?)",
            (current_user_id(), data.get("type"), data.get("name"), json.dumps(data.get("data", {})))
        )
    return jsonify({"status": "saved"})

@app.route("/saved/<int:sid>", methods=["DELETE"])
@login_required
def delete_saved(sid):
    with get_db() as conn:
        conn.execute("DELETE FROM saved_items WHERE id=? AND user_id=?", (sid, current_user_id()))
    return jsonify({"status": "deleted"})

# ── Supplement comparison ─────────────────────────────────────────────────────

@app.route("/compare", methods=["POST"])
@login_required
def compare():
    data = request.json or {}
    compounds = data.get("compounds", [])
    if len(compounds) < 2:
        return jsonify({"error": "At least 2 compounds required"}), 400
    if len(compounds) > 4:
        return jsonify({"error": "Maximum 4 compounds for comparison"}), 400
    with get_db() as conn:
        user = conn.execute("SELECT * FROM users WHERE id=?", (current_user_id(),)).fetchone()
    result = compare_supplements(compounds, dict(user))
    with get_db() as conn:
        conn.execute(
            "INSERT INTO comparisons(user_id,compounds,result_data) VALUES (?,?,?)",
            (current_user_id(), json.dumps(compounds), json.dumps(result))
        )
    return jsonify(result)

@app.route("/compare/history", methods=["GET"])
@login_required
def compare_history():
    with get_db() as conn:
        rows = conn.execute(
            "SELECT id,compounds,created_at FROM comparisons WHERE user_id=? ORDER BY created_at DESC LIMIT 10",
            (current_user_id(),)
        ).fetchall()
    return jsonify([dict(r) for r in rows])

# ── Diet generator ────────────────────────────────────────────────────────────

@app.route("/diet", methods=["POST"])
@login_required
def diet():
    data = request.json or {}
    with get_db() as conn:
        user = conn.execute("SELECT * FROM users WHERE id=?", (current_user_id(),)).fetchone()
    merged = {**dict(user), **data}
    calories = calculate_calories(merged)
    plan = generate_diet(merged, calories)
    with get_db() as conn:
        conn.execute(
            "INSERT INTO diet_plans(user_id,plan_data,goal,calories) VALUES (?,?,?,?)",
            (current_user_id(), json.dumps(plan), merged.get("goal"), calories)
        )
    return jsonify({"calories": calories, "diet": plan, "macros": plan.get("macros", {})})

@app.route("/diet/history", methods=["GET"])
@login_required
def diet_history():
    with get_db() as conn:
        rows = conn.execute(
            "SELECT id,goal,calories,created_at FROM diet_plans WHERE user_id=? ORDER BY created_at DESC LIMIT 10",
            (current_user_id(),)
        ).fetchall()
    return jsonify([dict(r) for r in rows])

# ── Cycle planner ─────────────────────────────────────────────────────────────

@app.route("/cycle", methods=["POST"])
@login_required
def cycle():
    data = request.json or {}
    with get_db() as conn:
        user = conn.execute("SELECT * FROM users WHERE id=?", (current_user_id(),)).fetchone()
    merged = {**dict(user), **data}
    result = generate_cycle(merged)
    with get_db() as conn:
        conn.execute(
            "INSERT INTO cycle_logs(user_id,cycle_name,cycle_data) VALUES (?,?,?)",
            (current_user_id(), result.get("cycle_name", "Custom cycle"), json.dumps(result))
        )
    return jsonify(result)

@app.route("/cycle/history", methods=["GET"])
@login_required
def cycle_history():
    with get_db() as conn:
        rows = conn.execute(
            "SELECT id,cycle_name,week_number,created_at FROM cycle_logs WHERE user_id=? ORDER BY created_at DESC LIMIT 10",
            (current_user_id(),)
        ).fetchall()
    return jsonify([dict(r) for r in rows])

# ── Uploads ───────────────────────────────────────────────────────────────────

@app.route("/upload_bca", methods=["POST"])
@login_required
def upload_bca():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    f = request.files["file"]
    fname = f"{current_user_id()}_bca_{int(time.time())}_{f.filename}"
    f.save(os.path.join(UPLOAD_FOLDER, fname))
    return jsonify({"status": "uploaded", "file": fname})

@app.route("/upload_physique", methods=["POST"])
@login_required
def upload_physique():
    files = request.files.getlist("files")
    uploaded = []
    for f in files:
        fname = f"{current_user_id()}_physique_{int(time.time())}_{f.filename}"
        f.save(os.path.join(UPLOAD_FOLDER, fname))
        uploaded.append(fname)
    return jsonify({"uploaded": uploaded, "count": len(uploaded)})

# ── Medical analysis ──────────────────────────────────────────────────────────

@app.route("/medical", methods=["POST"])
@login_required
def medical():
    data = request.json or {}
    with get_db() as conn:
        user = conn.execute("SELECT * FROM users WHERE id=?", (current_user_id(),)).fetchone()
    result = analyze_medical({**dict(user), **data})
    return jsonify(result)

# ── Grocery list ──────────────────────────────────────────────────────────────

@app.route("/grocery", methods=["POST"])
@login_required
def grocery():
    data = request.json or {}
    return jsonify(grocery_list(data))

if __name__ == "__main__":
    app.run(debug=True, port=5000)
