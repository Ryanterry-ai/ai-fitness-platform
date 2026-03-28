"""diet_ai.py — structured meal plan generator with macros"""

MEAL_TEMPLATES = {
    "muscle_gain": {
        "meals": [
            {"name": "Breakfast",     "foods": "6 whole eggs scrambled, 80g oats with milk, 1 banana, glass of whole milk",           "protein": 52, "carbs": 85, "fats": 28, "cal_factor": 0.26},
            {"name": "Mid-morning",   "foods": "400g Greek yogurt, 100g blueberries, 1 whey shake (30g protein powder)",              "protein": 48, "carbs": 38, "fats": 6,  "cal_factor": 0.15},
            {"name": "Lunch",         "foods": "250g chicken breast grilled, 250g cooked white rice, 200g broccoli, 15ml olive oil",  "protein": 55, "carbs": 92, "fats": 18, "cal_factor": 0.23},
            {"name": "Pre-workout",   "foods": "4 rice cakes, 30g peanut butter, 5g creatine monohydrate",                           "protein": 10, "carbs": 60, "fats": 16, "cal_factor": 0.12},
            {"name": "Post-workout",  "foods": "1 whey shake (30g protein), 200g cooked white rice, 1 apple",                        "protein": 38, "carbs": 70, "fats": 4,  "cal_factor": 0.15},
            {"name": "Dinner",        "foods": "200g salmon fillet, 300g sweet potato, large mixed salad, 15ml olive oil",           "protein": 45, "carbs": 65, "fats": 22, "cal_factor": 0.22},
        ],
        "supplements": ["Creatine monohydrate 5g (post-workout)", "Whey protein 2 scoops/day", "Vitamin D3 2000 IU", "Omega-3 3g/day"],
    },
    "fat_loss": {
        "meals": [
            {"name": "Breakfast",     "foods": "4 whole eggs + 4 egg whites, 200g spinach sautéed, 1 slice wholegrain toast",        "protein": 42, "carbs": 18, "fats": 18, "cal_factor": 0.22},
            {"name": "Mid-morning",   "foods": "200g cottage cheese, 1 apple, 10 almonds",                                           "protein": 28, "carbs": 22, "fats": 8,  "cal_factor": 0.15},
            {"name": "Lunch",         "foods": "200g chicken breast, 150g brown rice, 300g mixed vegetables, lemon dressing",        "protein": 48, "carbs": 55, "fats": 8,  "cal_factor": 0.25},
            {"name": "Pre-workout",   "foods": "1 whey shake (30g protein), 1 banana",                                               "protein": 32, "carbs": 30, "fats": 3,  "cal_factor": 0.13},
            {"name": "Dinner",        "foods": "200g white fish (tilapia/cod), 200g green beans, large salad, 10ml olive oil",       "protein": 42, "carbs": 15, "fats": 12, "cal_factor": 0.18},
            {"name": "Evening snack", "foods": "200g Greek yogurt (0%), 1 tsp honey, 100g berries",                                  "protein": 22, "carbs": 20, "fats": 1,  "cal_factor": 0.10},
        ],
        "supplements": ["Whey protein isolate 1–2 scoops/day", "Caffeine 200mg pre-workout", "L-Carnitine 2g pre-workout", "Omega-3 3g/day"],
    },
    "recomp": {
        "meals": [
            {"name": "Breakfast",     "foods": "5 eggs (2 whole + 3 whites), 60g oats, 1 cup mixed berries",                        "protein": 38, "carbs": 60, "fats": 14, "cal_factor": 0.22},
            {"name": "Mid-morning",   "foods": "30g casein protein, 150g Greek yogurt, handful of walnuts",                          "protein": 40, "carbs": 15, "fats": 12, "cal_factor": 0.15},
            {"name": "Lunch",         "foods": "200g turkey breast, 150g quinoa, 200g mixed veg, 10ml olive oil",                    "protein": 50, "carbs": 55, "fats": 14, "cal_factor": 0.25},
            {"name": "Pre-workout",   "foods": "1 banana, 20g whey, 5g creatine",                                                   "protein": 25, "carbs": 35, "fats": 2,  "cal_factor": 0.13},
            {"name": "Post-workout",  "foods": "40g whey protein, 150g white rice, 100g broccoli",                                   "protein": 48, "carbs": 50, "fats": 3,  "cal_factor": 0.13},
            {"name": "Dinner",        "foods": "200g lean beef (93%), large salad, 15ml olive oil, 100g roasted veg",               "protein": 45, "carbs": 15, "fats": 20, "cal_factor": 0.18},
        ],
        "supplements": ["Creatine monohydrate 5g", "Whey protein 1–2 scoops", "Omega-3 3g/day", "Multivitamin"],
    },
}


def generate_diet(data, calories):
    goal = data.get("goal", "muscle_gain")
    weight = float(data.get("weight") or 80)
    restrictions = data.get("dietary_restrictions", [])

    template_key = goal if goal in MEAL_TEMPLATES else "muscle_gain"
    template = MEAL_TEMPLATES[template_key]

    # Macro targets
    if goal in ("fat_loss", "cutting"):
        protein_g = round(weight * 2.4)
        fats_g    = round(weight * 0.9)
        carbs_g   = round((calories - (protein_g * 4) - (fats_g * 9)) / 4)
    elif goal in ("muscle_gain", "bulking"):
        protein_g = round(weight * 2.0)
        fats_g    = round(weight * 1.0)
        carbs_g   = round((calories - (protein_g * 4) - (fats_g * 9)) / 4)
    else:  # recomp / maintenance
        protein_g = round(weight * 2.2)
        fats_g    = round(weight * 0.9)
        carbs_g   = round((calories - (protein_g * 4) - (fats_g * 9)) / 4)

    carbs_g = max(carbs_g, 50)

    meals_out = []
    for meal in template["meals"]:
        meal_cal = round(calories * meal["cal_factor"])
        meals_out.append({
            "name":    meal["name"],
            "foods":   meal["foods"],
            "calories": meal_cal,
            "protein": meal["protein"],
            "carbs":   meal["carbs"],
            "fats":    meal["fats"],
        })

    return {
        "goal": goal,
        "total_calories": calories,
        "macros": {
            "protein_g": protein_g,
            "carbs_g":   max(carbs_g, 50),
            "fats_g":    fats_g,
        },
        "meals": meals_out,
        "supplements": template["supplements"],
        "notes": [
            f"Target {protein_g}g protein daily — prioritise hitting this above all else.",
            "Drink 3–4 litres of water daily.",
            "Adjust portion sizes up or down if weight isn't moving as expected after 2 weeks.",
        ],
    }
