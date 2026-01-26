from fastapi import APIRouter
from pydantic import BaseModel

from app.agents.recommendation_agent import run_recommendation_agent

router = APIRouter(prefix="/api/agent", tags=["AI Agent"])


class AgentRequest(BaseModel):
    user_id: int
    message: str


@router.post("/recommend")
def recommend_via_agent(payload: AgentRequest):
    return run_recommendation_agent(
        user_id=payload.user_id,
        message=payload.message
    )
