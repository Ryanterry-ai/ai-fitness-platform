
from flask import Flask, request, jsonify, session
from flask_cors import CORS
import sqlite3
import os

from diet_ai import generate_diet
from calorie_ai import calculate_calories
from grocery_ai import grocery_list
from cycle_ai import generate_cycle
from medical_ai import analyze_medical

app = Flask(__name__)
app.secret_key="secret"
CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return "AI Fitness Platform v3 Running"

@app.route("/register",methods=["POST"])
def register():
    data=request.json
    conn=sqlite3.connect("database/users.db")
    cur=conn.cursor()
    cur.execute("INSERT INTO users(email,password) VALUES (?,?)",(data["email"],data["password"]))
    conn.commit()
    conn.close()
    return jsonify({"status":"registered"})

@app.route("/login",methods=["POST"])
def login():
    data=request.json
    conn=sqlite3.connect("database/users.db")
    cur=conn.cursor()
    cur.execute("SELECT * FROM users WHERE email=? AND password=?",(data["email"],data["password"]))
    user=cur.fetchone()
    conn.close()
    if user:
        session["user"]=data["email"]
        return jsonify({"status":"success"})
    return jsonify({"status":"failed"})

@app.route("/upload_bca",methods=["POST"])
def upload_bca():
    file=request.files["file"]
    path=os.path.join(UPLOAD_FOLDER,file.filename)
    file.save(path)
    return jsonify({"status":"uploaded","file":file.filename})

@app.route("/upload_physique",methods=["POST"])
def upload_physique():
    files=request.files.getlist("files")
    uploaded=[]
    for f in files:
        path=os.path.join(UPLOAD_FOLDER,f.filename)
        f.save(path)
        uploaded.append(f.filename)
    return jsonify({"uploaded":uploaded})

@app.route("/medical",methods=["POST"])
def medical():
    data=request.json
    result=analyze_medical(data)
    return jsonify(result)

@app.route("/cycle",methods=["POST"])
def cycle():
    data=request.json
    result=generate_cycle(data)
    return jsonify(result)

@app.route("/diet",methods=["POST"])
def diet():
    data=request.json
    calories=calculate_calories(data)
    diet=generate_diet(data,calories)
    return jsonify({"calories":calories,"diet":diet})

@app.route("/grocery",methods=["POST"])
def grocery():
    data=request.json
    return jsonify(grocery_list(data))
