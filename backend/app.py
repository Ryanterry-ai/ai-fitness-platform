"""
app.py — FitSearch AI Platform v6
==================================
Production-grade Flask backend (Public version)
- No login / register required
- Real-time RAG search (Bing + Google + OpenAI)
- Serves modern index.html frontend
- Proper error handling, caching, and logging
"""

from __future__ import annotations
import os, json, hashlib, time, sqlite3, sys
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# ====================== PATHS ======================
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(CURRENT_DIR)
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
DB_DIR = os.path.join(BASE_DIR, "database")
DB_PATH = os.path.join(DB_DIR, "search_history.db")
os.makedirs(DB_DIR, exist_ok=True)

sys.path.insert(0, BASE_DIR)

# ====================== LAZY IMPORT SEARCH_AI ======================
def _safe_import():
    try:
        from backend.search_ai import search_knowledge
        return search_knowledge
    except Exception as e:
        print(f"[Import Error] backend.search_ai: {e}")
        return None

search_knowledge = _safe_import()

# ====================== FLASK APP ======================
app = Flask(__name__, static_folder=None)
app.secret_key = os.environ.get("SECRET_KEY", "fitsearch-secret-2025")
CORS(app, supports_credentials=True, origins="*")

# ====================== DATABASE (Global Search History) ======================
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS search_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL,
                results_count INTEGER DEFAULT 0,
                searched_at TEXT DEFAULT (datetime('now'))
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_query_time ON search_history(searched_at);")
init_db()

# ====================== STATIC FRONTEND SERVING ======================
@app.route("/")
def home():
    return send_from_directory(FRONTEND_DIR, "index.html")

@app.route("/<path:path>")
def catch_all(path):
    """Serve frontend files or fallback to index.html (SPA)"""
    fp = os.path.join(FRONTEND_DIR, path)
    if os.path.isfile(fp):
        return send_from_directory(FRONTEND_DIR, path)
    return send_from_directory(FRONTEND_DIR, "index.html")

# ====================== PUBLIC SEARCH ENDPOINT ======================
@app.route("/search", methods=["POST"])
def search():
    try:
        data = request.get_json(force=True) or {}
        query = (data.get("query") or "").strip()[:500]

        if not query:
            return jsonify({"query": "", "results": [], "count": 0})

        if not search_knowledge:
            return jsonify({"query": query, "results": [], "count": 0, "error": "Search module unavailable"}), 500

        results = search_knowledge(query)

        # Log search (public history)
        try:
            with sqlite3.connect(DB_PATH) as conn:
                conn.execute(
                    "INSERT INTO search_history (query, results_count) VALUES (?, ?)",
                    (query, len(results))
                )
        except Exception:
            pass

        return jsonify({
            "query": query,
            "results": results,
            "count": len(results)
        })

    except Exception as e:
        print(f"[Search Error] {e}")
        return jsonify({
            "query": "",
            "results": [],
            "count": 0,
            "error": "Search temporarily unavailable"
        }), 500

# ====================== SUGGESTIONS ======================
@app.route("/search/suggestions", methods=["GET"])
def search_suggestions():
    prefix = (request.args.get("q") or "").lower().strip()
    if len(prefix) < 2:
        return jsonify([])
    suggestions = [
        "How to lose belly fat", "Creatine monohydrate benefits",
        "Best SARMs for beginners", "Testosterone cycle guide",
        "BPC-157 dosage and benefits", "High protein Indian diet plan",
        "RAD140 vs LGD4033", "Post cycle therapy protocol",
        "HIIT workout for fat loss", "MK677 ibutamoren guide",
    ]
    return jsonify([s for s in suggestions if prefix in s.lower()][:8])

# ====================== HEALTH CHECK ======================
@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "version": "6.0",
        "search_engine": "RAG (Bing + Google + OpenAI)",
        "public": True,
        "ai_enabled": bool(os.environ.get("OPENAI_API_KEY"))
    })

# ====================== ERROR HANDLERS ======================
@app.errorhandler(404)
def not_found(e):
    if request.path.startswith(("/search", "/health")):
        return jsonify({"error": "Not found"}), 404
    return send_from_directory(FRONTEND_DIR, "index.html")

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error"}), 500

# ====================== START ======================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    print(f"[FitSearch AI v6] Public Mode | Port={port} | Ready")
    app.run(host="0.0.0.0", port=port, debug=debug)
