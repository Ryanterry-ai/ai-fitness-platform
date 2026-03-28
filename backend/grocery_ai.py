"""grocery_ai.py — structured weekly grocery list from diet goal"""

GROCERY_TEMPLATES = {
    "muscle_gain": {
        "proteins":  ["Chicken breast 2kg", "Whole eggs × 36", "Salmon fillets 500g", "Lean beef mince 500g", "Whey protein (1kg tub)", "Greek yogurt 1kg", "Cottage cheese 500g"],
        "carbs":     ["Oats 1kg", "White rice 2kg", "Sweet potatoes 1kg", "Wholegrain bread (loaf)", "Bananas × 10", "Apples × 6", "Rice cakes (pack)"],
        "fats":      ["Olive oil 500ml", "Peanut butter 500g", "Almonds 200g", "Avocados × 4", "Walnuts 150g"],
        "vegetables":["Broccoli 1kg", "Spinach 500g", "Mixed salad leaves 300g", "Bell peppers × 4", "Cherry tomatoes 400g"],
        "supplements":["Creatine monohydrate 500g", "Whey protein (if not listed)", "Vitamin D3", "Omega-3 fish oil"],
    },
    "fat_loss": {
        "proteins":  ["Chicken breast 1.5kg", "White fish (cod/tilapia) 800g", "Egg whites (carton 1L)", "Whey protein isolate", "Greek yogurt 0% 1kg", "Turkey breast 500g"],
        "carbs":     ["Brown rice 1kg", "Oats 500g", "Sweet potatoes 500g", "Blueberries 400g", "Strawberries 300g", "Apples × 6"],
        "fats":      ["Olive oil 500ml", "Avocados × 4", "Almonds 150g", "Salmon (omega-3 source) 400g"],
        "vegetables":["Broccoli 1kg", "Green beans 500g", "Spinach 500g", "Zucchini × 4", "Asparagus 300g", "Cucumber × 2"],
        "supplements":["Whey isolate", "L-Carnitine", "Caffeine tablets (200mg)", "Omega-3"],
    },
    "recomp": {
        "proteins":  ["Chicken breast 1.5kg", "Eggs × 24", "Salmon 500g", "Lean beef 500g", "Whey protein 1kg"],
        "carbs":     ["Quinoa 500g", "Sweet potatoes 800g", "Oats 500g", "Bananas × 8", "Brown rice 1kg"],
        "fats":      ["Olive oil 500ml", "Walnuts 150g", "Avocados × 4", "Peanut butter 300g"],
        "vegetables":["Broccoli 800g", "Spinach 400g", "Kale 300g", "Bell peppers × 4", "Mixed veg frozen 1kg"],
        "supplements":["Creatine monohydrate", "Whey protein", "Omega-3", "Multivitamin"],
    },
}

def grocery_list(data):
    goal = data.get("goal", "muscle_gain")
    template_key = goal if goal in GROCERY_TEMPLATES else "muscle_gain"
    template = GROCERY_TEMPLATES[template_key]
    return {
        "goal": goal,
        "weekly_list": template,
        "tips": [
            "Buy proteins in bulk and batch-cook 3–4 days at a time",
            "Frozen vegetables are as nutritious as fresh and much cheaper",
            "Cook rice and sweet potatoes in large batches on Sunday",
            "Pre-portion snacks (nuts, yogurt) to avoid overeating",
        ]
    }
