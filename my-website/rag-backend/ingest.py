"""Data ingestion pipeline for RAG chatbot.

Loads markdown files, chunks content, generates embeddings via Gemini, and stores in Qdrant.
"""

import os
import re
import time
from pathlib import Path
from typing import List, Dict, Any
import frontmatter
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct

import config


class DocumentChunk:
    """Represents a chunk of document content."""
    
    def __init__(
        self,
        content: str,
        metadata: Dict[str, Any],
        chunk_id: str
    ):
        self.content = content
        self.metadata = metadata
        self.chunk_id = chunk_id


class MarkdownLoader:
    """Load and parse markdown files from docs directory."""
    
    def __init__(self, docs_path: Path):
        self.docs_path = docs_path
    
    def load_all_files(self) -> List[Dict[str, Any]]:
        """Load all markdown files from docs directory."""
        documents = []
        
        for md_file in self.docs_path.rglob("*.md"):
            doc = self._load_file(md_file)
            if doc:
                documents.append(doc)
        
        print(f"Loaded {len(documents)} markdown files")
        return documents
    
    def _load_file(self, file_path: Path) -> Dict[str, Any] | None:
        """Load a single markdown file with frontmatter."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                post = frontmatter.load(f)
            
            # Extract module from path
            relative_path = file_path.relative_to(self.docs_path)
            parts = relative_path.parts
            module = parts[0] if len(parts) > 1 else "general"
            
            return {
                "file_path": str(relative_path),
                "file_name": file_path.stem,
                "module": module,
                "title": post.get("sidebar_label", file_path.stem),
                "content": post.content,
                "metadata": dict(post.metadata)
            }
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            return None


class TextChunker:
    """Split text into overlapping chunks."""
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def chunk_document(self, document: Dict[str, Any]) -> List[DocumentChunk]:
        """Split document into chunks."""
        content = document["content"]
        
        # Clean markdown: remove code blocks for better semantic search
        content = self._clean_content(content)
        
        # Split into sentences first
        sentences = self._split_into_sentences(content)
        
        chunks = []
        current_chunk = []
        current_length = 0
        chunk_idx = 0
        
        for sentence in sentences:
            sentence_len = len(sentence)
            
            if current_length + sentence_len > self.chunk_size and current_chunk:
                # Save current chunk
                chunk_text = " ".join(current_chunk)
                chunk_id = f"{document['file_name']}_{chunk_idx}"
                
                chunks.append(DocumentChunk(
                    content=chunk_text,
                    metadata={
                        "file_path": document["file_path"],
                        "file_name": document["file_name"],
                        "module": document["module"],
                        "title": document["title"],
                        "chunk_idx": chunk_idx
                    },
                    chunk_id=chunk_id
                ))
                
                # Start new chunk with overlap
                overlap_sentences = self._get_overlap_sentences(
                    current_chunk, self.chunk_overlap
                )
                current_chunk = overlap_sentences
                current_length = sum(len(s) for s in current_chunk)
                chunk_idx += 1
            
            current_chunk.append(sentence)
            current_length += sentence_len
        
        # Don't forget the last chunk
        if current_chunk:
            chunk_text = " ".join(current_chunk)
            chunk_id = f"{document['file_name']}_{chunk_idx}"
            
            chunks.append(DocumentChunk(
                content=chunk_text,
                metadata={
                    "file_path": document["file_path"],
                    "file_name": document["file_name"],
                    "module": document["module"],
                    "title": document["title"],
                    "chunk_idx": chunk_idx
                },
                chunk_id=chunk_id
            ))
        
        return chunks
    
    def _clean_content(self, content: str) -> str:
        """Clean markdown content for better embeddings."""
        # Remove code blocks but keep inline code
        content = re.sub(r"```[\s\S]*?```", " [code block] ", content)
        # Remove mermaid diagrams
        content = re.sub(r"```mermaid[\s\S]*?```", " [diagram] ", content)
        # Remove HTML comments
        content = re.sub(r"<!--[\s\S]*?-->", "", content)
        # Remove excessive whitespace
        content = re.sub(r"\n{3,}", "\n\n", content)
        content = re.sub(r" {2,}", " ", content)
        # Remove markdown links but keep text
        content = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", content)
        # Remove images
        content = re.sub(r"!\[([^\]]*)\]\([^)]+\)", "", content)
        
        return content.strip()
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        sentences = re.split(r"(?<=[.!?])\s+", text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _get_overlap_sentences(
        self, sentences: List[str], target_length: int
    ) -> List[str]:
        """Get sentences for overlap from end of chunk."""
        overlap = []
        current_len = 0
        
        for sentence in reversed(sentences):
            if current_len + len(sentence) > target_length:
                break
            overlap.insert(0, sentence)
            current_len += len(sentence)
        
        return overlap


class EmbeddingGenerator:
    """Generate embeddings using Sentence Transformers (local)."""
    
    def __init__(self, model_name: str = config.EMBEDDING_MODEL):
        self.model = SentenceTransformer(model_name)
        self.dimension = config.EMBEDDING_DIMENSION
        print(f"Using local embeddings: {model_name}")
        print(f"Embedding dimension: {self.dimension}")
    
    def embed_texts(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """Generate embeddings for a list of texts."""
        all_embeddings = []
        
        # SentenceTransformer handles batching internally efficiently, 
        # but we can explicit batch if needed.
        # encode returns numpy array, convert to list
        embeddings = self.model.encode(texts, batch_size=batch_size, show_progress_bar=True)
        return embeddings.tolist()
    
    def embed_query(self, query: str) -> List[float]:
        """Generate embedding for a single query."""
        embedding = self.model.encode(query)
        return embedding.tolist()


class QdrantStore:
    """Store and retrieve embeddings from Qdrant."""
    
    def __init__(
        self,
        url: str = None,
        api_key: str = None,
        collection_name: str = "documents"
    ):
        self.collection_name = collection_name
        
        # Connect to Qdrant
        if url == ":memory:":
            # Use in-memory storage for local development
            self.client = QdrantClient(":memory:")
            print("Connected to Qdrant (in-memory mode)")
        elif api_key:
            self.client = QdrantClient(url=url, api_key=api_key)
            print(f"Connected to Qdrant at {url}")
        else:
            self.client = QdrantClient(url=url)
            print(f"Connected to Qdrant at {url}")
    
    def create_collection(self, dimension: int):
        """Create collection if it doesn't exist."""
        collections = self.client.get_collections().collections
        collection_names = [c.name for c in collections]
        
        if self.collection_name in collection_names:
            print(f"Collection '{self.collection_name}' already exists, recreating...")
            self.client.delete_collection(self.collection_name)
        
        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(
                size=dimension,
                distance=Distance.COSINE
            )
        )
        print(f"Created collection '{self.collection_name}' with dimension {dimension}")
    
    def upsert_chunks(
        self,
        chunks: List[DocumentChunk],
        embeddings: List[List[float]]
    ):
        """Upsert chunks with embeddings to Qdrant."""
        points = []
        
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            point = PointStruct(
                id=i,
                vector=embedding,
                payload={
                    "content": chunk.content,
                    "chunk_id": chunk.chunk_id,
                    **chunk.metadata
                }
            )
            points.append(point)
        
        # Upsert in batches
        batch_size = 20
        for i in range(0, len(points), batch_size):
            batch = points[i:i + batch_size]
            self.client.upsert(
                collection_name=self.collection_name,
                points=batch
            )
            print(f"Upserted batch {i // batch_size + 1}/{(len(points) - 1) // batch_size + 1}")
        
        print(f"Total points upserted: {len(points)}")
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get collection statistics."""
        info = self.client.get_collection(self.collection_name)
        return {
            "name": self.collection_name,
            "vectors_count": info.vectors_count,
            "points_count": info.points_count,
            "status": info.status
        }


def run_ingestion():
    """Run the full ingestion pipeline."""
    print("=" * 50)
    print("RAG Ingestion Pipeline")
    print("=" * 50)
    
    # 1. Load documents
    print("\n[1/4] Loading documents...")
    loader = MarkdownLoader(config.DOCS_PATH)
    documents = loader.load_all_files()
    
    if not documents:
        print("No documents found!")
        return
    
    # 2. Chunk documents
    print("\n[2/4] Chunking documents...")
    chunker = TextChunker(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP
    )
    
    all_chunks = []
    for doc in documents:
        chunks = chunker.chunk_document(doc)
        all_chunks.extend(chunks)
        print(f"  - {doc['file_name']}: {len(chunks)} chunks")
    
    print(f"Total chunks: {len(all_chunks)}")
    
    # 3. Generate embeddings
    print("\n[3/4] Generating embeddings via Gemini API...")
    embedder = EmbeddingGenerator(config.EMBEDDING_MODEL)
    
    texts = [chunk.content for chunk in all_chunks]
    embeddings = embedder.embed_texts(texts)
    
    # 4. Store in Qdrant
    print("\n[4/4] Storing in Qdrant...")
    store = QdrantStore(
        url=config.QDRANT_URL,
        api_key=config.QDRANT_API_KEY if config.QDRANT_API_KEY else None,
        collection_name=config.QDRANT_COLLECTION_NAME
    )
    
    store.create_collection(dimension=embedder.dimension)
    store.upsert_chunks(all_chunks, embeddings)
    
    # Print summary
    info = store.get_collection_info()
    print("\n" + "=" * 50)
    print("Ingestion Complete!")
    print("=" * 50)
    print(f"Collection: {info['name']}")
    print(f"Total vectors: {info['vectors_count']}")
    print(f"Status: {info['status']}")


if __name__ == "__main__":
    run_ingestion()
