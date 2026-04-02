
def filter_by_entity(results, entity):
    filtered=[]
    for r in results:
        if entity.lower() in str(r).lower():
            filtered.append(r)
    return filtered
