"""Trusted domains configuration for source verification."""

TRUSTED_DOMAINS = {
    "pubmed.ncbi.nlm.nih.gov": {"name": "PubMed", "tier": "scientific", "trust": 5},
    "ncbi.nlm.nih.gov": {"name": "NCBI", "tier": "scientific", "trust": 5},
    "nih.gov": {"name": "NIH", "tier": "scientific", "trust": 5},
    "who.int": {"name": "WHO", "tier": "scientific", "trust": 5},
    "cdc.gov": {"name": "CDC", "tier": "scientific", "trust": 5},
    "mayoclinic.org": {"name": "Mayo Clinic", "tier": "medical", "trust": 5},
    "webmd.com": {"name": "WebMD", "tier": "medical", "trust": 4},
    "healthline.com": {"name": "Healthline", "tier": "health", "trust": 4},
    "examine.com": {"name": "Examine.com", "tier": "fitness", "trust": 5},
    "bodybuilding.com": {"name": "Bodybuilding.com", "tier": "fitness", "trust": 3},
    "nature.com": {"name": "Nature", "tier": "journal", "trust": 5},
    "health.harvard.edu": {"name": "Harvard Health", "tier": "academic", "trust": 5},
    "clevelandclinic.org": {"name": "Cleveland Clinic", "tier": "medical", "trust": 5},
}
