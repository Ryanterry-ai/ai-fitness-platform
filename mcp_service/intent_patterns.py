"""Intent patterns for fitness queries."""

INTENT_PATTERNS = {
    "supplement": {"keywords": ["supplement", "creatine", "protein", "whey", "bcaa", "pre-workout", "vitamin"], "weight": 2},
    "diet": {"keywords": ["diet", "nutrition", "meal plan", "calories", "macros", "keto", "bulking", "cutting"], "weight": 2},
    "workout": {"keywords": ["workout", "exercise", "training", "cardio", "strength", "reps", "sets", "gym"], "weight": 2},
    "compound": {"keywords": ["anavar", "testosterone", "nandrolone", "trenbolone", "sarm", "mk-677", "cycle", "pct"], "weight": 3},
    "medical": {"keywords": ["bloodwork", "blood test", "side effect", "liver", "kidney", "cholesterol", "safe", "dangerous"], "weight": 2},
    "dosage": {"keywords": ["dosage", "dose", "mg", "ml", "iu", "how much", "serving", "loading"], "weight": 3},
}
