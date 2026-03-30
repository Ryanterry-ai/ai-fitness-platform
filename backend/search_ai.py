"""
search_ai.py  —  FitSearch AI Hybrid Search Engine  (v2 — relevance fixed)
===========================================================================

BUGS FIXED vs v1:
  1. TAG LEAK  — compound tags no longer boost unrelated items.
     Tags extracted from a detected compound now ONLY boost items that also
     contain that compound. Global tag pool no longer cross-contaminates
     unrelated supplements.

  2. COMPOUND GATE  — items that share NO compound match are hard-capped at
     a low score unless the query is intentionally broad (e.g. "best for
     muscle gain" with no compound named). This prevents Whey and Testosterone
     from appearing in a creatine query.

  3. INTENT-AWARE ROUTING  — three distinct output paths:
       research_intent  → 10-section evidence report (PubMed, dosage, risks…)
       product_intent   → product recommendation list (name, price, tips)
       training_intent  → structured day-plan or protocol

  4. REAL-TIME FILTER EXECUTION  — cache keys now include filter state AND a
     version stamp ("live" if filters changed since last search). The /search
     route accepts force_fresh=True to bypass cache when filters change.

  5. RELEVANCE THRESHOLD  — items scoring below MIN_SCORE (configurable) are
     excluded, preventing barely-relevant results from appearing.

  6. PRODUCT KNOWLEDGE BASE  — curated product lists for "best X in India/USA"
     style queries, returned as structured product cards.

Pipeline:
  Query → Intent + Entity detection → Compound-gated scoring
        → Cache lookup → Live retrieval (parallel) → Evidence filtering
        → Claude call (research) or Product DB (product) → Cache write → Results
"""

from __future__ import annotations

import os, json, re, time, hashlib, sqlite3, threading
from datetime import datetime, timezone
from typing import Any

import requests

# ── API keys ──────────────────────────────────────────────────────────────
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
PUBMED_API_KEY    = os.getenv("PUBMED_API_KEY", "")
SERP_API_KEY      = os.getenv("SERP_API_KEY", "")

# ── Paths ─────────────────────────────────────────────────────────────────
BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_DB  = os.path.join(BASE_DIR, "database", "search_cache.db")

# ── Constants ─────────────────────────────────────────────────────────────
ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
PUBMED_SEARCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
PUBMED_FETCH  = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
OPENFDA_URL   = "https://api.fda.gov/drug/event.json"
CACHE_TTL_SEC = 86400   # 24 h for research queries
FILTER_TTL    = 300     # 5 min when filters active (near-real-time)
MIN_SCORE     = 15      # FIX: minimum score to appear in results

_cache_lock = threading.Lock()


# ═══════════════════════════════════════════════════════════════════════════
# KNOWLEDGE BASE — research compounds
# ═══════════════════════════════════════════════════════════════════════════

KB: list[dict] = [
    {
        "id": "crm_mono", "name": "Creatine monohydrate",
        "aliases": ["creatine", "kreatin", "creatina", "créatine", "क्रिएटिन", "肌酸",
                    "creatina monoidrata", "creatina monohidrato", "creatine mono"],
        "category": "supplement",
        "tags": ["strength", "muscle_gain", "power", "beginner", "creatine", "atp", "explosive"],
        "summary": "The most extensively researched ergogenic aid. Increases phosphocreatine stores enabling faster ATP regeneration during high-intensity exercise.",
        "what_it_is": "Creatine monohydrate is an organic compound naturally produced in the liver and kidneys from arginine, glycine, and methionine. ~95% is stored in skeletal muscle as phosphocreatine, directly fuelling the ATP-PCr energy system during explosive efforts lasting up to ~10 seconds.",
        "dosage": "Loading (optional): 20 g/day split into 4×5 g doses for 5–7 days. Maintenance: 3–5 g/day. No-loading: 3–5 g/day for ~3–4 weeks to full saturation.",
        "timing": "Post-workout slightly superior per meta-analyses. Consistency matters far more than timing — any time of day works.",
        "how_to_take": "Dissolve in 200–300 ml water, juice, or protein shake. Taking with carbohydrates increases muscle uptake via insulin.",
        "hydration": "Increase fluid intake to 2.5–3.5 L/day. Creatine draws water into muscle cells — adequate hydration prevents cramps.",
        "training_synergy": "Most effective with progressive-overload resistance training. Compound lifts maximise ATP-PCr benefits. Also improves HIIT performance.",
        "cycling": "No cycling required. Long-term continuous use (5+ years) shown safe in research.",
        "benefits": ["Strength increase 5–15%", "Power output improvement", "Faster recovery between sets", "Lean mass support", "Cognitive performance support (emerging)"],
        "side_effects": [{"effect": "Water retention (mild, intracellular)", "severity": "low"}, {"effect": "GI discomfort if loading dose taken all at once", "severity": "medium"}],
        "stacking": ["Beta-alanine", "Caffeine", "Whey protein"],
        "final_recommendation": "Pair 3–5 g creatine monohydrate post-workout with carbohydrate + protein. Expect strength improvements in 2–4 weeks.",
        "evidence_tier": "very_high",
        "safe_for_beginners": True,
        "pubmed_ids": ["28615996", "11509496", "14636102"],
        "examine_url": "https://examine.com/supplements/creatine/",
        "research_refs": ["Buford et al. (2007) JISSN — ISSN Position Stand", "Lanhers et al. (2017) Eur J Sport Sci — meta-analysis"],
    },
    {
        "id": "crm_hcl", "name": "Creatine HCL",
        "aliases": ["creatine hcl", "creatine hydrochloride", "hcl creatine", "con-cret"],
        "category": "supplement",
        "tags": ["strength", "muscle_gain", "creatine", "no_bloating"],
        "summary": "Higher-solubility creatine salt. Effective at smaller doses (1–2 g). Less bloating. Smaller evidence base than monohydrate.",
        "what_it_is": "Creatine bound to hydrochloric acid. HCL salt increases water solubility, allowing effective doses at 1–2 g vs 3–5 g for monohydrate.",
        "dosage": "1–2 g/day, no loading phase needed.",
        "timing": "Pre or post-workout.", "how_to_take": "Mix in 150–200 ml water.",
        "hydration": "2–3 L/day.", "training_synergy": "Identical to monohydrate — most effective with resistance training.",
        "cycling": "No cycling needed.",
        "benefits": ["Equivalent strength gains at lower dose", "Minimal bloating", "Easy dissolution"],
        "side_effects": [{"effect": "Minimal GI issues", "severity": "low"}],
        "stacking": ["Citrulline malate", "Beta-alanine"],
        "final_recommendation": "Choose HCL only if monohydrate causes persistent GI discomfort. Monohydrate is more cost-effective for most users.",
        "evidence_tier": "high", "safe_for_beginners": True,
        "pubmed_ids": ["19844003"], "examine_url": "https://examine.com/supplements/creatine/",
        "research_refs": ["Miller et al. (2009) J Int Soc Sports Nutr"],
    },
    {
        "id": "beta_al", "name": "Beta-alanine",
        "aliases": ["beta alanine", "beta-alanine", "carnosine precursor", "beta alanina"],
        "category": "supplement",
        "tags": ["endurance", "strength", "fatigue", "pre_workout", "carnosine"],
        "summary": "Amino acid precursor to carnosine — buffers lactic acid, delaying fatigue. Most effective for 60–240 second efforts.",
        "what_it_is": "Non-essential amino acid combining with histidine to form carnosine in muscle — a pH buffer neutralising lactic acid during intense exercise. Raises muscle carnosine 40–80% over 4–6 weeks.",
        "dosage": "3.2–6.4 g/day, split into 1.6 g doses to reduce tingling.",
        "timing": "Pre-workout or split through day.", "how_to_take": "Capsules or powder. Sustained-release reduces paresthesia.",
        "hydration": "2–3 L/day.", "training_synergy": "Synergises with creatine — creatine covers explosive <10 s, beta-alanine covers 60–240 s.",
        "cycling": "No cycling. Benefits plateau after ~10 weeks — maintenance at 3.2 g/day.",
        "benefits": ["Delayed muscle fatigue", "Higher rep capacity", "Endurance improvement in 1–4 min efforts"],
        "side_effects": [{"effect": "Tingling / paresthesia — harmless", "severity": "low"}],
        "stacking": ["Creatine", "Caffeine", "L-Citrulline"],
        "final_recommendation": "Stack with creatine for full energy system coverage. Use split dosing.",
        "evidence_tier": "high", "safe_for_beginners": True,
        "pubmed_ids": ["22649228", "27797728"], "examine_url": "https://examine.com/supplements/beta-alanine/",
        "research_refs": ["Hobson et al. (2012) Amino Acids — 15-study meta-analysis"],
    },
    {
        "id": "citrulline", "name": "L-Citrulline / Citrulline malate",
        "aliases": ["citrulline", "citrulline malate", "l-citrulline", "pump supplement", "no booster", "citrulina", "nitric oxide"],
        "category": "supplement",
        "tags": ["pump", "endurance", "blood_flow", "pre_workout", "nitric_oxide", "vasodilation"],
        "summary": "Precursor to arginine → nitric oxide. Enhances blood flow, muscle pump, and endurance. Malate form reduces fatigue via Krebs cycle.",
        "what_it_is": "L-citrulline converts to arginine in kidneys, then to NO — a potent vasodilator. Citrulline malate adds malic acid (Krebs cycle intermediate) for extra anti-fatigue benefit.",
        "dosage": "L-citrulline: 6–8 g. Citrulline malate 2:1: 8 g. Pre-workout.",
        "timing": "30–60 min pre-workout, empty stomach.", "how_to_take": "Mix in 300–400 ml water.",
        "hydration": "3+ L/day.", "training_synergy": "Best for high-volume, hypertrophy, and metabolic conditioning.",
        "cycling": "No cycling needed.",
        "benefits": ["Muscle pump via vasodilation", "Reduced DOMS 24–48 h post", "Endurance +12–15%", "Blood pressure support"],
        "side_effects": [{"effect": "GI discomfort >10 g", "severity": "low"}],
        "stacking": ["Beta-alanine", "Caffeine", "Creatine"],
        "final_recommendation": "Use 8 g citrulline malate 2:1 pre-workout for pump and endurance.",
        "evidence_tier": "high", "safe_for_beginners": True,
        "pubmed_ids": ["21414438", "26900386"], "examine_url": "https://examine.com/supplements/citrulline/",
        "research_refs": ["Pérez-Guisado & Jakeman (2010) JSCR"],
    },
    {
        "id": "caffeine", "name": "Caffeine",
        "aliases": ["caffeine", "caffeina", "caféine", "koffein", "कैफीन", "咖啡因", "caffeine anhydrous", "coffee"],
        "category": "supplement",
        "tags": ["strength", "endurance", "fat_loss", "focus", "pre_workout", "energy", "thermogenic"],
        "summary": "Adenosine receptor antagonist. Reduces perceived exertion, increases power output, endurance, and fat oxidation.",
        "what_it_is": "Caffeine blocks adenosine receptors reducing perceived effort and increasing catecholamine release. Most extensively studied ergogenic — effective in 300+ clinical trials.",
        "dosage": "3–6 mg/kg bodyweight (200–400 mg for most adults).",
        "timing": "30–60 min pre-workout. Avoid within 6 h of sleep.",
        "how_to_take": "Anhydrous pills for precision. Stack with 200 mg L-Theanine (2:1) for smooth focus.",
        "hydration": "Mild diuretic — extra 500 ml/day.",
        "training_synergy": "Effective for all modalities — endurance, strength, power, team sports.",
        "cycling": "Cycle off 1–2 weeks/month. Tolerance builds within 2 weeks of daily use.",
        "benefits": ["Power output +3–7%", "Endurance improvement", "Fat oxidation", "Focus and alertness"],
        "side_effects": [{"effect": "Tolerance with daily use", "severity": "medium"}, {"effect": "Sleep disruption if late dose", "severity": "medium"}, {"effect": "Anxiety at high doses", "severity": "medium"}],
        "stacking": ["L-Theanine 200 mg", "L-Citrulline", "Beta-alanine"],
        "final_recommendation": "3–5 mg/kg bodyweight 30–60 min pre-workout. Stack with L-Theanine. Cycle monthly.",
        "evidence_tier": "very_high", "safe_for_beginners": True,
        "pubmed_ids": ["34445894", "20019636"], "examine_url": "https://examine.com/supplements/caffeine/",
        "research_refs": ["Grgic et al. (2021) BJSM — 300-study meta-analysis"],
    },
    {
        "id": "whey", "name": "Whey protein",
        "aliases": ["whey", "whey protein", "proteina whey", "proteine whey", "proteína whey",
                    "व्हे प्रोटीन", "乳清蛋白", "protéine lactosérum", "molkenprotein", "protein powder"],
        "category": "supplement",
        "tags": ["muscle_gain", "recovery", "protein", "beginner", "leucine", "mps"],
        "summary": "Fast-digesting milk protein with highest leucine content — optimal for post-workout muscle protein synthesis.",
        "what_it_is": "Whey is the liquid by-product of cheese production, filtered into concentrate (70–80% protein), isolate (90%+, <1% lactose), or hydrolysate. Richest leucine source (10–11%) — primary trigger for muscle protein synthesis.",
        "dosage": "25–50 g/serving to reach 1.6–2.2 g/kg/day total protein.",
        "timing": "Post-workout or any time to supplement dietary protein deficit.",
        "how_to_take": "Shaker + 200–300 ml water or milk. Isolate for lactose intolerance.",
        "hydration": "2.5–3 L/day — protein metabolism increases urea production.",
        "training_synergy": "Consume within 2 h post-resistance training. Combine with fast carbs for insulin-mediated uptake.",
        "cycling": "No cycling. Use daily to hit protein targets.",
        "benefits": ["Maximises MPS via leucine", "Fast digestion post-workout", "Complete amino acid profile", "Cost-effective"],
        "side_effects": [{"effect": "GI discomfort if lactose intolerant — use isolate", "severity": "medium"}],
        "stacking": ["Creatine", "Fast carbs post-workout", "Casein before bed"],
        "final_recommendation": "Hit total daily protein target first. Post-workout whey + fast carbs optimises MPS and glycogen repletion.",
        "evidence_tier": "very_high", "safe_for_beginners": True,
        "pubmed_ids": ["19589961", "25048790"], "examine_url": "https://examine.com/supplements/whey-protein/",
        "research_refs": ["Tang et al. (2009) Am J Clin Nutr", "Morton et al. (2018) BJSM meta-analysis"],
    },
    {
        "id": "preworkout", "name": "Pre-workout supplements",
        "aliases": ["pre workout", "pre-workout", "preworkout", "pre workout supplement",
                    "pump pre workout", "stim pre workout", "non stim pre workout"],
        "category": "supplement",
        "tags": ["pre_workout", "energy", "pump", "strength", "endurance", "focus", "nitric_oxide"],
        "summary": "Multi-ingredient formulas combining caffeine, citrulline, beta-alanine, and creatine for energy, pump, and performance.",
        "what_it_is": "Pre-workout formulas typically combine: caffeine (energy/focus), L-citrulline (pump/endurance), beta-alanine (fatigue delay), and creatine (strength/power). Quality varies enormously — always verify doses against research-backed amounts on the label.",
        "dosage": "As labelled. Check: Citrulline 6–8 g, Caffeine 150–300 mg, Beta-alanine 3.2 g, Creatine 3–5 g.",
        "timing": "20–45 min before training.",
        "how_to_take": "Mix in 300–400 ml cold water. Start with half dose to assess tolerance.",
        "hydration": "3+ L/day. Stimulants increase sweating and fluid needs.",
        "training_synergy": "Best for compound strength sessions and high-volume hypertrophy. Avoid for easy recovery days — save tolerance.",
        "cycling": "Cycle 4–6 weeks on, 1–2 weeks off. Stimulant tolerance builds quickly.",
        "benefits": ["Energy and mental focus", "Muscle pump", "Endurance improvement", "Strength output"],
        "side_effects": [{"effect": "Jitteriness / anxiety (stimulant sensitivity)", "severity": "medium"}, {"effect": "Crash post-workout", "severity": "low"}, {"effect": "Tolerance buildup", "severity": "medium"}],
        "stacking": ["Extra creatine if underdosed in formula", "Electrolytes"],
        "final_recommendation": "Choose formulas with transparent dosing. Verify each ingredient vs research doses. Non-stim option available for evening training.",
        "evidence_tier": "high", "safe_for_beginners": True,
        "pubmed_ids": ["22080314", "23439702"], "examine_url": "https://examine.com/supplements/",
        "research_refs": ["Jagim et al. (2016) J Int Soc Sports Nutr — multi-ingredient review"],
    },
    {
        "id": "bcaa", "name": "BCAAs (Branched Chain Amino Acids)",
        "aliases": ["bcaa", "bcaas", "branched chain amino acids", "amino acids", "bcaa supplement",
                    "leucine isoleucine valine", "eaa"],
        "category": "supplement",
        "tags": ["muscle_gain", "recovery", "protein", "anti_catabolic", "amino"],
        "summary": "Leucine, isoleucine, valine blend. Useful for fasted training; largely redundant if total protein intake is adequate.",
        "what_it_is": "Three essential amino acids — leucine, isoleucine, valine — that are directly metabolised in muscle. Leucine is the primary MPS trigger. EAAs (essential amino acids) are superior to BCAAs alone.",
        "dosage": "5–10 g per dose if using. EAAs (10–15 g) preferred.",
        "timing": "Intra-workout or peri-workout, especially during fasted training.",
        "how_to_take": "Mix in water. Available in flavoured powder or capsules.",
        "hydration": "2.5–3 L/day.",
        "training_synergy": "Most useful during fasted morning training. Less effective if post-workout whey is consumed.",
        "cycling": "No cycling needed.",
        "benefits": ["Anti-catabolic during fasted training", "Leucine-mediated MPS", "Reduces DOMS"],
        "side_effects": [{"effect": "Largely redundant if protein targets are met from diet", "severity": "low"}],
        "stacking": ["Whey protein (superior alternative)", "Creatine"],
        "final_recommendation": "Prioritise whole protein sources and whey. BCAAs are useful only during fasted training or when dietary protein is insufficient.",
        "evidence_tier": "moderate", "safe_for_beginners": True,
        "pubmed_ids": ["17440567"], "examine_url": "https://examine.com/supplements/branched-chain-amino-acids/",
        "research_refs": ["Wolfe (2017) J Int Soc Sports Nutr — BCAA review"],
    },
    {
        "id": "ostarine", "name": "Ostarine (MK-2866)",
        "aliases": ["ostarine", "mk2866", "mk-2866", "enobosarm", "mk 2866", "ostarina"],
        "category": "sarm",
        "tags": ["muscle_gain", "fat_loss", "recomp", "sarm", "selective_androgen"],
        "summary": "Mildest SARM. Selective androgen receptor modulator with anabolic effects on muscle/bone. Research chemical — not approved.",
        "what_it_is": "Nonsteroidal SARM developed by GTx for muscle-wasting diseases. Selectively binds androgen receptors in muscle and bone with minimal reproductive tissue activation.",
        "dosage": "10–25 mg/day. Start at 10 mg first cycle.",
        "timing": "Once daily, same time, with or without food.",
        "how_to_take": "Oral liquid or capsule. Precise dosing syringe for liquids.",
        "hydration": "Standard 2.5–3 L/day.",
        "training_synergy": "Excellent for recomposition — muscle gain + fat loss simultaneously.",
        "cycling": "8-week cycles. Bloodwork before and 4–6 weeks post-cycle. PCT if needed.",
        "benefits": ["Lean muscle gain 2–4 kg in 8 weeks", "Fat loss support", "Joint support", "Lower suppression than steroids"],
        "side_effects": [{"effect": "Mild testosterone suppression", "severity": "medium"}, {"effect": "Lipid changes (HDL reduction)", "severity": "medium"}],
        "stacking": ["Cardarine GW-501516", "MK-677 Ibutamoren"],
        "final_recommendation": "Bloodwork baseline mandatory. Start 10 mg, run 8 weeks, recheck. Do not use without monitoring.",
        "evidence_tier": "moderate", "safe_for_beginners": True,
        "pubmed_ids": ["20814882", "23631853"], "examine_url": "https://examine.com/supplements/ostarine/",
        "research_refs": ["Dalton et al. (2011) Cancer Res"],
        "legal_status": "Research chemical — not approved for human use. Banned by WADA.",
    },
    {
        "id": "lgd4033", "name": "LGD-4033 (Ligandrol)",
        "aliases": ["lgd4033", "lgd-4033", "ligandrol", "vk5211", "lgd 4033"],
        "category": "sarm",
        "tags": ["muscle_gain", "strength", "bulking", "sarm"],
        "summary": "Most anabolic SARM. Significant lean mass and strength gains. Requires full PCT. Not for beginners.",
        "what_it_is": "Nonsteroidal SARM with high anabolic:androgenic ratio. More potent than Ostarine — approaches low-dose testosterone for mass gains.",
        "dosage": "5–10 mg/day for 8–12 weeks.",
        "timing": "Once daily.", "how_to_take": "Oral liquid or capsule.",
        "hydration": "2.5–3 L/day.", "training_synergy": "Best with progressive overload and calorie surplus.",
        "cycling": "8–12 weeks. Full PCT mandatory — Nolvadex 40/40/20/20 mg or Clomid 50/25/25.",
        "benefits": ["Significant lean mass gains", "Major strength increase", "Improved recovery"],
        "side_effects": [{"effect": "Significant testosterone suppression", "severity": "high"}, {"effect": "HDL reduction", "severity": "high"}],
        "stacking": ["MK-677", "Cardarine"],
        "final_recommendation": "Bloodwork mandatory. Not appropriate for first-time users — run Ostarine first.",
        "evidence_tier": "moderate", "safe_for_beginners": False,
        "pubmed_ids": ["23631853"], "examine_url": "https://examine.com/supplements/lgd-4033/",
        "research_refs": ["Basaria et al. (2013) Lancet — Phase I trial"],
        "legal_status": "Research chemical — not approved. Banned by WADA.",
    },
    {
        "id": "test_e", "name": "Testosterone enanthate",
        "aliases": ["testosterone enanthate", "test e", "testo e", "testosterone", "testosteron", "testosterona"],
        "category": "steroid",
        "tags": ["muscle_gain", "strength", "bulking", "testosterone", "steroid", "anabolic"],
        "summary": "Gold standard anabolic injectable. Long-ester testosterone with predictable pharmacokinetics and decades of clinical data.",
        "what_it_is": "Synthetic testosterone bound to enanthate ester, slowing release for stable blood levels with twice-weekly injections. Primary anabolic hormone — saturates androgen receptors in muscle, bone, and CNS.",
        "dosage": "Beginner: 300–500 mg/week (E3.5D). Intermediate: 500–750 mg/week.",
        "timing": "Injected subcutaneous or intramuscular every 3.5 days.",
        "how_to_take": "IM (glute, quads, delts) or SubQ. Rotate sites. 23–25G inject, 18–21G draw.",
        "hydration": "2.5–3 L/day. Monitor blood pressure.",
        "training_synergy": "Maximum output needs progressive overload, 2–2.4 g/kg protein, calorie surplus, sleep.",
        "cycling": "12–16 week cycles. AI (Anastrozole 0.25–0.5 mg E3D) required. PCT 2 weeks after last pin.",
        "benefits": ["Significant lean mass + strength", "Improved recovery", "Libido and well-being", "Predictable pharmacokinetics"],
        "side_effects": [{"effect": "Complete endogenous testosterone suppression", "severity": "high"}, {"effect": "Aromatisation — AI required", "severity": "medium"}, {"effect": "Cardiovascular strain (HDL reduction)", "severity": "high"}, {"effect": "Testicular atrophy during cycle", "severity": "high"}],
        "stacking": ["Anastrozole (AI mandatory)", "NPP or Deca (intermediate)", "Anavar (cut)"],
        "final_recommendation": "Bloodwork mandatory before, mid-cycle, post-PCT. AI + liver support + cardiovascular monitoring non-negotiable.",
        "evidence_tier": "very_high", "safe_for_beginners": False,
        "pubmed_ids": ["8637536", "11502560"], "examine_url": None,
        "research_refs": ["Bhasin et al. (1996) NEJM — landmark dose-response"],
        "legal_status": "Schedule III (USA). Prescription only in UK, India, Canada, Australia.",
    },
    {
        "id": "bpc157", "name": "BPC-157",
        "aliases": ["bpc157", "bpc-157", "body protection compound", "bpc 157", "pentadecapeptide"],
        "category": "peptide",
        "tags": ["recovery", "injury", "joint_health", "gut", "healing", "peptide", "tendon"],
        "summary": "15-amino acid peptide from gastric juice. Potent tendon, ligament, muscle, and gut healing properties.",
        "what_it_is": "Synthetic 15-amino acid sequence from human gastric juice. Animal research shows accelerated healing via growth hormone receptor upregulation and angiogenesis.",
        "dosage": "250–500 mcg/day subcutaneous or intramuscular.",
        "timing": "Near injury site or systemic (abdomen). Once or twice daily.",
        "how_to_take": "Reconstitute with bacteriostatic water. Insulin syringe 29–31G. Refrigerate 30-day maximum.",
        "hydration": "Standard 2.5–3 L/day.",
        "training_synergy": "Active rehabilitation during protocol maximises outcomes.",
        "cycling": "Acute injury: 4–6 weeks. Chronic: 8–12 weeks.",
        "benefits": ["Accelerated tendon/ligament healing", "Gut lining repair", "Anti-inflammatory", "Angiogenesis"],
        "side_effects": [{"effect": "Injection site irritation (mild)", "severity": "low"}],
        "stacking": ["TB-500", "Ipamorelin/CJC-1295"],
        "final_recommendation": "Source quality critical. Sterility non-negotiable. Not a substitute for physiotherapy.",
        "evidence_tier": "moderate", "safe_for_beginners": True,
        "pubmed_ids": ["23439702"], "examine_url": "https://examine.com/supplements/bpc-157/",
        "research_refs": ["Sikiric et al. (2013) Curr Pharm Des"],
        "legal_status": "Research chemical — not approved for human use.",
    },
    {
        "id": "hgh", "name": "Human Growth Hormone (HGH)",
        "aliases": ["hgh", "human growth hormone", "growth hormone", "gh", "somatropin", "rhgh", "生长激素", "hormona de crecimiento"],
        "category": "peptide",
        "tags": ["fat_loss", "muscle_gain", "recovery", "anti_aging", "hgh", "growth_hormone", "igf1"],
        "summary": "Recombinant somatropin. Potent lipolytic + anabolic. Prescription only. Reduces visceral fat, supports lean mass.",
        "what_it_is": "191-amino acid protein identical to endogenous GH. Stimulates liver IGF-1 production (anabolic) and drives lipolysis (fat breakdown). Age-related GH decline drives anti-aging interest.",
        "dosage": "Fat loss/anti-aging: 1–3 IU/day. Bodybuilding: 4–8 IU/day (significantly higher risk).",
        "timing": "Sub-Q injection on waking (fat loss) or before bed (GH pulse alignment).",
        "how_to_take": "Sub-Q abdominal injection, rotate sites. Reconstitute with bacteriostatic water. Refrigerate 2–8°C.",
        "hydration": "3+ L/day. Water retention common first 4–6 weeks.",
        "training_synergy": "Resistance training synergises with GH. Fasted morning cardio amplifies fat loss.",
        "cycling": "16–24 week cycles. Monitor IGF-1 levels quarterly.",
        "benefits": ["Significant visceral fat reduction", "Lean mass retention", "Connective tissue strengthening", "Improved sleep"],
        "side_effects": [{"effect": "Carpal tunnel syndrome", "severity": "medium"}, {"effect": "Insulin resistance", "severity": "high"}, {"effect": "Acromegaly risk at high sustained doses", "severity": "high"}],
        "stacking": ["Testosterone (synergistic)", "T3 (advanced)", "Insulin (extreme danger)"],
        "final_recommendation": "Physician supervision mandatory. Monitor IGF-1, fasting glucose, HbA1c quarterly. Pharmaceutical grade only.",
        "evidence_tier": "very_high", "safe_for_beginners": False,
        "pubmed_ids": ["2388534", "7476061"], "examine_url": None,
        "research_refs": ["Rudman et al. (1990) NEJM — landmark study"],
        "legal_status": "Prescription only in all countries. Banned by WADA.",
    },
    {
        "id": "vitamin_d", "name": "Vitamin D3 + K2",
        "aliases": ["vitamin d", "vitamin d3", "cholecalciferol", "vit d", "vitamina d", "vitamine d", "विटामिन डी"],
        "category": "supplement",
        "tags": ["health", "testosterone", "immune", "bone", "recovery", "foundation", "hormonal"],
        "summary": "Essential fat-soluble vitamin-hormone. Deficiency affects 40%+ globally. Regulates testosterone, immune function, bone density.",
        "what_it_is": "D3 (cholecalciferol) is a prohormone regulating 1,000+ genes including testosterone synthesis. K2 MK-7 directs calcium to bone and away from arteries.",
        "dosage": "D3: 2,000–5,000 IU/day. K2 MK-7: 100–200 mcg/day. Test 25-OH-D to calibrate.",
        "timing": "With largest fat-containing meal.",
        "how_to_take": "Softgel or drops. D3 + K2 together.", "hydration": "Standard 2.5–3 L/day.",
        "training_synergy": "Adequate D3 supports testosterone (+20% in deficient men), muscle contraction, and bone density.",
        "cycling": "Year-round — dietary and sunlight sources rarely suffice in training populations.",
        "benefits": ["Testosterone support", "Immune function", "Bone density", "Mood improvement"],
        "side_effects": [{"effect": "Toxicity only at >10,000 IU/day sustained without monitoring", "severity": "low"}],
        "stacking": ["Magnesium (D3 activation)", "Omega-3"],
        "final_recommendation": "Test serum 25-OH-D. Target 40–70 ng/mL. Take D3 + K2 MK-7 daily with fat.",
        "evidence_tier": "very_high", "safe_for_beginners": True,
        "pubmed_ids": ["21154195", "17556697"], "examine_url": "https://examine.com/supplements/vitamin-d/",
        "research_refs": ["Pilz et al. (2011) Horm Metab Res", "Holick (2007) NEJM review"],
    },
    {
        "id": "omega3", "name": "Omega-3 / Fish oil (EPA + DHA)",
        "aliases": ["omega 3", "fish oil", "omega-3", "epa dha", "fish oil supplement", "omega3"],
        "category": "supplement",
        "tags": ["health", "recovery", "anti_inflammatory", "cardiovascular", "joint_health", "foundation"],
        "summary": "EPA + DHA omega-3 fatty acids. Anti-inflammatory, cardiovascular support, joint health, and modest MPS benefits.",
        "what_it_is": "Long-chain polyunsaturated fatty acids EPA (eicosapentaenoic acid) and DHA (docosahexaenoic acid). Anti-inflammatory via resolvin/protectin pathways. Critically important for steroid users with elevated cardiovascular risk.",
        "dosage": "2–4 g combined EPA + DHA/day (check label — NOT total fish oil volume).",
        "timing": "With meals to prevent aftertaste.",
        "how_to_take": "Softgels or liquid. Enteric-coated for reduced burping.",
        "hydration": "Standard 2.5–3 L/day.",
        "training_synergy": "Reduces DOMS and exercise-induced inflammation. Improves recovery between sessions.",
        "cycling": "Year-round supplementation.",
        "benefits": ["Anti-inflammatory", "Cardiovascular protection", "Joint health", "Modest MPS support"],
        "side_effects": [{"effect": "Fish aftertaste — enteric-coated prevents this", "severity": "low"}],
        "stacking": ["Vitamin D3/K2", "Curcumin (anti-inflammatory synergy)"],
        "final_recommendation": "Look for 2–4 g EPA+DHA combined daily. Molecularly distilled for purity. Critical for anyone using anabolic compounds.",
        "evidence_tier": "very_high", "safe_for_beginners": True,
        "pubmed_ids": ["21610101"], "examine_url": "https://examine.com/supplements/fish-oil/",
        "research_refs": ["Smith et al. (2011) JCEM", "Calder (2013) Am J Clin Nutr"],
    },
]

# ── Alias index ────────────────────────────────────────────────────────────
_ALIAS: dict[str, dict] = {}
for _it in KB:
    _ALIAS[_it["name"].lower()] = _it
    for _a in _it.get("aliases", []):
        _ALIAS[_a.lower()] = _it


# ═══════════════════════════════════════════════════════════════════════════
# PRODUCT KNOWLEDGE BASE  — for product_intent queries
# ═══════════════════════════════════════════════════════════════════════════

PRODUCTS: list[dict] = [
    {
        "query_match": ["pre workout india", "best pre workout india", "pre workout supplement india"],
        "intent": "product",
        "category": "pre_workout",
        "goal": ["strength", "endurance", "muscle_gain"],
        "products": [
            {"name": "MuscleBlaze Pre Workout XXL", "brand": "MuscleBlaze", "price": "₹999–₹1,499", "rating": 4.3,
             "badge": "🔥 Most Popular India", "key_benefit": "High caffeine (200 mg) + Citrulline 3 g. Affordable entry-level option.",
             "servings": 30, "tip": "Start with half scoop to assess caffeine tolerance.", "region": "India"},
            {"name": "GNC AMP Gold Series Pre-Workout", "brand": "GNC", "price": "₹2,999–₹3,499", "rating": 4.5,
             "badge": "💪 Balanced Formula", "key_benefit": "Transparent dosing — 6 g Citrulline, 3.2 g Beta-alanine, 200 mg Caffeine.",
             "servings": 30, "tip": "Best dose-per-gram ratio in mid-range.", "region": "India"},
            {"name": "Optimum Nutrition Gold Standard Pre-Workout", "brand": "ON", "price": "₹2,499–₹2,999", "rating": 4.4,
             "badge": "🏅 Premium Brand", "key_benefit": "Globally trusted brand. Creatine + Caffeine + Beta-alanine combination.",
             "servings": 30, "tip": "Add extra 3–5 g creatine for full research-backed dose.", "region": "India"},
        ],
        "warning": "Always verify third-party testing. Stimulant pre-workouts not suitable for caffeine-sensitive individuals."
    },
    {
        "query_match": ["best whey protein india", "whey protein india", "protein powder india", "top protein india"],
        "intent": "product",
        "category": "protein",
        "goal": ["muscle_gain", "recovery"],
        "products": [
            {"name": "MuscleBlaze Raw Whey Protein", "brand": "MuscleBlaze", "price": "₹1,499–₹2,299", "rating": 4.4,
             "badge": "🔥 Best Value India", "key_benefit": "100% whey concentrate. 24 g protein/serving. No fillers. Most cost-effective option.",
             "servings": 33, "tip": "Stack with creatine 5 g post-workout for maximum effect.", "region": "India"},
            {"name": "Optimum Nutrition Gold Standard Whey", "brand": "ON", "price": "₹3,499–₹4,999", "rating": 4.7,
             "badge": "🏅 Gold Standard", "key_benefit": "Blend of whey isolate + concentrate. 24 g protein, 5.5 g BCAAs. Global benchmark.",
             "servings": 74, "tip": "Best for lactose-sensitive users (some isolate content).", "region": "India"},
            {"name": "Dymatize ISO 100 Whey Isolate", "brand": "Dymatize", "price": "₹4,999–₹5,999", "rating": 4.6,
             "badge": "💪 Pure Isolate", "key_benefit": "Hydrolysed whey isolate. 25 g protein, <1 g sugar, <1 g lactose. Fastest absorption.",
             "servings": 71, "tip": "Ideal post-workout for lean bulking or cutting phases.", "region": "India"},
        ],
        "warning": "Check for Labdoor / FSSAI certification. Avoid products without transparent amino acid profiles."
    },
    {
        "query_match": ["best creatine india", "creatine supplement india", "creatine monohydrate india"],
        "intent": "product",
        "category": "creatine",
        "goal": ["strength", "muscle_gain"],
        "products": [
            {"name": "MuscleBlaze Creapure Creatine", "brand": "MuscleBlaze", "price": "₹549–₹799", "rating": 4.5,
             "badge": "🔥 Creapure Certified", "key_benefit": "Creapure® monohydrate — gold standard purity from Germany. Most affordable Creapure in India.",
             "servings": 100, "tip": "3–5 g post-workout daily. No loading needed.", "region": "India"},
            {"name": "Optimum Nutrition Micronised Creatine", "brand": "ON", "price": "₹999–₹1,499", "rating": 4.6,
             "badge": "🏅 Globally Trusted", "key_benefit": "Micronised monohydrate mixes easily. Unflavoured. Global brand trust.",
             "servings": 114, "tip": "Mix with post-workout shake for convenience.", "region": "India"},
            {"name": "AS-IT-IS Creatine Monohydrate", "brand": "AS-IT-IS", "price": "₹449–₹649", "rating": 4.4,
             "badge": "💰 Budget Pick", "key_benefit": "Single-ingredient creatine monohydrate. No additives. Excellent value for money.",
             "servings": 100, "tip": "Best budget choice. Same molecule as premium brands.", "region": "India"},
        ],
        "warning": "Avoid creatine blends with proprietary matrices — always choose pure monohydrate."
    },
    {
        "query_match": ["best pre workout", "best pre workout supplement", "top pre workout"],
        "intent": "product",
        "category": "pre_workout",
        "goal": ["strength", "endurance", "muscle_gain"],
        "products": [
            {"name": "Transparent Labs BULK Pre-Workout", "brand": "Transparent Labs", "price": "$49–$54", "rating": 4.7,
             "badge": "🏅 Best Overall", "key_benefit": "8 g Citrulline, 4 g Beta-alanine, 200 mg Caffeine, 4 g BCAAs. Fully transparent dosing.",
             "servings": 30, "tip": "Best research-backed formula — all ingredients at effective doses.", "region": "Global"},
            {"name": "Legion Pulse Pre-Workout", "brand": "Legion Athletics", "price": "$44–$49", "rating": 4.6,
             "badge": "💪 Science-Backed", "key_benefit": "8 g Citrulline, 3.6 g Beta-alanine, 350 mg Caffeine. No proprietary blends.",
             "servings": 20, "tip": "High caffeine — not for sensitive users. Effective for experienced athletes.", "region": "Global"},
            {"name": "C4 Original Pre-Workout", "brand": "Cellucor", "price": "$29–$39", "rating": 4.3,
             "badge": "🔥 Most Popular", "key_benefit": "Widely available, affordable entry point. Note: citrulline dose is low (1 g).",
             "servings": 30, "tip": "Add 6 g citrulline separately to maximise pump. Good starter option.", "region": "Global"},
        ],
        "warning": "Proprietary blends hide under-dosed ingredients. Always choose transparent label formulas."
    },
    {
        "query_match": ["best whey protein", "best protein powder", "top whey protein", "best protein supplement"],
        "intent": "product",
        "category": "protein",
        "goal": ["muscle_gain", "recovery"],
        "products": [
            {"name": "Optimum Nutrition Gold Standard 100% Whey", "brand": "Optimum Nutrition", "price": "$35–$55", "rating": 4.7,
             "badge": "🏅 Industry Standard", "key_benefit": "24 g protein, 5.5 g BCAAs, 4 g glutamine. The global benchmark for 20+ years.",
             "servings": 74, "tip": "Double chocolate or vanilla ice cream are the best-tasting flavours.", "region": "Global"},
            {"name": "Dymatize ISO 100 Hydrolysed Whey Isolate", "brand": "Dymatize", "price": "$42–$58", "rating": 4.6,
             "badge": "💪 Fastest Absorbing", "key_benefit": "Hydrolysed isolate: 25 g protein, <1 g sugar, <0.5 g fat. Fastest MPS trigger.",
             "servings": 71, "tip": "Best for post-workout when fast absorption is priority.", "region": "Global"},
            {"name": "MyProtein Impact Whey Protein", "brand": "MyProtein", "price": "$25–$40", "rating": 4.4,
             "badge": "💰 Best Value", "key_benefit": "21 g protein/serving. 100+ flavour options. Excellent cost per gram of protein.",
             "servings": 100, "tip": "Stock up during sales — massive discount events several times a year.", "region": "Global"},
        ],
        "warning": "Third-party testing (Informed Sport / NSF) is important. Avoid products with amino spiking."
    },
]

# Product search index
_PRODUCT_IDX: list[tuple[str, dict]] = []
for _p in PRODUCTS:
    for _q in _p.get("query_match", []):
        _PRODUCT_IDX.append((_q.lower(), _p))


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
            intent      TEXT DEFAULT 'research',
            created_at  REAL NOT NULL
        )""")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_created ON report_cache(created_at)")

_init_cache()


def _cache_key(query: str, filters: list, intent: str = "research") -> str:
    # FIX: include intent and sorted filters — filter changes produce different keys
    raw = json.dumps({"q": query.lower().strip(), "f": sorted(filters), "i": intent}, sort_keys=True)
    return hashlib.sha256(raw.encode()).hexdigest()[:32]


def _cache_get(key: str, ttl: int = CACHE_TTL_SEC) -> list | None:
    try:
        with _cache_lock, sqlite3.connect(CACHE_DB) as conn:
            row = conn.execute(
                "SELECT report_json, created_at FROM report_cache WHERE cache_key=?", (key,)
            ).fetchone()
        if not row:
            return None
        if time.time() - row[1] > ttl:
            return None
        return json.loads(row[0])
    except Exception as e:
        print(f"[Cache GET] {e}")
        return None


def _cache_set(key: str, query: str, results: list, source: str = "ai", intent: str = "research") -> None:
    try:
        with _cache_lock, sqlite3.connect(CACHE_DB) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO report_cache(cache_key,query,report_json,source,intent,created_at) VALUES (?,?,?,?,?,?)",
                (key, query, json.dumps(results), source, intent, time.time())
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
# INTENT CLASSIFICATION  — three paths
# ═══════════════════════════════════════════════════════════════════════════

# Product query signals
_PRODUCT_SIGNALS = [
    "best pre workout", "best whey", "best creatine", "best protein",
    "top supplement", "which supplement", "recommend supplement",
    "good pre workout", "good protein", "good creatine",
    "india", "usa", "uk", "in india", "in usa", "to buy", "price",
    "brand", "buy online", "amazon", "flipkart", "rating",
    "best supplement for", "best bcaa", "best amino",
]

# Training / diet signals
_TRAINING_SIGNALS = [
    "workout plan", "training split", "hypertrophy", "powerlifting",
    "diet plan", "meal plan", "high protein diet", "keto", "calorie",
    "macro", "bulking diet", "cutting diet", "fat loss diet",
    "muscle building diet", "training program", "exercise plan",
    "testosterone levels", "lab results", "blood test",
]

def classify_intent(query: str) -> str:
    """
    Classify query into one of three intents:
      research_intent  — evidence report (dosage, mechanism, risks)
      product_intent   — product recommendation list
      training_intent  — diet plan, workout, health interpretation
    """
    q = query.lower()
    if any(sig in q for sig in _PRODUCT_SIGNALS):
        return "product_intent"
    if any(sig in q for sig in _TRAINING_SIGNALS):
        return "training_intent"
    return "research_intent"


# ═══════════════════════════════════════════════════════════════════════════
# ENTITY DETECTION  (fixed — no tag leak)
# ═══════════════════════════════════════════════════════════════════════════

def _detect_entities(query: str) -> tuple[list[str], dict[str, list[str]], str]:
    """
    Returns (compound_names, per_compound_tags, intent_label).

    FIX: tags are now returned PER COMPOUND, not as a single merged pool.
    This prevents tag-bleeding where creatine's 'muscle_gain' tag boosts
    Whey protein and Testosterone in a creatine-specific query.
    """
    q = query.lower()
    compounds: list[str]           = []
    per_compound_tags: dict[str, list[str]] = {}  # FIX: keyed by compound name

    # 1. Direct alias matching
    for alias, item in _ALIAS.items():
        if alias in q:
            cname = item["name"]
            if cname not in compounds:
                compounds.append(cname)
                per_compound_tags[cname] = list(item.get("tags", []))
            else:
                # Merge tags for same compound matched via different aliases
                for t in item.get("tags", []):
                    if t not in per_compound_tags[cname]:
                        per_compound_tags[cname].append(t)

    # 2. Word-level fuzzy matching
    for word in re.split(r"[\s\W]+", q):
        if len(word) < 3:
            continue
        for alias, item in _ALIAS.items():
            if word in alias:
                cname = item["name"]
                if cname not in compounds:
                    compounds.append(cname)
                    per_compound_tags[cname] = list(item.get("tags", []))

    # 3. Intent label (separate from compound tags)
    intent = "general"
    if any(w in q for w in ["dosage", "dose", "how much", "mg", "grams", "amount"]):
        intent = "dosage"
    elif any(w in q for w in ["side effect", "risk", "dangerous", "safe", "harm", "adverse"]):
        intent = "side_effects"
    elif any(w in q for w in ["compare", "vs", "versus", "better", "difference", "vs."]):
        intent = "compare"
    elif any(w in q for w in ["cycle", "protocol", "pct", "stack", "stacking"]):
        intent = "cycle"
    elif any(w in q for w in ["what is", "what are", "how does", "explain", "define", "kya hai", "kya hota"]):
        intent = "explain"
    elif any(w in q for w in ["best", "recommend", "should i", "which", "top"]):
        intent = "recommend"

    return list(dict.fromkeys(compounds)), per_compound_tags, intent


# ── Goal filter tags (from UI pills — not compound-derived)
_FILTER_TAG_MAP = {
    "muscle_gain": ["muscle_gain", "recovery", "protein", "bulking"],
    "fat_loss":    ["fat_loss", "thermogenic", "cutting", "endurance"],
    "strength":    ["strength", "power", "creatine", "atp"],
    "endurance":   ["endurance", "pre_workout", "cardio", "pump"],
    "beginner":    [],  # handled via safe_for_beginners flag
    "advanced":    [],
}


# ═══════════════════════════════════════════════════════════════════════════
# SCORING  (fixed — compound gate + tag isolation)
# ═══════════════════════════════════════════════════════════════════════════

def _score_item(
    query: str,
    compounds: list[str],
    per_compound_tags: dict[str, list[str]],
    filters: list[str],
    item: dict,
) -> int:
    """
    Fixed scoring function.

    KEY FIX: Tags from detected compounds only boost the item that OWNS
    those compounds. An item that doesn't share the primary compound only
    gets a small boost from goal filters — and only if explicitly requested.
    """
    q        = query.lower()
    s        = 0
    name     = item["name"].lower()
    aliases  = " ".join(item.get("aliases", []))
    item_tags = set(item.get("tags", []))

    # ── 1. COMPOUND MATCH (very high weight) ──────────────────────────────
    compound_matched = False
    for c in compounds:
        if c.lower() in name or name in c.lower():
            s += 40           # Strong direct compound match
            compound_matched = True
        elif any(alias in name or name in alias for alias in _ALIAS if _ALIAS[alias] == item):
            s += 30
            compound_matched = True

    # ── 2. QUERY WORD MATCH (independent of compound) ────────────────────
    for word in re.split(r"[\s\W]+", q):
        if len(word) < 3:
            continue
        if word in name:    s += 8
        if word in aliases: s += 5

    # ── 3. TAG BOOST — ONLY FROM MATCHED COMPOUND'S TAGS ─────────────────
    # FIX: Only use tags from the compound that actually appears in the query.
    # Do NOT add tags from one compound to boost a different compound's item.
    if compound_matched:
        for c in compounds:
            if c.lower() in name or name in c.lower():
                # Tags from THIS compound applied to THIS item — correct
                for t in per_compound_tags.get(c, []):
                    if t in item_tags:
                        s += 3
    else:
        # Item is NOT the queried compound.
        # Only minor boost if explicitly in query text via summary word match
        summary = item.get("summary", "").lower()
        for word in re.split(r"[\s\W]+", q):
            if len(word) > 4 and word in summary:
                s += 1

    # ── 4. FILTER BOOST (from UI pills) ──────────────────────────────────
    # FIX: Filter boosts are small and independent of compound context.
    # A muscle_gain filter should show muscle_gain items, but only if they
    # already have a decent base score. Lone filter boost cannot propel an
    # unrelated item above the threshold.
    for f in filters:
        if f == "beginner" and item.get("safe_for_beginners"):
            s += 5
        elif f == "advanced" and not item.get("safe_for_beginners"):
            s += 5
        elif f in _FILTER_TAG_MAP:
            for ft in _FILTER_TAG_MAP[f]:
                if ft in item_tags:
                    s += 2   # Small boost, not enough alone to pass threshold

    return s


def _kb_results(
    query: str,
    compounds: list[str],
    per_compound_tags: dict[str, list[str]],
    filters: list[str],
    max_results: int = 4,
) -> list[dict]:
    """
    Score KB items and return top matches.
    FIX: Items must score >= MIN_SCORE to appear (prevents irrelevant results).
    FIX: When specific compounds are detected, non-matching items are capped.
    """
    scored = []
    for item in KB:
        sc = _score_item(query, compounds, per_compound_tags, filters, item)

        # FIX: COMPOUND GATE
        # If the query contains specific compounds AND this item is not one of them,
        # cap its score heavily. A 'creatine' query cannot surface 'Whey protein'.
        if compounds:
            item_name = item["name"].lower()
            is_matched_compound = any(
                c.lower() in item_name or item_name in c.lower()
                for c in compounds
            )
            if not is_matched_compound:
                # Non-matched compound items are capped at 15 (below MIN_SCORE)
                sc = min(sc, 14)

        scored.append({**item, "_sc": sc})

    # FIX: Apply minimum score threshold
    scored = [r for r in scored if r["_sc"] >= MIN_SCORE]
    scored.sort(key=lambda x: x["_sc"], reverse=True)
    return [{k: v for k, v in r.items() if k != "_sc"} for r in scored[:max_results]]


# ═══════════════════════════════════════════════════════════════════════════
# PRODUCT SEARCH
# ═══════════════════════════════════════════════════════════════════════════

def _search_products(query: str, filters: list[str]) -> list[dict] | None:
    """
    Search the product knowledge base.
    Returns product card list or None if no match.
    """
    q = query.lower()

    # Find best matching product group
    best_match = None
    best_score = 0
    for trigger, pgroup in _PRODUCT_IDX:
        score = 0
        # Exact trigger match
        if trigger in q:
            score += len(trigger.split()) * 10
        else:
            # Word-level partial match
            for word in trigger.split():
                if word in q and len(word) > 3:
                    score += 3

        # Filter alignment
        for f in filters:
            if f in pgroup.get("goal", []):
                score += 5

        if score > best_score:
            best_score = score
            best_match = pgroup

    if not best_match or best_score < 5:
        return None

    return [{
        "_type":     "product_card",
        "_source":   "product_db",
        "name":      f"Top {best_match['category'].replace('_',' ').title()} Recommendations",
        "tagline":   f"Best {best_match['category'].replace('_',' ')} picks — region-aware, evidence-checked",
        "category":  best_match["category"],
        "intent":    "product_intent",
        "products":  best_match["products"],
        "warning":   best_match.get("warning", ""),
        "sections":  {},
    }]


# ═══════════════════════════════════════════════════════════════════════════
# LIVE DATA RETRIEVAL
# ═══════════════════════════════════════════════════════════════════════════

TRUST_TIERS = {"pubmed": 5, "clinicaltrials": 4, "examine": 4, "openfda": 3, "serp": 2, "scraped": 1}


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
        params2: dict[str, Any] = {"db": "pubmed", "id": ",".join(ids), "retmode": "json", "rettype": "abstract"}
        if PUBMED_API_KEY:
            params2["api_key"] = PUBMED_API_KEY
        r2 = requests.get(PUBMED_FETCH, params=params2, timeout=10)
        articles = r2.json().get("result", {}) if r2.status_code == 200 else {}
        refs = []
        for pid in ids:
            article = articles.get(pid, {})
            authors = article.get("authors", [])
            refs.append({
                "id": pid, "source": "pubmed", "trust": TRUST_TIERS["pubmed"],
                "title": article.get("title", f"PubMed ID: {pid}"),
                "authors": (authors[0].get("name", "") + " et al.") if authors else "",
                "journal": article.get("fulljournalname", ""),
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pid}/",
            })
        return refs
    except Exception as e:
        print(f"[PubMed] {e}")
        return []


def _examine_data(compound_name: str) -> dict | None:
    try:
        slug = compound_name.lower().replace(" ", "-").replace("(", "").replace(")", "")
        url = f"https://examine.com/supplements/{slug}/"
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=8)
        if r.status_code != 200:
            return None
        m = re.search(r'<meta[^>]*name="description"[^>]*content="([^"]{50,})"', r.text)
        summary = re.sub(r"<[^>]+>", "", m.group(1)).strip()[:400] if m else ""
        return {"source": "examine", "trust": TRUST_TIERS["examine"], "url": url, "summary": summary}
    except Exception as e:
        print(f"[Examine] {e}")
        return None


def _openfda_safety(compound_name: str) -> list[dict]:
    try:
        r = requests.get(OPENFDA_URL, params={"search": f'patient.drug.medicinalproduct:"{compound_name}"', "limit": 3}, timeout=6)
        if r.status_code != 200:
            return []
        events = []
        for ev in r.json().get("results", [])[:3]:
            reactions = [rx.get("reactionmeddrapt", "") for rx in ev.get("patient", {}).get("reaction", [])[:3]]
            events.append({"source": "openfda", "trust": TRUST_TIERS["openfda"], "reactions": reactions})
        return events
    except Exception as e:
        print(f"[OpenFDA] {e}")
        return []


def _serp_search(query: str) -> list[dict]:
    if not SERP_API_KEY:
        return []
    try:
        r = requests.get("https://serpapi.com/search.json", params={
            "q": f"{query} site:examine.com OR site:pubmed.ncbi.nlm.nih.gov OR site:jissn.biomedcentral.com",
            "api_key": SERP_API_KEY, "engine": "google", "num": 5, "hl": "en",
        }, timeout=8)
        if r.status_code != 200:
            return []
        return [{"source": "serp", "trust": TRUST_TIERS["serp"],
                 "title": res.get("title", ""), "url": res.get("link", ""), "snippet": res.get("snippet", "")}
                for res in r.json().get("organic_results", [])[:5]]
    except Exception as e:
        print(f"[SerpAPI] {e}")
        return []


def _retrieve_live(query: str, compounds: list[str]) -> dict:
    import concurrent.futures
    primary = compounds[0] if compounds else query
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
        fp = ex.submit(_pubmed_search, primary, 5)
        fe = ex.submit(_examine_data, primary)
        ff = ex.submit(_openfda_safety, primary)
        fs = ex.submit(_serp_search, query)
        return {"pubmed": fp.result(), "examine": fe.result() or {}, "fda": ff.result(), "serp": fs.result()}


def _filter_evidence(live: dict) -> dict:
    all_items = [*live.get("pubmed", []), *live.get("serp", []), *live.get("fda", [])]
    if live.get("examine"):
        all_items.append(live["examine"])
    filtered = sorted([i for i in all_items if i.get("trust", 0) >= 2], key=lambda x: x.get("trust", 0), reverse=True)
    return {
        "high_trust": [i for i in filtered if i.get("trust", 0) >= 4],
        "pubmed_ids": [i["id"] for i in live.get("pubmed", []) if "id" in i],
        "examine_url": live.get("examine", {}).get("url"),
        "examine_summary": live.get("examine", {}).get("summary", ""),
        "fda_events": live.get("fda", []),
    }


# ═══════════════════════════════════════════════════════════════════════════
# CLAUDE CALL
# ═══════════════════════════════════════════════════════════════════════════

_SYSTEM_PROMPT = """You are FitSearch AI — a world-class evidence-based sports nutrition scientist.

Generate a structured 10-section research report for the user's fitness query.

RULES:
1. Respond ONLY with valid JSON — no markdown fences, no prose outside JSON.
2. Respond in the SAME language as the user's query.
3. Specific dosages, timing, and practical tips required.
4. safe_for_beginners must be false for steroids and most SARMs.
5. Include real PubMed IDs where possible.
6. evidence_tier: "very_high" | "high" | "moderate" | "low"
7. legal_status for controlled/research substances.
8. RELEVANCE: Only generate a report for the PRIMARY compound in the query.
   Do NOT include unrelated compounds as primary results.

JSON structure:
{
  "detected_language": "English",
  "intent": "explain|recommend|dosage|compare|cycle|side_effects|general",
  "name": "Primary compound name",
  "tagline": "One-sentence description",
  "category": "supplement|sarm|steroid|peptide|training|diet",
  "evidence_tier": "very_high|high|moderate|low",
  "safe_for_beginners": true,
  "legal_status": "status or null",
  "sections": {
    "what_it_is": "2-4 sentences on mechanism",
    "dosage": "Specific evidence-based dosage",
    "timing": "Optimal timing and why",
    "how_to_take": "Practical tips",
    "hydration": "Fluid needs",
    "training_synergy": "How to combine with training",
    "cycling": "Cycling protocol or not needed",
    "benefits": ["benefit 1", "benefit 2", "benefit 3"],
    "side_effects": [{"effect": "description", "severity": "low|medium|high"}],
    "references": [
      {"type": "pubmed", "id": "PMID", "title": "Study title", "url": "https://pubmed.ncbi.nlm.nih.gov/PMID/"},
      {"type": "examine", "url": "https://examine.com/supplements/compound/", "title": "Examine.com"}
    ]
  },
  "stacking": ["compound 1", "compound 2"],
  "final_recommendation": "2-3 sentence actionable recommendation",
  "ai_note": "Confidence note"
}"""


def _call_claude(query: str, compounds: list[str], kb_items: list[dict], evidence: dict) -> dict | None:
    if not ANTHROPIC_API_KEY:
        return None
    pubmed_block = "\n\nLIVE PUBMED:\n" + "\n".join(f"- PMID {pid}: https://pubmed.ncbi.nlm.nih.gov/{pid}/" for pid in evidence.get("pubmed_ids", [])[:5]) if evidence.get("pubmed_ids") else ""
    examine_block = f"\n\nEXAMINE.COM:\nURL: {evidence['examine_url']}\nSummary: {evidence.get('examine_summary','')[:300]}" if evidence.get("examine_url") else ""
    kb_block = ""
    for item in kb_items[:2]:
        kb_block += f"\n\nKB — {item['name']}:\n{json.dumps({k: v for k, v in item.items() if k not in ['aliases', 'id']}, ensure_ascii=False)[:1200]}"
    user_msg = f"User query: {query}\nDetected compounds: {', '.join(compounds) if compounds else 'general'}\n{kb_block}{pubmed_block}{examine_block}"
    try:
        resp = requests.post(
            ANTHROPIC_URL,
            headers={"x-api-key": ANTHROPIC_API_KEY, "anthropic-version": "2023-06-01", "content-type": "application/json"},
            json={"model": "claude-sonnet-4-20250514", "max_tokens": 3000, "system": _SYSTEM_PROMPT, "messages": [{"role": "user", "content": user_msg}]},
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

def _kb_to_report(item: dict, live_evidence: dict) -> dict:
    sections: dict = {
        "what_it_is":       item.get("what_it_is", item.get("summary", "")),
        "dosage":           item.get("dosage", "—"),
        "timing":           item.get("timing", "—"),
        "how_to_take":      item.get("how_to_take", "Mix with water or protein shake."),
        "hydration":        item.get("hydration", "Maintain 2.5–3 L/day."),
        "training_synergy": item.get("training_synergy", "Effective with progressive-overload resistance training."),
        "cycling":          item.get("cycling", "No cycling required."),
        "benefits":         item.get("benefits", []),
        "side_effects":     item.get("side_effects", []),
        "references":       [],
    }
    for pid in (live_evidence.get("pubmed_ids") or item.get("pubmed_ids", []))[:5]:
        sections["references"].append({"type": "pubmed", "id": pid, "title": f"PubMed ID: {pid}", "url": f"https://pubmed.ncbi.nlm.nih.gov/{pid}/"})
    for ref in item.get("research_refs", []):
        sections["references"].append({"type": "journal", "id": None, "title": ref, "url": None})
    exam_url = item.get("examine_url") or live_evidence.get("examine_url")
    if exam_url:
        sections["references"].append({"type": "examine", "id": None, "title": f"Examine.com — {item['name']}", "url": exam_url})
    return {
        "name":                 item["name"],
        "tagline":              item.get("summary", "")[:120],
        "category":             item.get("category", "supplement"),
        "evidence_tier":        item.get("evidence_tier", "moderate"),
        "safe_for_beginners":   item.get("safe_for_beginners", True),
        "legal_status":         item.get("legal_status"),
        "sections":             sections,
        "stacking":             item.get("stacking", []),
        "final_recommendation": item.get("final_recommendation", ""),
        "ai_note":              "Curated knowledge base. Set ANTHROPIC_API_KEY for real-time AI reports.",
        "_source":              "kb",
        "_type":                "research_report",
    }


def _claude_to_report(ai_data: dict, live_evidence: dict) -> dict:
    sections = ai_data.get("sections", {})
    existing_ids = {r.get("id") for r in sections.get("references", [])}
    for pid in live_evidence.get("pubmed_ids", []):
        if pid not in existing_ids:
            sections.setdefault("references", []).append({"type": "pubmed", "id": pid, "title": f"PubMed ID: {pid}", "url": f"https://pubmed.ncbi.nlm.nih.gov/{pid}/"})
    if live_evidence.get("examine_url"):
        sections.setdefault("references", []).append({"type": "examine", "id": None, "title": f"Examine.com — {ai_data.get('name','')}", "url": live_evidence["examine_url"]})
    return {
        "name":                 ai_data.get("name", "Supplement"),
        "tagline":              ai_data.get("tagline", ""),
        "category":             ai_data.get("category", "supplement"),
        "evidence_tier":        ai_data.get("evidence_tier", "moderate"),
        "safe_for_beginners":   ai_data.get("safe_for_beginners", True),
        "legal_status":         ai_data.get("legal_status"),
        "sections":             sections,
        "stacking":             ai_data.get("stacking", []),
        "final_recommendation": ai_data.get("final_recommendation", ""),
        "ai_note":              ai_data.get("ai_note", "AI-generated report."),
        "_source":              "ai",
        "_type":                "research_report",
    }


# ═══════════════════════════════════════════════════════════════════════════
# TRAINING / DIET INTENT  — structured plan generator
# ═══════════════════════════════════════════════════════════════════════════

TRAINING_KB: dict[str, dict] = {
    "high protein diet": {
        "name": "High Protein Diet for Muscle Gain",
        "plan_type": "diet",
        "target": "muscle_gain",
        "sections": {
            "overview": "High-protein diets (1.6–2.2 g/kg/day) are the single most evidence-backed nutritional strategy for muscle gain and body recomposition.",
            "macros": {"protein_g_per_kg": "1.6–2.2", "carbs": "3–6 g/kg (training volume-dependent)", "fats": "0.8–1.2 g/kg"},
            "meal_timing": ["Breakfast: Eggs + oats + milk", "Pre-workout: Banana + whey or chicken sandwich", "Post-workout: Whey + rice/potato within 2 hours", "Dinner: Lean protein + vegetables + complex carbs", "Before bed: Casein protein or Greek yogurt"],
            "key_foods": ["Chicken breast", "Eggs (whole)", "Greek yogurt", "Cottage cheese", "Salmon / tuna", "Whey / casein protein", "Lean beef (93% lean)", "Tofu / tempeh (plant-based)"],
            "supplements": ["Creatine monohydrate 3–5 g/day", "Whey protein (if dietary shortfall)", "Vitamin D3 + K2", "Omega-3 fish oil"],
            "research_refs": ["Morton et al. (2018) BJSM — protein meta-analysis (49 RCTs)", "Phillips & Van Loon (2011) J Sports Sci — protein timing review"],
        },
        "_type": "training_plan",
        "_source": "kb",
    },
    "hypertrophy training": {
        "name": "Hypertrophy Training Split (4-Day)",
        "plan_type": "workout",
        "target": "muscle_gain",
        "sections": {
            "overview": "Hypertrophy-optimised training requires 10–20 working sets per muscle group per week, 6–20 rep ranges, and 48–72 h recovery per muscle group.",
            "schedule": {
                "Day 1": "Chest + Triceps — Bench press 4×8-12, Incline DB press 3×10, Cable fly 3×12-15, Tricep pushdown 3×12, Skull crushers 3×10",
                "Day 2": "Back + Biceps — Barbell row 4×6-10, Lat pulldown 3×10-12, Cable row 3×12, Barbell curl 3×10, Hammer curl 3×12",
                "Day 3": "REST or active recovery",
                "Day 4": "Legs — Squat 4×6-10, Romanian deadlift 3×10, Leg press 3×12, Leg curl 3×12, Calf raises 4×15",
                "Day 5": "Shoulders + Abs — OHP 4×6-10, Lateral raise 3×15, Face pull 3×15, Plank 3×45 s, Cable crunch 3×15",
            },
            "key_principles": ["Progressive overload — add weight or reps each session", "2–3 min rest for compound lifts, 60–90 s for isolation", "Train within 1–2 reps of failure for last set", "Track lifts — log everything"],
            "research_refs": ["Schoenfeld (2010) J Strength Cond Res — hypertrophy mechanisms", "Krieger (2010) J Strength Cond Res — sets per muscle meta-analysis"],
        },
        "_type": "training_plan",
        "_source": "kb",
    },
}

_TRAINING_TRIGGERS = {
    "high protein diet": "high protein diet",
    "muscle gain diet": "high protein diet",
    "bulking diet": "high protein diet",
    "hypertrophy": "hypertrophy training",
    "training split": "hypertrophy training",
    "workout plan": "hypertrophy training",
    "muscle building program": "hypertrophy training",
}


def _training_results(query: str) -> list[dict] | None:
    q = query.lower()
    for trigger, key in _TRAINING_TRIGGERS.items():
        if trigger in q:
            plan = TRAINING_KB.get(key)
            if plan:
                return [{**plan, "tagline": plan["sections"].get("overview", "")[:100]}]
    return None


# ═══════════════════════════════════════════════════════════════════════════
# PUBLIC INTERFACE
# ═══════════════════════════════════════════════════════════════════════════

def search_knowledge(query: str, filters: list | None = None, force_fresh: bool = False) -> list[dict]:
    """
    Main search entry point.

    FIX: force_fresh=True bypasses cache (used when filters change in real-time).
    FIX: filter changes produce a different cache key → correct results per filter state.
    FIX: relevance threshold prevents unrelated items from appearing.
    FIX: intent routing sends product queries to product DB, training to plan KB.
    """
    filters   = filters or []
    ts        = datetime.now(timezone.utc).isoformat()

    # Classify intent first
    top_intent = classify_intent(query)

    # ── PRODUCT INTENT ────────────────────────────────────────────────────
    if top_intent == "product_intent":
        ckey = _cache_key(query, filters, "product")
        if not force_fresh:
            cached = _cache_get(ckey, ttl=FILTER_TTL if filters else CACHE_TTL_SEC)
            if cached:
                for r in cached: r["_cached"] = True
                return cached
        results = _search_products(query, filters) or []
        if not results:
            # Fall through to research path if no product match
            top_intent = "research_intent"
        else:
            _cache_set(ckey, query, results, source="product_db", intent="product")
            return results

    # ── TRAINING / DIET INTENT ────────────────────────────────────────────
    if top_intent == "training_intent":
        ckey = _cache_key(query, filters, "training")
        if not force_fresh:
            cached = _cache_get(ckey)
            if cached:
                for r in cached: r["_cached"] = True
                return cached
        results = _training_results(query)
        if results:
            _cache_set(ckey, query, results, source="kb", intent="training")
            return results
        # Fall through to research

    # ── RESEARCH INTENT ───────────────────────────────────────────────────
    ckey = _cache_key(query, filters, "research")
    # FIX: filters with small TTL (5 min) for near-real-time filter updates
    ttl  = FILTER_TTL if filters else CACHE_TTL_SEC
    if not force_fresh:
        cached = _cache_get(ckey, ttl)
        if cached:
            for r in cached: r["_cached"] = True
            return cached

    # Entity detection
    compounds, per_compound_tags, intent = _detect_entities(query)

    # KB scoring with fixed algorithm
    kb_matches = _kb_results(query, compounds, per_compound_tags, filters)

    # Live data retrieval
    live     = _retrieve_live(query, compounds)
    evidence = _filter_evidence(live)

    # Claude call
    ai_data = _call_claude(query, compounds, kb_matches, evidence)

    results: list[dict] = []

    if ai_data and ai_data.get("sections"):
        report = _claude_to_report(ai_data, evidence)
        report["_timestamp"] = ts
        results.append(report)
        # Append only closely related KB items (same compound or same category)
        ai_name = ai_data.get("name", "").lower()
        for item in kb_matches:
            if item["name"].lower() != ai_name:
                # Only add if it shares the exact compound with the query
                if any(c.lower() in item["name"].lower() for c in compounds):
                    r = _kb_to_report(item, {})
                    r["_timestamp"] = ts
                    r["_supplementary"] = True
                    results.append(r)
    else:
        for item in kb_matches[:4]:
            r = _kb_to_report(item, evidence if not results else {})
            r["_timestamp"] = ts
            results.append(r)

    if not results:
        results = [_fallback(query, ts)]

    _cache_set(ckey, query, results, source="ai" if ai_data else "kb", intent="research")
    return results


def get_recommendations(recent_queries: list[str], user: dict) -> list[dict]:
    goal  = (user.get("goal") or "muscle_gain").replace("-", "_")
    level = user.get("experience_level") or "beginner"
    seen: set[str] = set()
    for q in recent_queries:
        comps, _, _ = _detect_entities(q)
        for c in comps:
            m = _ALIAS.get(c.lower())
            if m: seen.add(m["id"])
    recs = []
    for item in KB:
        if item["id"] in seen: continue
        sc = 0
        if goal in item.get("tags", []): sc += 4
        if item.get("safe_for_beginners") and level == "beginner": sc += 3
        if not item.get("safe_for_beginners") and level in ("intermediate", "advanced"): sc += 2
        if item["evidence_tier"] in ("very_high", "high"): sc += 1
        if sc <= 1: continue
        parts = [f"Matches your {goal.replace('_',' ')} goal"]
        if level == "beginner" and item.get("safe_for_beginners"): parts.append("beginner-friendly")
        if item["evidence_tier"] in ("very_high", "high"): parts.append("strong research support")
        recs.append({**item, "_sc": sc, "recommendation_reason": " · ".join(parts)})
    recs.sort(key=lambda x: x["_sc"], reverse=True)
    return [{k: v for k, v in r.items() if k != "_sc"} for r in recs[:6]]


def _fallback(query: str, ts: str) -> dict:
    return {
        "name": f"Search: {query}", "tagline": "No specific match found.",
        "category": "supplement", "evidence_tier": "moderate",
        "safe_for_beginners": True, "legal_status": None,
        "sections": {
            "what_it_is": f"No match for '{query}'. Try: Creatine monohydrate, Whey protein, Beta-alanine, Ostarine, Testosterone enanthate, BPC-157, HGH, Caffeine, Pre-workout, BCAAs.",
            "dosage": "—", "timing": "—", "how_to_take": "—",
            "hydration": "—", "training_synergy": "—", "cycling": "—",
            "benefits": [], "side_effects": [],
            "references": [{"type": "examine", "url": "https://examine.com", "title": "Examine.com", "id": None}],
        },
        "stacking": [], "final_recommendation": "Refine your query with a specific compound or supplement.",
        "ai_note": "No match.", "_source": "fallback", "_type": "research_report", "_timestamp": ts,
    }
