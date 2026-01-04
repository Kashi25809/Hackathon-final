"""FastAPI backend for RAG chatbot."""

from contextlib import asynccontextmanager
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import config
from models import ChatRequest, ChatMessage  # Import shared models


class Source(BaseModel):
    """Source citation model."""
    title: str
    file_path: str
    module: str
    score: float


class ChatResponse(BaseModel):
    """Chat response model."""
    answer: str
    sources: List[Source]
    query: str
    model: Optional[str] = None


class IngestResponse(BaseModel):
    """Ingestion response model."""
    status: str
    message: str
    documents_processed: int
    chunks_created: int


class StatsResponse(BaseModel):
    """Collection statistics response."""
    collection_name: str
    vectors_count: int
    points_count: int
    status: str


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    qdrant_connected: bool
    openai_configured: bool


# Lazy loading for heavy modules
_generator = None
_retriever = None


def get_generator():
    """Lazy load the generator."""
    global _generator
    if _generator is None:
        from generation import get_generator as load_generator
        _generator = load_generator()
    return _generator


def get_retriever():
    """Lazy load the retriever."""
    global _retriever
    if _retriever is None:
        from retrieval import get_retriever as load_retriever
        _retriever = load_retriever()
    return _retriever


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    print("RAG Chatbot API starting...")
    print(f"Docs path: {config.DOCS_PATH}")
    print(f"Qdrant URL: {config.QDRANT_URL}")
    print(f"Embedding model: {config.EMBEDDING_MODEL}")
    
    # Initialize Database
    from database import init_db
    init_db()
    
    # Auto-ingest if collection is empty
    try:
        retriever = get_retriever()
        stats = retriever.get_collection_stats()
        if "error" in stats or stats.get("vectors_count", 0) == 0:
            print("Collection missing or empty. Starting initial ingestion...")
            from ingest import run_ingestion
            run_ingestion()
    except Exception as e:
        print(f"Startup ingestion check failed: {e}")
    
    yield
    # Shutdown
    print("RAG Chatbot API shutting down...")


# Create FastAPI app
app = FastAPI(
    title="RAG Chatbot API",
    description="Retrieval-Augmented Generation chatbot for Physical AI & Humanoid Robotics textbook",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint."""
    return {
        "message": "RAG Chatbot API for Physical AI & Humanoid Robotics",
        "docs_url": "/docs",
        "health_url": "/health"
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Check API health status."""
    qdrant_ok = False
    openai_ok = bool(config.GEMINI_API_KEY) # Check Gemini key
    
    try:
        retriever = get_retriever()
        stats = retriever.get_collection_stats()
        qdrant_ok = "error" not in stats
    except Exception:
        pass
    
    return HealthResponse(
        status="healthy" if (qdrant_ok and openai_ok) else "degraded",
        qdrant_connected=qdrant_ok,
        openai_configured=openai_ok
    )


@app.get("/stats", response_model=StatsResponse, tags=["Admin"])
async def get_stats():
    """Get vector collection statistics."""
    try:
        retriever = get_retriever()
        stats = retriever.get_collection_stats()
        
        if "error" in stats:
            raise HTTPException(status_code=503, detail=stats["error"])
        
        return StatsResponse(
            collection_name=stats["collection_name"],
            vectors_count=stats.get("vectors_count", 0),
            points_count=stats.get("points_count", 0),
            status=stats.get("status", "unknown")
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ingest", response_model=IngestResponse, tags=["Admin"])
async def ingest_documents():
    """
    Ingest/re-ingest all documents from the docs folder.
    """
    try:
        from ingest import (
            MarkdownLoader, TextChunker, EmbeddingGenerator, QdrantStore, run_ingestion
        )
        
        # We can just run the main ingestion function logic or call it directly if refactored
        # For valid response, we'll replicate logic briefly or call a shared function
        # Since run_ingestion prints to stdout, let's reuse the logic like before
        
        # Load documents
        loader = MarkdownLoader(config.DOCS_PATH)
        documents = loader.load_all_files()
        
        if not documents:
            return IngestResponse(
                status="warning",
                message="No documents found in docs directory",
                documents_processed=0,
                chunks_created=0
            )
        
        # Chunk documents
        chunker = TextChunker(
            chunk_size=config.CHUNK_SIZE,
            chunk_overlap=config.CHUNK_OVERLAP
        )
        
        all_chunks = []
        for doc in documents:
            chunks = chunker.chunk_document(doc)
            all_chunks.extend(chunks)
        
        # Generate embeddings
        embedder = EmbeddingGenerator(config.EMBEDDING_MODEL)
        texts = [chunk.content for chunk in all_chunks]
        embeddings = embedder.embed_texts(texts)
        
        # Store in Qdrant
        store = QdrantStore(
            url=config.QDRANT_URL,
            api_key=config.QDRANT_API_KEY if config.QDRANT_API_KEY else None,
            collection_name=config.QDRANT_COLLECTION_NAME
        )
        
        store.create_collection(dimension=embedder.dimension)
        store.upsert_chunks(all_chunks, embeddings)
        
        # Reset singletons
        global _generator, _retriever
        _generator = None
        _retriever = None
        
        return IngestResponse(
            status="success",
            message=f"Successfully ingested {len(documents)} documents",
            documents_processed=len(documents),
            chunks_created=len(all_chunks)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest):
    """
    Chat with the RAG system.
    """
    import time
    from fastapi import Depends
    from sqlalchemy.orm import Session
    from database import get_db, save_chat_log
    
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    start_time = time.time()
    
    try:
        generator = get_generator()
        response = generator.generate_response(
            query=request.query,
            messages=request.messages, # Pass history
            top_k=request.top_k,
            include_sources=request.include_sources
        )
        
        sources = [
            Source(
                title=s["title"],
                file_path=s["file_path"],
                module=s["module"],
                score=s["score"]
            )
            for s in response["sources"]
        ]
        
        # Save to Database
        try:
            # We create a new session just for logging to handle it safely inside the async route
            # Alternatively we could use Depends(get_db) if we changed the signature, 
            # but usually it's better to keep it clean or use a middleware.
            # Here we'll just quickly instantiate for the log.
            from database import SessionLocal
            if SessionLocal:
                db = SessionLocal()
                save_chat_log(
                    db=db,
                    query=request.query,
                    answer=response["answer"],
                    model=response.get("model", "unknown"),
                    time_taken=time.time() - start_time,
                    sources_count=len(sources)
                )
                db.close()
        except Exception as e:
            print(f"Failed to log to DB: {e}")
        
        return ChatResponse(
            answer=response["answer"],
            sources=sources,
            query=response["query"],
            model=response.get("model")
        )
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search", tags=["Search"])
async def search(query: str, top_k: int = 5, module: Optional[str] = None):
    """
    Search for relevant passages without generating a response.
    """
    if not query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    try:
        retriever = get_retriever()
        
        if module:
            results = retriever.search_with_filter(query, module=module, top_k=top_k)
        else:
            results = retriever.search(query, top_k=top_k)
        
        return {
            "query": query,
            "results": results,
            "count": len(results)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
