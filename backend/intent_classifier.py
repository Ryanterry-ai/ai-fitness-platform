
import re

def classify_intent(query):
    query = query.lower()

    exercise_keywords = ["exercise","workout","training","routine","split","fat loss","cardio"]
    supplement_keywords = ["creatine","whey","protein","pre workout","supplement"]
    ped_keywords = ["sarm","steroid","mk","ostarine","tren","testosterone"]
    diet_keywords = ["diet","meal","calorie","nutrition"]

    if any(k in query for k in exercise_keywords):
        return "exercise"
    if any(k in query for k in supplement_keywords):
        return "supplement"
    if any(k in query for k in ped_keywords):
        return "ped"
    if any(k in query for k in diet_keywords):
        return "diet"

    return "general"
