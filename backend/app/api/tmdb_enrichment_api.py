import csv
import os
from typing import List, Optional
from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.base_models import Movie

router = APIRouter(tags=["TMDb Enrichment"])

LINKS_CSV = os.path.join(os.path.dirname(__file__), "..", "ml-latest-small", "links.csv")
HTML_PATH = os.path.join(os.path.dirname(__file__), "..", "scripts", "tmdb_enrichment.html")


@router.get("/enrich", response_class=HTMLResponse)
def serve_enrichment_page():
    """Serves the TMDb enrichment HTML page."""
    html_path = os.path.abspath(HTML_PATH)
    with open(html_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


class EnrichItem(BaseModel):
    movie_id: int
    audience_score: Optional[float] = None
    vote_count: Optional[int] = None
    language: Optional[str] = None
    region: Optional[str] = None
    runtime: Optional[int] = None
    poster_url: Optional[str] = None
    overview: Optional[str] = None


@router.get("/api/admin/tmdb-mapping")
def get_tmdb_mapping(db: Session = Depends(get_db)):
    """
    Returns {movieId: tmdbId} for all movies needing enrichment.
    """
    # Get movies missing audience_score
    rows = db.query(Movie.id).filter(Movie.audience_score.is_(None)).all()
    movie_ids = set(r[0] for r in rows)

    # Load links.csv
    mapping = {}
    csv_path = os.path.abspath(LINKS_CSV)
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            mid = int(row["movieId"])
            tmdb_raw = row.get("tmdbId", "").strip()
            if tmdb_raw and mid in movie_ids:
                mapping[str(mid)] = int(tmdb_raw)

    return mapping


@router.post("/api/admin/enrich-batch")
def enrich_batch(items: List[EnrichItem], db: Session = Depends(get_db)):
    """
    Receives a batch of TMDb data and updates the movies table.
    """
    updated = 0
    for item in items:
        movie = db.query(Movie).filter(Movie.id == item.movie_id).first()
        if movie:
            movie.audience_score = item.audience_score
            movie.vote_count = item.vote_count
            movie.language = item.language
            movie.region = item.region
            movie.runtime = item.runtime
            if item.poster_url:
                movie.poster_url = item.poster_url
            if item.overview:
                movie.overview = item.overview
            updated += 1

    db.commit()
    return {"updated": updated, "total_received": len(items)}
