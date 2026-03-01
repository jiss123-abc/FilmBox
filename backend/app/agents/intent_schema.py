from pydantic import BaseModel
from typing import List, Optional

class RecommendationIntent(BaseModel):
    intent: str  # always "recommend_movie"
    genres: Optional[List[str]] = None
    mood: Optional[str] = None
    time_context: Optional[str] = None
    movie_title: Optional[str] = None
    max_runtime: Optional[int] = None      # e.g., 120 (for "under 2 hours")
    min_score: Optional[float] = None      # e.g., 8.0 (for "highly rated")
    language: Optional[str] = None         # e.g., "en", "fr"
    quantity: Optional[int] = None         # e.g., 13 (for "13 highly rated movies")
