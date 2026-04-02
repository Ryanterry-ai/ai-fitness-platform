"""Embedding Agent - Simple keyword matching"""
from typing import List, Dict, Any

class EmbeddingAgent:
    def __init__(self):
        self.docs: List[Dict] = []

    def add(self, text: str, meta: Dict) -> bool:
        self.docs.append({"text": text, "meta": meta})
        return True

    def search(self, query: str, k: int = 5) -> List[Dict]:
        results = []
        q_lower = query.lower()
        for doc in self.docs:
            score = sum(1 for w in q_lower.split() if w in doc["text"].lower())
            if score > 0:
                results.append({**doc, "score": score})
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:k]

agent = EmbeddingAgent()

def add_document(text: str, meta: Dict) -> bool:
    return agent.add(text, meta)

def search_embeddings(query: str, k: int = 5) -> List[Dict]:
    return agent.search(query, k)
