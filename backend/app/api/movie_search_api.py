"""
Movie Search API — Live TMDb-powered movie search.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.tmdb_service import search_movies, find_or_create_movie

router = APIRouter(prefix="/api/movies", tags=["Movie Search"])


@router.get("/search")
def search(q: str = Query(..., min_length=1, description="Movie title to search for"),
           page: int = Query(1, ge=1),
           db: Session = Depends(get_db)):
    """
    Search for movies via TMDb. Results include poster, score, language, etc.
    """
    try:
        return search_movies(query=q, page=page)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"TMDb API error: {e}")


@router.post("/import/{tmdb_id}")
def import_movie(tmdb_id: int, db: Session = Depends(get_db)):
    """
    Import a specific movie from TMDb into the local database.
    If it already exists, returns the existing record.
    """
    try:
        movie = find_or_create_movie(tmdb_id, db)
        return {
            "status": "ok",
            "movie": {
                "id": movie.id,
                "title": movie.title,
                "release_year": movie.release_year,
                "poster_url": movie.poster_url,
                "audience_score": movie.audience_score,
                "language": movie.language,
                "region": movie.region,
                "runtime": movie.runtime,
            }
        }
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"TMDb API error: {e}")
