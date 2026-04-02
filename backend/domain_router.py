
def route_domain(intent):

    mapping = {
        "exercise": "exercise",
        "supplement": "supplement",
        "ped": "ped",
        "diet": "diet",
        "general": "general"
    }

    return mapping.get(intent, "general")
