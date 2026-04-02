"""cycle_ai.py — structured cycle planner with PCT and bloodwork checkpoints"""

CYCLES = {
    "beginner_testosterone": {
        "cycle_name": "Beginner testosterone-only cycle",
        "total_weeks": 16,
        "experience_required": "beginner",
        "category": "steroid",
        "weeks": [
            {"range": "Weeks 1–12", "compound": "Testosterone enanthate", "dose": "300–400 mg/week", "phase": "on", "notes": "Inject E3.5D for stable blood levels"},
            {"range": "Weeks 1–12", "compound": "Anastrozole (AI)",       "dose": "0.25 mg E3D",     "phase": "on", "notes": "Adjust based on estrogen symptoms"},
            {"range": "Weeks 13–14","compound": "Washout period",          "dose": "—",                "phase": "off","notes": "Allow testosterone to clear before PCT"},
            {"range": "Weeks 15–16","compound": "Nolvadex (PCT)",          "dose": "40 / 40 mg",       "phase": "pct","notes": "40mg/day weeks 1–2 of PCT"},
            {"range": "Weeks 17–18","compound": "Nolvadex (PCT)",          "dose": "20 / 20 mg",       "phase": "pct","notes": "20mg/day weeks 3–4 of PCT"},
        ],
        "on_cycle_support": ["Anastrozole 0.25mg E3D (aromatase inhibitor)", "TUDCA 500mg/day (liver)", "Fish oil 4g/day (cardiovascular)", "Blood pressure monitoring weekly"],
        "pct": "Nolvadex 40/40/20/20mg over 4 weeks",
        "bloodwork": ["Baseline before cycle start", "Week 6 (mid-cycle)", "2 weeks after PCT completion"],
        "warning": "This is a controlled substance in most countries. Consult a physician. Minimum age 25 recommended. Never use without bloodwork.",
    },
    "beginner_sarm_ostarine": {
        "cycle_name": "Beginner Ostarine (MK-2866) cycle",
        "total_weeks": 11,
        "experience_required": "beginner",
        "category": "sarm",
        "weeks": [
            {"range": "Weeks 1–8", "compound": "Ostarine (MK-2866)", "dose": "15–20 mg/day", "phase": "on",  "notes": "Once daily, same time each day"},
            {"range": "Weeks 9–11","compound": "Mini PCT (optional)", "dose": "20 mg Nolvadex", "phase": "pct","notes": "Only if suppression symptoms occur"},
        ],
        "on_cycle_support": ["Bloodwork before and after", "Liver support (TUDCA 250mg/day optional)", "Monitor mood and libido weekly"],
        "pct": "Nolvadex 20mg/day × 3 weeks (if suppressed) or no PCT if feeling normal",
        "bloodwork": ["Baseline testosterone before", "4–6 weeks post-cycle"],
        "warning": "Research chemical — not approved for human use. Do not use under age 21. Monitor testosterone levels via bloodwork.",
    },
    "intermediate_test_deca": {
        "cycle_name": "Intermediate test + NPP cycle",
        "total_weeks": 20,
        "experience_required": "intermediate",
        "category": "steroid",
        "weeks": [
            {"range": "Weeks 1–14", "compound": "Testosterone enanthate", "dose": "400–500 mg/week", "phase": "on",  "notes": "Twice-weekly injections"},
            {"range": "Weeks 1–12", "compound": "NPP (Nandrolone)",       "dose": "300 mg/week",      "phase": "on",  "notes": "E3.5D injections"},
            {"range": "Weeks 1–14", "compound": "Anastrozole (AI)",       "dose": "0.5 mg E3D",       "phase": "on",  "notes": "Monitor estrogen — adjust as needed"},
            {"range": "Weeks 15–16","compound": "Washout",                 "dose": "—",                "phase": "off", "notes": "NPP clears faster than enanthate"},
            {"range": "Weeks 17–20","compound": "Nolvadex (PCT)",          "dose": "40/40/20/20 mg",   "phase": "pct", "notes": "Full 4-week PCT"},
        ],
        "on_cycle_support": ["AI throughout", "Cabergoline 0.25mg E3D (prolactin control)", "TUDCA 500mg/day", "Fish oil 4g/day", "Weekly BP monitoring"],
        "pct": "Nolvadex 40/40/20/20mg + Clomid optional",
        "bloodwork": ["Baseline", "Week 6", "Week 12", "4 weeks post-PCT"],
        "warning": "Intermediate cycle — do not run without at least one successful beginner cycle. Bloodwork mandatory.",
    },
    "peptide_recovery": {
        "cycle_name": "Peptide recovery protocol — BPC-157 + Ipamorelin",
        "total_weeks": 12,
        "experience_required": "beginner",
        "category": "peptide",
        "weeks": [
            {"range": "Weeks 1–12", "compound": "BPC-157",           "dose": "250–500 mcg/day",      "phase": "on", "notes": "Subcutaneous near injury site or systemic"},
            {"range": "Weeks 1–12", "compound": "Ipamorelin/CJC-1295","dose": "300 mcg + 150 mcg",    "phase": "on", "notes": "Before bed, fasted. 2–3x daily for fat loss"},
        ],
        "on_cycle_support": ["Bacteriostatic water for reconstitution", "Insulin syringes (29–31G)", "Keep peptides refrigerated"],
        "pct": "No PCT needed for peptide-only protocols",
        "bloodwork": ["IGF-1 baseline (if running Ipamorelin long-term)", "Check at 6 weeks"],
        "warning": "Research chemicals — not approved for human use. Source quality matters enormously with peptides. Sterility is critical.",
    },
}


def generate_cycle(data):
    goal       = data.get("goal", "muscle_gain")
    level      = data.get("experience_level", "beginner")
    category   = data.get("compound_category", "auto")  # sarm / steroid / peptide / auto
    cycle_type = data.get("cycle_type")

    # Auto-select cycle
    if cycle_type and cycle_type in CYCLES:
        template = CYCLES[cycle_type]
    elif category == "sarm" or (category == "auto" and level == "beginner" and goal in ("recomp", "fat_loss")):
        template = CYCLES["beginner_sarm_ostarine"]
    elif category == "peptide":
        template = CYCLES["peptide_recovery"]
    elif level == "intermediate" and category in ("steroid", "auto"):
        template = CYCLES["intermediate_test_deca"]
    else:
        template = CYCLES["beginner_testosterone"]

    return {
        **template,
        "user_goal": goal,
        "user_level": level,
        "disclaimer": (
            "This information is for educational purposes only. Anabolic steroids and SARMs "
            "are controlled or unregulated substances in many jurisdictions. Always consult a "
            "qualified physician before starting any cycle. Regular bloodwork is non-negotiable."
        ),
    }
