from flask import Flask, request, jsonify, session
from flask_cors import CORS
import sqlite3
import os

# Fixed imports for Render deployment
from backend.diet_ai import generate_diet
from backend.calorie_ai import calculate_calories
from backend.grocery_ai import grocery_list
from backend.cycle_ai import generate_cycle
from backend.medical_ai import analyze_medical

app = Flask(__name__)
app.secret_key = "secret"
CORS(app)

# Base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
DATABASE_PATH = os.path.join(BASE_DIR, "database", "users.db")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "database"), exist_ok=True)


@app.route("/")
def home():
    return "AI Fitness Platform v3 Running"


# -------------------------------
# User Register
# -------------------------------
@app.route("/register", methods=["POST"])
def register():
    data = request.json
    conn = sqlite3.connect(DATABASE_PATH)
    cur = conn.cursor()

    cur.execute(
        "CREATE TABLE IF NOT EXISTS users (email TEXT, password TEXT)"
    )

    cur.execute(
        "INSERT INTO users(email,password) VALUES (?,?)",
        (data["email"], data["password"])
    )

    conn.commit()
    conn.close()

    return jsonify({"status": "registered"})


# -------------------------------
# Login
# -------------------------------
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    conn = sqlite3.connect(DATABASE_PATH)
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM users WHERE email=? AND password=?",
        (data["email"], data["password"])
    )

    user = cur.fetchone()
    conn.close()

    if user:
        session["user"] = data["email"]
        return jsonify({"status": "success"})

    return jsonify({"status": "failed"})


# -------------------------------
# Upload BCA
# -------------------------------
@app.route("/upload_bca", methods=["POST"])
def upload_bca():
    file = request.files["file"]

    path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(path)

    return jsonify({"status": "uploaded", "file": file.filename})


# -------------------------------
# Upload Physique Photos
# -------------------------------
@app.route("/upload_physique", methods=["POST"])
def upload_physique():
    files = request.files.getlist("files")

    uploaded = []

    for f in files:
        path = os.path.join(UPLOAD_FOLDER, f.filename)
        f.save(path)
        uploaded.append(f.filename)

    return jsonify({"uploaded": uploaded})


# -------------------------------
# Medical AI
# -------------------------------
@app.route("/medical", methods=["POST"])
def medical():
    data = request.json
    result = analyze_medical(data)

    return jsonify(result)


# -------------------------------
# Cycle Planner
# -------------------------------
@app.route("/cycle", methods=["POST"])
def cycle():
    data = request.json
    result = generate_cycle(data)

    return jsonify(result)


# -------------------------------
# Diet Generator
# -------------------------------
@app.route("/diet", methods=["POST"])
def diet():
    data = request.json

    calories = calculate_calories(data)
    diet = generate_diet(data, calories)

    return jsonify({
        "calories": calories,
        "diet": diet
    })


# -------------------------------
# Grocery Generator
# -------------------------------
@app.route("/grocery", methods=["POST"])
def grocery():
    data = request.json
    return jsonify(grocery_list(data))


# -------------------------------
# Render Deployment
# -------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
