from flask import Flask, request, jsonify
from flask_cors import CORS

from backend.search_ai import search_knowledge

app = Flask(__name__)
CORS(app)


# Health Check
@app.route("/")
def home():
    return jsonify({
        "status": "FitSearch AI Running",
        "version": "WorldClass v4"
    })


# Main Search API
@app.route("/search", methods=["GET", "POST"])
def search():

    query = ""

    if request.method == "GET":
        query = request.args.get("q", "")

    elif request.method == "POST":
        data = request.get_json()
        query = data.get("query", "")

    if not query:
        return jsonify({
            "error": "No query provided",
            "results": []
        })

    results = search_knowledge(query)

    return jsonify({
        "query": query,
        "results": results
    })


# Suggestions API
@app.route("/suggest", methods=["GET"])
def suggest():

    query = request.args.get("q", "")

    suggestions = [
        "best fat loss exercises",
        "best creatine",
        "ostarine cycle",
        "muscle gain workout"
    ]

    return jsonify({
        "suggestions": suggestions
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
