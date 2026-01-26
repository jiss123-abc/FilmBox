from typing import Dict, Any, List

from app.ml.recommender_interface import get_hybrid_recommendations


def run_recommendation_agent(user_id: int, message: str, genres: list[str] | None = None) -> Dict[str, Any]:
    """
    Deterministic recommendation agent.
    Orchestrates recommendation logic and formats explanations.
    """

    recommendations = get_hybrid_recommendations(user_id, genres=genres)

    if not recommendations:
        return {
            "response": "I don’t have enough information yet. Try rating a few movies first.",
            "recommendations": [],
            "strategy": "none"
        }

    formatted_movies: List[Dict[str, Any]] = []

    for movie in recommendations:
        formatted_movies.append({
            "movie_id": movie["movie_id"],
            "title": movie["title"],
            "explanation": movie["explanation"]
        })

    top_movie = formatted_movies[0]

    response_text = (
        f"I recommend **{top_movie['title']}**. "
        f"{top_movie['explanation']}"
    )

    return {
        "response": response_text,
        "recommendations": formatted_movies,
        "strategy": recommendations[0]["strategy"]
    }
