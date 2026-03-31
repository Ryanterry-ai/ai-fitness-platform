"""
search_ai.py  —  FitSearch AI  World-Class Fitness Research Engine  v4
=======================================================================
Pipeline: Query → Intent Detection → Domain Routing → Entity Extraction
          → Cache → KB Retrieval → Live APIs → Claude AI → Rich Output

Every result includes: What it is · How it works · Types · Dosage · Timing
· How to take · Side effects · Best ways to use · Who should use/avoid
· Research evidence · Articles · Magazines · Books · Videos · AI Summary
"""
from __future__ import annotations
import os, json, re, time, hashlib, sqlite3, threading, concurrent.futures
from datetime import datetime, timezone
from typing import Any
import requests

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
PUBMED_API_KEY    = os.getenv("PUBMED_API_KEY", "")
SERP_API_KEY      = os.getenv("SERP_API_KEY", "")

BASE_DIR      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_DB      = os.path.join(BASE_DIR, "database", "search_cache.db")
ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
PUBMED_SEARCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
PUBMED_FETCH  = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
CACHE_TTL_SEC = 86_400
_cache_lock   = threading.Lock()

# ── Domain routing ────────────────────────────────────────────────────────
QUERY_DOMAINS: dict[str, list[str]] = {
    "muscle_gain":  ["muscle gain","bulking","hypertrophy","build muscle","lean mass"],
    "fat_loss":     ["fat loss","cutting","weight loss","shred","burn fat","lose weight","lose fat","slim","tone"],
    "strength":     ["strength","powerlifting","power","strong","1rm","get stronger"],
    "endurance":    ["endurance","cardio","stamina","aerobic","running","cycling","marathon","hiit"],
    "recovery":     ["recovery","healing","injury","soreness","doms","joint pain","rehab"],
    "supplements":  ["creatine","whey","protein","pre workout","bcaa","supplement","beta alanine","citrulline","caffeine","fish oil","vitamin","zinc","magnesium","omega"],
    "steroids":     ["testosterone","tren","trenbolone","anavar","dbol","dianabol","nandrolone","deca","winstrol","steroid","anabolic","aas","pct"],
    "peptides":     ["mk677","bpc","bpc-157","ipamorelin","cjc","tb500","tb-500","sermorelin","ghrp","peptide"],
    "hgh":          ["hgh","growth hormone","somatropin","human growth","igf"],
    "sarms":        ["ostarine","lgd","ligandrol","rad140","testolone","cardarine","sarm","sarms","mk-2866"],
    "nutrition":    ["diet","nutrition","meal plan","macros","protein intake","carbs","calories","food","eating","keto"],
    "exercise":     ["exercise","workout","training","gym","lifting","sets","reps","program","routine","split","exercises for","best exercises","workout for","training for"],
}

def detect_domain(query: str) -> str:
    q = query.lower()
    scores: dict[str, int] = {}
    for domain, keywords in QUERY_DOMAINS.items():
        sc = sum(1 for kw in keywords if kw in q)
        if sc > 0:
            scores[domain] = sc
    return max(scores, key=lambda x: scores[x]) if scores else "general_fitness"

# ── Entity groups ─────────────────────────────────────────────────────────
ENTITY_GROUPS: dict[str, list[str]] = {
    "creatine":["crm_mono","crm_hcl"], "creatine_mono":["crm_mono"],
    "creatine_hcl":["crm_hcl"], "whey":["whey"], "protein":["whey"],
    "citrulline":["citrulline"], "beta_alanine":["beta_al"], "caffeine":["caffeine"],
    "pre_workout":["caffeine","citrulline","beta_al"], "sarm":["ostarine","lgd4033","rad140","mk677"],
    "ostarine":["ostarine"], "lgd4033":["lgd4033"], "rad140":["rad140"], "mk677":["mk677"],
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
    ("proteina whey","whey"),("protein powder","protein"),
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
    ("vitamin d3","vitamin_d"),("vitamin d","vitamin_d"),("cholecalciferol","vitamin_d"),
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

# ── Intent classification ─────────────────────────────────────────────────
_INTENT_RULES: list[tuple[list[str], str]] = [
    (["best brand","top brand","buy india","price india","cheapest brand","top 5 brand","top 10 brand",
      "which brand","best supplement india","affordable","value for money","recommend brand"],"product"),
    (["workout plan","training plan","training split","diet plan","meal plan","hypertrophy split",
      "push pull","4 day split","5 day split","high protein diet","macro plan","ppl split",
      "cutting diet","bulking diet","exercises for","best exercises","workout for",
      "training for","exercise for","fat loss exercises","muscle building exercises"],"exercise"),
    (["nutrition plan","what to eat","diet for","meal for","food for","macros for",
      "calories for","eating for"],"nutrition"),
    (["dosage","dose","how much","how many mg","how many grams","mcg","iu per day",
      "serving size","intake","loading phase","maintenance dose","how to take"],"dosage"),
    (["side effect","adverse effect","risk","dangerous","harmful","is it safe",
      "liver damage","kidney","toxicity","health risk","long term risk","safe for"],"side_effects"),
    (["vs","versus","compare","comparison","better than","difference between",
      "which is better","which one"],"compare"),
    (["cycle","protocol","pct","post cycle","on cycle","week cycle","blast cruise","stack protocol"],"cycle"),
    (["what is","what are","how does","explain","define","kya hai","क्या है"],"explain"),
    (["best","recommend","should i","beginner","which one","ideal for","good for",
      "top choice","for muscle gain","for fat loss","for strength","for beginners"],"recommend"),
]

def classify_intent(query: str) -> str:
    q = query.lower()
    for triggers, label in _INTENT_RULES:
        if any(t in q for t in triggers):
            return label
    return "research"

_GOAL_PHRASES: dict[str, list[str]] = {
    "muscle_gain": ["muscle gain","bulking","mass gain","hypertrophy","build muscle"],
    "fat_loss":    ["fat loss","weight loss","cutting","shred","lean","fat burning","burn fat"],
    "strength":    ["strength","powerlifting","power","strong","get stronger"],
    "endurance":   ["endurance","cardio","stamina","aerobic","running"],
    "recovery":    ["recovery","healing","injury","soreness","doms"],
    "beginner":    ["beginner","starter","new to","first time","safe","mild"],
    "advanced":    ["advanced","experienced","intermediate","serious athlete"],
}

def _extract_goal_modifiers(query: str) -> list[str]:
    q = query.lower()
    return [tag for tag, phrases in _GOAL_PHRASES.items() if any(p in q for p in phrases)]


# ═══════════════════════════════════════════════════════════════════════════
# KNOWLEDGE BASE
# ═══════════════════════════════════════════════════════════════════════════

KB: list[dict] = [
    {"id":"crm_mono","name":"Creatine monohydrate",
     "aliases":["creatine","kreatin","creatina","créatine","क्रिएटिन","肌酸"],
     "category":"supplement","tags":["strength","muscle_gain","power","beginner","creatine"],
     "summary":"Most researched ergogenic aid. Increases phosphocreatine for faster ATP regeneration.",
     "what_it_is":"Creatine monohydrate is a naturally occurring compound produced in the liver and kidneys. About 95% is stored in skeletal muscle as phosphocreatine, directly fuelling the ATP-PCr energy system during explosive efforts.",
     "how_it_works":"Creatine saturates muscle phosphocreatine stores, enabling faster ATP regeneration during high-intensity exercise. Delays fatigue, increases power output, and supports greater training volume leading to enhanced hypertrophy.",
     "types":[{"name":"Creatine Monohydrate","best_for":"Muscle gain and strength","evidence":"Very High"},{"name":"Creatine HCL","best_for":"Sensitive stomachs, less bloating","evidence":"High"},{"name":"Buffered Creatine (Kre-Alkalyn)","best_for":"Reduced bloating","evidence":"Moderate"}],
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
     "research_evidence":[{"study":"ISSN Position Stand","finding":"Creatine is the most effective ergogenic supplement for high-intensity exercise and lean body mass","source":"JISSN 2017"},{"study":"Meta-analysis of 22 RCTs","finding":"Creatine significantly increases maximal strength (8%) and weightlifting performance (14%)","source":"J Strength Cond Res 2003"}],
     "articles":[{"title":"Creatine Supplementation and Exercise Performance","author":"Jose Antonio & Conrad Ciccone","source":"J Int Soc Sports Nutr","url":"https://jissn.biomedcentral.com/articles/10.1186/1550-2783-1-2-38"}],
     "magazines":[{"title":"The Complete Creatine Guide","publisher":"Muscle & Fitness","url":"https://www.muscleandfitness.com/supplements/creatine/"},{"title":"Creatine: Everything You Need to Know","publisher":"Men's Health","url":"https://www.menshealth.com/fitness/creatine/"}],
     "books":[{"title":"The Encyclopedia of Sports Nutrition","author":"Robert Wildman & Barry Friedman","year":"2012"},{"title":"Sports Nutrition for Endurance Athletes","author":"Monique Ryan","year":"2012"}],
     "videos":[{"title":"Creatine: The Complete Guide","channel":"Jeff Nippard","platform":"YouTube","url":"https://www.youtube.com/results?search_query=jeff+nippard+creatine"},{"title":"Creatine Explained","channel":"Jeremy Ethier","platform":"YouTube","url":"https://www.youtube.com/results?search_query=jeremy+ethier+creatine"},{"title":"Does Creatine Work?","channel":"Renaissance Periodization","platform":"YouTube","url":"https://www.youtube.com/results?search_query=renaissance+periodization+creatine"}],
     "ai_summary":"Creatine Monohydrate is the most evidence-backed and cost-effective supplement for muscle gain, strength, and performance. Take 3–5g daily consistently. No loading required. No need to cycle off.",
     "stacking":["Beta-alanine","Caffeine","Whey protein"],
     "final_recommendation":"Pair 3–5g creatine monohydrate with a post-workout carb + protein meal. Start progressive overload the same week. Expect strength gains in 2–4 weeks.",
     "evidence_tier":"very_high","safe_for_beginners":True,
     "pubmed_ids":["28615996","11509496","14636102"],
     "examine_url":"https://examine.com/supplements/creatine/",
     "products":[{"name":"Optimum Nutrition Micronised Creatine","price_inr":1499,"rating":4.7,"badge":"🏅 Premium","best_for":"All users"},{"name":"MuscleBlaze Creatine Monohydrate","price_inr":749,"rating":4.5,"badge":"🔥 Popular","best_for":"Best value India"},{"name":"AS-IT-IS Creatine Monohydrate","price_inr":599,"rating":4.4,"badge":"💪 Balanced","best_for":"Budget pick"}]},

    {"id":"crm_hcl","name":"Creatine HCL",
     "aliases":["creatine hcl","creatine hydrochloride","hcl creatine","con-cret"],
     "category":"supplement","tags":["strength","muscle_gain","creatine"],
     "summary":"Higher-solubility creatine. Effective at 1–2g/day. Less bloating.",
     "what_it_is":"Creatine bonded to hydrochloric acid, dramatically increasing water solubility. Smaller effective doses mean less gastrointestinal load.",
     "how_it_works":"Same phosphocreatine resynthesis mechanism as monohydrate. HCL form absorbed faster at lower doses.",
     "types":[{"name":"Creatine HCL","best_for":"Sensitive stomachs","evidence":"High"}],
     "dosage":"1–2g/day. No loading phase needed.",
     "timing":"Pre or post-workout.",
     "how_to_take":"Mix in 150–200ml water. Dissolves faster than monohydrate.",
     "hydration":"2–3 L/day.",
     "training_synergy":"Same as monohydrate — maximised by resistance training.",
     "best_ways_to_use":["Use if monohydrate causes GI distress","No loading required","Consistent daily use"],
     "who_should_use":["GI-sensitive individuals","Those who dislike bloating"],
     "who_should_avoid":["Budget-conscious users (monohydrate better value)"],
     "cycling":"No cycling needed.",
     "benefits":["Equivalent strength gains at lower dose","Minimal bloating","Superior dissolution"],
     "side_effects":[{"effect":"Minimal GI issues","severity":"low"}],
     "research_evidence":[{"study":"Miller et al.","finding":"HCL form absorbed effectively at lower doses with less GI distress","source":"J Int Soc Sports Nutr 2009"}],
     "articles":[{"title":"Creatine HCL vs Monohydrate","author":"Examine Team","source":"Examine.com","url":"https://examine.com/supplements/creatine/"}],
     "magazines":[{"title":"Which Creatine Is Best?","publisher":"Bodybuilding.com","url":"https://www.bodybuilding.com/content/which-form-of-creatine-is-right-for-you.html"}],
     "books":[{"title":"Sports Supplementation","author":"Dr. Jose Antonio","year":"2019"}],
     "videos":[{"title":"Creatine HCL vs Monohydrate","channel":"PictureFit","platform":"YouTube","url":"https://www.youtube.com/results?search_query=creatine+hcl+vs+monohydrate"}],
     "ai_summary":"Choose Creatine HCL if monohydrate causes bloating or GI discomfort. Same muscle-building effects at a lower dose.",
     "stacking":["Citrulline malate","Beta-alanine"],
     "final_recommendation":"Choose HCL if monohydrate causes GI discomfort. Otherwise monohydrate is more cost-effective.",
     "evidence_tier":"high","safe_for_beginners":True,
     "pubmed_ids":["19844003"],"examine_url":"https://examine.com/supplements/creatine/"},

    {"id":"beta_al","name":"Beta-alanine",
     "aliases":["beta alanine","beta-alanine","carnosine precursor","beta alanina"],
     "category":"supplement","tags":["endurance","strength","pre_workout","fatigue"],
     "summary":"Amino acid precursor to carnosine. Buffers lactic acid, delays fatigue in 60–240s efforts.",
     "what_it_is":"Non-essential amino acid that pairs with histidine to form carnosine in muscle — a pH buffer against lactic acid.",
     "how_it_works":"Raises muscle carnosine 40–80% over 4–6 weeks, buffering H+ ions produced during intense exercise to delay the burning sensation and fatigue.",
     "types":[{"name":"Beta-Alanine (Standard)","best_for":"Endurance and high-rep training","evidence":"High"},{"name":"SR Beta-Alanine","best_for":"Reduced tingling","evidence":"High"}],
     "dosage":"3.2–6.4g/day split into 1.6g doses.",
     "timing":"Pre-workout or spread through day.",
     "how_to_take":"Powder or capsule. SR formulas reduce tingling.",
     "hydration":"2–3 L/day.",
     "training_synergy":"Best for high-rep resistance, HIIT, rowing, cycling. Synergises with creatine.",
     "best_ways_to_use":["Split dose to reduce tingling","Consistent daily use for 4 weeks before full effect","Stack with creatine for dual energy system coverage"],
     "who_should_use":["High-rep training athletes","Endurance athletes","CrossFitters","Combat sports athletes"],
     "who_should_avoid":["Those highly sensitive to tingling sensation"],
     "cycling":"No cycling. Benefits plateau ~10 weeks; maintain at 3.2g/day.",
     "benefits":["Delayed muscle fatigue","Higher rep capacity","Endurance in 1–4 min efforts"],
     "side_effects":[{"effect":"Tingling / paresthesia (harmless)","severity":"low"}],
     "research_evidence":[{"study":"Hobson et al. 15-study meta-analysis","finding":"Beta-alanine significantly increases exercise capacity","source":"Amino Acids 2012"}],
     "articles":[{"title":"Beta-Alanine: A Scientific Review","author":"Trexler ET et al.","source":"JISSN","url":"https://jissn.biomedcentral.com/articles/10.1186/s12970-015-0090-y"}],
     "magazines":[{"title":"Beta-Alanine Guide","publisher":"Bodybuilding.com","url":"https://www.bodybuilding.com/content/the-complete-guide-to-beta-alanine.html"}],
     "books":[{"title":"Sports Nutrition for Health Professionals","author":"Natalie Digate Muth","year":"2015"}],
     "videos":[{"title":"Beta-Alanine Explained","channel":"Jeff Nippard","platform":"YouTube","url":"https://www.youtube.com/results?search_query=beta+alanine+explained+jeff+nippard"}],
     "ai_summary":"Beta-alanine is a proven endurance supplement. It takes 4–6 weeks to fully load. The tingling is harmless. Most beneficial for sustained high-intensity efforts lasting 1–4 minutes.",
     "stacking":["Creatine monohydrate","Caffeine","L-Citrulline"],
     "final_recommendation":"Stack with creatine for comprehensive energy system coverage. Use split dosing.",
     "evidence_tier":"high","safe_for_beginners":True,
     "pubmed_ids":["22649228","27797728"],"examine_url":"https://examine.com/supplements/beta-alanine/"},

    {"id":"citrulline","name":"L-Citrulline / Citrulline malate",
     "aliases":["citrulline","citrulline malate","l-citrulline","pump supplement","no booster","citrulina"],
     "category":"supplement","tags":["pump","endurance","blood_flow","pre_workout"],
     "summary":"Converts to arginine → nitric oxide → vasodilation and muscle pump. Malate form reduces fatigue.",
     "what_it_is":"L-citrulline is converted to arginine in kidneys, then to nitric oxide. Citrulline malate adds malic acid for anti-fatigue synergy.",
     "how_it_works":"NO-mediated vasodilation increases blood flow, improving nutrient delivery, reducing waste product accumulation, and enhancing pump. Malate boosts Krebs cycle efficiency.",
     "types":[{"name":"L-Citrulline","best_for":"Pump and blood flow","evidence":"High"},{"name":"Citrulline Malate 2:1","best_for":"Pump + endurance","evidence":"High"}],
     "dosage":"L-citrulline: 6–8g. Citrulline malate 2:1: 8g. 30–60min pre-workout.",
     "timing":"30–60min pre-workout, light stomach.",
     "how_to_take":"Mix 300–400ml water. Slight tartness — juice helps.",
     "hydration":"3+ L/day. Vasodilation increases sweating.",
     "training_synergy":"Best for volume/hypertrophy days.",
     "best_ways_to_use":["Take 45–60min pre-workout","Use 8g citrulline malate for best results","Combine with caffeine and beta-alanine"],
     "who_should_use":["Bodybuilders seeking pump","Endurance athletes","High-volume trainers"],
     "who_should_avoid":["Those on blood pressure medication (consult doctor)"],
     "cycling":"No cycling needed.",
     "benefits":["Significant muscle pump","Reduced DOMS","Endurance +12–15%","Blood pressure support"],
     "side_effects":[{"effect":"GI discomfort at doses >10g","severity":"low"}],
     "research_evidence":[{"study":"Pérez-Guisado & Jakeman","finding":"8g citrulline malate significantly reduced muscle soreness 48h post-training","source":"JSCR 2010"}],
     "articles":[{"title":"L-Citrulline: Research and Uses","author":"Examine Team","source":"Examine.com","url":"https://examine.com/supplements/citrulline/"}],
     "magazines":[{"title":"Get a Better Pump with Citrulline","publisher":"Flex Magazine","url":"https://www.flex.com"}],
     "books":[{"title":"Advanced Sports Nutrition","author":"Dan Bernadot","year":"2012"}],
     "videos":[{"title":"Citrulline Malate Explained","channel":"PictureFit","platform":"YouTube","url":"https://www.youtube.com/results?search_query=citrulline+malate+explained"}],
     "ai_summary":"Citrulline malate is a top pre-workout ingredient. Take 8g 45 minutes before training for maximised pump, reduced fatigue, and improved endurance.",
     "stacking":["Beta-alanine","Caffeine","Creatine"],
     "final_recommendation":"Use 8g citrulline malate 2:1 pre-workout with beta-alanine and caffeine.",
     "evidence_tier":"high","safe_for_beginners":True,
     "pubmed_ids":["21414438","26900386"],"examine_url":"https://examine.com/supplements/citrulline/"},

    {"id":"whey","name":"Whey protein",
     "aliases":["whey","whey protein","proteina whey","व्हे प्रोटीन","乳清蛋白"],
     "category":"supplement","tags":["muscle_gain","recovery","protein","beginner"],
     "summary":"Fast-digesting milk protein with highest leucine content — optimal for muscle protein synthesis.",
     "what_it_is":"Whey is a by-product of cheese production. Available as concentrate (70–80% protein), isolate (90%+), or hydrolysate. Richest source of leucine (10–11%).",
     "how_it_works":"High leucine content triggers mTOR activation, initiating muscle protein synthesis. Fast digestion delivers amino acids to muscle rapidly post-workout.",
     "types":[{"name":"Whey Concentrate","best_for":"General muscle building, budget","evidence":"Very High"},{"name":"Whey Isolate","best_for":"Lactose intolerant, cutting phase","evidence":"Very High"},{"name":"Whey Hydrolysate","best_for":"Fastest absorption","evidence":"High"}],
     "dosage":"25–50g per serving to reach 1.6–2.2g protein/kg bodyweight daily.",
     "timing":"Post-workout optimal. Any time to supplement protein deficit.",
     "how_to_take":"Shaker with 200–300ml water or milk. Isolate mixes cleaner.",
     "hydration":"2.5–3 L/day — protein metabolism increases urea production.",
     "training_synergy":"Within 2h post-resistance training + fast carbs (banana) for insulin-driven uptake.",
     "best_ways_to_use":["Post-workout within 2 hours","With fast carbs for insulin spike","Daily to hit protein targets","Replace low-protein meals when needed"],
     "who_should_use":["Bodybuilders","Athletes","Anyone struggling to hit protein targets","Beginners"],
     "who_should_avoid":["Lactose intolerant (use isolate)","Dairy allergic","Kidney disease patients"],
     "cycling":"No cycling. Daily use to hit protein targets.",
     "benefits":["Maximises MPS via leucine","Fast post-workout absorption","Complete amino acid profile","Cost-effective"],
     "side_effects":[{"effect":"GI discomfort if lactose intolerant (use isolate)","severity":"medium"}],
     "research_evidence":[{"study":"Tang et al.","finding":"Whey protein stimulates greater muscle protein synthesis than soy or casein post-exercise","source":"Am J Clin Nutr 2009"}],
     "articles":[{"title":"Protein and Exercise","author":"Phillips SM","source":"J Nutr","url":"https://pubmed.ncbi.nlm.nih.gov/15051856/"}],
     "magazines":[{"title":"The Protein Bible","publisher":"Muscle & Fitness","url":"https://www.muscleandfitness.com/nutrition/whey-protein/"}],
     "books":[{"title":"Power Eating","author":"Susan Kleiner","year":"2014"},{"title":"The New Encyclopedia of Modern Bodybuilding","author":"Arnold Schwarzenegger","year":"1999"}],
     "videos":[{"title":"Best Protein for Muscle Growth","channel":"Jeff Nippard","platform":"YouTube","url":"https://www.youtube.com/results?search_query=jeff+nippard+best+protein+muscle+growth"}],
     "ai_summary":"Whey protein is the gold standard post-workout protein. Hit your daily protein target (1.6–2.2g/kg) and whey is the most convenient, fast-digesting tool to get there.",
     "stacking":["Creatine","Fast carbs post-workout","Casein before bed"],
     "final_recommendation":"Target total daily protein via food first; supplement shortfall with whey post-workout.",
     "evidence_tier":"very_high","safe_for_beginners":True,
     "pubmed_ids":["19589961","25048790"],"examine_url":"https://examine.com/supplements/whey-protein/",
     "products":[{"name":"ON Gold Standard Whey","price_inr":4499,"rating":4.8,"badge":"🏅 Premium","best_for":"Industry benchmark"},{"name":"MuscleBlaze Whey Protein","price_inr":2999,"rating":4.5,"badge":"🔥 Popular","best_for":"Best-seller India"},{"name":"AS-IT-IS Whey Concentrate","price_inr":1499,"rating":4.3,"badge":"💪 Balanced","best_for":"Budget"}]},

    {"id":"caffeine","name":"Caffeine",
     "aliases":["caffeine","caffeina","caféine","कैफीन","caffeine anhydrous"],
     "category":"supplement","tags":["strength","endurance","fat_loss","focus","pre_workout"],
     "summary":"Adenosine receptor antagonist. Reduces perceived exertion, boosts power output and fat oxidation.",
     "what_it_is":"Most-studied ergogenic aid. Caffeine blocks adenosine receptors in brain and peripheral tissue.",
     "how_it_works":"Blocks adenosine (fatigue signal) receptors, increases catecholamine release, enhances calcium mobilisation in muscle. Result: reduced fatigue, improved power, enhanced fat oxidation.",
     "types":[{"name":"Caffeine Anhydrous","best_for":"Precise dosing, fast absorption","evidence":"Very High"},{"name":"Coffee","best_for":"Natural source with polyphenols","evidence":"Very High"},{"name":"Di-Caffeine Malate","best_for":"Sustained release, less crash","evidence":"Moderate"}],
     "dosage":"3–6 mg/kg bodyweight (200–400mg for most adults).",
     "timing":"30–60min pre-workout. Avoid within 6h of sleep.",
     "how_to_take":"Anhydrous pills for precise dosing. Stack with L-Theanine 200mg (2:1).",
     "hydration":"Add 500ml extra water on caffeine days (mild diuretic).",
     "training_synergy":"Effective for resistance training, cardio, HIIT, team sports.",
     "best_ways_to_use":["200–300mg 30–45min pre-workout","Stack with L-Theanine for smooth focus","Cycle 5 days on, 2 days off to prevent tolerance"],
     "who_should_use":["Athletes needing performance boost","Those doing fasted cardio","Anyone needing focus"],
     "who_should_avoid":["Anxiety disorder sufferers","Heart condition patients","Pregnant women","Late-evening training"],
     "cycling":"Cycle off 1–2 weeks/month to reset adenosine receptor sensitivity.",
     "benefits":["Power output +3–7%","Endurance improvement","Fat oxidation","Focus and alertness","Reduced perceived effort"],
     "side_effects":[{"effect":"Tolerance with daily use","severity":"medium"},{"effect":"Sleep disruption if dosed too late","severity":"medium"},{"effect":"Anxiety at high doses","severity":"medium"}],
     "research_evidence":[{"study":"Grgic et al. systematic review","finding":"Caffeine significantly improves upper and lower body strength and endurance","source":"BJSM 2021"}],
     "articles":[{"title":"Caffeine and Exercise Performance","author":"Goldstein et al.","source":"JISSN","url":"https://jissn.biomedcentral.com/articles/10.1186/1550-2783-7-5"}],
     "magazines":[{"title":"The Science of Caffeine","publisher":"Men's Health","url":"https://www.menshealth.com/nutrition/caffeine/"}],
     "books":[{"title":"Caffeine for Sports Performance","author":"Louise Burke","year":"2013"}],
     "videos":[{"title":"Caffeine: How it Works","channel":"Thomas DeLauer","platform":"YouTube","url":"https://www.youtube.com/results?search_query=caffeine+sports+performance+science"},{"title":"Should You Use Caffeine?","channel":"Jeff Nippard","platform":"YouTube","url":"https://www.youtube.com/results?search_query=jeff+nippard+caffeine"}],
     "ai_summary":"Caffeine is the most proven ergogenic supplement. Take 3–5 mg/kg 30–60min before training. Stack with L-Theanine for focus without anxiety. Cycle regularly to prevent tolerance.",
     "stacking":["L-Theanine 200mg","L-Citrulline","Beta-alanine"],
     "final_recommendation":"3–5 mg/kg pre-workout with 200mg L-Theanine. Cycle 5 on / 2 off monthly.",
     "evidence_tier":"very_high","safe_for_beginners":True,
     "pubmed_ids":["34445894","20019636"],"examine_url":"https://examine.com/supplements/caffeine/"},

    {"id":"ostarine","name":"Ostarine (MK-2866)",
     "aliases":["ostarine","mk2866","mk-2866","enobosarm","mk 2866"],
     "category":"sarm","tags":["muscle_gain","fat_loss","recomp","sarm"],
     "summary":"Mildest SARM. Selective androgen receptor modulator. Lean mass gains. Research chemical.",
     "what_it_is":"Nonsteroidal SARM developed for muscle-wasting diseases. Selectively binds androgen receptors in muscle and bone.",
     "how_it_works":"Activates androgen receptors in muscle and bone selectively, producing anabolic effects without full androgenic side effects of testosterone.",
     "types":[{"name":"Ostarine (MK-2866)","best_for":"Recomposition, first SARM","evidence":"Moderate"}],
     "dosage":"10–25mg/day. Start at 10mg first cycle.",
     "timing":"Once daily, consistent time, with or without food.",
     "how_to_take":"Oral liquid or capsule. Use precise dosing syringe for liquid.",
     "hydration":"2.5–3 L/day.",
     "training_synergy":"Recomposition nutrition (maintenance calories) works well.",
     "best_ways_to_use":["Start low at 10mg","Get bloodwork before starting","Run 8-week cycle maximum","Monitor for suppression symptoms"],
     "who_should_use":["Experienced trainees considering SARMs","Those wanting recomp effect"],
     "who_should_avoid":["Beginners","Under 21","Women (virilisation risk)","Anyone without bloodwork access"],
     "cycling":"8-week cycles. Bloodwork before and 4–6 weeks post-cycle.",
     "benefits":["2–4kg lean mass gain in 8 weeks","Fat loss support","Joint healing","Lower suppression vs steroids"],
     "side_effects":[{"effect":"Mild testosterone suppression","severity":"medium"},{"effect":"HDL reduction","severity":"medium"},{"effect":"Liver enzyme elevation possible","severity":"low"}],
     "research_evidence":[{"study":"Dalton et al.","finding":"Ostarine significantly increased lean body mass in cancer patients with muscle wasting","source":"Cancer Res 2011"}],
     "articles":[{"title":"Ostarine: Research Overview","author":"Examine Team","source":"Examine.com","url":"https://examine.com/supplements/ostarine/"}],
     "magazines":[{"title":"SARMs Guide","publisher":"More Plates More Dates","url":"https://www.moreplatesmoredates.com"}],
     "books":[{"title":"SARMs: A Practical Guide","author":"Various","year":"2020"}],
     "videos":[{"title":"Ostarine: The Complete Guide","channel":"Thomas DeLauer","platform":"YouTube","url":"https://www.youtube.com/results?search_query=ostarine+mk+2866+complete+guide"}],
     "ai_summary":"Ostarine is the mildest SARM with the most research. Still requires bloodwork. Not approved for human use. Bloodwork is non-negotiable before any SARM cycle.",
     "stacking":["Cardarine GW-501516","MK-677 Ibutamoren"],
     "final_recommendation":"Bloodwork baseline mandatory. Start 10mg, run 8 weeks, recheck bloodwork.",
     "evidence_tier":"moderate","safe_for_beginners":False,
     "pubmed_ids":["20814882","23631853"],"examine_url":"https://examine.com/supplements/ostarine/",
     "legal_status":"Research chemical — not approved for human use. Banned by WADA."},

    {"id":"lgd4033","name":"LGD-4033 (Ligandrol)",
     "aliases":["lgd4033","lgd-4033","ligandrol","lgd 4033"],
     "category":"sarm","tags":["muscle_gain","strength","bulking","sarm"],
     "summary":"Most anabolic SARM. Significant suppression — full PCT required. Not for beginners.",
     "what_it_is":"LGD-4033 is the most potent SARM discovered to date. Phase I trial showed lean mass gains at 1mg/day.",
     "how_it_works":"High-affinity androgen receptor agonist in muscle and bone, producing anabolic effects comparable to low-dose testosterone.",
     "types":[{"name":"LGD-4033 (Ligandrol)","best_for":"Bulking, lean mass","evidence":"Moderate"}],
     "dosage":"5–10mg/day for 8–12 weeks.","timing":"Once daily.",
     "how_to_take":"Oral liquid or capsule.","hydration":"3 L/day.",
     "training_synergy":"Progressive overload, high protein (2+g/kg), calorie surplus.",
     "best_ways_to_use":["Always run bloodwork","Full PCT protocol after cycle"],
     "who_should_use":["Experienced trainees with bloodwork access"],
     "who_should_avoid":["Beginners","Under 21","Women","Those without bloodwork"],
     "cycling":"8–12 week cycles. Full PCT: Nolvadex 40/20/20/20.",
     "benefits":["3–5kg lean mass in 8–12 weeks","Major strength gains","Improved recovery"],
     "side_effects":[{"effect":"Significant testosterone suppression","severity":"high"},{"effect":"HDL reduction","severity":"high"}],
     "research_evidence":[{"study":"Basaria et al.","finding":"LGD-4033 dose-dependently increased lean body mass in healthy men","source":"Lancet 2013"}],
     "articles":[{"title":"LGD-4033: Phase I Trial","author":"Basaria S et al.","source":"Lancet","url":"https://pubmed.ncbi.nlm.nih.gov/24518353/"}],
     "magazines":[{"title":"SARMs Overview","publisher":"Flex Magazine","url":"https://flex.com"}],
     "books":[{"title":"Beyond Steroids","author":"Wade Lightheart","year":"2019"}],
     "videos":[{"title":"LGD 4033 Complete Guide","channel":"Greg Doucette","platform":"YouTube","url":"https://www.youtube.com/results?search_query=lgd+4033+ligandrol+guide"}],
     "ai_summary":"LGD-4033 is the most anabolic SARM. Significant suppression makes full PCT non-negotiable. Only for experienced users with bloodwork access.",
     "stacking":["MK-677 Ibutamoren","Cardarine"],
     "final_recommendation":"Bloodwork mandatory. Not for beginners. Full SERM PCT required.",
     "evidence_tier":"moderate","safe_for_beginners":False,
     "pubmed_ids":["24518353"],"examine_url":"https://examine.com/supplements/lgd-4033/",
     "legal_status":"Research chemical — not approved for human use. Banned by WADA."},

    {"id":"rad140","name":"RAD-140 (Testolone)",
     "aliases":["rad140","rad-140","testolone","rad 140"],
     "category":"sarm","tags":["muscle_gain","strength","fat_loss","sarm"],
     "summary":"Most potent SARM. Hepatotoxicity and strong suppression reported.",
     "what_it_is":"RAD-140 has the highest anabolic:androgenic ratio of any SARM. Hepatotoxicity case reports raise serious concerns.",
     "how_it_works":"Very high-affinity androgen receptor agonist. More anabolic than testosterone at equivalent doses.",
     "types":[{"name":"RAD-140 (Testolone)","best_for":"Advanced users only","evidence":"Low"}],
     "dosage":"5–15mg/day for 8–10 weeks.","timing":"Once daily.",
     "how_to_take":"Oral liquid or capsule.","hydration":"3+ L/day.",
     "training_synergy":"Progressive overload essential.",
     "best_ways_to_use":["Liver function tests mandatory","Short cycles (8 weeks max)","PCT mandatory"],
     "who_should_use":["Very experienced users who have used other SARMs"],
     "who_should_avoid":["Beginners","Those without LFT access","Women","Under 25"],
     "cycling":"8–10 week cycles. Full PCT mandatory.",
     "benefits":["Very high anabolic potency","Significant lean mass","Fat loss support"],
     "side_effects":[{"effect":"Strong testosterone suppression","severity":"high"},{"effect":"Hepatotoxicity — liver damage in case reports","severity":"high"}],
     "research_evidence":[{"study":"Jayaraman et al.","finding":"RAD-140 demonstrated anabolic effects in animal models","source":"Endocrinology 2014"}],
     "articles":[{"title":"RAD-140: Research Overview","author":"Examine Team","source":"Examine.com","url":"https://examine.com/supplements/rad-140/"}],
     "magazines":[{"title":"Testolone: The Ultimate Guide","publisher":"Evolutionary.org","url":"https://www.evolutionary.org"}],
     "books":[{"title":"SARMs: Research Guide","author":"Various","year":"2021"}],
     "videos":[{"title":"RAD 140 Complete Guide","channel":"Greg Doucette","platform":"YouTube","url":"https://www.youtube.com/results?search_query=rad+140+testolone+guide"}],
     "ai_summary":"RAD-140 is the most potent SARM but carries the highest risk including hepatotoxicity. Liver function tests mandatory. Not recommended for most users.",
     "final_recommendation":"Liver function tests mandatory. Not recommended due to hepatotoxicity risk.",
     "evidence_tier":"low","safe_for_beginners":False,
     "pubmed_ids":["20427478"],"legal_status":"Research chemical — not approved for human use. Banned by WADA."},

    {"id":"mk677","name":"MK-677 (Ibutamoren)",
     "aliases":["mk677","mk-677","ibutamoren","nutrobal","mk 677"],
     "category":"sarm","tags":["muscle_gain","fat_loss","recovery","hgh","sleep","sarm"],
     "summary":"Oral GH secretagogue. Stimulates pituitary GH/IGF-1 release. Non-suppressive — no PCT needed.",
     "what_it_is":"MK-677 is an oral ghrelin receptor agonist stimulating GH and IGF-1 release. Not a SARM — no androgen receptor binding, no testosterone suppression.",
     "how_it_works":"Mimics ghrelin to stimulate GH secretion from the pituitary gland, elevating GH and IGF-1. Improves muscle, fat loss, sleep quality, and recovery.",
     "types":[{"name":"MK-677 (Ibutamoren)","best_for":"GH elevation, recovery, sleep","evidence":"Moderate"}],
     "dosage":"10–25mg/day before bed.","timing":"Before bed to align with natural overnight GH pulse.",
     "how_to_take":"Oral capsule or liquid.","hydration":"3 L/day — water retention common early on.",
     "training_synergy":"Resistance training amplifies lean mass. Fasted morning cardio amplifies fat loss.",
     "best_ways_to_use":["Take before bed consistently","Monitor blood glucose if diabetic","Long-term use (12–24 weeks) for best results"],
     "who_should_use":["Those wanting GH benefits without injections","Recovery-focused athletes","Those with sleep issues"],
     "who_should_avoid":["Diabetics (elevates blood glucose)","Those with insulin resistance"],
     "cycling":"12–24 week cycles. No PCT needed.",
     "benefits":["Elevated GH and IGF-1","Improved sleep depth","Lean mass gain","Recovery support"],
     "side_effects":[{"effect":"Increased appetite and water retention","severity":"medium"},{"effect":"Elevated fasting glucose","severity":"medium"}],
     "research_evidence":[{"study":"Murphy et al.","finding":"MK-677 significantly increased GH and IGF-1 levels in elderly subjects","source":"JCEM 1998"}],
     "articles":[{"title":"MK-677: Research Summary","author":"Examine Team","source":"Examine.com","url":"https://examine.com/supplements/mk-677/"}],
     "magazines":[{"title":"Ibutamoren Guide","publisher":"More Plates More Dates","url":"https://www.moreplatesmoredates.com"}],
     "books":[{"title":"Growth Hormone Optimization","author":"Various","year":"2020"}],
     "videos":[{"title":"MK-677: Everything You Need to Know","channel":"Thomas DeLauer","platform":"YouTube","url":"https://www.youtube.com/results?search_query=mk+677+ibutamoren+complete+guide"}],
     "ai_summary":"MK-677 is unique — oral, non-suppressive, and elevates GH naturally. Best taken before bed. Monitor blood glucose. Great for recovery, sleep, and lean mass.",
     "stacking":["Ostarine","LGD-4033"],
     "final_recommendation":"Stack with Ostarine or LGD for synergistic results. Monitor IGF-1 and fasting glucose quarterly.",
     "evidence_tier":"moderate","safe_for_beginners":True,
     "pubmed_ids":["11149771"],"examine_url":"https://examine.com/supplements/mk-677/",
     "legal_status":"Research chemical — not approved for human use."},

    {"id":"test_e","name":"Testosterone enanthate",
     "aliases":["testosterone enanthate","test e","testo e","testosterone","testosteron"],
     "category":"steroid","tags":["muscle_gain","strength","bulking","testosterone","steroid"],
     "summary":"Gold standard anabolic injectable. Long-ester testosterone with predictable kinetics and decades of data.",
     "what_it_is":"Synthetic testosterone with enanthate ester providing stable blood levels. The body's primary anabolic hormone delivered exogenously.",
     "how_it_works":"Binds androgen receptors throughout body, activating protein synthesis, nitrogen retention, IGF-1 production, and satellite cell activation for muscle hypertrophy.",
     "types":[{"name":"Testosterone Enanthate","best_for":"Beginner/intermediate cycles","evidence":"Very High"},{"name":"Testosterone Cypionate","best_for":"US standard, weekly injection","evidence":"Very High"},{"name":"Testosterone Propionate","best_for":"Fast-acting, more frequent injection","evidence":"Very High"}],
     "dosage":"Beginner: 300–500mg/week (split E3.5D). Intermediate: 500–750mg/week.",
     "timing":"IM or SubQ injection every 3.5 days for stable levels.",
     "how_to_take":"IM (glute/quads/delts) or SubQ. Rotate sites. 23–25G for injection.",
     "hydration":"2.5–3 L/day. Monitor blood pressure.",
     "training_synergy":"Progressive overload, high protein (2–2.4g/kg), calorie surplus, adequate sleep.",
     "best_ways_to_use":["Run bloodwork before, mid-cycle, and post-PCT","Use AI (anastrozole) to manage estrogen","Start with testosterone-only first cycle","Maintain healthy lifestyle throughout"],
     "who_should_use":["Adult men over 21 with prior natural training","Under medical supervision for TRT"],
     "who_should_avoid":["Under 21","Women (virilisation)","Heart disease patients","Anyone not willing to run bloodwork"],
     "cycling":"12–16 week cycles. AI required. PCT: Nolvadex 40/40/20/20mg starting 2 weeks post-last injection.",
     "benefits":["Significant lean mass and strength gains","Improved recovery","Libido and well-being"],
     "side_effects":[{"effect":"Complete testosterone suppression","severity":"high"},{"effect":"Aromatisation — AI required","severity":"medium"},{"effect":"Cardiovascular strain","severity":"high"},{"effect":"Acne and hair loss","severity":"medium"}],
     "research_evidence":[{"study":"Bhasin et al.","finding":"Testosterone dose-dependently increases fat-free mass and muscle size","source":"NEJM 1996"}],
     "articles":[{"title":"Testosterone and Muscle","author":"Bhasin S et al.","source":"NEJM","url":"https://pubmed.ncbi.nlm.nih.gov/8637536/"}],
     "magazines":[{"title":"TRT Guide","publisher":"Men's Health","url":"https://www.menshealth.com/health/testosterone/"}],
     "books":[{"title":"The New Testosterone Treatment","author":"Abraham Morgentaler","year":"2014"},{"title":"Testosterone for Life","author":"Abraham Morgentaler","year":"2009"}],
     "videos":[{"title":"Testosterone Cycle Guide","channel":"Greg Doucette","platform":"YouTube","url":"https://www.youtube.com/results?search_query=testosterone+enanthate+cycle+beginners+guide"}],
     "ai_summary":"Testosterone enanthate is the gold standard for anabolic cycles. Bloodwork is non-negotiable. AI management, PCT, and cardiovascular monitoring are mandatory for safe use.",
     "stacking":["Anastrozole (AI)","NPP/Deca (intermediate+)","Anavar (cut)"],
     "final_recommendation":"Bloodwork before, mid-cycle, post-PCT. AI + cardiovascular monitoring non-negotiable.",
     "evidence_tier":"very_high","safe_for_beginners":False,
     "pubmed_ids":["8637536","11502560"],
     "legal_status":"Schedule III (USA). Prescription only in UK, India, Canada, Australia."},

    {"id":"anavar","name":"Anavar (Oxandrolone)",
     "aliases":["anavar","oxandrolone","var","oxandrin"],
     "category":"steroid","tags":["fat_loss","strength","cutting","steroid"],
     "summary":"Mild oral anabolic steroid. Popular for cutting. Preserves muscle in calorie deficit.",
     "what_it_is":"Oxandrolone is a 17α-alkylated oral anabolic steroid with low androgenic activity. Popular for cutting and with women at low doses.",
     "how_it_works":"Binds androgen receptors to stimulate protein synthesis and nitrogen retention. Low aromatisation means minimal water retention — ideal for cutting.",
     "types":[{"name":"Anavar (Oxandrolone)","best_for":"Cutting, lean mass preservation","evidence":"High"}],
     "dosage":"Men: 20–80mg/day split. Women: 5–20mg/day.",
     "timing":"Split twice daily — 9h half-life.","how_to_take":"Oral tablet.","hydration":"2.5–3 L/day.",
     "training_synergy":"Calorie deficit + high protein (2.2–2.4g/kg) for cutting benefit.",
     "best_ways_to_use":["Run liver support","Keep cycles short (6–8 weeks)","Monitor lipids closely"],
     "who_should_use":["Cutting phase athletes","Women (low doses)"],
     "who_should_avoid":["Beginners","Those with liver issues"],
     "cycling":"6–8 weeks. PCT required.",
     "benefits":["Muscle preservation on cut","Strength gains without mass","Minimal water retention"],
     "side_effects":[{"effect":"Liver stress (oral 17-AA)","severity":"medium"},{"effect":"HDL reduction","severity":"high"},{"effect":"Virilisation in women (dose-dependent)","severity":"high"}],
     "research_evidence":[{"study":"Multiple clinical trials","finding":"Oxandrolone significantly preserves lean mass during caloric restriction","source":"Multiple sources"}],
     "articles":[{"title":"Anavar Profile","author":"William Llewellyn","source":"Anabolics","url":"https://pubmed.ncbi.nlm.nih.gov/7998639/"}],
     "magazines":[{"title":"Anavar for Cutting","publisher":"Muscle & Performance","url":"https://www.muscleandperformance.com"}],
     "books":[{"title":"Anabolics","author":"William Llewellyn","year":"2017"}],
     "videos":[{"title":"Anavar Cycle Guide","channel":"Greg Doucette","platform":"YouTube","url":"https://www.youtube.com/results?search_query=anavar+cycle+guide+oxandrolone"}],
     "ai_summary":"Anavar is one of the milder steroids but still requires careful monitoring. Ideal for cutting phases. PCT mandatory. Liver and lipid monitoring throughout.",
     "final_recommendation":"Liver function and lipid tests mandatory. Not for beginners. SERM PCT required.",
     "evidence_tier":"high","safe_for_beginners":False,
     "legal_status":"Schedule III (USA). Prescription only."},

    {"id":"nandrolone","name":"Nandrolone / NPP / Deca-Durabolin",
     "aliases":["nandrolone","deca","deca durabolin","npp","nandrolone decanoate"],
     "category":"steroid","tags":["muscle_gain","strength","bulking","joint_health","steroid"],
     "summary":"19-nor anabolic steroid. Lean mass gains and joint lubrication. Requires prolactin management.",
     "what_it_is":"19-nortestosterone derivative available as NPP (short ester) or Deca-Durabolin (decanoate).",
     "how_it_works":"Highly anabolic with notable collagen synthesis benefits reducing joint pain. Significant prolactin elevation requires cabergoline management.",
     "types":[{"name":"Nandrolone Decanoate (Deca)","best_for":"Long cycles, joint support","evidence":"High"},{"name":"Nandrolone Phenylpropionate (NPP)","best_for":"Shorter cycles, faster clearance","evidence":"High"}],
     "dosage":"NPP: 300–400mg/week (E3.5D). Deca: 200–400mg/week (once weekly).",
     "timing":"IM injection on schedule.","how_to_take":"IM injection. Always run with testosterone base.","hydration":"3 L/day.",
     "training_synergy":"Progressive overload + high protein. Joint benefits allow higher training volume.",
     "best_ways_to_use":["Always run with testosterone","Use cabergoline for prolactin","Run bloodwork throughout"],
     "who_should_use":["Intermediate+ users","Those with joint issues"],
     "who_should_avoid":["Beginners","Women (high virilisation risk)","Those without prolactin management"],
     "cycling":"12–16 weeks with testosterone base. Full PCT required.",
     "benefits":["Lean mass gains","Joint lubrication","Collagen synthesis","Improved recovery"],
     "side_effects":[{"effect":"Prolactin elevation — cabergoline required","severity":"high"},{"effect":"Full testosterone suppression","severity":"high"},{"effect":"Erectile dysfunction without test base","severity":"high"}],
     "research_evidence":[{"study":"Bhasin et al.","finding":"Nandrolone increases lean mass and reduces fat mass","source":"NEJM 1996"}],
     "articles":[{"title":"Nandrolone Profile","author":"William Llewellyn","source":"Anabolics","url":"https://pubmed.ncbi.nlm.nih.gov/8637536/"}],
     "magazines":[{"title":"Deca Durabolin Guide","publisher":"Muscle & Fitness","url":"https://www.muscleandfitness.com"}],
     "books":[{"title":"Anabolics","author":"William Llewellyn","year":"2017"}],
     "videos":[{"title":"Nandrolone/Deca Guide","channel":"Greg Doucette","platform":"YouTube","url":"https://www.youtube.com/results?search_query=nandrolone+deca+durabolin+cycle"}],
     "ai_summary":"Nandrolone is highly effective but complex. Cabergoline for prolactin and testosterone base are non-negotiable.",
     "final_recommendation":"Must run with testosterone base. Cabergoline mandatory. Bloodwork throughout.",
     "evidence_tier":"high","safe_for_beginners":False,
     "legal_status":"Controlled substance. Prescription only."},

    {"id":"bpc157","name":"BPC-157",
     "aliases":["bpc157","bpc-157","body protection compound","bpc 157"],
     "category":"peptide","tags":["recovery","injury","joint_health","gut","healing","peptide"],
     "summary":"15-amino acid peptide from gastric juice. Accelerates tendon, ligament, muscle, and gut healing.",
     "what_it_is":"BPC-157 is a synthetic peptide from human gastric juice protein. Animal research shows accelerated healing via GH receptor upregulation and angiogenesis.",
     "how_it_works":"Promotes angiogenesis, upregulates GH receptors in tendons, reduces inflammation, and accelerates tissue repair across multiple tissue types.",
     "types":[{"name":"BPC-157 (Injectable)","best_for":"Systemic and local healing","evidence":"Moderate"},{"name":"BPC-157 (Oral)","best_for":"Gut healing","evidence":"Moderate"}],
     "dosage":"250–500mcg/day subcutaneous or intramuscular.",
     "timing":"Near injury site (local) or systemic abdomen. Once or twice daily.",
     "how_to_take":"Reconstitute with bacteriostatic water. Insulin syringe 29–31G. Refrigerate.","hydration":"2.5–3 L/day.",
     "training_synergy":"Active rehabilitation during protocol maximises healing.",
     "best_ways_to_use":["Inject near injury site for localised healing","500mcg twice daily for acute injuries","Combine with TB-500 for systemic healing"],
     "who_should_use":["Athletes with injuries","Those with gut issues","Post-surgery recovery"],
     "who_should_avoid":["Active cancer (potential angiogenesis promotion)","Pregnant women"],
     "cycling":"Acute injury: 4–6 weeks. Chronic: 8–12 weeks.",
     "benefits":["Accelerated tendon/ligament healing","Gut lining repair","Anti-inflammatory","Angiogenesis"],
     "side_effects":[{"effect":"Injection site irritation (mild, transient)","severity":"low"}],
     "research_evidence":[{"study":"Sikiric et al.","finding":"BPC-157 accelerates healing of various tissue types in animal models","source":"Curr Pharm Des 2013"}],
     "articles":[{"title":"BPC-157: Research Review","author":"Examine Team","source":"Examine.com","url":"https://examine.com/supplements/bpc-157/"}],
     "magazines":[{"title":"Healing Peptides Guide","publisher":"More Plates More Dates","url":"https://www.moreplatesmoredates.com"}],
     "books":[{"title":"Peptide Protocols","author":"Jay Campbell","year":"2019"}],
     "videos":[{"title":"BPC-157: The Healing Peptide","channel":"Derek at MPMD","platform":"YouTube","url":"https://www.youtube.com/results?search_query=bpc+157+healing+peptide+guide"}],
     "ai_summary":"BPC-157 is one of the most promising healing peptides. Source quality and sterility are critical.",
     "stacking":["TB-500","Ipamorelin/CJC-1295"],
     "final_recommendation":"Source quality critical. Sterility non-negotiable.",
     "evidence_tier":"moderate","safe_for_beginners":True,
     "pubmed_ids":["23439702","21447935"],"examine_url":"https://examine.com/supplements/bpc-157/",
     "legal_status":"Research chemical — not approved for human use."},

    {"id":"hgh","name":"Human Growth Hormone (HGH)",
     "aliases":["hgh","human growth hormone","growth hormone","gh","somatropin","rhgh"],
     "category":"peptide","tags":["fat_loss","muscle_gain","recovery","anti_aging","hgh"],
     "summary":"Recombinant somatropin. Potent lipolytic and anabolic agent. Prescription only globally.",
     "what_it_is":"Recombinant HGH (somatropin) stimulates IGF-1 (anabolic) and drives lipolysis directly.",
     "how_it_works":"Binds GH receptors throughout body, stimulating IGF-1 production in liver (muscle growth) and directly promoting lipolysis (fat breakdown). Strengthens connective tissue.",
     "types":[{"name":"Pharmaceutical Grade HGH","best_for":"Maximum purity and safety","evidence":"Very High"},{"name":"GH Peptides (Ipamorelin etc.)","best_for":"Stimulating natural GH","evidence":"Moderate"}],
     "dosage":"Anti-aging/fat loss: 1–3 IU/day. Bodybuilding: 4–8 IU/day (significantly higher risk).",
     "timing":"SubQ injection on waking (fat loss) or before bed (GH pulse).",
     "how_to_take":"SubQ abdomen, rotating sites. Reconstitute with bacteriostatic water. Store 2–8°C.","hydration":"3+ L/day.",
     "training_synergy":"Resistance training + fasted morning cardio maximise body composition.",
     "best_ways_to_use":["Start at 1–2 IU and titrate up slowly","Monitor IGF-1 quarterly","Use pharma-grade only","Physician supervision mandatory"],
     "who_should_use":["Adults over 30 with confirmed GH deficiency under medical supervision"],
     "who_should_avoid":["Active cancer","Diabetics without close monitoring","Anyone without physician supervision","Under 25"],
     "cycling":"Anti-aging: 6–12 months continuous. Bodybuilding: 16–24 weeks.",
     "benefits":["Significant visceral fat reduction","Lean mass retention","Connective tissue strengthening","Improved sleep quality"],
     "side_effects":[{"effect":"Carpal tunnel","severity":"medium"},{"effect":"Insulin resistance","severity":"high"},{"effect":"Acromegaly at high sustained doses","severity":"high"}],
     "research_evidence":[{"study":"Rudman et al.","finding":"HGH supplementation in elderly men significantly increased lean mass and reduced fat mass","source":"NEJM 1990"}],
     "articles":[{"title":"HGH in Adults with GH Deficiency","author":"Vance ML","source":"NEJM","url":"https://pubmed.ncbi.nlm.nih.gov/2388534/"}],
     "magazines":[{"title":"HGH: Truth vs Hype","publisher":"Men's Health","url":"https://www.menshealth.com/hgh/"}],
     "books":[{"title":"Grow Young with HGH","author":"Ronald Klatz","year":"1997"}],
     "videos":[{"title":"HGH: Everything You Need to Know","channel":"Derek at MPMD","platform":"YouTube","url":"https://www.youtube.com/results?search_query=hgh+growth+hormone+complete+guide"}],
     "ai_summary":"HGH is highly effective but expensive, prescription-only, and requires physician supervision. Pharmaceutical-grade only. Start at 1–2 IU and titrate based on IGF-1 bloodwork.",
     "stacking":["Testosterone (synergistic)","T3 (advanced)","Insulin (extreme danger)"],
     "final_recommendation":"Physician supervision mandatory. IGF-1, fasting glucose, HbA1c quarterly. Pharmaceutical-grade only.",
     "evidence_tier":"very_high","safe_for_beginners":False,
     "pubmed_ids":["2388534"],"legal_status":"Prescription only worldwide. Banned by WADA."},

    {"id":"vitamin_d","name":"Vitamin D3 + K2",
     "aliases":["vitamin d","vitamin d3","cholecalciferol","vit d","vitamina d"],
     "category":"supplement","tags":["health","testosterone","immune","bone","recovery"],
     "summary":"Essential fat-soluble vitamin-hormone. Deficiency widespread. Regulates testosterone, immunity, bone density.",
     "what_it_is":"D3 (cholecalciferol) is a fat-soluble prohormone synthesised in skin on UV exposure. K2 (MK-7) directs calcium to bone.",
     "how_it_works":"Acts as a steroid hormone, binding VDR receptors throughout the body. Regulates calcium metabolism, immune function, inflammation, and testosterone production.",
     "types":[{"name":"Vitamin D3 + K2 MK-7","best_for":"Optimal absorption and calcium direction","evidence":"Very High"}],
     "dosage":"D3: 2,000–5,000 IU/day. K2 MK-7: 100–200mcg/day.",
     "timing":"With largest fat-containing meal for optimal absorption.",
     "how_to_take":"Softgel capsule or oil drops. D3 + K2 in same meal.","hydration":"Standard 2.5–3 L/day.",
     "training_synergy":"Adequate D3 supports testosterone production and muscle function.",
     "best_ways_to_use":["Test serum 25-OH-D first","Target 40–70 ng/mL","Take with fat-containing meal","Always pair with K2"],
     "who_should_use":["Everyone (widespread deficiency)","Athletes","Office workers"],
     "who_should_avoid":["Hypercalcemia patients without doctor guidance"],
     "cycling":"Year-round — sunlight rarely achieves optimal levels.",
     "benefits":["Testosterone support","Immune regulation","Bone density","Mood improvement"],
     "side_effects":[{"effect":"Toxicity only at >10,000 IU/day without monitoring","severity":"low"}],
     "research_evidence":[{"study":"Pilz et al.","finding":"Vitamin D supplementation significantly increased testosterone levels in deficient men","source":"Horm Metab Res 2011"}],
     "articles":[{"title":"Vitamin D Deficiency","author":"Holick MF","source":"NEJM","url":"https://pubmed.ncbi.nlm.nih.gov/17556697/"}],
     "magazines":[{"title":"Why Everyone Needs Vitamin D","publisher":"Men's Health","url":"https://www.menshealth.com/vitamin-d/"}],
     "books":[{"title":"The Vitamin D Solution","author":"Michael Holick","year":"2011"}],
     "videos":[{"title":"Vitamin D: Complete Guide","channel":"Thomas DeLauer","platform":"YouTube","url":"https://www.youtube.com/results?search_query=vitamin+d+supplement+complete+guide"}],
     "ai_summary":"Vitamin D3 deficiency is epidemic. Test your levels and supplement accordingly. Always pair D3 with K2. Most people need 3,000–5,000 IU/day.",
     "stacking":["Magnesium","Omega-3"],
     "final_recommendation":"Test serum 25-OH-D. Target 40–70 ng/mL. Daily with K2.",
     "evidence_tier":"very_high","safe_for_beginners":True,
     "pubmed_ids":["21154195"],"examine_url":"https://examine.com/supplements/vitamin-d/"},

    {"id":"omega3","name":"Omega-3 fish oil (EPA + DHA)",
     "aliases":["omega 3","fish oil","omega-3","epa dha","omega 3 fish oil"],
     "category":"supplement","tags":["health","recovery","anti_inflammatory","cardiovascular"],
     "summary":"EPA + DHA reduce systemic inflammation, improve cardiovascular markers, support joints and brain.",
     "what_it_is":"Long-chain omega-3 polyunsaturated fatty acids from marine sources.",
     "how_it_works":"EPA and DHA compete with arachidonic acid in cell membranes, reducing pro-inflammatory eicosanoid production. Improve triglycerides, HDL, and support muscle protein synthesis.",
     "types":[{"name":"Fish Oil (EPA + DHA)","best_for":"General anti-inflammatory, cardiovascular","evidence":"Very High"},{"name":"Algae Oil","best_for":"Vegan DHA source","evidence":"High"}],
     "dosage":"3–6g combined EPA + DHA per day (not total oil volume).",
     "timing":"With meals to minimise fish aftertaste.","how_to_take":"Softgel or liquid. Enteric-coated if sensitive.","hydration":"Standard 2.5–3 L/day.",
     "training_synergy":"Anti-inflammatory effects reduce DOMS and support recovery.",
     "best_ways_to_use":["Check EPA + DHA content not just total oil","Take with fatty meals","Nordic Naturals or pharmaceutical-grade"],
     "who_should_use":["Everyone","Especially steroid users (cardiovascular protection)"],
     "who_should_avoid":["Fish allergy (use algae oil)","High blood thinners (doctor guidance)"],
     "cycling":"Daily, year-round.",
     "benefits":["Systemic anti-inflammatory","Cardiovascular protection","Joint health","MPS support"],
     "side_effects":[{"effect":"Fish aftertaste (take with meals)","severity":"low"}],
     "research_evidence":[{"study":"Smith et al.","finding":"Omega-3 supplementation enhanced muscle protein synthesis response to amino acids","source":"JCEM 2011"}],
     "articles":[{"title":"Omega-3 Fatty Acids and Exercise","author":"Smith GI et al.","source":"JCEM","url":"https://pubmed.ncbi.nlm.nih.gov/22334723/"}],
     "magazines":[{"title":"Why Every Athlete Should Take Fish Oil","publisher":"Men's Health","url":"https://www.menshealth.com/fish-oil/"}],
     "books":[{"title":"The Omega Rx Zone","author":"Barry Sears","year":"2002"}],
     "videos":[{"title":"Fish Oil: Complete Guide","channel":"Thomas DeLauer","platform":"YouTube","url":"https://www.youtube.com/results?search_query=fish+oil+omega+3+complete+guide"}],
     "ai_summary":"Omega-3 is one of the most important foundational supplements. Check EPA + DHA content on label. Essential for cardiovascular health, inflammation control, and recovery.",
     "stacking":["Vitamin D3/K2","Curcumin"],
     "final_recommendation":"Prioritise EPA + DHA mg on label. Nordic Naturals or pharmaceutical-grade brands.",
     "evidence_tier":"very_high","safe_for_beginners":True,
     "pubmed_ids":["19589961"],"examine_url":"https://examine.com/supplements/fish-oil/"},

    {"id":"zinc_magnesium","name":"Zinc & Magnesium (ZMA)",
     "aliases":["zma","zinc magnesium","zinc","magnesium","magnesium glycinate"],
     "category":"supplement","tags":["testosterone","sleep","recovery","health"],
     "summary":"Zinc supports testosterone synthesis; magnesium improves sleep, reduces cortisol. Both depleted in athletes.",
     "what_it_is":"ZMA combines zinc (testosterone, immunity) and magnesium (sleep, cortisol regulation, 300+ enzymatic reactions).",
     "how_it_works":"Zinc is a cofactor for testosterone biosynthesis enzymes. Magnesium enhances GABA signalling for sleep and reduces cortisol. Both depleted through sweat.",
     "types":[{"name":"ZMA (Zinc + Magnesium + B6)","best_for":"Testosterone support and sleep","evidence":"High"},{"name":"Magnesium Glycinate alone","best_for":"Sleep and cortisol reduction","evidence":"High"}],
     "dosage":"Zinc: 25–45mg/day. Magnesium: 300–500mg glycinate or malate.",
     "timing":"Before bed on empty stomach.","how_to_take":"Capsule. Avoid zinc with food.","hydration":"Standard 2.5–3 L/day.",
     "training_synergy":"Zinc and magnesium support testosterone and sleep — critical for training adaptation.",
     "best_ways_to_use":["Take before bed","Magnesium glycinate for best absorption","Test levels if deficiency suspected"],
     "who_should_use":["Athletes (sweat depletes both)","Those with sleep issues","Those with low testosterone"],
     "who_should_avoid":["Those on certain antibiotics (zinc competes for absorption)"],
     "cycling":"Daily, year-round.",
     "benefits":["Testosterone support when deficient","Sleep quality improvement","Cortisol reduction","Immune function"],
     "side_effects":[{"effect":"Nausea if zinc taken with food","severity":"low"}],
     "research_evidence":[{"study":"Prasad et al.","finding":"Zinc deficiency is associated with reduced testosterone levels","source":"Nutrition 1996"}],
     "articles":[{"title":"ZMA and Athletic Performance","author":"Brilla & Conte","source":"J Exerc Physiol","url":"https://pubmed.ncbi.nlm.nih.gov/10738264/"}],
     "magazines":[{"title":"The Benefits of ZMA","publisher":"Bodybuilding.com","url":"https://www.bodybuilding.com/content/the-benefits-of-zma.html"}],
     "books":[{"title":"Sports Nutrition Essentials","author":"Robert Murray","year":"2015"}],
     "videos":[{"title":"ZMA: Does It Work?","channel":"PictureFit","platform":"YouTube","url":"https://www.youtube.com/results?search_query=zma+zinc+magnesium+supplement+review"}],
     "ai_summary":"Zinc and magnesium are foundational supplements most athletes are deficient in. Magnesium glycinate for best absorption. Take before bed for testosterone and sleep benefits.",
     "final_recommendation":"Use magnesium glycinate. Test serum zinc and magnesium if deficiency suspected.",
     "evidence_tier":"high","safe_for_beginners":True,
     "pubmed_ids":["10738264"],"examine_url":"https://examine.com/supplements/zma/"},

    {"id":"fat_burner_stack","name":"Fat burner supplements",
     "aliases":["fat burner","fat burning supplement","thermogenic","fat loss supplement"],
     "category":"supplement","tags":["fat_loss","cutting","thermogenic","metabolism"],
     "summary":"Evidence-based fat loss supplements: Caffeine, L-Carnitine, EGCG, Yohimbine.",
     "what_it_is":"Fat burners combine thermogenics (caffeine, synephrine), fat transport agents (L-carnitine), lipolytic agents (yohimbine), and metabolic boosters (EGCG).",
     "how_it_works":"Multiple mechanisms: increased thermogenesis, enhanced fat mobilisation and oxidation, appetite suppression, and improved exercise performance in a calorie deficit.",
     "types":[{"name":"Caffeine + Green Tea EGCG","best_for":"Thermogenesis, proven","evidence":"High"},{"name":"L-Carnitine","best_for":"Fat transport to mitochondria","evidence":"Moderate"},{"name":"Yohimbine","best_for":"Fasted cardio fat loss","evidence":"Moderate"}],
     "dosage":"Caffeine 200mg, L-Carnitine 2–4g, EGCG 400mg, Yohimbine 2.5–20mg (start low).",
     "timing":"Fasted or pre-workout. Yohimbine requires fasted state.",
     "how_to_take":"Start at lowest dose. Assess tolerance over 5–7 days.","hydration":"3+ L/day.",
     "training_synergy":"Most effective with calorie deficit + resistance training.",
     "best_ways_to_use":["Calorie deficit first — no supplement replaces that","Yohimbine for fasted cardio","Stack caffeine with EGCG for synergy"],
     "who_should_use":["Those already in a calorie deficit wanting extra edge"],
     "who_should_avoid":["Anxiety sufferers","Heart patients","High blood pressure"],
     "cycling":"Cycle stimulant components 5 days on / 2 off.",
     "benefits":["Increased metabolic rate","Enhanced fat oxidation","Appetite suppression","Energy boost in deficit"],
     "side_effects":[{"effect":"Anxiety and elevated heart rate","severity":"medium"},{"effect":"Yohimbine: severe anxiety in sensitive individuals","severity":"high"}],
     "research_evidence":[{"study":"Westerterp-Plantenga et al.","finding":"Caffeine + green tea extract synergistically increase energy expenditure","source":"Obes Rev 2006"}],
     "articles":[{"title":"Fat Burners: Evidence Review","author":"Examine Team","source":"Examine.com","url":"https://examine.com/supplements/fat-burners/"}],
     "magazines":[{"title":"Top Fat Burners Ranked","publisher":"Men's Fitness","url":"https://www.mensfitness.com"}],
     "books":[{"title":"Burn the Fat, Feed the Muscle","author":"Tom Venuto","year":"2013"}],
     "videos":[{"title":"Fat Burners: Do They Work?","channel":"Jeff Nippard","platform":"YouTube","url":"https://www.youtube.com/results?search_query=fat+burners+do+they+work+science"}],
     "ai_summary":"Fat burners are adjuncts, not solutions. Calorie deficit + training is the foundation. Caffeine and EGCG have the best evidence. Yohimbine works best in fasted state.",
     "final_recommendation":"No fat burner replaces calorie tracking and training. Use as an adjunct to a structured deficit.",
     "evidence_tier":"moderate","safe_for_beginners":True,
     "pubmed_ids":["20019636"],"examine_url":"https://examine.com/supplements/fat-burners/",
     "products":[{"name":"Transparent Labs Fat Burner","price_inr":3499,"rating":4.5,"badge":"🏅 Premium","best_for":"Evidence-dosed"},{"name":"MuscleBlaze Fat Burner Pro","price_inr":1499,"rating":4.3,"badge":"🔥 Popular","best_for":"India best-seller"}]},
]

_ALIAS: dict[str, dict] = {}
for _it in KB:
    _ALIAS[_it["name"].lower()] = _it
    for _a in _it.get("aliases", []):
        _ALIAS[_a.lower()] = _it

_ID_IDX: dict[str, dict] = {it["id"]: it for it in KB}


# ═══════════════════════════════════════════════════════════════════════════
# CACHE  (SQLite — thread-safe, 24h TTL)
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
    raw = json.dumps({"q": query.lower().strip(), "f": sorted(filters)}, sort_keys=True)
    return hashlib.sha256(raw.encode()).hexdigest()[:32]

def _cache_get(key: str) -> list | None:
    try:
        with _cache_lock, sqlite3.connect(CACHE_DB) as c:
            row = c.execute(
                "SELECT report_json, created_at FROM report_cache WHERE cache_key=?", (key,)
            ).fetchone()
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
            fresh = c.execute(
                "SELECT COUNT(*) FROM report_cache WHERE created_at > ?",
                (time.time() - CACHE_TTL_SEC,)
            ).fetchone()[0]
        return {"total": total, "fresh": fresh}
    except Exception:
        return {}


# ═══════════════════════════════════════════════════════════════════════════
# STRICT KB SCORING  — entity-locked relevance
# ═══════════════════════════════════════════════════════════════════════════

def _score_strict(
    query: str, item: dict, allowed_ids: list[str],
    goal_mods: list[str], filters: list[str], intent: str,
) -> int:
    iid   = item["id"]
    name  = item["name"].lower()
    itags = " ".join(item.get("tags", []))
    q     = query.lower()
    # Hard exclude — if allowed_ids set and item not in it → 0
    if allowed_ids and iid not in allowed_ids:
        return 0
    s = 0
    if allowed_ids and iid in allowed_ids:
        s += 100   # entity membership dominant bonus
    for word in re.split(r"[\s\W]+", q):
        if len(word) < 3:
            continue
        aliases_str = " ".join(item.get("aliases", []))
        if word in name:        s += 8
        if word in aliases_str: s += 5
        if word in itags:       s += 3
    for mod in goal_mods:
        if mod in itags: s += 60   # filter re-rank boost
    for f in filters:
        if f in itags:   s += 60
    s += {"very_high":15,"high":10,"moderate":5,"low":0}.get(
        item.get("evidence_tier","moderate"), 5)
    if intent in ("dosage","research","explain"):
        if item.get("what_it_is"): s += 5
        if item.get("dosage"):     s += 5
    if intent == "product":
        if item.get("products"):   s += 30
    return s

def _kb_strict(
    query: str, allowed_ids: list[str], goal_mods: list[str],
    filters: list[str], intent: str, limit: int = 3,
) -> list[dict]:
    scored = [
        {**item, "_sc": _score_strict(query, item, allowed_ids, goal_mods, filters, intent)}
        for item in KB
    ]
    scored = [r for r in scored if r["_sc"] > 0]
    scored.sort(key=lambda x: x["_sc"], reverse=True)
    return [{k:v for k,v in r.items() if k != "_sc"} for r in scored[:limit]]


# ═══════════════════════════════════════════════════════════════════════════
# LIVE DATA RETRIEVAL  (parallel: PubMed + Examine + SerpAPI)
# ═══════════════════════════════════════════════════════════════════════════

def _pubmed(query: str, n: int = 5) -> list[dict]:
    try:
        p: dict[str, Any] = {
            "db":"pubmed","term":f"{query} supplement fitness",
            "retmax":n,"retmode":"json","sort":"relevance"
        }
        if PUBMED_API_KEY:
            p["api_key"] = PUBMED_API_KEY
        r = requests.get(PUBMED_SEARCH, params=p, timeout=8)
        if r.status_code != 200:
            return []
        ids = r.json().get("esearchresult",{}).get("idlist",[])
        if not ids:
            return []
        p2: dict[str, Any] = {"db":"pubmed","id":",".join(ids),"retmode":"json"}
        if PUBMED_API_KEY:
            p2["api_key"] = PUBMED_API_KEY
        r2 = requests.get(PUBMED_FETCH, params=p2, timeout=10)
        if r2.status_code != 200:
            return [{"id":pid,"source":"pubmed","trust":5,
                     "title":f"PubMed {pid}","url":f"https://pubmed.ncbi.nlm.nih.gov/{pid}/",
                     "snippet":"","authors":"","journal":"","year":""} for pid in ids]
        arts = r2.json().get("result",{})
        out = []
        for pid in ids:
            a = arts.get(pid,{})
            auth = (a.get("authors") or [{}])[0].get("name","") + " et al."
            out.append({
                "id":pid,"source":"pubmed","trust":5,
                "title":a.get("title",f"PubMed {pid}"),
                "authors":auth,"journal":a.get("fulljournalname",""),
                "year":(a.get("pubdate") or "")[:4],
                "url":f"https://pubmed.ncbi.nlm.nih.gov/{pid}/",
                "snippet":f"{auth}. {a.get('fulljournalname','')}.",
            })
        return out
    except Exception as e:
        print(f"[PubMed] {e}")
        return []

def _examine(name: str) -> dict | None:
    try:
        slug = re.sub(r"[^a-z0-9\-]","",name.lower().replace(" ","-"))
        url  = f"https://examine.com/supplements/{slug}/"
        r = requests.get(url, headers={"User-Agent":"FitSearchBot/4.0"}, timeout=8)
        if r.status_code != 200:
            return None
        m = re.search(r'<meta[^>]*name="description"[^>]*content="([^"]{50,})"', r.text)
        summary = m.group(1).strip()[:500] if m else ""
        return {"source":"examine","trust":4,"url":url,
                "summary":summary,"snippet":summary[:200]}
    except Exception as e:
        print(f"[Examine] {e}")
        return None

def _serp(query: str) -> list[dict]:
    if not SERP_API_KEY:
        return []
    try:
        r = requests.get("https://serpapi.com/search.json",
            params={"q":f"{query} site:examine.com OR site:pubmed.ncbi.nlm.nih.gov",
                    "api_key":SERP_API_KEY,"engine":"google","num":5,"hl":"en"},
            timeout=8)
        if r.status_code != 200:
            return []
        return [{"source":"serp","trust":2,
                 "title":res.get("title",""),"url":res.get("link",""),
                 "snippet":res.get("snippet","")}
                for res in r.json().get("organic_results",[])[:5]]
    except Exception as e:
        print(f"[SerpAPI] {e}")
        return []

def _live(query: str, entity_key: str | None) -> dict:
    term = entity_key.replace("_"," ") if entity_key else query
    live: dict = {"pubmed":[],"examine":{},"serp":[]}
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
        fp = ex.submit(_pubmed, term)
        fe = ex.submit(_examine, term)
        fs = ex.submit(_serp, query)
        live["pubmed"]  = fp.result()
        live["examine"] = fe.result() or {}
        live["serp"]    = fs.result()
    return live

def _evidence(live: dict) -> dict:
    return {
        "pubmed_refs":     live.get("pubmed",[]),
        "pubmed_ids":      [i["id"] for i in live.get("pubmed",[]) if "id" in i],
        "examine_url":     live.get("examine",{}).get("url"),
        "examine_summary": live.get("examine",{}).get("summary",""),
    }



# ═══════════════════════════════════════════════════════════════════════════
# CLAUDE AI SYNTHESIS — World-Class Research Report Generator
# ═══════════════════════════════════════════════════════════════════════════

_SYSTEM = """You are FitSearch AI — a world-class fitness research engine.

Generate a comprehensive structured report for ANY fitness query.
For supplement queries: complete supplement research guide.
For exercise/training queries: complete training science guide.
For nutrition queries: complete nutrition guide.
For steroid/SARM/peptide/HGH queries: complete compound guide with safety info.

CRITICAL RULES:
1. Respond ONLY with valid JSON. No markdown fences, no text outside JSON.
2. Same language as user query.
3. ALL arrays must have real content — never return empty arrays.
4. For general fitness queries (exercises, workouts): generate training guide content.
5. Include REAL book titles, REAL YouTube channels, REAL journal names.
6. evidence_tier: "very_high"|"high"|"moderate"|"low"
7. safe_for_beginners: false for steroids, most SARMs, advanced protocols.
8. Include legal_status for controlled/research substances.

Return this exact JSON:
{
  "name": "Topic name (e.g. 'Fat Loss Exercises for Women' or 'Creatine Monohydrate')",
  "tagline": "One compelling expert sentence",
  "category": "supplement|sarm|steroid|peptide|exercise|nutrition|general",
  "intent": "research|exercise|nutrition|dosage|cycle|compare|product|side_effects|explain|recommend",
  "domain": "supplements|steroids|sarms|peptides|hgh|exercise|nutrition|general_fitness",
  "evidence_tier": "very_high|high|moderate|low",
  "safe_for_beginners": true,
  "legal_status": null,
  "overview": "2-3 paragraph comprehensive expert overview",
  "what_it_is": "Background, definition, and origin",
  "how_it_works": "Mechanism of action / exercise science explanation",
  "types": [
    {"name": "Type or exercise name", "best_for": "Best use case", "evidence": "Evidence level"}
  ],
  "dosage": "Specific dosage info OR training volume (sets/reps/frequency)",
  "timing": "When and how often",
  "how_to_take": "Administration tips OR exercise execution tips",
  "hydration": "Fluid intake recommendations",
  "best_ways_to_use": ["actionable tip 1","tip 2","tip 3","tip 4","tip 5"],
  "who_should_use": ["group 1","group 2","group 3"],
  "who_should_avoid": ["contraindication 1","contraindication 2"],
  "training_synergy": "How to combine with training for maximum effect",
  "cycling": "Cycling protocol OR periodisation for exercise",
  "benefits": ["specific benefit 1","benefit 2","benefit 3","benefit 4"],
  "side_effects": [
    {"effect": "description", "severity": "low|medium|high"}
  ],
  "research_evidence": [
    {"study": "Author(s) or study name", "finding": "Key quantified finding", "source": "Journal, year"}
  ],
  "articles": [
    {"title": "Real article title", "author": "Real author", "source": "Real journal/site", "url": "Real URL or search URL"}
  ],
  "magazines": [
    {"title": "Article title", "publisher": "Real publisher name", "url": "URL"}
  ],
  "books": [
    {"title": "Real book title", "author": "Real author", "year": "Year"}
  ],
  "videos": [
    {"title": "Video title", "channel": "Real YouTube channel", "platform": "YouTube", "url": "https://www.youtube.com/results?search_query=relevant+search"}
  ],
  "ai_summary": "Expert 2-3 sentence summary and verdict",
  "stacking": ["related item 1","related item 2"],
  "final_recommendation": "3-4 sentence expert actionable recommendation",
  "products": [],
  "ai_note": "Confidence and evidence quality note"
}

For EXERCISE queries like "best exercises for fat loss for females":
- name: "Fat Loss Exercises for Women"
- types: list exercise types (HIIT, resistance training, cardio etc.)
- dosage → "Training Volume": sets, reps, sessions per week
- how_to_take → "Execution Tips": proper form and technique tips
- research_evidence: real exercise science studies
- books: real fitness/training books
- videos: real YouTube fitness channels (Jeff Nippard, Stephanie Buttermore, etc.)

For SUPPLEMENT queries like "best creatine for muscle gain":
- Cover all forms, dosages, timing, stacking
- Include PubMed references, Examine.com link
- real product info if product intent"""


def _claude(
    query: str, intent: str, domain: str,
    entity_key: str | None, kb_items: list[dict], ev: dict,
) -> dict | None:
    if not ANTHROPIC_API_KEY:
        return None

    # Build PubMed context
    pm = ""
    if ev.get("pubmed_refs"):
        pm = "\n\nLIVE PUBMED:\n" + "\n".join(
            f"- PMID {p['id']}: {p.get('title','')} — {p.get('journal','')} {p.get('year','')}"
            for p in ev["pubmed_refs"][:5]
        )

    # Build Examine context
    ex = ""
    if ev.get("examine_url"):
        ex = f"\n\nEXAMINE.COM: {ev['examine_url']}\n{ev.get('examine_summary','')[:300]}"

    # Build KB context
    kb_ctx = ""
    for item in kb_items[:2]:
        fields = {k:v for k,v in item.items()
                  if k not in ["aliases","id","products"] and v}
        kb_ctx += f"\n\nKB — {item['name']}:\n{json.dumps(fields, ensure_ascii=False)[:1200]}"

    entity_label = entity_key if entity_key else (
        "GENERAL FITNESS QUERY — no specific compound detected. "
        "Generate a comprehensive fitness/exercise/nutrition guide relevant to the query."
    )
    msg = (
        f"Query: {query}\n"
        f"Intent: {intent}\nDomain: {domain}\n"
        f"Entity: {entity_label}\n"
        f"IMPORTANT: Populate ALL arrays with real content. "
        f"research_evidence, articles, magazines, books, videos must NEVER be empty."
        f"{kb_ctx}{pm}{ex}"
    )

    try:
        resp = requests.post(
            ANTHROPIC_URL,
            headers={"x-api-key":ANTHROPIC_API_KEY,
                     "anthropic-version":"2023-06-01",
                     "content-type":"application/json"},
            json={"model":"claude-sonnet-4-20250514","max_tokens":4000,
                  "system":_SYSTEM,
                  "messages":[{"role":"user","content":msg}]},
            timeout=35,
        )
        resp.raise_for_status()
        text = resp.json()["content"][0]["text"].strip()
        text = re.sub(r"^```(?:json)?\s*","",text)
        text = re.sub(r"\s*```$","",text)
        return json.loads(text)
    except Exception as e:
        print(f"[Claude] {e}")
        return None


# ═══════════════════════════════════════════════════════════════════════════
# REPORT ASSEMBLY
# ═══════════════════════════════════════════════════════════════════════════

def _kb_to_report(item: dict, ev: dict, intent: str = "research") -> dict:
    """Convert KB item to full rich report format."""
    articles = list(item.get("articles", []))
    for pid in (ev.get("pubmed_ids") or item.get("pubmed_ids",[]))[:3]:
        articles.append({"title":f"PubMed PMID {pid}","author":"","source":"PubMed",
                         "url":f"https://pubmed.ncbi.nlm.nih.gov/{pid}/"})
    if item.get("examine_url") or ev.get("examine_url"):
        exam_url = item.get("examine_url") or ev.get("examine_url")
        articles.append({"title":f"Examine.com — {item['name']}","author":"Examine Team",
                         "source":"Examine.com","url":exam_url})
    return {
        "name":               item["name"],
        "tagline":            item.get("summary","")[:120],
        "category":           item.get("category","supplement"),
        "intent":             intent,
        "domain":             item.get("category","supplements"),
        "evidence_tier":      item.get("evidence_tier","moderate"),
        "safe_for_beginners": item.get("safe_for_beginners",True),
        "legal_status":       item.get("legal_status"),
        "overview":           item.get("what_it_is", item.get("summary","")),
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
        "cycling":            item.get("cycling","No cycling required."),
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
        "ai_note":            "Curated knowledge base. Set ANTHROPIC_API_KEY for AI-enhanced reports.",
        "examine_url":        item.get("examine_url") or ev.get("examine_url"),
        "_source":            "kb",
    }


def _ai_to_report(ai: dict, ev: dict) -> dict:
    """Normalise Claude output to final report format."""
    articles = list(ai.get("articles",[]))
    existing = {a.get("url","") for a in articles}
    for ref in ev.get("pubmed_refs",[])[:3]:
        url = f"https://pubmed.ncbi.nlm.nih.gov/{ref['id']}/"
        if url not in existing:
            articles.append({"title":ref.get("title",f"PubMed {ref['id']}"),
                              "author":ref.get("authors",""),
                              "source":ref.get("journal","PubMed"),"url":url})
    if ev.get("examine_url") and ev["examine_url"] not in existing:
        articles.append({"title":f"Examine.com — {ai.get('name','Supplement')}",
                         "author":"Examine Team","source":"Examine.com",
                         "url":ev["examine_url"]})
    return {
        "name":               ai.get("name","Research Report"),
        "tagline":            ai.get("tagline",""),
        "category":           ai.get("category","supplement"),
        "intent":             ai.get("intent","research"),
        "domain":             ai.get("domain","general_fitness"),
        "evidence_tier":      ai.get("evidence_tier","moderate"),
        "safe_for_beginners": ai.get("safe_for_beginners",True),
        "legal_status":       ai.get("legal_status"),
        "overview":           ai.get("overview",ai.get("what_it_is","")),
        "what_it_is":         ai.get("what_it_is",""),
        "how_it_works":       ai.get("how_it_works",""),
        "types":              ai.get("types",[]),
        "dosage":             ai.get("dosage","—"),
        "timing":             ai.get("timing","—"),
        "how_to_take":        ai.get("how_to_take",""),
        "hydration":          ai.get("hydration",""),
        "best_ways_to_use":   ai.get("best_ways_to_use",[]),
        "who_should_use":     ai.get("who_should_use",[]),
        "who_should_avoid":   ai.get("who_should_avoid",[]),
        "training_synergy":   ai.get("training_synergy",""),
        "cycling":            ai.get("cycling",""),
        "benefits":           ai.get("benefits",[]),
        "side_effects":       ai.get("side_effects",[]),
        "research_evidence":  ai.get("research_evidence",[]),
        "articles":           articles,
        "magazines":          ai.get("magazines",[]),
        "books":              ai.get("books",[]),
        "videos":             ai.get("videos",[]),
        "ai_summary":         ai.get("ai_summary",""),
        "stacking":           ai.get("stacking",[]),
        "final_recommendation": ai.get("final_recommendation",""),
        "products":           ai.get("products",[]),
        "ai_note":            ai.get("ai_note","AI-generated research report."),
        "examine_url":        ev.get("examine_url"),
        "_source":            "ai",
    }


def _fallback(query: str, ts: str, domain: str) -> dict:
    return {
        "name":f"Search: {query}","tagline":"Set ANTHROPIC_API_KEY for AI research reports.",
        "category":"general","intent":"research","domain":domain,
        "evidence_tier":"moderate","safe_for_beginners":True,"legal_status":None,
        "overview":f"No pre-built knowledge found for '{query}'. Set ANTHROPIC_API_KEY for comprehensive AI research reports on any fitness topic.",
        "what_it_is":"—","how_it_works":"—","types":[],
        "dosage":"—","timing":"—","how_to_take":"—","hydration":"—",
        "best_ways_to_use":[],"who_should_use":[],"who_should_avoid":[],
        "training_synergy":"—","cycling":"—",
        "benefits":[],"side_effects":[],
        "research_evidence":[],
        "articles":[{"title":"PubMed Research Database","author":"","source":"PubMed","url":"https://pubmed.ncbi.nlm.nih.gov"}],
        "magazines":[{"title":"Healthline Fitness","publisher":"Healthline","url":"https://www.healthline.com/fitness"}],
        "books":[{"title":"The New Encyclopedia of Modern Bodybuilding","author":"Arnold Schwarzenegger","year":"1999"}],
        "videos":[{"title":f"Search results: {query}","channel":"Jeff Nippard","platform":"YouTube",
                   "url":f"https://www.youtube.com/results?search_query={'+'.join(query.split())}"}],
        "ai_summary":"Set ANTHROPIC_API_KEY environment variable to enable full AI research reports.",
        "stacking":[],"final_recommendation":"Set ANTHROPIC_API_KEY for AI-powered answers.",
        "products":[],"ai_note":"Fallback — no KB match and no AI key.",
        "examine_url":None,"_source":"fallback","_timestamp":ts,
    }


# ═══════════════════════════════════════════════════════════════════════════
# PUBLIC INTERFACE
# ═══════════════════════════════════════════════════════════════════════════

def search_knowledge(query: str, filters: list | None = None) -> list[dict]:
    """
    World-Class AI Fitness Research Engine.

    Key fix: General fitness queries (exercises, workouts, nutrition) that
    don't match any specific compound entity now route directly to Claude AI
    for a comprehensive guide — they no longer pull irrelevant supplement KB
    results like HGH appearing for 'best exercises for fat loss for females'.
    """
    filters   = filters or []
    ts        = datetime.now(timezone.utc).isoformat()

    intent    = classify_intent(query)
    domain    = detect_domain(query)
    entity_key, allowed_ids = extract_primary_entity(query)
    goal_mods = list(set(_extract_goal_modifiers(query) + filters))

    ckey   = _cache_key(query, filters)
    cached = _cache_get(ckey)
    if cached:
        for r in cached:
            r["_cached"] = True
        return cached

    # KB lookup ONLY for compound/supplement queries with a detected entity
    kb = []
    if entity_key:
        kb = _kb_strict(query, allowed_ids, goal_mods, filters, intent, limit=3)

    # Live retrieval
    lv = _live(query, entity_key)
    ev = _evidence(lv)

    # Claude handles ALL queries — compounds with KB context, general with domain context
    ai = _claude(query, intent, domain, entity_key, kb, ev)

    results: list[dict] = []

    if ai and any(ai.get(k) for k in ["what_it_is","overview","benefits","how_it_works","types"]):
        r = _ai_to_report(ai, ev)
        r["_timestamp"] = ts
        results.append(r)
        # Supplementary KB card for same entity only
        if entity_key and len(kb) > 1:
            for item in kb[1:2]:
                if item["name"].lower() != ai.get("name","").lower():
                    sr = _kb_to_report(item, {}, intent)
                    sr["_timestamp"] = ts
                    sr["_supplementary"] = True
                    results.append(sr)
    elif kb:
        for item in kb[:3]:
            r = _kb_to_report(item, ev if not results else {}, intent)
            r["_timestamp"] = ts
            results.append(r)
    else:
        results = [_fallback(query, ts, domain)]

    _cache_set(ckey, query, results, source="ai" if ai else "kb")
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
        if goal in item.get("tags",[]):                                          sc += 4
        if item.get("safe_for_beginners") and level == "beginner":               sc += 3
        if not item.get("safe_for_beginners") and level in ("intermediate","advanced"): sc += 2
        if item["evidence_tier"] in ("very_high","high"):                        sc += 1
        if sc <= 1:
            continue
        parts = [f"Matches your {goal.replace('_',' ')} goal"]
        if level == "beginner" and item.get("safe_for_beginners"):
            parts.append("beginner-friendly")
        if item["evidence_tier"] in ("very_high","high"):
            parts.append("strong research support")
        recs.append({**item,"_sc":sc,"recommendation_reason":" · ".join(parts)})
    recs.sort(key=lambda x: x["_sc"], reverse=True)
    return [{k:v for k,v in r.items() if k != "_sc"} for r in recs[:6]]
