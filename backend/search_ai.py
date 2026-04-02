"""
search_ai.py  —  FitSearch AI  World-Class Fitness Research Engine  v5
=======================================================================
SELF-CONTAINED: Works without any API keys.
When ANTHROPIC_API_KEY is set, AI enhances every result.
Built-in knowledge base covers ALL fitness domains.

Architecture:
  Query → Intent → Domain → Entity/Topic Extraction
  → Cache → General-Topic KB OR Compound KB → AI Enhancement (optional)
  → Rich 17-section structured output
"""
from __future__ import annotations
import os, json, re, time, hashlib, sqlite3, threading, concurrent.futures
from datetime import datetime, timezone
from typing import Any
import requests

# ── API Keys (all optional — system works without them) ───────────────────
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
PUBMED_API_KEY    = os.getenv("PUBMED_API_KEY", "")
GOOGLE_SEARCH_API_KEY = os.getenv("GOOGLE_SEARCH_API_KEY", "")
GOOGLE_CX         = os.getenv("GOOGLE_CX", "")

# ── Paths ─────────────────────────────────────────────────────────────────
BASE_DIR      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_DB      = os.path.join(BASE_DIR, "database", "search_cache.db")
ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
PUBMED_SEARCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
PUBMED_FETCH  = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
CACHE_TTL_SEC = 86_400
_cache_lock   = threading.Lock()


# ═══════════════════════════════════════════════════════════════════════════
# INTENT CLASSIFICATION
# ═══════════════════════════════════════════════════════════════════════════

_INTENT_RULES: list[tuple[list[str], str]] = [
    (["best brand","top brand","buy india","price india","cheapest brand",
      "top 5","top 10","which brand","affordable","value for money"],"product"),
    (["workout plan","training plan","training split","diet plan","meal plan",
      "hypertrophy split","push pull","4 day split","5 day split","ppl split",
      "cutting diet","bulking diet","exercises for","best exercises",
      "workout for","training for","exercise for","fat loss exercises",
      "muscle building exercises","gym routine","workout routine",
      "training program","exercise plan","fitness routine"],"exercise"),
    (["nutrition plan","what to eat","diet for","meal for","food for",
      "macros for","calories for","eating for","high protein","protein diet",
      "keto diet","intermittent fasting","meal timing"],"nutrition"),
    (["dosage","dose","how much","how many mg","how many grams",
      "mcg","iu per day","serving size","loading phase","maintenance dose"],"dosage"),
    (["side effect","adverse effect","risk","dangerous","harmful",
      "is it safe","liver damage","kidney","toxicity","health risk",
      "long term risk","safe for"],"side_effects"),
    (["vs","versus","compare","comparison","better than",
      "difference between","which is better","which one"],"compare"),
    (["cycle","protocol","pct","post cycle","on cycle",
      "week cycle","blast cruise","stack protocol"],"cycle"),
    (["what is","what are","how does","explain","define",
      "kya hai","क्या है","was ist"],"explain"),
    (["best","recommend","should i","beginner","which one",
      "ideal for","good for","top choice","for muscle gain",
      "for fat loss","for strength","for beginners"],"recommend"),
]

def classify_intent(query: str) -> str:
    q = query.lower()
    for triggers, label in _INTENT_RULES:
        if any(t in q for t in triggers):
            return label
    return "research"


# ── Goal modifiers ────────────────────────────────────────────────────────
_GOAL_PHRASES: dict[str, list[str]] = {
    "muscle_gain": ["muscle gain","bulking","mass gain","hypertrophy","build muscle","lean mass"],
    "fat_loss":    ["fat loss","weight loss","cutting","shred","lean","fat burning","burn fat","lose fat","slim"],
    "strength":    ["strength","powerlifting","power","strong","get stronger","1rm"],
    "endurance":   ["endurance","cardio","stamina","aerobic","running","cycling","hiit"],
    "recovery":    ["recovery","healing","injury","soreness","doms","rehab"],
    "female":      ["female","women","woman","girl","females","ladies"],
    "beginner":    ["beginner","starter","new to","first time","newbie","noob"],
    "advanced":    ["advanced","experienced","intermediate","serious athlete"],
}

def _extract_goal_modifiers(query: str) -> list[str]:
    q = query.lower()
    return [tag for tag, phrases in _GOAL_PHRASES.items() if any(p in q for p in phrases)]


# ═══════════════════════════════════════════════════════════════════════════
# DOMAIN ROUTING
# ═══════════════════════════════════════════════════════════════════════════

QUERY_DOMAINS: dict[str, list[str]] = {
    "muscle_gain":  ["muscle gain","bulking","hypertrophy","build muscle","lean mass"],
    "fat_loss":     ["fat loss","cutting","weight loss","shred","burn fat","lose weight","lose fat","slim","tone"],
    "strength":     ["strength","powerlifting","power","strong","1rm"],
    "endurance":    ["endurance","cardio","stamina","aerobic","running","cycling","marathon","hiit"],
    "recovery":     ["recovery","healing","injury","soreness","doms","rehab"],
    "supplements":  ["creatine","whey","protein","pre workout","bcaa","supplement","beta alanine",
                     "citrulline","caffeine","fish oil","vitamin","zinc","magnesium","omega"],
    "steroids":     ["testosterone","tren","trenbolone","anavar","dbol","dianabol",
                     "nandrolone","deca","winstrol","steroid","anabolic","aas","pct"],
    "peptides":     ["mk677","bpc","bpc-157","ipamorelin","cjc","tb500","tb-500","sermorelin","ghrp","peptide"],
    "hgh":          ["hgh","growth hormone","somatropin","human growth","igf"],
    "sarms":        ["ostarine","lgd","ligandrol","rad140","testolone","cardarine","sarm","sarms","mk-2866"],
    "nutrition":    ["diet","nutrition","meal plan","macros","protein intake","carbs","calories",
                     "food","eating","keto","intermittent fasting"],
    "exercise":     ["exercise","workout","training","gym","lifting","sets","reps","program",
                     "routine","split","exercises for","best exercises","workout for","training for"],
}

def detect_domain(query: str) -> str:
    q = query.lower()
    scores: dict[str, int] = {}
    for domain, keywords in QUERY_DOMAINS.items():
        sc = sum(1 for kw in keywords if kw in q)
        if sc > 0:
            scores[domain] = sc
    return max(scores, key=lambda x: scores[x]) if scores else "general_fitness"


# ═══════════════════════════════════════════════════════════════════════════
# ENTITY GROUPS — compound/supplement specific queries
# ═══════════════════════════════════════════════════════════════════════════

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
    """Returns (entity_key, allowed_kb_ids). Returns (None,[]) for general topics."""
    q = query.lower()
    for phrase, key in ENTITY_TRIGGERS:
        if phrase in q:
            return key, ENTITY_GROUPS.get(key, [])
    return None, []


# ═══════════════════════════════════════════════════════════════════════════
# GENERAL TOPIC KNOWLEDGE BASE
# Topics not tied to specific compounds: exercise, training, nutrition, etc.
# These handle ALL non-compound queries so the system NEVER returns a fallback.
# ═══════════════════════════════════════════════════════════════════════════

GENERAL_TOPICS: list[dict] = [
    {
        "id": "fat_loss_exercise",
        "triggers": ["fat loss exercise","fat loss workout","fat burning exercise",
                     "exercises for fat loss","workout for fat loss","cardio for fat loss",
                     "exercise for weight loss","fat loss training","burn fat exercise",
                     "fat loss for females","fat loss for women","best exercises fat loss",
                     "exercise to lose fat","exercises to lose weight","exercise lose weight"],
        "name": "Fat Loss Exercises",
        "tagline": "Evidence-based exercise selection for maximising fat loss while preserving muscle.",
        "category": "exercise", "evidence_tier": "very_high", "safe_for_beginners": True,
        "intent": "exercise",
        "what_it_is": "Fat loss through exercise is driven by creating a caloric deficit, elevating metabolic rate, and preserving lean muscle mass. The most effective approach combines resistance training (to preserve/build muscle and elevate BMR) with cardiovascular training (to directly burn calories and improve cardiovascular health). Neither alone is as effective as the combination.",
        "how_it_works": "Exercise burns calories directly and elevates metabolic rate for hours post-exercise (EPOC — excess post-exercise oxygen consumption). Resistance training builds metabolically active muscle tissue, permanently raising your BMR. High-intensity intervals (HIIT) produce the greatest EPOC effect. The combination of both creates superior fat loss outcomes vs cardio alone.",
        "types": [
            {"name": "Resistance Training (Weight Training)", "best_for": "Preserving muscle, elevating BMR, long-term fat loss", "evidence": "Very High"},
            {"name": "HIIT (High-Intensity Interval Training)", "best_for": "Maximum calorie burn in minimum time, EPOC", "evidence": "Very High"},
            {"name": "Steady-State Cardio (LISS)", "best_for": "Active recovery, additional calorie burn, beginners", "evidence": "High"},
            {"name": "Circuit Training", "best_for": "Combining strength + cardio, time efficiency", "evidence": "High"},
            {"name": "Walking (especially fasted)", "best_for": "Low-impact daily calorie burn, recovery", "evidence": "High"},
        ],
        "dosage": "Training Volume: 3–5 sessions/week total. Resistance training: 3–4 days (3 sets × 8–15 reps per exercise, 6–10 exercises). HIIT: 2–3 days (20–30 min). LISS cardio: 2–3 days (30–60 min). Total weekly exercise: 300–500 min for fat loss.",
        "timing": "Resistance training any time. Fasted cardio (morning, before eating) may marginally increase fat oxidation. Avoid intense cardio immediately before resistance training. Allow 1–2 rest days per week.",
        "how_to_take": "For females: Prioritise resistance training over cardio. Women respond excellently to progressive overload. Best fat loss exercises: Squats, deadlifts, hip thrusts, lunges, push-ups, rows, HIIT circuits, walking lunges, step-ups.",
        "hydration": "2.5–3.5 L water daily. Increase by 500ml per hour of training. Electrolytes essential if training >60 min in heat.",
        "training_synergy": "Exercise is most effective in a calorie deficit (300–500 kcal/day below TDEE). High protein intake (1.8–2.2 g/kg) preserves muscle during fat loss. Sleep 7–9 hours — poor sleep elevates cortisol and impairs fat loss.",
        "best_ways_to_use": [
            "Prioritise resistance training 3–4x/week as the foundation",
            "Add HIIT 2x/week for metabolic boost (20–30 min sessions)",
            "Daily walking 7,000–10,000 steps as low-impact calorie burn",
            "Maintain calorie deficit through diet — exercise alone rarely creates sufficient deficit",
            "Progressive overload in resistance training to preserve muscle",
            "Track workouts to ensure progressive overload",
        ],
        "who_should_use": ["Anyone seeking fat loss", "Females at all levels", "Beginners to advanced athletes", "Those wanting to preserve muscle while losing fat"],
        "who_should_avoid": ["Those with acute injuries (modify exercises)", "Postpartum women (consult physician first)", "Those with cardiovascular conditions (medical clearance needed)"],
        "benefits": ["Direct calorie expenditure during exercise", "Elevated BMR through muscle preservation/gain", "Improved insulin sensitivity", "Enhanced EPOC (afterburn effect)", "Hormonal improvements (reduced cortisol, improved leptin sensitivity)", "Cardiovascular health improvement"],
        "side_effects": [{"effect": "Muscle soreness (DOMS) — normal adaptation", "severity": "low"}, {"effect": "Overtraining if volume too high without recovery", "severity": "medium"}],
        "research_evidence": [
            {"study": "Willis et al. — STRRIDE AT/RT trial", "finding": "Combination of resistance + aerobic training produces superior fat loss vs aerobic training alone", "source": "Am J Physiol Endocrinol Metab, 2012"},
            {"study": "Boutcher SH", "finding": "HIIT produces greater reductions in abdominal and subcutaneous fat vs LISS despite lower exercise volume", "source": "J Obes, 2011"},
            {"study": "Stiegler & Cunliffe", "finding": "Resistance training during caloric restriction preserves 93% of lean mass vs 69% with cardio only", "source": "Sports Med, 2006"},
        ],
        "articles": [
            {"title": "Exercise for Weight Loss: Calories Burned in 1 Hour", "author": "Mayo Clinic Staff", "source": "Mayo Clinic", "url": "https://www.mayoclinic.org/healthy-lifestyle/weight-loss/in-depth/exercise/art-20050999"},
            {"title": "The Best Exercises for Weight Loss", "author": "Healthline Editorial", "source": "Healthline", "url": "https://www.healthline.com/nutrition/best-exercise-for-weight-loss"},
            {"title": "Resistance Training for Fat Loss", "author": "Examine Team", "source": "Examine.com", "url": "https://examine.com/topics/fat-loss/"},
        ],
        "magazines": [
            {"title": "The Ultimate Fat Loss Workout Plan", "publisher": "Women's Health", "url": "https://www.womenshealthmag.com/fitness/fat-loss-workouts/"},
            {"title": "Best Fat-Burning Exercises", "publisher": "Men's Health", "url": "https://www.menshealth.com/fitness/fat-burning-exercises/"},
            {"title": "Science-Based Fat Loss Training Guide", "publisher": "T-Nation", "url": "https://www.t-nation.com/training/fat-loss/"},
        ],
        "books": [
            {"title": "Lean In 15", "author": "Joe Wicks", "year": "2015"},
            {"title": "The New Rules of Lifting for Women", "author": "Lou Schuler & Alwyn Cosgrove", "year": "2008"},
            {"title": "Burn the Fat, Feed the Muscle", "author": "Tom Venuto", "year": "2013"},
            {"title": "Bigger Leaner Stronger", "author": "Michael Matthews", "year": "2019"},
        ],
        "videos": [
            {"title": "The PERFECT Fat Loss Workout (Science-Based)", "channel": "Jeff Nippard", "platform": "YouTube", "url": "https://www.youtube.com/results?search_query=jeff+nippard+fat+loss+workout+science"},
            {"title": "Fat Loss for Women — Complete Guide", "channel": "Stephanie Buttermore", "platform": "YouTube", "url": "https://www.youtube.com/results?search_query=stephanie+buttermore+fat+loss+for+women"},
            {"title": "BEST Exercises for Fat Loss (Ranked)", "channel": "Renaissance Periodization", "platform": "YouTube", "url": "https://www.youtube.com/results?search_query=renaissance+periodization+best+exercises+fat+loss"},
            {"title": "The Science of Getting Lean", "channel": "Jeremy Ethier", "platform": "YouTube", "url": "https://www.youtube.com/results?search_query=jeremy+ethier+science+fat+loss"},
        ],
        "ai_summary": "The most effective fat loss exercise strategy combines resistance training (3–4x/week) as the primary driver — which preserves muscle and elevates metabolic rate — with HIIT (2x/week) for maximum calorie burn. For females specifically, resistance training is critical to avoid the 'skinny fat' outcome common with cardio-only approaches. Exercise alone rarely creates sufficient deficit; nutrition is responsible for 70–80% of fat loss results.",
        "stacking": ["High-protein diet (1.8–2.2 g/kg)", "Calorie deficit (300–500 kcal)", "Creatine (preserves strength during deficit)", "Caffeine (fat oxidation + performance)"],
        "final_recommendation": "Start with 3 days resistance training + 2 days walking/HIIT. Build progressive overload in the weight room. Pair with a 300–500 kcal daily deficit from diet. Aim for 0.5–1% bodyweight loss per week to preserve muscle. Most importantly: consistency over 12–16 weeks beats any perfect short-term plan.",
    },
    {
        "id": "muscle_gain_training",
        "triggers": ["muscle gain workout","muscle building training","build muscle workout",
                     "hypertrophy training","muscle building program","gain muscle workout",
                     "bodybuilding training","mass building workout","best exercises muscle gain",
                     "workout for muscle gain","training for muscle","muscle building exercises",
                     "hypertrophy program","gain muscle exercises","weight training muscle"],
        "name": "Muscle Gain Training",
        "tagline": "Science-based resistance training program for maximising muscle hypertrophy.",
        "category": "exercise", "evidence_tier": "very_high", "safe_for_beginners": True,
        "intent": "exercise",
        "what_it_is": "Muscle hypertrophy (growth) occurs when muscle protein synthesis exceeds muscle protein breakdown over time. This requires a progressive mechanical stimulus (resistance training), adequate protein, sufficient calories, and recovery. Hypertrophy training falls into two mechanisms: mechanical tension (heavy loads, full ROM) and metabolic stress (moderate loads, higher reps, pump).",
        "how_it_works": "Resistance training creates micro-tears in muscle fibres. Recovery with adequate protein triggers the muscle to repair larger and stronger — this is muscle protein synthesis (MPS). The primary drivers are: mechanical tension (the stretch and squeeze under load), metabolic stress (the pump/burn), and muscle damage. Progressive overload — gradually increasing stress — ensures continuous adaptation.",
        "types": [
            {"name": "PPL (Push/Pull/Legs)", "best_for": "Intermediate+, 6 days/week, high volume", "evidence": "Very High"},
            {"name": "Upper/Lower Split", "best_for": "Intermediate, 4 days/week, balanced", "evidence": "Very High"},
            {"name": "Full Body (3x/week)", "best_for": "Beginners, maximises muscle protein synthesis frequency", "evidence": "Very High"},
            {"name": "Bro Split (1 muscle/day)", "best_for": "Advanced, high volume per muscle", "evidence": "High"},
            {"name": "Conjugate/Westside", "best_for": "Strength + hypertrophy, powerlifting base", "evidence": "High"},
        ],
        "dosage": "Training Volume: 10–20 working sets per muscle group per week. 6–20 reps per set (8–12 for hypertrophy sweet spot). 3–5 sets per exercise. 60–90 sec rest for hypertrophy, 3–5 min for strength. Train each muscle 2–3x/week for optimal frequency.",
        "timing": "4–5 training days per week optimal for most intermediate lifters. Train each muscle group 2–3x/week. Evening training shows marginal strength advantages but time of day matters far less than consistency.",
        "how_to_take": "Best hypertrophy exercises by muscle: Chest — bench press, incline DB press, cable flyes. Back — deadlift, barbell rows, pull-ups, cable rows. Quads — squats, leg press, lunges. Hamstrings — Romanian deadlifts, leg curl. Shoulders — OHP, lateral raises. Arms — barbell curls, tricep pushdowns.",
        "hydration": "3 L/day minimum. Muscle is 75% water — dehydration directly impairs strength and protein synthesis.",
        "training_synergy": "High protein intake (1.6–2.2 g/kg/day) is the primary nutritional driver. Calorie surplus (250–500 kcal above TDEE) accelerates muscle gain but not required (body recomposition possible). Creatine monohydrate adds 5–15% strength increase. Sleep 8–9 hours — 70% of muscle repair happens during sleep.",
        "best_ways_to_use": [
            "Progressive overload: add weight, reps, or sets each week",
            "Train to near failure (2 reps in reserve) for maximum hypertrophy",
            "Full range of motion — stretched position produces more hypertrophy",
            "Compound movements first (squats, deadlifts, bench) then isolation",
            "Track every workout — what gets measured gets improved",
            "Prioritise 7–9 hours sleep for muscle recovery",
        ],
        "who_should_use": ["Anyone wanting to build muscle mass", "Beginners to advanced athletes", "Females seeking body recomposition", "Those recovering from injury (modified)"],
        "who_should_avoid": ["Acute injury — modified movements required", "Those without medical clearance for resistance training"],
        "benefits": ["Increased muscle mass and size", "Elevated basal metabolic rate", "Improved strength and power", "Enhanced insulin sensitivity", "Better bone density", "Improved posture and joint stability", "Hormone optimisation (testosterone response)"],
        "side_effects": [{"effect": "DOMS (delayed onset muscle soreness) — normal adaptation", "severity": "low"}, {"effect": "Injury risk if form is poor or overloading too fast", "severity": "medium"}],
        "research_evidence": [
            {"study": "Schoenfeld BJ meta-analysis", "finding": "Training each muscle 2–3x/week produces 3.1% greater hypertrophy than 1x/week with equal volume", "source": "J Strength Cond Res, 2016"},
            {"study": "Morton et al.", "finding": "10–20 sets per muscle per week optimal for hypertrophy; below 10 sets = suboptimal, above 20 = diminishing returns", "source": "J Physiol, 2019"},
            {"study": "Krieger JW meta-analysis", "finding": "Multiple sets (3+) produce 40% greater hypertrophy vs single sets", "source": "J Strength Cond Res, 2010"},
        ],
        "articles": [
            {"title": "The Mechanisms of Muscle Hypertrophy", "author": "Schoenfeld BJ", "source": "J Strength Cond Res", "url": "https://pubmed.ncbi.nlm.nih.gov/20847704/"},
            {"title": "How to Build Muscle: A Complete Guide", "author": "Healthline Editorial", "source": "Healthline", "url": "https://www.healthline.com/nutrition/how-to-build-muscle"},
        ],
        "magazines": [
            {"title": "The Ultimate Hypertrophy Guide", "publisher": "Muscle & Fitness", "url": "https://www.muscleandfitness.com/training/build-muscle/"},
            {"title": "Science-Based Muscle Building Program", "publisher": "T-Nation", "url": "https://www.t-nation.com/training/hypertrophy/"},
        ],
        "books": [
            {"title": "The Science of Lifting", "author": "Greg Nuckols", "year": "2019"},
            {"title": "Bigger Leaner Stronger", "author": "Michael Matthews", "year": "2019"},
            {"title": "The New Encyclopedia of Modern Bodybuilding", "author": "Arnold Schwarzenegger", "year": "1999"},
            {"title": "Strength Training Anatomy", "author": "Frédéric Delavier", "year": "2010"},
        ],
        "videos": [
            {"title": "The MOST Effective Science-Based Hypertrophy Program", "channel": "Jeff Nippard", "platform": "YouTube", "url": "https://www.youtube.com/results?search_query=jeff+nippard+hypertrophy+program"},
            {"title": "How to Build Muscle (Explained in 5 Levels)", "channel": "Jeremy Ethier", "platform": "YouTube", "url": "https://www.youtube.com/results?search_query=jeremy+ethier+how+to+build+muscle"},
            {"title": "Science of Muscle Growth", "channel": "Renaissance Periodization", "platform": "YouTube", "url": "https://www.youtube.com/results?search_query=renaissance+periodization+muscle+growth+science"},
        ],
        "ai_summary": "Muscle hypertrophy requires progressive overload, sufficient volume (10–20 sets/muscle/week), high protein (1.6–2.2 g/kg), and adequate recovery. Training each muscle 2–3x per week with 8–20 rep ranges is the scientifically optimal approach. Consistency over 6–12 months produces the most dramatic transformations.",
        "stacking": ["Creatine monohydrate (5g/day)", "Whey protein (post-workout)", "Calorie surplus 250–500 kcal"],
        "final_recommendation": "Beginners: Start with 3x/week full-body programme. Intermediate: Move to 4-day upper/lower split. Advanced: 5–6 day PPL. Always prioritise compound movements, progressive overload, and sufficient protein. Results require 6–12 months of consistent training.",
    },
    {
        "id": "beginner_workout",
        "triggers": ["beginner workout","beginner training","beginner gym","beginner routine",
                     "beginner exercise","start working out","gym for beginners","new to gym",
                     "how to start gym","beginner fitness","first time gym","gym beginner guide",
                     "workout for beginners","training for beginners","exercises for beginners",
                     "beginner program","starting workout","how to begin gym"],
        "name": "Beginner Workout Guide",
        "tagline": "The complete science-based starter guide to building your first training programme.",
        "category": "exercise", "evidence_tier": "very_high", "safe_for_beginners": True,
        "intent": "exercise",
        "what_it_is": "A beginner training programme is designed for those with less than 6 months of consistent resistance training experience. Beginners are in the uniquely advantaged 'newbie gains' period — they can build strength and muscle simultaneously while losing fat. Any progressive stimulus produces rapid adaptation in this phase.",
        "how_it_works": "Beginners experience rapid neuromuscular adaptations (strength gains from improved motor unit recruitment) in the first 4–8 weeks before true hypertrophy begins. Full-body sessions 3x/week maximise muscle protein synthesis frequency. Simple linear progression (adding 2.5–5 kg per week) works optimally for beginners.",
        "types": [
            {"name": "StrongLifts 5×5", "best_for": "Pure strength foundation, very simple", "evidence": "Very High"},
            {"name": "Starting Strength", "best_for": "Strength-focused, proven beginner system", "evidence": "Very High"},
            {"name": "GZCLP", "best_for": "Strength + hypertrophy balance", "evidence": "High"},
            {"name": "3-Day Full Body (PPL light)", "best_for": "Balanced muscle development", "evidence": "Very High"},
            {"name": "Bodyweight Foundation", "best_for": "No gym access, building base fitness", "evidence": "High"},
        ],
        "dosage": "3 days/week, full-body sessions. 3–5 exercises per session. 3 sets × 5–8 reps for compound lifts. 45–60 min per session maximum. Progressive overload: add 2.5 kg/session for upper body, 5 kg/session for lower body.",
        "timing": "3 non-consecutive days (e.g., Mon/Wed/Fri). Rest days between training sessions. 8–9 hours sleep minimum for newbie gains.",
        "how_to_take": "Beginner session template: 1) Squat or leg press (5×5), 2) Bench press or push-ups (3×8), 3) Barbell rows or cable rows (3×8), 4) Overhead press (3×8), 5) Deadlift (1×5). Learn form with light weight first. Film yourself to check technique.",
        "hydration": "2.5–3 L/day. Take water to every session.",
        "training_synergy": "Protein: 1.6–2 g/kg bodyweight/day critical for newbie gains. Calories at maintenance or slight surplus. Quality sleep — 8 hours minimum. Consistency (showing up 3x/week for 12 weeks) beats any perfect programme.",
        "best_ways_to_use": [
            "Master the big 4: squat, deadlift, bench press, overhead press",
            "Start light — focus on perfect form for first 4 weeks",
            "Add weight every single session while form allows",
            "Track workouts in a notebook or app",
            "3 months consistent training before changing programme",
            "Protein at every meal — eggs, chicken, fish, dairy, protein shakes",
        ],
        "who_should_use": ["Absolute beginners", "Those returning after long break", "Anyone who hasn't lifted consistently in 6+ months"],
        "who_should_avoid": ["Those with untreated injuries (see physio first)", "Pre-existing medical conditions (get clearance)"],
        "benefits": ["Rapid strength gains (neuromuscular adaptation)", "Body recomposition (gain muscle + lose fat simultaneously)", "Improved metabolic health", "Foundation for long-term athletic development", "Bone density improvement", "Mental health benefits"],
        "side_effects": [{"effect": "DOMS (muscle soreness) in first 2–4 weeks", "severity": "low"}, {"effect": "Poor technique risk — learn form before loading", "severity": "medium"}],
        "research_evidence": [
            {"study": "Rhea et al.", "finding": "Linear periodization produces 2× strength gains vs non-periodized training in beginners", "source": "J Strength Cond Res, 2002"},
            {"study": "Aaberg E", "finding": "Full-body 3x/week training superior to split routines for beginner muscle development", "source": "NSCA, 2007"},
        ],
        "articles": [
            {"title": "The Beginner's Guide to the Gym", "author": "Healthline Editorial", "source": "Healthline", "url": "https://www.healthline.com/health/exercise-fitness/gym-for-beginners"},
            {"title": "How to Start Strength Training", "author": "Greg Nuckols", "source": "Stronger by Science", "url": "https://www.strongerbyscience.com/"},
        ],
        "magazines": [
            {"title": "Beginner's Guide to Lifting Weights", "publisher": "Men's Health", "url": "https://www.menshealth.com/fitness/beginners-guide-lifting/"},
            {"title": "The Complete Beginner's Workout Plan", "publisher": "Women's Health", "url": "https://www.womenshealthmag.com/fitness/beginners-workout/"},
        ],
        "books": [
            {"title": "Starting Strength", "author": "Mark Rippetoe", "year": "2011"},
            {"title": "Bigger Leaner Stronger", "author": "Michael Matthews", "year": "2019"},
            {"title": "The New Rules of Lifting", "author": "Lou Schuler & Alwyn Cosgrove", "year": "2006"},
        ],
        "videos": [
            {"title": "The Perfect Beginner Workout (Science-Based)", "channel": "Jeremy Ethier", "platform": "YouTube", "url": "https://www.youtube.com/results?search_query=jeremy+ethier+perfect+beginner+workout"},
            {"title": "Beginner's Guide to Lifting Weights", "channel": "Jeff Nippard", "platform": "YouTube", "url": "https://www.youtube.com/results?search_query=jeff+nippard+beginner+guide+lifting"},
            {"title": "How to Start Going to the Gym", "channel": "Alan Thrall", "platform": "YouTube", "url": "https://www.youtube.com/results?search_query=alan+thrall+how+to+start+gym"},
        ],
        "ai_summary": "Beginners are in the most advantageous phase of their training career — capable of simultaneous muscle gain and fat loss. 3x/week full-body training with compound movements and linear progression is the scientifically optimal approach. Consistency for 3–6 months and adequate protein intake (1.6–2 g/kg) are the only requirements for dramatic transformation.",
        "stacking": ["Whey protein (post-workout)", "Creatine monohydrate (optional, 5g/day)", "Good sleep (8+ hours)"],
        "final_recommendation": "Start with StrongLifts 5×5 or a 3-day full-body programme. Learn form with light weight first 4 weeks. Add weight progressively. Eat 1.6–2 g/kg protein daily. Show up 3 days per week for 12 weeks without missing. The programme matters far less than the consistency.",
    },
    {
        "id": "hiit_cardio",
        "triggers": ["hiit","hiit cardio","hiit workout","hiit training","interval training",
                     "high intensity interval","cardio workout","cardio training","best cardio",
                     "cardio for weight loss","cardio exercise","aerobic training","endurance training",
                     "cardio plan","running program","cycling training","fasted cardio"],
        "name": "HIIT & Cardio Training",
        "tagline": "Evidence-based cardiovascular training guide for fat loss, fitness, and performance.",
        "category": "exercise", "evidence_tier": "very_high", "safe_for_beginners": True,
        "intent": "exercise",
        "what_it_is": "HIIT (High-Intensity Interval Training) alternates periods of maximum effort with recovery periods. LISS (Low-Intensity Steady State) maintains moderate intensity continuously. Both improve cardiovascular fitness and burn calories, but through different mechanisms. HIIT produces greater EPOC (afterburn) while LISS is lower impact and sustainable for greater duration.",
        "how_it_works": "HIIT activates both aerobic and anaerobic energy systems, elevates heart rate to 80–95% max HR, and creates significant metabolic demand that continues post-exercise (EPOC lasts 12–48 hours). LISS operates at 50–65% max HR, primarily using fat as fuel, and is sustainable for 30–90+ minutes. Heart adaptations (larger stroke volume, lower resting HR) occur with both.",
        "types": [
            {"name": "Tabata (20s on / 10s off × 8)", "best_for": "Maximum intensity, 4-min protocol", "evidence": "Very High"},
            {"name": "Sprint Intervals (30s sprint / 90s walk)", "best_for": "Fat loss, anaerobic capacity", "evidence": "Very High"},
            {"name": "Steady-State Running/Cycling", "best_for": "Endurance base, active recovery", "evidence": "Very High"},
            {"name": "Zone 2 Cardio (conversational pace)", "best_for": "Mitochondrial density, metabolic health", "evidence": "Very High"},
            {"name": "Stairmaster / Incline Walk", "best_for": "Low impact, high calorie burn", "evidence": "High"},
        ],
        "dosage": "HIIT: 2–3 sessions/week, 20–30 min each. LISS: 3–5 sessions/week, 30–60 min each. Beginners start with 2 cardio sessions/week and build. Do not exceed 5 HIIT sessions/week — overtraining risk and impairs recovery.",
        "timing": "Fasted morning cardio marginally increases fat oxidation. Avoid intense cardio within 3 hours of resistance training (impairs anabolic signalling). Separate HIIT and resistance training by 6+ hours when possible.",
        "how_to_take": "HIIT example: 5 min warm-up, 8 rounds of (30s max effort / 90s walk), 5 min cool-down. Equipment options: sprint, cycling, rowing, kettlebell swings, jump rope, stairs.",
        "hydration": "500ml water 30 min before cardio. 150–250ml every 20 min during. Electrolytes for sessions >60 min.",
        "training_synergy": "Cardio + calorie deficit = fat loss. Cardio alone without protein = muscle loss risk. Ensure 1.8–2 g/kg protein when doing high cardio volume. Zone 2 cardio improves mitochondrial density, which benefits all athletic performance including resistance training.",
        "best_ways_to_use": [
            "Combine 2x HIIT + 2–3x LISS per week for optimal fat loss",
            "Zone 2 training (60–65% max HR) builds aerobic base without impacting recovery",
            "Fasted morning walks are underrated — 10,000 steps/day burns 400–600 kcal",
            "Rowing machine offers full-body HIIT option with minimal joint impact",
            "Track heart rate — a $30 HR monitor transforms training",
        ],
        "who_should_use": ["Anyone wanting cardiovascular fitness", "Fat loss seekers", "Athletes", "Those limited on time (HIIT efficiency)"],
        "who_should_avoid": ["HIIT: beginners (build LISS base first)", "Those with heart conditions (medical clearance needed)", "Overtrainers (add rest, not more cardio)"],
        "benefits": ["Fat burning during and after exercise", "Cardiovascular health improvement", "VO2 max improvement", "Insulin sensitivity improvement", "Mental health benefits", "Reduced resting heart rate", "Improved lung capacity"],
        "side_effects": [{"effect": "Joint stress with high-impact HIIT — choose lower-impact options if needed", "severity": "low"}, {"effect": "Overtraining with excessive HIIT frequency", "severity": "medium"}],
        "research_evidence": [
            {"study": "Tabata et al.", "finding": "4-min Tabata protocol improved VO2max by 14.5% and anaerobic capacity by 28% in 6 weeks", "source": "Med Sci Sports Exerc, 1996"},
            {"study": "Boutcher SH", "finding": "HIIT produced 3× more subcutaneous fat loss than LISS with 40% less time investment", "source": "J Obes, 2011"},
        ],
        "articles": [
            {"title": "HIIT vs Steady-State Cardio — Which is Better?", "author": "Examine Team", "source": "Examine.com", "url": "https://examine.com/topics/cardio/"},
            {"title": "Zone 2 Training: Benefits and How to Do It", "author": "Peter Attia", "source": "Peter Attia MD", "url": "https://peterattiamd.com/zone2training/"},
        ],
        "magazines": [
            {"title": "The Best HIIT Workouts for Fat Loss", "publisher": "Men's Health", "url": "https://www.menshealth.com/fitness/hiit-workouts/"},
            {"title": "Science-Based Cardio Guide", "publisher": "T-Nation", "url": "https://www.t-nation.com/training/cardio/"},
        ],
        "books": [
            {"title": "Becoming a Supple Leopard", "author": "Kelly Starrett", "year": "2013"},
            {"title": "The One-Minute Workout", "author": "Martin Gibala", "year": "2017"},
            {"title": "80/20 Running", "author": "Matt Fitzgerald", "year": "2014"},
        ],
        "videos": [
            {"title": "How to Do HIIT Correctly (Science-Based)", "channel": "Jeff Nippard", "platform": "YouTube", "url": "https://www.youtube.com/results?search_query=jeff+nippard+hiit+science"},
            {"title": "Zone 2 Training for Fat Loss", "channel": "Thomas DeLauer", "platform": "YouTube", "url": "https://www.youtube.com/results?search_query=thomas+delauer+zone+2+cardio+fat+loss"},
            {"title": "Best Cardio for Fat Loss", "channel": "Jeremy Ethier", "platform": "YouTube", "url": "https://www.youtube.com/results?search_query=jeremy+ethier+best+cardio+fat+loss"},
        ],
        "ai_summary": "HIIT is superior to LISS for time-efficient fat loss due to its EPOC effect and metabolic adaptations. However, 2–3 HIIT sessions/week maximum — more is counterproductive. Zone 2 cardio (conversational pace) for the remaining sessions improves mitochondrial density and aids recovery. Daily walking is underrated as the most sustainable calorie burner.",
        "stacking": ["Caffeine pre-HIIT (+15% performance)", "Beta-alanine for sprint endurance", "Electrolytes for sessions >60 min"],
        "final_recommendation": "2 HIIT sessions/week (20–25 min each) + daily walking (8,000–10,000 steps) + 2 Zone 2 cardio sessions (30–45 min each) is the evidence-based sweet spot for fat loss without overtraining. Add resistance training as the foundation.",
    },
    {
        "id": "protein_diet",
        "triggers": ["high protein diet","protein diet","protein meal plan","protein nutrition",
                     "diet for muscle gain","nutrition for muscle","eating for muscle",
                     "macros muscle gain","diet plan muscle","muscle diet","nutrition muscle building",
                     "protein intake muscle","how much protein","daily protein","protein for bodybuilding",
                     "nutrition plan","eating plan","diet plan","meal plan muscle"],
        "name": "High Protein Diet for Muscle Gain",
        "tagline": "Evidence-based nutrition strategy for maximising muscle protein synthesis and body composition.",
        "category": "nutrition", "evidence_tier": "very_high", "safe_for_beginners": True,
        "intent": "nutrition",
        "what_it_is": "A high-protein diet (1.6–2.4 g/kg bodyweight/day) maximises muscle protein synthesis (MPS), preserves muscle during fat loss, and supports recovery. Protein is the only macronutrient that directly builds muscle tissue. The leucine threshold (2–3 g leucine per meal) triggers MPS — requiring approximately 30–40 g protein per meal from complete sources.",
        "how_it_works": "Dietary protein is broken down into amino acids absorbed into the bloodstream. The essential amino acid leucine acts as the primary MPS trigger, activating the mTOR pathway. Distributing protein across 4–6 meals ensures sustained leucine elevation throughout the day, maximising the total MPS response. Post-workout protein accelerates recovery via the anabolic window (0–2 hours post-training).",
        "types": [
            {"name": "Whole-food protein sources", "best_for": "Micronutrients, satiety, long-term health", "evidence": "Very High"},
            {"name": "Whey protein supplementation", "best_for": "Convenient fast-digesting post-workout", "evidence": "Very High"},
            {"name": "Casein protein", "best_for": "Slow-digesting, before bed, anti-catabolic", "evidence": "High"},
            {"name": "Plant-based protein", "best_for": "Vegans/vegetarians, digestive preference", "evidence": "High"},
        ],
        "dosage": "Protein: 1.6–2.2 g/kg bodyweight/day for muscle building; 2.2–2.4 g/kg during cutting. Carbohydrates: 3–5 g/kg for training performance. Fats: 0.8–1.2 g/kg minimum for hormonal health. Total calories: TDEE + 250–500 kcal for lean bulk.",
        "timing": "Distribute protein across 4–5 meals (30–40 g per meal). Post-workout meal within 2 hours. Pre-sleep casein/cottage cheese. Protein with every meal — skip no-protein meals.",
        "how_to_take": "Best protein sources (per 100g): Chicken breast — 31g. Tuna — 28g. Eggs — 13g (6 eggs = 78g protein). Greek yogurt — 10g. Cottage cheese — 11g. Whey protein — 80–90g. Lentils — 9g. Tofu — 8g.",
        "hydration": "Increase water intake with high protein (kidneys work harder). 3 L/day minimum. 500ml extra per high-protein meal.",
        "training_synergy": "Protein timing matters most post-workout (anabolic window). Pre-workout meal: carbs + moderate protein 2 hours before. Post-workout: 30–40 g whey + fast carbs within 2 hours. Bedtime: 30–40 g casein or cottage cheese (proven to increase overnight MPS).",
        "best_ways_to_use": [
            "Hit daily protein target first — other macros fill remaining calories",
            "Prioritise complete protein sources (contain all essential amino acids)",
            "Spread across 4–5 meals for sustained MPS",
            "Post-workout whey + banana = optimal recovery meal",
            "Meal prep weekly to ensure protein hits every day",
            "Track with MyFitnessPal for first 4 weeks to build awareness",
        ],
        "who_should_use": ["All resistance training athletes", "Fat loss seekers", "Muscle building athletes", "Vegans needing to plan more carefully"],
        "who_should_avoid": ["Kidney disease patients (reduce to 0.8 g/kg — consult doctor)", "Those with specific metabolic disorders (medical guidance)"],
        "benefits": ["Maximised muscle protein synthesis", "Muscle preservation during fat loss", "Improved satiety (most filling macronutrient)", "Thermogenic effect (25–30% of protein calories used in digestion)", "Faster recovery from training"],
        "side_effects": [{"effect": "GI discomfort with very high intakes (>3 g/kg) in untrained individuals", "severity": "low"}, {"effect": "Kidney stress only in pre-existing kidney disease — not healthy individuals", "severity": "low"}],
        "research_evidence": [
            {"study": "Morton et al. meta-analysis (49 RCTs)", "finding": "1.62 g/kg/day is the protein threshold for maximum muscle gain; above this shows diminishing returns", "source": "BJSM, 2018"},
            {"study": "Areta et al.", "finding": "20 g protein every 3 hours produces greater MPS than 10 g every 1.5 hours or 40 g every 6 hours", "source": "J Physiol, 2013"},
        ],
        "articles": [
            {"title": "How Much Protein Do You Need?", "author": "Examine Team", "source": "Examine.com", "url": "https://examine.com/topics/protein-intake/"},
            {"title": "The Optimal Protein Intake Guide", "author": "Greg Nuckols", "source": "Stronger by Science", "url": "https://www.strongerbyscience.com/how-much-protein/"},
        ],
        "magazines": [
            {"title": "The Definitive Guide to Protein", "publisher": "Muscle & Fitness", "url": "https://www.muscleandfitness.com/nutrition/protein/"},
            {"title": "Best High-Protein Meal Plans", "publisher": "Men's Health", "url": "https://www.menshealth.com/nutrition/high-protein-meal-plan/"},
        ],
        "books": [
            {"title": "The Protein Book", "author": "Lyle McDonald", "year": "2007"},
            {"title": "Power Eating", "author": "Susan Kleiner", "year": "2014"},
            {"title": "Nutrient Timing", "author": "John Ivy & Robert Portman", "year": "2004"},
        ],
        "videos": [
            {"title": "How Much Protein Do You ACTUALLY Need?", "channel": "Jeff Nippard", "platform": "YouTube", "url": "https://www.youtube.com/results?search_query=jeff+nippard+how+much+protein+do+you+need"},
            {"title": "The Ultimate Protein Guide", "channel": "Jeremy Ethier", "platform": "YouTube", "url": "https://www.youtube.com/results?search_query=jeremy+ethier+protein+guide"},
            {"title": "Protein Timing for Muscle Growth", "channel": "Renaissance Periodization", "platform": "YouTube", "url": "https://www.youtube.com/results?search_query=renaissance+periodization+protein+timing"},
        ],
        "ai_summary": "Protein is the most critical macronutrient for body composition. Aim for 1.6–2.2 g/kg/day distributed across 4–5 meals (30–40 g each). Post-workout whey and pre-sleep casein are the two most impactful protein timing strategies. The specific source matters less than hitting the daily target consistently.",
        "stacking": ["Creatine monohydrate (5g/day)", "Leucine (2.5g extra if plant-protein based)", "Digestive enzymes if GI discomfort"],
        "final_recommendation": "Set a daily protein target (bodyweight in kg × 2 = grams of protein). Build every meal around a protein source. Use whey post-workout and cottage cheese before bed. Track macros for 4 weeks to build lasting habits. Everything else is secondary.",
    },
    {
        "id": "fat_loss_diet",
        "triggers": ["fat loss diet","fat loss meal plan","cutting diet","diet to lose fat",
                     "diet for weight loss","weight loss diet","fat loss nutrition","lose fat diet",
                     "calorie deficit diet","diet for cutting","lean diet","fat loss eating",
                     "what to eat for fat loss","fat burning diet","weight loss meal plan",
                     "how to lose fat diet","nutrition for fat loss"],
        "name": "Fat Loss Diet & Nutrition Plan",
        "tagline": "Evidence-based nutritional strategy for maximising fat loss while preserving muscle.",
        "category": "nutrition", "evidence_tier": "very_high", "safe_for_beginners": True,
        "intent": "nutrition",
        "what_it_is": "Fat loss is achieved through a sustained calorie deficit — consuming fewer calories than you burn (TDEE). The size of the deficit determines the rate of fat loss. A moderate deficit (300–500 kcal/day) produces 0.3–0.5 kg fat loss per week while preserving muscle. Aggressive deficits (>750 kcal) accelerate fat loss but increase muscle loss risk significantly.",
        "how_it_works": "Body fat is stored energy (triglycerides in adipocytes). A calorie deficit forces the body to mobilise these stores via lipolysis (fat breakdown). High protein intake (2–2.4 g/kg) during a deficit sends the mTOR/MPS signal to preserve muscle tissue even in the absence of a calorie surplus. The type of calories matters less than the total, but protein has 3 advantages: satiety, thermogenesis (25–30% of calories burned in digestion), and muscle preservation.",
        "types": [
            {"name": "Standard Calorie Deficit (300–500 kcal)", "best_for": "Sustainable fat loss, muscle preservation", "evidence": "Very High"},
            {"name": "Intermittent Fasting (16:8)", "best_for": "Calorie control, insulin sensitivity", "evidence": "High"},
            {"name": "Ketogenic Diet", "best_for": "Some find lower hunger, metabolic benefits", "evidence": "High"},
            {"name": "Low-Carb / High-Protein", "best_for": "Appetite control, muscle preservation", "evidence": "Very High"},
        ],
        "dosage": "Calorie deficit: 300–500 kcal below TDEE for moderate fat loss. Protein: 2–2.4 g/kg (critical — highest during cutting). Carbs: 2–4 g/kg around training. Fats: 0.8 g/kg minimum. Fat loss rate: 0.5–1% bodyweight/week is optimal.",
        "timing": "No universal optimal meal timing for fat loss. Intermittent fasting works by restricting eating window, not metabolic magic. Pre-workout carbs improve performance. Post-workout protein critical. Avoid skipping protein meals.",
        "how_to_take": "Fat loss meal structure example (2,000 kcal): Breakfast — 4 eggs + spinach + 1 slice toast (400 kcal). Lunch — 200g chicken + large salad + olive oil (500 kcal). Snack — Greek yogurt + berries (200 kcal). Dinner — 150g salmon + vegetables + rice (500 kcal). Post-workout — whey shake (120 kcal). Total: 1,720 kcal with ~180g protein.",
        "hydration": "3 L/day. Water before meals reduces calorie intake by 22% (study: Davy et al. 2010). Black coffee and green tea are calorie-free thermogenics.",
        "training_synergy": "Resistance training preserves muscle during deficit. Protein above 2 g/kg is crucial. Cardio adds to deficit. Sleep deprivation increases hunger hormones (ghrelin up 24%, leptin down 18%) — 7–9 hours mandatory.",
        "best_ways_to_use": [
            "Calculate TDEE and subtract 300–500 kcal for daily target",
            "Protein 2–2.4 g/kg — non-negotiable to prevent muscle loss",
            "Prioritise volume eating — vegetables, lean protein, low-calorie density foods",
            "Track calories for at least 4 weeks — most people underestimate intake by 20–40%",
            "Meal prep to avoid impulsive high-calorie choices",
            "Allow one higher-calorie day per week (diet break) to reset leptin",
        ],
        "who_should_use": ["Anyone in a fat loss phase", "Those wanting body recomposition", "Athletes cutting for competition"],
        "who_should_avoid": ["Those with history of eating disorders (seek professional support)", "Pregnant/breastfeeding women"],
        "benefits": ["Sustainable fat loss at 0.5–1 kg/week", "Improved metabolic health markers", "Reduced cardiovascular risk", "Improved insulin sensitivity", "Maintained muscle mass with high protein"],
        "side_effects": [{"effect": "Hunger — manageable with high-volume, high-protein eating", "severity": "low"}, {"effect": "Fatigue if deficit too aggressive", "severity": "medium"}, {"effect": "Muscle loss if protein too low or deficit too large", "severity": "medium"}],
        "research_evidence": [
            {"study": "Hall KD meta-analysis", "finding": "Total calorie deficit is the primary driver of fat loss — macronutrient composition secondary", "source": "Cell Metabolism, 2012"},
            {"study": "Helms et al.", "finding": "Protein ≥2.3 g/kg preserves 93% of lean mass during aggressive calorie restriction in trained athletes", "source": "J Int Soc Sports Nutr, 2014"},
        ],
        "articles": [
            {"title": "How to Calculate Your TDEE and Set Up a Deficit", "author": "Examine Team", "source": "Examine.com", "url": "https://examine.com/topics/fat-loss/"},
            {"title": "The Complete Fat Loss Diet Guide", "author": "Lyle McDonald", "source": "BodyRecomposition.com", "url": "https://www.bodyrecomposition.com"},
        ],
        "magazines": [
            {"title": "The Ultimate Cutting Diet", "publisher": "Muscle & Fitness", "url": "https://www.muscleandfitness.com/nutrition/fat-loss-diet/"},
            {"title": "Fat Loss Meal Plans That Work", "publisher": "Men's Health", "url": "https://www.menshealth.com/nutrition/fat-loss-meal-plan/"},
        ],
        "books": [
            {"title": "The Rapid Fat Loss Handbook", "author": "Lyle McDonald", "year": "2005"},
            {"title": "Burn the Fat, Feed the Muscle", "author": "Tom Venuto", "year": "2013"},
            {"title": "The Obesity Code", "author": "Jason Fung", "year": "2016"},
        ],
        "videos": [
            {"title": "How to Set Up Your Fat Loss Diet", "channel": "Jeff Nippard", "platform": "YouTube", "url": "https://www.youtube.com/results?search_query=jeff+nippard+fat+loss+diet+setup"},
            {"title": "The Science of Fat Loss Nutrition", "channel": "Renaissance Periodization", "platform": "YouTube", "url": "https://www.youtube.com/results?search_query=renaissance+periodization+fat+loss+diet+science"},
        ],
        "ai_summary": "Fat loss is 70–80% diet and 20–30% exercise. A 300–500 kcal daily deficit with protein at 2–2.4 g/kg bodyweight is the most effective and sustainable strategy. Track calories honestly for 4 weeks — most people significantly underestimate intake. The best diet is one you can sustain for 12–16 weeks.",
        "stacking": ["Caffeine + green tea (thermogenic)", "Creatine (preserves strength during deficit)", "High-volume vegetables (calorie-free bulk)"],
        "final_recommendation": "Calculate your TDEE (use any online calculator), subtract 400 kcal, set protein at 2.2 g/kg bodyweight, fill remaining calories with carbs and fats. Track for 4 weeks. Adjust deficit/surplus based on actual results. Aim for 0.5–0.75 kg fat loss per week.",
    },
    {
        "id": "natural_testosterone",
        "triggers": ["natural testosterone","boost testosterone","increase testosterone",
                     "testosterone optimization","testosterone naturally","low testosterone",
                     "testosterone levels","raise testosterone","testosterone supplements",
                     "testosterone diet","testosterone training","testosterone lifestyle"],
        "name": "Natural Testosterone Optimisation",
        "tagline": "Evidence-based lifestyle and nutrition strategies to maximise natural testosterone production.",
        "category": "nutrition", "evidence_tier": "very_high", "safe_for_beginners": True,
        "intent": "research",
        "what_it_is": "Testosterone is the primary male anabolic hormone produced in the Leydig cells of the testes. In women, small amounts are produced in the ovaries and adrenal glands. Low testosterone is associated with reduced muscle mass, increased body fat, low libido, fatigue, and poor mood. Multiple lifestyle factors directly regulate testosterone production.",
        "how_it_works": "Testosterone production is regulated by the HPG axis (hypothalamic-pituitary-gonadal). LH (luteinising hormone) from the pituitary signals Leydig cells to produce testosterone. Key drivers: cholesterol (testosterone precursor), zinc (LH receptor function), vitamin D (hormonal regulation), sleep (80% of testosterone released during sleep), body composition (excess fat increases aromatase activity converting testosterone to estrogen).",
        "types": [
            {"name": "Sleep Optimisation", "best_for": "Greatest impact — 10–15% testosterone per hour of sleep lost", "evidence": "Very High"},
            {"name": "Resistance Training", "best_for": "Acute + chronic testosterone elevation", "evidence": "Very High"},
            {"name": "Vitamin D Supplementation", "best_for": "20% increase in deficient individuals", "evidence": "High"},
            {"name": "Zinc + Magnesium (ZMA)", "best_for": "Corrects deficiency-driven suppression", "evidence": "High"},
            {"name": "Fat Loss", "best_for": "Reduces aromatase activity", "evidence": "Very High"},
        ],
        "dosage": "Sleep: 7–9 hours (non-negotiable). Vitamin D: 3,000–5,000 IU/day if deficient. Zinc: 25–45 mg/day. Magnesium: 300–500 mg glycinate/day. Resistance training: 3–4x/week compound movements. Maintain bodyfat <20% men, <30% women.",
        "timing": "ZMA before bed (improves sleep quality + testosterone release). Vitamin D with largest meal. Resistance training increases testosterone acutely for 15–30 min post-exercise — cumulative benefits with regular training.",
        "how_to_take": "The hierarchy of natural testosterone optimisation: 1) Sleep 8 hours (most impactful), 2) Reduce body fat if overweight, 3) Resistance training 3–4x/week, 4) Correct vitamin D, zinc, magnesium deficiencies, 5) Manage chronic stress (cortisol is antagonistic to testosterone), 6) Dietary fat >30% of calories (precursor), 7) Avoid alcohol and excessive endurance exercise.",
        "hydration": "3 L/day. Dehydration elevates cortisol which suppresses testosterone.",
        "training_synergy": "Compound movements (squats, deadlifts, bench press) produce the greatest testosterone response. Short rest periods (60 sec) with moderate-heavy loads optimal. Endurance cardio >90 min may chronically suppress testosterone — keep cardio to moderate volume.",
        "best_ways_to_use": [
            "Prioritise 8-hour sleep above everything else",
            "Test serum testosterone, vitamin D, zinc, and LH before supplementing",
            "Reduce to <15% bodyfat (men) for optimal testosterone to estrogen ratio",
            "Compound heavy lifting 3–4x/week",
            "Dietary fat: egg yolks, red meat, olive oil, avocado (cholesterol precursor)",
            "Minimise alcohol — even moderate drinking suppresses testosterone by 6.8%",
        ],
        "who_should_use": ["Men with suboptimal testosterone", "Anyone over 30 wanting to maintain hormonal health", "Athletes wanting to maximise natural hormonal output"],
        "who_should_avoid": ["Those with diagnosed hypogonadism (TRT may be appropriate — see endocrinologist)"],
        "benefits": ["Increased muscle mass and strength", "Reduced body fat", "Improved libido", "Better mood and cognitive function", "Increased energy", "Improved bone density"],
        "side_effects": [{"effect": "No side effects from lifestyle optimisation", "severity": "low"}],
        "research_evidence": [
            {"study": "Pilz et al.", "finding": "Vitamin D supplementation increased testosterone by 25% in 1 year in deficient men", "source": "Horm Metab Res, 2011"},
            {"study": "Leproult & Van Cauter", "finding": "Sleeping 5 hours/night for 1 week reduced testosterone by 10–15% in young healthy men", "source": "JAMA, 2011"},
        ],
        "articles": [
            {"title": "Testosterone: What You Need to Know", "author": "Examine Team", "source": "Examine.com", "url": "https://examine.com/topics/testosterone/"},
            {"title": "How to Naturally Boost Testosterone", "author": "Healthline Editorial", "source": "Healthline", "url": "https://www.healthline.com/nutrition/boost-testosterone"},
        ],
        "magazines": [
            {"title": "The Complete Guide to Natural Testosterone", "publisher": "Men's Health", "url": "https://www.menshealth.com/health/testosterone-boost/"},
            {"title": "Lifestyle Testosterone Optimization", "publisher": "T-Nation", "url": "https://www.t-nation.com/all-articles/testosterone/"},
        ],
        "books": [
            {"title": "The Testosterone Advantage Plan", "author": "Lou Schuler", "year": "2002"},
            {"title": "Testosterone for Life", "author": "Abraham Morgentaler", "year": "2009"},
        ],
        "videos": [
            {"title": "How to Naturally Boost Testosterone", "channel": "Thomas DeLauer", "platform": "YouTube", "url": "https://www.youtube.com/results?search_query=thomas+delauer+natural+testosterone+boost"},
            {"title": "Testosterone: The Complete Science", "channel": "Jeff Nippard", "platform": "YouTube", "url": "https://www.youtube.com/results?search_query=jeff+nippard+testosterone+science"},
        ],
        "ai_summary": "Natural testosterone optimisation is dominated by sleep (80% of testosterone is released during sleep), body composition (fat drives aromatase), and resistance training. Vitamin D and zinc correction in deficient individuals can produce 20–25% increases. No supplement meaningfully raises testosterone beyond addressing deficiencies. Optimise lifestyle first.",
        "stacking": ["Vitamin D3 + K2 (5,000 IU/day)", "Zinc & Magnesium ZMA (before bed)", "Ashwagandha (reduces cortisol)"],
        "final_recommendation": "Test baseline testosterone (and vitamin D, zinc, LH, FSH) via a blood test. Optimise sleep to 8 hours, reduce bodyfat, add 3–4x/week resistance training, and correct deficiencies. Expect 20–40% improvement over 3–6 months with disciplined lifestyle optimisation.",
    },
    {
        "id": "supplement_guide",
        "triggers": ["best supplements","supplements for","supplement stack","which supplements",
                     "supplements to take","beginner supplements","essential supplements",
                     "supplements muscle gain","supplements fat loss","supplements strength",
                     "supplement guide","what supplements","supplement list","supplements for gym"],
        "name": "Essential Supplements Guide",
        "tagline": "Evidence-ranked supplement guide — what actually works, what doesn't, and why.",
        "category": "supplement", "evidence_tier": "very_high", "safe_for_beginners": True,
        "intent": "recommend",
        "what_it_is": "Supplements are products that add to (not replace) a sound diet and training programme. The vast majority of supplements have weak or no evidence. A small group have strong evidence and meaningful real-world effects. The hierarchy: food first, then evidence-based supplements to fill gaps or amplify training.",
        "how_it_works": "Effective supplements work through specific mechanisms: Creatine (phosphocreatine resynthesis for ATP), Caffeine (adenosine receptor antagonism), Protein powders (amino acid supply for MPS), Beta-alanine (carnosine for H+ buffering), Citrulline (nitric oxide for vasodilation). All others have weak evidence or work only in deficient individuals.",
        "types": [
            {"name": "Tier 1 — Very High Evidence", "best_for": "Creatine monohydrate, Protein powder, Caffeine", "evidence": "Very High"},
            {"name": "Tier 2 — High Evidence", "best_for": "Beta-alanine, Citrulline malate, Vitamin D, Omega-3, ZMA", "evidence": "High"},
            {"name": "Tier 3 — Moderate Evidence", "best_for": "Ashwagandha, HMB, L-carnitine, Glutamine", "evidence": "Moderate"},
            {"name": "Tier 4 — Low/No Evidence", "best_for": "Most proprietary blends, fat burners, 'natural testosterone boosters'", "evidence": "Low"},
        ],
        "dosage": "Tier 1 stack: Creatine monohydrate 5g/day. Whey protein 25–50g post-workout. Caffeine 3–5 mg/kg pre-workout. Tier 2: Beta-alanine 3.2–6.4g/day. Citrulline malate 8g pre-workout. Vitamin D3 3,000–5,000 IU. Omega-3 3–6g EPA+DHA. Zinc 25–45mg. Magnesium 300–500mg.",
        "timing": "Creatine: any time (daily consistency). Caffeine: 30–60 min pre-workout. Beta-alanine: pre-workout or split through day. Citrulline: 45–60 min pre-workout. Vitamin D: with food. ZMA: before bed.",
        "how_to_take": "Start with basics: protein if diet is inadequate, creatine for all goals, vitamin D year-round, omega-3 daily. Add caffeine for training intensity. Everything else is optional.",
        "hydration": "Increase water with stimulant supplements and creatine. 3 L/day minimum.",
        "training_synergy": "Supplements amplify — they don't replace — training and nutrition. No supplement overcomes a bad diet or poor sleep. The return on investment: nutrition > sleep > training > creatine > everything else.",
        "best_ways_to_use": [
            "Start with food: hit protein targets from whole foods first",
            "Creatine + Vitamin D + Omega-3 are the universal foundation",
            "Add caffeine for training intensity",
            "Pre-workout stack: Caffeine + Beta-alanine + Citrulline",
            "Post-workout: Whey protein + Creatine",
            "Bedtime: ZMA (zinc + magnesium)",
        ],
        "who_should_use": ["All gym-goers wanting evidence-based supplementation", "Beginners wanting a clear starting point"],
        "who_should_avoid": ["Those with medical conditions — check with doctor first", "Under 18 — focus on food and training"],
        "benefits": ["Creatine: +5–15% strength", "Caffeine: +3–7% power output", "Protein: convenient MPS trigger", "Vitamin D: testosterone + immunity", "Omega-3: anti-inflammatory recovery"],
        "side_effects": [{"effect": "Caffeine: tolerance, sleep disruption", "severity": "medium"}, {"effect": "Creatine: mild water retention", "severity": "low"}],
        "research_evidence": [
            {"study": "Kerksick et al. — ISSN Position Stand", "finding": "Creatine and protein are the only supplements with sufficient evidence to strongly recommend for muscle and performance", "source": "JISSN, 2018"},
        ],
        "articles": [
            {"title": "ISSN Exercise & Sport Nutrition Review", "author": "Kerksick et al.", "source": "J Int Soc Sports Nutr", "url": "https://jissn.biomedcentral.com/articles/10.1186/s12970-018-0242-y"},
            {"title": "Evidence-Based Supplement Ranking", "author": "Examine Team", "source": "Examine.com", "url": "https://examine.com/topics/supplements/"},
        ],
        "magazines": [
            {"title": "Supplement Rankings by Evidence", "publisher": "T-Nation", "url": "https://www.t-nation.com/supplements/"},
            {"title": "Best Supplements for Muscle Gain", "publisher": "Muscle & Fitness", "url": "https://www.muscleandfitness.com/supplements/"},
        ],
        "books": [
            {"title": "Supplements for Sport", "author": "Jose Antonio", "year": "2014"},
            {"title": "The Encyclopedia of Sports Nutrition", "author": "Robert Wildman", "year": "2012"},
        ],
        "videos": [
            {"title": "Which Supplements Actually Work?", "channel": "Jeff Nippard", "platform": "YouTube", "url": "https://www.youtube.com/results?search_query=jeff+nippard+supplements+that+actually+work"},
            {"title": "Evidence-Based Supplement Guide", "channel": "Renaissance Periodization", "platform": "YouTube", "url": "https://www.youtube.com/results?search_query=renaissance+periodization+supplement+guide+science"},
        ],
        "ai_summary": "Only a handful of supplements have strong research support. The Tier 1 stack (creatine + protein + caffeine) accounts for 90% of obtainable supplementation benefit. Vitamin D, omega-3, and ZMA fill dietary gaps. Everything else is largely marketing. Save money and focus on the fundamentals.",
        "stacking": ["Creatine 5g + Whey protein + Caffeine 200mg = Complete performance stack"],
        "final_recommendation": "Foundation: Creatine monohydrate (5g/day), Vitamin D3 (3,000–5,000 IU), Omega-3 (3–4g EPA+DHA). Training: Caffeine (200–300mg pre-workout), Citrulline malate (8g pre-workout), Beta-alanine (3.2g). Recovery: Whey protein (post-workout), ZMA (bedtime). Start here. Everything else is optional.",
    },
    {
        "id": "strength_training",
        "triggers": ["strength training","strength program","powerlifting","strength workout",
                     "how to get stronger","increase strength","build strength","strength exercises",
                     "1rm","maximal strength","powerlifting program","strength and muscle",
                     "strength training program","compound lifts","progressive overload"],
        "name": "Strength Training & Progressive Overload",
        "tagline": "Science-based strength training methodology for consistent, long-term strength gains.",
        "category": "exercise", "evidence_tier": "very_high", "safe_for_beginners": True,
        "intent": "exercise",
        "what_it_is": "Strength training is resistance exercise focused on maximising force production. Unlike hypertrophy (muscle size) training which operates at 8–20 reps, pure strength training uses heavy loads (85–100% 1RM) at 1–5 reps. The key adaptation is neuromuscular — more motor units recruited, improved rate coding, better inter/intra-muscular coordination — alongside structural muscle adaptations.",
        "how_it_works": "Heavy loads (>85% 1RM) recruit high-threshold motor units and type II muscle fibres. Repeated exposure to these loads improves CNS efficiency (stronger neural drive to muscles) and promotes myofibrillar hypertrophy (stronger, denser fibres rather than larger). Periodisation — systematically varying intensity and volume — prevents accommodation and drives continued progress.",
        "types": [
            {"name": "5×5 Linear Progression (SL5×5, Starting Strength)", "best_for": "Beginners, rapid strength development", "evidence": "Very High"},
            {"name": "5/3/1 (Wendler)", "best_for": "Intermediate+, sustainable long-term progress", "evidence": "Very High"},
            {"name": "Westside Conjugate", "best_for": "Advanced, powerlifters", "evidence": "High"},
            {"name": "Daily Undulating Periodization (DUP)", "best_for": "Intermediate+, concurrent strength + hypertrophy", "evidence": "High"},
        ],
        "dosage": "1–5 reps per set for pure strength. 3–5 sets per compound lift. 3–5 min rest between sets (critical for full CNS recovery). 3–4 training days/week. Train each lift 2–3x/week for optimal frequency.",
        "timing": "Heavy compound lifts first when CNS is fresh. Squat, bench, deadlift are foundations. Accessory work after main lifts. At least 48 hours between training the same movement pattern.",
        "how_to_take": "The Big Four for strength: Squat, Bench Press, Deadlift, Overhead Press. Accessory: Romanian deadlifts, barbell rows, weighted pull-ups, dips. Form is critical — get coaching on the big lifts. Film every set to check technique.",
        "hydration": "3 L/day. Dehydration reduces maximal strength by 2–3%.",
        "training_synergy": "Creatine monohydrate (5g/day) adds 5–15% to strength through phosphocreatine supplementation. High protein (1.8–2.2 g/kg) maintains muscle mass. Calorie surplus (250–500 kcal) accelerates progress. Sleep 8 hours — CNS recovery is paramount for strength.",
        "best_ways_to_use": [
            "3–5 reps with 85–95% 1RM for maximum strength adaptation",
            "Increase load when you hit top of prescribed rep range with good form",
            "5 min rest between heavy sets — non-negotiable for CNS recovery",
            "Technique first: get form right before adding weight",
            "Log every session — track squat, bench, deadlift, OHP weekly",
            "Deload every 4–6 weeks (reduce volume 50%) to prevent overtraining",
        ],
        "who_should_use": ["Anyone wanting to increase maximal strength", "Powerlifters", "Athletes in strength-dominant sports", "Those who've plateaued on higher-rep training"],
        "who_should_avoid": ["Beginners (start with 8–12 rep hypertrophy work to build a base)", "Those with joint issues (modify or seek physiotherapy)"],
        "benefits": ["Maximal strength improvement", "Neuromuscular efficiency gains", "Dense, strong muscle tissue", "Improved athletic performance", "Bone density improvement", "CNS adaptation and coordination"],
        "side_effects": [{"effect": "Higher injury risk with poor form or excessive loading — get coaching", "severity": "medium"}, {"effect": "CNS fatigue with excessive heavy volume", "severity": "medium"}],
        "research_evidence": [
            {"study": "Kraemer & Ratamess", "finding": "1–5 rep ranges at 85–100% 1RM produce greater strength gains than moderate rep ranges (8–12) with equal volume", "source": "Med Sci Sports Exerc, 2004"},
            {"study": "Rhea et al.", "finding": "Progressive linear periodization produces significantly greater strength gains than non-periodized training", "source": "J Strength Cond Res, 2002"},
        ],
        "articles": [
            {"title": "The Science of Strength Training", "author": "Greg Nuckols", "source": "Stronger by Science", "url": "https://www.strongerbyscience.com/science-of-strength/"},
            {"title": "Progressive Overload Explained", "author": "Examine Team", "source": "Examine.com", "url": "https://examine.com/topics/progressive-overload/"},
        ],
        "magazines": [
            {"title": "The Complete Strength Training Guide", "publisher": "T-Nation", "url": "https://www.t-nation.com/training/strength/"},
            {"title": "How to Get Stronger", "publisher": "Men's Health", "url": "https://www.menshealth.com/fitness/strength-training/"},
        ],
        "books": [
            {"title": "Starting Strength", "author": "Mark Rippetoe", "year": "2011"},
            {"title": "5/3/1 Forever", "author": "Jim Wendler", "year": "2017"},
            {"title": "Science and Practice of Strength Training", "author": "Vladimir Zatsiorsky", "year": "2006"},
        ],
        "videos": [
            {"title": "How to Get Stronger — The Science", "channel": "Jeff Nippard", "platform": "YouTube", "url": "https://www.youtube.com/results?search_query=jeff+nippard+how+to+get+stronger+science"},
            {"title": "5/3/1 Program Explained", "channel": "Alan Thrall", "platform": "YouTube", "url": "https://www.youtube.com/results?search_query=alan+thrall+531+wendler+program+explained"},
        ],
        "ai_summary": "Strength is primarily a neuromuscular adaptation to heavy mechanical loading. 1–5 rep ranges with 85–95% 1RM, compound movements, 3–5 min rest between sets, and progressive overload are the non-negotiables. Creatine adds 5–15% to strength. Consistent progressive overload over years produces elite-level strength.",
        "stacking": ["Creatine monohydrate 5g/day", "Caffeine pre-workout", "High-protein diet"],
        "final_recommendation": "Build a strength foundation with StrongLifts 5×5 or Starting Strength for 6 months. Progress to 5/3/1 for sustainable long-term development. The compound movements (squat, bench, deadlift, OHP) are the programme. Everything else is accessory.",
    },
]

# ── General topic trigger index for fast matching ─────────────────────────
def _find_general_topic(query: str) -> dict | None:
    """Match query to a general topic using trigger phrases."""
    q = query.lower()
    best_match: dict | None = None
    best_score = 0
    for topic in GENERAL_TOPICS:
        score = 0
        for trigger in topic["triggers"]:
            if trigger in q:
                # Longer trigger phrase = more specific match = higher score
                score += len(trigger.split())
        if score > best_score:
            best_score = score
            best_match = topic
    # Also check domain/intent keywords even if no exact trigger
    if best_match is None:
        domain = detect_domain(query)
        intent = classify_intent(query)
        mods   = _extract_goal_modifiers(query)
        # Map domain+intent to best general topic
        if "fat_loss" in domain or "fat_loss" in mods:
            if intent in ("exercise","research"):
                best_match = next((t for t in GENERAL_TOPICS if t["id"] == "fat_loss_exercise"), None)
            else:
                best_match = next((t for t in GENERAL_TOPICS if t["id"] == "fat_loss_diet"), None)
        elif "muscle_gain" in domain or "muscle_gain" in mods:
            if intent in ("exercise","research"):
                best_match = next((t for t in GENERAL_TOPICS if t["id"] == "muscle_gain_training"), None)
            else:
                best_match = next((t for t in GENERAL_TOPICS if t["id"] == "protein_diet"), None)
        elif domain == "exercise" or intent == "exercise":
            if "beginner" in mods:
                best_match = next((t for t in GENERAL_TOPICS if t["id"] == "beginner_workout"), None)
            else:
                best_match = next((t for t in GENERAL_TOPICS if t["id"] == "fat_loss_exercise"), None)
        elif domain == "nutrition" or intent == "nutrition":
            best_match = next((t for t in GENERAL_TOPICS if t["id"] == "protein_diet"), None)
        elif domain == "strength":
            best_match = next((t for t in GENERAL_TOPICS if t["id"] == "strength_training"), None)
        elif domain == "endurance":
            best_match = next((t for t in GENERAL_TOPICS if t["id"] == "hiit_cardio"), None)
        elif domain == "supplements":
            best_match = next((t for t in GENERAL_TOPICS if t["id"] == "supplement_guide"), None)
    return best_match



# ═══════════════════════════════════════════════════════════════════════════
# COMPOUND / SUPPLEMENT KNOWLEDGE BASE
# ═══════════════════════════════════════════════════════════════════════════

KB: list[dict] = [
    {"id":"crm_mono","name":"Creatine monohydrate",
     "aliases":["creatine","kreatin","creatina","créatine","क्रिएटिन","肌酸"],
     "category":"supplement","tags":["strength","muscle_gain","power","beginner","creatine"],
     "summary":"Most researched ergogenic aid. Increases phosphocreatine for faster ATP regeneration.",
     "what_it_is":"Creatine monohydrate is a naturally occurring compound produced in the liver and kidneys from amino acids arginine, glycine, and methionine. About 95% is stored in skeletal muscle as phosphocreatine, directly fuelling the ATP-PCr energy system during explosive efforts.",
     "how_it_works":"Creatine saturates muscle phosphocreatine stores, enabling faster ATP regeneration during high-intensity exercise. Delays fatigue, increases power output, and supports greater training volume leading to enhanced hypertrophy.",
     "types":[{"name":"Creatine Monohydrate","best_for":"Muscle gain and strength — gold standard","evidence":"Very High"},{"name":"Creatine HCL","best_for":"Sensitive stomachs, less bloating","evidence":"High"},{"name":"Buffered Creatine (Kre-Alkalyn)","best_for":"Reduced bloating","evidence":"Moderate"}],
     "dosage":"Loading (optional): 20g/day in 4×5g doses for 5–7 days. Maintenance: 3–5g/day. No-loading: 3–5g/day for ~4 weeks to saturate.",
     "timing":"Post-workout slightly superior; consistency matters most — any time of day works.",
     "how_to_take":"Mix in 200–300ml water, juice, or protein shake. Tasteless. Taking with carbohydrates improves uptake via insulin.",
     "hydration":"2.5–3.5 L/day. Creatine draws water into muscle cells.",
     "training_synergy":"Most effective with progressive-overload resistance training. Compound lifts and HIIT maximise ATP benefit.",
     "best_ways_to_use":["Take daily without missing","Combine with resistance training","Stay hydrated (3L/day)","Pair with protein and carbs post-workout","No need to cycle off"],
     "who_should_use":["Bodybuilders","Athletes","Beginners","Strength trainers","Power sport athletes"],
     "who_should_avoid":["Kidney disease patients","Those with dehydration conditions"],
     "cycling":"No cycling required. Long-term continuous use is safe.",
     "benefits":["Strength increase 5–15%","Power output improvement (PCr resynthesis)","Faster inter-set recovery","Lean mass support","Cognitive support (emerging)"],
     "side_effects":[{"effect":"Mild water retention (intracellular)","severity":"low"},{"effect":"GI discomfort if loading dose taken all at once","severity":"medium"}],
     "research_evidence":[{"study":"ISSN Position Stand 2017","finding":"Creatine is the most effective ergogenic supplement for high-intensity exercise and lean body mass","source":"JISSN 2017"},{"study":"Meta-analysis 22 RCTs","finding":"Creatine significantly increases maximal strength (8%) and weightlifting performance (14%)","source":"J Strength Cond Res 2003"}],
     "articles":[{"title":"Creatine Supplementation and Exercise Performance","author":"Jose Antonio & Conrad Ciccone","source":"J Int Soc Sports Nutr","url":"https://jissn.biomedcentral.com/articles/10.1186/1550-2783-1-2-38"},{"title":"Creatine: Research Summary","author":"Examine Team","source":"Examine.com","url":"https://examine.com/supplements/creatine/"}],
     "magazines":[{"title":"The Complete Creatine Guide","publisher":"Muscle & Fitness","url":"https://www.muscleandfitness.com/supplements/creatine/"},{"title":"Creatine: Everything You Need to Know","publisher":"Men's Health","url":"https://www.menshealth.com/fitness/creatine/"}],
     "books":[{"title":"The Encyclopedia of Sports Nutrition","author":"Robert Wildman & Barry Friedman","year":"2012"},{"title":"Sports Nutrition for Endurance Athletes","author":"Monique Ryan","year":"2012"}],
     "videos":[{"title":"Creatine: The Complete Guide","channel":"Jeff Nippard","platform":"YouTube","url":"https://www.youtube.com/results?search_query=jeff+nippard+creatine+complete+guide"},{"title":"Creatine Explained","channel":"Jeremy Ethier","platform":"YouTube","url":"https://www.youtube.com/results?search_query=jeremy+ethier+creatine+explained"},{"title":"Does Creatine Work?","channel":"Renaissance Periodization","platform":"YouTube","url":"https://www.youtube.com/results?search_query=renaissance+periodization+creatine"}],
     "ai_summary":"Creatine Monohydrate is the most evidence-backed supplement for muscle gain and strength. Take 3–5g daily consistently. No loading required. No need to cycle off.",
     "stacking":["Beta-alanine","Caffeine","Whey protein"],
     "final_recommendation":"Pair 3–5g creatine monohydrate with a post-workout carb + protein meal. Start progressive overload the same week. Expect strength gains in 2–4 weeks.",
     "evidence_tier":"very_high","safe_for_beginners":True,
     "pubmed_ids":["28615996","11509496","14636102"],"examine_url":"https://examine.com/supplements/creatine/",
     "products":[{"name":"Optimum Nutrition Micronised Creatine","price_inr":1499,"rating":4.7,"badge":"🏅 Premium","best_for":"All users"},{"name":"MuscleBlaze Creatine Monohydrate","price_inr":749,"rating":4.5,"badge":"🔥 Popular","best_for":"Best value India"},{"name":"AS-IT-IS Creatine Monohydrate","price_inr":599,"rating":4.4,"badge":"💪 Balanced","best_for":"Budget pick"}]},

    {"id":"crm_hcl","name":"Creatine HCL","aliases":["creatine hcl","creatine hydrochloride","hcl creatine"],
     "category":"supplement","tags":["strength","muscle_gain","creatine"],
     "summary":"Higher-solubility creatine. Effective at 1–2g/day. Less bloating.","what_it_is":"Creatine bonded to hydrochloric acid, dramatically increasing water solubility. Smaller effective doses mean less gastrointestinal load.","how_it_works":"Same phosphocreatine resynthesis mechanism as monohydrate. HCL form absorbed faster at lower doses.",
     "types":[{"name":"Creatine HCL","best_for":"Sensitive stomachs","evidence":"High"}],
     "dosage":"1–2g/day. No loading phase needed.","timing":"Pre or post-workout.","how_to_take":"Mix in 150–200ml water.","hydration":"2–3 L/day.","training_synergy":"Same as monohydrate — maximised by resistance training.",
     "best_ways_to_use":["Use if monohydrate causes GI distress","No loading required","Consistent daily use"],
     "who_should_use":["GI-sensitive individuals","Those who dislike bloating"],"who_should_avoid":["Budget-conscious users (monohydrate better value)"],
     "cycling":"No cycling needed.","benefits":["Equivalent strength gains at lower dose","Minimal bloating","Superior dissolution"],
     "side_effects":[{"effect":"Minimal GI issues","severity":"low"}],
     "research_evidence":[{"study":"Miller et al.","finding":"HCL form absorbed effectively at lower doses with less GI distress","source":"J Int Soc Sports Nutr 2009"}],
     "articles":[{"title":"Creatine HCL vs Monohydrate","author":"Examine Team","source":"Examine.com","url":"https://examine.com/supplements/creatine/"}],
     "magazines":[{"title":"Which Creatine Is Best?","publisher":"Bodybuilding.com","url":"https://www.bodybuilding.com/content/which-form-of-creatine-is-right-for-you.html"}],
     "books":[{"title":"Sports Supplementation","author":"Dr. Jose Antonio","year":"2019"}],
     "videos":[{"title":"Creatine HCL vs Monohydrate","channel":"PictureFit","platform":"YouTube","url":"https://www.youtube.com/results?search_query=creatine+hcl+vs+monohydrate"}],
     "ai_summary":"Choose Creatine HCL if monohydrate causes bloating or GI discomfort. Same muscle-building effects at a lower dose.",
     "stacking":["Citrulline malate","Beta-alanine"],"final_recommendation":"Choose HCL if monohydrate causes GI discomfort. Otherwise monohydrate is more cost-effective.",
     "evidence_tier":"high","safe_for_beginners":True,"pubmed_ids":["19844003"],"examine_url":"https://examine.com/supplements/creatine/"},

    {"id":"beta_al","name":"Beta-alanine","aliases":["beta alanine","beta-alanine","carnosine precursor"],
     "category":"supplement","tags":["endurance","strength","pre_workout"],
     "summary":"Amino acid precursor to carnosine. Buffers lactic acid, delays fatigue in 60–240s efforts.",
     "what_it_is":"Non-essential amino acid that pairs with histidine to form carnosine in muscle — a pH buffer against lactic acid.",
     "how_it_works":"Raises muscle carnosine 40–80% over 4–6 weeks, buffering H+ ions during intense exercise to delay fatigue.",
     "types":[{"name":"Beta-Alanine (Standard)","best_for":"Endurance and high-rep training","evidence":"High"},{"name":"SR Beta-Alanine","best_for":"Reduced tingling","evidence":"High"}],
     "dosage":"3.2–6.4g/day split into 1.6g doses.","timing":"Pre-workout or spread through day.","how_to_take":"Powder or capsule. SR formulas reduce tingling.","hydration":"2–3 L/day.",
     "training_synergy":"Best for high-rep resistance, HIIT, rowing, cycling. Synergises with creatine.",
     "best_ways_to_use":["Split dose to reduce tingling","4 weeks minimum before full effect","Stack with creatine for dual energy system coverage"],
     "who_should_use":["High-rep training athletes","Endurance athletes","CrossFitters"],"who_should_avoid":["Those highly sensitive to tingling sensation"],
     "cycling":"No cycling. Benefits plateau ~10 weeks; maintain at 3.2g/day.",
     "benefits":["Delayed muscle fatigue","Higher rep capacity","Endurance in 1–4 min efforts"],
     "side_effects":[{"effect":"Tingling / paresthesia (harmless)","severity":"low"}],
     "research_evidence":[{"study":"Hobson et al. 15-study meta-analysis","finding":"Beta-alanine significantly increases exercise capacity in efforts lasting 1–4 minutes","source":"Amino Acids 2012"}],
     "articles":[{"title":"Beta-Alanine: A Scientific Review","author":"Trexler ET et al.","source":"JISSN","url":"https://jissn.biomedcentral.com/articles/10.1186/s12970-015-0090-y"}],
     "magazines":[{"title":"Beta-Alanine Guide","publisher":"Bodybuilding.com","url":"https://www.bodybuilding.com/content/the-complete-guide-to-beta-alanine.html"}],
     "books":[{"title":"Sports Nutrition for Health Professionals","author":"Natalie Digate Muth","year":"2015"}],
     "videos":[{"title":"Beta-Alanine Explained","channel":"Jeff Nippard","platform":"YouTube","url":"https://www.youtube.com/results?search_query=beta+alanine+explained+jeff+nippard"}],
     "ai_summary":"Beta-alanine is a proven endurance supplement. 4–6 weeks to fully load. The tingling is harmless. Most beneficial for sustained high-intensity efforts lasting 1–4 minutes.",
     "stacking":["Creatine monohydrate","Caffeine","L-Citrulline"],"final_recommendation":"Stack with creatine for comprehensive energy system coverage. Use split dosing.",
     "evidence_tier":"high","safe_for_beginners":True,"pubmed_ids":["22649228","27797728"],"examine_url":"https://examine.com/supplements/beta-alanine/"},

    {"id":"citrulline","name":"L-Citrulline / Citrulline malate",
     "aliases":["citrulline","citrulline malate","l-citrulline","pump supplement","no booster"],
     "category":"supplement","tags":["pump","endurance","blood_flow","pre_workout"],
     "summary":"Converts to arginine → nitric oxide → vasodilation and muscle pump.",
     "what_it_is":"L-citrulline is converted to arginine in kidneys, then to nitric oxide. Citrulline malate adds malic acid for anti-fatigue synergy.",
     "how_it_works":"NO-mediated vasodilation increases blood flow, improving nutrient delivery and pump. Malate boosts Krebs cycle efficiency.",
     "types":[{"name":"L-Citrulline","best_for":"Pump and blood flow","evidence":"High"},{"name":"Citrulline Malate 2:1","best_for":"Pump + endurance","evidence":"High"}],
     "dosage":"L-citrulline: 6–8g. Citrulline malate 2:1: 8g. 30–60min pre-workout.","timing":"30–60min pre-workout.","how_to_take":"Mix 300–400ml water.","hydration":"3+ L/day.",
     "training_synergy":"Best for volume/hypertrophy days.",
     "best_ways_to_use":["Take 45–60min pre-workout","Use 8g citrulline malate for best results","Combine with caffeine and beta-alanine"],
     "who_should_use":["Bodybuilders seeking pump","Endurance athletes","High-volume trainers"],"who_should_avoid":["Those on blood pressure medication (consult doctor)"],
     "cycling":"No cycling needed.","benefits":["Significant muscle pump","Reduced DOMS","Endurance +12–15%","Blood pressure support"],
     "side_effects":[{"effect":"GI discomfort at doses >10g","severity":"low"}],
     "research_evidence":[{"study":"Pérez-Guisado & Jakeman","finding":"8g citrulline malate significantly reduced muscle soreness 48h post-training","source":"JSCR 2010"}],
     "articles":[{"title":"L-Citrulline: Research and Uses","author":"Examine Team","source":"Examine.com","url":"https://examine.com/supplements/citrulline/"}],
     "magazines":[{"title":"Get a Better Pump with Citrulline","publisher":"Flex Magazine","url":"https://www.flex.com"}],
     "books":[{"title":"Advanced Sports Nutrition","author":"Dan Bernadot","year":"2012"}],
     "videos":[{"title":"Citrulline Malate Explained","channel":"PictureFit","platform":"YouTube","url":"https://www.youtube.com/results?search_query=citrulline+malate+explained"}],
     "ai_summary":"Citrulline malate is a top pre-workout ingredient. Take 8g 45 minutes before training for maximised pump, reduced fatigue, and improved endurance.",
     "stacking":["Beta-alanine","Caffeine","Creatine"],"final_recommendation":"Use 8g citrulline malate 2:1 pre-workout with beta-alanine and caffeine.",
     "evidence_tier":"high","safe_for_beginners":True,"pubmed_ids":["21414438","26900386"],"examine_url":"https://examine.com/supplements/citrulline/"},

    {"id":"whey","name":"Whey protein",
     "aliases":["whey","whey protein","proteina whey","व्हे प्रोटीन","乳清蛋白"],
     "category":"supplement","tags":["muscle_gain","recovery","protein","beginner"],
     "summary":"Fast-digesting milk protein with highest leucine content — optimal for muscle protein synthesis.",
     "what_it_is":"Whey is a by-product of cheese production. Available as concentrate (70–80% protein), isolate (90%+), or hydrolysate. Richest source of leucine (10–11%).",
     "how_it_works":"High leucine content triggers mTOR activation, initiating muscle protein synthesis. Fast digestion delivers amino acids to muscle rapidly post-workout.",
     "types":[{"name":"Whey Concentrate","best_for":"General muscle building, budget","evidence":"Very High"},{"name":"Whey Isolate","best_for":"Lactose intolerant, cutting phase","evidence":"Very High"},{"name":"Whey Hydrolysate","best_for":"Fastest absorption","evidence":"High"}],
     "dosage":"25–50g per serving to reach 1.6–2.2g protein/kg bodyweight daily.","timing":"Post-workout optimal. Any time to supplement protein deficit.","how_to_take":"Shaker with 200–300ml water or milk. Isolate mixes cleaner.","hydration":"2.5–3 L/day.",
     "training_synergy":"Within 2h post-resistance training + fast carbs (banana) for insulin-driven uptake.",
     "best_ways_to_use":["Post-workout within 2 hours","With fast carbs for insulin spike","Daily to hit protein targets"],
     "who_should_use":["Bodybuilders","Athletes","Anyone struggling to hit protein targets","Beginners"],"who_should_avoid":["Lactose intolerant (use isolate)","Dairy allergic"],
     "cycling":"No cycling. Daily use to hit protein targets.",
     "benefits":["Maximises MPS via leucine","Fast post-workout absorption","Complete amino acid profile","Cost-effective"],
     "side_effects":[{"effect":"GI discomfort if lactose intolerant (use isolate)","severity":"medium"}],
     "research_evidence":[{"study":"Tang et al.","finding":"Whey protein stimulates greater muscle protein synthesis than soy or casein post-exercise","source":"Am J Clin Nutr 2009"}],
     "articles":[{"title":"Protein and Exercise","author":"Phillips SM","source":"J Nutr","url":"https://pubmed.ncbi.nlm.nih.gov/15051856/"},{"title":"Whey Protein Research","author":"Examine Team","source":"Examine.com","url":"https://examine.com/supplements/whey-protein/"}],
     "magazines":[{"title":"The Protein Bible","publisher":"Muscle & Fitness","url":"https://www.muscleandfitness.com/nutrition/whey-protein/"}],
     "books":[{"title":"Power Eating","author":"Susan Kleiner","year":"2014"},{"title":"The New Encyclopedia of Modern Bodybuilding","author":"Arnold Schwarzenegger","year":"1999"}],
     "videos":[{"title":"Best Protein for Muscle Growth","channel":"Jeff Nippard","platform":"YouTube","url":"https://www.youtube.com/results?search_query=jeff+nippard+best+protein+muscle+growth"}],
     "ai_summary":"Whey protein is the gold standard post-workout protein. Hit your daily protein target (1.6–2.2g/kg) and whey is the most convenient, fast-digesting tool to get there.",
     "stacking":["Creatine","Fast carbs post-workout","Casein before bed"],
     "final_recommendation":"Target total daily protein via food first; supplement shortfall with whey post-workout.",
     "evidence_tier":"very_high","safe_for_beginners":True,"pubmed_ids":["19589961","25048790"],"examine_url":"https://examine.com/supplements/whey-protein/",
     "products":[{"name":"ON Gold Standard Whey","price_inr":4499,"rating":4.8,"badge":"🏅 Premium","best_for":"Industry benchmark"},{"name":"MuscleBlaze Whey Protein","price_inr":2999,"rating":4.5,"badge":"🔥 Popular","best_for":"Best-seller India"},{"name":"AS-IT-IS Whey Concentrate","price_inr":1499,"rating":4.3,"badge":"💪 Balanced","best_for":"Budget"}]},

    {"id":"caffeine","name":"Caffeine","aliases":["caffeine","caffeina","caféine","कैफीन","caffeine anhydrous"],
     "category":"supplement","tags":["strength","endurance","fat_loss","focus","pre_workout"],
     "summary":"Adenosine receptor antagonist. Reduces perceived exertion, boosts power output and fat oxidation.",
     "what_it_is":"Most-studied ergogenic aid. Caffeine blocks adenosine receptors in brain and peripheral tissue.",
     "how_it_works":"Blocks adenosine (fatigue signal) receptors, increases catecholamine release, enhances calcium mobilisation in muscle. Result: reduced fatigue, improved power, fat oxidation.",
     "types":[{"name":"Caffeine Anhydrous","best_for":"Precise dosing, fast absorption","evidence":"Very High"},{"name":"Coffee","best_for":"Natural source with polyphenols","evidence":"Very High"}],
     "dosage":"3–6 mg/kg bodyweight (200–400mg for most adults).","timing":"30–60min pre-workout. Avoid within 6h of sleep.","how_to_take":"Anhydrous pills for precise dosing. Stack with L-Theanine 200mg (2:1).","hydration":"Add 500ml extra water on caffeine days.",
     "training_synergy":"Effective for resistance training, cardio, HIIT, team sports.",
     "best_ways_to_use":["200–300mg 30–45min pre-workout","Stack with L-Theanine for smooth focus","Cycle 5 days on, 2 days off to prevent tolerance"],
     "who_should_use":["Athletes needing performance boost","Those doing fasted cardio"],"who_should_avoid":["Anxiety disorder sufferers","Heart condition patients","Pregnant women"],
     "cycling":"Cycle off 1–2 weeks/month to reset adenosine receptor sensitivity.",
     "benefits":["Power output +3–7%","Endurance improvement","Fat oxidation","Focus and alertness","Reduced perceived effort"],
     "side_effects":[{"effect":"Tolerance with daily use","severity":"medium"},{"effect":"Sleep disruption if dosed too late","severity":"medium"},{"effect":"Anxiety at high doses","severity":"medium"}],
     "research_evidence":[{"study":"Grgic et al. systematic review","finding":"Caffeine significantly improves upper and lower body strength and endurance performance","source":"BJSM 2021"}],
     "articles":[{"title":"Caffeine and Exercise Performance","author":"Goldstein et al.","source":"JISSN","url":"https://jissn.biomedcentral.com/articles/10.1186/1550-2783-7-5"}],
     "magazines":[{"title":"The Science of Caffeine","publisher":"Men's Health","url":"https://www.menshealth.com/nutrition/caffeine/"}],
     "books":[{"title":"Caffeine for Sports Performance","author":"Louise Burke","year":"2013"}],
     "videos":[{"title":"Caffeine: How it Works","channel":"Thomas DeLauer","platform":"YouTube","url":"https://www.youtube.com/results?search_query=caffeine+sports+performance+science"},{"title":"Should You Use Caffeine?","channel":"Jeff Nippard","platform":"YouTube","url":"https://www.youtube.com/results?search_query=jeff+nippard+caffeine+supplement"}],
     "ai_summary":"Caffeine is the most proven ergogenic supplement. Take 3–5 mg/kg 30–60min before training. Stack with L-Theanine for focus without anxiety. Cycle regularly to prevent tolerance.",
     "stacking":["L-Theanine 200mg","L-Citrulline","Beta-alanine"],
     "final_recommendation":"3–5 mg/kg pre-workout with 200mg L-Theanine. Cycle 5 on / 2 off monthly.",
     "evidence_tier":"very_high","safe_for_beginners":True,"pubmed_ids":["34445894","20019636"],"examine_url":"https://examine.com/supplements/caffeine/"},

    {"id":"ostarine","name":"Ostarine (MK-2866)","aliases":["ostarine","mk2866","mk-2866","enobosarm"],
     "category":"sarm","tags":["muscle_gain","fat_loss","recomp","sarm"],
     "summary":"Mildest SARM. Lean mass gains with lower suppression than steroids. Research chemical.",
     "what_it_is":"Nonsteroidal SARM developed for muscle-wasting diseases. Selectively binds androgen receptors in muscle and bone.",
     "how_it_works":"Activates androgen receptors in muscle and bone selectively, producing anabolic effects without full androgenic side effects.",
     "types":[{"name":"Ostarine (MK-2866)","best_for":"Recomposition, first SARM","evidence":"Moderate"}],
     "dosage":"10–25mg/day. Start at 10mg first cycle.","timing":"Once daily.","how_to_take":"Oral liquid or capsule.","hydration":"2.5–3 L/day.",
     "training_synergy":"Recomposition nutrition (maintenance calories) works well.",
     "best_ways_to_use":["Start low at 10mg","Get bloodwork before starting","Run 8-week cycle maximum"],
     "who_should_use":["Experienced trainees considering SARMs"],"who_should_avoid":["Beginners","Under 21","Women (virilisation risk)"],
     "cycling":"8-week cycles. Bloodwork before and 4–6 weeks post-cycle.",
     "benefits":["2–4kg lean mass gain in 8 weeks","Fat loss support","Joint healing"],
     "side_effects":[{"effect":"Mild testosterone suppression","severity":"medium"},{"effect":"HDL reduction","severity":"medium"}],
     "research_evidence":[{"study":"Dalton et al.","finding":"Ostarine significantly increased lean body mass in cancer patients with muscle wasting","source":"Cancer Res 2011"}],
     "articles":[{"title":"Ostarine: Research Overview","author":"Examine Team","source":"Examine.com","url":"https://examine.com/supplements/ostarine/"}],
     "magazines":[{"title":"SARMs Guide","publisher":"More Plates More Dates","url":"https://www.moreplatesmoredates.com"}],
     "books":[{"title":"SARMs: A Practical Guide","author":"Various","year":"2020"}],
     "videos":[{"title":"Ostarine: The Complete Guide","channel":"Thomas DeLauer","platform":"YouTube","url":"https://www.youtube.com/results?search_query=ostarine+mk+2866+complete+guide"}],
     "ai_summary":"Ostarine is the mildest SARM with the most research. Bloodwork is non-negotiable before any SARM cycle. Not approved for human use.",
     "stacking":["Cardarine GW-501516","MK-677 Ibutamoren"],"final_recommendation":"Bloodwork baseline mandatory. Start 10mg, run 8 weeks, recheck bloodwork.",
     "evidence_tier":"moderate","safe_for_beginners":False,"pubmed_ids":["20814882","23631853"],"examine_url":"https://examine.com/supplements/ostarine/","legal_status":"Research chemical — not approved for human use. Banned by WADA."},

    {"id":"lgd4033","name":"LGD-4033 (Ligandrol)","aliases":["lgd4033","lgd-4033","ligandrol"],
     "category":"sarm","tags":["muscle_gain","strength","bulking","sarm"],
     "summary":"Most anabolic SARM. Significant suppression — full PCT required.",
     "what_it_is":"LGD-4033 is the most potent SARM. Phase I trial showed lean mass gains at 1mg/day.","how_it_works":"High-affinity androgen receptor agonist in muscle and bone producing anabolic effects.",
     "types":[{"name":"LGD-4033 (Ligandrol)","best_for":"Bulking, lean mass","evidence":"Moderate"}],
     "dosage":"5–10mg/day for 8–12 weeks.","timing":"Once daily.","how_to_take":"Oral liquid or capsule.","hydration":"3 L/day.",
     "training_synergy":"Progressive overload, high protein (2+g/kg), calorie surplus.",
     "best_ways_to_use":["Always run bloodwork","Full PCT protocol after cycle"],
     "who_should_use":["Experienced trainees with bloodwork access"],"who_should_avoid":["Beginners","Under 21","Women"],
     "cycling":"8–12 week cycles. Full PCT: Nolvadex 40/20/20/20.",
     "benefits":["3–5kg lean mass in 8–12 weeks","Major strength gains"],
     "side_effects":[{"effect":"Significant testosterone suppression","severity":"high"},{"effect":"HDL reduction","severity":"high"}],
     "research_evidence":[{"study":"Basaria et al.","finding":"LGD-4033 dose-dependently increased lean body mass in healthy men","source":"Lancet 2013"}],
     "articles":[{"title":"LGD-4033: Phase I Trial","author":"Basaria S et al.","source":"Lancet","url":"https://pubmed.ncbi.nlm.nih.gov/24518353/"}],
     "magazines":[{"title":"SARMs Overview","publisher":"Flex Magazine","url":"https://flex.com"}],
     "books":[{"title":"Beyond Steroids","author":"Wade Lightheart","year":"2019"}],
     "videos":[{"title":"LGD 4033 Complete Guide","channel":"Greg Doucette","platform":"YouTube","url":"https://www.youtube.com/results?search_query=lgd+4033+ligandrol+guide"}],
     "ai_summary":"LGD-4033 is the most anabolic SARM. Significant suppression makes full PCT non-negotiable. Only for experienced users with bloodwork access.",
     "stacking":["MK-677 Ibutamoren","Cardarine"],"final_recommendation":"Bloodwork mandatory. Not for beginners. Full SERM PCT required.",
     "evidence_tier":"moderate","safe_for_beginners":False,"pubmed_ids":["24518353"],"examine_url":"https://examine.com/supplements/lgd-4033/","legal_status":"Research chemical. Banned by WADA."},

    {"id":"rad140","name":"RAD-140 (Testolone)","aliases":["rad140","rad-140","testolone","rad 140"],
     "category":"sarm","tags":["muscle_gain","strength","fat_loss","sarm"],
     "summary":"Most potent SARM. Hepatotoxicity and strong suppression reported.",
     "what_it_is":"RAD-140 has the highest anabolic:androgenic ratio of any SARM. Hepatotoxicity case reports raise serious concerns.","how_it_works":"Very high-affinity androgen receptor agonist. More anabolic than testosterone at equivalent doses.",
     "types":[{"name":"RAD-140 (Testolone)","best_for":"Advanced users only","evidence":"Low"}],
     "dosage":"5–15mg/day for 8–10 weeks.","timing":"Once daily.","how_to_take":"Oral liquid or capsule.","hydration":"3+ L/day.",
     "training_synergy":"Progressive overload essential.",
     "best_ways_to_use":["Liver function tests mandatory","Short cycles (8 weeks max)"],
     "who_should_use":["Very experienced users"],"who_should_avoid":["Beginners","Under 25","Women"],
     "cycling":"8–10 week cycles. Full PCT mandatory.",
     "benefits":["Very high anabolic potency","Significant lean mass"],
     "side_effects":[{"effect":"Strong testosterone suppression","severity":"high"},{"effect":"Hepatotoxicity — liver damage in case reports","severity":"high"}],
     "research_evidence":[{"study":"Jayaraman et al.","finding":"RAD-140 demonstrated anabolic effects in animal models","source":"Endocrinology 2014"}],
     "articles":[{"title":"RAD-140: Research Overview","author":"Examine Team","source":"Examine.com","url":"https://examine.com/supplements/rad-140/"}],
     "magazines":[{"title":"Testolone Guide","publisher":"Evolutionary.org","url":"https://www.evolutionary.org"}],
     "books":[{"title":"SARMs: Research Guide","author":"Various","year":"2021"}],
     "videos":[{"title":"RAD 140 Complete Guide","channel":"Greg Doucette","platform":"YouTube","url":"https://www.youtube.com/results?search_query=rad+140+testolone+guide"}],
     "ai_summary":"RAD-140 is the most potent SARM but carries the highest risk including hepatotoxicity. Liver function tests mandatory. Not recommended for most users.",
     "final_recommendation":"Liver function tests mandatory. Not recommended due to hepatotoxicity risk.",
     "evidence_tier":"low","safe_for_beginners":False,"pubmed_ids":["20427478"],"legal_status":"Research chemical. Banned by WADA."},

    {"id":"mk677","name":"MK-677 (Ibutamoren)","aliases":["mk677","mk-677","ibutamoren","nutrobal"],
     "category":"sarm","tags":["muscle_gain","fat_loss","recovery","hgh","sleep"],
     "summary":"Oral GH secretagogue. Stimulates pituitary GH/IGF-1 release. Non-suppressive.",
     "what_it_is":"MK-677 is an oral ghrelin receptor agonist stimulating GH and IGF-1 release. Not a SARM — no androgen receptor binding, no testosterone suppression.","how_it_works":"Mimics ghrelin to stimulate GH secretion from the pituitary gland, elevating GH and IGF-1.",
     "types":[{"name":"MK-677 (Ibutamoren)","best_for":"GH elevation, recovery, sleep","evidence":"Moderate"}],
     "dosage":"10–25mg/day before bed.","timing":"Before bed to align with natural overnight GH pulse.","how_to_take":"Oral capsule or liquid.","hydration":"3 L/day.",
     "training_synergy":"Resistance training amplifies lean mass. Fasted morning cardio amplifies fat loss.",
     "best_ways_to_use":["Take before bed consistently","Monitor blood glucose if diabetic"],
     "who_should_use":["Those wanting GH benefits without injections","Recovery-focused athletes"],"who_should_avoid":["Diabetics (elevates blood glucose)"],
     "cycling":"12–24 week cycles. No PCT needed.",
     "benefits":["Elevated GH and IGF-1","Improved sleep depth","Lean mass gain","Recovery support"],
     "side_effects":[{"effect":"Increased appetite and water retention","severity":"medium"},{"effect":"Elevated fasting glucose","severity":"medium"}],
     "research_evidence":[{"study":"Murphy et al.","finding":"MK-677 significantly increased GH and IGF-1 levels in elderly subjects","source":"JCEM 1998"}],
     "articles":[{"title":"MK-677: Research Summary","author":"Examine Team","source":"Examine.com","url":"https://examine.com/supplements/mk-677/"}],
     "magazines":[{"title":"Ibutamoren Guide","publisher":"More Plates More Dates","url":"https://www.moreplatesmoredates.com"}],
     "books":[{"title":"Growth Hormone Optimization","author":"Various","year":"2020"}],
     "videos":[{"title":"MK-677: Everything You Need to Know","channel":"Thomas DeLauer","platform":"YouTube","url":"https://www.youtube.com/results?search_query=mk+677+ibutamoren+complete+guide"}],
     "ai_summary":"MK-677 is unique — oral, non-suppressive, and elevates GH naturally. Best taken before bed. Monitor blood glucose. Great for recovery, sleep, and lean mass.",
     "stacking":["Ostarine","LGD-4033"],"final_recommendation":"Stack with Ostarine or LGD for synergistic results. Monitor IGF-1 quarterly.",
     "evidence_tier":"moderate","safe_for_beginners":True,"pubmed_ids":["11149771"],"examine_url":"https://examine.com/supplements/mk-677/","legal_status":"Research chemical — not approved for human use."},

    {"id":"test_e","name":"Testosterone enanthate","aliases":["testosterone enanthate","test e","testo e","testosterone","testosteron"],
     "category":"steroid","tags":["muscle_gain","strength","bulking","testosterone","steroid"],
     "summary":"Gold standard anabolic injectable. Long-ester testosterone with predictable kinetics.",
     "what_it_is":"Synthetic testosterone with enanthate ester providing stable blood levels. The body's primary anabolic hormone delivered exogenously.","how_it_works":"Binds androgen receptors throughout body, activating protein synthesis, nitrogen retention, IGF-1 production.",
     "types":[{"name":"Testosterone Enanthate","best_for":"Beginner/intermediate cycles","evidence":"Very High"},{"name":"Testosterone Cypionate","best_for":"US standard, weekly injection","evidence":"Very High"},{"name":"Testosterone Propionate","best_for":"Fast-acting, more frequent injection","evidence":"Very High"}],
     "dosage":"Beginner: 300–500mg/week (split E3.5D). Intermediate: 500–750mg/week.","timing":"IM or SubQ injection every 3.5 days.","how_to_take":"IM (glute/quads/delts) or SubQ. Rotate sites.","hydration":"2.5–3 L/day. Monitor blood pressure.",
     "training_synergy":"Progressive overload, high protein (2–2.4g/kg), calorie surplus.",
     "best_ways_to_use":["Run bloodwork before, mid-cycle, and post-PCT","Use AI (anastrozole) to manage estrogen","Start with testosterone-only first cycle"],
     "who_should_use":["Adult men over 21 with prior natural training"],"who_should_avoid":["Under 21","Women","Heart disease patients","Anyone not willing to run bloodwork"],
     "cycling":"12–16 week cycles. AI required. PCT: Nolvadex 40/40/20/20mg starting 2 weeks post-last injection.",
     "benefits":["Significant lean mass and strength gains","Improved recovery","Libido and well-being"],
     "side_effects":[{"effect":"Complete testosterone suppression","severity":"high"},{"effect":"Aromatisation — AI required","severity":"medium"},{"effect":"Cardiovascular strain","severity":"high"}],
     "research_evidence":[{"study":"Bhasin et al.","finding":"Testosterone dose-dependently increases fat-free mass and muscle size","source":"NEJM 1996"}],
     "articles":[{"title":"Testosterone and Muscle","author":"Bhasin S et al.","source":"NEJM","url":"https://pubmed.ncbi.nlm.nih.gov/8637536/"}],
     "magazines":[{"title":"TRT Guide","publisher":"Men's Health","url":"https://www.menshealth.com/health/testosterone/"}],
     "books":[{"title":"The New Testosterone Treatment","author":"Abraham Morgentaler","year":"2014"}],
     "videos":[{"title":"Testosterone Cycle Guide","channel":"Greg Doucette","platform":"YouTube","url":"https://www.youtube.com/results?search_query=testosterone+enanthate+cycle+beginners+guide"}],
     "ai_summary":"Testosterone enanthate is the gold standard for anabolic cycles. Bloodwork is non-negotiable. AI management, PCT, and cardiovascular monitoring are mandatory.",
     "stacking":["Anastrozole (AI)","NPP/Deca (intermediate+)","Anavar (cut)"],"final_recommendation":"Bloodwork before, mid-cycle, post-PCT. AI + cardiovascular monitoring non-negotiable.",
     "evidence_tier":"very_high","safe_for_beginners":False,"pubmed_ids":["8637536","11502560"],"legal_status":"Schedule III (USA). Prescription only."},

    {"id":"anavar","name":"Anavar (Oxandrolone)","aliases":["anavar","oxandrolone","var"],
     "category":"steroid","tags":["fat_loss","strength","cutting","steroid"],
     "summary":"Mild oral anabolic steroid. Popular for cutting. Preserves muscle in calorie deficit.",
     "what_it_is":"Oxandrolone — 17α-alkylated oral anabolic with low androgenic activity. Popular for cutting and women at low doses.","how_it_works":"Binds androgen receptors to stimulate protein synthesis. Low aromatisation = minimal water retention.",
     "types":[{"name":"Anavar (Oxandrolone)","best_for":"Cutting, lean mass preservation","evidence":"High"}],
     "dosage":"Men: 20–80mg/day split. Women: 5–20mg/day.","timing":"Split twice daily.","how_to_take":"Oral tablet.","hydration":"2.5–3 L/day.",
     "training_synergy":"Calorie deficit + high protein (2.2–2.4g/kg).",
     "best_ways_to_use":["Run liver support","Keep cycles short (6–8 weeks)"],
     "who_should_use":["Cutting phase athletes","Women (low doses)"],"who_should_avoid":["Beginners","Those with liver issues"],
     "cycling":"6–8 weeks. PCT required.",
     "benefits":["Muscle preservation on cut","Strength gains without mass","Minimal water retention"],
     "side_effects":[{"effect":"Liver stress (oral 17-AA)","severity":"medium"},{"effect":"HDL reduction","severity":"high"}],
     "research_evidence":[{"study":"Multiple clinical trials","finding":"Oxandrolone significantly preserves lean mass during caloric restriction","source":"Multiple sources"}],
     "articles":[{"title":"Anavar Profile","author":"William Llewellyn","source":"Anabolics","url":"https://pubmed.ncbi.nlm.nih.gov/7998639/"}],
     "magazines":[{"title":"Anavar for Cutting","publisher":"Muscle & Performance","url":"https://www.muscleandperformance.com"}],
     "books":[{"title":"Anabolics","author":"William Llewellyn","year":"2017"}],
     "videos":[{"title":"Anavar Cycle Guide","channel":"Greg Doucette","platform":"YouTube","url":"https://www.youtube.com/results?search_query=anavar+cycle+guide+oxandrolone"}],
     "ai_summary":"Anavar is one of the milder steroids but still requires careful monitoring. Ideal for cutting phases. PCT mandatory.",
     "final_recommendation":"Liver function and lipid tests mandatory. Not for beginners. SERM PCT required.",
     "evidence_tier":"high","safe_for_beginners":False,"legal_status":"Schedule III (USA). Prescription only."},

    {"id":"nandrolone","name":"Nandrolone / NPP / Deca-Durabolin","aliases":["nandrolone","deca","deca durabolin","npp"],
     "category":"steroid","tags":["muscle_gain","strength","bulking","joint_health","steroid"],
     "summary":"19-nor anabolic steroid. Lean mass gains and joint lubrication. Requires prolactin management.",
     "what_it_is":"19-nortestosterone derivative available as NPP or Deca-Durabolin.","how_it_works":"Highly anabolic with notable collagen synthesis benefits. Significant prolactin elevation requires cabergoline.",
     "types":[{"name":"Nandrolone Decanoate (Deca)","best_for":"Long cycles, joint support","evidence":"High"},{"name":"NPP","best_for":"Shorter cycles, faster clearance","evidence":"High"}],
     "dosage":"NPP: 300–400mg/week. Deca: 200–400mg/week.","timing":"IM injection on schedule.","how_to_take":"IM injection. Always run with testosterone base.","hydration":"3 L/day.",
     "training_synergy":"Progressive overload + high protein. Joint benefits allow higher training volume.",
     "best_ways_to_use":["Always run with testosterone","Use cabergoline for prolactin"],
     "who_should_use":["Intermediate+ users","Those with joint issues"],"who_should_avoid":["Beginners","Women"],
     "cycling":"12–16 weeks with testosterone base. Full PCT required.",
     "benefits":["Lean mass gains","Joint lubrication","Collagen synthesis"],
     "side_effects":[{"effect":"Prolactin elevation — cabergoline required","severity":"high"},{"effect":"Full testosterone suppression","severity":"high"}],
     "research_evidence":[{"study":"Bhasin et al.","finding":"Nandrolone increases lean mass and reduces fat mass","source":"NEJM 1996"}],
     "articles":[{"title":"Nandrolone Profile","author":"William Llewellyn","source":"Anabolics","url":"https://pubmed.ncbi.nlm.nih.gov/8637536/"}],
     "magazines":[{"title":"Deca Durabolin Guide","publisher":"Muscle & Fitness","url":"https://www.muscleandfitness.com"}],
     "books":[{"title":"Anabolics","author":"William Llewellyn","year":"2017"}],
     "videos":[{"title":"Nandrolone/Deca Guide","channel":"Greg Doucette","platform":"YouTube","url":"https://www.youtube.com/results?search_query=nandrolone+deca+durabolin+cycle"}],
     "ai_summary":"Nandrolone is highly effective but complex. Cabergoline for prolactin and testosterone base are non-negotiable.",
     "final_recommendation":"Must run with testosterone base. Cabergoline mandatory. Bloodwork throughout.",
     "evidence_tier":"high","safe_for_beginners":False,"legal_status":"Controlled substance. Prescription only."},

    {"id":"bpc157","name":"BPC-157","aliases":["bpc157","bpc-157","body protection compound","bpc 157"],
     "category":"peptide","tags":["recovery","injury","joint_health","gut","healing","peptide"],
     "summary":"15-amino acid peptide from gastric juice. Accelerates tendon, ligament, muscle, and gut healing.",
     "what_it_is":"BPC-157 is a synthetic peptide from human gastric juice protein. Animal research shows accelerated healing.","how_it_works":"Promotes angiogenesis, upregulates GH receptors in tendons, reduces inflammation, accelerates tissue repair.",
     "types":[{"name":"BPC-157 (Injectable)","best_for":"Systemic and local healing","evidence":"Moderate"},{"name":"BPC-157 (Oral)","best_for":"Gut healing","evidence":"Moderate"}],
     "dosage":"250–500mcg/day subcutaneous or intramuscular.","timing":"Near injury site or systemic. Once or twice daily.","how_to_take":"Reconstitute with bacteriostatic water. Insulin syringe 29–31G.","hydration":"2.5–3 L/day.",
     "training_synergy":"Active rehabilitation during protocol maximises healing.",
     "best_ways_to_use":["Inject near injury site for localised healing","500mcg twice daily for acute injuries","Combine with TB-500 for systemic healing"],
     "who_should_use":["Athletes with injuries","Those with gut issues"],"who_should_avoid":["Active cancer patients","Pregnant women"],
     "cycling":"Acute injury: 4–6 weeks. Chronic: 8–12 weeks.",
     "benefits":["Accelerated tendon/ligament healing","Gut lining repair","Anti-inflammatory"],
     "side_effects":[{"effect":"Injection site irritation (mild, transient)","severity":"low"}],
     "research_evidence":[{"study":"Sikiric et al.","finding":"BPC-157 accelerates healing of various tissue types in animal models","source":"Curr Pharm Des 2013"}],
     "articles":[{"title":"BPC-157: Research Review","author":"Examine Team","source":"Examine.com","url":"https://examine.com/supplements/bpc-157/"}],
     "magazines":[{"title":"Healing Peptides Guide","publisher":"More Plates More Dates","url":"https://www.moreplatesmoredates.com"}],
     "books":[{"title":"Peptide Protocols","author":"Jay Campbell","year":"2019"}],
     "videos":[{"title":"BPC-157: The Healing Peptide","channel":"Derek at MPMD","platform":"YouTube","url":"https://www.youtube.com/results?search_query=bpc+157+healing+peptide+guide"}],
     "ai_summary":"BPC-157 is one of the most promising healing peptides. Source quality and sterility are critical.",
     "stacking":["TB-500","Ipamorelin/CJC-1295"],"final_recommendation":"Source quality critical. Sterility non-negotiable.",
     "evidence_tier":"moderate","safe_for_beginners":True,"pubmed_ids":["23439702","21447935"],"examine_url":"https://examine.com/supplements/bpc-157/","legal_status":"Research chemical — not approved for human use."},

    {"id":"hgh","name":"Human Growth Hormone (HGH)","aliases":["hgh","human growth hormone","growth hormone","gh","somatropin"],
     "category":"peptide","tags":["fat_loss","muscle_gain","recovery","anti_aging","hgh"],
     "summary":"Recombinant somatropin. Potent lipolytic and anabolic agent. Prescription only globally.",
     "what_it_is":"Recombinant HGH (somatropin) stimulates IGF-1 (anabolic) and drives lipolysis directly.","how_it_works":"Binds GH receptors throughout body, stimulating IGF-1 (muscle growth) and directly promoting lipolysis (fat breakdown).",
     "types":[{"name":"Pharmaceutical Grade HGH","best_for":"Maximum purity and safety","evidence":"Very High"},{"name":"GH Peptides (Ipamorelin etc.)","best_for":"Stimulating natural GH","evidence":"Moderate"}],
     "dosage":"Anti-aging/fat loss: 1–3 IU/day. Bodybuilding: 4–8 IU/day (significantly higher risk).","timing":"SubQ injection on waking (fat loss) or before bed (GH pulse).","how_to_take":"SubQ abdomen, rotating sites. Reconstitute with bacteriostatic water. Store 2–8°C.","hydration":"3+ L/day.",
     "training_synergy":"Resistance training + fasted morning cardio maximise body composition.",
     "best_ways_to_use":["Start at 1–2 IU and titrate up slowly","Monitor IGF-1 quarterly","Use pharma-grade only","Physician supervision mandatory"],
     "who_should_use":["Adults over 30 with confirmed GH deficiency under medical supervision"],"who_should_avoid":["Active cancer","Diabetics without close monitoring","Anyone without physician supervision"],
     "cycling":"Anti-aging: 6–12 months. Bodybuilding: 16–24 weeks.",
     "benefits":["Significant visceral fat reduction","Lean mass retention","Connective tissue strengthening","Improved sleep quality"],
     "side_effects":[{"effect":"Carpal tunnel","severity":"medium"},{"effect":"Insulin resistance","severity":"high"},{"effect":"Acromegaly at high sustained doses","severity":"high"}],
     "research_evidence":[{"study":"Rudman et al.","finding":"HGH supplementation in elderly men significantly increased lean mass and reduced fat mass","source":"NEJM 1990"}],
     "articles":[{"title":"HGH in Adults","author":"Vance ML","source":"NEJM","url":"https://pubmed.ncbi.nlm.nih.gov/2388534/"}],
     "magazines":[{"title":"HGH: Truth vs Hype","publisher":"Men's Health","url":"https://www.menshealth.com/hgh/"}],
     "books":[{"title":"Grow Young with HGH","author":"Ronald Klatz","year":"1997"}],
     "videos":[{"title":"HGH: Everything You Need to Know","channel":"Derek at MPMD","platform":"YouTube","url":"https://www.youtube.com/results?search_query=hgh+growth+hormone+complete+guide"}],
     "ai_summary":"HGH is highly effective but expensive, prescription-only, and requires physician supervision. Pharmaceutical-grade only. Start at 1–2 IU and titrate based on IGF-1 bloodwork.",
     "stacking":["Testosterone (synergistic)","T3 (advanced)"],"final_recommendation":"Physician supervision mandatory. IGF-1, fasting glucose, HbA1c quarterly. Pharmaceutical-grade only.",
     "evidence_tier":"very_high","safe_for_beginners":False,"pubmed_ids":["2388534"],"legal_status":"Prescription only worldwide. Banned by WADA."},

    {"id":"vitamin_d","name":"Vitamin D3 + K2","aliases":["vitamin d","vitamin d3","cholecalciferol","vit d"],
     "category":"supplement","tags":["health","testosterone","immune","bone","recovery"],
     "summary":"Essential fat-soluble vitamin-hormone. Deficiency widespread. Regulates testosterone, immunity, bone density.",
     "what_it_is":"D3 (cholecalciferol) is a fat-soluble prohormone synthesised in skin on UV exposure. K2 (MK-7) directs calcium to bone.","how_it_works":"Acts as a steroid hormone binding VDR receptors throughout the body, regulating calcium, immune function, and testosterone production.",
     "types":[{"name":"Vitamin D3 + K2 MK-7","best_for":"Optimal absorption and calcium direction","evidence":"Very High"}],
     "dosage":"D3: 2,000–5,000 IU/day. K2 MK-7: 100–200mcg/day.","timing":"With largest fat-containing meal.","how_to_take":"Softgel capsule. D3 + K2 in same meal.","hydration":"Standard 2.5–3 L/day.",
     "training_synergy":"Adequate D3 supports testosterone production and muscle function.",
     "best_ways_to_use":["Test serum 25-OH-D first","Target 40–70 ng/mL","Take with fat-containing meal","Always pair with K2"],
     "who_should_use":["Everyone (widespread deficiency)","Athletes"],"who_should_avoid":["Hypercalcemia patients without doctor guidance"],
     "cycling":"Year-round.","benefits":["Testosterone support","Immune regulation","Bone density","Mood improvement"],
     "side_effects":[{"effect":"Toxicity only at >10,000 IU/day without monitoring","severity":"low"}],
     "research_evidence":[{"study":"Pilz et al.","finding":"Vitamin D supplementation increased testosterone by 25% in 1 year in deficient men","source":"Horm Metab Res 2011"}],
     "articles":[{"title":"Vitamin D Deficiency","author":"Holick MF","source":"NEJM","url":"https://pubmed.ncbi.nlm.nih.gov/17556697/"}],
     "magazines":[{"title":"Why Everyone Needs Vitamin D","publisher":"Men's Health","url":"https://www.menshealth.com/vitamin-d/"}],
     "books":[{"title":"The Vitamin D Solution","author":"Michael Holick","year":"2011"}],
     "videos":[{"title":"Vitamin D: Complete Guide","channel":"Thomas DeLauer","platform":"YouTube","url":"https://www.youtube.com/results?search_query=vitamin+d+supplement+complete+guide"}],
     "ai_summary":"Vitamin D3 deficiency is epidemic. Test your levels and supplement accordingly. Always pair D3 with K2. Most people need 3,000–5,000 IU/day.",
     "stacking":["Magnesium","Omega-3"],"final_recommendation":"Test serum 25-OH-D. Target 40–70 ng/mL. Daily with K2.",
     "evidence_tier":"very_high","safe_for_beginners":True,"pubmed_ids":["21154195"],"examine_url":"https://examine.com/supplements/vitamin-d/"},

    {"id":"omega3","name":"Omega-3 fish oil (EPA + DHA)","aliases":["omega 3","fish oil","omega-3","epa dha"],
     "category":"supplement","tags":["health","recovery","anti_inflammatory","cardiovascular"],
     "summary":"EPA + DHA reduce systemic inflammation, improve cardiovascular markers, support joints and brain.",
     "what_it_is":"Long-chain omega-3 polyunsaturated fatty acids from marine sources.","how_it_works":"EPA and DHA reduce pro-inflammatory eicosanoid production, improve HDL/triglycerides, and support muscle protein synthesis.",
     "types":[{"name":"Fish Oil (EPA + DHA)","best_for":"General anti-inflammatory, cardiovascular","evidence":"Very High"},{"name":"Algae Oil","best_for":"Vegan DHA source","evidence":"High"}],
     "dosage":"3–6g combined EPA + DHA per day (not total oil volume).","timing":"With meals.","how_to_take":"Softgel or liquid. Enteric-coated if sensitive.","hydration":"Standard 2.5–3 L/day.",
     "training_synergy":"Anti-inflammatory effects reduce DOMS and support recovery.",
     "best_ways_to_use":["Check EPA + DHA content not just total oil","Take with fatty meals"],
     "who_should_use":["Everyone","Especially steroid users (cardiovascular protection)"],"who_should_avoid":["Fish allergy (use algae oil)"],
     "cycling":"Daily, year-round.","benefits":["Systemic anti-inflammatory","Cardiovascular protection","Joint health","MPS support"],
     "side_effects":[{"effect":"Fish aftertaste (take with meals)","severity":"low"}],
     "research_evidence":[{"study":"Smith et al.","finding":"Omega-3 supplementation enhanced muscle protein synthesis response to amino acids","source":"JCEM 2011"}],
     "articles":[{"title":"Omega-3 Fatty Acids and Exercise","author":"Smith GI et al.","source":"JCEM","url":"https://pubmed.ncbi.nlm.nih.gov/22334723/"}],
     "magazines":[{"title":"Why Every Athlete Should Take Fish Oil","publisher":"Men's Health","url":"https://www.menshealth.com/fish-oil/"}],
     "books":[{"title":"The Omega Rx Zone","author":"Barry Sears","year":"2002"}],
     "videos":[{"title":"Fish Oil: Complete Guide","channel":"Thomas DeLauer","platform":"YouTube","url":"https://www.youtube.com/results?search_query=fish+oil+omega+3+complete+guide"}],
     "ai_summary":"Omega-3 is one of the most important foundational supplements. Check EPA + DHA content on label. Essential for cardiovascular health, inflammation control, and recovery.",
     "stacking":["Vitamin D3/K2","Curcumin"],"final_recommendation":"Prioritise EPA + DHA mg on label.",
     "evidence_tier":"very_high","safe_for_beginners":True,"pubmed_ids":["19589961"],"examine_url":"https://examine.com/supplements/fish-oil/"},

    {"id":"zinc_magnesium","name":"Zinc & Magnesium (ZMA)","aliases":["zma","zinc magnesium","zinc","magnesium"],
     "category":"supplement","tags":["testosterone","sleep","recovery","health"],
     "summary":"Zinc supports testosterone synthesis; magnesium improves sleep, reduces cortisol.",
     "what_it_is":"ZMA combines zinc (testosterone, immunity) and magnesium (sleep, cortisol regulation).","how_it_works":"Zinc is a cofactor for testosterone biosynthesis. Magnesium enhances GABA signalling for sleep and reduces cortisol.",
     "types":[{"name":"ZMA (Zinc + Magnesium + B6)","best_for":"Testosterone support and sleep","evidence":"High"}],
     "dosage":"Zinc: 25–45mg/day. Magnesium: 300–500mg glycinate or malate.","timing":"Before bed on empty stomach.","how_to_take":"Capsule. Avoid zinc with food.","hydration":"Standard 2.5–3 L/day.",
     "training_synergy":"Support testosterone and sleep — critical for training adaptation.",
     "best_ways_to_use":["Take before bed","Magnesium glycinate for best absorption"],
     "who_should_use":["Athletes (sweat depletes both)","Those with sleep issues"],"who_should_avoid":["Those on certain antibiotics"],
     "cycling":"Daily, year-round.","benefits":["Testosterone support when deficient","Sleep quality improvement","Cortisol reduction"],
     "side_effects":[{"effect":"Nausea if zinc taken with food","severity":"low"}],
     "research_evidence":[{"study":"Prasad et al.","finding":"Zinc deficiency is associated with reduced testosterone levels","source":"Nutrition 1996"}],
     "articles":[{"title":"ZMA and Athletic Performance","author":"Brilla & Conte","source":"J Exerc Physiol","url":"https://pubmed.ncbi.nlm.nih.gov/10738264/"}],
     "magazines":[{"title":"The Benefits of ZMA","publisher":"Bodybuilding.com","url":"https://www.bodybuilding.com/content/the-benefits-of-zma.html"}],
     "books":[{"title":"Sports Nutrition Essentials","author":"Robert Murray","year":"2015"}],
     "videos":[{"title":"ZMA: Does It Work?","channel":"PictureFit","platform":"YouTube","url":"https://www.youtube.com/results?search_query=zma+zinc+magnesium+supplement+review"}],
     "ai_summary":"Zinc and magnesium are foundational supplements most athletes are deficient in. Magnesium glycinate for best absorption. Take before bed.",
     "final_recommendation":"Use magnesium glycinate. Test serum zinc and magnesium if deficiency suspected.",
     "evidence_tier":"high","safe_for_beginners":True,"pubmed_ids":["10738264"],"examine_url":"https://examine.com/supplements/zma/"},

    {"id":"fat_burner_stack","name":"Fat burner supplements","aliases":["fat burner","fat burning supplement","thermogenic"],
     "category":"supplement","tags":["fat_loss","cutting","thermogenic","metabolism"],
     "summary":"Evidence-based fat loss supplements: Caffeine, L-Carnitine, EGCG, Yohimbine.",
     "what_it_is":"Fat burners combine thermogenics (caffeine), fat transport (L-carnitine), lipolytic agents (yohimbine), and metabolic boosters (EGCG).","how_it_works":"Multiple mechanisms: increased thermogenesis, enhanced fat mobilisation, appetite suppression.",
     "types":[{"name":"Caffeine + Green Tea EGCG","best_for":"Thermogenesis, proven","evidence":"High"},{"name":"L-Carnitine","best_for":"Fat transport to mitochondria","evidence":"Moderate"},{"name":"Yohimbine","best_for":"Fasted cardio fat loss","evidence":"Moderate"}],
     "dosage":"Caffeine 200mg, L-Carnitine 2–4g, EGCG 400mg, Yohimbine 2.5–20mg (start low).","timing":"Fasted or pre-workout.","how_to_take":"Start at lowest dose.","hydration":"3+ L/day.",
     "training_synergy":"Most effective with calorie deficit + resistance training.",
     "best_ways_to_use":["Calorie deficit first","Yohimbine for fasted cardio","Stack caffeine with EGCG for synergy"],
     "who_should_use":["Those already in a calorie deficit"],"who_should_avoid":["Anxiety sufferers","Heart patients","High blood pressure"],
     "cycling":"Cycle stimulant components 5 days on / 2 off.",
     "benefits":["Increased metabolic rate","Enhanced fat oxidation","Appetite suppression"],
     "side_effects":[{"effect":"Anxiety and elevated heart rate","severity":"medium"},{"effect":"Yohimbine: severe anxiety in sensitive individuals","severity":"high"}],
     "research_evidence":[{"study":"Westerterp-Plantenga et al.","finding":"Caffeine + green tea extract synergistically increase energy expenditure","source":"Obes Rev 2006"}],
     "articles":[{"title":"Fat Burners: Evidence Review","author":"Examine Team","source":"Examine.com","url":"https://examine.com/supplements/fat-burners/"}],
     "magazines":[{"title":"Top Fat Burners Ranked","publisher":"Men's Fitness","url":"https://www.mensfitness.com"}],
     "books":[{"title":"Burn the Fat, Feed the Muscle","author":"Tom Venuto","year":"2013"}],
     "videos":[{"title":"Fat Burners: Do They Work?","channel":"Jeff Nippard","platform":"YouTube","url":"https://www.youtube.com/results?search_query=fat+burners+do+they+work+science"}],
     "ai_summary":"Fat burners are adjuncts, not solutions. Calorie deficit + training is the foundation. Caffeine and EGCG have the best evidence.",
     "final_recommendation":"No fat burner replaces calorie tracking and training.",
     "evidence_tier":"moderate","safe_for_beginners":True,"pubmed_ids":["20019636"],"examine_url":"https://examine.com/supplements/fat-burners/",
     "products":[{"name":"Transparent Labs Fat Burner","price_inr":3499,"rating":4.5,"badge":"🏅 Premium","best_for":"Evidence-dosed"},{"name":"MuscleBlaze Fat Burner Pro","price_inr":1499,"rating":4.3,"badge":"🔥 Popular","best_for":"India best-seller"}]},
]

_ALIAS: dict[str, dict] = {}
for _it in KB:
    _ALIAS[_it["name"].lower()] = _it
    for _a in _it.get("aliases", []):
        _ALIAS[_a.lower()] = _it
_ID_IDX: dict[str, dict] = {it["id"]: it for it in KB}



# ═══════════════════════════════════════════════════════════════════════════
# CACHE
# ═══════════════════════════════════════════════════════════════════════════

def _init_cache() -> None:
    os.makedirs(os.path.dirname(CACHE_DB), exist_ok=True)
    with sqlite3.connect(CACHE_DB) as c:
        c.execute("""CREATE TABLE IF NOT EXISTS report_cache (
            cache_key TEXT PRIMARY KEY, query TEXT NOT NULL,
            report_json TEXT NOT NULL, source TEXT DEFAULT 'kb', created_at REAL NOT NULL
        )""")
        c.execute("CREATE INDEX IF NOT EXISTS idx_crt ON report_cache(created_at)")

_init_cache()

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
    except Exception as e:
        print(f"[Cache GET] {e}"); return None

def _cache_set(key: str, query: str, results: list, source: str = "kb") -> None:
    try:
        with _cache_lock, sqlite3.connect(CACHE_DB) as c:
            c.execute("INSERT OR REPLACE INTO report_cache(cache_key,query,report_json,source,created_at) VALUES (?,?,?,?,?)",
                      (key, query, json.dumps(results), source, time.time()))
    except Exception as e:
        print(f"[Cache SET] {e}")

def _cache_stats() -> dict:
    try:
        with sqlite3.connect(CACHE_DB) as c:
            total = c.execute("SELECT COUNT(*) FROM report_cache").fetchone()[0]
            fresh = c.execute("SELECT COUNT(*) FROM report_cache WHERE created_at > ?", (time.time() - CACHE_TTL_SEC,)).fetchone()[0]
        return {"total": total, "fresh": fresh}
    except Exception:
        return {}


# ═══════════════════════════════════════════════════════════════════════════
# STRICT KB SCORING for compound queries
# ═══════════════════════════════════════════════════════════════════════════

def _score_strict(query: str, item: dict, allowed_ids: list[str],
                  goal_mods: list[str], filters: list[str], intent: str) -> int:
    iid   = item["id"]; name = item["name"].lower(); itags = " ".join(item.get("tags", [])); q = query.lower()
    if allowed_ids and iid not in allowed_ids:
        return 0
    s = 100 if (allowed_ids and iid in allowed_ids) else 0
    aliases_str = " ".join(item.get("aliases", []))
    for word in re.split(r"[\s\W]+", q):
        if len(word) < 3: continue
        if word in name: s += 8
        if word in aliases_str: s += 5
        if word in itags: s += 3
    for mod in goal_mods:
        if mod in itags: s += 60
    for f in filters:
        if f in itags: s += 60
    s += {"very_high":15,"high":10,"moderate":5,"low":0}.get(item.get("evidence_tier","moderate"), 5)
    if intent in ("dosage","research","explain"):
        if item.get("what_it_is"): s += 5
        if item.get("dosage"):     s += 5
    if intent == "product" and item.get("products"): s += 30
    return s

def _kb_strict(query: str, allowed_ids: list[str], goal_mods: list[str],
               filters: list[str], intent: str, limit: int = 3) -> list[dict]:
    scored = [{**item, "_sc": _score_strict(query, item, allowed_ids, goal_mods, filters, intent)} for item in KB]
    scored = [r for r in scored if r["_sc"] > 0]
    scored.sort(key=lambda x: x["_sc"], reverse=True)
    return [{k:v for k,v in r.items() if k != "_sc"} for r in scored[:limit]]


# ═══════════════════════════════════════════════════════════════════════════
# LIVE DATA RETRIEVAL (optional — system works without)
# ═══════════════════════════════════════════════════════════════════════════

def _pubmed(query: str, n: int = 5) -> list[dict]:
    try:
        p: dict[str,Any] = {"db":"pubmed","term":f"{query} fitness","retmax":n,"retmode":"json","sort":"relevance"}
        if PUBMED_API_KEY: p["api_key"] = PUBMED_API_KEY
        r = requests.get(PUBMED_SEARCH, params=p, timeout=6)
        if r.status_code != 200: return []
        ids = r.json().get("esearchresult",{}).get("idlist",[])
        if not ids: return []
        p2: dict[str,Any] = {"db":"pubmed","id":",".join(ids),"retmode":"json"}
        if PUBMED_API_KEY: p2["api_key"] = PUBMED_API_KEY
        r2 = requests.get(PUBMED_FETCH, params=p2, timeout=8)
        if r2.status_code != 200:
            return [{"id":pid,"source":"pubmed","trust":5,"title":f"PubMed {pid}","url":f"https://pubmed.ncbi.nlm.nih.gov/{pid}/","snippet":"","authors":"","journal":"","year":""} for pid in ids]
        arts = r2.json().get("result",{})
        out = []
        for pid in ids:
            a = arts.get(pid,{})
            auth = (a.get("authors") or [{}])[0].get("name","") + " et al."
            out.append({"id":pid,"source":"pubmed","trust":5,"title":a.get("title",f"PubMed {pid}"),
                        "authors":auth,"journal":a.get("fulljournalname",""),"year":(a.get("pubdate") or "")[:4],
                        "url":f"https://pubmed.ncbi.nlm.nih.gov/{pid}/","snippet":f"{auth}. {a.get('fulljournalname','')}."})
        return out
    except Exception as e:
        print(f"[PubMed] {e}"); return []

def _examine(name: str) -> dict | None:
    try:
        slug = re.sub(r"[^a-z0-9\-]","",name.lower().replace(" ","-"))
        url  = f"https://examine.com/supplements/{slug}/"
        r = requests.get(url, headers={"User-Agent":"FitSearchBot/5.0"}, timeout=6)
        if r.status_code != 200: return None
        m = re.search(r'<meta[^>]*name="description"[^>]*content="([^"]{50,})"', r.text)
        summary = m.group(1).strip()[:500] if m else ""
        return {"source":"examine","trust":4,"url":url,"summary":summary}
    except Exception as e:
        print(f"[Examine] {e}"); return None

def _live(query: str, entity_key: str | None) -> dict:
    term = entity_key.replace("_"," ") if entity_key else query
    live: dict = {"pubmed":[],"examine":{}}
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
        fp = ex.submit(_pubmed, term)
        fe = ex.submit(_examine, term)
        live["pubmed"]  = fp.result()
        live["examine"] = fe.result() or {}
    return live

def _evidence(live: dict) -> dict:
    return {"pubmed_refs":live.get("pubmed",[]),
            "pubmed_ids":[i["id"] for i in live.get("pubmed",[]) if "id" in i],
            "examine_url":live.get("examine",{}).get("url"),
            "examine_summary":live.get("examine",{}).get("summary","")}


# ═══════════════════════════════════════════════════════════════════════════
# CLAUDE AI SYNTHESIS (enhances KB results when API key available)
# ═══════════════════════════════════════════════════════════════════════════

_SYSTEM = """You are FitSearch AI — a world-class fitness research engine.
Enhance the provided knowledge base entry with additional depth and the latest research.

RULES:
1. Respond ONLY with valid JSON. No markdown fences.
2. Same language as user query.
3. Enrich EXISTING content — do not contradict or replace correct KB data.
4. Add more recent research_evidence entries (2020–2024).
5. Add more specific video recommendations with real YouTube creator names.
6. evidence_tier: "very_high"|"high"|"moderate"|"low"

Return the COMPLETE enriched report JSON matching this schema exactly:
{
  "name":"","tagline":"","category":"","intent":"","domain":"",
  "evidence_tier":"","safe_for_beginners":true,"legal_status":null,
  "overview":"","what_it_is":"","how_it_works":"",
  "types":[{"name":"","best_for":"","evidence":""}],
  "dosage":"","timing":"","how_to_take":"","hydration":"",
  "best_ways_to_use":[],"who_should_use":[],"who_should_avoid":[],
  "training_synergy":"","cycling":"",
  "benefits":[],"side_effects":[{"effect":"","severity":""}],
  "research_evidence":[{"study":"","finding":"","source":""}],
  "articles":[{"title":"","author":"","source":"","url":""}],
  "magazines":[{"title":"","publisher":"","url":""}],
  "books":[{"title":"","author":"","year":""}],
  "videos":[{"title":"","channel":"","platform":"YouTube","url":""}],
  "ai_summary":"","stacking":[],"final_recommendation":"","products":[],"ai_note":""
}"""

def _claude(query: str, intent: str, domain: str, entity_key: str | None,
            kb_data: dict, ev: dict) -> dict | None:
    if not ANTHROPIC_API_KEY:
        return None
    pm = ""
    if ev.get("pubmed_refs"):
        pm = "\n\nLIVE PUBMED:\n" + "\n".join(
            f"- PMID {p['id']}: {p.get('title','')} — {p.get('journal','')} {p.get('year','')}"
            for p in ev["pubmed_refs"][:4])
    ex_ctx = f"\n\nEXAMINE: {ev['examine_url']}\n{ev.get('examine_summary','')[:200]}" if ev.get("examine_url") else ""
    kb_json = json.dumps({k:v for k,v in kb_data.items() if k not in ["aliases","id","_source","_cached"]}, ensure_ascii=False)[:2000]
    msg = (f"Query: {query}\nIntent: {intent}\nDomain: {domain}\n"
           f"Entity: {entity_key or 'general'}\n\n"
           f"EXISTING KB DATA TO ENRICH:\n{kb_json}{pm}{ex_ctx}")
    try:
        resp = requests.post(ANTHROPIC_URL,
            headers={"x-api-key":ANTHROPIC_API_KEY,"anthropic-version":"2023-06-01","content-type":"application/json"},
            json={"model":"claude-sonnet-4-20250514","max_tokens":3500,"system":_SYSTEM,
                  "messages":[{"role":"user","content":msg}]},
            timeout=30)
        resp.raise_for_status()
        text = resp.json()["content"][0]["text"].strip()
        text = re.sub(r"^```(?:json)?\s*","",text); text = re.sub(r"\s*```$","",text)
        return json.loads(text)
    except Exception as e:
        print(f"[Claude] {e}"); return None


# ═══════════════════════════════════════════════════════════════════════════
# REPORT ASSEMBLY — converts any KB entry to standard rich report format
# ═══════════════════════════════════════════════════════════════════════════

def _to_report(item: dict, ev: dict, intent: str = "research",
               source: str = "kb", is_general: bool = False) -> dict:
    """
    Universal converter: works for both compound KB items and general topic items.
    Merges live PubMed refs into articles array.
    """
    articles = list(item.get("articles", []))
    # Add live PubMed refs
    existing_urls = {a.get("url","") for a in articles}
    for ref in ev.get("pubmed_refs", [])[:3]:
        url = f"https://pubmed.ncbi.nlm.nih.gov/{ref['id']}/"
        if url not in existing_urls:
            articles.append({"title":ref.get("title",f"PubMed {ref['id']}"),"author":ref.get("authors",""),
                              "source":ref.get("journal","PubMed"),"url":url})
    # Add static pubmed_ids from KB
    for pid in item.get("pubmed_ids",[]):
        url = f"https://pubmed.ncbi.nlm.nih.gov/{pid}/"
        if url not in {a.get("url","") for a in articles}:
            articles.append({"title":f"PubMed PMID {pid}","author":"","source":"PubMed","url":url})
    # Add Examine link
    exam_url = item.get("examine_url") or ev.get("examine_url")
    if exam_url and exam_url not in {a.get("url","") for a in articles}:
        articles.append({"title":f"Examine.com — {item['name']}","author":"Examine Team","source":"Examine.com","url":exam_url})

    return {
        "name":               item["name"],
        "tagline":            item.get("tagline", item.get("summary","")[:120]),
        "category":           item.get("category","supplement"),
        "intent":             item.get("intent", intent),
        "domain":             item.get("category","supplements"),
        "evidence_tier":      item.get("evidence_tier","moderate"),
        "safe_for_beginners": item.get("safe_for_beginners",True),
        "legal_status":       item.get("legal_status"),
        "overview":           item.get("what_it_is", item.get("overview", item.get("summary",""))),
        "what_it_is":         item.get("what_it_is",""),
        "how_it_works":       item.get("how_it_works",""),
        "types":              item.get("types",[]),
        "dosage":             item.get("dosage","—"),
        "timing":             item.get("timing","—"),
        "how_to_take":        item.get("how_to_take",""),
        "hydration":          item.get("hydration",""),
        "best_ways_to_use":   item.get("best_ways_to_use",[]),
        "who_should_use":     item.get("who_should_use",[]),
        "who_should_avoid":   item.get("who_should_avoid",[]),
        "training_synergy":   item.get("training_synergy",""),
        "cycling":            item.get("cycling",""),
        "benefits":           item.get("benefits",[]),
        "side_effects":       item.get("side_effects",[]),
        "research_evidence":  item.get("research_evidence",[]),
        "articles":           articles,
        "magazines":          item.get("magazines",[]),
        "books":              item.get("books",[]),
        "videos":             item.get("videos",[]),
        "ai_summary":         item.get("ai_summary", item.get("final_recommendation","")),
        "stacking":           item.get("stacking",[]),
        "final_recommendation": item.get("final_recommendation",""),
        "products":           item.get("products",[]) if intent == "product" else [],
        "ai_note":            "Curated knowledge base. Set ANTHROPIC_API_KEY for AI-enhanced reports." if source == "kb" else "AI-enhanced report.",
        "examine_url":        exam_url,
        "_source":            source,
    }


def _ai_merge_report(ai: dict, base: dict, ev: dict) -> dict:
    """Merge Claude's enhancement into the base KB report."""
    if not ai:
        return base
    # Claude enriches — we merge, keeping base as fallback for any missing field
    merged = dict(base)
    for field in ["overview","what_it_is","how_it_works","types","dosage","timing",
                  "how_to_take","hydration","best_ways_to_use","who_should_use","who_should_avoid",
                  "training_synergy","cycling","benefits","side_effects","ai_summary",
                  "stacking","final_recommendation"]:
        ai_val = ai.get(field)
        if ai_val:  # Only override if Claude actually provided content
            merged[field] = ai_val
    # Merge research_evidence (add new without duplicating)
    existing_studies = {e.get("study","") for e in merged.get("research_evidence",[])}
    for ev_item in ai.get("research_evidence",[]):
        if ev_item.get("study","") not in existing_studies:
            merged.setdefault("research_evidence",[]).append(ev_item)
    # Merge videos (add new)
    existing_titles = {v.get("title","") for v in merged.get("videos",[])}
    for v in ai.get("videos",[]):
        if v.get("title","") not in existing_titles:
            merged.setdefault("videos",[]).append(v)
    merged["ai_note"] = "AI-enhanced report with latest research."
    merged["_source"] = "ai"
    return merged


# ═══════════════════════════════════════════════════════════════════════════
# PUBLIC INTERFACE
# ═══════════════════════════════════════════════════════════════════════════

def search_knowledge(query: str, filters: list | None = None) -> list[dict]:
    """
    World-Class AI Fitness Research Engine — SELF-CONTAINED.

    Works without any API key by serving from two knowledge bases:
      1. Compound KB (19 items) — for supplement/steroid/SARM/peptide queries
      2. General Topic KB (8 topics) — for exercise/training/nutrition/fitness queries

    When ANTHROPIC_API_KEY is set, results are AI-enhanced with latest research.

    Flow:
      1. Intent + domain detection
      2. Entity extraction (compound-specific?) OR General topic match
      3. Cache check
      4. KB lookup (strict for compounds, topic match for general)
      5. Live PubMed retrieval (if network available)
      6. AI enhancement (if ANTHROPIC_API_KEY set)
      7. Return rich 17-section structured report
    """
    filters   = filters or []
    ts        = datetime.now(timezone.utc).isoformat()

    intent    = classify_intent(query)
    domain    = detect_domain(query)
    entity_key, allowed_ids = extract_primary_entity(query)
    goal_mods = list(set(_extract_goal_modifiers(query) + filters))

    # Cache check
    ckey = _cache_key(query, filters)
    cached = _cache_get(ckey)
    if cached:
        for r in cached:
            r["_cached"] = True
        return cached

    results: list[dict] = []

    if entity_key:
        # ── COMPOUND QUERY: use strict KB ────────────────────────────────
        kb = _kb_strict(query, allowed_ids, goal_mods, filters, intent, limit=3)
        lv = _live(query, entity_key)
        ev = _evidence(lv)

        if kb:
            for i, item in enumerate(kb[:3]):
                base_report = _to_report(item, ev, intent, source="kb")
                # AI enhancement for primary result
                if i == 0 and ANTHROPIC_API_KEY:
                    ai = _claude(query, intent, domain, entity_key, base_report, ev)
                    if ai:
                        base_report = _ai_merge_report(ai, base_report, ev)
                base_report["_timestamp"] = ts
                if i > 0:
                    base_report["_supplementary"] = True
                results.append(base_report)
    else:
        # ── GENERAL QUERY: use general topic KB ───────────────────────────
        topic = _find_general_topic(query)
        if topic:
            lv = _live(query, None)
            ev = _evidence(lv)
            base_report = _to_report(topic, ev, intent, source="kb", is_general=True)
            # AI enhancement
            if ANTHROPIC_API_KEY:
                ai = _claude(query, intent, domain, None, base_report, ev)
                if ai:
                    base_report = _ai_merge_report(ai, base_report, ev)
            base_report["_timestamp"] = ts
            results.append(base_report)
        else:
            # Last resort: use best-matching supplement topic
            lv = _live(query, None)
            ev = _evidence(lv)
            topic = next((t for t in GENERAL_TOPICS if t["id"] == "supplement_guide"), GENERAL_TOPICS[0])
            base_report = _to_report(topic, ev, intent, source="kb", is_general=True)
            base_report["_timestamp"] = ts
            results.append(base_report)

    _cache_set(ckey, query, results, source=results[0].get("_source","kb") if results else "kb")
    return results


def get_recommendations(recent_queries: list[str], user: dict) -> list[dict]:
    """Personalised recommendations from user history + profile."""
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
        if sc <= 1: continue
        parts = [f"Matches your {goal.replace('_',' ')} goal"]
        if level == "beginner" and item.get("safe_for_beginners"):
            parts.append("beginner-friendly")
        if item["evidence_tier"] in ("very_high","high"):
            parts.append("strong research support")
        recs.append({**item,"_sc":sc,"recommendation_reason":" · ".join(parts)})
    recs.sort(key=lambda x: x["_sc"], reverse=True)
    return [{k:v for k,v in r.items() if k != "_sc"} for r in recs[:6]]
