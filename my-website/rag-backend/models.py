"""Chat request models."""
from typing import List, Optional
from pydantic import BaseModel

class ChatMessage(BaseModel):
    """Chat message model."""
    role: str
    content: str

class ChatRequest(BaseModel):
    """Chat request model with history."""
    query: str
    messages: Optional[List[ChatMessage]] = []
    top_k: Optional[int] = 5
    include_sources: Optional[bool] = True
