from typing import Literal, Optional

from pydantic import BaseModel


class HistoryMessage(BaseModel):
    session_id: str
    role: Literal["assistant", "user"]
    content: str
    created_at: str


class ChatRequest(BaseModel):
    prompt: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    status: str
    reply: str
    session_id: str
