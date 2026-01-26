from fastapi import APIRouter
from pydantic import BaseModel
from app.agents.conversational_agent import run_conversational_agent

router = APIRouter(prefix="/api/agent", tags=["Conversational Agent"])


class ConversationalRequest(BaseModel):
    user_id: int
    message: str


@router.post("/conversational")
def conversational_recommendation(payload: ConversationalRequest):
    """
    Returns conversational recommendations using the agent.
    """
    return run_conversational_agent(
        user_id=payload.user_id,
        message=payload.message
    )
