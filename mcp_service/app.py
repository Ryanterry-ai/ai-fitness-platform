"""MCP Service - Flask Application."""

import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ZENSERP_API_KEY = os.getenv("ZENSERP_API_KEY", "")

from trusted_domains import TRUSTED_DOMAINS
from web_search import web_search
from deep_research import deep_research
from intent_detection import detect_intent
from source_verification import verify_source

app = Flask(__name__, static_folder=os.path.join(BASE_DIR, "static"))
app.secret_key = os.environ.get("SECRET_KEY", "fitsearch-mcp-2026")
CORS(app, supports_credentials=True, origins="*")

@app.route("/mcp/web_search", methods=["GET", "POST"])
def mcp_search():
    if request.method == "POST":
        data = request.get_json() or {}
        query = data.get("query", "")
        max_results = data.get("max_results", 10)
    else:
        query = request.args.get("query", "")
        max_results = int(request.args.get("max_results", 10))
    if not query:
        return jsonify({"error": "Query required"}), 400
    return jsonify({"tool": "web_search", "query": query, "results": web_search(query, max_results), "intent": detect_intent(query)})

@app.route("/mcp/deep_research", methods=["GET", "POST"])
def mcp_deep():
    if request.method == "POST":
        data = request.get_json() or {}
        query = data.get("query", "")
    else:
        query = request.args.get("query", "")
    if not query:
        return jsonify({"error": "Query required"}), 400
    return jsonify({"tool": "deep_research", "query": query, "research": deep_research(query)})

@app.route("/mcp/intent", methods=["GET", "POST"])
def mcp_intent():
    if request.method == "POST":
        data = request.get_json() or {}
        query = data.get("query", "")
    else:
        query = request.args.get("query", "")
    if not query:
        return jsonify({"error": "Query required"}), 400
    return jsonify({"tool": "intent_detection", "query": query, "intent": detect_intent(query)})

@app.route("/mcp/verify", methods=["GET", "POST"])
def mcp_verify():
    if request.method == "POST":
        data = request.get_json() or {}
        url = data.get("url", "")
    else:
        url = request.args.get("url", "")
    if not url:
        return jsonify({"error": "URL required"}), 400
    return jsonify({"tool": "verify_source", "url": url, "verification": verify_source(url)})

@app.route("/mcp/trusted-domains", methods=["GET"])
def mcp_trusted():
    return jsonify({"trusted_domains": TRUSTED_DOMAINS, "total": len(TRUSTED_DOMAINS)})

@app.route("/search", methods=["GET", "POST"])
def api_search():
    if request.method == "POST":
        data = request.get_json() or {}
        query = data.get("query", "")
    else:
        query = request.args.get("query", "")
    if not query:
        return jsonify({"error": "Query required"}), 400
    intent = detect_intent(query)
    results = web_search(query, 15)
    return jsonify({"query": query, "intent": intent, "results": results.get("results", []), "verified_results": results.get("verified_results", []), "stats": {"total": results.get("total_results", 0), "verified": results.get("verified_count", 0)}})

@app.route("/health", methods=["GET"])
def api_health():
    return jsonify({"status": "ok", "version": "MCP v1.0", "services": {"zenserp": bool(ZENSERP_API_KEY)}, "trusted_domains": len(TRUSTED_DOMAINS)})

@app.route("/")
def home():
    return send_from_directory(os.path.join(BASE_DIR, "frontend"), "index.html")

@app.route("/<path:path>")
def static_files(path):
    frontend_path = os.path.join(BASE_DIR, "frontend", path)
    if os.path.isfile(frontend_path):
        return send_from_directory(os.path.join(BASE_DIR, "frontend"), path)
    return send_from_directory(os.path.join(BASE_DIR, "frontend"), "index.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"[FitSearch MCP Server] Running on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)
