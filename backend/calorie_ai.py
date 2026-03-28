"""calorie_ai.py — Mifflin-St Jeor BMR with activity multiplier"""

ACTIVITY_MULTIPLIERS = {
    "sedentary":   1.2,
    "light":       1.375,
    "moderate":    1.55,
    "active":      1.725,
    "very_active": 1.9,
}

GOAL_ADJUSTMENTS = {
    "fat_loss":    -500,
    "cutting":     -500,
    "recomp":      0,
    "maintenance": 0,
    "muscle_gain": +300,
    "bulking":     +500,
}

def calculate_calories(data):
    weight  = float(data.get("weight") or 80)
    height  = float(data.get("height") or 175)
    age     = int(data.get("age") or 28)
    sex     = data.get("sex", "male").lower()
    activity = data.get("activity_level", "moderate")
    goal    = data.get("goal", "muscle_gain")

    # Mifflin-St Jeor
    if sex == "female":
        bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161
    else:
        bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5

    multiplier = ACTIVITY_MULTIPLIERS.get(activity, 1.55)
    tdee = bmr * multiplier
    adjustment = GOAL_ADJUSTMENTS.get(goal, 0)
    return int(tdee + adjustment)
