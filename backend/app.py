from flask import Flask, request, jsonify, session, send_from_directory
from flask_cors import CORS
import sqlite3, os, hashlib, sys
from functools import wraps

# ── Project Directories ───────────────────────────────────────────────
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(CURRENT_DIR)
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
DB_DIR = os.path.join(BASE_DIR, "database")
DB_PATH = os.path.join(DB_DIR, "users.db")

os.makedirs(DB_DIR, exist_ok=True)

sys.path.append(CURRENT_DIR)

# ── Backend Imports ───────────────────────────────────────────────────
from backend.search_ai import search_knowledge, get_recommendations

# ── Flask Setup ───────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "super-secret")
CORS(app, supports_credentials=True)


# ── Database ──────────────────────────────────────────────────────────

def init_db():

    # Delete corrupted DB file
    if os.path.exists(DB_PATH):
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.execute("PRAGMA schema_version;")
            conn.close()
        except:
            print("⚠️ Corrupt DB detected — deleting")
            os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)

    conn.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        password_hash TEXT,
        tier TEXT DEFAULT 'free',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS saved_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        item_name TEXT,
        item_type TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS search_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        query TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)

    conn.commit()
    conn.close()


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


init_db()


# ── Auth Helpers ──────────────────────────────────────────────────────

def hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "Login required"}), 401
        return f(*args, **kwargs)
    return decorated


def current_user_id():
    return session.get("user_id")


# ── Frontend ──────────────────────────────────────────────────────────

@app.route("/")
def home():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/<path:path>")
def static_files(path):
    return send_from_directory(FRONTEND_DIR, path)


# ── Register ──────────────────────────────────────────────────────────

@app.route("/register", methods=["POST"])
def register():

    try:

        data = request.json or {}

        if not data.get("email") or not data.get("password"):
            return jsonify({
                "error": "Email and password required"
            }), 400

        with get_db() as conn:
            conn.execute(
                "INSERT INTO users(name,email,password_hash) VALUES (?,?,?)",
                (
                    data.get("name", "User"),
                    data["email"],
                    hash_password(data["password"])
                )
            )

        return jsonify({"status": "registered"})

    except sqlite3.IntegrityError:

        return jsonify({
            "error": "Already Signed up please login with your email and password"
        }), 409

    except Exception as e:

        print("Register Error:", e)
        return jsonify({"error": "Server error"}), 500


# ── Login ─────────────────────────────────────────────────────────────

@app.route("/login", methods=["POST"])
def login():

    try:

        data = request.json or {}

        if not data.get("email") or not data.get("password"):
            return jsonify({
                "error": "Email and password required"
            }), 400

        with get_db() as conn:

            user = conn.execute(
                "SELECT * FROM users WHERE email=? AND password_hash=?",
                (data["email"], hash_password(data["password"]))
            ).fetchone()

        if user:

            session["user_id"] = user["id"]

            return jsonify({
                "status": "success",
                "user": {
                    "id": user["id"],
                    "email": user["email"],
                    "tier": user["tier"]
                }
            })

        return jsonify({
            "error": "Invalid email or password"
        }), 401

    except Exception as e:

        print("Login Error:", e)
        return jsonify({"error": "Server error"}), 500


# ── Search ────────────────────────────────────────────────────────────

@app.route("/search", methods=["POST"])
def search():

    try:

        data = request.json or {}
        query = data.get("query", "")

        results = search_knowledge(query)
        recommendations = get_recommendations([query])

        return jsonify({
            "results": results,
            "recommendations": recommendations
        })

    except Exception as e:

        print("Search Error:", e)

        return jsonify({
            "results": [],
            "recommendations": []
        })


# ── Save ──────────────────────────────────────────────────────────────

@app.route("/save", methods=["POST"])
def save():

    data = request.json or {}

    if not current_user_id():
        return jsonify({"status": "saved"})

    with get_db() as conn:

        conn.execute(
            "INSERT INTO saved_items (user_id,item_name,item_type) VALUES (?,?,?)",
            (
                current_user_id(),
                data.get("name"),
                data.get("type", "search")
            )
        )

    return jsonify({"status": "saved"})


# ── Saved ─────────────────────────────────────────────────────────────

@app.route("/saved")
def saved():

    if not current_user_id():
        return jsonify([])

    with get_db() as conn:

        rows = conn.execute(
            "SELECT * FROM saved_items WHERE user_id=?",
            (current_user_id(),)
        ).fetchall()

    return jsonify([dict(r) for r in rows])


# ── Tier ──────────────────────────────────────────────────────────────

@app.route("/tier")
def tier():

    if not current_user_id():
        return jsonify({"tier": "free"})

    with get_db() as conn:

        user = conn.execute(
            "SELECT tier FROM users WHERE id=?",
            (current_user_id(),)
        ).fetchone()

    return jsonify({"tier": user["tier"]})


# ── Upgrade ───────────────────────────────────────────────────────────

@app.route("/upgrade", methods=["POST"])
@login_required
def upgrade():

    with get_db() as conn:

        conn.execute(
            "UPDATE users SET tier='premium' WHERE id=?",
            (current_user_id(),)
        )

    return jsonify({"status": "premium"})


# ── Run ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True, port=5000)
