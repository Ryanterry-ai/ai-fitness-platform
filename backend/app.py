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
import anthropic
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

# ── Claude AI ─────────────────────────────────────────────────────────────

claude_client = None

try:
    if os.getenv("ANTHROPIC_API_KEY"):
        claude_client = anthropic.Anthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
        print("Claude AI initialized")
    else:
        print("Claude disabled — no API key")

except Exception as e:
    print("Claude init error:", e)


def ask_claude(prompt):
    if not claude_client:
        return None

    try:
        response = claude_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1200,
            temperature=0.2,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        return response.content[0].text

    except Exception as e:
        print("Claude error:", e)
        return None

# ── Database ───────────────────────────────────────────────────────────────

def init_db():

    conn = sqlite3.connect(DB_PATH)

    conn.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        password_hash TEXT,
        experience_level TEXT,
        goal TEXT,
        weight REAL,
        height REAL,
        age INTEGER,
        sex TEXT,
        activity_level TEXT,
        tier TEXT DEFAULT 'free',
        created_at TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS search_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        query TEXT,
        results_count INTEGER,
        searched_at TEXT DEFAULT (datetime('now'))
    );
    """)

    conn.commit()
    conn.close()

init_db()


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ── Auth Helpers ──────────────────────────────────────────────────────────

def hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "Login required"}), 401
        return f(*args, **kwargs)

    return decorated


def uid():
    return session.get("user_id")


# ──────────────────────────────────────────────────────────────────────────
# FRONTEND
# ──────────────────────────────────────────────────────────────────────────

@app.route("/")
def home():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/<path:path>")
def catch_all(path):
    fp = os.path.join(FRONTEND_DIR, path)

    if os.path.isfile(fp):
        return send_from_directory(FRONTEND_DIR, path)

    return send_from_directory(FRONTEND_DIR, "index.html")


# ──────────────────────────────────────────────────────────────────────────
# AUTH
# ──────────────────────────────────────────────────────────────────────────

@app.route("/register", methods=["POST"])
def register():

    data = request.json

    with get_db() as conn:
        conn.execute(
            "INSERT INTO users(name,email,password_hash) VALUES (?,?,?)",
            (
                data["name"],
                data["email"],
                hash_password(data["password"])
            )
        )

    return jsonify({"status": "registered"})


@app.route("/login", methods=["POST"])
def login():

    data = request.json

    with get_db() as conn:
        user = conn.execute(
            "SELECT * FROM users WHERE email=? AND password_hash=?",
            (data["email"], hash_password(data["password"]))
        ).fetchone()

    if not user:
        return jsonify({"error": "Invalid credentials"}), 401

    session["user_id"] = user["id"]

    return jsonify({"status": "success"})


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"status": "ok"})


# ──────────────────────────────────────────────────────────────────────────
# SEARCH (Claude Enabled)
# ──────────────────────────────────────────────────────────────────────────

@app.route("/search", methods=["POST"])
@login_required
def search():

    try:

        data = request.json
        query = data.get("query", "")
        filters = data.get("filters", [])

        results = search_knowledge(query, filters)

        # Claude ranking
        if results:

            prompt = f"""
User Search Query:
{query}

Results:
{results}

Return only best relevant results ranked.
Return JSON list only.
"""

            ai = ask_claude(prompt)

            if ai:
                try:
                    import json
                    parsed = json.loads(ai)

                    if isinstance(parsed, list):
                        results = parsed

                except:
                    pass

        with get_db() as conn:
            conn.execute(
                "INSERT INTO search_history(user_id,query,results_count) VALUES (?,?,?)",
                (uid(), query, len(results))
            )

        return jsonify({
            "query": query,
            "results": results,
            "count": len(results)
        })

    except Exception as e:

        print("Search error:", e)

        return jsonify({
            "query": query,
            "results": [],
            "count": 0
        })


# ──────────────────────────────────────────────────────────────────────────
# DIET
# ──────────────────────────────────────────────────────────────────────────

@app.route("/diet", methods=["POST"])
@login_required
def diet():

    data = request.json

    calories = calculate_calories(data)
    plan = generate_diet(data, calories)

    return jsonify({
        "calories": calories,
        "diet": plan
    })


# ──────────────────────────────────────────────────────────────────────────
# CYCLE
# ──────────────────────────────────────────────────────────────────────────

@app.route("/cycle", methods=["POST"])
@login_required
def cycle():

    data = request.json

    result = generate_cycle(data)

    return jsonify(result)


# ──────────────────────────────────────────────────────────────────────────
# MEDICAL
# ──────────────────────────────────────────────────────────────────────────

@app.route("/medical", methods=["POST"])
@login_required
def medical():

    data = request.json

    result = analyze_medical(data)

    return jsonify(result)


# ──────────────────────────────────────────────────────────────────────────
# HEALTH
# ──────────────────────────────────────────────────────────────────────────

@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "version": "5.0",
        "ai": "claude-enabled"
    })


# ──────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
