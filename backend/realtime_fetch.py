
import requests

def fetch_realtime(query):
    try:
        # placeholder for real-time API
        return {
            "query": query,
            "results": [
                {"title": "Sample Real Time Result", "source": "live_api"}
            ]
        }
    except:
        return {"results": []}
