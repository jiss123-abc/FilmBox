GENRE_SYNONYMS = {
    "animated": "Animation",
    "cartoon": "Animation",
    "kids": "Animation",
    "funny": "Comedy",
    "romcom": "Romance",
    "scifi": "Sci-Fi",
    "science fiction": "Sci-Fi",
    "thriller": "Thriller",
    "crime": "Crime",
}

def normalize_genres(genres: list[str]) -> list[str]:
    """
    Maps common synonyms and loose strings to official MovieLens genre names.
    Ensures that intent extraction matches database categories.
    """
    normalized = []
    for g in genres:
        key = g.lower().strip()
        # Get from synonym map, or use title case as a safe default
        normalized.append(GENRE_SYNONYMS.get(key, g.title()))
    return normalized
