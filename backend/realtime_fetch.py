
def fetch_realtime_results(query, domain):
    if domain == "exercise":
        return [
            {"title":"HIIT Training","category":"exercise","evidence":"High"},
            {"title":"Squats","category":"exercise","evidence":"High"},
            {"title":"Walking Lunges","category":"exercise","evidence":"Moderate"}
        ]
    return []
