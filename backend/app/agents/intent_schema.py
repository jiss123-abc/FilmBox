from pydantic import BaseModel
from typing import List, Optional

class RecommendationIntent(BaseModel):
    intent: str  # always "recommend_movie"
    genres: Optional[List[str]] = None
    mood: Optional[str] = None
    time_context: Optional[str] = None
