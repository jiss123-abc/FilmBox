def apply_taste_bias(
    movies: list[dict],
    genre_weights: dict[str, float]
) -> list[dict]:
    """
    Adjusts movie scores based on user genre preferences.
    This nudges the ranking without completely overriding the base strategy.
    """
    for movie in movies:
        # Ensure score exists
        current_score = movie.get("score", 0.0)
        if current_score is None:
            current_score = 0.0
            
        bias = 0.0
        # Handle genres being a list of strings or list of objects if raw from DB
        # Assuming dicts with 'genres' as list of names (str) usually
        genres = movie.get("genres", [])
        
        for genre in genres:
            # If genre is an object with .name, handle it (defensive coding)
            genre_name = genre
            if hasattr(genre, "name"):
                genre_name = genre.name
            
            # Add weight if exists
            bias += genre_weights.get(genre_name, 0.0)

        movie["score"] = current_score + bias

    # Return sorted by new score
    return sorted(movies, key=lambda x: x["score"], reverse=True)
