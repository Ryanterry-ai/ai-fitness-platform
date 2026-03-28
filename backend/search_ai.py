"""
search_ai.py
============
Real-time, multilingual, NLP-powered search engine for FitSearch AI Platform.

Architecture (3 layers, executed in order of availability):
  Layer 1 → Anthropic Claude API   — NLP understanding + structured AI answer
  Layer 2 → SerpAPI                — Live Google web results
  Layer 3 → Local Knowledge Base   — Curated offline fallback (zero API keys needed)

Supported languages : ALL languages (Claude handles translation internally)
Natural language    : YES — "What are SARMs", "Best creatine for strength",
                            "क्रिएटिन के फायदे", "Créatine pour la force" all work

Environment variables (set in Render dashboard):
  ANTHROPIC_API_KEY   — Claude API key for NLP + AI answers
  SERP_API_KEY        — SerpAPI key for real-time Google results (optional)
"""

from __future__ import annotations
import os, json, re, requests
from datetime import datetime, timezone

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
SERP_API_KEY      = os.getenv("SERP_API_KEY", "")

ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
SERP_URL      = "https://serpapi.com/search.json"


# ═══════════════════════════════════════════════════════════════════════════
# LOCAL KNOWLEDGE BASE  — offline fallback, always works
# ═══════════════════════════════════════════════════════════════════════════

KB = [
    {
        "id": "crm_mono",
        "name": "Creatine monohydrate",
        "aliases": ["creatine", "kreatin", "creatina", "creatine monohydrate", "créatine",
                    "creatina monoidrata", "creatina monohidrato", "kreatin monohidrat", "क्रिएटिन", "肌酸"],
        "category": "supplement",
        "tags": ["strength", "muscle_gain", "power", "beginner", "best", "creatine"],
        "summary": "The most extensively researched ergogenic aid in sports science. Increases phosphocreatine stores in muscle, directly fuelling ATP regeneration during high-intensity efforts. Produces consistent strength and power gains across all training levels with no cycling required.",
        "dosage": "3–5 g/day (loading optional: 20 g/day × 5 days then 3–5 g maintenance)",
        "timing": "Post-workout or any time of day — consistency matters more than timing",
        "benefits": ["Strength increase 5–15%", "Power output improvement", "Faster recovery between sets", "Lean mass support", "Cognitive performance support"],
        "side_effects": [{"effect": "Water retention (mild, intracellular)", "severity": "low"}, {"effect": "GI discomfort if taking full dose at once during loading", "severity": "medium"}],
        "stacking": ["Beta-alanine", "Caffeine", "Whey protein"],
        "evidence_tier": "very_high",
        "safe_for_beginners": True,
        "research_refs": ["Buford et al. (2007) ISSN Creatine Position Stand", "Rawson & Volek (2003) JSCR meta-analysis"],
    },
    {
        "id": "crm_hcl",
        "name": "Creatine HCL",
        "aliases": ["creatine hcl", "creatine hydrochloride", "hcl creatine", "con-cret"],
        "category": "supplement",
        "tags": ["strength", "muscle_gain", "creatine", "no bloating"],
        "summary": "Hydrochloride salt of creatine with higher water solubility, allowing effective doses of 1–2 g vs 3–5 g for monohydrate. Reported to cause less bloating. Clinical evidence is comparable but the research body is much smaller than monohydrate.",
        "dosage": "1–2 g/day, no loading phase needed",
        "timing": "Pre or post-workout",
        "benefits": ["Minimal water retention and bloating", "Easy to dissolve in water", "Equivalent strength gains at lower dose", "Good for GI-sensitive individuals"],
        "side_effects": [{"effect": "Minimal GI issues", "severity": "low"}],
        "stacking": ["Citrulline malate", "Beta-alanine"],
        "evidence_tier": "high",
        "safe_for_beginners": True,
        "research_refs": ["Miller et al. (2009) J Int Soc Sports Nutr"],
    },
    {
        "id": "beta_al",
        "name": "Beta-alanine",
        "aliases": ["beta alanine", "beta-alanine", "carnosine precursor", "tingling supplement", "beta alanina"],
        "category": "supplement",
        "tags": ["endurance", "strength", "fatigue", "pre_workout"],
        "summary": "Amino acid that combines with histidine to form carnosine in muscle, acting as a pH buffer to delay lactic acid buildup and fatigue. Most effective for exercise lasting 60–240 seconds (high-rep training, rowing, cycling).",
        "dosage": "3.2–6.4 g/day — split into 1.6 g doses throughout the day to minimise tingling",
        "timing": "Pre-workout or split across the day; tingling (paresthesia) is harmless",
        "benefits": ["Delayed muscle fatigue and lactic acid buildup", "Higher rep capacity before failure", "Endurance improvement in 1–4 minute efforts", "Synergy with creatine for full energy system coverage"],
        "side_effects": [{"effect": "Tingling / paresthesia — harmless, dose-dependent", "severity": "low"}],
        "stacking": ["Creatine monohydrate", "Caffeine", "L-Citrulline"],
        "evidence_tier": "high",
        "safe_for_beginners": True,
        "research_refs": ["Hobson et al. (2012) Amino Acids — 15-study meta-analysis"],
    },
    {
        "id": "citrulline",
        "name": "L-Citrulline / Citrulline malate",
        "aliases": ["citrulline", "citrulline malate", "l-citrulline", "nitric oxide supplement",
                    "pump supplement", "no booster", "citrulina", "citrulline malate 2:1"],
        "category": "supplement",
        "tags": ["pump", "endurance", "blood_flow", "fat_loss", "pre_workout", "nitric oxide"],
        "summary": "Converted to arginine in the kidneys, then to nitric oxide, causing vasodilation and the muscle pump effect. Citrulline malate (2:1 ratio) also reduces fatigue via malate's role in the Krebs cycle. One of the most evidence-backed pre-workout ingredients.",
        "dosage": "6–8 g L-citrulline or 8 g citrulline malate 2:1 ratio",
        "timing": "30–60 minutes pre-workout on an empty stomach for best absorption",
        "benefits": ["Significant muscle pump and vasodilation", "Reduced fatigue in high-volume training", "Blood pressure support", "Endurance improvement by 12–15%"],
        "side_effects": [{"effect": "GI discomfort at doses above 10 g", "severity": "low"}],
        "stacking": ["Beta-alanine", "Caffeine", "Creatine monohydrate"],
        "evidence_tier": "high",
        "safe_for_beginners": True,
        "research_refs": ["Pérez-Guisado & Jakeman (2010) JSCR", "Suzuki et al. (2016) Eur J Nutr"],
    },
    {
        "id": "whey",
        "name": "Whey protein",
        "aliases": ["whey", "whey protein", "proteina whey", "proteine whey", "proteína whey",
                    "व्हे प्रोटीन", "乳清蛋白", "protéine lactosérum", "molkenprotein", "proteina del siero"],
        "category": "supplement",
        "tags": ["muscle_gain", "recovery", "protein", "beginner", "best"],
        "summary": "Fast-digesting complete protein derived from milk with the highest leucine content of any protein source (approximately 10–11% leucine). Leucine is the primary trigger for muscle protein synthesis. The most evidence-backed protein supplement for muscle gain and recovery.",
        "dosage": "25–50 g per serving as needed to reach total daily target of 1.6–2.2 g/kg bodyweight",
        "timing": "Post-workout for peak MPS stimulus; any time of day to supplement dietary protein",
        "benefits": ["Maximises muscle protein synthesis via high leucine content", "Fast absorption ideal post-workout", "Complete amino acid profile", "Supports both muscle gain and fat loss", "Convenient and cost-effective protein source"],
        "side_effects": [{"effect": "GI issues if lactose intolerant — use whey isolate instead", "severity": "medium"}],
        "stacking": ["Creatine monohydrate", "Carbohydrates post-workout for insulin spike", "Casein protein before bed"],
        "evidence_tier": "very_high",
        "safe_for_beginners": True,
        "research_refs": ["Tang et al. (2009) Am J Clin Nutr", "Phillips & Van Loon (2011) JSCR review"],
    },
    {
        "id": "caffeine",
        "name": "Caffeine",
        "aliases": ["caffeine", "caffeina", "caféine", "koffein", "कैफीन", "咖啡因",
                    "caffeine anhydrous", "caffeine pills"],
        "category": "supplement",
        "tags": ["strength", "endurance", "fat_loss", "focus", "pre_workout", "energy"],
        "summary": "The most studied ergogenic aid in sports science with over 100 clinical trials. Blocks adenosine receptors to reduce perceived exertion, increases power output, and enhances fat oxidation. Effective for endurance, strength, power, and team sports.",
        "dosage": "3–6 mg/kg body weight (200–400 mg for most adults) pre-workout",
        "timing": "30–60 minutes before training; avoid within 6 hours of sleep to protect sleep quality",
        "benefits": ["Power output improvement +3–7%", "Endurance capacity improvement", "Fat oxidation / thermogenic effect", "Focus, reaction time and alertness", "Reduced perceived effort"],
        "side_effects": [{"effect": "Tolerance buildup with daily use — cycle off 1–2 weeks monthly", "severity": "medium"}, {"effect": "Sleep disruption if dosed too late", "severity": "medium"}, {"effect": "Anxiety and elevated heart rate at high doses", "severity": "medium"}],
        "stacking": ["L-Theanine 200 mg (2:1 ratio for focus without jitters)", "L-Citrulline", "Beta-alanine"],
        "evidence_tier": "very_high",
        "safe_for_beginners": True,
        "research_refs": ["Grgic et al. (2021) BJSM — 300+ study meta-analysis", "Astorino & Roberson (2010) JSCR"],
    },
    {
        "id": "casein",
        "name": "Casein protein",
        "aliases": ["casein", "slow protein", "night protein", "micellar casein", "casein protein powder"],
        "category": "supplement",
        "tags": ["muscle_gain", "recovery", "protein", "anti_catabolic", "night"],
        "summary": "Slow-digesting milk protein that gels in the stomach to provide a sustained 5–7 hour release of amino acids. Ideal before sleep to maximise overnight muscle protein synthesis and prevent catabolism. Complements whey protein perfectly — whey post-workout, casein before bed.",
        "dosage": "30–40 g before bed",
        "timing": "30–60 minutes before sleep",
        "benefits": ["Anti-catabolic protection overnight for 5–7 hours", "Sustained amino acid release vs whey spike", "High leucine content comparable to whey", "Satiety improvement — reduces late-night hunger"],
        "side_effects": [{"effect": "GI discomfort if lactose intolerant", "severity": "medium"}],
        "stacking": ["ZMA / Magnesium", "Melatonin 0.5–1 mg"],
        "evidence_tier": "high",
        "safe_for_beginners": True,
        "research_refs": ["Res et al. (2012) Med Sci Sports Exerc", "Snijders et al. (2015) JNBS"],
    },
    {
        "id": "bcaa",
        "name": "BCAAs (Branched Chain Amino Acids)",
        "aliases": ["bcaa", "bcaas", "branched chain amino acids", "leucine isoleucine valine",
                    "amino acids", "eaa", "essential amino acids"],
        "category": "supplement",
        "tags": ["muscle_gain", "recovery", "anti_catabolic", "fasting", "intra_workout"],
        "summary": "Leucine, isoleucine, and valine — the three branched-chain essential amino acids. Most effective during fasted training or when total daily protein intake is below 1.6 g/kg. Largely redundant if you're consuming adequate total protein. Leucine (2.5 g+) is the primary trigger for MPS.",
        "dosage": "5–10 g per serving; 2:1:1 leucine:isoleucine:valine ratio is standard",
        "timing": "Intra-workout or during fasted morning training",
        "benefits": ["Muscle protein synthesis stimulation via leucine", "Anti-catabolic during fasted training", "Reduced DOMS and muscle soreness", "Prevent muscle breakdown during calorie deficit"],
        "side_effects": [{"effect": "Largely redundant — inefficient if whole protein intake is adequate", "severity": "low"}],
        "stacking": ["Whey protein", "Glutamine"],
        "evidence_tier": "moderate",
        "safe_for_beginners": True,
        "research_refs": ["Wolfe (2017) J Int Soc Sports Nutr", "Jackman et al. (2017) Front Physiol"],
    },
    {
        "id": "fat_burner_stack",
        "name": "Fat burner supplements",
        "aliases": ["fat burner", "fat burning supplement", "weight loss supplement", "thermogenic",
                    "fat loss supplement", "metabolism booster", "weight loss pills", "quemagrasas",
                    "brûleur de graisses", "fettverbrenner"],
        "category": "supplement",
        "tags": ["fat_loss", "cutting", "weight_loss", "thermogenic", "metabolism"],
        "summary": "Evidence-based fat loss supplements include: Caffeine (thermogenic, raises metabolic rate 3–11%), L-Carnitine (transports fatty acids to mitochondria for oxidation), Green tea extract / EGCG (catechin-caffeine synergy), Yohimbine (alpha-2 receptor antagonist, requires fasted state to work), and Synephrine / p-synephrine (bitter orange, milder stimulant than ephedrine).",
        "dosage": "Caffeine 200 mg, L-Carnitine 2–4 g, Green tea extract 400 mg EGCG, Yohimbine 2.5–20 mg, Synephrine 20–50 mg",
        "timing": "Fasted or pre-workout; yohimbine specifically requires fasted state to work via alpha-2 blockade",
        "benefits": ["Increased resting metabolic rate", "Improved fat oxidation during exercise", "Appetite suppression", "Energy boost for training in a deficit"],
        "side_effects": [{"effect": "Anxiety, elevated heart rate, and blood pressure", "severity": "medium"}, {"effect": "Yohimbine: severe anxiety in sensitive individuals — start at 2.5 mg", "severity": "high"}],
        "stacking": ["High protein diet (2–2.4 g/kg)", "Calorie deficit (500 kcal/day)", "Resistance training to preserve muscle"],
        "evidence_tier": "moderate",
        "safe_for_beginners": True,
        "research_refs": ["Westerterp-Plantenga et al. (2006) Obesity Reviews", "Stohs et al. (2011) Int J Med Sci"],
    },
    {
        "id": "pre_workout",
        "name": "Pre-workout supplements",
        "aliases": ["pre workout", "pre-workout", "preworkout", "pre workout supplement",
                    "pump formula", "training supplement", "pre workout formula", "pré workout"],
        "category": "supplement",
        "tags": ["pre_workout", "energy", "pump", "strength", "endurance", "focus"],
        "summary": "Multi-ingredient pre-workout formulas. Best ingredients with research support: Caffeine (3–6 mg/kg for energy), L-Citrulline 6–8 g (pump and endurance), Beta-alanine 3.2 g (fatigue delay), Creatine 3–5 g (strength), L-Theanine 200 mg (smooth focus without jitters). Many commercial products are under-dosed — always check ingredient amounts.",
        "dosage": "Verify key ingredient doses: Citrulline 6–8g, Caffeine 150–300mg, Beta-alanine 3.2g, Creatine 3–5g",
        "timing": "20–45 minutes before training",
        "benefits": ["Increased energy and mental focus", "Enhanced muscle pump via NO production", "Improved muscular endurance", "Strength output boost", "Motivation and training intensity"],
        "side_effects": [{"effect": "Jitteriness and anxiety if caffeine-sensitive", "severity": "medium"}, {"effect": "Energy crash post-training with stimulant-heavy formulas", "severity": "low"}, {"effect": "Tolerance builds quickly — cycle every 4–6 weeks", "severity": "medium"}],
        "stacking": ["Creatine (if not in formula)", "Electrolytes for hydration"],
        "evidence_tier": "high",
        "safe_for_beginners": True,
        "research_refs": ["Campbell et al. (2013) JISSN", "Jagim et al. (2016) JISSN"],
    },
    {
        "id": "vitamin_d",
        "name": "Vitamin D3 + K2",
        "aliases": ["vitamin d", "vitamin d3", "cholecalciferol", "vit d", "sunshine vitamin",
                    "vitamina d", "vitamine d", "विटामिन डी"],
        "category": "supplement",
        "tags": ["health", "testosterone", "immune", "bone", "recovery", "foundation"],
        "summary": "Vitamin D3 deficiency affects over 40% of the global population. It functions as a hormone regulating over 1,000 genes including those controlling testosterone synthesis. D3 + K2 (MK-7) is the optimal combination — K2 directs calcium to bones and away from arteries. Critical for athletes and anyone training hard.",
        "dosage": "Vitamin D3: 2,000–5,000 IU/day; Vitamin K2 MK-7: 100–200 mcg/day",
        "timing": "With a fat-containing meal for optimal fat-soluble vitamin absorption",
        "benefits": ["Testosterone support (+20% in deficient individuals)", "Immune system function", "Bone density and fracture prevention", "Mood improvement and depression reduction", "Cardiovascular and muscle function"],
        "side_effects": [{"effect": "Toxicity risk only at sustained doses above 10,000 IU/day without monitoring", "severity": "low"}],
        "stacking": ["Magnesium (required for D3 metabolism)", "Omega-3 fish oil"],
        "evidence_tier": "very_high",
        "safe_for_beginners": True,
        "research_refs": ["Pilz et al. (2011) Hormone & Metabolic Research", "Holick (2007) NEJM review"],
    },
    {
        "id": "omega3",
        "name": "Omega-3 fish oil (EPA + DHA)",
        "aliases": ["omega 3", "fish oil", "omega-3", "epa dha", "fatty acids", "omega 3 fish oil",
                    "aceite de pescado", "huile de poisson", "फिश ऑयल"],
        "category": "supplement",
        "tags": ["health", "recovery", "anti_inflammatory", "cardiovascular", "joint_health", "foundation"],
        "summary": "EPA and DHA are omega-3 long-chain fatty acids with powerful anti-inflammatory effects. Reduce exercise-induced inflammation, improve cardiovascular markers (triglycerides, HDL), support joint health, and modestly enhance muscle protein synthesis. Critically important for steroid users who experience significant cardiovascular strain.",
        "dosage": "3–6 g combined EPA + DHA per day (check label — NOT total oil volume, which includes inactive fats)",
        "timing": "With meals to reduce GI discomfort and fish aftertaste",
        "benefits": ["Systemic anti-inflammatory action", "Cardiovascular protection (HDL up, triglycerides down)", "Joint health and pain reduction", "Muscle protein synthesis support", "Brain and mood support"],
        "side_effects": [{"effect": "Fish aftertaste / burping — take with meals or use enteric-coated", "severity": "low"}, {"effect": "Very mild blood-thinning at doses above 5 g/day", "severity": "low"}],
        "stacking": ["Vitamin D3/K2", "Curcumin (anti-inflammatory synergy)"],
        "evidence_tier": "very_high",
        "safe_for_beginners": True,
        "research_refs": ["Smith et al. (2011) JCEM", "Calder (2013) Am J Clin Nutr review"],
    },
    {
        "id": "zinc_magnesium",
        "name": "Zinc & Magnesium (ZMA)",
        "aliases": ["zma", "zinc magnesium", "zinc", "magnesium", "mineral supplements",
                    "magnesium glycinate", "zinc picolinate"],
        "category": "supplement",
        "tags": ["testosterone", "sleep", "recovery", "health", "foundation"],
        "summary": "Zinc is essential for testosterone synthesis, immune function, and protein synthesis — athletes commonly lose zinc in sweat. Magnesium improves sleep architecture, reduces cortisol, and supports over 300 enzymatic reactions including energy production. Deficiencies in both are widespread in training populations.",
        "dosage": "Zinc: 25–45 mg/day (picolinate or citrate form); Magnesium: 300–500 mg glycinate or malate",
        "timing": "Before bed on empty stomach for optimal testosterone and sleep hormone effects",
        "benefits": ["Testosterone support (especially when deficient)", "Sleep quality and depth improvement", "Cortisol reduction", "Immune function support", "Muscle function and recovery"],
        "side_effects": [{"effect": "Nausea if zinc taken without food", "severity": "low"}, {"effect": "GI upset (diarrhoea) at high magnesium doses — use glycinate form", "severity": "low"}],
        "stacking": ["Vitamin D3", "Ashwagandha (cortisol and testosterone)"],
        "evidence_tier": "high",
        "safe_for_beginners": True,
        "research_refs": ["Prasad et al. (1996) Nutrition", "Brilla & Conte (2000) Agric Med"],
    },
    {
        "id": "ostarine",
        "name": "Ostarine (MK-2866)",
        "aliases": ["ostarine", "mk2866", "mk-2866", "enobosarm", "gtx-024", "ostarina",
                    "mk 2866", "ostarine mk 2866"],
        "category": "sarm",
        "tags": ["muscle_gain", "fat_loss", "recomp", "beginner_sarm", "sarm"],
        "summary": "The mildest and most clinically studied SARM. Selectively binds androgen receptors in muscle and bone with minimal androgenic activity elsewhere. Commonly used for body recomposition and as a first SARM. Still causes testosterone suppression and is a research chemical not approved for human use.",
        "dosage": "10–25 mg/day for 8 weeks",
        "timing": "Once daily, same time each day, with or without food",
        "benefits": ["Lean muscle gain (2–4 kg typical in 8 weeks)", "Fat loss support during recomp", "Joint support and injury healing", "Lower suppression than steroids", "Improved body composition without water retention"],
        "side_effects": [{"effect": "Mild testosterone suppression — bloodwork required", "severity": "medium"}, {"effect": "Lipid changes (HDL reduction, LDL increase)", "severity": "medium"}, {"effect": "Mild liver enzyme elevation", "severity": "low"}],
        "stacking": ["Cardarine GW-501516 (fat loss)", "MK-677 Ibutamoren (GH and recovery)"],
        "cycle_length": "8 weeks",
        "pct_needed": "Optional mini PCT — Nolvadex 20 mg/day × 3 weeks if suppression symptoms arise",
        "evidence_tier": "moderate",
        "safe_for_beginners": True,
        "legal_status": "Research chemical — not approved for human use in any country. Banned by WADA in sport.",
        "research_refs": ["Dalton et al. (2011) Cancer Research", "Papanicolaou et al. (2013) J Gerontol"],
    },
    {
        "id": "lgd4033",
        "name": "LGD-4033 (Ligandrol)",
        "aliases": ["lgd4033", "lgd-4033", "ligandrol", "vk5211", "anabolicum", "lgd 4033"],
        "category": "sarm",
        "tags": ["muscle_gain", "strength", "bulking", "sarm"],
        "summary": "The most anabolic SARM available with strength and mass gains approaching low-dose testosterone. Produces 3–5 kg lean mass gains in 8–12 weeks at 5–10 mg/day. Significant testosterone suppression occurs and requires full PCT. Not suitable for beginners.",
        "dosage": "5–10 mg/day for 8–12 weeks",
        "timing": "Once daily, same time each day",
        "benefits": ["3–5 kg lean mass gains typical in 8–12 weeks", "Major strength increase", "Improved recovery and training volume capacity"],
        "side_effects": [{"effect": "Significant testosterone suppression — bloodwork mandatory", "severity": "high"}, {"effect": "HDL reduction — cardiovascular risk", "severity": "high"}, {"effect": "Potential liver enzyme elevation", "severity": "medium"}],
        "stacking": ["MK-677 Ibutamoren", "Cardarine GW-501516"],
        "cycle_length": "8–12 weeks",
        "pct_needed": "Full SERM PCT required — Nolvadex 40/20/20/20 mg or Clomid 50/25/25/25 mg over 4 weeks",
        "evidence_tier": "moderate",
        "safe_for_beginners": False,
        "legal_status": "Research chemical — not approved for human use. Banned by WADA. Triggered anti-doping violations in athletes.",
        "research_refs": ["Basaria et al. (2013) Lancet — phase I trial"],
    },
    {
        "id": "rad140",
        "name": "RAD-140 (Testolone)",
        "aliases": ["rad140", "rad-140", "testolone", "rad 140"],
        "category": "sarm",
        "tags": ["muscle_gain", "strength", "fat_loss", "sarm"],
        "summary": "One of the most potent SARMs with the highest anabolic:androgenic ratio. Produces significant lean mass and strength gains. Strong testosterone suppression and hepatotoxicity (liver damage) have been reported in case studies. Not suitable for beginners.",
        "dosage": "5–15 mg/day for 8–10 weeks",
        "timing": "Once daily",
        "benefits": ["High anabolic potency", "Lean mass gains", "Fat loss support", "Neuroprotective effects in early research"],
        "side_effects": [{"effect": "Strong testosterone suppression — requires bloodwork", "severity": "high"}, {"effect": "Aggression and mood changes", "severity": "medium"}, {"effect": "Hepatotoxicity — liver damage in case reports", "severity": "high"}],
        "cycle_length": "8–10 weeks",
        "pct_needed": "Full PCT mandatory",
        "evidence_tier": "low",
        "safe_for_beginners": False,
        "legal_status": "Research chemical — not approved for human use. Banned by WADA.",
        "research_refs": ["Jayaraman et al. (2014) Endocrinology", "FDA safety warning 2017"],
    },
    {
        "id": "mk677",
        "name": "MK-677 (Ibutamoren)",
        "aliases": ["mk677", "mk-677", "ibutamoren", "nutrobal", "gh secretagogue", "mk 677"],
        "category": "sarm",
        "tags": ["muscle_gain", "fat_loss", "recovery", "hgh", "sleep", "sarm", "growth hormone"],
        "summary": "Oral growth hormone secretagogue that stimulates the pituitary to release GH and raise IGF-1 levels. Not technically a SARM but grouped with them. Non-suppressive of testosterone. Improves sleep quality, lean mass, recovery, and reduces body fat. Long half-life enables once-daily dosing.",
        "dosage": "10–25 mg/day",
        "timing": "Before bed to align with and amplify the natural overnight GH pulse",
        "benefits": ["Elevated GH and IGF-1 levels", "Lean mass gain", "Significantly improved sleep depth and quality", "Joint and recovery support", "Skin and collagen improvement"],
        "side_effects": [{"effect": "Increased appetite — challenging in fat loss phase", "severity": "medium"}, {"effect": "Water retention (mild)", "severity": "medium"}, {"effect": "Elevated fasting blood glucose / insulin resistance", "severity": "medium"}],
        "cycle_length": "12–24 weeks (long-term use common)",
        "pct_needed": "No PCT needed — non-suppressive of testosterone",
        "evidence_tier": "moderate",
        "safe_for_beginners": True,
        "legal_status": "Research chemical — not approved for human use",
        "research_refs": ["Murphy et al. (1998) JCEM", "Svensson et al. (1998) Eur J Endocrinol"],
    },
    {
        "id": "test_e",
        "name": "Testosterone enanthate",
        "aliases": ["testosterone enanthate", "test e", "testo e", "test enanthate", "testosterone",
                    "testosteron", "テストステロン", "تستوستيرون", "testosterona"],
        "category": "steroid",
        "tags": ["muscle_gain", "strength", "bulking", "base_compound", "testosterone", "steroid"],
        "summary": "Long-ester injectable testosterone and the gold standard base compound for anabolic cycles. Provides the most predictable, well-studied anabolic and androgenic effects. Injected every 3.5 days or twice weekly for stable blood levels. Decades of clinical data on efficacy and side effect management.",
        "dosage": "300–500 mg/week beginner, 500–750 mg/week intermediate",
        "timing": "Injected subcutaneous or intramuscular every 3.5 days for stable hormone levels",
        "benefits": ["Significant lean mass and strength gains", "Improved recovery allowing higher training volume", "Libido and well-being enhancement", "Predictable, well-understood effects"],
        "side_effects": [{"effect": "Complete natural testosterone suppression", "severity": "high"}, {"effect": "Aromatisation to estrogen — requires aromatase inhibitor", "severity": "medium"}, {"effect": "Acne and hair loss (genetically determined)", "severity": "medium"}, {"effect": "Cardiovascular strain — HDL reduction, LVH risk", "severity": "high"}, {"effect": "Testicular atrophy during cycle", "severity": "high"}],
        "stacking": ["Nandrolone NPP (intermediate+)", "Anavar oxandrolone (cut)", "Anadrol or Dianabol (mass)"],
        "cycle_length": "12–16 weeks",
        "pct_needed": "Full PCT — Nolvadex 40/40/20/20 mg over 4 weeks, start 2 weeks after last injection",
        "evidence_tier": "very_high",
        "safe_for_beginners": False,
        "legal_status": "Schedule III controlled substance USA. Prescription only in UK, India, Canada, Australia. Illegal to possess without prescription in most countries.",
        "research_refs": ["Bhasin et al. (1996) NEJM — landmark dose-response study", "Bhasin et al. (2001) NEJM"],
    },
    {
        "id": "anavar",
        "name": "Anavar (Oxandrolone)",
        "aliases": ["anavar", "oxandrolone", "var", "oxandrin", "oxandrolona"],
        "category": "steroid",
        "tags": ["fat_loss", "strength", "cutting", "lean_muscle", "steroid", "mild_steroid"],
        "summary": "Mild oral anabolic steroid with low androgenic activity, making it popular for cutting cycles and with women (at low doses). Preserves muscle mass during calorie deficit and increases strength without significant water retention. Still hepatotoxic and hormonally suppressive.",
        "dosage": "20–80 mg/day men (split doses), 5–20 mg/day women",
        "timing": "Split into 2 doses due to 9-hour half-life (morning and evening)",
        "benefits": ["Muscle preservation during calorie deficit", "Strength gains without significant mass gain", "Minimal water retention compared to other steroids", "Mild side effect profile versus most anabolic steroids"],
        "side_effects": [{"effect": "Liver stress — oral 17-alpha alkylated; limit to 6–8 weeks", "severity": "medium"}, {"effect": "Testosterone suppression requiring PCT", "severity": "medium"}, {"effect": "Significant lipid changes (HDL reduction)", "severity": "high"}, {"effect": "Virilisation in women at doses above 10 mg/day", "severity": "high"}],
        "cycle_length": "6–8 weeks (oral limit due to liver)",
        "pct_needed": "Yes — standard SERM PCT required",
        "evidence_tier": "high",
        "safe_for_beginners": False,
        "legal_status": "Schedule III controlled substance. Prescription only in all countries where legal.",
        "research_refs": ["Bhasin anabolic steroid research series", "Giorgi et al. (1999) Clin J Sport Med"],
    },
    {
        "id": "nandrolone",
        "name": "Nandrolone / NPP / Deca-Durabolin",
        "aliases": ["nandrolone", "deca", "deca durabolin", "npp", "nandrolone decanoate",
                    "nandrolone phenylpropionate", "deca-durabolin"],
        "category": "steroid",
        "tags": ["muscle_gain", "strength", "bulking", "joint_health", "steroid"],
        "summary": "19-nor anabolic steroid available as NPP (short ester, faster clearance) and Deca-Durabolin (long decanoate ester). Well known for lean mass gains and joint lubrication. Requires prolactin management with cabergoline and must always be run with a testosterone base to avoid severe sexual dysfunction.",
        "dosage": "NPP: 300–400 mg/week (E3.5D injections); Deca: 200–400 mg/week (weekly injection)",
        "timing": "Subcutaneous or intramuscular injection on schedule",
        "benefits": ["Lean mass gains with less water retention than testosterone", "Joint lubrication and pain relief", "Collagen synthesis improvement", "Improved recovery and training volume"],
        "side_effects": [{"effect": "Prolactin elevation — cabergoline 0.25 mg E3D required", "severity": "high"}, {"effect": "Complete natural testosterone suppression", "severity": "high"}, {"effect": "Cardiovascular strain", "severity": "high"}, {"effect": "Erectile dysfunction without testosterone base (deca dick)", "severity": "high"}],
        "cycle_length": "12–16 weeks",
        "pct_needed": "Full PCT required — recovery more complex due to 19-nor suppression mechanism",
        "evidence_tier": "high",
        "safe_for_beginners": False,
        "legal_status": "Controlled substance in most countries. Prescription only.",
        "research_refs": ["Bhasin et al. (1996) NEJM nandrolone arm"],
    },
    {
        "id": "bpc157",
        "name": "BPC-157",
        "aliases": ["bpc157", "bpc-157", "body protection compound", "bpc 157", "pentadecapeptide", "bpc-157 peptide"],
        "category": "peptide",
        "tags": ["recovery", "injury", "joint_health", "gut", "healing", "peptide"],
        "summary": "15-amino acid peptide derived from human gastric juice with potent healing properties. Accelerates recovery of tendons, ligaments, muscle, and gut lining. Strong animal research and extensive anecdotal evidence with no serious side effects reported. One of the safest and most used research peptides.",
        "dosage": "250–500 mcg/day by subcutaneous or intramuscular injection",
        "timing": "Near the injury site (local) or systemic (abdomen), once or twice daily",
        "benefits": ["Significantly accelerated tendon and ligament healing", "Gut lining repair (leaky gut syndrome)", "Anti-inflammatory effects throughout body", "Muscle and wound repair acceleration", "Angiogenesis stimulation improving blood supply to injuries"],
        "side_effects": [{"effect": "Injection site irritation (mild, transient)", "severity": "low"}, {"effect": "Mild nausea with oral form", "severity": "low"}],
        "stacking": ["TB-500 (systemic healing synergy)", "Ipamorelin/CJC-1295"],
        "evidence_tier": "moderate",
        "safe_for_beginners": True,
        "legal_status": "Research chemical — not approved for human use in any country",
        "research_refs": ["Sikiric et al. (2013) Current Pharmaceutical Design review", "Chang et al. (2011) JBMR"],
    },
    {
        "id": "tb500",
        "name": "TB-500 (Thymosin Beta-4)",
        "aliases": ["tb500", "tb-500", "thymosin beta 4", "thymosin beta-4", "tb 500"],
        "category": "peptide",
        "tags": ["recovery", "injury", "muscle_repair", "flexibility", "peptide", "healing"],
        "summary": "Synthetic peptide analogue of Thymosin Beta-4, a naturally occurring protein involved in cell migration, angiogenesis, and tissue repair throughout the body. Acts as a systemic healing agent often combined with BPC-157 for synergistic injury recovery. Improves flexibility and reduces inflammation.",
        "dosage": "2–2.5 mg twice weekly (loading phase 4–6 weeks), then 2 mg bi-weekly maintenance",
        "timing": "Subcutaneous injection, any time of day",
        "benefits": ["Systemic tissue repair and regeneration", "Improved joint and muscle flexibility", "Enhanced angiogenesis (new blood vessel formation)", "Systemic anti-inflammatory action", "Synergistic injury recovery with BPC-157"],
        "side_effects": [{"effect": "Injection site irritation", "severity": "low"}, {"effect": "Brief head rush or fatigue immediately post-injection", "severity": "low"}],
        "stacking": ["BPC-157", "Ipamorelin/CJC-1295"],
        "evidence_tier": "moderate",
        "safe_for_beginners": True,
        "legal_status": "Research chemical — not approved for human use",
        "research_refs": ["Goldstein et al. (2012) Annals NY Acad Sci"],
    },
    {
        "id": "ipamorelin",
        "name": "Ipamorelin / CJC-1295",
        "aliases": ["ipamorelin", "cjc1295", "cjc-1295", "ipamorelin cjc", "ghrp",
                    "gh peptide", "growth hormone peptide", "ipamorelin cjc 1295"],
        "category": "peptide",
        "tags": ["fat_loss", "recovery", "hgh", "anti_aging", "sleep", "gh", "growth hormone", "peptide"],
        "summary": "The gold standard GH peptide combination. Ipamorelin selectively triggers GH release with minimal cortisol or prolactin elevation. CJC-1295 without DAC extends the GH pulse by amplifying the GHRH signal. Combined, they produce a strong, clean, physiological-style GH release ideal for fat loss, recovery, and anti-aging.",
        "dosage": "Ipamorelin 200–300 mcg + CJC-1295 no-DAC 100–200 mcg, 2–3 times daily",
        "timing": "Before bed (mandatory for GH pulse alignment), plus morning and pre-workout; must be fasted (no food 2 hours before)",
        "benefits": ["Amplified natural GH pulse", "Accelerated fat loss especially visceral fat", "Improved sleep depth and REM quality", "Lean mass retention and recovery", "Skin, hair, and collagen improvement over long term"],
        "side_effects": [{"effect": "Mild water retention (transient, first 2 weeks)", "severity": "low"}, {"effect": "Increased hunger", "severity": "low"}, {"effect": "Tingling or numbness at injection site", "severity": "low"}],
        "stacking": ["BPC-157", "TB-500", "MK-677 (oral alternative for GH stimulation)"],
        "evidence_tier": "moderate",
        "safe_for_beginners": False,
        "legal_status": "Research chemical — not approved for human use in any country",
        "research_refs": ["Raun et al. (1998) Eur J Endocrinol", "Svensson et al. (1997) Eur J Endocrinol"],
    },
    {
        "id": "hgh",
        "name": "Human Growth Hormone (HGH)",
        "aliases": ["hgh", "human growth hormone", "growth hormone", "gh", "somatropin",
                    "rhgh", "igf-1", "hormona de crecimiento", "hormone de croissance",
                    "성장 호르몬", "生长激素", "wachstumshormon"],
        "category": "peptide",
        "tags": ["fat_loss", "muscle_gain", "recovery", "anti_aging", "hgh", "gh", "growth hormone"],
        "summary": "Recombinant human growth hormone (somatropin). The most potent anti-aging and body composition agent available. Dramatically reduces visceral fat, supports lean mass, strengthens connective tissue, improves sleep and recovery. Expensive, requires daily injection, and is prescription-only globally.",
        "dosage": "1–3 IU/day (anti-aging / fat loss), 4–8 IU/day (bodybuilding — significantly higher risk)",
        "timing": "Subcutaneous injection on waking (fat loss protocol) or before bed (GH pulse alignment). Some split doses.",
        "benefits": ["Significant visceral and subcutaneous fat loss", "Lean mass retention and modest gain", "Connective tissue and tendon strengthening", "Improved sleep quality and energy", "Skin quality and anti-aging effects"],
        "side_effects": [{"effect": "Carpal tunnel syndrome (tingling hands)", "severity": "medium"}, {"effect": "Insulin resistance — monitor blood glucose", "severity": "high"}, {"effect": "Water retention and joint pain (dose-dependent)", "severity": "medium"}, {"effect": "Acromegaly (organ / bone growth) at sustained high doses", "severity": "high"}, {"effect": "Very expensive — USD 600–2000+/month for quality product", "severity": "low"}],
        "stacking": ["Testosterone (synergistic)", "Insulin (advanced users only — extreme danger)", "T3 thyroid hormone (advanced)"],
        "evidence_tier": "very_high",
        "safe_for_beginners": False,
        "legal_status": "Prescription only in all countries. Banned by WADA. Significant anti-doping and legal risk.",
        "research_refs": ["Rudman et al. (1990) NEJM — landmark study", "Vance (1990) NEJM", "Birzniece et al. (2020) review"],
    },
    {
        "id": "sermorelin_cjc",
        "name": "Sermorelin / GHRH peptides",
        "aliases": ["sermorelin", "ghrh analogue", "sermorelin acetate", "modified grf", "mod grf 1-29"],
        "category": "peptide",
        "tags": ["hgh", "fat_loss", "anti_aging", "recovery", "gh", "growth hormone", "peptide"],
        "summary": "GHRH (growth hormone releasing hormone) analogues that stimulate the pituitary to produce and release GH in a physiological pattern. Softer, more natural GH stimulation than exogenous HGH. Often prescribed in anti-aging medicine. More affordable than HGH with a better safety profile.",
        "dosage": "Sermorelin: 200–500 mcg before bed. Mod GRF 1-29: 100–200 mcg per dose",
        "timing": "Subcutaneous injection before sleep, minimum 2 hours fasted",
        "benefits": ["Natural-pattern GH stimulation via pituitary", "Body composition improvement over 3–6 months", "Improved sleep quality and recovery", "Lower cost than exogenous HGH", "Better safety profile than HGH due to pituitary regulation"],
        "side_effects": [{"effect": "Injection site redness", "severity": "low"}, {"effect": "Flushing and warmth", "severity": "low"}],
        "stacking": ["Ipamorelin (GHRP + GHRH synergy)", "BPC-157"],
        "evidence_tier": "moderate",
        "safe_for_beginners": False,
        "legal_status": "Sermorelin: Prescription only in USA and many countries. Mod GRF 1-29: Research chemical.",
        "research_refs": ["Walker et al. (2004) JCEM", "Prakash & Goa (1999) BioDrugs review"],
    },
]

# ── Fast lookup structures ──────────────────────────────────────────────────
_ALIAS_MAP: dict[str, dict] = {}

for _item in KB:
    _ALIAS_MAP[_item["name"].lower()] = _item
    for _alias in _item.get("aliases", []):
        _ALIAS_MAP[_alias.lower()] = _item

# ── Synonym / intent map ───────────────────────────────────────────────────
INTENT_MAP: dict[str, list[str]] = {
    "lose weight": ["fat_loss","cutting","thermogenic"],
    "fat loss":    ["fat_loss","cutting","thermogenic"],
    "burn fat":    ["fat_loss","cutting","thermogenic"],
    "weight loss": ["fat_loss","cutting","weight_loss"],
    "cut":         ["fat_loss","cutting"],
    "shred":       ["fat_loss","cutting"],
    "bulk":        ["muscle_gain","bulking"],
    "build muscle":["muscle_gain","bulking"],
    "muscle gain": ["muscle_gain","bulking"],
    "muscle growth":["muscle_gain","bulking"],
    "get strong":  ["strength"],
    "strength":    ["strength"],
    "endurance":   ["endurance"],
    "recovery":    ["recovery","healing"],
    "joint":       ["joint_health","recovery"],
    "injury":      ["recovery","injury","healing"],
    "sleep":       ["sleep","anti_aging","recovery"],
    "pump":        ["pump","pre_workout","nitric oxide"],
    "energy":      ["pre_workout","energy","focus"],
    "focus":       ["pre_workout","focus","energy"],
    "sarm":        ["sarm","muscle_gain"],
    "sarms":       ["sarm","muscle_gain"],
    "steroid":     ["steroid","muscle_gain"],
    "steroids":    ["steroid","muscle_gain"],
    "peptide":     ["peptide","recovery"],
    "peptides":    ["peptide","recovery"],
    "growth hormone":["hgh","gh","growth hormone"],
    "hgh":         ["hgh","gh","growth hormone"],
    "human growth":["hgh","gh","growth hormone"],
    "pre workout":  ["pre_workout","energy","pump"],
    "preworkout":   ["pre_workout","energy","pump"],
    "protein":     ["protein","muscle_gain","recovery"],
    "vitamin":     ["health","foundation"],
    "mineral":     ["health","foundation"],
    "best":        [],
    "safe":        ["beginner"],
    "beginner":    ["beginner"],
    "advanced":    ["strength","muscle_gain"],
    "cycle":       ["steroid","sarm"],
    "stack":       ["pre_workout","muscle_gain"],
    "what are":    [],
    "what is":     [],
    "how does":    [],
    "how to":      [],
    "dosage":      [],
    "dose":        [],
    "side effects":["side_effects"],
    "benefits":    [],
    "compare":     [],
}

# ── Multilingual keyword map ───────────────────────────────────────────────
MULTILINGUAL_MAP: dict[str, list[str]] = {
    # Hindi
    "क्रिएटिन": ["creatine"], "मसल": ["muscle_gain"], "प्रोटीन": ["protein"],
    "ताकत": ["strength"], "वजन कम": ["fat_loss"], "चर्बी": ["fat_loss"],
    "सार्म": ["sarm"], "पेप्टाइड": ["peptide"],
    # Spanish
    "músculo": ["muscle_gain"], "fuerza": ["strength"],
    "grasa": ["fat_loss"], "ciclo": ["steroid","sarm"], "pérdida de grasa": ["fat_loss"],
    # French
    "muscle": ["muscle_gain"], "force": ["strength"], "graisse": ["fat_loss"],
    # Portuguese
    "músculo": ["muscle_gain"], "gordura": ["fat_loss"], "força": ["strength"],
    # German
    "muskel": ["muscle_gain"], "fett": ["fat_loss"], "kraft": ["strength"],
    # Arabic
    "عضلات": ["muscle_gain"], "دهون": ["fat_loss"], "قوة": ["strength"],
    # Russian
    "мышцы": ["muscle_gain"], "жир": ["fat_loss"], "сила": ["strength"],
    # Chinese
    "肌肉": ["muscle_gain"], "脂肪": ["fat_loss"], "力量": ["strength"],
    "生长激素": ["hgh","gh"], "蛋白质": ["protein"],
    # Japanese
    "筋肉": ["muscle_gain"], "脂肪燃焼": ["fat_loss"], "成長ホルモン": ["hgh","gh"],
    # Turkish
    "kas": ["muscle_gain"], "yağ yakma": ["fat_loss"], "güç": ["strength"],
    # Italian
    "muscolo": ["muscle_gain"], "grassi": ["fat_loss"], "forza": ["strength"],
    # Bengali
    "পেশী": ["muscle_gain"], "চর্বি": ["fat_loss"],
}


# ═══════════════════════════════════════════════════════════════════════════
# LAYER 1 — ANTHROPIC CLAUDE API
# ═══════════════════════════════════════════════════════════════════════════

_SYSTEM_PROMPT = """You are FitSearch AI — a world-class fitness, sports nutrition, and performance enhancement expert.

RULES:
1. Always respond in the SAME language as the user's query (detect language automatically)
2. Respond ONLY with a valid JSON object — no markdown, no prose outside JSON
3. Include honest safety warnings for steroids, SARMs, peptides, and HGH
4. safe_for_beginners must be false for steroids and most SARMs
5. evidence_tier must honestly reflect the research quality
6. Return 1–4 most relevant results

JSON response format (respond ONLY with this, nothing else):
{
  "detected_language": "language name",
  "intent": "explain | recommend | dosage | compare | cycle | side_effects | general",
  "compounds_mentioned": ["compound names found in query"],
  "tags": ["relevant tags"],
  "results": [
    {
      "name": "compound or topic name",
      "category": "supplement | sarm | steroid | peptide | training | diet",
      "summary": "3-5 sentence comprehensive answer in the user's language",
      "dosage": "evidence-based dosage",
      "timing": "when to take",
      "benefits": ["benefit 1", "benefit 2", "benefit 3"],
      "side_effects": [{"effect": "description", "severity": "low | medium | high"}],
      "stacking": ["compound 1", "compound 2"],
      "evidence_tier": "very_high | high | moderate | low",
      "safe_for_beginners": true,
      "legal_status": "status or null",
      "research_refs": ["key reference"],
      "cycle_length": "if applicable or null",
      "pct_needed": "if applicable or null"
    }
  ],
  "ai_summary": "2-3 sentence direct answer to the user's question in their language",
  "safety_note": "important safety warning in user's language if applicable, otherwise null"
}"""


def _call_anthropic(query: str) -> dict | None:
    if not ANTHROPIC_API_KEY:
        return None
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
                "max_tokens": 2000,
                "system":     _SYSTEM_PROMPT,
                "messages":   [{"role": "user", "content": query}],
            },
            timeout=20,
        )
        resp.raise_for_status()
        text = resp.json()["content"][0]["text"].strip()
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
        return json.loads(text)
    except Exception as e:
        print(f"[Anthropic] Error: {e}")
        return None


# ═══════════════════════════════════════════════════════════════════════════
# LAYER 2 — SERPAPI  (real-time Google results)
# ═══════════════════════════════════════════════════════════════════════════

def _call_serp(query: str) -> list[dict]:
    if not SERP_API_KEY:
        return []
    try:
        resp = requests.get(
            SERP_URL,
            params={
                "q":       f"{query} supplement research site:examine.com OR site:pubmed.ncbi.nlm.nih.gov OR site:jissn.biomedcentral.com",
                "api_key": SERP_API_KEY,
                "engine":  "google",
                "num":     5,
                "hl":      "en",
            },
            timeout=8,
        )
        if resp.status_code != 200:
            return []
        return [
            {"title": r.get("title",""), "snippet": r.get("snippet",""),
             "link": r.get("link",""), "source": r.get("displayed_link","")}
            for r in resp.json().get("organic_results", [])[:5]
        ]
    except Exception as e:
        print(f"[SerpAPI] Error: {e}")
        return []


# ═══════════════════════════════════════════════════════════════════════════
# LAYER 3 — LOCAL KNOWLEDGE BASE
# ═══════════════════════════════════════════════════════════════════════════

def _expand_query(query: str) -> tuple[list[str], list[str]]:
    """Extract compound names and goal tags from natural language query (any language)."""
    q_lower = query.lower()
    compounds: list[str] = []
    tags: list[str]      = []

    # Direct alias matching
    for alias, item in _ALIAS_MAP.items():
        if alias in q_lower:
            if item["name"] not in compounds:
                compounds.append(item["name"])
            tags.extend(item.get("tags", []))

    # Intent phrase matching
    for phrase, phrase_tags in INTENT_MAP.items():
        if phrase in q_lower:
            tags.extend(phrase_tags)

    # Multilingual keyword matching (case-sensitive for non-Latin scripts)
    for word, word_tags in MULTILINGUAL_MAP.items():
        if word in query:
            tags.extend(word_tags)
            for wt in word_tags:
                m = _ALIAS_MAP.get(wt)
                if m and m["name"] not in compounds:
                    compounds.append(m["name"])

    # Word-level fuzzy matching against aliases
    for word in re.split(r"[\s\W]+", q_lower):
        if len(word) < 3:
            continue
        for alias, item in _ALIAS_MAP.items():
            if word in alias and item["name"] not in compounds:
                compounds.append(item["name"])
                tags.extend(item.get("tags", []))

    return list(dict.fromkeys(compounds)), list(dict.fromkeys(tags))


def _score_item(q_lower: str, compounds: list[str], tags: list[str],
                item: dict, filters: list[str]) -> int:
    s         = 0
    name      = item["name"].lower()
    summ      = item["summary"].lower()
    itags_str = " ".join(item.get("tags", []))
    aliases   = " ".join(item.get("aliases", []))

    for c in compounds:
        if c.lower() in name or name in c.lower():
            s += 20

    for t in tags:
        if t in itags_str:
            s += 5

    for word in re.split(r"[\s\W]+", q_lower):
        if len(word) < 3:
            continue
        if word in name:    s += 8
        if word in aliases: s += 6
        if word in itags_str: s += 4
        if word in summ:    s += 1

    if "beginner" in filters and item.get("safe_for_beginners"):
        s += 4
    if "advanced" in filters and not item.get("safe_for_beginners"):
        s += 2
    for f in filters:
        if f in itags_str:
            s += 3

    return s


def _search_kb(query: str, filters: list[str]) -> list[dict]:
    q_lower = query.lower()
    compounds, tags = _expand_query(query)
    scored = [
        {**item, "_sc": _score_item(q_lower, compounds, tags, item, filters)}
        for item in KB
    ]
    scored = [r for r in scored if r["_sc"] > 0]
    scored.sort(key=lambda x: x["_sc"], reverse=True)
    return [{k: v for k, v in r.items() if k != "_sc"} for r in scored[:6]]


# ═══════════════════════════════════════════════════════════════════════════
# MAIN PUBLIC FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def search_knowledge(query: str, filters: list | None = None) -> list[dict]:
    """
    Main search entry point called by app.py.
    Tries Anthropic → SerpAPI → local KB in order of availability.
    Returns a list of structured result dicts ready for the frontend.
    """
    filters   = filters or []
    ts        = datetime.now(timezone.utc).isoformat()

    # ── Layer 1: Anthropic (NLP + AI-generated structured answer) ──────────
    ai = _call_anthropic(query)
    if ai and ai.get("results"):
        results = ai["results"]
        # Enrich AI results with local KB data where compound names overlap
        for r in results:
            kb = _ALIAS_MAP.get(r.get("name", "").lower())
            if kb:
                r.setdefault("research_refs", kb.get("research_refs", []))
                r.setdefault("stacking",      kb.get("stacking", []))
            r["_source"]    = "ai"
            r["_timestamp"] = ts
        # Inject AI summary and safety note into the first result
        if results:
            results[0]["ai_summary"]  = ai.get("ai_summary", "")
            results[0]["safety_note"] = ai.get("safety_note")
        return results

    # ── Layer 2: SerpAPI (live web results) + local KB ─────────────────────
    web  = _call_serp(query)
    kb   = _search_kb(query, filters)

    if web:
        web_fmt = [
            {
                "id": f"web_{i}", "name": r["title"], "category": "research",
                "summary": r["snippet"], "dosage": None, "timing": None,
                "benefits": [], "side_effects": [], "stacking": [],
                "evidence_tier": "moderate", "safe_for_beginners": None,
                "legal_status": None, "research_refs": [r["link"]],
                "source_url": r["link"], "source_name": r["source"],
                "_source": "web", "_timestamp": ts,
            }
            for i, r in enumerate(web)
        ]
        combined = (kb[:3] if kb else []) + web_fmt[:2]
        for r in combined:
            r.setdefault("_source", "kb")
            r.setdefault("_timestamp", ts)
        return combined if combined else _fallback(query, ts)

    # ── Layer 3: Local KB only ─────────────────────────────────────────────
    for r in kb:
        r["_source"]    = "kb"
        r["_timestamp"] = ts
    return kb if kb else _fallback(query, ts)


def _fallback(query: str, ts: str) -> list[dict]:
    return [{
        "id": "fallback", "name": f"Search: {query}", "category": "supplement",
        "summary": (
            f"No exact match for '{query}'. Try: 'Creatine monohydrate', 'Ostarine', "
            "'Testosterone enanthate', 'BPC-157', 'Ipamorelin', 'Whey protein', "
            "'fat burner', 'pre-workout', or goal-based queries like "
            "'best supplement for strength' or 'safe SARMs for beginners'."
        ),
        "dosage": None, "timing": None, "benefits": [], "side_effects": [],
        "stacking": [], "evidence_tier": "moderate", "safe_for_beginners": True,
        "legal_status": None,
        "research_refs": ["https://examine.com", "https://pubmed.ncbi.nlm.nih.gov"],
        "_source": "fallback", "_timestamp": ts,
    }]


def get_recommendations(recent_queries: list[str], user: dict) -> list[dict]:
    """Personalised recommendations from user history + profile. No API calls needed."""
    goal  = (user.get("goal") or "muscle_gain").replace("-", "_")
    level = user.get("experience_level") or "beginner"

    seen: set[str] = set()
    for q in recent_queries:
        _, _ = _expand_query(q)
        compounds, _ = _expand_query(q)
        for c in compounds:
            m = _ALIAS_MAP.get(c.lower())
            if m:
                seen.add(m["id"])

    recs: list[dict] = []
    for item in KB:
        if item["id"] in seen:
            continue
        sc = 0
        if goal in item.get("tags", []):
            sc += 4
        if item.get("safe_for_beginners") and level == "beginner":
            sc += 3
        if not item.get("safe_for_beginners") and level in ("intermediate","advanced"):
            sc += 2
        if item["category"] == "supplement":
            sc += 1
        if item["evidence_tier"] in ("very_high","high"):
            sc += 1
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
