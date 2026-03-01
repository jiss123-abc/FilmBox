import re

# Simple keyword mapping for TMDb genres
GENRE_MAP = {
    "action": "Action",
    "comedy": "Comedy",
    "comedies": "Comedy",
    "drama": "Drama",
    "dramas": "Drama",
    "thriller": "Thriller",
    "thrillers": "Thriller",
    "horror": "Horror",
    "horrors": "Horror",
    "sci-fi": "Sci-Fi",
    "scifi": "Sci-Fi",
    "science fiction": "Sci-Fi",
    "mystery": "Mystery",
    "mysteries": "Mystery",
    "romance": "Romance",
    "romantic": "Romance",
    "fantasy": "Fantasy",
    "documentary": "Documentary",
    "documentaries": "Documentary",
    "animation": "Animation",
    "anime": "Animation",
    "crime": "Crime",
    "family": "Family",
    "history": "History",
    "music": "Music",
    "war": "War",
    "western": "Western"
}

# Common ISO 639-1 language codes for movie filtering
LANGUAGE_MAP = {
    "hindi": "hi",
    "english": "en",
    "french": "fr",
    "spanish": "es",
    "german": "de",
    "italian": "it",
    "japanese": "ja",
    "korean": "ko",
    "chinese": "zh",
    "mandarin": "zh",
    "tamil": "ta",
    "telugu": "te",
    "kannada": "kn",
    "malayalam": "ml",
    "bengali": "bn",
    "punjabi": "pa",
    "russian": "ru",
    "portuguese": "pt"
}

def parse_user_filters(message: str) -> dict:
    """
    Extracts deterministic filters from a user message.
    Returns a dict with: genres, max_runtime, min_year, language, min_score
    """
    msg_lower = message.lower()
    filters = {
        "genres": [],
        "max_runtime": None,
        "min_year": None,
        "language": None,
        "min_score": None,
        "max_score": None
    }

    # 1. Parse Genres
    extracted_genres = set()
    for kw, genre in GENRE_MAP.items():
        # Allow optional plural s or es
        if re.search(r'\b' + kw + r'(?:s|es|ies)?\b', msg_lower):
            extracted_genres.add(genre)
    if extracted_genres:
        filters["genres"] = list(extracted_genres)

    # 2. Parse Language
    for kw, lang_code in LANGUAGE_MAP.items():
        if re.search(r'\b' + kw + r'\b', msg_lower):
            filters["language"] = lang_code
            break # Just take the first one found

    # 3. Parse Runtime
    if "short" in msg_lower:
        filters["max_runtime"] = 100
        
    # under X hours / mins
    hr_match = re.search(r'under (\d+(?:\.\d+)?)\s*hour', msg_lower)
    if hr_match:
        filters["max_runtime"] = int(float(hr_match.group(1)) * 60)
        
    min_match = re.search(r'under (\d+)\s*min', msg_lower)
    if min_match:
        filters["max_runtime"] = int(min_match.group(1))

    # 4. Parse Year
    if "newer" in msg_lower or "recent" in msg_lower:
        filters["min_year"] = 2015
        
    year_match = re.search(r'(?:after|since|from)\s*(\d{4})', msg_lower)
    if year_match:
        filters["min_year"] = int(year_match.group(1))
        
    # Decade match (e.g., 90s, 80s)
    if re.search(r'\b90s\b', msg_lower):
        filters["min_year"] = 1990
    elif re.search(r'\b80s\b', msg_lower):
        filters["min_year"] = 1980
    elif re.search(r'\b2000s\b', msg_lower):
        filters["min_year"] = 2000

    # 5. Parse Ratings
    # Above / Min Score
    above_match = re.search(r'(?:above|over|more than|better than|greater than)\s*(\d+(?:\.\d+)?)', msg_lower)
    if above_match:
        filters["min_score"] = float(above_match.group(1))
    elif "good" in msg_lower or "great" in msg_lower or "highly rated" in msg_lower:
        filters["min_score"] = 7.0
        
    # Below / Max Score
    below_match = re.search(r'(?:below|under|less than|worse than)\s*(\d+(?:\.\d+)?)', msg_lower)
    if below_match:
        filters["max_score"] = float(below_match.group(1))
    elif "bad" in msg_lower or "flop" in msg_lower or "poorly rated" in msg_lower:
        filters["max_score"] = 5.0
        
    return filters

if __name__ == "__main__":
    # Test cases
    print(parse_user_filters("short Hindi thrillers after 2015 rated above 7"))
    print(parse_user_filters("comedy under 2 hours"))
    print(parse_user_filters("newer French action movies"))
