"""
MCP Server for FitSearch AI
============================
Model Context Protocol server with live web search, deep research,
and fitness domain tools.

Tools:
- web_search: Search the web for fitness/health topics
- deep_research: Comprehensive research with verified sources
- intent_detection: Classify user query intent
- verify_source: Check if a source is from trusted domains
"""
import os
import json
import re
import time
import hashlib
import sqlite3
import threading
import concurrent.futures
from datetime import datetime, timezone
from typing import Any, Optional
from urllib.parse import urlparse, quote
import requests
from flask import Flask, request, jsonify, session, send_from_directory
from flask_cors import CORS

# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, "database")
DB_PATH = os.path.join(DB_DIR, "fitsearch.db")

os.makedirs(DB_DIR, exist_ok=True)

# API Keys
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
PUBMED_API_KEY = os.getenv("PUBMED_API_KEY", "")
ZENSERP_API_KEY = os.getenv("ZENSERP_API_KEY", "")

# Trusted domains for source verification
TRUSTED_DOMAINS = {
    # Scientific/Medical
    "pubmed.ncbi.nlm.nih.gov": {"name": "PubMed", "tier": "scientific", "trust": 5},
    "ncbi.nlm.nih.gov": {"name": "NCBI", "tier": "scientific", "trust": 5},
    "nih.gov": {"name": "NIH", "tier": "scientific", "trust": 5},
    "who.int": {"name": "WHO", "tier": "scientific", "trust": 5},
    "cdc.gov": {"name": "CDC", "tier": "scientific", "trust": 5},
    "mayoclinic.org": {"name": "Mayo Clinic", "tier": "medical", "trust": 5},
    "webmd.com": {"name": "WebMD", "tier": "medical", "trust": 4},
    "healthline.com": {"name": "Healthline", "tier": "health", "trust": 4},
    "medicalnewstoday.com": {"name": "Medical News Today", "tier": "health", "trust": 4},
    # Fitness Specific
    "examine.com": {"name": "Examine.com", "tier": "fitness", "trust": 5},
    " bodybuilding.com": {"name": "Bodybuilding.com", "tier": "fitness", "trust": 3},
    "muscleandstrength.com": {"name": "Muscle & Strength", "tier": "fitness", "trust": 3},
    "t-nation.com": {"name": "T Nation", "tier": "fitness", "trust": 3},
    "jeffnippard.com": {"name": "Jeff Nippard", "tier": "fitness", "trust": 4},
    "renaissannepolymath": {"name": "Renaissance Periodization", "tier": "fitness", "trust": 4},
    # Journals
    "nature.com": {"name": "Nature", "tier": "journal", "trust": 5},
    "sciencedirect.com": {"name": "ScienceDirect", "tier": "journal", "trust": 5},
    "springer.com": {"name": "Springer", "tier": "journal", "trust": 5},
    "wiley.com": {"name": "Wiley", "tier": "journal", "trust": 5},
    "plos.org": {"name": "PLOS", "tier": "journal", "trust": 5},
    "jissn.com": {"name": "JISSN", "tier": "journal", "trust": 5},
    # Supplements
    "noopsec": {"name": "Nootropics", "tier": "supplements", "trust": 3},
    "examine.com": {"name": "Examine", "tier": "supplements", "trust": 5},
    # General Health
    "health.harvard.edu": {"name": "Harvard Health", "tier": "academic", "trust": 5},
    "clevelandclinic.org": {"name": "Cleveland Clinic", "tier": "medical", "trust": 5},
    "uclahealth.org": {"name": "UCLA Health", "tier": "academic", "trust": 5},
}

# Intent classification patterns
INTENT_PATTERNS = {
    "supplement": {
        "keywords": ["supplement", "creatine", "protein", "whey", "bcaa", "pre-workout", 
                     "testosterone", "steroid", "sarm", "peptide", "hgh", "melatonin",
                     "vitamin", "mineral", "zma", "fish oil", "omega-3", "vitamin d"],
        "weight": 2
    },
    "diet": {
        "keywords": ["diet", "nutrition", "meal plan", "calories", "macros", "keto", 
                     "paleo", "intermittent fasting", "bulking", "cutting", "carb", 
                     "protein intake", "what to eat", "meal prep", "nutrition plan"],
        "weight": 2
    },
    "workout": {
        "keywords": ["workout", "exercise", "training", "cardio", "strength", "hypertrophy",
                     "reps", "sets", "gym", "bench press", "squat", "deadlift", "routine",
                     "program", "splits", "push pull", "ppl", "workout plan"],
        "weight": 2
    },
    "compound": {
        "keywords": ["anavar", "testosterone", "nandrolone", "trenbolone", "winstrol",
                     "oxandrolone", "dianabol", "anadrol", " deca", "eq", "mk-677",
                     "rad-140", "lgd-4033", "yk-11", "s4", "ostarine", "cardarine",
                     "stacking", "cycle", " pct", "post cycle", "injection"],
        "weight": 3
    },
    "medical": {
        "keywords": ["bloodwork", "blood test", "side effect", "liver", "kidney", 
                     "cholesterol", "heart", "cancer", "medical", "doctor", "prescription",
                     "health risk", "safe", "dangerous", "harmful", "toxicity"],
        "weight": 2
    },
    "comparison": {
        "keywords": ["vs", "versus", "compare", "difference between", "which is better",
                     "anavar vs", "creatine vs", "sarm vs", "better than"],
        "weight": 2
    },
    "dosage": {
        "keywords": ["dosage", "dose", "mg", "ml", "iu", "how much", "how many",
                      "serving", "loading", "maintenance", "cycle length"],
        "weight": 3
    },
    "explanation": {
        "keywords": ["what is", "what are", "how does", "explain", "define",
                     "mechanism", "how it works", "science behind", "原理", "kya hai"],
        "weight": 1
    }
}

# Domain aliases
DOMAIN_ALIASES = {
    "examine.com": "examine.com",
    "pubmed.ncbi.nlm.nih.gov": "pubmed",
    "pubmed.gov": "pubmed",
    "ncbi.nlm.nih.gov": "ncbi",
    "nih.gov": "nih",
    "who.int": "who",
    "cdc.gov": "cdc",
    "healthline.com": "healthline",
    "medicalnewstoday.com": "mnt",
    "webmd.com": "webmd",
    "mayoclinic.org": "mayo",
    "nature.com": "nature",
    "sciencedirect.com": "sciencedirect",
    "springer.com": "springer",
    "wiley.com": "wiley",
    "plos.org": "plos",
}


# ═══════════════════════════════════════════════════════════════════════════
# DATABASE
# ═══════════════════════════════════════════════════════════════════════════

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS searches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        query TEXT NOT NULL,
        query_hash TEXT NOT NULL,
        intent TEXT,
        results_count INTEGER DEFAULT 0,
        verified_count INTEGER DEFAULT 0,
        created_at TEXT DEFAULT (datetime('now'))
    );
    CREATE TABLE IF NOT EXISTS web_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        search_id INTEGER NOT NULL,
        title TEXT,
        url TEXT,
        snippet TEXT,
        domain TEXT,
        is_verified INTEGER DEFAULT 0,
        trust_tier TEXT,
        trust_score INTEGER DEFAULT 0,
        source_type TEXT,
        created_at TEXT DEFAULT (datetime('now')),
        FOREIGN KEY(search_id) REFERENCES searches(id)
    );
    CREATE TABLE IF NOT EXISTS deep_research (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        query TEXT NOT NULL,
        query_hash TEXT NOT NULL,
        summary TEXT,
        key_findings TEXT,
        verified_sources TEXT,
        benefits TEXT,
        risks TEXT,
        dosage_info TEXT,
        references_links TEXT,
        created_at TEXT DEFAULT (datetime('now'))
    );
    CREATE INDEX IF NOT EXISTS idx_search_hash ON searches(query_hash);
    CREATE INDEX IF NOT EXISTS idx_results_search ON web_results(search_id);
    CREATE INDEX IF NOT EXISTS idx_research_hash ON deep_research(query_hash);
    """)
    conn.commit()
    conn.close()

init_db()


# ═══════════════════════════════════════════════════════════════════════════
# SOURCE VERIFICATION
# ═══════════════════════════════════════════════════════════════════════════

def verify_source(url: str) -> dict:
    """Verify if a URL is from a trusted domain."""
    if not url:
        return {"verified": False, "trust_score": 0, "tier": None, "name": None}
    
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower().replace("www.", "")
        
        # Check exact match
        if domain in TRUSTED_DOMAINS:
            info = TRUSTED_DOMAINS[domain]
            return {
                "verified": True,
                "trust_score": info["trust"],
                "tier": info["tier"],
                "name": info["name"],
                "domain": domain
            }
        
        # Check partial match
        for trusted, info in TRUSTED_DOMAINS.items():
            if trusted in domain or domain in trusted:
                return {
                    "verified": True,
                    "trust_score": info["trust"],
                    "tier": info["tier"],
                    "name": info["name"],
                    "domain": domain
                }
        
        return {
            "verified": False,
            "trust_score": 1,
            "tier": "general",
            "name": domain[:30] if domain else "Unknown",
            "domain": domain
        }
    except Exception:
        return {"verified": False, "trust_score": 0, "tier": None, "name": None}


def extract_domain(url: str) -> str:
    """Extract clean domain from URL."""
    try:
        parsed = urlparse(url)
        return parsed.netloc.replace("www.", "").lower()
    except:
        return ""


# ═══════════════════════════════════════════════════════════════════════════
# INTENT DETECTION
# ═══════════════════════════════════════════════════════════════════════════

def detect_intent(query: str) -> dict:
    """Detect the intent and category of a user query."""
    query_lower = query.lower()
    scores = {}
    
    for intent_name, config in INTENT_PATTERNS.items():
        score = 0
        for keyword in config["keywords"]:
            if keyword.lower() in query_lower:
                score += config["weight"]
        if score > 0:
            scores[intent_name] = score
    
    # Determine primary intent
    if scores:
        primary_intent = max(scores, key=scores.get)
        confidence = min(scores[primary_intent] / 10, 1.0)
    else:
        primary_intent = "general"
        confidence = 0.3
    
    # Determine category
    category = "research"
    if primary_intent in ["supplement", "compound", "dosage"]:
        category = "supplements"
    elif primary_intent == "diet":
        category = "nutrition"
    elif primary_intent == "workout":
        category = "training"
    elif primary_intent == "medical":
        category = "medical"
    
    return {
        "primary_intent": primary_intent,
        "confidence": round(confidence, 2),
        "all_intents": dict(sorted(scores.items(), key=lambda x: x[1], reverse=True)),
        "category": category,
        "query_normalized": query.strip()
    }


# ═══════════════════════════════════════════════════════════════════════════
# LIVE WEB SEARCH (via Zenserp)
# ═══════════════════════════════════════════════════════════════════════════

def web_search(query: str, num_results: int = 10) -> dict:
    """Perform live web search via Zenserp API."""
    results = {
        "query": query,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "results": [],
        "verified_results": [],
        "total_results": 0,
        "verified_count": 0,
        "sources_by_domain": {}
    }
    
    if not ZENSERP_API_KEY:
        results["error"] = "Zenserp API key not configured"
        return results
    
    try:
        url = f"https://app.zenserp.com/api/v2/search?q={quote(query)}&apikey={ZENSERP_API_KEY}&num_results={num_results}"
        resp = requests.get(url, timeout=15)
        
        if resp.status_code != 200:
            results["error"] = f"API error: {resp.status_code}"
            return results
        
        data = resp.json()
        organic = data.get("organic", [])
        
        for item in organic[:num_results]:
            result_url = item.get("url", "")
            domain = extract_domain(result_url)
            verification = verify_source(result_url)
            
            result_item = {
                "title": item.get("title", ""),
                "url": result_url,
                "snippet": item.get("description", ""),
                "domain": domain,
                "source_type": verification["tier"] or "general",
                "is_verified": verification["verified"],
                "trust_score": verification["trust_score"],
                "verified_source": verification["name"] if verification["verified"] else None
            }
            
            results["results"].append(result_item)
            
            if verification["verified"]:
                results["verified_results"].append(result_item)
                results["verified_count"] += 1
                
                # Group by domain
                if domain not in results["sources_by_domain"]:
                    results["sources_by_domain"][domain] = []
                results["sources_by_domain"][domain].append(result_item)
        
        results["total_results"] = len(results["results"])
        
    except Exception as e:
        results["error"] = str(e)
    
    return results


def pubmed_search(query: str, max_results: int = 5) -> dict:
    """Search PubMed for scientific papers."""
    results = {
        "query": query,
        "papers": [],
        "total": 0
    }
    
    try:
        # Search for papers
        search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        params = {
            "db": "pubmed",
            "term": query,
            "retmax": max_results,
            "sort": "relevance",
            "retmode": "json"
        }
        if PUBMED_API_KEY:
            params["api_key"] = PUBMED_API_KEY
        
        resp = requests.get(search_url, params=params, timeout=10)
        data = resp.json()
        
        ids = data.get("esearchresult", {}).get("idlist", [])
        
        if not ids:
            return results
        
        # Fetch paper details
        fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
        fetch_params = {
            "db": "pubmed",
            "id": ",".join(ids),
            "retmode": "json"
        }
        if PUBMED_API_KEY:
            fetch_params["api_key"] = PUBMED_API_KEY
        
        resp = requests.get(fetch_url, params=fetch_params, timeout=10)
        data = resp.json()
        
        for pid in ids:
            paper = data.get("result", {}).get(pid, {})
            if paper:
                results["papers"].append({
                    "pmid": pid,
                    "title": paper.get("title", ""),
                    "authors": [a.get("name", "") for a in paper.get("authors", [])[:3]],
                    "journal": paper.get("source", ""),
                    "pubdate": paper.get("pubdate", ""),
                    "url": f"https://pubmed.ncbi.nlm.nih.gov/{pid}/"
                })
        
        results["total"] = len(results["papers"])
        
    except Exception as e:
        results["error"] = str(e)
    
    return results


# ═══════════════════════════════════════════════════════════════════════════
# DEEP RESEARCH
# ═══════════════════════════════════════════════════════════════════════════

def deep_research(query: str) -> dict:
    """Perform comprehensive deep research on a topic."""
    research = {
        "query": query,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "intent": detect_intent(query),
        "summary": "",
        "key_findings": [],
        "verified_sources": [],
        "benefits": [],
        "risks": [],
        "dosage_info": "",
        "usage_recommendations": [],
        "references": [],
        "videos": [],
        "books": [],
        "articles": [],
        "source_stats": {
            "verified": 0,
            "scientific": 0,
            "general": 0
        }
    }
    
    # Run searches in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        web_future = executor.submit(web_search, query, 15)
        pubmed_future = executor.submit(pubmed_search, query, 5)
        
        web_results = web_future.result()
        pubmed_results = pubmed_future.result()
    
    # Process web results
    all_sources = []
    
    for result in web_results.get("results", []):
        source = {
            "title": result["title"],
            "url": result["url"],
            "snippet": result["snippet"],
            "domain": result["domain"],
            "is_verified": result["is_verified"],
            "trust_score": result["trust_score"],
            "type": result["source_type"]
        }
        all_sources.append(source)
        
        # Track source stats
        if result["is_verified"]:
            research["source_stats"]["verified"] += 1
            if result["source_type"] == "scientific":
                research["source_stats"]["scientific"] += 1
            research["verified_sources"].append(source)
        else:
            research["source_stats"]["general"] += 1
        
        # Categorize by intent
        if research["intent"]["primary_intent"] == "dosage" and "dosage" in result["snippet"].lower():
            research["dosage_info"] = result["snippet"]
        
        # Add to articles
        if len(research["articles"]) < 10:
            research["articles"].append({
                "title": result["title"],
                "url": result["url"],
                "source": result["domain"],
                "verified": result["is_verified"]
            })
    
    # Process PubMed results
    for paper in pubmed_results.get("papers", []):
        source = {
            "title": paper["title"],
            "url": paper["url"],
            "snippet": f"Published in {paper['journal']} ({paper['pubdate']})",
            "domain": "pubmed.ncbi.nlm.nih.gov",
            "is_verified": True,
            "trust_score": 5,
            "type": "scientific"
        }
        all_sources.append(source)
        research["verified_sources"].append(source)
        research["references"].append(paper)
        research["source_stats"]["verified"] += 1
        research["source_stats"]["scientific"] += 1
        
        research["key_findings"].append({
            "source": paper["journal"],
            "pmid": paper["pmid"],
            "title": paper["title"]
        })
    
    # Generate summary from verified sources
    if research["verified_sources"]:
        summary_parts = []
        for src in research["verified_sources"][:3]:
            if src.get("snippet"):
                summary_parts.append(src["snippet"][:200])
        research["summary"] = " ".join(summary_parts)
    
    # Extract benefits/risks from snippets
    for src in all_sources:
        snippet_lower = src.get("snippet", "").lower()
        if "benefit" in snippet_lower or "increases" in snippet_lower or "improves" in snippet_lower:
            if len(research["benefits"]) < 5:
                research["benefits"].append(src["snippet"][:150])
        if "risk" in snippet_lower or "side effect" in snippet_lower or "harmful" in snippet_lower:
            if len(research["risks"]) < 5:
                research["risks"].append(src["snippet"][:150])
    
    return research


# ═══════════════════════════════════════════════════════════════════════════
# MCP TOOLS (JSON-RPC Format)
# ═══════════════════════════════════════════════════════════════════════════

def mcp_web_search(query: str, max_results: int = 10) -> dict:
    """MCP tool: Web search with source verification."""
    return {
        "tool": "web_search",
        "query": query,
        "results": web_search(query, max_results),
        "intent": detect_intent(query)
    }


def mcp_deep_research(query: str) -> dict:
    """MCP tool: Comprehensive deep research."""
    return {
        "tool": "deep_research",
        "query": query,
        "research": deep_research(query)
    }


def mcp_detect_intent(query: str) -> dict:
    """MCP tool: Detect query intent."""
    return {
        "tool": "intent_detection",
        "query": query,
        "intent": detect_intent(query)
    }


def mcp_verify_source(url: str) -> dict:
    """MCP tool: Verify if URL is from trusted source."""
    return {
        "tool": "verify_source",
        "url": url,
        "verification": verify_source(url)
    }


# ═══════════════════════════════════════════════════════════════════════════
# FLASK APPLICATION
# ═══════════════════════════════════════════════════════════════════════════

app = Flask(__name__, static_folder=os.path.join(BASE_DIR, "static"))
app.secret_key = os.environ.get("SECRET_KEY", "fitsearch-mcp-2026")
CORS(app, supports_credentials=True, origins="*")


# ─── MCP Endpoints ──────────────────────────────────────────────────────────

@app.route("/mcp/web_search", methods=["GET", "POST"])
def mcp_search():
    """MCP tool endpoint for web search."""
    if request.method == "POST":
        data = request.get_json() or {}
        query = data.get("query", "")
        max_results = data.get("max_results", 10)
    else:
        query = request.args.get("query", "")
        max_results = int(request.args.get("max_results", 10))
    
    if not query:
        return jsonify({"error": "Query required"}), 400
    
    result = mcp_web_search(query, max_results)
    return jsonify(result)


@app.route("/mcp/deep_research", methods=["GET", "POST"])
def mcp_deep():
    """MCP tool endpoint for deep research."""
    if request.method == "POST":
        data = request.get_json() or {}
        query = data.get("query", "")
    else:
        query = request.args.get("query", "")
    
    if not query:
        return jsonify({"error": "Query required"}), 400
    
    result = mcp_deep_research(query)
    return jsonify(result)


@app.route("/mcp/intent", methods=["GET", "POST"])
def mcp_intent():
    """MCP tool endpoint for intent detection."""
    if request.method == "POST":
        data = request.get_json() or {}
        query = data.get("query", "")
    else:
        query = request.args.get("query", "")
    
    if not query:
        return jsonify({"error": "Query required"}), 400
    
    result = mcp_detect_intent(query)
    return jsonify(result)


@app.route("/mcp/verify", methods=["GET", "POST"])
def mcp_verify():
    """MCP tool endpoint for source verification."""
    if request.method == "POST":
        data = request.get_json() or {}
        url = data.get("url", "")
    else:
        url = request.args.get("url", "")
    
    if not url:
        return jsonify({"error": "URL required"}), 400
    
    result = mcp_verify_source(url)
    return jsonify(result)


@app.route("/mcp/trusted-domains", methods=["GET"])
def mcp_trusted():
    """Get list of all trusted domains."""
    return jsonify({
        "trusted_domains": TRUSTED_DOMAINS,
        "total": len(TRUSTED_DOMAINS)
    })


# ─── Standard Endpoints ────────────────────────────────────────────────────

@app.route("/search", methods=["GET", "POST"])
def api_search():
    """Standard search endpoint."""
    if request.method == "POST":
        data = request.get_json() or {}
        query = data.get("query", "")
    else:
        query = request.args.get("query", "")
    
    if not query:
        return jsonify({"error": "Query required"}), 400
    
    intent = detect_intent(query)
    results = web_search(query, 15)
    pubmed = pubmed_search(query, 5)
    
    return jsonify({
        "query": query,
        "intent": intent,
        "results": results.get("results", []),
        "verified_results": results.get("verified_results", []),
        "pubmed": pubmed.get("papers", []),
        "stats": {
            "total": results.get("total_results", 0),
            "verified": results.get("verified_count", 0),
            "pubmed": pubmed.get("total", 0)
        }
    })


@app.route("/deep-research", methods=["GET", "POST"])
def api_deep():
    """Deep research endpoint."""
    if request.method == "POST":
        data = request.get_json() or {}
        query = data.get("query", "")
    else:
        query = request.args.get("query", "")
    
    if not query:
        return jsonify({"error": "Query required"}), 400
    
    research = deep_research(query)
    return jsonify(research)


@app.route("/intent", methods=["GET", "POST"])
def api_intent():
    """Intent detection endpoint."""
    if request.method == "POST":
        data = request.get_json() or {}
        query = data.get("query", "")
    else:
        query = request.args.get("query", "")
    
    if not query:
        return jsonify({"error": "Query required"}), 400
    
    return jsonify(detect_intent(query))


@app.route("/health", methods=["GET"])
def api_health():
    """Health check endpoint."""
    return jsonify({
        "status": "ok",
        "version": "MCP v1.0",
        "services": {
            "zenserp": bool(ZENSERP_API_KEY),
            "anthropic": bool(ANTHROPIC_API_KEY),
            "pubmed": bool(PUBMED_API_KEY)
        },
        "trusted_domains": len(TRUSTED_DOMAINS)
    })


# ─── Static Files & SPA ───────────────────────────────────────────────────

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
