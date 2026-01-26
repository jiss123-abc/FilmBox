from fastapi import APIRouter
from pydantic import BaseModel
from app.agents.conversational_agent import run_conversational_agent_llm

router = APIRouter(prefix="/api/agent", tags=["Conversational Agent LLM"])

class ConversationalRequest(BaseModel):
    user_id: int
    message: str

@router.post("/llm")
def conversational_recommendation_llm(payload: ConversationalRequest):
    """
    Conversational recommendations with LLM rephrasing.
    """
    return run_conversational_agent_llm(payload.user_id, payload.message)
