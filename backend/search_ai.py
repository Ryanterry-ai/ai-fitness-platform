"""
search_ai.py  —  FitSearch AI Hybrid Search Engine
====================================================

Pipeline (executed left to right, first success wins):

  User Query
      │
      ▼
  1. ENTITY DETECTION  — detect compounds + intent
      │
      ▼
  2. CACHE LOOKUP  — SQLite: was this query answered in last 24 h?
      │ miss
      ▼
  3. LIVE DATA RETRIEVAL (parallel)
      ├── PubMed API        (peer-reviewed research)
      ├── Examine.com API   (trusted supplement DB)
      ├── OpenFDA API       (safety / adverse events)
      └── Web scrape fallback (if APIs incomplete)
      │
      ▼
  4. EVIDENCE FILTERING  — score + rank by trust tier
      │
      ▼
  5. CLAUDE LLM CALL  — entity + KB + live data → structured report
      │
      ▼
  6. CACHE WRITE  — store report in SQLite for 24 h
      │
      ▼
  7. STRUCTURED RESULT  — 10-section clickable report returned to frontend

Environment variables:
  ANTHROPIC_API_KEY   — required for AI reports
  PUBMED_API_KEY      — optional, raises PubMed rate limit from 3/s to 10/s
  SERP_API_KEY        — optional, enables live Google results via SerpAPI
"""

from __future__ import annotations

import os, json, re, time, hashlib, sqlite3, threading
import urllib.parse
from datetime import datetime, timezone
from typing import Any

import requests

# ── API keys ──────────────────────────────────────────────────────────────
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
PUBMED_API_KEY    = os.getenv("PUBMED_API_KEY", "")
SERP_API_KEY      = os.getenv("SERP_API_KEY", "")

# ── Paths ─────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_DB   = os.path.join(BASE_DIR, "database", "search_cache.db")

# ── Constants ─────────────────────────────────────────────────────────────
ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
PUBMED_SEARCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
PUBMED_FETCH  = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
OPENFDA_URL   = "https://api.fda.gov/drug/event.json"
EXAMINE_BASE  = "https://examine.com/supplements/"
CACHE_TTL_SEC = 86400  # 24 hours

_cache_lock = threading.Lock()


# ═══════════════════════════════════════════════════════════════════════════
# LOCAL KNOWLEDGE BASE  — always-available offline data
# ═══════════════════════════════════════════════════════════════════════════

KB: list[dict] = [
    {
        "id": "crm_mono", "name": "Creatine monohydrate",
        "aliases": ["creatine", "kreatin", "creatina", "créatine", "क्रिएटिन", "肌酸",
                    "creatina monoidrata", "creatina monohidrato"],
        "category": "supplement",
        "tags": ["strength", "muscle_gain", "power", "beginner", "creatine", "atp"],
        "summary": "The most extensively researched ergogenic aid. Increases phosphocreatine stores enabling faster ATP regeneration during high-intensity exercise.",
        "what_it_is": "Creatine monohydrate is an organic compound naturally produced in the liver and kidneys from amino acids arginine, glycine, and methionine. About 95% is stored in skeletal muscle as phosphocreatine. Supplementation saturates these stores, directly fuelling the ATP-PCr energy system during short, explosive efforts.",
        "dosage": "Loading (optional): 20 g/day split into 4 × 5 g doses for 5–7 days. Maintenance: 3–5 g/day. No-loading protocol: 3–5 g/day consistently (~3–4 weeks to full saturation.",
        "timing": "Post-workout slightly superior to pre-workout per meta-analyses. Consistency matters far more than exact timing — any time of day works.",
        "how_to_take": "Dissolve in 200–300 ml of water, juice, or protein shake. Monohydrate is tasteless and mixes easily. Taking with carbohydrates increases muscle uptake via insulin.",
        "hydration": "Increase fluid intake to 2.5–3.5 L/day. Creatine draws water into muscle cells — adequate hydration prevents cramps and supports performance.",
        "training_synergy": "Most effective with progressive-overload resistance training. Compound lifts (squat, deadlift, bench press) maximise creatine's ATP benefits. Also benefits high-intensity interval training.",
        "cycling": "No cycling required — long-term continuous use (5+ years) has been shown safe in research. No washout period needed.",
        "benefits": ["Strength increase 5–15%", "Power output improvement (PCr resynthesis)", "Faster recovery between sets", "Lean mass support (muscle volumisation + synthesis)", "Cognitive performance support (emerging research)"],
        "side_effects": [{"effect": "Water retention (mild, intracellular — cosmetic only)", "severity": "low"}, {"effect": "GI discomfort if loading dose taken all at once", "severity": "medium"}],
        "stacking": ["Beta-alanine (complementary energy systems)", "Caffeine (minor antagonism at high doses — not clinically significant)", "Whey protein (muscle protein synthesis)"],
        "final_recommendation": "Pair 3–5 g creatine monohydrate with a post-workout carbohydrate + protein meal. Begin progressive overload training within the same week. Expect strength improvements in 2–4 weeks.",
        "evidence_tier": "very_high",
        "safe_for_beginners": True,
        "pubmed_ids": ["28615996", "11509496", "14636102"],
        "examine_url": "https://examine.com/supplements/creatine/",
        "research_refs": ["Buford et al. (2007) JISSN 4:6 — ISSN Position Stand", "Rawson & Volek (2003) J Strength Cond Res", "Lanhers et al. (2017) Eur J Sport Sci — strength meta-analysis"],
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
        "benefits": ["Equivalent strength gains at lower dose", "Minimal bloating", "Easy dissolution"],
        "side_effects": [{"effect": "Minimal GI issues", "severity": "low"}],
        "stacking": ["Citrulline malate", "Beta-alanine"],
        "final_recommendation": "Choose HCL if monohydrate causes GI discomfort. For most users monohydrate is the superior cost-effective choice.",
        "evidence_tier": "high",
        "safe_for_beginners": True,
        "pubmed_ids": ["19844003"],
        "examine_url": "https://examine.com/supplements/creatine/",
        "research_refs": ["Miller et al. (2009) J Int Soc Sports Nutr"],
    },
    {
        "id": "beta_al", "name": "Beta-alanine",
        "aliases": ["beta alanine", "beta-alanine", "carnosine precursor", "beta alanina"],
        "category": "supplement",
        "tags": ["endurance", "strength", "fatigue", "pre_workout"],
        "summary": "Amino acid precursor to carnosine — buffers lactic acid in muscle, delaying fatigue. Most effective for exercise lasting 60–240 seconds.",
        "what_it_is": "Non-essential amino acid that combines with histidine in muscle tissue to form carnosine — a pH buffer that neutralises lactic acid during intense exercise. Supplementation raises muscle carnosine by 40–80% over 4–6 weeks.",
        "dosage": "3.2–6.4 g/day. Split into 1.6 g doses throughout the day to reduce tingling (paresthesia).",
        "timing": "Pre-workout or evenly split throughout the day. Tingling peaks 30–60 min post-dose and is harmless.",
        "how_to_take": "Capsules or powder mixed in water or shake. Sustained-release formulas reduce paresthesia.",
        "hydration": "2–3 L/day standard.",
        "training_synergy": "Ideal for high-rep resistance training, rowing, cycling, and team sports. Synergises with creatine — creatine covers explosive < 10 s, beta-alanine covers sustained 60–240 s.",
        "cycling": "No cycling required. Benefits plateau after ~10 weeks at full dose — maintenance at 3.2 g/day thereafter.",
        "benefits": ["Delayed muscle fatigue and H+ accumulation", "Higher rep capacity before failure", "Endurance improvement in 1–4 minute efforts"],
        "side_effects": [{"effect": "Tingling / paresthesia — harmless, dose-dependent", "severity": "low"}],
        "stacking": ["Creatine monohydrate", "Caffeine", "L-Citrulline"],
        "final_recommendation": "Stack with creatine for comprehensive energy system coverage. Use split dosing to eliminate tingling.",
        "evidence_tier": "high",
        "safe_for_beginners": True,
        "pubmed_ids": ["22649228", "27797728"],
        "examine_url": "https://examine.com/supplements/beta-alanine/",
        "research_refs": ["Hobson et al. (2012) Amino Acids — 15-study meta-analysis", "Stout et al. (2006) Int J Sport Nutr Exerc Metab"],
    },
    {
        "id": "citrulline", "name": "L-Citrulline / Citrulline malate",
        "aliases": ["citrulline", "citrulline malate", "l-citrulline", "pump supplement", "no booster", "citrulina"],
        "category": "supplement",
        "tags": ["pump", "endurance", "blood_flow", "pre_workout", "nitric_oxide"],
        "summary": "Precursor to arginine → nitric oxide. Enhances blood flow, muscle pump, and endurance. Malate form also reduces fatigue.",
        "what_it_is": "L-citrulline is an amino acid converted to arginine in the kidneys, then to nitric oxide — a potent vasodilator. Citrulline malate combines citrulline with malic acid (a Krebs cycle intermediate) for additional anti-fatigue effects.",
        "dosage": "L-citrulline: 6–8 g. Citrulline malate 2:1: 8 g. Take 30–60 min pre-workout.",
        "timing": "30–60 minutes pre-workout on an empty or light stomach for optimal absorption.",
        "how_to_take": "Mix in 300–400 ml water. Slight tartness — juice improves palatability.",
        "hydration": "3+ L/day. Vasodilation increases sweating.",
        "training_synergy": "Best for volume training and metabolic conditioning. Excellent for hypertrophy days where pump and endurance are priority.",
        "cycling": "No cycling needed. Some athletes cycle stimulant-containing pre-workouts that include citrulline.",
        "benefits": ["Significant muscle pump via NO-mediated vasodilation", "Reduced muscle soreness 24–48 h post-training", "Endurance improvement 12–15%", "Blood pressure support"],
        "side_effects": [{"effect": "GI discomfort at doses above 10 g", "severity": "low"}],
        "stacking": ["Beta-alanine", "Caffeine", "Creatine"],
        "final_recommendation": "Use 8 g citrulline malate 2:1 pre-workout. Combine with beta-alanine and caffeine for a complete evidence-based pre-workout.",
        "evidence_tier": "high",
        "safe_for_beginners": True,
        "pubmed_ids": ["21414438", "26900386"],
        "examine_url": "https://examine.com/supplements/citrulline/",
        "research_refs": ["Pérez-Guisado & Jakeman (2010) JSCR", "Suzuki et al. (2016) Eur J Nutr"],
    },
    {
        "id": "whey", "name": "Whey protein",
        "aliases": ["whey", "whey protein", "proteina whey", "proteine whey", "proteína whey",
                    "व्हे प्रोटीन", "乳清蛋白", "protéine lactosérum", "molkenprotein"],
        "category": "supplement",
        "tags": ["muscle_gain", "recovery", "protein", "beginner"],
        "summary": "Fast-digesting milk protein with highest leucine content of any protein — optimal for post-workout muscle protein synthesis.",
        "what_it_is": "Whey is the liquid by-product of cheese production. Filtered and dried into concentrate (70–80% protein), isolate (90%+ protein, < 1% lactose), or hydrolysate (pre-digested). Richest natural source of leucine (10–11%) — the primary amino acid trigger for muscle protein synthesis.",
        "dosage": "25–50 g per serving as needed to reach total daily protein target of 1.6–2.2 g/kg bodyweight.",
        "timing": "Post-workout for peak MPS stimulus. Any time of day to supplement dietary protein deficit.",
        "how_to_take": "Shaker bottle with 200–300 ml water or milk. Add to oats, yogurt, or baking. Isolate mixes more cleanly.",
        "hydration": "Protein metabolism increases urea production — maintain 2.5–3 L/day water intake.",
        "training_synergy": "Consume within 2 hours post-resistance training for optimal MPS. Combine with fast carbohydrates (banana, white rice) for insulin-mediated uptake.",
        "cycling": "No cycling. Use daily as needed to hit protein targets.",
        "benefits": ["Maximises MPS via leucine content", "Fast digestion ideal post-workout", "Complete amino acid profile", "Cost-effective protein source"],
        "side_effects": [{"effect": "GI discomfort if lactose intolerant — use isolate", "severity": "medium"}, {"effect": "Kidney stress only relevant in existing kidney disease", "severity": "low"}],
        "stacking": ["Creatine", "Carbohydrates post-workout", "Casein before bed"],
        "final_recommendation": "Target total daily protein first (food + supplement). Post-workout whey shake with fast carbs optimises muscle protein synthesis and glycogen replenishment.",
        "evidence_tier": "very_high",
        "safe_for_beginners": True,
        "pubmed_ids": ["19589961", "25048790"],
        "examine_url": "https://examine.com/supplements/whey-protein/",
        "research_refs": ["Tang et al. (2009) Am J Clin Nutr", "Morton et al. (2018) BJSM — protein meta-analysis"],
    },
    {
        "id": "caffeine", "name": "Caffeine",
        "aliases": ["caffeine", "caffeina", "caféine", "koffein", "कैफीन", "咖啡因", "caffeine anhydrous"],
        "category": "supplement",
        "tags": ["strength", "endurance", "fat_loss", "focus", "pre_workout", "energy"],
        "summary": "Adenosine receptor antagonist reducing perceived exertion. Increases power output, endurance, and fat oxidation.",
        "what_it_is": "Caffeine blocks adenosine receptors in the brain and peripheral tissue, reducing perceived effort and increasing catecholamine release. The most extensively studied ergogenic aid — effective in over 300 clinical trials across all sport types.",
        "dosage": "3–6 mg/kg bodyweight (200–400 mg for most adults). Higher doses do not provide additional ergogenic benefit and increase side effects.",
        "timing": "30–60 minutes before training. Half-life ~5–6 hours — avoid dosing within 6 hours of sleep.",
        "how_to_take": "Anhydrous caffeine (pills/powder) for precise dosing. Coffee effective but variable caffeine content. Combined with L-Theanine (2:1 ratio) for smooth focus without jitters.",
        "hydration": "Mild diuretic effect — increase water intake by 500 ml on caffeine days.",
        "training_synergy": "Effective across all training modalities. Most pronounced benefits in endurance, strength, and power sports. Take 30 min pre-workout; pre-exhaustion athletes may need 45–60 min.",
        "cycling": "Cycle off caffeine 1–2 weeks per month to reset adenosine receptor sensitivity. Tolerance builds within 2 weeks of daily use, blunting ergogenic effects.",
        "benefits": ["Power output +3–7%", "Endurance capacity improvement", "Fat oxidation (thermogenic)", "Focus, reaction time, alertness", "Reduced perceived effort"],
        "side_effects": [{"effect": "Tolerance buildup with daily use", "severity": "medium"}, {"effect": "Sleep disruption if dosed too late", "severity": "medium"}, {"effect": "Anxiety and elevated heart rate at high doses", "severity": "medium"}],
        "stacking": ["L-Theanine 200 mg (2:1 ratio)", "L-Citrulline", "Beta-alanine"],
        "final_recommendation": "Use 3–5 mg/kg bodyweight 30–60 min pre-workout. Stack with 200 mg L-Theanine. Cycle 5 days on / 2 days off or take planned 1–2 week breaks monthly.",
        "evidence_tier": "very_high",
        "safe_for_beginners": True,
        "pubmed_ids": ["34445894", "20019636"],
        "examine_url": "https://examine.com/supplements/caffeine/",
        "research_refs": ["Grgic et al. (2021) BJSM — 300-study meta-analysis", "Goldstein et al. (2010) J Int Soc Sports Nutr — ISSN position stand"],
    },
    {
        "id": "ostarine", "name": "Ostarine (MK-2866)",
        "aliases": ["ostarine", "mk2866", "mk-2866", "enobosarm", "mk 2866", "ostarina"],
        "category": "sarm",
        "tags": ["muscle_gain", "fat_loss", "recomp", "sarm"],
        "summary": "Mildest SARM. Selective androgen receptor modulator with muscle and bone anabolic effects and reduced androgenic activity. Research chemical — not approved for human use.",
        "what_it_is": "Ostarine is a nonsteroidal SARM originally developed by GTx for muscle-wasting diseases. Selectively binds androgen receptors in muscle and bone with minimal activation of reproductive tissue receptors. Produces lean mass gains without the full androgenic side-effect profile of testosterone.",
        "dosage": "10–25 mg/day. Start at 10 mg for first cycle to assess tolerance.",
        "timing": "Once daily, same time each day, with or without food.",
        "how_to_take": "Oral liquid or capsule. Measure carefully — liquid suspensions require precise dosing syringe.",
        "hydration": "Standard 2.5–3 L/day. No special hydration requirement.",
        "training_synergy": "Excellent for recomposition — muscle gain + fat loss simultaneously. Pairs well with body recomposition nutrition protocols (slight calorie surplus or maintenance).",
        "cycling": "8-week cycles standard. Run bloodwork before and 4–6 weeks post-cycle. Mini PCT (Nolvadex 20 mg/day × 3 weeks) if suppression symptoms occur.",
        "benefits": ["Lean muscle gain 2–4 kg typical in 8 weeks", "Fat loss support", "Joint support and healing", "Mild testosterone suppression vs steroids"],
        "side_effects": [{"effect": "Mild testosterone suppression — bloodwork required", "severity": "medium"}, {"effect": "Lipid changes (HDL reduction)", "severity": "medium"}, {"effect": "Mild liver enzyme elevation possible", "severity": "low"}],
        "stacking": ["Cardarine GW-501516 (fat loss)", "MK-677 Ibutamoren (GH + recovery)"],
        "final_recommendation": "If considering Ostarine: obtain bloodwork baseline. Start at 10 mg, run 8 weeks, recheck bloodwork. Do not use without access to bloodwork monitoring.",
        "evidence_tier": "moderate",
        "safe_for_beginners": True,
        "pubmed_ids": ["20814882", "23631853"],
        "examine_url": "https://examine.com/supplements/ostarine/",
        "research_refs": ["Dalton et al. (2011) Cancer Res", "Papanicolaou et al. (2013) J Gerontol — Phase II"],
        "legal_status": "Research chemical — not approved for human use in any country. Banned by WADA.",
    },
    {
        "id": "test_e", "name": "Testosterone enanthate",
        "aliases": ["testosterone enanthate", "test e", "testo e", "testosterone", "testosteron", "testosterona"],
        "category": "steroid",
        "tags": ["muscle_gain", "strength", "bulking", "testosterone", "steroid"],
        "summary": "Gold standard anabolic injectable. Long-ester testosterone with predictable pharmacokinetics and decades of clinical data.",
        "what_it_is": "Synthetic testosterone bound to an enanthate ester (7-carbon chain). The ester slows release, providing stable blood levels with twice-weekly injections. Testosterone is the body's primary anabolic hormone — exogenous administration saturates androgen receptors in muscle, bone, and CNS.",
        "dosage": "Beginner: 300–500 mg/week (split E3.5D). Intermediate: 500–750 mg/week.",
        "timing": "Injected subcutaneous or intramuscular every 3.5 days for stable blood levels.",
        "how_to_take": "IM (glute, quads, delts) or SubQ. Rotate injection sites. Use 23–25G needle for injection, 18–21G for drawing.",
        "hydration": "2.5–3 L/day. Monitor blood pressure — elevated sodium retention occurs.",
        "training_synergy": "Maximum anabolic output requires progressive overload resistance training, adequate protein (2–2.4 g/kg), calorie surplus (muscle gain), and sufficient sleep.",
        "cycling": "12–16 week cycles standard. Aromatase inhibitor (Anastrozole 0.25–0.5 mg E3D) required. PCT (Nolvadex 40/40/20/20 mg) begins 2 weeks after last injection.",
        "benefits": ["Significant lean mass and strength gains", "Improved recovery capacity", "Libido and well-being improvement", "Predictable pharmacokinetics"],
        "side_effects": [{"effect": "Complete testosterone suppression", "severity": "high"}, {"effect": "Aromatisation → estrogen management required", "severity": "medium"}, {"effect": "Cardiovascular strain (HDL reduction, LVH risk)", "severity": "high"}, {"effect": "Testicular atrophy during cycle", "severity": "high"}, {"effect": "Acne and hair loss (genetic)", "severity": "medium"}],
        "stacking": ["Anastrozole (AI)", "NPP or Deca (intermediate+)", "Anavar (cut)"],
        "final_recommendation": "Bloodwork mandatory before, mid-cycle, and post-PCT. AI + liver support + cardiovascular monitoring non-negotiable. Consult endocrinologist.",
        "evidence_tier": "very_high",
        "safe_for_beginners": False,
        "pubmed_ids": ["8637536", "11502560"],
        "examine_url": None,
        "research_refs": ["Bhasin et al. (1996) NEJM — landmark dose-response", "Bhasin et al. (2001) NEJM"],
        "legal_status": "Schedule III controlled substance (USA). Prescription only in UK, India, Canada, Australia.",
    },
    {
        "id": "bpc157", "name": "BPC-157",
        "aliases": ["bpc157", "bpc-157", "body protection compound", "bpc 157", "pentadecapeptide"],
        "category": "peptide",
        "tags": ["recovery", "injury", "joint_health", "gut", "healing", "peptide"],
        "summary": "15-amino acid peptide from gastric juice with potent tendon, ligament, muscle, and gut healing properties.",
        "what_it_is": "BPC-157 (Body Protection Compound-157) is a synthetic 15-amino acid sequence derived from a protein found in human gastric juice. Animal research demonstrates accelerated healing of tendons, ligaments, muscles, and intestinal tissue via upregulation of growth hormone receptor expression and angiogenesis.",
        "dosage": "250–500 mcg/day subcutaneous or intramuscular. Some protocols use 200–400 mcg twice daily.",
        "timing": "Near injury site (local protocol) or systemic (abdominal subcutaneous). Once or twice daily.",
        "how_to_take": "Reconstitute lyophilised powder with bacteriostatic water. Use insulin syringes (29–31G). Store reconstituted solution refrigerated, use within 30 days.",
        "hydration": "Standard 2.5–3 L/day.",
        "training_synergy": "Active rehabilitation exercises appropriate to the injury site during BPC-157 protocol maximise healing outcomes per animal research.",
        "cycling": "Acute injury: 4–6 week protocol. Chronic issues: 8–12 weeks. No established need for cycling.",
        "benefits": ["Accelerated tendon/ligament healing", "Gut lining repair", "Anti-inflammatory effects", "Angiogenesis promotion"],
        "side_effects": [{"effect": "Injection site irritation (mild, transient)", "severity": "low"}, {"effect": "Mild nausea (oral form)", "severity": "low"}],
        "stacking": ["TB-500 (systemic healing synergy)", "Ipamorelin/CJC-1295"],
        "final_recommendation": "Source quality is critical — obtain from reputable peptide research vendor. Sterility is non-negotiable. Not a substitute for physiotherapy.",
        "evidence_tier": "moderate",
        "safe_for_beginners": True,
        "pubmed_ids": ["23439702", "21447935"],
        "examine_url": "https://examine.com/supplements/bpc-157/",
        "research_refs": ["Sikiric et al. (2013) Curr Pharm Des", "Chang et al. (2011) JBMR"],
        "legal_status": "Research chemical — not approved for human use.",
    },
    {
        "id": "hgh", "name": "Human Growth Hormone (HGH)",
        "aliases": ["hgh", "human growth hormone", "growth hormone", "gh", "somatropin", "rhgh", "生长激素", "hormona de crecimiento"],
        "category": "peptide",
        "tags": ["fat_loss", "muscle_gain", "recovery", "anti_aging", "hgh", "growth hormone"],
        "summary": "Recombinant somatropin. Potent lipolytic and anabolic agent. Prescription only. Dramatically reduces visceral fat and supports lean mass.",
        "what_it_is": "Recombinant human growth hormone (somatropin) is a 191-amino acid protein identical to endogenous GH. Stimulates IGF-1 production in the liver — IGF-1 drives anabolic effects. GH itself drives lipolysis (fat breakdown). Age-related GH decline makes supplementation appealing for anti-aging and body composition.",
        "dosage": "Anti-aging/fat loss: 1–3 IU/day. Bodybuilding: 4–8 IU/day (significantly higher risk at bodybuilding doses).",
        "timing": "Sub-Q injection on waking (fat loss protocol) or before bed (GH pulse alignment). Some split protocols dose am + pm.",
        "how_to_take": "Sub-Q injection in abdomen fat, rotating sites. Reconstitute with bacteriostatic water. Refrigerate at 2–8°C.",
        "hydration": "3+ L/day. Water retention common especially in first 4–6 weeks.",
        "training_synergy": "Resistance training synergises with GH to maximise lean mass. Fasted morning cardio amplifies fat loss effects.",
        "cycling": "Anti-aging protocols often continuous (6–12 month cycles). Bodybuilding: 16–24 week cycles. Monitor IGF-1 levels to guide dosing.",
        "benefits": ["Significant visceral fat reduction", "Lean mass retention and modest gain", "Connective tissue strengthening", "Improved sleep quality"],
        "side_effects": [{"effect": "Carpal tunnel syndrome (tingling hands)", "severity": "medium"}, {"effect": "Insulin resistance — monitor blood glucose", "severity": "high"}, {"effect": "Acromegaly risk at sustained high doses", "severity": "high"}, {"effect": "Very expensive — $600–2000+/month for pharmaceutical grade", "severity": "low"}],
        "stacking": ["Testosterone (synergistic)", "T3 thyroid (advanced)", "Insulin (extreme danger — advanced only)"],
        "final_recommendation": "Physician supervision mandatory. Monitor IGF-1, fasting glucose, HbA1c quarterly. Only use pharmaceutical-grade (Novo Nordisk, Pfizer, Eli Lilly) to avoid counterfeit risk.",
        "evidence_tier": "very_high",
        "safe_for_beginners": False,
        "pubmed_ids": ["2388534", "7476061"],
        "examine_url": None,
        "research_refs": ["Rudman et al. (1990) NEJM — landmark study", "Vance (1990) NEJM editorial"],
        "legal_status": "Prescription only in all countries. Banned by WADA. Significant legal risk.",
    },
    {
        "id": "vitamin_d", "name": "Vitamin D3 + K2",
        "aliases": ["vitamin d", "vitamin d3", "cholecalciferol", "vit d", "vitamina d", "vitamine d", "विटामिन डी"],
        "category": "supplement",
        "tags": ["health", "testosterone", "immune", "bone", "recovery", "foundation"],
        "summary": "Essential fat-soluble vitamin-hormone. Deficiency affects 40%+ of population globally. Regulates testosterone synthesis, immune function, and bone density.",
        "what_it_is": "Vitamin D3 (cholecalciferol) is a fat-soluble prohormone synthesised in skin on UV exposure. Functions as a hormone regulating 1,000+ genes. Vitamin K2 (MK-7) is required alongside D3 to direct calcium to bone and away from arteries. Deficiency is epidemic in office workers, those in northern latitudes, and darker-skinned individuals.",
        "dosage": "Vitamin D3: 2,000–5,000 IU/day. Vitamin K2 MK-7: 100–200 mcg/day. Test serum 25-OH-D to dial in personal dose.",
        "timing": "With largest fat-containing meal for optimal absorption.",
        "how_to_take": "Softgel capsule or oil drops. Take D3 + K2 in same capsule or same meal. Avoid taking with calcium supplements — K2 directs calcium correctly without excess supplementation.",
        "hydration": "Standard 2.5–3 L/day.",
        "training_synergy": "Adequate vitamin D supports testosterone production (+20% in deficient men), muscle contraction efficiency, and injury prevention via bone density.",
        "cycling": "Take year-round — dietary sources and sunlight rarely achieve optimal serum levels in training populations.",
        "benefits": ["Testosterone support", "Immune system regulation", "Bone density", "Mood improvement", "Muscle function"],
        "side_effects": [{"effect": "Toxicity only at >10,000 IU/day sustained without monitoring", "severity": "low"}],
        "stacking": ["Magnesium (required for D3 activation)", "Omega-3"],
        "final_recommendation": "Get serum 25-OH-D tested. Target 40–70 ng/mL. Adjust D3 dose accordingly. Take with K2 MK-7 daily.",
        "evidence_tier": "very_high",
        "safe_for_beginners": True,
        "pubmed_ids": ["21154195", "17556697"],
        "examine_url": "https://examine.com/supplements/vitamin-d/",
        "research_refs": ["Pilz et al. (2011) Horm Metab Res", "Holick (2007) NEJM — Vitamin D deficiency review"],
    },
]

# ── Alias index ────────────────────────────────────────────────────────────
_ALIAS: dict[str, dict] = {}
for _it in KB:
    _ALIAS[_it["name"].lower()] = _it
    for _a in _it.get("aliases", []):
        _ALIAS[_a.lower()] = _it

# ── Intent / synonym map ────────────────────────────────────────────────────
INTENT_MAP: dict[str, list[str]] = {
    "muscle gain": ["muscle_gain"], "build muscle": ["muscle_gain"], "bulk": ["muscle_gain"],
    "fat loss": ["fat_loss"], "lose weight": ["fat_loss"], "cut": ["fat_loss"],
    "strength": ["strength"], "power": ["strength"],
    "endurance": ["endurance"], "cardio": ["endurance"],
    "recovery": ["recovery"], "injury": ["recovery", "joint_health"],
    "pre workout": ["pre_workout"], "pump": ["pump"],
    "sarm": ["sarm"], "sarms": ["sarm"],
    "steroid": ["steroid"], "steroids": ["steroid"],
    "peptide": ["peptide"], "peptides": ["peptide"],
    "growth hormone": ["hgh"], "hgh": ["hgh"],
    "protein": ["muscle_gain", "recovery"],
    "dosage": [], "dose": [], "timing": [], "how to": [],
    "side effects": [], "risks": [], "cycle": [], "stack": [],
    "what is": [], "what are": [], "best": [], "safe": [], "beginner": [],
    "recommended": [], "research": [], "evidence": [],
}

MULTILINGUAL: dict[str, list[str]] = {
    "क्रिएटिन": ["creatine"], "मसल": ["muscle_gain"], "प्रोटीन": ["protein"],
    "ताकत": ["strength"], "वजन कम": ["fat_loss"],
    "creatina": ["creatine"], "músculo": ["muscle_gain"], "fuerza": ["strength"],
    "créatine": ["creatine"], "muscle": ["muscle_gain"], "force": ["strength"],
    "kreatin": ["creatine"], "muskel": ["muscle_gain"], "kraft": ["strength"],
    "мышцы": ["muscle_gain"], "сила": ["strength"], "жир": ["fat_loss"],
    "肌肉": ["muscle_gain"], "肌酸": ["creatine"], "力量": ["strength"],
}


# ═══════════════════════════════════════════════════════════════════════════
# CACHE  (SQLite — thread-safe)
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
    raw = json.dumps({"q": query.lower().strip(), "f": sorted(filters)})
    return hashlib.sha256(raw.encode()).hexdigest()[:32]


def _cache_get(key: str) -> list | None:
    try:
        with _cache_lock, sqlite3.connect(CACHE_DB) as conn:
            row = conn.execute(
                "SELECT report_json, created_at FROM report_cache WHERE cache_key=?", (key,)
            ).fetchone()
        if not row:
            return None
        age = time.time() - row[1]
        if age > CACHE_TTL_SEC:
            return None  # expired
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
            total    = conn.execute("SELECT COUNT(*) FROM report_cache").fetchone()[0]
            fresh    = conn.execute(
                "SELECT COUNT(*) FROM report_cache WHERE created_at > ?",
                (time.time() - CACHE_TTL_SEC,)
            ).fetchone()[0]
        return {"total": total, "fresh": fresh}
    except Exception:
        return {}


# ═══════════════════════════════════════════════════════════════════════════
# ENTITY DETECTION  (rule-based NLP)
# ═══════════════════════════════════════════════════════════════════════════

def _detect_entities(query: str) -> tuple[list[str], list[str], str]:
    """
    Returns (compounds, tags, intent_label).
    intent_label: explain | dosage | compare | cycle | side_effects | general
    """
    q = query.lower()
    compounds: list[str] = []
    tags: list[str]      = []

    # Alias matching
    for alias, item in _ALIAS.items():
        if alias in q:
            if item["name"] not in compounds:
                compounds.append(item["name"])
            tags.extend(item.get("tags", []))

    # Multilingual
    for word, wtags in MULTILINGUAL.items():
        if word in query:
            tags.extend(wtags)

    # Intent matching
    for phrase, ptags in INTENT_MAP.items():
        if phrase in q:
            tags.extend(ptags)

    # Word-level fuzzy
    for word in re.split(r"[\s\W]+", q):
        if len(word) < 3:
            continue
        for alias, item in _ALIAS.items():
            if word in alias and item["name"] not in compounds:
                compounds.append(item["name"])
                tags.extend(item.get("tags", []))

    # Intent label
    intent = "general"
    if any(w in q for w in ["dosage", "dose", "how much", "mg", "grams"]):
        intent = "dosage"
    elif any(w in q for w in ["side effect", "risk", "dangerous", "safe", "harm"]):
        intent = "side_effects"
    elif any(w in q for w in ["compare", "vs", "versus", "better", "difference"]):
        intent = "compare"
    elif any(w in q for w in ["cycle", "protocol", "pct", "stack"]):
        intent = "cycle"
    elif any(w in q for w in ["what is", "what are", "how does", "explain", "define"]):
        intent = "explain"
    elif any(w in q for w in ["best", "recommend", "should i", "beginner"]):
        intent = "recommend"

    return (
        list(dict.fromkeys(compounds)),
        list(dict.fromkeys(tags)),
        intent
    )


# ═══════════════════════════════════════════════════════════════════════════
# LIVE DATA RETRIEVAL
# ═══════════════════════════════════════════════════════════════════════════

# Trust tiers for evidence scoring
TRUST_TIERS = {
    "pubmed":        5,
    "clinicaltrials":4,
    "examine":       4,
    "openfda":       3,
    "jissn":         4,
    "ncbi":          5,
    "serp":          2,
    "scraped":       1,
}


def _pubmed_search(query: str, max_results: int = 5) -> list[dict]:
    """Search PubMed for peer-reviewed research. Returns structured reference list."""
    try:
        params: dict[str, Any] = {
            "db":      "pubmed",
            "term":    f"{query} supplement exercise",
            "retmax":  max_results,
            "retmode": "json",
            "sort":    "relevance",
        }
        if PUBMED_API_KEY:
            params["api_key"] = PUBMED_API_KEY

        r = requests.get(PUBMED_SEARCH, params=params, timeout=8)
        if r.status_code != 200:
            return []

        ids = r.json().get("esearchresult", {}).get("idlist", [])
        if not ids:
            return []

        # Fetch summaries
        params2: dict[str, Any] = {
            "db":      "pubmed",
            "id":      ",".join(ids),
            "retmode": "json",
            "rettype": "abstract",
        }
        if PUBMED_API_KEY:
            params2["api_key"] = PUBMED_API_KEY

        r2 = requests.get(PUBMED_FETCH, params=params2, timeout=10)
        if r2.status_code != 200:
            return [{"id": pid, "source": "pubmed", "trust": TRUST_TIERS["pubmed"],
                     "title": f"PubMed ID: {pid}", "url": f"https://pubmed.ncbi.nlm.nih.gov/{pid}/",
                     "snippet": ""} for pid in ids]

        articles = r2.json().get("result", {})
        refs = []
        for pid in ids:
            article = articles.get(pid, {})
            authors = article.get("authors", [])
            author_str = authors[0].get("name", "") + " et al." if authors else ""
            pubdate = article.get("pubdate", "")
            title   = article.get("title", f"PubMed ID: {pid}")
            journal = article.get("fulljournalname", "")
            refs.append({
                "id":      pid,
                "source":  "pubmed",
                "trust":   TRUST_TIERS["pubmed"],
                "title":   title,
                "authors": author_str,
                "journal": journal,
                "year":    pubdate[:4] if pubdate else "",
                "url":     f"https://pubmed.ncbi.nlm.nih.gov/{pid}/",
                "snippet": f"{author_str} {pubdate}. {journal}.",
            })
        return refs

    except Exception as e:
        print(f"[PubMed] {e}")
        return []


def _examine_data(compound_name: str) -> dict | None:
    """Attempt to retrieve structured data from Examine.com by scraping the supplement page."""
    try:
        slug = compound_name.lower().replace(" ", "-").replace("(", "").replace(")", "")
        url  = f"https://examine.com/supplements/{slug}/"
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; FitSearchBot/1.0; research purposes)"
        }
        r = requests.get(url, headers=headers, timeout=8)
        if r.status_code != 200:
            return None

        # Extract key structured data from Examine page
        text = r.text

        # Extract summary paragraph (first 500 chars of main content area)
        summary_match = re.search(
            r'<p[^>]*class="[^"]*summary[^"]*"[^>]*>(.*?)</p>', text, re.DOTALL | re.IGNORECASE
        )
        if not summary_match:
            summary_match = re.search(r'<meta[^>]*name="description"[^>]*content="([^"]{50,})"', text)

        summary = ""
        if summary_match:
            summary = re.sub(r"<[^>]+>", "", summary_match.group(1)).strip()[:500]

        return {
            "source":  "examine",
            "trust":   TRUST_TIERS["examine"],
            "url":     url,
            "summary": summary,
            "snippet": summary[:200] if summary else "",
        }
    except Exception as e:
        print(f"[Examine] {e}")
        return None


def _openfda_safety(compound_name: str) -> list[dict]:
    """Query OpenFDA for adverse event reports related to the compound."""
    try:
        r = requests.get(
            OPENFDA_URL,
            params={
                "search": f'patient.drug.medicinalproduct:"{compound_name}"',
                "limit":  3,
            },
            timeout=6,
        )
        if r.status_code != 200:
            return []
        results = r.json().get("results", [])
        events = []
        for ev in results[:3]:
            reactions = [
                r.get("reactionmeddrapt", "Unknown")
                for r in ev.get("patient", {}).get("reaction", [])[:3]
            ]
            events.append({
                "source":  "openfda",
                "trust":   TRUST_TIERS["openfda"],
                "reactions": reactions,
                "snippet": f"FDA adverse event report: {', '.join(reactions)}",
            })
        return events
    except Exception as e:
        print(f"[OpenFDA] {e}")
        return []


def _serp_search(query: str) -> list[dict]:
    """Live Google search via SerpAPI. Falls back gracefully if key not set."""
    if not SERP_API_KEY:
        return []
    try:
        r = requests.get(
            "https://serpapi.com/search.json",
            params={
                "q":       f"{query} site:examine.com OR site:pubmed.ncbi.nlm.nih.gov OR site:jissn.biomedcentral.com",
                "api_key": SERP_API_KEY,
                "engine":  "google",
                "num":     5,
                "hl":      "en",
            },
            timeout=8,
        )
        if r.status_code != 200:
            return []
        return [
            {
                "source":  "serp",
                "trust":   TRUST_TIERS["serp"],
                "title":   result.get("title", ""),
                "url":     result.get("link", ""),
                "snippet": result.get("snippet", ""),
            }
            for result in r.json().get("organic_results", [])[:5]
        ]
    except Exception as e:
        print(f"[SerpAPI] {e}")
        return []


def _retrieve_live_data(query: str, compounds: list[str]) -> dict:
    """
    Parallel live data retrieval from all configured sources.
    Returns merged evidence dictionary.
    """
    import concurrent.futures

    live: dict = {"pubmed": [], "examine": {}, "fda": [], "serp": []}

    primary = compounds[0] if compounds else query

    def run_pubmed():   return _pubmed_search(primary, 5)
    def run_examine():  return _examine_data(primary)
    def run_fda():      return _openfda_safety(primary)
    def run_serp():     return _serp_search(query)

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
        f_pub  = ex.submit(run_pubmed)
        f_exam = ex.submit(run_examine)
        f_fda  = ex.submit(run_fda)
        f_serp = ex.submit(run_serp)

        live["pubmed"]  = f_pub.result()
        live["examine"] = f_exam.result() or {}
        live["fda"]     = f_fda.result()
        live["serp"]    = f_serp.result()

    return live


def _filter_evidence(live: dict) -> dict:
    """
    Score and rank all retrieved evidence by trust tier.
    Discards low-quality / anecdotal sources.
    Returns filtered, sorted evidence.
    """
    all_items = []
    all_items.extend(live.get("pubmed",  []))
    all_items.extend(live.get("serp",    []))
    all_items.extend(live.get("fda",     []))
    if live.get("examine"):
        all_items.append(live["examine"])

    # Sort by trust, discard trust < 2
    filtered = sorted(
        [i for i in all_items if i.get("trust", 0) >= 2],
        key=lambda x: x.get("trust", 0),
        reverse=True
    )

    return {
        "high_trust": [i for i in filtered if i.get("trust", 0) >= 4],
        "medium_trust": [i for i in filtered if i.get("trust", 0) == 3],
        "pubmed_ids": [i["id"] for i in live.get("pubmed", []) if "id" in i],
        "examine_url": live.get("examine", {}).get("url"),
        "examine_summary": live.get("examine", {}).get("summary", ""),
        "fda_events": live.get("fda", []),
    }


# ═══════════════════════════════════════════════════════════════════════════
# CLAUDE LLM  — structured report generation
# ═══════════════════════════════════════════════════════════════════════════

_REPORT_SYSTEM_PROMPT = """You are FitSearch AI — a world-class evidence-based fitness and nutrition scientist.

Your job is to generate a structured 10-section research report answering the user's fitness query.

RULES:
1. Respond ONLY with valid JSON — no markdown fences, no prose outside JSON.
2. Respond in the SAME language as the user's query.
3. Be specific with dosages, timing, and practical tips.
4. safe_for_beginners must be false for steroids and most SARMs.
5. Include real PubMed IDs and reference links wherever possible.
6. evidence_tier: "very_high" | "high" | "moderate" | "low"
7. Include legal_status for any controlled/research substance.

Respond with this exact JSON structure:
{
  "detected_language": "English",
  "intent": "explain | recommend | dosage | compare | cycle | side_effects | general",
  "name": "Primary supplement/compound name",
  "tagline": "One-sentence description",
  "category": "supplement | sarm | steroid | peptide | training | diet",
  "evidence_tier": "very_high | high | moderate | low",
  "safe_for_beginners": true,
  "legal_status": "legal / prescription only / research chemical / banned — or null",
  "sections": {
    "what_it_is": "2-4 sentence explanation of mechanism and origin",
    "dosage": "Specific evidence-based dosage with loading/maintenance phases if applicable",
    "timing": "Optimal timing and why",
    "how_to_take": "Practical preparation and consumption tips",
    "hydration": "Fluid requirements and why",
    "training_synergy": "How to combine with training for maximum effect",
    "cycling": "Whether cycling is needed, and recommended protocol",
    "benefits": ["benefit 1", "benefit 2", "benefit 3"],
    "side_effects": [{"effect": "description", "severity": "low | medium | high"}],
    "references": [
      {"type": "pubmed", "id": "PMID", "title": "Study title", "url": "https://pubmed.ncbi.nlm.nih.gov/PMID/"},
      {"type": "examine", "url": "https://examine.com/supplements/compound/", "title": "Examine.com — Compound"}
    ]
  },
  "stacking": ["compound 1", "compound 2"],
  "final_recommendation": "2-3 sentence actionable recommendation",
  "ai_note": "brief note on confidence level based on available evidence"
}"""


def _call_claude(query: str, compounds: list[str], kb_items: list[dict], evidence: dict) -> dict | None:
    """Call Claude with query + KB data + live evidence to generate structured report."""
    if not ANTHROPIC_API_KEY:
        return None

    # Build evidence context for prompt
    pubmed_block = ""
    if evidence.get("pubmed_ids"):
        pubmed_block = f"\n\nLIVE PUBMED RESULTS:\n" + "\n".join(
            f"- PMID {pid}: https://pubmed.ncbi.nlm.nih.gov/{pid}/"
            for pid in evidence["pubmed_ids"][:5]
        )

    examine_block = ""
    if evidence.get("examine_url"):
        examine_block = f"\n\nEXAMINE.COM DATA:\nURL: {evidence['examine_url']}\nSummary: {evidence.get('examine_summary', '')[:300]}"

    fda_block = ""
    if evidence.get("fda_events"):
        reactions = [ev["reactions"] for ev in evidence["fda_events"][:2]]
        fda_block = f"\n\nFDA ADVERSE EVENTS:\n{json.dumps(reactions)}"

    kb_block = ""
    for item in kb_items[:3]:
        kb_block += f"\n\nKNOWLEDGE BASE ENTRY — {item['name']}:\n{json.dumps({k: v for k, v in item.items() if k not in ['aliases', 'id']}, ensure_ascii=False)[:1500]}"

    user_message = (
        f"User query: {query}\n"
        f"Detected compounds: {', '.join(compounds) if compounds else 'general fitness query'}\n"
        f"{kb_block}"
        f"{pubmed_block}"
        f"{examine_block}"
        f"{fda_block}"
    )

    try:
        resp = requests.post(
            ANTHROPIC_URL,
            headers={
                "x-api-key":         ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type":      "application/json",
            },
            json={
                "model":      "claude-sonnet-4-20250514",
                "max_tokens": 3000,
                "system":     _REPORT_SYSTEM_PROMPT,
                "messages":   [{"role": "user", "content": user_message}],
            },
            timeout=30,
        )
        resp.raise_for_status()
        text = resp.json()["content"][0]["text"].strip()
        # Strip markdown code fences if Claude adds them
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
        return json.loads(text)
    except Exception as e:
        print(f"[Claude] {e}")
        return None


# ═══════════════════════════════════════════════════════════════════════════
# KB SCORING  (offline)
# ═══════════════════════════════════════════════════════════════════════════

def _score_kb(query: str, compounds: list[str], tags: list[str], item: dict, filters: list[str]) -> int:
    q = query.lower()
    s = 0
    name     = item["name"].lower()
    aliases  = " ".join(item.get("aliases", []))
    summ     = item.get("summary", "").lower()
    itags    = " ".join(item.get("tags", []))

    for c in compounds:
        if c.lower() in name or name in c.lower():
            s += 25
    for t in tags:
        if t in itags:
            s += 6
    for word in re.split(r"[\s\W]+", q):
        if len(word) < 3:
            continue
        if word in name:    s += 10
        if word in aliases: s += 7
        if word in itags:   s += 4
        if word in summ:    s += 1
    if "beginner" in filters and item.get("safe_for_beginners"):
        s += 5
    for f in filters:
        if f in itags:
            s += 4
    return s


def _kb_results(query: str, compounds: list[str], tags: list[str], filters: list[str]) -> list[dict]:
    scored = [
        {**item, "_sc": _score_kb(query, compounds, tags, item, filters)}
        for item in KB
    ]
    scored = [r for r in scored if r["_sc"] > 0]
    scored.sort(key=lambda x: x["_sc"], reverse=True)
    return [{k: v for k, v in r.items() if k != "_sc"} for r in scored[:5]]


# ═══════════════════════════════════════════════════════════════════════════
# REPORT ASSEMBLY  — convert Claude/KB data → frontend format
# ═══════════════════════════════════════════════════════════════════════════

def _kb_to_report(item: dict, live_evidence: dict) -> dict:
    """
    Convert a local KB item into the full 10-section report format.
    Used when Claude is unavailable.
    """
    sections = {
        "what_it_is":      item.get("what_it_is", item.get("summary", "")),
        "dosage":          item.get("dosage", "—"),
        "timing":          item.get("timing", "—"),
        "how_to_take":     item.get("how_to_take", "Mix with water or a protein shake."),
        "hydration":       item.get("hydration", "Maintain 2.5–3 L/day water intake."),
        "training_synergy":item.get("training_synergy", "Most effective combined with progressive-overload resistance training."),
        "cycling":         item.get("cycling", "No cycling required."),
        "benefits":        item.get("benefits", []),
        "side_effects":    item.get("side_effects", []),
        "references": [],
    }

    # Attach live PubMed references
    for pid in (live_evidence.get("pubmed_ids") or item.get("pubmed_ids", []))[:5]:
        sections["references"].append({
            "type":  "pubmed",
            "id":    pid,
            "title": f"PubMed ID: {pid}",
            "url":   f"https://pubmed.ncbi.nlm.nih.gov/{pid}/",
        })

    # Attach static KB references
    for ref in item.get("research_refs", []):
        sections["references"].append({
            "type":  "journal",
            "id":    None,
            "title": ref,
            "url":   None,
        })

    # Examine.com link
    if item.get("examine_url") or live_evidence.get("examine_url"):
        exam_url = item.get("examine_url") or live_evidence.get("examine_url")
        sections["references"].append({
            "type":  "examine",
            "id":    None,
            "title": f"Examine.com — {item['name']}",
            "url":   exam_url,
        })

    return {
        "name":                item["name"],
        "tagline":             item.get("summary", "")[:120],
        "category":            item.get("category", "supplement"),
        "evidence_tier":       item.get("evidence_tier", "moderate"),
        "safe_for_beginners":  item.get("safe_for_beginners", True),
        "legal_status":        item.get("legal_status"),
        "sections":            sections,
        "stacking":            item.get("stacking", []),
        "final_recommendation":item.get("final_recommendation", ""),
        "ai_note":             "Report generated from curated knowledge base. For most recent research, set ANTHROPIC_API_KEY.",
        "_source":             "kb",
    }


def _claude_to_report(ai_data: dict, live_evidence: dict) -> dict:
    """Normalise Claude's JSON output into the standard report format."""
    sections = ai_data.get("sections", {})

    # Merge live PubMed IDs into references if not already included
    existing_ids = {r.get("id") for r in sections.get("references", [])}
    for pid in live_evidence.get("pubmed_ids", []):
        if pid not in existing_ids:
            sections.setdefault("references", []).append({
                "type":  "pubmed",
                "id":    pid,
                "title": f"PubMed ID: {pid}",
                "url":   f"https://pubmed.ncbi.nlm.nih.gov/{pid}/",
            })

    if live_evidence.get("examine_url"):
        sections.setdefault("references", []).append({
            "type":  "examine",
            "id":    None,
            "title": f"Examine.com — {ai_data.get('name', 'Supplement')}",
            "url":   live_evidence["examine_url"],
        })

    return {
        "name":                ai_data.get("name", "Supplement"),
        "tagline":             ai_data.get("tagline", ""),
        "category":            ai_data.get("category", "supplement"),
        "evidence_tier":       ai_data.get("evidence_tier", "moderate"),
        "safe_for_beginners":  ai_data.get("safe_for_beginners", True),
        "legal_status":        ai_data.get("legal_status"),
        "sections":            sections,
        "stacking":            ai_data.get("stacking", []),
        "final_recommendation":ai_data.get("final_recommendation", ""),
        "ai_note":             ai_data.get("ai_note", "AI-generated report."),
        "_source":             "ai",
    }


# ═══════════════════════════════════════════════════════════════════════════
# PUBLIC INTERFACE
# ═══════════════════════════════════════════════════════════════════════════

def search_knowledge(query: str, filters: list | None = None) -> list[dict]:
    """
    Main entry point called by app.py /search route.

    Returns a list of structured 10-section reports.
    Each report has sections: what_it_is, dosage, timing, how_to_take,
    hydration, training_synergy, cycling, benefits, side_effects, references.
    """
    filters = filters or []
    ts      = datetime.now(timezone.utc).isoformat()

    # 1. Check cache
    ckey = _cache_key(query, filters)
    cached = _cache_get(ckey)
    if cached:
        for r in cached:
            r["_cached"] = True
        return cached

    # 2. Entity detection
    compounds, tags, intent = _detect_entities(query)

    # 3. KB lookup
    kb_matches = _kb_results(query, compounds, tags, filters)

    # 4. Live data retrieval (parallel)
    live = _retrieve_live_data(query, compounds)

    # 5. Evidence filtering
    evidence = _filter_evidence(live)

    # 6. Claude call
    ai_data = _call_claude(query, compounds, kb_matches, evidence)

    results: list[dict] = []

    if ai_data and ai_data.get("sections"):
        # AI report is primary result
        report = _claude_to_report(ai_data, evidence)
        report["_timestamp"] = ts
        results.append(report)

        # Append additional KB results as supplementary cards
        for item in kb_matches[1:3]:
            if item["name"].lower() != ai_data.get("name", "").lower():
                r = _kb_to_report(item, {})
                r["_timestamp"] = ts
                r["_supplementary"] = True
                results.append(r)

    else:
        # Fallback: build reports from KB only
        for item in kb_matches[:4]:
            r = _kb_to_report(item, evidence if not results else {})
            r["_timestamp"] = ts
            results.append(r)

    if not results:
        results = [_fallback_report(query, ts)]

    # 7. Cache results
    _cache_set(ckey, query, results, source="ai" if ai_data else "kb")

    return results


def get_recommendations(recent_queries: list[str], user: dict) -> list[dict]:
    """Personalised recommendations based on user history. No API calls."""
    goal  = (user.get("goal") or "muscle_gain").replace("-", "_")
    level = user.get("experience_level") or "beginner"

    seen: set[str] = set()
    for q in recent_queries:
        comps, _, _ = _detect_entities(q)
        for c in comps:
            m = _ALIAS.get(c.lower())
            if m:
                seen.add(m["id"])

    recs = []
    for item in KB:
        if item["id"] in seen:
            continue
        sc = 0
        if goal in item.get("tags", []):         sc += 4
        if item.get("safe_for_beginners") and level == "beginner": sc += 3
        if not item.get("safe_for_beginners") and level in ("intermediate", "advanced"): sc += 2
        if item["evidence_tier"] in ("very_high", "high"):         sc += 1
        if sc <= 1:
            continue
        parts = [f"Matches your {goal.replace('_', ' ')} goal"]
        if level == "beginner" and item.get("safe_for_beginners"):
            parts.append("beginner-friendly")
        if item["evidence_tier"] in ("very_high", "high"):
            parts.append("strong research support")
        recs.append({**item, "_sc": sc, "recommendation_reason": " · ".join(parts)})

    recs.sort(key=lambda x: x["_sc"], reverse=True)
    return [{k: v for k, v in r.items() if k != "_sc"} for r in recs[:6]]


def _fallback_report(query: str, ts: str) -> dict:
    return {
        "name":    f"Search: {query}",
        "tagline": "No exact match found.",
        "category": "supplement",
        "evidence_tier": "moderate",
        "safe_for_beginners": True,
        "legal_status": None,
        "sections": {
            "what_it_is": (
                f"No specific results found for '{query}'. "
                "Try searching: Creatine monohydrate, Whey protein, Beta-alanine, "
                "Ostarine, Testosterone enanthate, BPC-157, HGH, Vitamin D3, Caffeine."
            ),
            "dosage": "—", "timing": "—", "how_to_take": "—",
            "hydration": "—", "training_synergy": "—", "cycling": "—",
            "benefits": [], "side_effects": [],
            "references": [
                {"type": "examine", "url": "https://examine.com", "title": "Examine.com — Supplement Database", "id": None},
                {"type": "pubmed",  "url": "https://pubmed.ncbi.nlm.nih.gov", "title": "PubMed — Research Database", "id": None},
            ],
        },
        "stacking": [],
        "final_recommendation": "Refine your query with a specific supplement, compound, or topic.",
        "ai_note": "No match in knowledge base or live retrieval.",
        "_source": "fallback",
        "_timestamp": ts,
    }
