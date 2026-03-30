"""
diet_ai.py — structured and personalized meal plan generator
Handles macro calculation, diet preference filtering, and profession adjustments.
"""

MEAL_TEMPLATES = {
    "muscle_gain": [
        {"name": "Breakfast", "foods": "6 whole eggs scrambled, 80g oats with milk, 1 banana, glass of whole milk", "protein": 52, "carbs": 85, "fats": 28, "cal_factor": 0.26},
        {"name": "Mid-morning", "foods": "400g Greek yogurt, 100g blueberries, 1 whey shake (30g protein powder)", "protein": 48, "carbs": 38, "fats": 6, "cal_factor": 0.15},
        {"name": "Lunch", "foods": "250g chicken breast, 250g cooked white rice, 200g broccoli, 15ml olive oil", "protein": 55, "carbs": 92, "fats": 18, "cal_factor": 0.23},
        {"name": "Pre-workout", "foods": "4 rice cakes, 30g peanut butter, 5g creatine monohydrate", "protein": 10, "carbs": 60, "fats": 16, "cal_factor": 0.12},
        {"name": "Post-workout", "foods": "1 whey shake (30g protein), 200g cooked white rice, 1 apple", "protein": 38, "carbs": 70, "fats": 4, "cal_factor": 0.15},
        {"name": "Dinner", "foods": "200g salmon fillet, 300g sweet potato, large mixed salad, 15ml olive oil", "protein": 45, "carbs": 65, "fats": 22, "cal_factor": 0.22},
    ],
    "fat_loss": [
        {"name": "Breakfast", "foods": "4 whole eggs + 4 egg whites, 200g spinach sautéed, 1 slice wholegrain toast", "protein": 42, "carbs": 18, "fats": 18, "cal_factor": 0.22},
        {"name": "Mid-morning", "foods": "200g cottage cheese, 1 apple, 10 almonds", "protein": 28, "carbs": 22, "fats": 8, "cal_factor": 0.15},
        {"name": "Lunch", "foods": "200g chicken breast, 150g brown rice, 300g mixed vegetables, lemon dressing", "protein": 48, "carbs": 55, "fats": 8, "cal_factor": 0.25},
        {"name": "Pre-workout", "foods": "1 whey shake (30g protein), 1 banana", "protein": 32, "carbs": 30, "fats": 3, "cal_factor": 0.13},
        {"name": "Dinner", "foods": "200g white fish (tilapia/cod), 200g green beans, large salad, 10ml olive oil", "protein": 42, "carbs": 15, "fats": 12, "cal_factor": 0.18},
        {"name": "Evening snack", "foods": "200g Greek yogurt (0%), 1 tsp honey, 100g berries", "protein": 22, "carbs": 20, "fats": 1, "cal_factor": 0.10},
    ],
    "recomp": [
        {"name": "Breakfast", "foods": "5 eggs (2 whole + 3 whites), 60g oats, 1 cup mixed berries", "protein": 38, "carbs": 60, "fats": 14, "cal_factor": 0.22},
        {"name": "Mid-morning", "foods": "30g casein protein, 150g Greek yogurt, handful of walnuts", "protein": 40, "carbs": 15, "fats": 12, "cal_factor": 0.15},
        {"name": "Lunch", "foods": "200g turkey breast, 150g quinoa, 200g mixed veg, 10ml olive oil", "protein": 50, "carbs": 55, "fats": 14, "cal_factor": 0.25},
        {"name": "Pre-workout", "foods": "1 banana, 20g whey, 5g creatine", "protein": 25, "carbs": 35, "fats": 2, "cal_factor": 0.13},
        {"name": "Post-workout", "foods": "40g whey protein, 150g white rice, 100g broccoli", "protein": 48, "carbs": 50, "fats": 3, "cal_factor": 0.13},
        {"name": "Dinner", "foods": "200g lean beef (93%), large salad, 15ml olive oil, 100g roasted veg", "protein": 45, "carbs": 15, "fats": 20, "cal_factor": 0.18},
    ]
}

SUPPLEMENTS = {
    "muscle_gain": ["Creatine monohydrate 5g post-workout", "Whey protein 2 scoops/day", "Vitamin D3 2000 IU", "Omega-3 3g/day"],
    "fat_loss": ["Whey protein isolate 1–2 scoops/day", "Caffeine 200mg pre-workout", "L-Carnitine 2g pre-workout", "Omega-3 3g/day"],
    "recomp": ["Creatine monohydrate 5g", "Whey protein 1–2 scoops", "Omega-3 3g/day", "Multivitamin"]
}

def generate_diet(user_data, total_calories):
    """
    Generate personalized meal plan
    user_data: dict containing goal, weight, diet preference (veg/non-veg/both), profession, etc
    total_calories: integer, calories per day
    """
    goal = user_data.get("goal", "muscle_gain")
    weight = float(user_data.get("weight") or 70)
    diet_pref = user_data.get("dietary_restrictions", "both")  # veg / non-veg / both
    profession = user_data.get("profession", "other")

    # Macros calculation
    if goal == "muscle_gain":
        protein = round(weight*2.0)
        fats = round(weight*1.0)
    elif goal == "fat_loss":
        protein = round(weight*2.4)
        fats = round(weight*0.9)
    else:  # recomp
        protein = round(weight*2.2)
        fats = round(weight*0.9)
    carbs = max(round((total_calories - (protein*4 + fats*9))/4), 50)

    # Adjust meals by diet preference
    template = MEAL_TEMPLATES.get(goal, MEAL_TEMPLATES["muscle_gain"])
    filtered_meals = []
    for meal in template:
        food_lower = meal["foods"].lower()
        if diet_pref == "veg" and any(nv in food_lower for nv in ["chicken", "beef", "fish", "salmon", "turkey", "whey"]):
            continue
        filtered_meals.append(meal)

    # Adjust calories per meal
    meals_out = []
    for meal in filtered_meals:
        meal_cal = round(total_calories * meal["cal_factor"])
        meals_out.append({
            "name": meal["name"],
            "foods": meal["foods"],
            "calories": meal_cal,
            "protein": meal["protein"],
            "carbs": meal["carbs"],
            "fats": meal["fats"]
        })

    return {
        "goal": goal,
        "total_calories": total_calories,
        "macros": {"protein_g": protein, "carbs_g": carbs, "fats_g": fats},
        "meals": meals_out,
        "supplements": SUPPLEMENTS.get(goal, []),
        "notes": [
            f"Target {protein}g protein daily.",
            "Drink 3–4 litres of water daily.",
            "Adjust portion sizes if weight isn't changing after 2 weeks."
        ]
    }
