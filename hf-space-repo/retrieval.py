"""Retrieval module for semantic search in Qdrant."""

from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http import models

import config


class Retriever:
    """Semantic search retriever using Qdrant."""
    
    def __init__(self):
        # Use local sentence-transformers model instead of Gemini
        self.embedding_model_name = config.EMBEDDING_MODEL
        print(f"Loading embedding model: {self.embedding_model_name}")
        self.embedding_model = SentenceTransformer(self.embedding_model_name)
        print(f"Embedding dimension: {self.embedding_model.get_sentence_embedding_dimension()}")
        
        # Connect to Qdrant
        qdrant_url = config.QDRANT_URL
        if qdrant_url == ":memory:":
            # Use in-memory storage for local development
            self.client = QdrantClient(":memory:")
        elif config.QDRANT_API_KEY:
            self.client = QdrantClient(
                url=qdrant_url,
                api_key=config.QDRANT_API_KEY
            )
        else:
            self.client = QdrantClient(url=qdrant_url)
        
        self.collection_name = config.QDRANT_COLLECTION_NAME
    
    def _embed_query(self, query: str) -> List[float]:
        """Generate embedding for query using sentence-transformers."""
        embedding = self.embedding_model.encode(query, convert_to_tensor=False)
        return embedding.tolist()
    
    def search(
        self,
        query: str,
        top_k: int = None,
        score_threshold: float = None
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant passages.
        
        Args:
            query: User's question
            top_k: Number of results to return
            score_threshold: Minimum similarity score
            
        Returns:
            List of relevant passages with metadata and scores
        """
        top_k = top_k or config.TOP_K_RESULTS
        score_threshold = score_threshold or config.SIMILARITY_THRESHOLD
        
        # Embed the query
        query_embedding = self._embed_query(query)
        
        # Search Qdrant
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=top_k,
            score_threshold=score_threshold
        )
        
        # Format results
        passages = []
        for result in results:
            passage = {
                "content": result.payload.get("content", ""),
                "score": result.score,
                "metadata": {
                    "file_path": result.payload.get("file_path", ""),
                    "file_name": result.payload.get("file_name", ""),
                    "module": result.payload.get("module", ""),
                    "title": result.payload.get("title", ""),
                    "chunk_id": result.payload.get("chunk_id", ""),
                    "chunk_idx": result.payload.get("chunk_idx", 0)
                }
            }
            passages.append(passage)
        
        return passages
    
    def search_with_filter(
        self,
        query: str,
        module: str = None,
        top_k: int = None
    ) -> List[Dict[str, Any]]:
        """
        Search with optional module filter.
        
        Args:
            query: User's question
            module: Filter by specific module (e.g., "01-robotic-nervous-system")
            top_k: Number of results
            
        Returns:
            Filtered list of passages
        """
        top_k = top_k or config.TOP_K_RESULTS
        
        # Embed the query
        query_embedding = self._embed_query(query)
        
        # Build filter
        query_filter = None
        if module:
            query_filter = models.Filter(
                must=[
                    models.FieldCondition(
                        key="module",
                        match=models.MatchValue(value=module)
                    )
                ]
            )
        
        # Search with filter
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=top_k,
            query_filter=query_filter
        )
        
        # Format results
        passages = []
        for result in results:
            passage = {
                "content": result.payload.get("content", ""),
                "score": result.score,
                "metadata": {
                    "file_path": result.payload.get("file_path", ""),
                    "file_name": result.payload.get("file_name", ""),
                    "module": result.payload.get("module", ""),
                    "title": result.payload.get("title", ""),
                    "chunk_id": result.payload.get("chunk_id", "")
                }
            }
            passages.append(passage)
        
        return passages
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection."""
        try:
            info = self.client.get_collection(self.collection_name)
            return {
                "collection_name": self.collection_name,
                "vectors_count": info.vectors_count,
                "points_count": info.points_count,
                "status": str(info.status)
            }
        except Exception as e:
            return {
                "error": str(e),
                "collection_name": self.collection_name
            }


# Singleton instance for reuse
_retriever_instance = None


def get_retriever() -> Retriever:
    """Get or create retriever singleton."""
    global _retriever_instance
    if _retriever_instance is None:
        _retriever_instance = Retriever()
    return _retriever_instance


if __name__ == "__main__":
    # Test retrieval
    retriever = get_retriever()
    
    print("Collection stats:", retriever.get_collection_stats())
    
    # Test query
    query = "What is ROS 2?"
    results = retriever.search(query)
    
    print(f"\nQuery: {query}")
    print(f"Results: {len(results)}")
    
    for i, r in enumerate(results):
        print(f"\n--- Result {i+1} (score: {r['score']:.3f}) ---")
        print(f"Source: {r['metadata']['title']}")
        print(f"Content: {r['content'][:200]}...")
