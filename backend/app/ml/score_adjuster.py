from typing import List, Dict

def apply_intent_boosts(
    recommendations: List[Dict],
    intent: str | None = None,
    genres: List[str] | None = None,
    mood: str | None = None,
    time_context: str | None = None
) -> List[Dict]:
    """
    Re-rank recommendations using intent-aware boosts.
    Purely deterministic mathematical adjustment.
    """

    for rec in recommendations:
        # Start with current rank/score (default to 1.0)
        score = rec.get("score", 1.0)

        # --- Genre boost ---
        # If user explicitly asked for genres, increase their score
        if genres:
            movie_genres = [g.lower() for g in rec.get("genres", [])]
            for g in genres:
                if g.lower() in movie_genres:
                    score *= 1.25

        # --- Mood boost ---
        if mood == "fun":
            if "Comedy" in rec.get("genres", []) or "Animation" in rec.get("genres", []):
                score *= 1.2

        # --- Time-based boost ---
        runtime = rec.get("runtime")
        if time_context == "tonight" and runtime:
            if runtime <= 100:
                score *= 1.15
            elif runtime >= 150:
                score *= 0.85

        # --- Popularity stability ---
        if rec.get("num_ratings", 0) >= 200:
            score *= 1.05

        rec["final_score"] = round(score, 4)

    # Re-sort list based on updated final_score
    return sorted(
        recommendations,
        key=lambda x: x.get("final_score", 0),
        reverse=True
    )
