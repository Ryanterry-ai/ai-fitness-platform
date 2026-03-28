"""supplement_ai.py — side-by-side compound comparison engine"""
from backend.search_ai import KNOWLEDGE_BASE

COMPOUND_INDEX = {item["name"].lower(): item for item in KNOWLEDGE_BASE}
# Also index by id
COMPOUND_INDEX_BY_ID = {item["id"]: item for item in KNOWLEDGE_BASE}


def find_compound(name):
    name_lower = name.lower()
    # Exact match
    if name_lower in COMPOUND_INDEX:
        return COMPOUND_INDEX[name_lower]
    # Partial match
    for key, item in COMPOUND_INDEX.items():
        if name_lower in key or key in name_lower:
            return item
    return None


ATTRIBUTE_CONFIG = [
    {"key": "dosage",          "label": "Daily dosage",      "higher_is_better": None},
    {"key": "evidence_tier",   "label": "Evidence level",    "higher_is_better": True,
     "order": ["very_high", "high", "moderate", "low"]},
    {"key": "cycle_length",    "label": "Cycle length",      "higher_is_better": None},
    {"key": "pct_needed",      "label": "PCT required",      "higher_is_better": False},
    {"key": "safe_for_beginners", "label": "Beginner-safe",  "higher_is_better": True},
    {"key": "legal_status",    "label": "Legal status",      "higher_is_better": None},
]


def evidence_rank(tier):
    order = ["low", "moderate", "high", "very_high"]
    try:
        return order.index(tier)
    except ValueError:
        return -1


def pick_winner(compounds, attr_key):
    """Return index of the winner compound for a given attribute, or None."""
    if attr_key == "evidence_tier":
        ranks = [evidence_rank(c.get(attr_key, "low")) for c in compounds]
        max_rank = max(ranks)
        winners = [i for i, r in enumerate(ranks) if r == max_rank]
        return winners[0] if len(winners) == 1 else None
    if attr_key == "safe_for_beginners":
        values = [c.get(attr_key, False) for c in compounds]
        if values.count(True) == 1:
            return values.index(True)
    return None


def verdict(compounds, user):
    """Generate a natural-language verdict based on user's goal + experience."""
    goal = user.get("goal", "muscle_gain")
    level = user.get("experience_level", "beginner")

    # Score each compound by suitability
    scores = []
    for c in compounds:
        s = 0
        if goal.replace("-","_") in c.get("tags", []):
            s += 3
        if level == "beginner" and c.get("safe_for_beginners"):
            s += 2
        et = evidence_rank(c.get("evidence_tier", "low"))
        s += et
        scores.append(s)

    best_idx = scores.index(max(scores))
    best = compounds[best_idx]

    if level == "beginner":
        note = f"For a beginner focused on {goal.replace('_',' ')}, {best['name']} is the safest and most evidence-backed choice."
    else:
        note = f"For an {level} athlete targeting {goal.replace('_',' ')}, {best['name']} offers the best combination of efficacy and research support."

    return {"recommended": best["name"], "reasoning": note}


def compare_supplements(compound_names, user):
    compounds = []
    not_found = []
    for name in compound_names:
        c = find_compound(name)
        if c:
            compounds.append(c)
        else:
            not_found.append(name)

    if len(compounds) < 2:
        return {"error": f"Could not find: {', '.join(not_found)}. Try full names like 'Creatine monohydrate', 'Ostarine', 'Testosterone enanthate'."}

    rows = []
    attributes = [
        ("category",       "Category"),
        ("dosage",         "Dosage"),
        ("evidence_tier",  "Evidence level"),
        ("cycle_length",   "Cycle length"),
        ("pct_needed",     "PCT required"),
        ("safe_for_beginners", "Beginner-safe"),
        ("legal_status",   "Legal status"),
    ]

    for attr_key, attr_label in attributes:
        row = {"attribute": attr_label, "values": [], "winner_index": None}
        for i, c in enumerate(compounds):
            val = c.get(attr_key)
            if val is None:
                val = "—"
            elif isinstance(val, bool):
                val = "Yes" if val else "No"
            row["values"].append(str(val))
        row["winner_index"] = pick_winner(compounds, attr_key)
        rows.append(row)

    # Benefits comparison
    benefit_row = {
        "attribute": "Key benefits",
        "values": [", ".join(c.get("benefits", [])[:3]) for c in compounds],
        "winner_index": None
    }
    rows.append(benefit_row)

    # Side effects
    se_row = {
        "attribute": "Main side effects",
        "values": [
            ", ".join(se["effect"] for se in c.get("side_effects", [])[:2]) or "Minimal"
            for c in compounds
        ],
        "winner_index": None
    }
    rows.append(se_row)

    return {
        "compounds": [c["name"] for c in compounds],
        "categories": [c["category"] for c in compounds],
        "rows": rows,
        "verdict": verdict(compounds, user),
        "not_found": not_found,
    }
