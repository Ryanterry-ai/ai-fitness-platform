
def classify_intent(query: str):
    query = query.lower()

    exercise_keywords = [
        "exercise","workout","training","routine","fat loss",
        "cardio","hiit","home workout","gym workout"
    ]

    supplement_keywords = [
        "creatine","whey","protein","pre workout",
        "bcaa","mass gainer","supplement"
    ]

    ped_keywords = [
        "sarm","steroid","cycle","mk-2866",
        "testosterone","tren","anavar","performance enhancing"
    ]

    diet_keywords = [
        "diet","nutrition","meal plan",
        "calories","macro"
    ]

    for word in exercise_keywords:
        if word in query:
            return "exercise"

    for word in supplement_keywords:
        if word in query:
            return "supplement"

    for word in ped_keywords:
        if word in query:
            return "ped"

    for word in diet_keywords:
        if word in query:
            return "diet"

    return "general"
