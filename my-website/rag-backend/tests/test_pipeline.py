"""Tests for RAG pipeline."""

import pytest
from pathlib import Path


class TestMarkdownLoader:
    """Test markdown loading."""
    
    def test_load_files_exists(self):
        """Test that docs directory has markdown files."""
        from ingest import MarkdownLoader
        import config
        
        # Check docs path exists
        assert config.DOCS_PATH.exists(), f"Docs path does not exist: {config.DOCS_PATH}"
        
        # Check for markdown files
        md_files = list(config.DOCS_PATH.rglob("*.md"))
        assert len(md_files) > 0, "No markdown files found"


class TestTextChunker:
    """Test text chunking."""
    
    def test_chunk_document(self):
        """Test document chunking."""
        from ingest import TextChunker, DocumentChunk
        
        chunker = TextChunker(chunk_size=100, chunk_overlap=20)
        
        doc = {
            "file_path": "test.md",
            "file_name": "test",
            "module": "test-module",
            "title": "Test Document",
            "content": "This is a test sentence. " * 50  # ~1200 chars
        }
        
        chunks = chunker.chunk_document(doc)
        
        assert len(chunks) > 1, "Should create multiple chunks"
        assert all(isinstance(c, DocumentChunk) for c in chunks)
        assert all(c.metadata["file_name"] == "test" for c in chunks)


class TestEmbeddingGenerator:
    """Test embedding generation."""
    
    def test_embed_texts(self):
        """Test text embedding."""
        from ingest import EmbeddingGenerator
        
        embedder = EmbeddingGenerator("all-MiniLM-L6-v2")
        
        texts = ["Hello world", "ROS 2 is a robot operating system"]
        embeddings = embedder.embed_texts(texts)
        
        assert len(embeddings) == 2
        assert len(embeddings[0]) == 384  # all-MiniLM-L6-v2 dimension
    
    def test_embed_query(self):
        """Test single query embedding."""
        from ingest import EmbeddingGenerator
        
        embedder = EmbeddingGenerator("all-MiniLM-L6-v2")
        
        embedding = embedder.embed_query("What is ROS 2?")
        
        assert len(embedding) == 384


class TestAPIEndpoints:
    """Test API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        from fastapi.testclient import TestClient
        from main import app
        return TestClient(app)
    
    def test_root(self, client):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        assert "message" in response.json()
    
    def test_health(self, client):
        """Test health endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "qdrant_connected" in data
        assert "openai_configured" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
