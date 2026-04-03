"""Web search tool using Zenserp API."""

import os
from urllib.parse import quote
from datetime import datetime, timezone
import requests
from source_verification import verify_source, extract_domain

ZENSERP_API_KEY = os.getenv("ZENSERP_API_KEY", "")

def web_search(query, num_results=10):
    results = {"query": query, "timestamp": datetime.now(timezone.utc).isoformat(), "results": [], "verified_results": [], "total_results": 0, "verified_count": 0}
    if not ZENSERP_API_KEY:
        results["error"] = "Zenserp API key not configured"
        return results
    try:
        url = f"https://app.zenserp.com/api/v2/search?q={quote(query)}&apikey={ZENSERP_API_KEY}&num_results={num_results}"
        resp = requests.get(url, timeout=15)
        if resp.status_code != 200:
            results["error"] = f"API error: {resp.status_code}"
            return results
        data = resp.json()
        organic = data.get("organic", [])
        for item in organic[:num_results]:
            result_url = item.get("url", "")
            domain = extract_domain(result_url)
            verification = verify_source(result_url)
            result_item = {
                "title": item.get("title", ""),
                "url": result_url,
                "snippet": item.get("description", ""),
                "domain": domain,
                "source_type": verification["tier"] or "general",
                "is_verified": verification["verified"],
                "trust_score": verification["trust_score"],
                "verified_source": verification["name"] if verification["verified"] else None
            }
            results["results"].append(result_item)
            if verification["verified"]:
                results["verified_results"].append(result_item)
                results["verified_count"] += 1
        results["total_results"] = len(results["results"])
    except Exception as e:
        results["error"] = str(e)
    return results
