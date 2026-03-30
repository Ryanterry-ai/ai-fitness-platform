"""
search_ai.py  —  FitSearch AI — World-Class Hybrid Search Engine v2
====================================================================

Architecture (Perplexity + ChatGPT + Google AI combined):

  User Query
      │
      ▼  1. INTENT CLASSIFICATION  — Research | Product | Training/Diet/Health
      │
      ▼  2. ENTITY EXTRACTION  — primary entity + secondary modifiers
      │
      ▼  3. STRICT RELEVANCE FILTER  — entity-locked result set (fixes Issue 1)
      │
      ▼  4. CACHE LOOKUP  — SQLite 24 h TTL (cache key includes filters)
      │
      ▼  5. LIVE RETRIEVAL (parallel)  — PubMed · Examine · OpenFDA · SerpAPI
      │
      ▼  6. TRUST SCORING  — PubMed(5) Examine(4) NIH(4) Expert(3) Web(2)
      │
      ▼  7. CLAUDE SYNTHESIS  — intent-specific structured output
      │
      ▼  8. CACHE WRITE
      │
      ▼  9. DYNAMIC RESULT  — filter-aware, re-ranked on every filter click

FIX 1 — Irrelevant results
  → Strict entity group enforcement: creatine query → ONLY creatine items
  → Primary entity identified, all results must belong to that entity group
  → Supplementary items only added if from same compound family

FIX 2 — Real-time filtering
  → Cache key includes filters array → different cache entry per filter combo
  → Filter clicks POST to /search with new filters → full re-rank + re-render
  → Filter boosts: matching tag items get +50 score boost (dominant)

Environment variables:
  ANTHROPIC_API_KEY   — Claude API for structured AI reports
  PUBMED_API_KEY      — optional, raises rate limit to 10/s
  SERP_API_KEY        — optional, live Google results
"""

from __future__ import annotations
import os, json, re, time, hashlib, sqlite3, threading, concurrent.futures
from datetime import datetime, timezone
from typing import Any
import requests

# ── Keys ──────────────────────────────────────────────────────────────────
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
PUBMED_API_KEY    = os.getenv("PUBMED_API_KEY", "")
SERP_API_KEY      = os.getenv("SERP_API_KEY", "")

# ── Paths ─────────────────────────────────────────────────────────────────
BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_DB  = os.path.join(BASE_DIR, "database", "search_cache.db")

# ── Endpoints ─────────────────────────────────────────────────────────────
ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
PUBMED_SEARCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
PUBMED_FETCH  = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
OPENFDA_URL   = "https://api.fda.gov/drug/event.json"
CACHE_TTL_SEC = 86400  # 24 h

_cache_lock = threading.Lock()

# ═══════════════════════════════════════════════════════════════════════════
# ENTITY GROUP MAP — strict relevance enforcement
# Each group lists every KB id that belongs to the same compound family.
# When a query matches a group, ONLY members of that group can appear in
# results. This completely eliminates the cross-contamination bug.
# ═══════════════════════════════════════════════════════════════════════════

ENTITY_GROUPS: dict[str, list[str]] = {
    # Creatine family
    "creatine":     ["crm_mono", "crm_hcl"],
    # Protein family
    "protein":      ["whey", "casein", "plant_protein"],
    "whey":         ["whey"],
    "casein":       ["casein"],
    # Pre-workout / stimulants
    "pre_workout":  ["caffeine", "citrulline", "beta_al"],
    "caffeine":     ["caffeine"],
    "citrulline":   ["citrulline"],
    "beta_alanine": ["beta_al"],
    # Fat loss
    "fat_burner":   ["caffeine", "fat_burner_stack"],
    "fat loss":     ["caffeine", "fat_burner_stack"],
    # SARMs
    "sarm":         ["ostarine", "lgd4033", "rad140", "mk677"],
    "ostarine":     ["ostarine"],
    "lgd":          ["lgd4033"],
    "rad140":       ["rad140"],
    "mk677":        ["mk677"],
    # Steroids
    "steroid":      ["test_e", "anavar", "nandrolone"],
    "testosterone": ["test_e"],
    "anavar":       ["anavar"],
    "nandrolone":   ["nandrolone"],
    "deca":         ["nandrolone"],
    # Peptides
    "peptide":      ["bpc157", "tb500", "ipamorelin", "sermorelin"],
    "bpc157":       ["bpc157"],
    "bpc-157":      ["bpc157"],
    "ipamorelin":   ["ipamorelin"],
    "hgh":          ["hgh"],
    "growth hormone": ["hgh"],
    # Vitamins / minerals
    "vitamin d":    ["vitamin_d"],
    "omega":        ["omega3"],
    "fish oil":     ["omega3"],
    "zinc":         ["zinc_magnesium"],
    "magnesium":    ["zinc_magnesium"],
}

# ── PRIMARY ENTITY TRIGGER PHRASES ────────────────────────────────────────
# Maps query keywords → entity group key. First match wins.
ENTITY_TRIGGERS: list[tuple[str, str]] = [
    # Creatine
    ("creatine monohydrate", "creatine"),
    ("creatine hcl",         "creatine"),
    ("creatine hydrochloride","creatine"),
    ("kreatin",              "creatine"),
    ("creatina",             "creatine"),
    ("créatine",             "creatine"),
    ("क्रिएटिन",            "creatine"),
    ("creatine",             "creatine"),
    # Protein
    ("whey protein",         "whey"),
    ("whey isolate",         "whey"),
    ("whey concentrate",     "whey"),
    ("whey",                 "whey"),
    ("casein protein",       "casein"),
    ("casein",               "casein"),
    ("protein powder",       "protein"),
    ("plant protein",        "protein"),
    # Pre-workout ingredients
    ("citrulline malate",    "citrulline"),
    ("l-citrulline",         "citrulline"),
    ("citrulline",           "citrulline"),
    ("beta-alanine",         "beta_alanine"),
    ("beta alanine",         "beta_alanine"),
    ("caffeine anhydrous",   "caffeine"),
    ("caffeine",             "caffeine"),
    # SARMs
    ("ostarine",             "ostarine"),
    ("mk-2866",              "ostarine"),
    ("mk2866",               "ostarine"),
    ("enobosarm",            "ostarine"),
    ("lgd-4033",             "lgd"),
    ("lgd4033",              "lgd"),
    ("ligandrol",            "lgd"),
    ("rad-140",              "rad140"),
    ("testolone",            "rad140"),
    ("mk-677",               "mk677"),
    ("ibutamoren",           "mk677"),
    ("sarm",                 "sarm"),
    ("sarms",                "sarm"),
    # Steroids
    ("testosterone enanthate","testosterone"),
    ("test enanthate",        "testosterone"),
    ("test e",               "testosterone"),
    ("testosterone",         "testosterone"),
    ("testosteron",          "testosterone"),
    ("oxandrolone",          "anavar"),
    ("anavar",               "anavar"),
    ("nandrolone",           "nandrolone"),
    ("deca durabolin",       "nandrolone"),
    ("npp",                  "nandrolone"),
    ("steroid",              "steroid"),
    ("steroids",             "steroid"),
    # Peptides
    ("bpc-157",              "bpc157"),
    ("bpc157",               "bpc157"),
    ("body protection compound","bpc157"),
    ("ipamorelin",           "ipamorelin"),
    ("cjc-1295",             "ipamorelin"),
    ("human growth hormone", "hgh"),
    ("growth hormone",       "hgh"),
    ("hgh",                  "hgh"),
    ("somatropin",           "hgh"),
    ("peptide",              "peptide"),
    ("peptides",             "peptide"),
    # Vitamins
    ("vitamin d3",           "vitamin d"),
    ("vitamin d",            "vitamin d"),
    ("omega-3",              "omega"),
    ("fish oil",             "fish oil"),
    ("omega 3",              "omega"),
    ("zinc magnesium",       "zinc"),
    ("zma",                  "zinc"),
    # Fat loss
    ("fat burner",           "fat_burner"),
    ("fat burning",          "fat_burner"),
    ("fat loss supplement",  "fat_burner"),
    # Pre-workout (generic — no specific compound)
    ("pre-workout",          "pre_workout"),
    ("pre workout",          "pre_workout"),
    ("preworkout",           "pre_workout"),
]

# ═══════════════════════════════════════════════════════════════════════════
# INTENT CLASSIFICATION
# ═══════════════════════════════════════════════════════════════════════════

# Intent types → drives output format
# research     → 10-section scientific report
# product      → product list with price/rating/category
# training     → day-wise plans / structured tables
# dosage       → focused dosage guide
# compare      → side-by-side table
# side_effects → risk/safety-focused report
# cycle        → cycle protocol + PCT
# explain      → definition + mechanism
# recommend    → ranked recommendation list

INTENT_RULES: list[tuple[list[str], str]] = [
    # Product intent — MUST come before generic research
    (["best brand", "which brand", "top brand", "brand india", "buy india",
      "price india", "cheapest", "most popular brand", "top 5", "top 10",
      "best supplement india", "recommend brand", "product"], "product"),
    # Training / diet
    (["workout plan", "training plan", "diet plan", "meal plan",
      "hypertrophy split", "ppl", "push pull", "4 day split",
      "high protein diet", "macro plan", "calorie plan"], "training"),
    # Dosage focused
    (["dosage", "dose", "how much", "mg", "grams", "mcg", "iu",
      "how many", "intake", "serving size"], "dosage"),
    # Side effects / risks
    (["side effect", "risk", "dangerous", "harm", "liver", "kidney",
      "safe", "safety", "danger", "adverse", "toxicity"], "side_effects"),
    # Compare
    (["vs", "versus", "compare", "comparison", "better than",
      "difference between", "which is better"], "compare"),
    # Cycle / protocol
    (["cycle", "protocol", "pct", "post cycle", "on cycle",
      "week cycle", "blast", "cruise"], "cycle"),
    # Explain / define
    (["what is", "what are", "how does", "explain", "define",
      "kya hai", "क्या है", "was ist", "qu'est-ce"], "explain"),
    # Recommend
    (["best", "recommend", "should i", "beginner",
      "which one", "top", "ideal for"], "recommend"),
    # Default
    ([], "research"),
]

def classify_intent(query: str) -> str:
    """Classify query into one of the intent types above."""
    q = query.lower()
    for triggers, intent in INTENT_RULES:
        if any(t in q for t in triggers):
            return intent
    return "research"

def extract_primary_entity(query: str) -> tuple[str | None, list[str]]:
    """
    Returns (entity_group_key, list_of_allowed_kb_ids).
    entity_group_key is None if no specific entity detected (general query).
    """
    q = query.lower()
    for phrase, group_key in ENTITY_TRIGGERS:
        if phrase in q:
            allowed_ids = ENTITY_GROUPS.get(group_key, [])
            return group_key, allowed_ids
    return None, []

# ── Secondary modifiers (goals) ────────────────────────────────────────────
GOAL_MODIFIERS: dict[str, list[str]] = {
    "muscle_gain":  ["muscle gain", "bulking", "mass", "hypertrophy", "build muscle", "muscle"],
    "fat_loss":     ["fat loss", "weight loss", "cutting", "shred", "lean", "fat burning"],
    "strength":     ["strength", "powerlifting", "power", "strong", "1rm", "max strength"],
    "endurance":    ["endurance", "cardio", "stamina", "aerobic", "running", "cycling"],
    "recovery":     ["recovery", "healing", "injury", "soreness", "doms"],
    "pre_workout":  ["pre workout", "pump", "energy", "focus", "performance"],
}

def extract_goal_modifiers(query: str) -> list[str]:
    """Returns list of matched goal tags from query."""
    q = query.lower()
    matched = []
    for tag, phrases in GOAL_MODIFIERS.items():
        if any(p in q for p in phrases):
            matched.append(tag)
    return matched

# ═══════════════════════════════════════════════════════════════════════════
# LOCAL KNOWLEDGE BASE
# ═══════════════════════════════════════════════════════════════════════════

KB: list[dict] = [
    {
        "id": "crm_mono", "name": "Creatine monohydrate",
        "aliases": ["creatine", "kreatin", "creatina", "créatine", "क्रिएटिन", "肌酸",
                    "creatina monoidrata", "creatina monohidrato", "creatine monohydrate"],
        "category": "supplement",
        "tags": ["strength", "muscle_gain", "power", "beginner", "creatine", "atp"],
        "summary": "The most extensively researched ergogenic aid. Increases phosphocreatine stores enabling faster ATP regeneration during high-intensity exercise.",
        "what_it_is": "Creatine monohydrate is an organic compound naturally produced in the liver and kidneys from amino acids arginine, glycine, and methionine. About 95% is stored in skeletal muscle as phosphocreatine. Supplementation saturates these stores, directly fuelling the ATP-PCr energy system during short, explosive efforts.",
        "dosage": "Loading (optional): 20 g/day split into 4 × 5 g doses for 5–7 days. Maintenance: 3–5 g/day. No-loading protocol: 3–5 g/day consistently (~3–4 weeks to full saturation).",
        "timing": "Post-workout slightly superior to pre-workout per meta-analyses. Consistency matters far more than exact timing — any time of day works.",
        "how_to_take": "Dissolve in 200–300 ml of water, juice, or protein shake. Monohydrate is tasteless and mixes easily. Taking with carbohydrates increases muscle uptake via insulin.",
        "hydration": "Increase fluid intake to 2.5–3.5 L/day. Creatine draws water into muscle cells — adequate hydration prevents cramps and supports performance.",
        "training_synergy": "Most effective with progressive-overload resistance training. Compound lifts (squat, deadlift, bench press) maximise creatine's ATP benefits. Also benefits HIIT.",
        "cycling": "No cycling required — long-term continuous use (5+ years) has been shown safe. No washout period needed.",
        "benefits": ["Strength increase 5–15%", "Power output improvement via PCr resynthesis", "Faster recovery between sets", "Lean mass support (muscle volumisation + synthesis)", "Cognitive performance support (emerging research)"],
        "side_effects": [{"effect": "Water retention (mild, intracellular — cosmetic only)", "severity": "low"}, {"effect": "GI discomfort if loading dose taken all at once", "severity": "medium"}],
        "stacking": ["Beta-alanine (complementary energy systems)", "Caffeine (minor antagonism — not clinically significant)", "Whey protein (muscle protein synthesis)"],
        "final_recommendation": "Pair 3–5 g creatine monohydrate with a post-workout carbohydrate + protein meal. Begin progressive overload training. Expect strength improvements in 2–4 weeks.",
        "evidence_tier": "very_high",
        "safe_for_beginners": True,
        "pubmed_ids": ["28615996", "11509496", "14636102"],
        "examine_url": "https://examine.com/supplements/creatine/",
        "research_refs": ["Buford et al. (2007) JISSN — ISSN Position Stand", "Rawson & Volek (2003) JSCR", "Lanhers et al. (2017) Eur J Sport Sci"],
        # Product data (for product intent)
        "products": [
            {"name": "Optimum Nutrition Creatine Monohydrate", "price_inr": 1599, "rating": 4.7, "category": "🏅 Premium", "key_benefit": "Micronised, mixes cleanly, Creapure certified"},
            {"name": "MuscleBlaze Creatine Monohydrate", "price_inr": 799, "rating": 4.5, "category": "🔥 Popular", "key_benefit": "Best value in India, lab-tested"},
            {"name": "AS-IT-IS Creatine Monohydrate", "price_inr": 649, "rating": 4.4, "category": "💪 Balanced", "key_benefit": "Unflavoured, 100% pure, budget pick"},
        ],
    },
    {
        "id": "crm_hcl", "name": "Creatine HCL",
        "aliases": ["creatine hcl", "creatine hydrochloride", "hcl creatine", "con-cret"],
        "category": "supplement",
        "tags": ["strength", "muscle_gain", "creatine"],
        "summary": "Higher-solubility creatine requiring a smaller dose (1–2 g). Less bloating reported. Smaller evidence base than monohydrate.",
        "what_it_is": "Creatine bound to hydrochloric acid. The HCL salt significantly increases water solubility compared to monohydrate, meaning effective doses are smaller and GI absorption may be faster.",
        "dosage": "1–2 g/day, no loading phase needed due to superior absorption kinetics.",
        "timing": "Pre or post-workout.",
        "how_to_take": "Mix in 150–200 ml water. Dissolves more readily than monohydrate.",
        "hydration": "2–3 L/day. Less water retention than monohydrate due to smaller dose.",
        "training_synergy": "Same as monohydrate — most effective with resistance training.",
        "cycling": "No cycling needed.",
        "benefits": ["Equivalent strength gains at lower dose", "Minimal bloating and GI issues", "Easy dissolution"],
        "side_effects": [{"effect": "Minimal GI issues", "severity": "low"}],
        "stacking": ["Citrulline malate", "Beta-alanine"],
        "final_recommendation": "Choose HCL if monohydrate causes GI discomfort. For most users monohydrate is the superior cost-effective choice.",
        "evidence_tier": "high",
        "safe_for_beginners": True,
        "pubmed_ids": ["19844003"],
        "examine_url": "https://examine.com/supplements/creatine/",
        "research_refs": ["Miller et al. (2009) J Int Soc Sports Nutr"],
        "products": [
            {"name": "Kaged Muscle C-HCl", "price_inr": 2999, "rating": 4.6, "category": "🏅 Premium", "key_benefit": "Patented HCL form, no loading"},
            {"name": "Con-Cret Creatine HCL", "price_inr": 2499, "rating": 4.4, "category": "💪 Balanced", "key_benefit": "Original HCL brand, concentrated"},
        ],
    },
    {
        "id": "beta_al", "name": "Beta-alanine",
        "aliases": ["beta alanine", "beta-alanine", "carnosine precursor", "beta alanina"],
        "category": "supplement",
        "tags": ["endurance", "strength", "fatigue", "pre_workout"],
        "summary": "Amino acid precursor to carnosine — buffers lactic acid in muscle, delaying fatigue. Most effective for exercise lasting 60–240 seconds.",
        "what_it_is": "Non-essential amino acid that combines with histidine in muscle tissue to form carnosine — a pH buffer that neutralises lactic acid during intense exercise. Raises muscle carnosine by 40–80% over 4–6 weeks.",
        "dosage": "3.2–6.4 g/day. Split into 1.6 g doses to reduce tingling (paresthesia).",
        "timing": "Pre-workout or evenly split throughout the day.",
        "how_to_take": "Capsules or powder. Sustained-release formulas reduce paresthesia.",
        "hydration": "2–3 L/day standard.",
        "training_synergy": "Ideal for high-rep resistance training, rowing, cycling, team sports. Synergises with creatine.",
        "cycling": "No cycling required. Benefits plateau after ~10 weeks — maintenance at 3.2 g/day thereafter.",
        "benefits": ["Delayed muscle fatigue and H+ accumulation", "Higher rep capacity before failure", "Endurance improvement in 1–4 minute efforts"],
        "side_effects": [{"effect": "Tingling / paresthesia — harmless, dose-dependent", "severity": "low"}],
        "stacking": ["Creatine monohydrate", "Caffeine", "L-Citrulline"],
        "final_recommendation": "Stack with creatine for comprehensive energy system coverage. Use split dosing.",
        "evidence_tier": "high",
        "safe_for_beginners": True,
        "pubmed_ids": ["22649228", "27797728"],
        "examine_url": "https://examine.com/supplements/beta-alanine/",
        "research_refs": ["Hobson et al. (2012) Amino Acids — 15-study meta-analysis"],
        "products": [
            {"name": "Bulk Supplements Beta-Alanine", "price_inr": 1899, "rating": 4.5, "category": "💪 Balanced", "key_benefit": "Pure powder, high dose per serving"},
        ],
    },
    {
        "id": "citrulline", "name": "L-Citrulline / Citrulline malate",
        "aliases": ["citrulline", "citrulline malate", "l-citrulline", "pump supplement", "no booster", "citrulina"],
        "category": "supplement",
        "tags": ["pump", "endurance", "blood_flow", "pre_workout", "nitric_oxide"],
        "summary": "Precursor to arginine → nitric oxide. Enhances blood flow, muscle pump, and endurance. Malate form also reduces fatigue.",
        "what_it_is": "L-citrulline is converted to arginine in the kidneys, then to nitric oxide — a potent vasodilator. Citrulline malate combines citrulline with malic acid for additional anti-fatigue effects.",
        "dosage": "L-citrulline: 6–8 g. Citrulline malate 2:1: 8 g. 30–60 min pre-workout.",
        "timing": "30–60 minutes pre-workout on an empty or light stomach.",
        "how_to_take": "Mix in 300–400 ml water. Slight tartness — juice improves palatability.",
        "hydration": "3+ L/day. Vasodilation increases sweating.",
        "training_synergy": "Best for volume training and metabolic conditioning. Excellent for hypertrophy days.",
        "cycling": "No cycling needed.",
        "benefits": ["Significant muscle pump via NO-mediated vasodilation", "Reduced muscle soreness 24–48 h post-training", "Endurance improvement 12–15%", "Blood pressure support"],
        "side_effects": [{"effect": "GI discomfort at doses above 10 g", "severity": "low"}],
        "stacking": ["Beta-alanine", "Caffeine", "Creatine"],
        "final_recommendation": "Use 8 g citrulline malate 2:1 pre-workout. Combine with beta-alanine and caffeine.",
        "evidence_tier": "high",
        "safe_for_beginners": True,
        "pubmed_ids": ["21414438", "26900386"],
        "examine_url": "https://examine.com/supplements/citrulline/",
        "research_refs": ["Pérez-Guisado & Jakeman (2010) JSCR", "Suzuki et al. (2016) Eur J Nutr"],
        "products": [
            {"name": "Bulk Supplements Citrulline Malate 2:1", "price_inr": 1699, "rating": 4.6, "category": "💪 Balanced", "key_benefit": "Pure 2:1 ratio, best pump formula"},
        ],
    },
    {
        "id": "whey", "name": "Whey protein",
        "aliases": ["whey", "whey protein", "proteina whey", "proteine whey", "proteína whey",
                    "व्हे प्रोटीन", "乳清蛋白", "protéine lactosérum", "molkenprotein",
                    "whey isolate", "whey concentrate"],
        "category": "supplement",
        "tags": ["muscle_gain", "recovery", "protein", "beginner"],
        "summary": "Fast-digesting milk protein with highest leucine content of any protein — optimal for post-workout muscle protein synthesis.",
        "what_it_is": "Whey is the liquid by-product of cheese production. Available as concentrate (70–80% protein), isolate (90%+, < 1% lactose), or hydrolysate (pre-digested). Richest natural source of leucine (10–11%) — primary trigger for muscle protein synthesis.",
        "dosage": "25–50 g per serving to reach total daily protein target of 1.6–2.2 g/kg bodyweight.",
        "timing": "Post-workout for peak MPS. Any time of day to supplement dietary protein deficit.",
        "how_to_take": "Shaker bottle with 200–300 ml water or milk. Add to oats, yogurt, or baking.",
        "hydration": "Protein metabolism increases urea production — maintain 2.5–3 L/day.",
        "training_synergy": "Consume within 2 hours post-resistance training. Combine with fast carbohydrates for insulin-mediated uptake.",
        "cycling": "No cycling. Use daily to hit protein targets.",
        "benefits": ["Maximises MPS via leucine content", "Fast digestion ideal post-workout", "Complete amino acid profile", "Cost-effective protein source"],
        "side_effects": [{"effect": "GI discomfort if lactose intolerant — use isolate", "severity": "medium"}],
        "stacking": ["Creatine", "Carbohydrates post-workout", "Casein before bed"],
        "final_recommendation": "Target total daily protein first (food + supplement). Post-workout whey + fast carbs optimises MPS and glycogen replenishment.",
        "evidence_tier": "very_high",
        "safe_for_beginners": True,
        "pubmed_ids": ["19589961", "25048790"],
        "examine_url": "https://examine.com/supplements/whey-protein/",
        "research_refs": ["Tang et al. (2009) Am J Clin Nutr", "Morton et al. (2018) BJSM"],
        "products": [
            {"name": "Optimum Nutrition Gold Standard Whey", "price_inr": 4499, "rating": 4.8, "category": "🏅 Premium", "key_benefit": "Industry benchmark, 24g protein/scoop"},
            {"name": "MuscleBlaze Whey Protein", "price_inr": 2999, "rating": 4.5, "category": "🔥 Popular", "key_benefit": "Best-selling in India, digestion enzymes"},
            {"name": "AS-IT-IS Whey Protein Concentrate", "price_inr": 1599, "rating": 4.3, "category": "💪 Balanced", "key_benefit": "Budget pick, unflavoured 80% protein"},
        ],
    },
    {
        "id": "caffeine", "name": "Caffeine",
        "aliases": ["caffeine", "caffeina", "caféine", "koffein", "कैफीन", "咖啡因", "caffeine anhydrous"],
        "category": "supplement",
        "tags": ["strength", "endurance", "fat_loss", "focus", "pre_workout", "energy"],
        "summary": "Adenosine receptor antagonist reducing perceived exertion. Increases power output, endurance, and fat oxidation.",
        "what_it_is": "Caffeine blocks adenosine receptors in the brain and peripheral tissue, reducing perceived effort and increasing catecholamine release. The most extensively studied ergogenic aid across 300+ clinical trials.",
        "dosage": "3–6 mg/kg bodyweight (200–400 mg for most adults). Higher doses don't provide additional benefit.",
        "timing": "30–60 minutes before training. Avoid within 6 hours of sleep.",
        "how_to_take": "Anhydrous caffeine pills for precise dosing. Combined with L-Theanine (2:1 ratio) for smooth focus.",
        "hydration": "Mild diuretic — increase water intake by 500 ml on caffeine days.",
        "training_synergy": "Effective across all modalities. Pre-workout 30–45 min before training.",
        "cycling": "Cycle off 1–2 weeks per month to reset adenosine receptor sensitivity.",
        "benefits": ["Power output +3–7%", "Endurance capacity improvement", "Fat oxidation / thermogenic effect", "Focus and alertness", "Reduced perceived effort"],
        "side_effects": [{"effect": "Tolerance buildup with daily use", "severity": "medium"}, {"effect": "Sleep disruption if dosed too late", "severity": "medium"}, {"effect": "Anxiety at high doses", "severity": "medium"}],
        "stacking": ["L-Theanine 200 mg (2:1)", "L-Citrulline", "Beta-alanine"],
        "final_recommendation": "Use 3–5 mg/kg bodyweight 30–60 min pre-workout with 200 mg L-Theanine. Cycle regularly.",
        "evidence_tier": "very_high",
        "safe_for_beginners": True,
        "pubmed_ids": ["34445894", "20019636"],
        "examine_url": "https://examine.com/supplements/caffeine/",
        "research_refs": ["Grgic et al. (2021) BJSM — 300-study meta-analysis"],
        "products": [
            {"name": "Optimum Nutrition Caffeine Caps 200mg", "price_inr": 999, "rating": 4.6, "category": "🔥 Popular", "key_benefit": "Precise dosing, cost-effective"},
            {"name": "Bulk Supplements Caffeine Anhydrous", "price_inr": 799, "rating": 4.4, "category": "💪 Balanced", "key_benefit": "Pure powder, dose as needed"},
        ],
    },
    {
        "id": "ostarine", "name": "Ostarine (MK-2866)",
        "aliases": ["ostarine", "mk2866", "mk-2866", "enobosarm", "mk 2866", "ostarina", "gtx-024"],
        "category": "sarm",
        "tags": ["muscle_gain", "fat_loss", "recomp", "sarm"],
        "summary": "Mildest SARM. Selective androgen receptor modulator with muscle and bone anabolic effects. Research chemical — not approved for human use.",
        "what_it_is": "Ostarine (GTx-024 / Enobosarm) is a nonsteroidal SARM originally developed for muscle-wasting diseases. Selectively binds androgen receptors in muscle and bone with minimal reproductive tissue activation. Produces lean mass gains without the full androgenic side-effect profile of testosterone.",
        "dosage": "10–25 mg/day. Start at 10 mg for first cycle to assess tolerance.",
        "timing": "Once daily, same time each day, with or without food.",
        "how_to_take": "Oral liquid or capsule. Measure carefully — liquid suspensions require a precise dosing syringe.",
        "hydration": "Standard 2.5–3 L/day.",
        "training_synergy": "Excellent for recomposition — muscle gain + fat loss simultaneously. Body recomposition nutrition protocols recommended.",
        "cycling": "8-week cycles standard. Bloodwork before and 4–6 weeks post-cycle. Mini PCT (Nolvadex 20 mg/day × 3 weeks) if suppression symptoms.",
        "benefits": ["Lean muscle gain 2–4 kg typical in 8 weeks", "Fat loss support during recomp", "Joint support and healing", "Lower suppression than steroids"],
        "side_effects": [{"effect": "Mild testosterone suppression — bloodwork required", "severity": "medium"}, {"effect": "Lipid changes (HDL reduction)", "severity": "medium"}, {"effect": "Mild liver enzyme elevation", "severity": "low"}],
        "stacking": ["Cardarine GW-501516 (fat loss)", "MK-677 Ibutamoren (GH + recovery)"],
        "final_recommendation": "Bloodwork baseline mandatory. Start at 10 mg, run 8 weeks, recheck bloodwork. Not for use without monitoring.",
        "evidence_tier": "moderate",
        "safe_for_beginners": True,
        "pubmed_ids": ["20814882", "23631853"],
        "examine_url": "https://examine.com/supplements/ostarine/",
        "research_refs": ["Dalton et al. (2011) Cancer Res", "Papanicolaou et al. (2013) J Gerontol"],
        "legal_status": "Research chemical — not approved for human use in any country. Banned by WADA.",
    },
    {
        "id": "lgd4033", "name": "LGD-4033 (Ligandrol)",
        "aliases": ["lgd4033", "lgd-4033", "ligandrol", "vk5211", "anabolicum", "lgd 4033"],
        "category": "sarm",
        "tags": ["muscle_gain", "strength", "bulking", "sarm"],
        "summary": "Most anabolic SARM. Strength and mass gains approaching low-dose testosterone. Significant suppression — full PCT required.",
        "what_it_is": "LGD-4033 is the most anabolic SARM discovered to date. Binds androgen receptors with high selectivity and affinity. Phase I clinical trial showed 1 mg/day produced significant lean mass gains. Causes meaningful testosterone suppression requiring structured PCT.",
        "dosage": "5–10 mg/day for 8–12 weeks.",
        "timing": "Once daily, same time each day.",
        "how_to_take": "Oral liquid or capsule.",
        "hydration": "3 L/day. Monitor for water retention.",
        "training_synergy": "Progressive overload resistance training. High protein diet (2+ g/kg).",
        "cycling": "8–12 week cycles. Full SERM PCT (Nolvadex 40/20/20/20 or Clomid 50/25/25/25) required.",
        "benefits": ["3–5 kg lean mass gains in 8–12 weeks", "Major strength increase", "Improved recovery and training capacity"],
        "side_effects": [{"effect": "Significant testosterone suppression", "severity": "high"}, {"effect": "HDL reduction — cardiovascular risk", "severity": "high"}, {"effect": "Liver enzyme elevation possible", "severity": "medium"}],
        "stacking": ["MK-677 Ibutamoren", "Cardarine GW-501516"],
        "final_recommendation": "Bloodwork mandatory. Not for beginners. Full SERM PCT required after every cycle.",
        "evidence_tier": "moderate",
        "safe_for_beginners": False,
        "pubmed_ids": ["24518353"],
        "examine_url": "https://examine.com/supplements/lgd-4033/",
        "research_refs": ["Basaria et al. (2013) Lancet — Phase I trial"],
        "legal_status": "Research chemical — not approved for human use. Banned by WADA.",
    },
    {
        "id": "rad140", "name": "RAD-140 (Testolone)",
        "aliases": ["rad140", "rad-140", "testolone", "rad 140"],
        "category": "sarm",
        "tags": ["muscle_gain", "strength", "fat_loss", "sarm"],
        "summary": "Most potent SARM. High anabolic:androgenic ratio. Significant suppression and hepatotoxicity risk. Not for beginners.",
        "what_it_is": "RAD-140 has the highest anabolic:androgenic ratio of any SARM. Developed by Radius Health for muscle wasting and breast cancer. Case reports of hepatotoxicity at doses used by athletes raise serious safety concerns.",
        "dosage": "5–15 mg/day for 8–10 weeks.",
        "timing": "Once daily.",
        "how_to_take": "Oral liquid or capsule.",
        "hydration": "3 L/day minimum.",
        "training_synergy": "Progressive overload resistance training essential.",
        "cycling": "8–10 week cycles. Full PCT mandatory.",
        "benefits": ["High anabolic potency", "Lean mass gains", "Fat loss support"],
        "side_effects": [{"effect": "Strong testosterone suppression", "severity": "high"}, {"effect": "Aggression / mood changes", "severity": "medium"}, {"effect": "Hepatotoxicity — liver damage in case reports", "severity": "high"}],
        "final_recommendation": "Bloodwork including liver function tests mandatory. Not recommended due to hepatotoxicity case reports.",
        "evidence_tier": "low",
        "safe_for_beginners": False,
        "pubmed_ids": ["20427478"],
        "examine_url": "https://examine.com/supplements/rad-140/",
        "legal_status": "Research chemical — not approved for human use. Banned by WADA.",
    },
    {
        "id": "mk677", "name": "MK-677 (Ibutamoren)",
        "aliases": ["mk677", "mk-677", "ibutamoren", "nutrobal", "gh secretagogue", "mk 677"],
        "category": "sarm",
        "tags": ["muscle_gain", "fat_loss", "recovery", "hgh", "sleep", "sarm"],
        "summary": "Oral GH secretagogue stimulating pituitary GH release. Non-suppressive. Improves sleep, lean mass, recovery. Not technically a SARM.",
        "what_it_is": "MK-677 (Ibutamoren) is an oral ghrelin receptor agonist that stimulates GH and IGF-1 release from the pituitary. Unlike SARMs it does not bind androgen receptors, causes no testosterone suppression, and requires no PCT. Often grouped with SARMs commercially.",
        "dosage": "10–25 mg/day, before bed.",
        "timing": "Before bed to align with natural overnight GH pulse.",
        "how_to_take": "Oral capsule or liquid.",
        "hydration": "3 L/day. Water retention common initially.",
        "training_synergy": "Resistance training amplifies lean mass effects. Fasted morning cardio amplifies fat loss.",
        "cycling": "12–24 week cycles. No PCT needed — non-suppressive.",
        "benefits": ["Elevated GH and IGF-1", "Improved sleep depth and quality", "Lean mass gain", "Recovery support"],
        "side_effects": [{"effect": "Increased appetite and water retention", "severity": "medium"}, {"effect": "Elevated fasting glucose — monitor in diabetics", "severity": "medium"}],
        "stacking": ["Ostarine (recomp)", "LGD-4033 (bulk)"],
        "final_recommendation": "Stack with Ostarine or LGD for synergistic lean mass results. Monitor IGF-1 and fasting glucose quarterly.",
        "evidence_tier": "moderate",
        "safe_for_beginners": True,
        "pubmed_ids": ["11149771"],
        "examine_url": "https://examine.com/supplements/mk-677/",
        "legal_status": "Research chemical — not approved for human use.",
    },
    {
        "id": "test_e", "name": "Testosterone enanthate",
        "aliases": ["testosterone enanthate", "test e", "testo e", "testosterone", "testosteron", "testosterona"],
        "category": "steroid",
        "tags": ["muscle_gain", "strength", "bulking", "testosterone", "steroid"],
        "summary": "Gold standard anabolic injectable. Long-ester testosterone with predictable pharmacokinetics and decades of clinical data.",
        "what_it_is": "Synthetic testosterone bound to an enanthate ester (7-carbon chain). Provides stable blood levels with twice-weekly injections. Decades of clinical pharmacokinetic and safety data. Most predictable anabolic compound available.",
        "dosage": "Beginner: 300–500 mg/week (split E3.5D). Intermediate: 500–750 mg/week.",
        "timing": "Injected subcutaneous or intramuscular every 3.5 days.",
        "how_to_take": "IM (glute, quads, delts) or SubQ. Rotate injection sites. 23–25G needle for injection.",
        "hydration": "2.5–3 L/day. Monitor blood pressure.",
        "training_synergy": "Progressive overload resistance training, high protein (2–2.4 g/kg), calorie surplus, adequate sleep.",
        "cycling": "12–16 week cycles. Anastrozole 0.25–0.5 mg E3D required. PCT: Nolvadex 40/40/20/20 mg begins 2 weeks after last injection.",
        "benefits": ["Significant lean mass and strength gains", "Improved recovery capacity", "Libido and well-being improvement"],
        "side_effects": [{"effect": "Complete testosterone suppression", "severity": "high"}, {"effect": "Aromatisation → estrogen management required", "severity": "medium"}, {"effect": "Cardiovascular strain (HDL reduction, LVH risk)", "severity": "high"}, {"effect": "Acne and hair loss (genetic)", "severity": "medium"}],
        "stacking": ["Anastrozole (AI)", "NPP or Deca (intermediate+)", "Anavar (cut)"],
        "final_recommendation": "Bloodwork mandatory before, mid-cycle, post-PCT. AI + liver support + cardiovascular monitoring non-negotiable.",
        "evidence_tier": "very_high",
        "safe_for_beginners": False,
        "pubmed_ids": ["8637536", "11502560"],
        "research_refs": ["Bhasin et al. (1996) NEJM — landmark dose-response", "Bhasin et al. (2001) NEJM"],
        "legal_status": "Schedule III controlled substance (USA). Prescription only in UK, India, Canada, Australia.",
    },
    {
        "id": "bpc157", "name": "BPC-157",
        "aliases": ["bpc157", "bpc-157", "body protection compound", "bpc 157"],
        "category": "peptide",
        "tags": ["recovery", "injury", "joint_health", "gut", "healing", "peptide"],
        "summary": "15-amino acid peptide from gastric juice with potent tendon, ligament, muscle, and gut healing properties.",
        "what_it_is": "BPC-157 (Body Protection Compound-157) is a synthetic 15-amino acid sequence derived from a protein in human gastric juice. Animal research demonstrates accelerated healing of tendons, ligaments, muscles, and intestinal tissue.",
        "dosage": "250–500 mcg/day subcutaneous or intramuscular.",
        "timing": "Near injury site (local) or systemic, once or twice daily.",
        "how_to_take": "Reconstitute lyophilised powder with bacteriostatic water. Insulin syringe (29–31G). Refrigerate after reconstitution.",
        "hydration": "2.5–3 L/day standard.",
        "training_synergy": "Active rehabilitation exercises during BPC-157 protocol maximise healing.",
        "cycling": "Acute injury: 4–6 weeks. Chronic: 8–12 weeks.",
        "benefits": ["Accelerated tendon and ligament healing", "Gut lining repair", "Anti-inflammatory effects", "Angiogenesis promotion"],
        "side_effects": [{"effect": "Injection site irritation (mild, transient)", "severity": "low"}],
        "stacking": ["TB-500 (systemic healing synergy)", "Ipamorelin/CJC-1295"],
        "final_recommendation": "Source quality is critical. Sterility is non-negotiable. Not a substitute for physiotherapy.",
        "evidence_tier": "moderate",
        "safe_for_beginners": True,
        "pubmed_ids": ["23439702"],
        "examine_url": "https://examine.com/supplements/bpc-157/",
        "legal_status": "Research chemical — not approved for human use.",
    },
    {
        "id": "hgh", "name": "Human Growth Hormone (HGH)",
        "aliases": ["hgh", "human growth hormone", "growth hormone", "gh", "somatropin", "rhgh", "生长激素", "hormona de crecimiento"],
        "category": "peptide",
        "tags": ["fat_loss", "muscle_gain", "recovery", "anti_aging", "hgh", "growth_hormone"],
        "summary": "Recombinant somatropin. Potent lipolytic and anabolic agent. Prescription only. Dramatically reduces visceral fat.",
        "what_it_is": "Recombinant human growth hormone (somatropin) is a 191-amino acid protein identical to endogenous GH. Stimulates IGF-1 production in the liver, which drives anabolic effects. GH itself is primarily lipolytic.",
        "dosage": "Anti-aging / fat loss: 1–3 IU/day. Bodybuilding: 4–8 IU/day (significantly higher risk).",
        "timing": "Sub-Q injection on waking (fat loss) or before bed (GH pulse alignment).",
        "how_to_take": "Sub-Q injection. Reconstitute with bacteriostatic water. Refrigerate at 2–8°C.",
        "hydration": "3+ L/day. Water retention common first 4–6 weeks.",
        "training_synergy": "Resistance training synergises with GH for lean mass. Fasted morning cardio amplifies fat loss.",
        "cycling": "Anti-aging: 6–12 month cycles. Bodybuilding: 16–24 weeks. Monitor IGF-1.",
        "benefits": ["Significant visceral fat reduction", "Lean mass retention and modest gain", "Connective tissue strengthening", "Improved sleep quality"],
        "side_effects": [{"effect": "Carpal tunnel syndrome (tingling hands)", "severity": "medium"}, {"effect": "Insulin resistance — monitor blood glucose", "severity": "high"}, {"effect": "Acromegaly risk at sustained high doses", "severity": "high"}],
        "final_recommendation": "Physician supervision mandatory. Monitor IGF-1, fasting glucose, HbA1c quarterly. Only pharmaceutical-grade.",
        "evidence_tier": "very_high",
        "safe_for_beginners": False,
        "pubmed_ids": ["2388534"],
        "research_refs": ["Rudman et al. (1990) NEJM — landmark study"],
        "legal_status": "Prescription only in all countries. Banned by WADA.",
    },
    {
        "id": "vitamin_d", "name": "Vitamin D3 + K2",
        "aliases": ["vitamin d", "vitamin d3", "cholecalciferol", "vit d", "vitamina d", "vitamine d", "विटामिन डी"],
        "category": "supplement",
        "tags": ["health", "testosterone", "immune", "bone", "recovery", "foundation"],
        "summary": "Essential fat-soluble vitamin-hormone. Deficiency affects 40%+ globally. Regulates testosterone synthesis, immune function, bone density.",
        "what_it_is": "Vitamin D3 (cholecalciferol) is a fat-soluble prohormone synthesised in skin on UV exposure. Functions as a hormone regulating 1,000+ genes. K2 (MK-7) required alongside D3 to direct calcium to bone.",
        "dosage": "Vitamin D3: 2,000–5,000 IU/day. K2 MK-7: 100–200 mcg/day.",
        "timing": "With largest fat-containing meal.",
        "how_to_take": "Softgel capsule or oil drops. D3 + K2 together in same meal.",
        "hydration": "Standard 2.5–3 L/day.",
        "training_synergy": "Adequate D3 supports testosterone production, muscle contraction efficiency, and injury prevention.",
        "cycling": "Year-round supplementation recommended.",
        "benefits": ["Testosterone support (+20% in deficient individuals)", "Immune system regulation", "Bone density", "Mood improvement"],
        "side_effects": [{"effect": "Toxicity only at >10,000 IU/day without monitoring", "severity": "low"}],
        "final_recommendation": "Test serum 25-OH-D. Target 40–70 ng/mL. Adjust dose accordingly. Daily with K2.",
        "evidence_tier": "very_high",
        "safe_for_beginners": True,
        "pubmed_ids": ["21154195"],
        "examine_url": "https://examine.com/supplements/vitamin-d/",
        "research_refs": ["Pilz et al. (2011) Horm Metab Res", "Holick (2007) NEJM"],
    },
    {
        "id": "omega3", "name": "Omega-3 fish oil (EPA + DHA)",
        "aliases": ["omega 3", "fish oil", "omega-3", "epa dha", "omega 3 fish oil", "aceite de pescado"],
        "category": "supplement",
        "tags": ["health", "recovery", "anti_inflammatory", "cardiovascular", "joint_health"],
        "summary": "EPA + DHA omega-3 fatty acids with powerful anti-inflammatory effects. Critical for cardiovascular health, especially for steroid users.",
        "what_it_is": "Long-chain omega-3 polyunsaturated fatty acids. EPA (eicosapentaenoic acid) and DHA (docosahexaenoic acid) reduce systemic inflammation, improve cardiovascular markers, support joint health and brain function.",
        "dosage": "3–6 g combined EPA + DHA per day (not total oil volume).",
        "timing": "With meals to reduce GI discomfort.",
        "how_to_take": "Softgel or liquid. Enteric-coated for those sensitive to fish aftertaste.",
        "hydration": "Standard 2.5–3 L/day.",
        "training_synergy": "Anti-inflammatory effects support recovery from intense training.",
        "cycling": "Daily, year-round.",
        "benefits": ["Systemic anti-inflammatory action", "Cardiovascular protection (HDL up, triglycerides down)", "Joint health", "Muscle protein synthesis support"],
        "side_effects": [{"effect": "Fish aftertaste/burping — take with meals", "severity": "low"}],
        "final_recommendation": "Choose EPA + DHA combined over total fish oil volume on label. Nordic Naturals or similar pharmaceutical-grade brands.",
        "evidence_tier": "very_high",
        "safe_for_beginners": True,
        "pubmed_ids": ["19589961"],
        "examine_url": "https://examine.com/supplements/fish-oil/",
    },
    {
        "id": "zinc_magnesium", "name": "Zinc & Magnesium (ZMA)",
        "aliases": ["zma", "zinc magnesium", "zinc", "magnesium", "mineral supplements", "magnesium glycinate", "zinc picolinate"],
        "category": "supplement",
        "tags": ["testosterone", "sleep", "recovery", "health", "foundation"],
        "summary": "Zinc supports testosterone synthesis and immune function. Magnesium improves sleep quality and reduces cortisol. Both commonly deficient in athletes.",
        "what_it_is": "ZMA combines zinc (testosterone synthesis, immune function) and magnesium (sleep architecture, cortisol regulation, 300+ enzymatic reactions). Athletes commonly deplete both through sweat.",
        "dosage": "Zinc: 25–45 mg/day. Magnesium: 300–500 mg glycinate or malate.",
        "timing": "Before bed on empty stomach.",
        "how_to_take": "Capsule form. Avoid taking zinc with food (competes with absorption).",
        "hydration": "Standard 2.5–3 L/day.",
        "training_synergy": "Adequate zinc and magnesium support testosterone production and sleep quality — both critical for training adaptation.",
        "cycling": "Daily, year-round.",
        "benefits": ["Testosterone support when deficient", "Sleep quality improvement", "Cortisol reduction", "Immune function"],
        "side_effects": [{"effect": "Nausea if zinc taken with food", "severity": "low"}],
        "final_recommendation": "Use magnesium glycinate (best bioavailability, fewest GI issues). Test serum zinc and magnesium if deficiency suspected.",
        "evidence_tier": "high",
        "safe_for_beginners": True,
        "pubmed_ids": ["10738264"],
        "examine_url": "https://examine.com/supplements/zma/",
    },
    {
        "id": "fat_burner_stack", "name": "Fat burner supplements",
        "aliases": ["fat burner", "fat burning supplement", "thermogenic", "fat loss supplement", "weight loss supplement"],
        "category": "supplement",
        "tags": ["fat_loss", "cutting", "thermogenic", "metabolism"],
        "summary": "Evidence-based fat loss supplements: Caffeine (thermogenic), L-Carnitine (fat transport), Green tea EGCG (synergistic), Yohimbine (alpha-2 antagonist).",
        "what_it_is": "Fat burners combine multiple compounds with different mechanisms: thermogenesis (caffeine, synephrine), fat transport (L-carnitine), lipolysis (yohimbine at alpha-2 receptors), and metabolic rate increase (EGCG + caffeine). Evidence quality varies significantly by ingredient.",
        "dosage": "Caffeine: 200 mg. L-Carnitine: 2–4 g. EGCG: 400 mg. Yohimbine: 2.5–20 mg (start low).",
        "timing": "Fasted state or pre-workout. Yohimbine specifically requires fasted state.",
        "how_to_take": "Capsule or powder form. Start at low doses and assess tolerance.",
        "hydration": "3+ L/day. Stimulants increase sweating.",
        "training_synergy": "Most effective with calorie deficit + resistance training to preserve muscle mass.",
        "cycling": "Cycle stimulant components 5 days on / 2 days off.",
        "benefits": ["Increased resting metabolic rate", "Enhanced fat oxidation", "Appetite suppression", "Energy boost for training in deficit"],
        "side_effects": [{"effect": "Anxiety and elevated heart rate", "severity": "medium"}, {"effect": "Yohimbine: severe anxiety in sensitive individuals", "severity": "high"}],
        "final_recommendation": "No fat burner supplements diet and calorie tracking. Use as adjunct to structured deficit — not a shortcut.",
        "evidence_tier": "moderate",
        "safe_for_beginners": True,
        "pubmed_ids": ["20019636"],
        "examine_url": "https://examine.com/supplements/fat-burners/",
        "products": [
            {"name": "Transparent Labs PhysiqueSeries Fat Burner", "price_inr": 3499, "rating": 4.5, "category": "🏅 Premium", "key_benefit": "Evidence-dosed, no proprietary blends"},
            {"name": "MuscleBlaze Fat Burner Pro", "price_inr": 1499, "rating": 4.3, "category": "🔥 Popular", "key_benefit": "Best-selling India fat burner"},
        ],
    },
]

# Build alias index
_ALIAS: dict[str, dict] = {}
for _it in KB:
    _ALIAS[_it["name"].lower()] = _it
    for _a in _it.get("aliases", []):
        _ALIAS[_a.lower()] = _it

# Build ID index
_ID_INDEX: dict[str, dict] = {item["id"]: item for item in KB}

# ═══════════════════════════════════════════════════════════════════════════
# CACHE
# ═══════════════════════════════════════════════════════════════════════════

def _init_cache() -> None:
    os.makedirs(os.path.dirname(CACHE_DB), exist_ok=True)
    with sqlite3.connect(CACHE_DB) as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS report_cache (
            cache_key   TEXT PRIMARY KEY,
            query       TEXT NOT NULL,
            report_json TEXT NOT NULL,
            source      TEXT DEFAULT 'kb',
            created_at  REAL NOT NULL
        )""")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_created ON report_cache(created_at)")

_init_cache()

def _cache_key(query: str, filters: list) -> str:
    # Filters are part of the cache key → different filter combo = different cache entry
    raw = json.dumps({"q": query.lower().strip(), "f": sorted(filters)}, sort_keys=True)
    return hashlib.sha256(raw.encode()).hexdigest()[:32]

def _cache_get(key: str) -> list | None:
    try:
        with _cache_lock, sqlite3.connect(CACHE_DB) as conn:
            row = conn.execute(
                "SELECT report_json, created_at FROM report_cache WHERE cache_key=?", (key,)
            ).fetchone()
        if not row:
            return None
        if (time.time() - row[1]) > CACHE_TTL_SEC:
            return None
        return json.loads(row[0])
    except Exception as e:
        print(f"[Cache GET] {e}")
        return None

def _cache_set(key: str, query: str, results: list, source: str = "ai") -> None:
    try:
        with _cache_lock, sqlite3.connect(CACHE_DB) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO report_cache(cache_key,query,report_json,source,created_at) VALUES (?,?,?,?,?)",
                (key, query, json.dumps(results), source, time.time())
            )
    except Exception as e:
        print(f"[Cache SET] {e}")

def _cache_stats() -> dict:
    try:
        with sqlite3.connect(CACHE_DB) as conn:
            total = conn.execute("SELECT COUNT(*) FROM report_cache").fetchone()[0]
            fresh = conn.execute(
                "SELECT COUNT(*) FROM report_cache WHERE created_at > ?",
                (time.time() - CACHE_TTL_SEC,)
            ).fetchone()[0]
        return {"total": total, "fresh": fresh}
    except Exception:
        return {}

# ═══════════════════════════════════════════════════════════════════════════
# STRICT RELEVANCE SCORING  (replaces the old _score_kb)
# ═══════════════════════════════════════════════════════════════════════════

TRUST_TIERS = {"pubmed": 5, "examine": 4, "nih": 4, "openfda": 3, "serp": 2, "scraped": 1}

def _score_strict(
    query: str,
    item: dict,
    allowed_ids: list[str],
    goal_modifiers: list[str],
    filters: list[str],
    intent: str,
) -> int:
    """
    Strict entity-locked scorer.

    Rules:
    1. If allowed_ids is non-empty and item.id NOT in it → score = 0 (hard exclude)
    2. Entity match bonus is large (100 pts) so entity-matched items always top
    3. Filter/goal modifier bonus re-ranks within the entity set
    4. Intent bonus for dosage/explain pulls most detailed item to top
    """
    iid   = item["id"]
    name  = item["name"].lower()
    itags = " ".join(item.get("tags", []))
    q     = query.lower()

    # ── HARD EXCLUDE (the core relevance fix) ─────────────────────────────
    if allowed_ids and iid not in allowed_ids:
        return 0

    s = 0

    # ── Entity match bonus ─────────────────────────────────────────────────
    if allowed_ids and iid in allowed_ids:
        s += 100  # dominant — guarantees entity members beat non-members

    # ── Query word match (within entity set) ──────────────────────────────
    aliases = " ".join(item.get("aliases", []))
    for word in re.split(r"[\s\W]+", q):
        if len(word) < 3:
            continue
        if word in name:    s += 8
        if word in aliases: s += 5
        if word in itags:   s += 3

    # ── Goal modifier boost (for filter re-ranking) ──────────────────────
    # This is deliberately large so filter clicks cause meaningful re-ordering
    for mod in goal_modifiers:
        if mod in itags:
            s += 50  # makes filter clicks dominant within entity set

    # ── Filter chips boost ────────────────────────────────────────────────
    for f in filters:
        if f in itags:
            s += 50

    # ── Evidence tier bonus ───────────────────────────────────────────────
    tier_bonus = {"very_high": 15, "high": 10, "moderate": 5, "low": 0}
    s += tier_bonus.get(item.get("evidence_tier", "moderate"), 5)

    # ── Intent-specific boosts ────────────────────────────────────────────
    # Push most info-rich item to top for dosage/research queries
    has_what   = bool(item.get("what_it_is"))
    has_dosage = bool(item.get("dosage"))
    has_refs   = bool(item.get("pubmed_ids"))
    if intent in ("dosage", "research"):
        if has_dosage: s += 10
        if has_refs:   s += 8
    if intent == "explain":
        if has_what:   s += 10
    if intent == "product":
        if item.get("products"): s += 20

    return s


def _apply_strict_filter(
    query: str,
    allowed_ids: list[str],
    goal_modifiers: list[str],
    filters: list[str],
    intent: str,
    limit: int = 4,
) -> list[dict]:
    """Score all KB items with strict entity filter and return top N."""
    scored = []
    for item in KB:
        sc = _score_strict(query, item, allowed_ids, goal_modifiers, filters, intent)
        if sc > 0:
            scored.append({**item, "_sc": sc})
    scored.sort(key=lambda x: x["_sc"], reverse=True)
    return [{k: v for k, v in r.items() if k != "_sc"} for r in scored[:limit]]

# ═══════════════════════════════════════════════════════════════════════════
# LIVE DATA RETRIEVAL
# ═══════════════════════════════════════════════════════════════════════════

def _pubmed_search(query: str, max_results: int = 5) -> list[dict]:
    try:
        params: dict[str, Any] = {
            "db": "pubmed", "term": f"{query} supplement exercise",
            "retmax": max_results, "retmode": "json", "sort": "relevance",
        }
        if PUBMED_API_KEY:
            params["api_key"] = PUBMED_API_KEY
        r = requests.get(PUBMED_SEARCH, params=params, timeout=8)
        if r.status_code != 200:
            return []
        ids = r.json().get("esearchresult", {}).get("idlist", [])
        if not ids:
            return []
        params2: dict[str, Any] = {"db": "pubmed", "id": ",".join(ids), "retmode": "json"}
        if PUBMED_API_KEY:
            params2["api_key"] = PUBMED_API_KEY
        r2 = requests.get(PUBMED_FETCH, params=params2, timeout=10)
        if r2.status_code != 200:
            return [{"id": pid, "source": "pubmed", "trust": 5,
                     "title": f"PubMed ID: {pid}", "url": f"https://pubmed.ncbi.nlm.nih.gov/{pid}/", "snippet": ""}
                    for pid in ids]
        articles = r2.json().get("result", {})
        refs = []
        for pid in ids:
            article = articles.get(pid, {})
            authors = article.get("authors", [])
            author_str = authors[0].get("name", "") + " et al." if authors else ""
            refs.append({
                "id": pid, "source": "pubmed", "trust": 5,
                "title": article.get("title", f"PubMed ID: {pid}"),
                "authors": author_str, "journal": article.get("fulljournalname", ""),
                "year": article.get("pubdate", "")[:4],
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pid}/",
                "snippet": f"{author_str} {article.get('pubdate','')}. {article.get('fulljournalname','')}.",
            })
        return refs
    except Exception as e:
        print(f"[PubMed] {e}")
        return []

def _examine_data(compound_name: str) -> dict | None:
    try:
        slug = compound_name.lower().replace(" ", "-").replace("(","").replace(")","")
        url = f"https://examine.com/supplements/{slug}/"
        r = requests.get(url, headers={"User-Agent": "FitSearchBot/2.0"}, timeout=8)
        if r.status_code != 200:
            return None
        sm = re.search(r'<meta[^>]*name="description"[^>]*content="([^"]{50,})"', r.text)
        summary = sm.group(1).strip()[:500] if sm else ""
        return {"source": "examine", "trust": 4, "url": url, "summary": summary, "snippet": summary[:200]}
    except Exception as e:
        print(f"[Examine] {e}")
        return None

def _openfda_safety(compound_name: str) -> list[dict]:
    try:
        r = requests.get(OPENFDA_URL, params={
            "search": f'patient.drug.medicinalproduct:"{compound_name}"', "limit": 3,
        }, timeout=6)
        if r.status_code != 200:
            return []
        results = r.json().get("results", [])
        return [{"source": "openfda", "trust": 3,
                 "reactions": [rx.get("reactionmeddrapt","") for rx in ev.get("patient",{}).get("reaction",[])[:3]],
                 "snippet": "FDA adverse event report",
                 } for ev in results[:3]]
    except Exception as e:
        print(f"[OpenFDA] {e}")
        return []

def _serp_search(query: str) -> list[dict]:
    if not SERP_API_KEY:
        return []
    try:
        r = requests.get("https://serpapi.com/search.json", params={
            "q": f"{query} site:examine.com OR site:pubmed.ncbi.nlm.nih.gov OR site:nih.gov",
            "api_key": SERP_API_KEY, "engine": "google", "num": 5, "hl": "en",
        }, timeout=8)
        if r.status_code != 200:
            return []
        return [{"source": "serp", "trust": 2, "title": res.get("title",""),
                 "url": res.get("link",""), "snippet": res.get("snippet","")}
                for res in r.json().get("organic_results", [])[:5]]
    except Exception as e:
        print(f"[SerpAPI] {e}")
        return []

def _retrieve_live_data(query: str, primary_entity: str | None) -> dict:
    search_term = primary_entity if primary_entity else query
    live: dict = {"pubmed": [], "examine": {}, "fda": [], "serp": []}
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
        f_pub  = ex.submit(_pubmed_search, search_term, 5)
        f_exam = ex.submit(_examine_data, search_term)
        f_fda  = ex.submit(_openfda_safety, search_term)
        f_serp = ex.submit(_serp_search, query)
        live["pubmed"]  = f_pub.result()
        live["examine"] = f_exam.result() or {}
        live["fda"]     = f_fda.result()
        live["serp"]    = f_serp.result()
    return live

def _filter_evidence(live: dict) -> dict:
    all_items = live.get("pubmed",[]) + live.get("serp",[]) + live.get("fda",[])
    if live.get("examine"):
        all_items.append(live["examine"])
    filtered = sorted([i for i in all_items if i.get("trust",0) >= 2],
                      key=lambda x: x.get("trust",0), reverse=True)
    return {
        "high_trust": [i for i in filtered if i.get("trust",0) >= 4],
        "pubmed_ids": [i["id"] for i in live.get("pubmed",[]) if "id" in i],
        "examine_url": live.get("examine",{}).get("url"),
        "examine_summary": live.get("examine",{}).get("summary",""),
        "fda_events": live.get("fda",[]),
    }

# ═══════════════════════════════════════════════════════════════════════════
# CLAUDE SYNTHESIS  — intent-specific structured output
# ═══════════════════════════════════════════════════════════════════════════

_SYSTEM_PROMPT = """You are FitSearch AI — a world-class evidence-based sports nutrition scientist and analyst.

Generate a structured report answering the user's query. The intent type determines the output format:

INTENT → FORMAT:
- research / explain / dosage / side_effects / cycle: → 10-section scientific report
- recommend: → ranked recommendation list with evidence scores
- compare: → side-by-side comparison table
- product: → structured product list with price/rating/category
- training: → day-wise plan or structured table

STRICT RULES:
1. Respond ONLY with valid JSON — no markdown, no prose outside JSON.
2. Respond in the SAME language as the user's query.
3. Only include results DIRECTLY related to the query entity.
4. safe_for_beginners must be false for all steroids and advanced SARMs.
5. Include real PubMed IDs in references.
6. evidence_tier: "very_high" | "high" | "moderate" | "low"
7. Include legal_status for controlled/research substances.

For research/explain/dosage/side_effects/cycle intent respond with:
{
  "detected_language": "English",
  "intent": "research",
  "name": "Primary compound name",
  "tagline": "One-sentence description",
  "category": "supplement | sarm | steroid | peptide | training | diet",
  "evidence_tier": "very_high",
  "safe_for_beginners": true,
  "legal_status": null,
  "sections": {
    "what_it_is": "2-4 sentences on mechanism and origin",
    "dosage": "Specific dosage with phases",
    "timing": "Optimal timing and rationale",
    "how_to_take": "Practical preparation tips",
    "hydration": "Fluid requirements",
    "training_synergy": "Training protocols that maximise effect",
    "cycling": "Cycling protocol or reason none needed",
    "benefits": ["benefit 1", "benefit 2"],
    "side_effects": [{"effect": "description", "severity": "low | medium | high"}],
    "references": [
      {"type": "pubmed", "id": "PMID", "title": "Study title", "url": "https://pubmed.ncbi.nlm.nih.gov/PMID/"},
      {"type": "examine", "url": "https://examine.com/supplements/x/", "title": "Examine.com"}
    ]
  },
  "stacking": ["compound 1"],
  "final_recommendation": "2-3 sentence actionable recommendation",
  "ai_note": "confidence level note"
}

For product intent respond with:
{
  "detected_language": "English",
  "intent": "product",
  "name": "Category name",
  "tagline": "One-sentence category description",
  "category": "supplement",
  "evidence_tier": "high",
  "safe_for_beginners": true,
  "legal_status": null,
  "products": [
    {
      "name": "Product Name",
      "price_inr": 1999,
      "rating": 4.5,
      "category_badge": "🔥 Popular | 💪 Balanced | 🏅 Premium",
      "key_benefit": "Main selling point",
      "protein_per_scoop": "25g",
      "servings": "30",
      "usage_tips": "When and how to use",
      "best_for": "goal this product is best suited for"
    }
  ],
  "sections": {
    "what_it_is": "Category overview",
    "dosage": "General dosage guidelines",
    "timing": "General timing guidelines",
    "how_to_take": "General usage tips",
    "hydration": "Hydration notes",
    "training_synergy": "Training synergy",
    "cycling": "No cycling needed",
    "benefits": ["benefit 1"],
    "side_effects": [{"effect": "description", "severity": "low"}],
    "references": []
  },
  "stacking": [],
  "final_recommendation": "Buying recommendation",
  "ai_note": "note"
}"""

def _call_claude(query: str, intent: str, entity_key: str | None, kb_items: list[dict], evidence: dict) -> dict | None:
    if not ANTHROPIC_API_KEY:
        return None
    pubmed_block = ""
    if evidence.get("pubmed_ids"):
        pubmed_block = "\n\nLIVE PUBMED:\n" + "\n".join(
            f"- PMID {pid}: https://pubmed.ncbi.nlm.nih.gov/{pid}/"
            for pid in evidence["pubmed_ids"][:5])
    examine_block = ""
    if evidence.get("examine_url"):
        examine_block = f"\n\nEXAMINE.COM: {evidence['examine_url']}\n{evidence.get('examine_summary','')[:300]}"
    kb_block = ""
    for item in kb_items[:2]:
        kb_block += f"\n\nKB ENTRY — {item['name']}:\n{json.dumps({k:v for k,v in item.items() if k not in ['aliases','id','_sc']}, ensure_ascii=False)[:1200]}"
    user_message = (
        f"Query: {query}\n"
        f"Intent: {intent}\n"
        f"Primary entity: {entity_key or 'general'}\n"
        f"{kb_block}{pubmed_block}{examine_block}"
    )
    try:
        resp = requests.post(
            ANTHROPIC_URL,
            headers={"x-api-key": ANTHROPIC_API_KEY, "anthropic-version": "2023-06-01", "content-type": "application/json"},
            json={"model": "claude-sonnet-4-20250514", "max_tokens": 3500, "system": _SYSTEM_PROMPT,
                  "messages": [{"role": "user", "content": user_message}]},
            timeout=30,
        )
        resp.raise_for_status()
        text = resp.json()["content"][0]["text"].strip()
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
        return json.loads(text)
    except Exception as e:
        print(f"[Claude] {e}")
        return None

# ═══════════════════════════════════════════════════════════════════════════
# REPORT ASSEMBLY
# ═══════════════════════════════════════════════════════════════════════════

def _kb_to_report(item: dict, evidence: dict, intent: str = "research") -> dict:
    secs = {
        "what_it_is":      item.get("what_it_is", item.get("summary", "")),
        "dosage":          item.get("dosage", "—"),
        "timing":          item.get("timing", "—"),
        "how_to_take":     item.get("how_to_take", "Mix with water or a protein shake."),
        "hydration":       item.get("hydration", "Maintain 2.5–3 L/day water intake."),
        "training_synergy":item.get("training_synergy", "Most effective with progressive-overload resistance training."),
        "cycling":         item.get("cycling", "No cycling required."),
        "benefits":        item.get("benefits", []),
        "side_effects":    item.get("side_effects", []),
        "references":      [],
    }
    # PubMed refs
    for pid in (evidence.get("pubmed_ids") or item.get("pubmed_ids", []))[:5]:
        secs["references"].append({"type": "pubmed", "id": pid, "title": f"PubMed ID: {pid}",
                                   "url": f"https://pubmed.ncbi.nlm.nih.gov/{pid}/"})
    # Static refs
    for ref in item.get("research_refs", []):
        secs["references"].append({"type": "journal", "id": None, "title": ref, "url": None})
    # Examine
    if item.get("examine_url") or evidence.get("examine_url"):
        exam = item.get("examine_url") or evidence.get("examine_url")
        secs["references"].append({"type": "examine", "id": None, "title": f"Examine.com — {item['name']}", "url": exam})
    return {
        "name":               item["name"],
        "tagline":            item.get("summary", "")[:120],
        "category":           item.get("category", "supplement"),
        "evidence_tier":      item.get("evidence_tier", "moderate"),
        "safe_for_beginners": item.get("safe_for_beginners", True),
        "legal_status":       item.get("legal_status"),
        "intent":             intent,
        "sections":           secs,
        "products":           item.get("products", []) if intent == "product" else [],
        "stacking":           item.get("stacking", []),
        "final_recommendation": item.get("final_recommendation", ""),
        "ai_note":            "Report from curated knowledge base. Set ANTHROPIC_API_KEY for AI-enhanced reports.",
        "_source":            "kb",
    }

def _claude_to_report(ai: dict, evidence: dict) -> dict:
    secs = ai.get("sections", {})
    for pid in evidence.get("pubmed_ids", []):
        if not any(r.get("id") == pid for r in secs.get("references", [])):
            secs.setdefault("references", []).append(
                {"type": "pubmed", "id": pid, "title": f"PubMed ID: {pid}",
                 "url": f"https://pubmed.ncbi.nlm.nih.gov/{pid}/"})
    if evidence.get("examine_url"):
        secs.setdefault("references", []).append(
            {"type": "examine", "id": None,
             "title": f"Examine.com — {ai.get('name','Supplement')}",
             "url": evidence["examine_url"]})
    return {
        "name":               ai.get("name", "Supplement"),
        "tagline":            ai.get("tagline", ""),
        "category":           ai.get("category", "supplement"),
        "evidence_tier":      ai.get("evidence_tier", "moderate"),
        "safe_for_beginners": ai.get("safe_for_beginners", True),
        "legal_status":       ai.get("legal_status"),
        "intent":             ai.get("intent", "research"),
        "sections":           secs,
        "products":           ai.get("products", []),
        "stacking":           ai.get("stacking", []),
        "final_recommendation": ai.get("final_recommendation", ""),
        "ai_note":            ai.get("ai_note", "AI-generated report."),
        "_source":            "ai",
    }

def _fallback_report(query: str, ts: str) -> dict:
    return {
        "name": f"Search: {query}", "tagline": "No exact match found.",
        "category": "supplement", "evidence_tier": "moderate",
        "safe_for_beginners": True, "legal_status": None, "intent": "general",
        "sections": {
            "what_it_is": (
                f"No specific results for '{query}'. "
                "Try: Creatine monohydrate, Whey protein, Beta-alanine, Ostarine, "
                "Testosterone enanthate, BPC-157, HGH, Caffeine, Vitamin D3."
            ),
            "dosage": "—", "timing": "—", "how_to_take": "—", "hydration": "—",
            "training_synergy": "—", "cycling": "—", "benefits": [], "side_effects": [],
            "references": [
                {"type": "examine", "url": "https://examine.com", "title": "Examine.com", "id": None},
                {"type": "pubmed", "url": "https://pubmed.ncbi.nlm.nih.gov", "title": "PubMed", "id": None},
            ],
        },
        "products": [], "stacking": [],
        "final_recommendation": "Refine your query with a specific supplement or compound name.",
        "ai_note": "No match found.", "_source": "fallback", "_timestamp": ts,
    }

# ═══════════════════════════════════════════════════════════════════════════
# PUBLIC INTERFACE
# ═══════════════════════════════════════════════════════════════════════════

def search_knowledge(query: str, filters: list | None = None) -> list[dict]:
    """
    Main entry point. Full multi-engine pipeline:
    Intent → Entity Extraction → Strict Filter → Cache → Live Retrieval →
    Trust Score → Claude → Cache Write → Structured Results

    FIX 1: Strict entity filtering — creatine query returns ONLY creatine items
    FIX 2: Filters are part of cache key → every filter combination re-ranks
    """
    filters = filters or []
    ts      = datetime.now(timezone.utc).isoformat()

    # 1. Intent classification
    intent = classify_intent(query)

    # 2. Entity extraction (strict)
    entity_key, allowed_ids = extract_primary_entity(query)

    # 3. Goal modifier extraction (for filter-based re-ranking)
    goal_modifiers = extract_goal_modifiers(query)
    # Also include explicit filter chips as goal modifiers
    goal_modifiers = list(set(goal_modifiers + filters))

    # 4. Cache lookup (includes filters in key — different filter = different result)
    ckey   = _cache_key(query, filters)
    cached = _cache_get(ckey)
    if cached:
        for r in cached:
            r["_cached"] = True
        return cached

    # 5. KB strict filtering + scoring
    kb_matches = _apply_strict_filter(query, allowed_ids, goal_modifiers, filters, intent, limit=5)

    # 6. Live data retrieval (parallel)
    live     = _retrieve_live_data(query, entity_key)
    evidence = _filter_evidence(live)

    # 7. Claude synthesis
    ai_data = _call_claude(query, intent, entity_key, kb_matches, evidence)

    results: list[dict] = []

    if ai_data and (ai_data.get("sections") or ai_data.get("products")):
        report = _claude_to_report(ai_data, evidence)
        report["_timestamp"] = ts
        results.append(report)
        # Supplementary KB items — ONLY from same entity group
        for item in kb_matches[1:3]:
            if item["name"].lower() != ai_data.get("name","").lower():
                r = _kb_to_report(item, {}, intent)
                r["_timestamp"] = ts
                r["_supplementary"] = True
                results.append(r)
    else:
        for item in kb_matches[:4]:
            r = _kb_to_report(item, evidence if not results else {}, intent)
            r["_timestamp"] = ts
            results.append(r)

    if not results:
        results = [_fallback_report(query, ts)]

    _cache_set(ckey, query, results, source="ai" if ai_data else "kb")
    return results


def get_recommendations(recent_queries: list[str], user: dict) -> list[dict]:
    """Personalised recs from history. No API calls."""
    goal  = (user.get("goal") or "muscle_gain").replace("-","_")
    level = user.get("experience_level") or "beginner"
    seen: set[str] = set()
    for q in recent_queries:
        _, allowed = extract_primary_entity(q)
        seen.update(allowed)
    recs = []
    for item in KB:
        if item["id"] in seen:
            continue
        sc = 0
        if goal in item.get("tags",[]): sc += 4
        if item.get("safe_for_beginners") and level == "beginner": sc += 3
        if not item.get("safe_for_beginners") and level in ("intermediate","advanced"): sc += 2
        if item["evidence_tier"] in ("very_high","high"): sc += 1
        if sc <= 1:
            continue
        parts = [f"Matches your {goal.replace('_',' ')} goal"]
        if level == "beginner" and item.get("safe_for_beginners"):
            parts.append("beginner-friendly")
        if item["evidence_tier"] in ("very_high","high"):
            parts.append("strong research support")
        recs.append({**item, "_sc": sc, "recommendation_reason": " · ".join(parts)})
    recs.sort(key=lambda x: x["_sc"], reverse=True)
    return [{k: v for k, v in r.items() if k != "_sc"} for r in recs[:6]]
