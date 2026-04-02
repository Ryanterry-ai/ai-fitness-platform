"""
Embedding Agent - Stub implementation (vector embeddings optional)
"""
from typing import List, Dict, Any

class EmbeddingAgent:
    """Simple TF-IDF based embedding (numpy optional for advanced features)"""
    
    def __init__(self):
        self.documents: List[Dict[str, Any]] = []
        self.enabled = False

    def add_document(self, text: str, metadata: Dict[str, Any]) -> bool:
        self.documents.append({"text": text, "metadata": metadata})
        return True

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        # Simple keyword matching fallback
        results = []
        query_lower = query.lower()
        for doc in self.documents:
            text_lower = doc["text"].lower()
            score = sum(1 for word in query_lower.split() if word in text_lower)
            if score > 0:
                results.append({"text": doc["text"], "metadata": doc["metadata"], "score": score})
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    def get_stats(self) -> Dict[str, Any]:
        return {"documents": len(self.documents), "enabled": self.enabled}


agent = EmbeddingAgent()

def add_document(text: str, metadata: Dict[str, Any]) -> bool:
    return agent.add_document(text, metadata)

def search_embeddings(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    return agent.search(query, top_k)

def get_embedding_stats() -> Dict[str, Any]:
    return agent.get_stats()
