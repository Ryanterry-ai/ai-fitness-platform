
def route_domain(intent):
    routes = {
        "exercise": "exercise_db",
        "supplement": "supplement_db",
        "ped": "ped_db",
        "diet": "diet_db",
        "general": "general_db"
    }
    return routes.get(intent, "general_db")
