from backend.search_ai import KNOWLEDGE_BASE


# Flatten Knowledge Base (Handle Multiple Structures)
COMPOUND_INDEX = {}

try:
    # Case 1: Nested dictionary (category -> items)
    for category, items in KNOWLEDGE_BASE.items():
        if isinstance(items, dict):
            for name, data in items.items():
                COMPOUND_INDEX[name.lower()] = {
                    "name": name,
                    "category": category,
                    **data
                }

        # Case 2: List structure
        elif isinstance(items, list):
            for item in items:
                name = item.get("name", "").lower()
                if name:
                    COMPOUND_INDEX[name] = item

except Exception as e:
    print("Knowledge base loading warning:", str(e))


def compare_supplements(compounds, user=None):

    results = []

    for compound in compounds:
        item = COMPOUND_INDEX.get(compound.lower())

        if item:
            results.append(item)
        else:
            results.append({
                "name": compound,
                "category": "unknown",
                "benefits": [],
                "side_effects": [],
                "best_for": []
            })

    return {
        "comparison": results,
        "recommended": compounds[0] if compounds else None
    }
