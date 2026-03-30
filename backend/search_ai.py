"""
search_ai.py  —  FitSearch AI  World-Class Research Engine  v4
===============================================================

Architecture:
  User Query → Intent Detection → Domain Routing → Entity Extraction
  → Cache Lookup → Knowledge Retrieval → Live Research Sources
  → AI Answer Generation → Rich Structured Output

Output always includes:
  What it is · How it works · Types/Forms · Dosage · Timing
  How to take · Side effects · Best ways to use · Who should use
  Who should avoid · Research evidence · Articles · Magazines · Books · Videos · AI Summary

Supported domains:
  Health · Fitness · Bodybuilding · Muscle Gain · Fat Loss · Strength
  Supplements · Vitamins · Nutrition · Diet · Recovery
  Anabolic Steroids · PEDs · HGH · Peptides · SARMs · Sports Performance
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

# ── Paths / constants ─────────────────────────────────────────────────────
BASE_DIR      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_DB      = os.path.join(BASE_DIR, "database", "search_cache.db")
ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
PUBMED_SEARCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
PUBMED_FETCH  = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
OPENFDA_URL   = "https://api.fda.gov/drug/event.json"
CACHE_TTL_SEC = 86_400          # 24 h
_cache_lock   = threading.Lock()

# ═══════════════════════════════════════════════════════════════════════════
# QUERY INTELLIGENCE — domain routing
# ═══════════════════════════════════════════════════════════════════════════

QUERY_DOMAINS: dict[str, list[str]] = {
    "muscle_gain":  ["muscle gain", "bulking", "hypertrophy", "build muscle", "lean mass"],
    "fat_loss":     ["fat loss", "cutting", "weight loss", "shred", "fat burning", "burn fat"],
    "strength":     ["strength", "powerlifting", "power", "strong", "1rm", "maximal strength"],
    "endurance":    ["endurance", "cardio", "stamina", "aerobic", "running", "cycling"],
    "recovery":     ["recovery", "healing", "injury", "soreness", "doms", "joint pain"],
    "supplements":  ["creatine", "whey", "protein", "pre workout", "bcaa", "amino acid",
                     "supplement", "beta alanine", "citrulline", "caffeine", "fish oil",
                     "vitamin", "zinc", "magnesium"],
    "steroids":     ["testosterone", "tren", "trenbolone", "anavar", "dbol", "dianabol",
                     "nandrolone", "deca", "winstrol", "steroid", "anabolic", "aas", "pct"],
    "peptides":     ["mk677", "bpc", "bpc-157", "ipamorelin", "cjc", "tb500", "tb-500",
                     "sermorelin", "ghrp", "peptide", "healing peptide"],
    "hgh":          ["hgh", "growth hormone", "somatropin", "human growth", "gh", "igf"],
    "sarms":        ["ostarine", "lgd", "ligandrol", "rad140", "testolone", "cardarine",
                     "sarm", "sarms", "selective androgen", "mk-2866"],
    "nutrition":    ["diet", "nutrition", "meal plan", "macros", "protein intake",
                     "carbs", "calories", "food", "eating", "keto"],
    "exercise":     ["exercise", "workout", "training", "gym", "lifting",
                     "sets", "reps", "program", "routine", "split", "exercises for"],
}

def detect_domain(query: str) -> str:
    q = query.lower()
    scores: dict[str, int] = {}
    for domain, keywords in QUERY_DOMAINS.items():
        sc = sum(1 for kw in keywords if kw in q)
        if sc > 0:
            scores[domain] = sc
    if not scores:
        return "supplements"
    return max(scores, key=lambda x: scores[x])



# ═══════════════════════════════════════════════════════════════════════════
# ENTITY GROUPS  ← the master fix for Issue 1
#
# Maps a canonical entity key → exhaustive list of KB item IDs that belong
# to that compound family.  _score_strict() uses this as a hard allow-list:
# items NOT in the list receive score 0, so they can NEVER appear in results.
# ═══════════════════════════════════════════════════════════════════════════

ENTITY_GROUPS: dict[str, list[str]] = {
    # Creatine family
    "creatine":       ["crm_mono", "crm_hcl"],
    # Individual creatine forms
    "creatine_mono":  ["crm_mono"],
    "creatine_hcl":   ["crm_hcl"],
    # Protein family
    "whey":           ["whey"],
    "protein":        ["whey"],          # generic "protein" → whey (most common)
    # Pre-workout ingredients
    "citrulline":     ["citrulline"],
    "beta_alanine":   ["beta_al"],
    "caffeine":       ["caffeine"],
    "pre_workout":    ["caffeine", "citrulline", "beta_al"],
    # SARMs family
    "sarm":           ["ostarine", "lgd4033", "rad140", "mk677"],
    "ostarine":       ["ostarine"],
    "lgd4033":        ["lgd4033"],
    "rad140":         ["rad140"],
    "mk677":          ["mk677"],
    # Steroids
    "steroid":        ["test_e", "anavar", "nandrolone"],
    "testosterone":   ["test_e"],
    "anavar":         ["anavar"],
    "nandrolone":     ["nandrolone"],
    # Peptides
    "peptide":        ["bpc157", "tb500", "ipamorelin", "sermorelin"],
    "bpc157":         ["bpc157"],
    "tb500":          ["tb500"],
    "ipamorelin":     ["ipamorelin"],
    "hgh":            ["hgh"],
    # Vitamins / minerals
    "vitamin_d":      ["vitamin_d"],
    "omega3":         ["omega3"],
    "zinc_magnesium": ["zinc_magnesium"],
    # Fat loss stack
    "fat_burner":     ["caffeine", "fat_burner_stack"],
}

# ── Longest-match entity trigger table ───────────────────────────────────
# Ordered longest-first so "creatine monohydrate" matches before "creatine".
ENTITY_TRIGGERS: list[tuple[str, str]] = sorted([
    # Creatine
    ("creatine monohydrate", "creatine_mono"),
    ("creatine hcl",         "creatine_hcl"),
    ("creatine hydrochloride","creatine_hcl"),
    ("kreatin",              "creatine"),
    ("creatina",             "creatine"),
    ("créatine",             "creatine"),
    ("क्रिएटिन",            "creatine"),
    ("肌酸",                 "creatine"),
    ("creatine",             "creatine"),
    # Whey / protein
    ("whey protein",         "whey"),
    ("whey isolate",         "whey"),
    ("whey concentrate",     "whey"),
    ("whey",                 "whey"),
    ("proteina whey",        "whey"),
    ("व्हे प्रोटीन",        "whey"),
    ("protein powder",       "protein"),
    # Pre-workout ingredients
    ("citrulline malate",    "citrulline"),
    ("l-citrulline",         "citrulline"),
    ("citrulline",           "citrulline"),
    ("beta-alanine",         "beta_alanine"),
    ("beta alanine",         "beta_alanine"),
    ("caffeine anhydrous",   "caffeine"),
    ("caffeine",             "caffeine"),
    ("pre-workout",          "pre_workout"),
    ("pre workout",          "pre_workout"),
    ("preworkout",           "pre_workout"),
    # SARMs
    ("ostarine",             "ostarine"),
    ("mk-2866",              "ostarine"),
    ("mk2866",               "ostarine"),
    ("enobosarm",            "ostarine"),
    ("lgd-4033",             "lgd4033"),
    ("lgd4033",              "lgd4033"),
    ("ligandrol",            "lgd4033"),
    ("rad-140",              "rad140"),
    ("rad140",               "rad140"),
    ("testolone",            "rad140"),
    ("mk-677",               "mk677"),
    ("mk677",                "mk677"),
    ("ibutamoren",           "mk677"),
    ("sarms",                "sarm"),
    ("sarm",                 "sarm"),
    # Steroids
    ("testosterone enanthate","testosterone"),
    ("test enanthate",       "testosterone"),
    ("test e",               "testosterone"),
    ("testosterone",         "testosterone"),
    ("testosteron",          "testosterone"),
    ("testosterona",         "testosterone"),
    ("oxandrolone",          "anavar"),
    ("anavar",               "anavar"),
    ("nandrolone decanoate", "nandrolone"),
    ("deca durabolin",       "nandrolone"),
    ("nandrolone",           "nandrolone"),
    ("steroids",             "steroid"),
    ("steroid",              "steroid"),
    # Peptides
    ("bpc-157",              "bpc157"),
    ("bpc157",               "bpc157"),
    ("body protection compound","bpc157"),
    ("tb-500",               "tb500"),
    ("tb500",                "tb500"),
    ("thymosin beta",        "tb500"),
    ("ipamorelin",           "ipamorelin"),
    ("cjc-1295",             "ipamorelin"),
    ("human growth hormone", "hgh"),
    ("growth hormone",       "hgh"),
    ("somatropin",           "hgh"),
    ("rhgh",                 "hgh"),
    ("hgh",                  "hgh"),
    ("peptides",             "peptide"),
    ("peptide",              "peptide"),
    # Vitamins
    ("vitamin d3",           "vitamin_d"),
    ("vitamin d",            "vitamin_d"),
    ("cholecalciferol",      "vitamin_d"),
    ("omega-3",              "omega3"),
    ("fish oil",             "omega3"),
    ("omega 3",              "omega3"),
    ("zma",                  "zinc_magnesium"),
    ("zinc magnesium",       "zinc_magnesium"),
    ("zinc",                 "zinc_magnesium"),
    # Fat loss
    ("fat burner",           "fat_burner"),
    ("fat burning",          "fat_burner"),
    ("thermogenic",          "fat_burner"),
], key=lambda t: len(t[0]), reverse=True)


def extract_primary_entity(query: str) -> tuple[str | None, list[str]]:
    """
    Returns (entity_key, allowed_kb_ids).
    Longest-match wins → "creatine monohydrate" → "creatine_mono" not just "creatine".
    Returns (None, []) when no specific entity is detected (general query).
    """
    q = query.lower()
    for phrase, key in ENTITY_TRIGGERS:
        if phrase in q:
            allowed = ENTITY_GROUPS.get(key, [])
            return key, allowed
    return None, []


# ═══════════════════════════════════════════════════════════════════════════
# INTENT CLASSIFICATION  ← ChatGPT-style query analysis
# ═══════════════════════════════════════════════════════════════════════════

# (trigger_words, intent_label) — first match wins; order matters
_INTENT_RULES: list[tuple[list[str], str]] = [
    # Product intent must come before generic 'best' / research
    (["best brand", "top brand", "buy india", "price india", "cheapest brand",
      "popular brand", "top 5 brands", "top 10 brands", "which brand",
      "best supplement india", "best whey india", "best creatine india",
      "recommend brand", "affordable", "value for money"], "product"),
    # Training / diet
    (["workout plan", "training plan", "training split", "exercise plan",
     "diet plan", "meal plan",
      "hypertrophy split", "push pull legs", "4 day split", "5 day split",
      "high protein diet", "macro plan", "calorie plan", "ppl split",
      "cutting diet", "bulking diet",
      "best exercises", "exercise for", "exercises for",
      "workout for", "fat loss workout", "muscle building workout"], "training"),
    # Dosage
    (["dosage", "dose", "how much", "how many mg", "how many grams",
      "mcg", "iu per day", "serving size", "intake amount",
      "loading phase", "maintenance dose"], "dosage"),
    # Side effects / safety
    (["side effect", "adverse effect", "risk", "dangerous", "harmful",
      "is it safe", "liver damage", "kidney", "toxicity",
      "health risk", "long term risk", "safe for"], "side_effects"),
    # Compare
    (["vs", "versus", "compare", "comparison", "better than",
      "difference between", "which is better", "which one",
      "monohydrate vs hcl", "ostarine vs lgd"], "compare"),
    # Cycle / protocol
    (["cycle", "protocol", "pct", "post cycle", "on cycle",
      "week cycle", "blast cruise", "stack protocol"], "cycle"),
    # Explain / what is
    (["what is", "what are", "how does", "explain",
      "define", "kya hai", "क्या है", "was ist",
      "qu'est-ce", "cos'è", "nedir", "qu'est"], "explain"),
    # Recommend
    (["best", "recommend", "should i", "beginner",
      "which one", "ideal for", "good for", "top choice",
      "for muscle gain", "for fat loss", "for strength",
      "for beginners", "starter supplement"], "recommend"),
]

def classify_intent(query: str) -> str:
    q = query.lower()
    for triggers, label in _INTENT_RULES:
        if any(t in q for t in triggers):
            return label
    return "research"


# ═══════════════════════════════════════════════════════════════════════════
# GOAL MODIFIER EXTRACTION  (for filter chip re-ranking)
# ═══════════════════════════════════════════════════════════════════════════

_GOAL_PHRASES: dict[str, list[str]] = {
    "muscle_gain":  ["muscle gain", "bulking", "mass gain", "hypertrophy",
                     "build muscle", "lean mass"],
    "fat_loss":     ["fat loss", "weight loss", "cutting", "shred",
                     "lean", "fat burning", "burn fat", "cut"],
    "strength":     ["strength", "powerlifting", "power", "strong",
                     "1rm", "maximal strength", "get stronger"],
    "endurance":    ["endurance", "cardio", "stamina", "aerobic",
                     "running", "cycling", "distance"],
    "recovery":     ["recovery", "healing", "injury", "soreness", "doms"],
    "beginner":     ["beginner", "starter", "new to", "first time",
                     "safe", "mild", "start with"],
    "advanced":     ["advanced", "experienced", "intermediate",
                     "heavy user", "serious athlete"],
}

def _extract_goal_modifiers(query: str) -> list[str]:
    q = query.lower()
    return [tag for tag, phrases in _GOAL_PHRASES.items()
            if any(p in q for p in phrases)]


# ═══════════════════════════════════════════════════════════════════════════
# LOCAL KNOWLEDGE BASE
# ═══════════════════════════════════════════════════════════════════════════

KB: list[dict] = [
    # ── Creatine monohydrate ──────────────────────────────────────────────
    {
        "id": "crm_mono", "name": "Creatine monohydrate",
        "aliases": ["creatine", "kreatin", "creatina", "créatine",
                    "क्रिएटिन", "肌酸", "creatine monohydrate"],
        "category": "supplement",
        "tags": ["strength", "muscle_gain", "power", "beginner", "creatine"],
        "summary": "The most extensively researched ergogenic aid. Increases phosphocreatine stores enabling faster ATP regeneration during high-intensity exercise.",
        "what_it_is": "Creatine monohydrate is an organic compound produced in the liver and kidneys from arginine, glycine, and methionine. ~95% is stored in skeletal muscle as phosphocreatine, directly fuelling the ATP-PCr energy system during explosive efforts.",
        "dosage": "Loading (optional): 20 g/day split into 4×5 g doses for 5–7 days. Maintenance: 3–5 g/day. No-loading: 3–5 g/day for ~3–4 weeks to reach saturation.",
        "timing": "Post-workout is marginally superior; consistency matters far more than timing — any time of day works.",
        "how_to_take": "Dissolve in 200–300 ml water, juice, or protein shake. Tasteless. Taking with carbohydrates improves uptake via insulin response.",
        "hydration": "2.5–3.5 L/day. Creatine draws water into muscle cells — adequate hydration prevents cramping.",
        "training_synergy": "Maximally effective with progressive-overload resistance training. Compound lifts (squat, deadlift, bench) and HIIT extract the most ATP benefit.",
        "cycling": "No cycling required. Long-term continuous use (5+ years) is well-documented as safe. No washout period needed.",
        "benefits": ["Strength increase 5–15%", "Power output improvement (PCr resynthesis)", "Faster inter-set recovery", "Lean mass support (volumisation + synthesis)", "Cognitive support (emerging research)"],
        "side_effects": [{"effect": "Mild water retention (intracellular — cosmetic only)", "severity": "low"}, {"effect": "GI discomfort if full loading dose taken at once", "severity": "medium"}],
        "how_it_works": "Creatine increases phosphocreatine (PCr) stores in muscles. During high-intensity exercise, PCr donates a phosphate group to ADP to rapidly regenerate ATP. More PCr = more ATP = more reps, heavier lifts, faster sprints.",
        "types": [
            {"name": "Creatine Monohydrate", "best_for": "Muscle gain, strength, overall performance", "evidence": "Very High", "note": "Most studied, most cost-effective"},
            {"name": "Creatine HCL", "best_for": "GI sensitivity, no bloating", "evidence": "High", "note": "Smaller dose needed"},
            {"name": "Buffered Creatine (Kre-Alkalyn)", "best_for": "Reduced bloating", "evidence": "Moderate", "note": "pH-buffered, comparable to monohydrate"},
        ],
        "best_ways_to_use": [
            "Take daily — consistency is more important than exact timing",
            "Combine with resistance training for maximum ATP benefit",
            "Stay hydrated (3+ L/day)",
            "Pair with post-workout carbs + protein for optimal uptake",
            "Loading phase optional — skip if GI sensitive",
        ],
        "who_should_use": ["Bodybuilders and powerlifters", "Athletes in explosive sports", "Beginners wanting faster strength gains", "Vegetarians/vegans (lower dietary creatine)"],
        "who_should_avoid": ["Individuals with kidney disease (consult physician)", "Anyone with creatine metabolism disorders"],
        "research_evidence": [
            {"study": "ISSN Position Stand (Buford et al. 2007)", "finding": "Creatine is the most effective ergogenic supplement for increasing high-intensity exercise capacity and lean body mass", "year": "2007"},
            {"study": "Rawson & Volek (2003) JSCR", "finding": "Short-term creatine supplementation increases strength and endurance by 5–15%", "year": "2003"},
        ],
        "articles": [
            {"title": "Creatine Supplementation and Exercise Performance", "author": "Jose Antonio PhD", "source": "J Int Soc Sports Nutr", "url": "https://pubmed.ncbi.nlm.nih.gov/28615996/"},
        ],
        "magazines": [
            {"title": "The Complete Creatine Guide", "publisher": "Muscle & Fitness", "url": "https://www.muscleandfitness.com"},
            {"title": "Creatine: Everything You Need to Know", "publisher": "Men's Health", "url": "https://www.menshealth.com"},
        ],
        "books": [
            {"title": "Sports Nutrition Handbook", "author": "Luc van Loon", "note": "Comprehensive coverage of creatine mechanisms"},
        ],
        "videos": [
            {"title": "Creatine: Everything You Need To Know", "channel": "Jeff Nippard", "platform": "YouTube", "url": "https://www.youtube.com/results?search_query=creatine+explained+jeff+nippard"},
            {"title": "The Science of Creatine", "channel": "Andrew Huberman", "platform": "YouTube", "url": "https://www.youtube.com/results?search_query=huberman+creatine+science"},
        ],
        "ai_summary": "Creatine Monohydrate is the single most effective and best-researched supplement for muscle gain, strength, and performance. With 200+ studies confirming its safety and efficacy, 3–5 g daily is safe, effective, and sustainable long-term.",
        "stacking": ["Beta-alanine (complementary energy systems)", "Caffeine", "Whey protein"],
        "final_recommendation": "Take 3–5 g creatine monohydrate daily with a post-workout carb + protein meal. Loading phase optional. Expect strength gains in 2–4 weeks.",
        "evidence_tier": "very_high", "safe_for_beginners": True,
        "pubmed_ids": ["28615996", "11509496", "14636102"],
        "examine_url": "https://examine.com/supplements/creatine/",
        "research_refs": ["Buford et al. (2007) JISSN — ISSN Position Stand", "Rawson & Volek (2003) JSCR", "Lanhers et al. (2017) Eur J Sport Sci"],
        "products": [
            {"name": "Optimum Nutrition Micronised Creatine", "price_inr": 1499, "rating": 4.7, "badge": "🏅 Premium", "best_for": "All users — industry benchmark"},
            {"name": "MuscleBlaze Creatine Monohydrate", "price_inr": 749,  "rating": 4.5, "badge": "🔥 Popular", "best_for": "Best value in India"},
            {"name": "AS-IT-IS Creatine Monohydrate",    "price_inr": 599,  "rating": 4.4, "badge": "💪 Balanced", "best_for": "Budget, 100% pure unflavoured"},
        ],
    },
    # ── Creatine HCL ─────────────────────────────────────────────────────
    {
        "id": "crm_hcl", "name": "Creatine HCL",
        "aliases": ["creatine hcl", "creatine hydrochloride", "hcl creatine", "con-cret"],
        "category": "supplement",
        "tags": ["strength", "muscle_gain", "creatine"],
        "summary": "Higher-solubility creatine form. Effective at 1–2 g/day. Less bloating than monohydrate. Smaller clinical evidence base.",
        "what_it_is": "Creatine bonded to hydrochloric acid, dramatically increasing water solubility. Smaller effective doses (1–2 g vs 3–5 g) mean less gastrointestinal load.",
        "dosage": "1–2 g/day. No loading phase needed.",
        "timing": "Pre or post-workout.",
        "how_to_take": "Mix in 150–200 ml water. Dissolves faster than monohydrate.",
        "hydration": "2–3 L/day. Less water retention than monohydrate.",
        "training_synergy": "Identical mechanism to monohydrate — maximised by resistance training.",
        "cycling": "No cycling needed.",
        "benefits": ["Equivalent strength gains at lower dose", "Minimal bloating", "Superior dissolution"],
        "side_effects": [{"effect": "Minimal GI issues", "severity": "low"}],
        "stacking": ["Citrulline malate", "Beta-alanine"],
        "final_recommendation": "Choose HCL if monohydrate causes bloating or GI issues. Monohydrate remains the better-evidenced and more cost-effective option for most.",
        "evidence_tier": "high", "safe_for_beginners": True,
        "pubmed_ids": ["19844003"],
        "examine_url": "https://examine.com/supplements/creatine/",
        "research_refs": ["Miller et al. (2009) J Int Soc Sports Nutr"],
        "products": [
            {"name": "Kaged Muscle C-HCl", "price_inr": 2999, "rating": 4.6, "badge": "🏅 Premium", "best_for": "Sensitive stomachs, no bloat"},
            {"name": "Con-Cret Creatine HCl", "price_inr": 2299, "rating": 4.3, "badge": "💪 Balanced", "best_for": "Original HCL brand"},
        ],
    },
    # ── Beta-alanine ──────────────────────────────────────────────────────
    {
        "id": "beta_al", "name": "Beta-alanine",
        "aliases": ["beta alanine", "beta-alanine", "carnosine precursor", "beta alanina"],
        "category": "supplement",
        "tags": ["endurance", "strength", "pre_workout", "fatigue"],
        "summary": "Amino acid precursor to carnosine — buffers lactic acid in muscle, delaying fatigue. Most effective for sustained high-intensity efforts lasting 60–240 s.",
        "what_it_is": "Non-essential amino acid that pairs with histidine to form carnosine in muscle, acting as a pH buffer against lactic acid. Supplementation raises muscle carnosine 40–80% over 4–6 weeks.",
        "dosage": "3.2–6.4 g/day. Split into 1.6 g doses to reduce tingling (paresthesia).",
        "timing": "Pre-workout or spread throughout the day. Tingling peaks 30–60 min post-dose — harmless.",
        "how_to_take": "Powder or capsule. SR formulas reduce tingling.",
        "hydration": "2–3 L/day standard.",
        "training_synergy": "Ideal for high-rep resistance, rowing, cycling, team sports. Synergises with creatine: creatine covers <10 s, beta-alanine covers 60–240 s.",
        "cycling": "No cycling. Benefits plateau ~10 weeks at full dose; maintain at 3.2 g/day.",
        "benefits": ["Delayed muscle fatigue and H⁺ accumulation", "Higher rep capacity before failure", "Endurance in 1–4 min efforts"],
        "side_effects": [{"effect": "Tingling / paresthesia — harmless, dose-dependent", "severity": "low"}],
        "stacking": ["Creatine monohydrate", "Caffeine", "L-Citrulline"],
        "final_recommendation": "Stack with creatine for comprehensive energy system coverage. Split dose to eliminate tingling.",
        "evidence_tier": "high", "safe_for_beginners": True,
        "pubmed_ids": ["22649228", "27797728"],
        "examine_url": "https://examine.com/supplements/beta-alanine/",
        "research_refs": ["Hobson et al. (2012) Amino Acids — 15-study meta-analysis"],
    },
    # ── L-Citrulline ──────────────────────────────────────────────────────
    {
        "id": "citrulline", "name": "L-Citrulline / Citrulline malate",
        "aliases": ["citrulline", "citrulline malate", "l-citrulline",
                    "pump supplement", "no booster", "citrulina"],
        "category": "supplement",
        "tags": ["pump", "endurance", "blood_flow", "pre_workout", "nitric_oxide"],
        "summary": "Converts to arginine → nitric oxide → vasodilation and muscle pump. Malate form also reduces fatigue via Krebs cycle.",
        "what_it_is": "L-citrulline is converted to arginine in kidneys, then to nitric oxide — a potent vasodilator. Citrulline malate adds malic acid (Krebs cycle) for anti-fatigue synergy.",
        "dosage": "L-citrulline: 6–8 g. Citrulline malate 2:1: 8 g. Take 30–60 min pre-workout.",
        "timing": "30–60 min pre-workout, light stomach.",
        "how_to_take": "Mix 300–400 ml water. Slight tartness — juice helps.",
        "hydration": "3+ L/day. Vasodilation increases sweating.",
        "training_synergy": "Best for volume / hypertrophy days. Excellent for pump-focused training.",
        "cycling": "No cycling needed.",
        "benefits": ["Significant muscle pump (NO vasodilation)", "Reduced DOMS 24–48 h", "Endurance +12–15%", "Blood pressure support"],
        "side_effects": [{"effect": "GI discomfort at doses >10 g", "severity": "low"}],
        "stacking": ["Beta-alanine", "Caffeine", "Creatine"],
        "final_recommendation": "Use 8 g citrulline malate 2:1 pre-workout with beta-alanine and caffeine for a complete evidence-based pre-workout.",
        "evidence_tier": "high", "safe_for_beginners": True,
        "pubmed_ids": ["21414438", "26900386"],
        "examine_url": "https://examine.com/supplements/citrulline/",
        "research_refs": ["Pérez-Guisado & Jakeman (2010) JSCR", "Suzuki et al. (2016) Eur J Nutr"],
    },
    # ── Whey protein ─────────────────────────────────────────────────────
    {
        "id": "whey", "name": "Whey protein",
        "aliases": ["whey", "whey protein", "proteina whey",
                    "proteine whey", "proteína whey",
                    "व्हे प्रोटीन", "乳清蛋白", "molkenprotein"],
        "category": "supplement",
        "tags": ["muscle_gain", "recovery", "protein", "beginner"],
        "summary": "Fast-digesting milk protein with highest leucine content of any protein source — optimal for post-workout muscle protein synthesis.",
        "what_it_is": "Whey is a by-product of cheese production. Available as concentrate (70–80% protein), isolate (90%+, <1% lactose), or hydrolysate. Richest source of leucine (10–11%) — the primary MPS trigger.",
        "dosage": "25–50 g per serving to reach daily target: 1.6–2.2 g protein/kg bodyweight.",
        "timing": "Post-workout for peak MPS. Any time to supplement dietary protein deficit.",
        "how_to_take": "Shaker bottle with 200–300 ml water or milk. Isolate mixes cleaner.",
        "hydration": "2.5–3 L/day — protein metabolism increases urea production.",
        "training_synergy": "Within 2 h post-resistance training + fast carbs (banana, white rice) for insulin-driven uptake.",
        "cycling": "No cycling. Daily use to hit protein targets.",
        "benefits": ["Maximises MPS via leucine content", "Fast digestion ideal post-workout", "Complete amino acid profile", "Cost-effective protein source"],
        "side_effects": [{"effect": "GI discomfort if lactose intolerant — use isolate", "severity": "medium"}, {"effect": "Kidney concern only in existing kidney disease", "severity": "low"}],
        "stacking": ["Creatine", "Fast carbs post-workout", "Casein before bed"],
        "final_recommendation": "Hit total daily protein via food first; supplement shortfall with whey. Post-workout whey + fast carbs optimises MPS and glycogen replenishment.",
        "evidence_tier": "very_high", "safe_for_beginners": True,
        "pubmed_ids": ["19589961", "25048790"],
        "examine_url": "https://examine.com/supplements/whey-protein/",
        "research_refs": ["Tang et al. (2009) Am J Clin Nutr", "Morton et al. (2018) BJSM — meta-analysis"],
        "products": [
            {"name": "ON Gold Standard Whey",      "price_inr": 4499, "rating": 4.8, "badge": "🏅 Premium", "best_for": "Industry benchmark, 24 g protein/scoop"},
            {"name": "MuscleBlaze Whey Protein",   "price_inr": 2999, "rating": 4.5, "badge": "🔥 Popular", "best_for": "Best-seller India, digestion enzymes"},
            {"name": "AS-IT-IS Whey Concentrate",  "price_inr": 1499, "rating": 4.3, "badge": "💪 Balanced", "best_for": "Budget, 80% protein, unflavoured"},
        ],
    },
    # ── Caffeine ──────────────────────────────────────────────────────────
    {
        "id": "caffeine", "name": "Caffeine",
        "aliases": ["caffeine", "caffeina", "caféine", "koffein",
                    "कैफीन", "咖啡因", "caffeine anhydrous"],
        "category": "supplement",
        "tags": ["strength", "endurance", "fat_loss", "focus",
                 "pre_workout", "energy"],
        "summary": "Most-studied ergogenic aid. Blocks adenosine receptors to reduce perceived exertion, boost power output, and enhance fat oxidation.",
        "what_it_is": "Caffeine is an adenosine receptor antagonist reducing perceived effort and increasing catecholamine release. Effective across endurance, strength, and power sports in over 300 clinical trials.",
        "dosage": "3–6 mg/kg bodyweight (200–400 mg for most adults). Higher doses add side effects without additional ergogenic benefit.",
        "timing": "30–60 min pre-workout. Half-life ~5–6 h — avoid within 6 h of sleep.",
        "how_to_take": "Anhydrous pills for precise dosing. Stack with L-Theanine 200 mg (2:1 ratio) for smooth focus.",
        "hydration": "Mild diuretic — add 500 ml extra water on caffeine days.",
        "training_synergy": "Universal ergogenic — effective for resistance training, cardio, HIIT, team sports. 30 min pre-workout.",
        "cycling": "Cycle off 1–2 weeks/month to reset adenosine receptor sensitivity. Tolerance builds within 2 weeks of daily use.",
        "benefits": ["Power output +3–7%", "Endurance improvement", "Fat oxidation / thermogenic", "Focus and alertness", "Reduced perceived effort"],
        "side_effects": [{"effect": "Tolerance with daily use", "severity": "medium"}, {"effect": "Sleep disruption if dosed too late", "severity": "medium"}, {"effect": "Anxiety / elevated HR at high doses", "severity": "medium"}],
        "stacking": ["L-Theanine 200 mg (2:1)", "L-Citrulline", "Beta-alanine"],
        "final_recommendation": "3–5 mg/kg pre-workout with 200 mg L-Theanine. Cycle 5 on / 2 off or 1 week off per month.",
        "evidence_tier": "very_high", "safe_for_beginners": True,
        "pubmed_ids": ["34445894", "20019636"],
        "examine_url": "https://examine.com/supplements/caffeine/",
        "research_refs": ["Grgic et al. (2021) BJSM — 300-study meta-analysis"],
    },
    # ── Ostarine ─────────────────────────────────────────────────────────
    {
        "id": "ostarine", "name": "Ostarine (MK-2866)",
        "aliases": ["ostarine", "mk2866", "mk-2866", "enobosarm",
                    "mk 2866", "ostarina", "gtx-024"],
        "category": "sarm",
        "tags": ["muscle_gain", "fat_loss", "recomp", "sarm", "beginner"],
        "summary": "Mildest, most-studied SARM. Selective androgen receptor modulator. Lean mass gains with lower suppression than steroids. Research chemical — not approved for human use.",
        "what_it_is": "Nonsteroidal SARM originally developed by GTx for muscle-wasting diseases. Selectively binds androgen receptors in muscle and bone with minimal reproductive tissue activation.",
        "dosage": "10–25 mg/day. Start at 10 mg first cycle to assess tolerance.",
        "timing": "Once daily, consistent time, with or without food.",
        "how_to_take": "Oral liquid or capsule. Use precise dosing syringe for liquid.",
        "hydration": "2.5–3 L/day standard.",
        "training_synergy": "Excellent for recomposition — simultaneous muscle gain + fat loss. Recomp nutrition (maintenance calories) works well.",
        "cycling": "8-week cycles. Bloodwork before and 4–6 weeks post-cycle. Mini PCT (Nolvadex 20 mg/day × 3 weeks) if suppression symptoms.",
        "benefits": ["2–4 kg lean mass gain in 8 weeks", "Fat loss support", "Joint healing", "Lower suppression vs steroids"],
        "side_effects": [{"effect": "Mild testosterone suppression — bloodwork required", "severity": "medium"}, {"effect": "HDL reduction", "severity": "medium"}, {"effect": "Mild liver enzyme elevation", "severity": "low"}],
        "stacking": ["Cardarine GW-501516 (fat loss)", "MK-677 Ibutamoren (GH + recovery)"],
        "final_recommendation": "Bloodwork baseline mandatory. Start 10 mg, run 8 weeks, recheck bloodwork. Do not use without monitoring access.",
        "evidence_tier": "moderate", "safe_for_beginners": True,
        "pubmed_ids": ["20814882", "23631853"],
        "examine_url": "https://examine.com/supplements/ostarine/",
        "research_refs": ["Dalton et al. (2011) Cancer Res", "Papanicolaou et al. (2013) J Gerontol"],
        "legal_status": "Research chemical — not approved for human use. Banned by WADA.",
    },
    # ── LGD-4033 ─────────────────────────────────────────────────────────
    {
        "id": "lgd4033", "name": "LGD-4033 (Ligandrol)",
        "aliases": ["lgd4033", "lgd-4033", "ligandrol", "vk5211", "lgd 4033"],
        "category": "sarm",
        "tags": ["muscle_gain", "strength", "bulking", "sarm"],
        "summary": "Most anabolic SARM. Strength and mass gains approaching low-dose testosterone. Significant suppression — full PCT required. Not for beginners.",
        "what_it_is": "LGD-4033 is the most potent SARM to date. Phase I trial showed significant lean mass at 1 mg/day. Causes meaningful testosterone suppression requiring full SERM PCT.",
        "dosage": "5–10 mg/day for 8–12 weeks.",
        "timing": "Once daily.",
        "how_to_take": "Oral liquid or capsule.",
        "hydration": "3 L/day; monitor water retention.",
        "training_synergy": "Progressive overload, high protein (2+ g/kg), calorie surplus for mass.",
        "cycling": "8–12 week cycles. Full PCT: Nolvadex 40/20/20/20 or Clomid 50/25/25/25.",
        "benefits": ["3–5 kg lean mass in 8–12 weeks", "Major strength gains", "Improved recovery capacity"],
        "side_effects": [{"effect": "Significant testosterone suppression", "severity": "high"}, {"effect": "HDL reduction — cardiovascular risk", "severity": "high"}, {"effect": "Liver enzyme elevation possible", "severity": "medium"}],
        "stacking": ["MK-677 Ibutamoren", "Cardarine GW-501516"],
        "final_recommendation": "Bloodwork mandatory. Not for beginners. Full SERM PCT required after every cycle.",
        "evidence_tier": "moderate", "safe_for_beginners": False,
        "pubmed_ids": ["24518353"],
        "examine_url": "https://examine.com/supplements/lgd-4033/",
        "research_refs": ["Basaria et al. (2013) Lancet — Phase I trial"],
        "legal_status": "Research chemical — not approved for human use. Banned by WADA.",
    },
    # ── RAD-140 ───────────────────────────────────────────────────────────
    {
        "id": "rad140", "name": "RAD-140 (Testolone)",
        "aliases": ["rad140", "rad-140", "testolone", "rad 140"],
        "category": "sarm",
        "tags": ["muscle_gain", "strength", "fat_loss", "sarm"],
        "summary": "Most potent SARM. Highest anabolic:androgenic ratio. Hepatotoxicity and strong suppression reported. Not for beginners.",
        "what_it_is": "RAD-140 has the highest anabolic:androgenic ratio of any SARM. Case reports of hepatotoxicity at athlete-used doses present serious safety concerns.",
        "dosage": "5–15 mg/day for 8–10 weeks.",
        "timing": "Once daily.",
        "how_to_take": "Oral liquid or capsule.",
        "hydration": "3+ L/day.",
        "training_synergy": "Progressive overload essential to capitalise on anabolic environment.",
        "cycling": "8–10 week cycles. Full PCT mandatory.",
        "benefits": ["Very high anabolic potency", "Significant lean mass gains", "Fat loss support"],
        "side_effects": [{"effect": "Strong testosterone suppression", "severity": "high"}, {"effect": "Aggression / mood changes", "severity": "medium"}, {"effect": "Hepatotoxicity — liver damage in case reports", "severity": "high"}],
        "final_recommendation": "Liver function tests mandatory. Not recommended due to hepatotoxicity risk.",
        "evidence_tier": "low", "safe_for_beginners": False,
        "pubmed_ids": ["20427478"],
        "examine_url": "https://examine.com/supplements/rad-140/",
        "legal_status": "Research chemical — not approved for human use. Banned by WADA.",
    },
    # ── MK-677 ────────────────────────────────────────────────────────────
    {
        "id": "mk677", "name": "MK-677 (Ibutamoren)",
        "aliases": ["mk677", "mk-677", "ibutamoren", "nutrobal", "mk 677"],
        "category": "sarm",
        "tags": ["muscle_gain", "fat_loss", "recovery", "hgh", "sleep", "sarm"],
        "summary": "Oral GH secretagogue. Stimulates pituitary GH and IGF-1 release. Non-suppressive — no PCT needed. Improves sleep, lean mass, and recovery.",
        "what_it_is": "MK-677 is an oral ghrelin receptor agonist stimulating GH and IGF-1 release. Not technically a SARM — no androgen receptor binding, no testosterone suppression, no PCT required.",
        "dosage": "10–25 mg/day before bed.",
        "timing": "Before bed to align with natural overnight GH pulse.",
        "how_to_take": "Oral capsule or liquid.",
        "hydration": "3 L/day — water retention common early on.",
        "training_synergy": "Resistance training amplifies lean mass effects. Fasted morning cardio amplifies fat loss.",
        "cycling": "12–24 week cycles. No PCT needed.",
        "benefits": ["Elevated GH and IGF-1", "Improved sleep depth", "Lean mass gain", "Recovery support", "Skin and collagen improvement"],
        "side_effects": [{"effect": "Increased appetite and water retention", "severity": "medium"}, {"effect": "Elevated fasting glucose — monitor in diabetics", "severity": "medium"}],
        "stacking": ["Ostarine (recomp)", "LGD-4033 (bulk)"],
        "final_recommendation": "Stack with Ostarine or LGD for synergistic results. Monitor IGF-1 and fasting glucose quarterly.",
        "evidence_tier": "moderate", "safe_for_beginners": True,
        "pubmed_ids": ["11149771"],
        "examine_url": "https://examine.com/supplements/mk-677/",
        "legal_status": "Research chemical — not approved for human use.",
    },
    # ── Testosterone enanthate ───────────────────────────────────────────
    {
        "id": "test_e", "name": "Testosterone enanthate",
        "aliases": ["testosterone enanthate", "test e", "testo e",
                    "testosterone", "testosteron", "testosterona"],
        "category": "steroid",
        "tags": ["muscle_gain", "strength", "bulking", "testosterone", "steroid"],
        "summary": "Gold standard anabolic injectable. Long-ester testosterone with predictable kinetics and decades of clinical data.",
        "what_it_is": "Synthetic testosterone with enanthate ester providing stable blood levels at twice-weekly injections. The body's primary anabolic hormone delivered exogenously saturates androgen receptors in muscle, bone, and CNS.",
        "dosage": "Beginner: 300–500 mg/week (split E3.5D). Intermediate: 500–750 mg/week.",
        "timing": "IM or SubQ injection every 3.5 days for stable levels.",
        "how_to_take": "IM (glute/quads/delts) or SubQ. Rotate sites. 23–25G for injection, 18–21G for drawing.",
        "hydration": "2.5–3 L/day. Monitor blood pressure.",
        "training_synergy": "Progressive overload, high protein (2–2.4 g/kg), calorie surplus, adequate sleep.",
        "cycling": "12–16 week cycles. AI (Anastrozole 0.25–0.5 mg E3D) required. PCT: Nolvadex 40/40/20/20 mg starting 2 weeks post-last injection.",
        "benefits": ["Significant lean mass and strength gains", "Improved recovery", "Libido and well-being"],
        "side_effects": [{"effect": "Complete testosterone suppression", "severity": "high"}, {"effect": "Aromatisation — AI required", "severity": "medium"}, {"effect": "Cardiovascular strain (HDL ↓, LVH risk)", "severity": "high"}, {"effect": "Acne and hair loss (genetic)", "severity": "medium"}],
        "stacking": ["Anastrozole (AI)", "NPP/Deca (intermediate+)", "Anavar (cut)"],
        "final_recommendation": "Bloodwork before, mid-cycle, post-PCT. AI + liver support + cardiovascular monitoring non-negotiable. Consult endocrinologist.",
        "evidence_tier": "very_high", "safe_for_beginners": False,
        "pubmed_ids": ["8637536", "11502560"],
        "research_refs": ["Bhasin et al. (1996) NEJM — dose-response landmark", "Bhasin et al. (2001) NEJM"],
        "legal_status": "Schedule III (USA). Prescription only in UK, India, Canada, Australia.",
    },
    # ── Anavar ───────────────────────────────────────────────────────────
    {
        "id": "anavar", "name": "Anavar (Oxandrolone)",
        "aliases": ["anavar", "oxandrolone", "var", "oxandrin", "oxandrolona"],
        "category": "steroid",
        "tags": ["fat_loss", "strength", "cutting", "lean_muscle", "steroid"],
        "summary": "Mild oral anabolic steroid popular for cutting. Preserves muscle in calorie deficit, minimal water retention. Still hepatotoxic and suppressive.",
        "what_it_is": "Oxandrolone is a 17α-alkylated oral anabolic steroid with low androgenic activity. Widely used for cutting cycles and by women at low doses for its comparatively mild virilisation risk.",
        "dosage": "Men: 20–80 mg/day split. Women: 5–20 mg/day.",
        "timing": "Split twice daily (morning + evening) — 9 h half-life.",
        "how_to_take": "Oral tablet.",
        "hydration": "2.5–3 L/day.",
        "training_synergy": "Calorie deficit + high protein (2.2–2.4 g/kg) for maximum cutting benefit.",
        "cycling": "6–8 weeks (limit due to hepatotoxicity). PCT required.",
        "benefits": ["Muscle preservation on cut", "Strength gains without mass", "Minimal water retention"],
        "side_effects": [{"effect": "Liver stress (oral 17-AA)", "severity": "medium"}, {"effect": "Testosterone suppression", "severity": "medium"}, {"effect": "HDL reduction", "severity": "high"}, {"effect": "Virilisation in women (dose-dependent)", "severity": "high"}],
        "final_recommendation": "Liver function and lipid tests mandatory. Not for beginners. SERM PCT required.",
        "evidence_tier": "high", "safe_for_beginners": False,
        "pubmed_ids": ["7998639"],
        "legal_status": "Schedule III (USA). Prescription only.",
    },
    # ── Nandrolone ───────────────────────────────────────────────────────
    {
        "id": "nandrolone", "name": "Nandrolone / NPP / Deca-Durabolin",
        "aliases": ["nandrolone", "deca", "deca durabolin", "npp",
                    "nandrolone decanoate", "deca-durabolin"],
        "category": "steroid",
        "tags": ["muscle_gain", "strength", "bulking", "joint_health", "steroid"],
        "summary": "19-nor anabolic steroid. Known for lean mass gains and joint lubrication. Requires prolactin management and testosterone base. Not for beginners.",
        "what_it_is": "19-nortestosterone derivative available as NPP (short ester) or Deca-Durabolin (decanoate). Highly anabolic, lower androgenic ratio than testosterone, notable collagen synthesis and joint benefits.",
        "dosage": "NPP: 300–400 mg/week (E3.5D). Deca: 200–400 mg/week (once weekly).",
        "timing": "IM injection on schedule.",
        "how_to_take": "IM injection. Always run with testosterone base.",
        "hydration": "3 L/day.",
        "training_synergy": "Progressive overload + high protein. Joint benefits allow higher training volume.",
        "cycling": "12–16 weeks with testosterone base. Cabergoline for prolactin. Full PCT required.",
        "benefits": ["Lean mass gains with less water retention than test", "Joint lubrication", "Collagen synthesis", "Improved recovery"],
        "side_effects": [{"effect": "Prolactin elevation — cabergoline required", "severity": "high"}, {"effect": "Full testosterone suppression", "severity": "high"}, {"effect": "Cardiovascular strain", "severity": "high"}, {"effect": "Erectile dysfunction without test base (deca dick)", "severity": "high"}],
        "final_recommendation": "Must be run with testosterone base. Cabergoline mandatory. Bloodwork throughout cycle.",
        "evidence_tier": "high", "safe_for_beginners": False,
        "pubmed_ids": ["8637536"],
        "legal_status": "Controlled substance. Prescription only.",
    },
    # ── BPC-157 ───────────────────────────────────────────────────────────
    {
        "id": "bpc157", "name": "BPC-157",
        "aliases": ["bpc157", "bpc-157", "body protection compound",
                    "bpc 157", "pentadecapeptide"],
        "category": "peptide",
        "tags": ["recovery", "injury", "joint_health", "gut", "healing", "peptide"],
        "summary": "15-amino acid peptide derived from gastric juice. Strong animal evidence for tendon, ligament, muscle, and gut healing. Research chemical.",
        "what_it_is": "BPC-157 is a synthetic peptide sequence from human gastric juice protein. Animal research shows accelerated healing of tendons, ligaments, and intestinal tissue via GH receptor upregulation and angiogenesis.",
        "dosage": "250–500 mcg/day subcutaneous or intramuscular.",
        "timing": "Near injury site (local) or systemic abdomen. Once or twice daily.",
        "how_to_take": "Reconstitute with bacteriostatic water. Insulin syringe 29–31G. Refrigerate — use within 30 days.",
        "hydration": "2.5–3 L/day standard.",
        "training_synergy": "Active rehabilitation during protocol maximises healing per animal research.",
        "cycling": "Acute injury: 4–6 weeks. Chronic: 8–12 weeks.",
        "benefits": ["Accelerated tendon/ligament healing", "Gut lining repair", "Anti-inflammatory", "Angiogenesis"],
        "side_effects": [{"effect": "Injection site irritation (mild, transient)", "severity": "low"}, {"effect": "Mild nausea (oral form)", "severity": "low"}],
        "stacking": ["TB-500 (systemic healing synergy)", "Ipamorelin/CJC-1295"],
        "final_recommendation": "Source quality critical. Sterility non-negotiable. Complements physiotherapy; does not replace it.",
        "evidence_tier": "moderate", "safe_for_beginners": True,
        "pubmed_ids": ["23439702", "21447935"],
        "examine_url": "https://examine.com/supplements/bpc-157/",
        "research_refs": ["Sikiric et al. (2013) Curr Pharm Des", "Chang et al. (2011) JBMR"],
        "legal_status": "Research chemical — not approved for human use.",
    },
    # ── TB-500 ────────────────────────────────────────────────────────────
    {
        "id": "tb500", "name": "TB-500 (Thymosin Beta-4)",
        "aliases": ["tb500", "tb-500", "thymosin beta-4", "tb 500"],
        "category": "peptide",
        "tags": ["recovery", "injury", "flexibility", "healing", "peptide"],
        "summary": "Thymosin Beta-4 analogue. Systemic healing, improved flexibility, angiogenesis. Often stacked with BPC-157.",
        "what_it_is": "TB-500 is a synthetic analogue of Thymosin Beta-4, a naturally occurring protein involved in cell migration, angiogenesis, and tissue repair. Acts systemically rather than locally.",
        "dosage": "2–2.5 mg twice weekly (loading 4–6 weeks), then 2 mg bi-weekly maintenance.",
        "timing": "SubQ injection, any time.",
        "how_to_take": "Reconstitute with bacteriostatic water. Insulin syringe.",
        "hydration": "2.5–3 L/day.",
        "training_synergy": "Gradual return-to-training protocol during TB-500 course maximises healing.",
        "cycling": "Loading 4–6 weeks then maintenance.",
        "benefits": ["Systemic tissue repair", "Improved flexibility", "Angiogenesis", "Anti-inflammatory"],
        "side_effects": [{"effect": "Injection site irritation", "severity": "low"}, {"effect": "Head rush immediately post-injection", "severity": "low"}],
        "stacking": ["BPC-157", "Ipamorelin/CJC-1295"],
        "final_recommendation": "Best in combination with BPC-157 for comprehensive injury recovery.",
        "evidence_tier": "moderate", "safe_for_beginners": True,
        "pubmed_ids": ["22747353"],
        "legal_status": "Research chemical — not approved for human use.",
    },
    # ── Ipamorelin / CJC-1295 ────────────────────────────────────────────
    {
        "id": "ipamorelin", "name": "Ipamorelin / CJC-1295",
        "aliases": ["ipamorelin", "cjc1295", "cjc-1295",
                    "ipamorelin cjc", "ghrp", "gh peptide"],
        "category": "peptide",
        "tags": ["fat_loss", "recovery", "hgh", "sleep", "anti_aging", "peptide"],
        "summary": "Gold-standard GH peptide stack. Clean GH pulse with minimal cortisol/prolactin elevation. Popular for fat loss, recovery, and anti-aging.",
        "what_it_is": "Ipamorelin is a selective GHRP with minimal side effects; CJC-1295 without DAC is a GHRH analogue extending GH pulse. Together they produce a physiological, amplified GH release.",
        "dosage": "Ipamorelin 200–300 mcg + CJC-1295 no-DAC 100–200 mcg per dose, 2–3× daily.",
        "timing": "Before bed (mandatory), plus AM and pre-workout — always fasted (no food 2 h prior).",
        "how_to_take": "SubQ injection. Refrigerate after reconstitution.",
        "hydration": "3 L/day.",
        "training_synergy": "Resistance training + fasted morning cardio maximise lean mass and fat loss outcomes.",
        "cycling": "12–24 week cycles. No PCT (not suppressive).",
        "benefits": ["Amplified GH pulse", "Fat loss (especially visceral)", "Improved REM sleep", "Lean mass retention", "Collagen/skin improvement"],
        "side_effects": [{"effect": "Mild water retention (first 2 weeks)", "severity": "low"}, {"effect": "Increased hunger", "severity": "low"}],
        "stacking": ["BPC-157", "TB-500", "MK-677 (oral GH alternative)"],
        "final_recommendation": "Most effective at 3× daily fasted dosing. Monitor IGF-1 quarterly.",
        "evidence_tier": "moderate", "safe_for_beginners": False,
        "pubmed_ids": ["9535775"],
        "legal_status": "Research chemical — not approved for human use.",
    },
    # ── Sermorelin ───────────────────────────────────────────────────────
    {
        "id": "sermorelin", "name": "Sermorelin / GHRH peptides",
        "aliases": ["sermorelin", "ghrh analogue", "mod grf 1-29", "modified grf"],
        "category": "peptide",
        "tags": ["hgh", "fat_loss", "anti_aging", "recovery", "gh", "peptide"],
        "summary": "GHRH analogue stimulating pituitary GH release. Softer, more natural GH increase vs exogenous HGH. Often prescribed in anti-aging clinics.",
        "what_it_is": "GHRH analogue stimulating endogenous GH release from pituitary with pulsatile, physiological pattern — safer profile than exogenous HGH.",
        "dosage": "Sermorelin: 200–500 mcg before bed. Mod GRF 1-29: 100–200 mcg/dose.",
        "timing": "SubQ before sleep, minimum 2 h fasted.",
        "how_to_take": "SubQ injection.",
        "hydration": "3 L/day.",
        "training_synergy": "Resistance training + fasted cardio amplify fat loss.",
        "cycling": "6–12 month cycles.",
        "benefits": ["Natural-pattern GH stimulation", "Composition improvement over 3–6 months", "Better sleep", "Lower cost than HGH"],
        "side_effects": [{"effect": "Injection site redness", "severity": "low"}, {"effect": "Flushing", "severity": "low"}],
        "stacking": ["Ipamorelin (GHRP + GHRH synergy)", "BPC-157"],
        "final_recommendation": "Physician supervision recommended. Monitor IGF-1 quarterly.",
        "evidence_tier": "moderate", "safe_for_beginners": False,
        "legal_status": "Prescription in USA/most countries. Research chemical elsewhere.",
    },
    # ── HGH ──────────────────────────────────────────────────────────────
    {
        "id": "hgh", "name": "Human Growth Hormone (HGH)",
        "aliases": ["hgh", "human growth hormone", "growth hormone",
                    "gh", "somatropin", "rhgh",
                    "生长激素", "hormona de crecimiento"],
        "category": "peptide",
        "tags": ["fat_loss", "muscle_gain", "recovery", "anti_aging", "hgh"],
        "summary": "Recombinant somatropin. Potent lipolytic and anabolic agent. Prescription only globally. Dramatically reduces visceral fat.",
        "what_it_is": "Recombinant HGH (somatropin) stimulates IGF-1 (anabolic) and drives lipolysis directly. Age-related GH decline makes it appealing for anti-aging and body composition.",
        "dosage": "Anti-aging/fat loss: 1–3 IU/day. Bodybuilding: 4–8 IU/day (significantly higher risk).",
        "timing": "SubQ injection on waking (fat loss) or before bed (GH pulse). Some use split AM+PM.",
        "how_to_take": "SubQ abdomen, rotating sites. Reconstitute with bacteriostatic water. Store 2–8 °C.",
        "hydration": "3+ L/day — water retention common in weeks 1–6.",
        "training_synergy": "Resistance training + fasted morning cardio maximise body composition outcomes.",
        "cycling": "Anti-aging: 6–12 months continuous. Bodybuilding: 16–24 weeks. Monitor IGF-1.",
        "benefits": ["Significant visceral fat reduction", "Lean mass retention + modest gain", "Connective tissue strengthening", "Improved sleep quality"],
        "side_effects": [{"effect": "Carpal tunnel (tingling hands)", "severity": "medium"}, {"effect": "Insulin resistance — monitor glucose", "severity": "high"}, {"effect": "Acromegaly at sustained high doses", "severity": "high"}],
        "stacking": ["Testosterone (synergistic)", "T3 (advanced)", "Insulin (extreme danger — advanced only)"],
        "final_recommendation": "Physician supervision mandatory. IGF-1, fasting glucose, HbA1c quarterly. Pharmaceutical-grade only (Novo Nordisk, Pfizer, Eli Lilly).",
        "evidence_tier": "very_high", "safe_for_beginners": False,
        "pubmed_ids": ["2388534"],
        "research_refs": ["Rudman et al. (1990) NEJM — landmark study"],
        "legal_status": "Prescription only worldwide. Banned by WADA.",
    },
    # ── Vitamin D3 + K2 ──────────────────────────────────────────────────
    {
        "id": "vitamin_d", "name": "Vitamin D3 + K2",
        "aliases": ["vitamin d", "vitamin d3", "cholecalciferol",
                    "vit d", "vitamina d", "vitamine d", "विटामिन डी"],
        "category": "supplement",
        "tags": ["health", "testosterone", "immune", "bone", "recovery"],
        "summary": "Essential fat-soluble hormone-vitamin. Deficiency affects 40%+ globally. Regulates testosterone, immune function, and bone density.",
        "what_it_is": "D3 (cholecalciferol) is a fat-soluble prohormone synthesised in skin on UV exposure, regulating 1,000+ genes. K2 (MK-7) directs calcium to bone, away from arteries.",
        "dosage": "D3: 2,000–5,000 IU/day. K2 MK-7: 100–200 mcg/day. Test serum 25-OH-D to personalise.",
        "timing": "With largest fat-containing meal for optimal absorption.",
        "how_to_take": "Softgel or oil drops. D3 + K2 in same meal.",
        "hydration": "Standard 2.5–3 L/day.",
        "training_synergy": "Adequate D3 supports testosterone production (+20% in deficient individuals) and muscle function.",
        "cycling": "Year-round — sunlight and diet rarely achieve optimal levels in training populations.",
        "benefits": ["Testosterone support", "Immune regulation", "Bone density", "Mood improvement"],
        "side_effects": [{"effect": "Toxicity only at >10,000 IU/day without monitoring", "severity": "low"}],
        "stacking": ["Magnesium (required for D3 activation)", "Omega-3"],
        "final_recommendation": "Test serum 25-OH-D. Target 40–70 ng/mL. Adjust dose accordingly. Daily with K2.",
        "evidence_tier": "very_high", "safe_for_beginners": True,
        "pubmed_ids": ["21154195"],
        "examine_url": "https://examine.com/supplements/vitamin-d/",
        "research_refs": ["Pilz et al. (2011) Horm Metab Res", "Holick (2007) NEJM"],
    },
    # ── Omega-3 ───────────────────────────────────────────────────────────
    {
        "id": "omega3", "name": "Omega-3 fish oil (EPA + DHA)",
        "aliases": ["omega 3", "fish oil", "omega-3", "epa dha",
                    "omega 3 fish oil", "aceite de pescado", "फिश ऑयल"],
        "category": "supplement",
        "tags": ["health", "recovery", "anti_inflammatory", "cardiovascular", "joint_health"],
        "summary": "EPA + DHA reduce systemic inflammation, improve cardiovascular markers, support joints and brain function.",
        "what_it_is": "Long-chain omega-3 polyunsaturated fatty acids. EPA and DHA reduce inflammatory cytokines, improve HDL/triglycerides, and support muscle protein synthesis.",
        "dosage": "3–6 g combined EPA + DHA per day (not total oil volume on label).",
        "timing": "With meals to minimise fish aftertaste.",
        "how_to_take": "Softgel or liquid. Enteric-coated if sensitive.",
        "hydration": "Standard 2.5–3 L/day.",
        "training_synergy": "Anti-inflammatory effects reduce DOMS and support recovery from intense training.",
        "cycling": "Daily, year-round.",
        "benefits": ["Systemic anti-inflammatory", "Cardiovascular protection", "Joint health", "Muscle protein synthesis support"],
        "side_effects": [{"effect": "Fish aftertaste / burping (take with meals)", "severity": "low"}],
        "final_recommendation": "Prioritise EPA + DHA mg on label over total oil volume. Nordic Naturals or pharmaceutical-grade brands.",
        "evidence_tier": "very_high", "safe_for_beginners": True,
        "pubmed_ids": ["19589961"],
        "examine_url": "https://examine.com/supplements/fish-oil/",
    },
    # ── Zinc & Magnesium ─────────────────────────────────────────────────
    {
        "id": "zinc_magnesium", "name": "Zinc & Magnesium (ZMA)",
        "aliases": ["zma", "zinc magnesium", "zinc", "magnesium",
                    "magnesium glycinate", "zinc picolinate", "mineral supplements"],
        "category": "supplement",
        "tags": ["testosterone", "sleep", "recovery", "health"],
        "summary": "Zinc supports testosterone synthesis and immune function; magnesium improves sleep, reduces cortisol. Both commonly depleted in athletes.",
        "what_it_is": "Athletes lose zinc in sweat (testosterone synthesis, immunity) and magnesium (sleep architecture, cortisol, 300+ enzymatic reactions). Deficiency in both is widespread in training populations.",
        "dosage": "Zinc: 25–45 mg/day (picolinate or citrate). Magnesium: 300–500 mg glycinate or malate.",
        "timing": "Before bed on empty stomach — optimal testosterone and sleep hormone effects.",
        "how_to_take": "Capsule. Avoid zinc with food.",
        "hydration": "Standard 2.5–3 L/day.",
        "training_synergy": "Zinc and magnesium support testosterone and sleep — critical for training adaptation.",
        "cycling": "Daily, year-round.",
        "benefits": ["Testosterone support when deficient", "Sleep quality improvement", "Cortisol reduction", "Immune function"],
        "side_effects": [{"effect": "Nausea if zinc taken with food", "severity": "low"}],
        "final_recommendation": "Use magnesium glycinate (best bioavailability). Test serum zinc and magnesium if deficiency suspected.",
        "evidence_tier": "high", "safe_for_beginners": True,
        "pubmed_ids": ["10738264"],
        "examine_url": "https://examine.com/supplements/zma/",
    },
    # ── Fat burner stack ─────────────────────────────────────────────────
    {
        "id": "fat_burner_stack", "name": "Fat burner supplements",
        "aliases": ["fat burner", "fat burning supplement", "thermogenic",
                    "fat loss supplement", "weight loss supplement",
                    "quemagrasas", "brûleur de graisses"],
        "category": "supplement",
        "tags": ["fat_loss", "cutting", "thermogenic", "metabolism", "energy"],
        "summary": "Evidence-based fat loss supplements: Caffeine (thermogenic), L-Carnitine (fat transport), EGCG (synergistic), Yohimbine (alpha-2 antagonist).",
        "what_it_is": "Fat burners combine thermogenics (caffeine, synephrine), fat transport (L-carnitine), lipolytic agents (yohimbine at fasted alpha-2 receptors), and metabolic boosters (EGCG + caffeine). Evidence quality varies significantly by ingredient.",
        "dosage": "Caffeine 200 mg, L-Carnitine 2–4 g, EGCG 400 mg, Yohimbine 2.5–20 mg (start low).",
        "timing": "Fasted or pre-workout. Yohimbine strictly requires fasted state.",
        "how_to_take": "Capsule or powder. Start at lowest dose — assess tolerance over 5–7 days.",
        "hydration": "3+ L/day. Stimulants increase sweating.",
        "training_synergy": "Most effective with a calorie deficit + resistance training to preserve lean mass.",
        "cycling": "Cycle stimulant components 5 days on / 2 off.",
        "benefits": ["Increased resting metabolic rate", "Enhanced fat oxidation", "Appetite suppression", "Training energy boost in deficit"],
        "side_effects": [{"effect": "Anxiety and elevated heart rate (stimulants)", "severity": "medium"}, {"effect": "Yohimbine: severe anxiety/BP in sensitive individuals", "severity": "high"}],
        "final_recommendation": "No fat burner replaces calorie tracking. Use as adjunct to structured deficit + resistance training.",
        "evidence_tier": "moderate", "safe_for_beginners": True,
        "pubmed_ids": ["20019636"],
        "examine_url": "https://examine.com/supplements/fat-burners/",
        "products": [
            {"name": "Transparent Labs Fat Burner",  "price_inr": 3499, "rating": 4.5, "badge": "🏅 Premium", "best_for": "Evidence-dosed, no proprietary blends"},
            {"name": "MuscleBlaze Fat Burner Pro",   "price_inr": 1499, "rating": 4.3, "badge": "🔥 Popular", "best_for": "Best-seller India, thermogenic"},
            {"name": "HealthXP Lean Burner",         "price_inr": 899,  "rating": 4.1, "badge": "💪 Balanced", "best_for": "Budget thermogenic India"},
        ],
    },
]

# ── Index structures ───────────────────────────────────────────────────────
_ALIAS: dict[str, dict] = {}
for _it in KB:
    _ALIAS[_it["name"].lower()] = _it
    for _a in _it.get("aliases", []):
        _ALIAS[_a.lower()] = _it

_ID_IDX: dict[str, dict] = {it["id"]: it for it in KB}


# ═══════════════════════════════════════════════════════════════════════════
# CACHE  (SQLite — thread-safe)
# ═══════════════════════════════════════════════════════════════════════════

def _init_cache() -> None:
    os.makedirs(os.path.dirname(CACHE_DB), exist_ok=True)
    with sqlite3.connect(CACHE_DB) as c:
        c.execute("""CREATE TABLE IF NOT EXISTS report_cache (
            cache_key   TEXT PRIMARY KEY,
            query       TEXT NOT NULL,
            report_json TEXT NOT NULL,
            source      TEXT DEFAULT 'kb',
            created_at  REAL NOT NULL
        )""")
        c.execute("CREATE INDEX IF NOT EXISTS idx_crt ON report_cache(created_at)")

_init_cache()


def _cache_key(query: str, filters: list) -> str:
    """
    Cache key includes filters.
    FIX 2 (backend part): different filter set → different key → fresh re-rank.
    """
    raw = json.dumps({"q": query.lower().strip(), "f": sorted(filters)}, sort_keys=True)
    return hashlib.sha256(raw.encode()).hexdigest()[:32]


def _cache_get(key: str) -> list | None:
    try:
        with _cache_lock, sqlite3.connect(CACHE_DB) as c:
            row = c.execute("SELECT report_json, created_at FROM report_cache WHERE cache_key=?", (key,)).fetchone()
        if not row or (time.time() - row[1]) > CACHE_TTL_SEC:
            return None
        return json.loads(row[0])
    except Exception as e:
        print(f"[Cache GET] {e}")
        return None


def _cache_set(key: str, query: str, results: list, source: str = "ai") -> None:
    try:
        with _cache_lock, sqlite3.connect(CACHE_DB) as c:
            c.execute(
                "INSERT OR REPLACE INTO report_cache(cache_key,query,report_json,source,created_at) VALUES (?,?,?,?,?)",
                (key, query, json.dumps(results), source, time.time())
            )
    except Exception as e:
        print(f"[Cache SET] {e}")


def _cache_stats() -> dict:
    try:
        with sqlite3.connect(CACHE_DB) as c:
            total = c.execute("SELECT COUNT(*) FROM report_cache").fetchone()[0]
            fresh = c.execute("SELECT COUNT(*) FROM report_cache WHERE created_at > ?",
                              (time.time() - CACHE_TTL_SEC,)).fetchone()[0]
        return {"total": total, "fresh": fresh}
    except Exception:
        return {}


# ═══════════════════════════════════════════════════════════════════════════
# STRICT ENTITY-LOCKED SCORING  ← core fix for Issue 1
# ═══════════════════════════════════════════════════════════════════════════

def _score_strict(
    query: str,
    item: dict,
    allowed_ids: list[str],
    goal_mods: list[str],
    filters: list[str],
    intent: str,
) -> int:
    """
    Relevance score with hard entity enforcement.

    Step 1: If allowed_ids is non-empty AND item.id NOT in it → return 0.
            This is the hard exclusion — "best creatine" will NEVER show whey.
    Step 2: Items in the allow-list start with a 100-point entity bonus,
            so they always outrank any hypothetical non-locked item.
    Step 3: Goal modifier + filter boosts re-rank within the allowed set.
            The +60 boost makes filter clicks visibly change result order.
    """
    iid   = item["id"]
    name  = item["name"].lower()
    itags = " ".join(item.get("tags", []))
    q     = query.lower()

    # ── HARD EXCLUDE ──────────────────────────────────────────────────────
    if allowed_ids and iid not in allowed_ids:
        return 0

    s = 0

    # ── Entity membership bonus ───────────────────────────────────────────
    if allowed_ids and iid in allowed_ids:
        s += 100          # dominates over any non-member

    # ── Query word match (within the allowed set) ─────────────────────────
    aliases_str = " ".join(item.get("aliases", []))
    for word in re.split(r"[\s\W]+", q):
        if len(word) < 3:
            continue
        if word in name:          s += 8
        if word in aliases_str:   s += 5
        if word in itags:         s += 3

    # ── Goal modifier boost  ← FIX 2 (backend part) ──────────────────────
    # Deliberately large (+60) so clicking a filter chip meaningfully
    # re-orders results within the entity set.
    for mod in goal_mods:
        if mod in itags:
            s += 60

    # ── Filter chip boost ─────────────────────────────────────────────────
    for f in filters:
        if f in itags:
            s += 60

    # ── Evidence tier ─────────────────────────────────────────────────────
    s += {"very_high": 15, "high": 10, "moderate": 5, "low": 0}.get(
        item.get("evidence_tier", "moderate"), 5)

    # ── Intent-specific boosts ────────────────────────────────────────────
    if intent in ("dosage", "research", "explain"):
        if item.get("what_it_is"): s += 5
        if item.get("dosage"):     s += 5
        if item.get("pubmed_ids"): s += 5
    if intent == "product":
        if item.get("products"):   s += 30

    return s


def _kb_strict(
    query: str,
    allowed_ids: list[str],
    goal_mods: list[str],
    filters: list[str],
    intent: str,
    limit: int = 4,
) -> list[dict]:
    scored = [
        {**item, "_sc": _score_strict(query, item, allowed_ids, goal_mods, filters, intent)}
        for item in KB
    ]
    scored = [r for r in scored if r["_sc"] > 0]
    scored.sort(key=lambda x: x["_sc"], reverse=True)
    return [{k: v for k, v in r.items() if k != "_sc"} for r in scored[:limit]]


# ═══════════════════════════════════════════════════════════════════════════
# LIVE DATA RETRIEVAL  (parallel)
# ═══════════════════════════════════════════════════════════════════════════

TRUST: dict[str, int] = {
    "pubmed": 5, "ncbi": 5, "examine": 4, "nih": 4,
    "jissn": 4, "openfda": 3, "serp": 2, "scraped": 1,
}


def _pubmed(query: str, n: int = 5) -> list[dict]:
    try:
        p: dict[str, Any] = {"db": "pubmed", "term": f"{query} supplement",
                              "retmax": n, "retmode": "json", "sort": "relevance"}
        if PUBMED_API_KEY:
            p["api_key"] = PUBMED_API_KEY
        r = requests.get(PUBMED_SEARCH, params=p, timeout=8)
        if r.status_code != 200:
            return []
        ids = r.json().get("esearchresult", {}).get("idlist", [])
        if not ids:
            return []
        p2: dict[str, Any] = {"db": "pubmed", "id": ",".join(ids), "retmode": "json"}
        if PUBMED_API_KEY:
            p2["api_key"] = PUBMED_API_KEY
        r2 = requests.get(PUBMED_FETCH, params=p2, timeout=10)
        if r2.status_code != 200:
            return [{"id": pid, "source": "pubmed", "trust": 5,
                     "title": f"PubMed {pid}",
                     "url": f"https://pubmed.ncbi.nlm.nih.gov/{pid}/", "snippet": ""}
                    for pid in ids]
        arts = r2.json().get("result", {})
        out = []
        for pid in ids:
            a = arts.get(pid, {})
            auth = (a.get("authors") or [{}])[0].get("name", "") + " et al."
            out.append({"id": pid, "source": "pubmed", "trust": 5,
                        "title": a.get("title", f"PubMed {pid}"),
                        "authors": auth, "journal": a.get("fulljournalname", ""),
                        "year": (a.get("pubdate") or "")[:4],
                        "url": f"https://pubmed.ncbi.nlm.nih.gov/{pid}/",
                        "snippet": f"{auth} {a.get('pubdate','')}. {a.get('fulljournalname','')}."})
        return out
    except Exception as e:
        print(f"[PubMed] {e}")
        return []


def _examine(name: str) -> dict | None:
    try:
        slug = name.lower().replace(" ", "-").replace("(", "").replace(")", "")
        url = f"https://examine.com/supplements/{slug}/"
        r = requests.get(url, headers={"User-Agent": "FitSearchBot/3.0"}, timeout=8)
        if r.status_code != 200:
            return None
        m = re.search(r'<meta[^>]*name="description"[^>]*content="([^"]{50,})"', r.text)
        summary = m.group(1).strip()[:500] if m else ""
        return {"source": "examine", "trust": 4, "url": url,
                "summary": summary, "snippet": summary[:200]}
    except Exception as e:
        print(f"[Examine] {e}")
        return None


def _openfda(name: str) -> list[dict]:
    try:
        r = requests.get(OPENFDA_URL,
                         params={"search": f'patient.drug.medicinalproduct:"{name}"', "limit": 3},
                         timeout=6)
        if r.status_code != 200:
            return []
        return [{"source": "openfda", "trust": 3,
                 "reactions": [rx.get("reactionmeddrapt", "") for rx in
                                ev.get("patient", {}).get("reaction", [])[:3]],
                 "snippet": "FDA adverse event report"}
                for ev in r.json().get("results", [])[:3]]
    except Exception as e:
        print(f"[OpenFDA] {e}")
        return []


def _serp(query: str) -> list[dict]:
    if not SERP_API_KEY:
        return []
    try:
        r = requests.get("https://serpapi.com/search.json",
                         params={"q": f"{query} site:examine.com OR site:pubmed.ncbi.nlm.nih.gov",
                                 "api_key": SERP_API_KEY, "engine": "google",
                                 "num": 5, "hl": "en"},
                         timeout=8)
        if r.status_code != 200:
            return []
        return [{"source": "serp", "trust": 2,
                 "title": res.get("title", ""), "url": res.get("link", ""),
                 "snippet": res.get("snippet", "")}
                for res in r.json().get("organic_results", [])[:5]]
    except Exception as e:
        print(f"[SerpAPI] {e}")
        return []


def _live(query: str, entity_key: str | None) -> dict:
    term = entity_key.replace("_", " ") if entity_key else query
    live: dict = {"pubmed": [], "examine": {}, "fda": [], "serp": []}
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
        fp = ex.submit(_pubmed, term)
        fe = ex.submit(_examine, term)
        ff = ex.submit(_openfda, term)
        fs = ex.submit(_serp, query)
        live["pubmed"]  = fp.result()
        live["examine"] = fe.result() or {}
        live["fda"]     = ff.result()
        live["serp"]    = fs.result()
    return live


def _evidence(live: dict) -> dict:
    items = live.get("pubmed", []) + live.get("serp", []) + live.get("fda", [])
    if live.get("examine"):
        items.append(live["examine"])
    f = sorted([i for i in items if i.get("trust", 0) >= 2],
               key=lambda x: x.get("trust", 0), reverse=True)
    return {
        "high_trust":      [i for i in f if i.get("trust", 0) >= 4],
        "pubmed_ids":      [i["id"] for i in live.get("pubmed", []) if "id" in i],
        "examine_url":     live.get("examine", {}).get("url"),
        "examine_summary": live.get("examine", {}).get("summary", ""),
        "fda_events":      live.get("fda", []),
    }


# ═══════════════════════════════════════════════════════════════════════════
# CLAUDE SYNTHESIS  (ChatGPT-style structured analysis)
# ═══════════════════════════════════════════════════════════════════════════

_SYSTEM = """You are FitSearch AI — a world-class evidence-based sports nutrition scientist.

Generate a structured report for the user's query. Output format depends on intent:

intent = research / explain / dosage / side_effects / cycle:
→ 10-section scientific report JSON

intent = product:
→ product list JSON with price/rating/badge

intent = training:
→ structured training/diet plan JSON

intent = compare:
→ side-by-side comparison JSON

intent = recommend:
→ ranked recommendation list JSON

STRICT RULES:
1. Only JSON. No markdown fences, no prose outside JSON.
2. Same language as user query.
3. ONLY include results directly related to the queried entity.
4. safe_for_beginners: false for all steroids and most SARMs.
5. Include real PubMed IDs.
6. evidence_tier: "very_high"|"high"|"moderate"|"low"
7. Include legal_status for controlled/research substances.

For research/explain/dosage/side_effects/cycle use:
{
  "detected_language":"English",
  "intent":"research",
  "name":"Primary compound",
  "tagline":"One-sentence description",
  "category":"supplement|sarm|steroid|peptide|training|diet",
  "evidence_tier":"very_high",
  "safe_for_beginners":true,
  "legal_status":null,
  "sections":{
    "what_it_is":"2-4 sentences on mechanism + origin",
    "dosage":"Specific evidence-based dosage",
    "timing":"Optimal timing + rationale",
    "how_to_take":"Practical prep tips",
    "hydration":"Fluid requirements",
    "training_synergy":"Training protocol for maximum effect",
    "cycling":"Cycling protocol or why none needed",
    "benefits":["b1","b2","b3"],
    "side_effects":[{"effect":"desc","severity":"low|medium|high"}],
    "references":[
      {"type":"pubmed","id":"PMID","title":"Study","url":"https://pubmed.ncbi.nlm.nih.gov/PMID/"},
      {"type":"examine","url":"https://examine.com/supplements/x/","title":"Examine.com — X"}
    ]
  },
  "stacking":["compound1"],
  "final_recommendation":"2-3 sentence actionable recommendation",
  "ai_note":"confidence note"
}

For product intent use:
{
  "detected_language":"English",
  "intent":"product",
  "name":"Category",
  "tagline":"Category description",
  "category":"supplement",
  "evidence_tier":"high",
  "safe_for_beginners":true,
  "legal_status":null,
  "products":[
    {"name":"Product","price_inr":1999,"rating":4.5,
     "badge":"🔥 Popular|💪 Balanced|🏅 Premium",
     "best_for":"goal/user type",
     "key_benefit":"main selling point"}
  ],
  "sections":{
    "what_it_is":"Overview","dosage":"General dosage","timing":"Timing",
    "how_to_take":"Usage","hydration":"Hydration","training_synergy":"Training",
    "cycling":"No cycling needed","benefits":["b1"],"side_effects":[],
    "references":[]
  },
  "stacking":[],"final_recommendation":"Buying advice","ai_note":"note"
}"""


def _claude(query: str, intent: str, entity_key: str | None,
            kb_items: list[dict], ev: dict) -> dict | None:
    if not ANTHROPIC_API_KEY:
        return None
    pm = ("\n\nLIVE PUBMED:\n" +
          "\n".join(f"- PMID {p}: https://pubmed.ncbi.nlm.nih.gov/{p}/"
                   for p in ev.get("pubmed_ids", [])[:5])
          ) if ev.get("pubmed_ids") else ""
    ex = (f"\n\nEXAMINE.COM: {ev['examine_url']}\n{ev.get('examine_summary','')[:300]}"
          if ev.get("examine_url") else "")
    kb_ctx = ""
    for item in kb_items[:2]:
        kb_ctx += f"\n\nKB — {item['name']}:\n{json.dumps({k:v for k,v in item.items() if k not in ['aliases','id']}, ensure_ascii=False)[:1200]}"
    msg = (f"Query: {query}\nIntent: {intent}\nEntity: {entity_key or 'general'}"
           f"{kb_ctx}{pm}{ex}")
    try:
        resp = requests.post(
            ANTHROPIC_URL,
            headers={"x-api-key": ANTHROPIC_API_KEY,
                     "anthropic-version": "2023-06-01",
                     "content-type": "application/json"},
            json={"model": "claude-sonnet-4-20250514", "max_tokens": 3500,
                  "system": _SYSTEM,
                  "messages": [{"role": "user", "content": msg}]},
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

def _kb_to_report(item: dict, ev: dict, intent: str = "research") -> dict:
    secs: dict = {
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
    for pid in (ev.get("pubmed_ids") or item.get("pubmed_ids", []))[:5]:
        secs["references"].append({"type": "pubmed", "id": pid,
                                   "title": f"PubMed ID: {pid}",
                                   "url": f"https://pubmed.ncbi.nlm.nih.gov/{pid}/"})
    for ref in item.get("research_refs", []):
        secs["references"].append({"type": "journal", "id": None, "title": ref, "url": None})
    exam = item.get("examine_url") or ev.get("examine_url")
    if exam:
        secs["references"].append({"type": "examine", "id": None,
                                   "title": f"Examine.com — {item['name']}", "url": exam})
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
        "ai_note":            "Generated from curated KB. Set ANTHROPIC_API_KEY for AI-enhanced reports.",
        "_source":            "kb",
    }


def _ai_to_report(ai: dict, ev: dict) -> dict:
    secs = ai.get("sections", {})
    existing = {r.get("id") for r in secs.get("references", [])}
    for pid in ev.get("pubmed_ids", []):
        if pid not in existing:
            secs.setdefault("references", []).append(
                {"type": "pubmed", "id": pid, "title": f"PubMed ID: {pid}",
                 "url": f"https://pubmed.ncbi.nlm.nih.gov/{pid}/"})
    if ev.get("examine_url"):
        secs.setdefault("references", []).append(
            {"type": "examine", "id": None,
             "title": f"Examine.com — {ai.get('name','Supplement')}",
             "url": ev["examine_url"]})
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


def _fallback(query: str, ts: str) -> dict:
    return {
        "name": f"Search: {query}", "tagline": "No exact match.",
        "category": "supplement", "evidence_tier": "moderate",
        "safe_for_beginners": True, "legal_status": None, "intent": "general",
        "sections": {
            "what_it_is": (
                f"No specific results for '{query}'. "
                "Try: Creatine monohydrate, Whey protein, Beta-alanine, "
                "Ostarine, Testosterone, BPC-157, HGH, Caffeine, Vitamin D3."
            ),
            "dosage": "—", "timing": "—", "how_to_take": "—", "hydration": "—",
            "training_synergy": "—", "cycling": "—",
            "benefits": [], "side_effects": [],
            "references": [
                {"type": "examine", "url": "https://examine.com", "title": "Examine.com", "id": None},
                {"type": "pubmed",  "url": "https://pubmed.ncbi.nlm.nih.gov", "title": "PubMed", "id": None},
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
    Main entry point — Perplexity + ChatGPT + Google style pipeline:

      1. Intent classification  (fast rule-based)
      2. Entity extraction      (longest-match, strict)
      3. Cache check            (key includes filters — FIX 2 backend)
      4. KB strict scoring      (entity-locked — FIX 1)
      5. Parallel live retrieval (PubMed · Examine · OpenFDA · SerpAPI)
      6. Evidence trust-scoring
      7. Claude synthesis       (intent-specific structured output)
      8. Cache write
      9. Return structured results
    """
    filters   = filters or []
    ts        = datetime.now(timezone.utc).isoformat()

    # 1. Intent
    intent = classify_intent(query)

    # 2. Entity extraction
    entity_key, allowed_ids = extract_primary_entity(query)

    # 3. Goal modifiers (query text + filter chips both count)
    goal_mods = list(set(_extract_goal_modifiers(query) + filters))

    # 4. Cache (key includes filters — every filter combo is a distinct entry)
    ckey   = _cache_key(query, filters)
    cached = _cache_get(ckey)
    if cached:
        for r in cached:
            r["_cached"] = True
        return cached

    # 5. KB strict scoring
    kb = _kb_strict(query, allowed_ids, goal_mods, filters, intent, limit=5)

    # 6. Live retrieval (parallel)
    lv  = _live(query, entity_key)
    ev  = _evidence(lv)

    # 7. Claude synthesis
    ai = _claude(query, intent, entity_key, kb, ev)

    results: list[dict] = []

    if ai and (ai.get("sections") or ai.get("products")):
        report = _ai_to_report(ai, ev)
        report["_timestamp"] = ts
        results.append(report)
        # Supplementary cards — ONLY from same entity group (no cross-contamination)
        for item in kb[1:3]:
            if item["name"].lower() != ai.get("name", "").lower():
                r = _kb_to_report(item, {}, intent)
                r["_timestamp"] = ts
                r["_supplementary"] = True
                results.append(r)
    else:
        for item in kb[:4]:
            r = _kb_to_report(item, ev if not results else {}, intent)
            r["_timestamp"] = ts
            results.append(r)

    if not results:
        results = [_fallback(query, ts)]

    _cache_set(ckey, query, results, source="ai" if ai else "kb")
    return results


def get_recommendations(recent_queries: list[str], user: dict) -> list[dict]:
    """Personalised recs from user history + profile. No API calls."""
    goal  = (user.get("goal") or "muscle_gain").replace("-", "_")
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
        if goal in item.get("tags", []):                sc += 4
        if item.get("safe_for_beginners") and level == "beginner":     sc += 3
        if not item.get("safe_for_beginners") and level in ("intermediate", "advanced"): sc += 2
        if item["evidence_tier"] in ("very_high", "high"):             sc += 1
        if sc <= 1:
            continue
        parts = [f"Matches your {goal.replace('_',' ')} goal"]
        if level == "beginner" and item.get("safe_for_beginners"):
            parts.append("beginner-friendly")
        if item["evidence_tier"] in ("very_high", "high"):
            parts.append("strong research support")
        recs.append({**item, "_sc": sc, "recommendation_reason": " · ".join(parts)})
    recs.sort(key=lambda x: x["_sc"], reverse=True)
    return [{k: v for k, v in r.items() if k != "_sc"} for r in recs[:6]]
