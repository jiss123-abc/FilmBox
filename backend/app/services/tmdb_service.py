"""
TMDb Service — Live movie lookup via The Movie Database API.
Used for searching movies not yet in the local database and auto-importing them.
"""
import os
import requests
from typing import Optional
from sqlalchemy.orm import Session
from app.models.base_models import Movie


TMDB_BASE = "https://api.themoviedb.org/3"


def _get_api_key() -> str:
    key = os.getenv("TMDB_API_KEY", "")
    if not key:
        raise RuntimeError("TMDB_API_KEY not set in environment")
    return key


def search_movies(query: str, page: int = 1) -> dict:
    """
    Search TMDb for movies matching a query string.
    Returns the raw TMDb search response with results list.
    """
    resp = requests.get(
        f"{TMDB_BASE}/search/movie",
        params={
            "api_key": _get_api_key(),
            "query": query,
            "page": page,
            "language": "en-US",
            "include_adult": False,
        },
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()

    # Normalize results for our frontend
    results = []
    for item in data.get("results", []):
        poster_path = item.get("poster_path")
        results.append({
            "tmdb_id": item["id"],
            "title": item.get("title", ""),
            "release_date": item.get("release_date", ""),
            "overview": item.get("overview", ""),
            "poster_url": f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None,
            "audience_score": item.get("vote_average"),
            "vote_count": item.get("vote_count"),
            "language": item.get("original_language"),
            "popularity": item.get("popularity"),
        })

    return {
        "page": data.get("page", 1),
        "total_pages": data.get("total_pages", 1),
        "total_results": data.get("total_results", 0),
        "results": results,
    }


def get_movie_details(tmdb_id: int) -> dict:
    """
    Fetch full movie details from TMDb by tmdb_id.
    """
    resp = requests.get(
        f"{TMDB_BASE}/movie/{tmdb_id}",
        params={"api_key": _get_api_key(), "language": "en-US"},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()


def find_or_create_movie(tmdb_id: int, db: Session) -> Movie:
    """
    Check if a movie with this tmdb_id exists in the local DB.
    If not, fetch it from TMDb and insert it.
    Returns the Movie ORM object.
    """
    # Check local DB first
    movie = db.query(Movie).filter(Movie.id == tmdb_id).first()
    if movie:
        return movie

    # Fetch from TMDb
    data = get_movie_details(tmdb_id)

    poster_path = data.get("poster_path")
    countries = data.get("production_countries", [])
    release_date = data.get("release_date", "")
    release_year = int(release_date[:4]) if release_date and len(release_date) >= 4 else None

    movie = Movie(
        id=tmdb_id,
        title=data.get("title", "Unknown"),
        release_year=release_year,
        poster_url=f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None,
        overview=data.get("overview"),
        popularity=data.get("popularity"),
        audience_score=data.get("vote_average"),
        vote_count=data.get("vote_count"),
        language=data.get("original_language"),
        region=countries[0]["iso_3166_1"] if countries else None,
        runtime=data.get("runtime"),
    )

    # Also link genres if they exist locally
    from app.models.base_models import Genre
    for g in data.get("genres", []):
        genre = db.query(Genre).filter(Genre.name == g["name"]).first()
        if genre:
            movie.genres.append(genre)

    db.add(movie)
    db.commit()
    db.refresh(movie)
    return movie
