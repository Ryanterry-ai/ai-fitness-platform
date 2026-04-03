"""Source verification tool."""

import os
from urllib.parse import urlparse
from trusted_domains import TRUSTED_DOMAINS

def extract_domain(url):
    try:
        return urlparse(url).netloc.replace("www.", "").lower()
    except:
        return ""

def verify_source(url):
    if not url:
        return {"verified": False, "trust_score": 0, "tier": None, "name": None}
    try:
        domain = extract_domain(url)
        if domain in TRUSTED_DOMAINS:
            info = TRUSTED_DOMAINS[domain]
            return {"verified": True, "trust_score": info["trust"], "tier": info["tier"], "name": info["name"], "domain": domain}
        for trusted, info in TRUSTED_DOMAINS.items():
            if trusted in domain or domain in trusted:
                return {"verified": True, "trust_score": info["trust"], "tier": info["tier"], "name": info["name"], "domain": domain}
        return {"verified": False, "trust_score": 1, "tier": "general", "name": domain[:30] if domain else "Unknown", "domain": domain}
    except:
        return {"verified": False, "trust_score": 0, "tier": None, "name": None}
