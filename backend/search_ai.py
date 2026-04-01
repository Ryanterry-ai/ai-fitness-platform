"""
search_ai.py — FitSearch AI
World-Class Fitness Research Engine v5 (Real-Time + RAG + Bing + Google)
================================================================================
Uses Bing + Google (CX: 860eab761ebac4c12) for real-time data + OpenAI RAG.
"""

from __future__ import annotations
import os, json, re, time, hashlib, sqlite3, threading
from datetime import datetime, timezone
from typing import Any
import requests

# ====================== CONFIG ======================
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "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")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "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")
BING_API_KEY = os.getenv("BING_API_KEY", "")
GOOGLE_SEARCH_API_KEY = os.getenv("GOOGLE_SEARCH_API_KEY", "AIzaSyAe6LNE1Er_KpTK4PdpTVb5OrqbD5wLZG8")
GOOGLE_CX = os.getenv("GOOGLE_CX", "860eab761ebac4c12")   # ← Your confirmed CX

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_DB = os.path.join(BASE_DIR, "database", "search_cache.db")
CACHE_TTL_SEC = 86400

_cache_lock = threading.Lock()

# ====================== OPTIMIZED DATABASE INIT ======================
def init_db():
    os.makedirs(os.path.dirname(CACHE_DB), exist_ok=True)
    with sqlite3.connect(CACHE_DB) as conn:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        conn.execute("PRAGMA cache_size=-64000;")
        conn.execute("PRAGMA temp_store=MEMORY;")
        conn.execute("PRAGMA auto_vacuum=INCREMENTAL;")
        conn.execute("PRAGMA mmap_size=300000000;")

        conn.execute("""
            CREATE TABLE IF NOT EXISTS report_cache (
                cache_key TEXT PRIMARY KEY,
                query TEXT,
                report_json TEXT,
                source TEXT,
                created_at REAL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS query_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL,
                result_json TEXT NOT NULL,
                timestamp REAL NOT NULL,
                source TEXT DEFAULT 'kb',
                last_updated REAL NOT NULL
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_query_history_query ON query_history(query);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_query_history_timestamp ON query_history(timestamp);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_report_cache_created ON report_cache(created_at);")
init_db()

# ====================== INTENT CLASSIFICATION ======================
_INTENT_RULES: list[tuple[list[str], str]] = [
    (["what is", "what are", "explain", "define"], "what_is"),
    (["how does", "how it works", "mechanism"], "how_it_works"),
    (["benefits of"], "benefits"),
    (["side effects", "risks", "dangerous", "is it safe"], "side_effects"),
    (["dosage", "dose", "how much"], "dosage"),
    (["when to take", "best time", "timing"], "timing"),
    (["compare", "vs", "versus"], "compare"),
    (["stack"], "stack"),
    (["cycle", "pct", "post cycle"], "cycle"),
    (["beginner"], "beginner"),
    (["advanced"], "advanced"),
    (["for women", "female"], "female_specific"),
    (["bloodwork", "lab results"], "bloodwork"),
    (["meal plan", "diet plan", "macros"], "meal_plan"),
    (["workout", "training program", "routine", "split", "exercises for"], "workout_routine"),
]

def classify_intent(query: str) -> str:
    q = query.lower()
    for triggers, label in _INTENT_RULES:
        if any(t in q for t in triggers):
            return label
    return "research"

# ====================== GOAL MODIFIERS ======================
_GOAL_PHRASES: dict[str, list[str]] = {
    "muscle_gain": ["muscle gain", "bulking", "hypertrophy"],
    "fat_loss": ["fat loss", "cutting", "weight loss", "belly fat", "loose belly", "lose belly"],
    "strength": ["strength", "powerlifting"],
    "female": ["women", "female"],
    "beginner": ["beginner"],
}

def _extract_goal_modifiers(query: str) -> list[str]:
    q = query.lower()
    return [tag for tag, phrases in _GOAL_PHRASES.items() if any(p in q for p in phrases)]

# ====================== DOMAIN & ENTITY ======================
QUERY_DOMAINS: dict[str, list[str]] = {
    "muscle_gain": ["muscle gain","bulking","hypertrophy","build muscle"],
    "fat_loss": ["fat loss","cutting","weight loss","shred","burn fat","belly fat","loose belly","lose belly"],
    "strength": ["strength","powerlifting","power","strong"],
    "endurance": ["endurance","cardio","stamina"],
    "recovery": ["recovery","healing","injury"],
    "supplements": ["creatine","whey","protein","pre workout"],
    "steroids": ["testosterone","anavar","tren","steroid"],
    "sarms": ["ostarine","lgd","rad140","sarm"],
    "peptides": ["bpc157","tb500","ipamorelin","peptide"],
    "hgh": ["hgh","growth hormone"],
    "nutrition": ["diet","nutrition","meal plan"],
    "exercise": ["workout","training","exercises for"],
}

def detect_domain(query: str) -> str:
    q = query.lower()
    scores: dict[str, int] = {}
    for domain, keywords in QUERY_DOMAINS.items():
        sc = sum(1 for kw in keywords if kw in q)
        if sc > 0:
            scores[domain] = sc
    return max(scores, key=lambda x: scores[x]) if scores else "general_fitness"

ENTITY_GROUPS: dict[str, list[str]] = {
    "creatine":["crm_mono","crm_hcl"], "creatine_mono":["crm_mono"], "creatine_hcl":["crm_hcl"],
    "whey":["whey"], "protein":["whey"],
    "citrulline":["citrulline"], "beta_alanine":["beta_al"], "caffeine":["caffeine"],
    "pre_workout":["caffeine","citrulline","beta_al"],
    "sarm":["ostarine","lgd4033","rad140","mk677"], "ostarine":["ostarine"],
    "lgd4033":["lgd4033"], "rad140":["rad140"], "mk677":["mk677"],
    "steroid":["test_e","anavar","nandrolone"], "testosterone":["test_e"],
    "anavar":["anavar"], "nandrolone":["nandrolone"],
    "peptide":["bpc157","tb500","ipamorelin"], "bpc157":["bpc157"],
    "tb500":["tb500"], "ipamorelin":["ipamorelin"], "hgh":["hgh"],
    "vitamin_d":["vitamin_d"], "omega3":["omega3"], "zinc_magnesium":["zinc_magnesium"],
    "fat_burner":["caffeine","fat_burner_stack"],
}

ENTITY_TRIGGERS: list[tuple[str, str]] = sorted([
    ("creatine monohydrate","creatine_mono"),("creatine hcl","creatine_hcl"),
    ("creatine hydrochloride","creatine_hcl"),("creatina","creatine"),("créatine","creatine"),
    ("kreatin","creatine"),("क्रिएटिन","creatine"),("creatine","creatine"),
    ("whey protein","whey"),("whey isolate","whey"),("whey concentrate","whey"),("whey","whey"),
    ("protein powder","protein"),
    ("citrulline malate","citrulline"),("l-citrulline","citrulline"),("citrulline","citrulline"),
    ("beta-alanine","beta_alanine"),("beta alanine","beta_alanine"),
    ("caffeine anhydrous","caffeine"),("caffeine","caffeine"),
    ("pre-workout","pre_workout"),("pre workout","pre_workout"),("preworkout","pre_workout"),
    ("ostarine","ostarine"),("mk-2866","ostarine"),("mk2866","ostarine"),("enobosarm","ostarine"),
    ("lgd-4033","lgd4033"),("lgd4033","lgd4033"),("ligandrol","lgd4033"),
    ("rad-140","rad140"),("rad140","rad140"),("testolone","rad140"),
    ("mk-677","mk677"),("mk677","mk677"),("ibutamoren","mk677"),
    ("sarms","sarm"),("sarm","sarm"),
    ("testosterone enanthate","testosterone"),("test enanthate","testosterone"),
    ("test e","testosterone"),("testosterone","testosterone"),("testosteron","testosterone"),
    ("oxandrolone","anavar"),("anavar","anavar"),
    ("nandrolone decanoate","nandrolone"),("deca durabolin","nandrolone"),("nandrolone","nandrolone"),
    ("steroids","steroid"),("steroid","steroid"),
    ("bpc-157","bpc157"),("bpc157","bpc157"),("body protection compound","bpc157"),
    ("tb-500","tb500"),("tb500","tb500"),
    ("ipamorelin","ipamorelin"),("cjc-1295","ipamorelin"),
    ("human growth hormone","hgh"),("growth hormone","hgh"),("somatropin","hgh"),("hgh","hgh"),
    ("peptides","peptide"),("peptide","peptide"),
    ("vitamin d3","vitamin_d"),("vitamin d","vitamin_d"),
    ("fish oil","omega3"),("omega-3","omega3"),("omega 3","omega3"),
    ("zma","zinc_magnesium"),("zinc magnesium","zinc_magnesium"),
    ("fat burner","fat_burner"),("thermogenic","fat_burner"),
], key=lambda t: len(t[0]), reverse=True)

def extract_primary_entity(query: str) -> tuple[str | None, list[str]]:
    q = query.lower()
    for phrase, key in ENTITY_TRIGGERS:
        if phrase in q:
            return key, ENTITY_GROUPS.get(key, [])
    return None, []

# ====================== EXPANDED GENERAL TOPICS ======================
GENERAL_TOPICS: list[dict] = [
    {
        "id": "belly_fat_loss",
        "triggers": ["lose belly fat", "loose belly fat", "reduce belly fat", "belly fat", "how i can loose my belly fat", "how to lose belly fat"],
        "name": "How to Lose Belly Fat",
        "tagline": "Science-based guide to reduce belly fat and get a leaner midsection",
        "category": "nutrition",
        "evidence_tier": "very_high",
        "what_it_is": "Belly fat (visceral fat) cannot be spot-reduced. You must create an overall calorie deficit while preserving muscle.",
        "how_it_works": "Calorie deficit + high protein + resistance training + some cardio/HIIT is the most effective combination.",
        "dosage": "500–750 kcal daily deficit. Protein 2.0–2.4 g/kg bodyweight.",
        "timing": "Daily consistent deficit. HIIT 2–3x/week. Daily walking 8,000–12,000 steps.",
        "best_ways_to_use": ["Create a moderate calorie deficit", "Prioritise resistance training 3–4x/week", "Eat high protein at every meal", "Include some HIIT or steady cardio", "Sleep 7–9 hours and manage stress"],
        "who_should_use": ["Anyone with excess belly fat"],
        "who_should_avoid": ["Those with eating disorder history"],
        "benefits": ["Reduced visceral fat", "Improved health markers", "Better aesthetics"],
        "side_effects": [{"effect": "Temporary hunger in deficit", "severity": "low"}],
        "final_recommendation": "Focus on overall fat loss through calorie deficit, high protein, and resistance training.",
        "ai_summary": "You cannot spot-reduce belly fat. Create a calorie deficit, eat high protein, lift weights, and be consistent for 8–12 weeks.",
    },
]

def _find_general_topic(query: str) -> dict | None:
    q = query.lower()
    best_match = None
    best_score = 0
    for topic in GENERAL_TOPICS:
        score = sum(1 for trigger in topic["triggers"] if trigger in q)
        if score > best_score:
            best_score = score
            best_match = topic
    return best_match

# ====================== MAIN SEARCH FUNCTION (RAG) ======================
def search_knowledge(query: str, filters: list[str] | None = None) -> list[dict]:
    filters = filters or []
    intent = classify_intent(query)
    domain = detect_domain(query)
    entity_key, allowed_ids = extract_primary_entity(query)
    goal_mods = _extract_goal_modifiers(query)

    cache_key = _cache_key(query, filters)
    cached = _cache_get(cache_key)
    if cached:
        return cached

    results: list[dict] = []

    bing_results = _bing_search(query)
    google_results = _google_search(query)
    combined_context = bing_results + google_results

    rag_report = _openai_rag_generate_report(query, intent, domain, combined_context)

    if rag_report:
        results.append(rag_report)

    if results:
        _store_query(query, results)
        _cache_set(cache_key, query, results)

    return results

# ====================== GOOGLE SEARCH API ======================
def _google_search(query: str) -> list[dict]:
    if not GOOGLE_SEARCH_API_KEY or not GOOGLE_CX:
        return []
    try:
        url = "https://www.googleapis.com/customsearch/v1"
        params = {"key": GOOGLE_SEARCH_API_KEY, "cx": GOOGLE_CX, "q": query, "num": 8}
        r = requests.get(url, params=params, timeout=10)
        if r.status_code != 200:
            return []
        data = r.json()
        results = []
        for item in data.get("items", []):
            results.append({"title": item.get("title", ""), "url": item.get("link", ""), "snippet": item.get("snippet", ""), "source": "Google"})
        return results
    except Exception as e:
        print(f"[Google Search] Error: {e}")
        return []

# ====================== BING WEB SEARCH API ======================
def _bing_search(query: str) -> list[dict]:
    if not BING_API_KEY:
        return []
    try:
        headers = {"Ocp-Apim-Subscription-Key": BING_API_KEY}
        params = {"q": query, "count": 8, "freshness": "Week"}
        r = requests.get("https://api.bing.microsoft.com/v7.0/search", headers=headers, params=params, timeout=10)
        if r.status_code != 200:
            return []
        data = r.json()
        results = []
        for item in data.get("webPages", {}).get("value", []):
            results.append({"title": item.get("name", ""), "url": item.get("url", ""), "snippet": item.get("snippet", ""), "source": "Bing"})
        return results
    except Exception as e:
        print(f"[Bing Search] Error: {e}")
        return []

# ====================== OPENAI RAG REPORT GENERATION ======================
def _openai_rag_generate_report(query: str, intent: str, domain: str, context: list) -> dict | None:
    if not OPENAI_API_KEY:
        return None
    try:
        system_prompt = "You are FitSearch AI, a world-class fitness research engine. Use the provided real-time search context to generate a highly accurate, structured, and helpful response. Always ground your answer in the given context."
        user_prompt = f"Query: {query}\nIntent: {intent}\nDomain: {domain}\n\nReal-time Search Context (Bing + Google):\n{json.dumps(context, ensure_ascii=False)}\n\nGenerate a complete structured fitness report in this exact JSON format: {{ \"name\": \"Short title\", \"tagline\": \"One compelling sentence\", \"category\": \"nutrition|exercise|supplement|research|general\", \"evidence_tier\": \"very_high|high|moderate|low\", \"safe_for_beginners\": true, \"what_it_is\": \"Clear explanation\", \"how_it_works\": \"Mechanism\", \"dosage\": \"Practical advice\", \"timing\": \"When to do it\", \"best_ways_to_use\": [\"Tip 1\", \"Tip 2\"], \"who_should_use\": [\"Group 1\"], \"who_should_avoid\": [\"Group 1\"], \"benefits\": [\"Benefit 1\"], \"side_effects\": [{\"effect\": \"Description\", \"severity\": \"low|medium|high\"}], \"final_recommendation\": \"Actionable advice\", \"ai_summary\": \"Expert summary\" }}"

        r = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"},
            json={"model": "gpt-4o", "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}], "temperature": 0.7, "max_tokens": 2000},
            timeout=30
        )
        r.raise_for_status()
        content = r.json()["choices"][0]["message"]["content"].strip()
        return json.loads(content)
    except Exception as e:
        print(f"[OpenAI RAG] Error: {e}")
        return None

# ====================== STORE QUERY ======================
def _store_query(query: str, results: list):
    try:
        with sqlite3.connect(CACHE_DB) as conn:
            conn.execute("INSERT INTO query_history (query, result_json, timestamp, last_updated) VALUES (?, ?, ?, ?)", (query, json.dumps(results), time.time(), time.time()))
    except Exception as e:
        print(f"[Store Query] Error: {e}")

# ====================== REPORT BUILDER ======================
def _to_report(item: dict, ev: dict, intent: str, source: str = "kb", is_general: bool = False) -> dict:
    return {
        "name": item.get("name", "Fitness Answer"),
        "tagline": item.get("tagline", ""),
        "category": item.get("category", "general"),
        "evidence_tier": item.get("evidence_tier", "moderate"),
        "safe_for_beginners": item.get("safe_for_beginners", True),
        "what_it_is": item.get("what_it_is", ""),
        "how_it_works": item.get("how_it_works", ""),
        "dosage": item.get("dosage", ""),
        "timing": item.get("timing", ""),
        "best_ways_to_use": item.get("best_ways_to_use", []),
        "who_should_use": item.get("who_should_use", []),
        "who_should_avoid": item.get("who_should_avoid", []),
        "benefits": item.get("benefits", []),
        "side_effects": item.get("side_effects", []),
        "research_evidence": item.get("research_evidence", []),
        "final_recommendation": item.get("final_recommendation", ""),
        "ai_summary": item.get("ai_summary", ""),
        "_source": source,
    }

# ====================== CACHE ======================
def _cache_key(query: str, filters: list) -> str:
    raw = json.dumps({"q": query.lower().strip(), "f": sorted(filters)}, sort_keys=True)
    return hashlib.sha256(raw.encode()).hexdigest()[:32]

def _cache_get(key: str) -> list | None:
    try:
        with _cache_lock, sqlite3.connect(CACHE_DB) as c:
            row = c.execute("SELECT report_json, created_at FROM report_cache WHERE cache_key=?", (key,)).fetchone()
        if not row or (time.time() - row[1]) > CACHE_TTL_SEC:
            return None
        return json.loads(row[0])
    except Exception:
        return None

def _cache_set(key: str, query: str, results: list, source: str = "kb") -> None:
    try:
        with _cache_lock, sqlite3.connect(CACHE_DB) as c:
            c.execute("INSERT OR REPLACE INTO report_cache(cache_key,query,report_json,source,created_at) VALUES (?,?,?,?,?)",
                      (key, query, json.dumps(results), source, time.time()))
    except Exception:
        pass

print("✅ FitSearch AI v5 loaded successfully with Google Search API (CX: 860eab761ebac4c12) + Full RAG.")

# End of file
