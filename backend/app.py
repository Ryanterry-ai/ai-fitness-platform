from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

from search_ai import search, get_trending

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return send_from_directory(".", "index.html")


@app.route("/search", methods=["POST"])
def search_api():

    query = request.json.get("query")

    return jsonify({
        "success": True,
        "data": search(query, deep=False)
    })


@app.route("/deep-search", methods=["POST"])
def deep():

    query = request.json.get("query")

    return jsonify({
        "success": True,
        "data": search(query, deep=True)
    })


@app.route("/trending")
def trending():

    return jsonify({
        "trending": get_trending()
    })


if __name__ == "__main__":
    app.run(debug=True)
