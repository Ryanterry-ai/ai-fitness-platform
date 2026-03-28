from flask import Flask, request, jsonify, session, send_from_directory
from flask_cors import CORS
import sqlite3, os, hashlib, json, time, sys
from functools import wraps
from datetime import datetime

# ── Project Directories ───────────────────────────────────────────────
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))       # backend/ directory
BASE_DIR = os.path.dirname(CURRENT_DIR)                         # project root
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
DB_PATH = os.path.join(BASE_DIR, "database", "users.db")

# Ensure necessary directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# ── Fix module import path ────────────────────────────────────────────
sys.path.append(CURRENT_DIR)

# ── Backend module imports ───────────────────────────────────────────
from backend.diet_ai import generate_diet
from backend.calorie_ai import calculate_calories
from backend.grocery_ai import grocery_list
from backend.cycle_ai import generate_cycle
from backend.medical_ai import analyze_medical
from backend.search_ai import search_knowledge, get_recommendations
from backend.supplement_ai import compare_supplements

# ── Flask App Setup ───────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-me-in-production-please")
CORS(app, supports_credentials=True)

# ── Database Helpers ──────────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

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

# ── Auth Helpers ───────────────────────────────────────────────────────
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

# ── Frontend Routes ────────────────────────────────────────────────────
@app.route("/")
def home():
    return send_from_directory(FRONTEND_DIR, "index.html")

@app.route("/<path:path>")
def serve_static(path):
    return send_from_directory(FRONTEND_DIR, path)

# ── Auth Routes ────────────────────────────────────────────────────────
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
    return jsonify(dict(user))

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
        conn.execute(f"UPDATE users SET {set_clause} WHERE id=?", (*updates.values(), current_user_id()))
    return jsonify({"status": "updated"})

# ── Search, Recommendations, Saved Items, Diet, Cycle, Compare, Uploads, Medical Routes ───────────────────────────────
# [KEEP THE REST OF YOUR ROUTES FROM ORIGINAL APP.PY AS IS, USING THE CORRECT PATHS]

if __name__ == "__main__":
    app.run(debug=True, port=5000)
