from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import List, Dict
from app.agents.conversational_agent import run_conversational_agent_llm

router = APIRouter(prefix="/api/agent", tags=["AI Agent"])

class ConversationalRequest(BaseModel):
    user_id: int
    message: str = Field(..., max_length=500)
    chat_history: List[Dict[str, str]] = []

@router.post("/chat")
def conversational_recommendation_llm(payload: ConversationalRequest):
    """
    Unified AI Agent Chat Endpoint.
    Extracts intent, finds movies, and responds using Gemini.
    """
    return run_conversational_agent_llm(payload.user_id, payload.message, payload.chat_history)
