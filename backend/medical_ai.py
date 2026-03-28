"""medical_ai.py — basic health screening and training readiness assessment"""

def analyze_medical(data):
    conditions = data.get("conditions", [])
    medications = data.get("medications", [])
    age = int(data.get("age") or 28)
    goal = data.get("goal", "muscle_gain")

    flags = []
    recommendations = []

    # Age-based flags
    if age < 21:
        flags.append({"flag": "Age under 21", "severity": "high", "note": "Anabolic compounds not recommended — still in hormonal development"})
    if age > 45:
        recommendations.append("Consider baseline testosterone bloodwork before any cycle")

    # Condition checks
    HIGH_RISK_CONDITIONS = ["hypertension", "heart disease", "liver disease", "kidney disease", "diabetes"]
    for c in conditions:
        c_lower = c.lower()
        for risk in HIGH_RISK_CONDITIONS:
            if risk in c_lower:
                flags.append({"flag": c, "severity": "high", "note": f"{c} significantly increases risk — physician clearance mandatory"})

    # Medication interactions
    INTERACTIONS = {
        "warfarin":     "Blood thinners interact with many anabolic compounds",
        "statins":      "Liver stress compounds with oral steroids",
        "antidepressants": "Some SSRIs interact with hormonal therapies",
        "insulin":      "Anabolic compounds affect insulin sensitivity",
    }
    for med in medications:
        for drug, note in INTERACTIONS.items():
            if drug in med.lower():
                flags.append({"flag": f"Medication: {med}", "severity": "medium", "note": note})

    # General recs
    recommendations += [
        "Complete CBC, lipid panel, liver enzymes, and testosterone levels before any cycle",
        "Monitor blood pressure at least weekly during active cycles",
        "Cardiovascular health assessment recommended before any steroid use",
    ]

    overall = "high_risk" if any(f["severity"] == "high" for f in flags) else ("moderate_risk" if flags else "low_risk")

    return {
        "overall_risk": overall,
        "flags": flags,
        "recommendations": recommendations,
        "clearance": overall == "low_risk",
        "note": "This is a screening tool only, not a medical assessment. Always consult a qualified physician.",
    }
