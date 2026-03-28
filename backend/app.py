from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os

from backend.search_ai import search_knowledge, get_recommendations

app = Flask(__name__)
CORS(app)


# Serve frontend
@app.route("/")
def home():
    return send_from_directory("../frontend", "index.html")


# Search API
@app.route("/search", methods=["POST"])
def search():

    data = request.json
    query = data.get("query", "")

    results = search_knowledge(query)
    recommendations = get_recommendations([query])

    return jsonify({
        "results": results,
        "recommendations": recommendations
    })


# Save (basic version)
saved = []

@app.route("/save", methods=["POST"])
def save():

    data = request.json
    saved.append({
        "item_name": data.get("name")
    })

    return jsonify({"status": "saved"})


@app.route("/saved")
def get_saved():
    return jsonify(saved)


@app.route("/tier")
def tier():
    return jsonify({"tier": "free"})


@app.route("/upgrade", methods=["POST"])
def upgrade():
    return jsonify({"status": "upgraded"})


if __name__ == "__main__":
    app.run(debug=True)
