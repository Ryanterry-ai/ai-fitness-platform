"""
Embedding Agent
===============
Manages vector embeddings for semantic search.
"""

import os
import json
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from config import settings


class EmbeddingAgent:
    """
    Agent responsible for managing embeddings and semantic search.
    
    Responsibilities:
    - Generate embeddings for documents
    - Store embeddings in vector database
    - Perform similarity search
    - Enable semantic search capabilities
    """
    
    def __init__(self, persist_dir: Optional[str] = None):
        self.persist_dir = persist_dir or settings.CHROMA_PERSIST_DIR
        self.embedding_model = settings.EMBEDDING_MODEL
        self.embeddings = {}  # In-memory store
        self.metadata = {}   # Document metadata
        self._load_persisted()
    
    def _load_persisted(self) -> None:
        """Load persisted embeddings"""
        embeddings_file = os.path.join(self.persist_dir, "embeddings.json")
        metadata_file = os.path.join(self.persist_dir, "metadata.json")
        
        if os.path.exists(embeddings_file):
            try:
                with open(embeddings_file, 'r') as f:
                    data = json.load(f)
                    self.embeddings = {
                        k: np.array(v) for k, v in data.get("embeddings", {}).items()
                    }
            except Exception as e:
                print(f"Error loading embeddings: {e}")
        
        if os.path.exists(metadata_file):
            try:
                with open(metadata_file, 'r') as f:
                    self.metadata = json.load(f)
            except Exception as e:
                print(f"Error loading metadata: {e}")
    
    def _persist(self) -> None:
        """Persist embeddings to disk"""
        os.makedirs(self.persist_dir, exist_ok=True)
        
        embeddings_file = os.path.join(self.persist_dir, "embeddings.json")
        metadata_file = os.path.join(self.persist_dir, "metadata.json")
        
        try:
            # Save embeddings as lists (numpy arrays aren't JSON serializable)
            embeddings_data = {
                k: v.tolist() for k, v in self.embeddings.items()
            }
            
            with open(embeddings_file, 'w') as f:
                json.dump({"embeddings": embeddings_data}, f)
            
            with open(metadata_file, 'w') as f:
                json.dump(self.metadata, f)
                
        except Exception as e:
            print(f"Error persisting embeddings: {e}")
    
    def _generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding for text.
        
        Note: In production, this would call OpenAI or Anthropic embedding API.
        For now, we use a simple TF-IDF-like approach as fallback.
        """
        # Check for API keys
        if settings.OPENAI_API_KEY:
            return self._generate_openai_embedding(text)
        elif settings.ANTHROPIC_API_KEY:
            return self._generate_anthropic_embedding(text)
        
        # Fallback: Simple hash-based embedding
        return self._generate_simple_embedding(text)
    
    def _generate_openai_embedding(self, text: str) -> np.ndarray:
        """Generate embedding using OpenAI API"""
        try:
            import openai
            
            response = openai.Embedding.create(
                model=self.embedding_model,
                input=text
            )
            
            embedding = response['data'][0]['embedding']
            return np.array(embedding)
            
        except Exception as e:
            print(f"OpenAI embedding error: {e}")
            return self._generate_simple_embedding(text)
    
    def _generate_anthropic_embedding(self, text: str) -> np.ndarray:
        """Generate embedding using Anthropic (via OpenAI-compatible endpoint)"""
        # Anthropic doesn't have a direct embedding API, use OpenAI if available
        if settings.OPENAI_API_KEY:
            return self._generate_openai_embedding(text)
        return self._generate_simple_embedding(text)
    
    def _generate_simple_embedding(self, text: str) -> np.ndarray:
        """
        Generate simple embedding using word frequency.
        This is a fallback and not suitable for production.
        """
        # Simple TF-IDF-like embedding
        words = text.lower().split()
        vector = np.zeros(256)
        
        for i, word in enumerate(words[:256]):
            hash_val = hash(word) % 256
            vector[hash_val] += 1
        
        # Normalize
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
        
        return vector
    
    def add_document(
        self,
        doc_id: str,
        text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Add a document and its embedding.
        
        Args:
            doc_id: Unique document ID
            text: Document text
            metadata: Optional document metadata
            
        Returns:
            True if added successfully
        """
        try:
            embedding = self._generate_embedding(text)
            self.embeddings[doc_id] = embedding
            self.metadata[doc_id] = {
                "text": text[:1000],  # Store truncated text
                "metadata": metadata or {},
                "created_at": datetime.utcnow().isoformat()
            }
            self._persist()
            return True
            
        except Exception as e:
            print(f"Error adding document: {e}")
            return False
    
    def add_documents(self, documents: List[Dict[str, Any]]) -> int:
        """
        Add multiple documents.
        
        Args:
            documents: List of dicts with 'id', 'text', and optional 'metadata'
            
        Returns:
            Number of documents added successfully
        """
        count = 0
        for doc in documents:
            if self.add_document(
                doc.get("id", f"doc_{count}"),
                doc.get("text", ""),
                doc.get("metadata")
            ):
                count += 1
        return count
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        threshold: float = 0.5
    ) -> List[Tuple[str, float, Dict[str, Any]]]:
        """
        Search for similar documents.
        
        Args:
            query: Search query
            top_k: Number of results to return
            threshold: Minimum similarity threshold
            
        Returns:
            List of tuples (doc_id, similarity_score, metadata)
        """
        try:
            query_embedding = self._generate_embedding(query)
            
            results = []
            for doc_id, doc_embedding in self.embeddings.items():
                similarity = self._cosine_similarity(query_embedding, doc_embedding)
                
                if similarity >= threshold:
                    metadata = self.metadata.get(doc_id, {})
                    results.append((doc_id, float(similarity), metadata))
            
            # Sort by similarity
            results.sort(key=lambda x: x[1], reverse=True)
            
            return results[:top_k]
            
        except Exception as e:
            print(f"Search error: {e}")
            return []
    
    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        dot_product = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return dot_product / (norm_a * norm_b)
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete a document and its embedding"""
        try:
            if doc_id in self.embeddings:
                del self.embeddings[doc_id]
            if doc_id in self.metadata:
                del self.metadata[doc_id]
            self._persist()
            return True
        except Exception as e:
            print(f"Error deleting document: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get embedding statistics"""
        return {
            "total_documents": len(self.embeddings),
            "embedding_dimensions": 256,  # Our fallback dimension
            "embedding_model": self.embedding_model,
            "metadata_fields": list(set(
                field
                for meta in self.metadata.values()
                for field in (meta.get("metadata", {}) or {}).keys()
            ))
        }


# Singleton instance
embedding_agent = EmbeddingAgent()


def add_document(
    doc_id: str,
    text: str,
    metadata: Optional[Dict[str, Any]] = None
) -> bool:
    """Add a document to the embedding store"""
    return embedding_agent.add_document(doc_id, text, metadata)


def search_embeddings(query: str, top_k: int = 5) -> List[Tuple[str, float, Dict[str, Any]]]:
    """Search for similar documents"""
    return embedding_agent.search(query, top_k)


def get_embedding_stats() -> Dict[str, Any]:
    """Get embedding statistics"""
    return embedding_agent.get_stats()
