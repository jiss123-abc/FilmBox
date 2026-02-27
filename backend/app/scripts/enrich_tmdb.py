"""
TMDb Enrichment Script
Reads links.csv (movieId → tmdbId) and fetches metadata from TMDb API
to populate: audience_score, vote_count, language, region, runtime
"""
import csv
import os
import sys
import time
import requests
import sqlite3

TMDB_BASE = "https://api.themoviedb.org/3/movie"
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "filmBox.db")
LINKS_CSV = os.path.join(os.path.dirname(__file__), "..", "ml-latest-small", "links.csv")
BATCH_SIZE = 50  # commit every N movies
RATE_LIMIT_DELAY = 0.03  # ~33 req/sec (TMDb allows ~40)


def load_links(csv_path: str) -> dict:
    """Returns {movieId: tmdbId} mapping from links.csv."""
    mapping = {}
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            mid = int(row["movieId"])
            tmdb_raw = row.get("tmdbId", "").strip()
            if tmdb_raw:
                mapping[mid] = int(tmdb_raw)
    return mapping


def fetch_tmdb(tmdb_id: int, api_key: str) -> dict | None:
    """Fetch movie details from TMDb API. Returns parsed dict or None."""
    url = f"{TMDB_BASE}/{tmdb_id}"
    params = {"api_key": api_key, "language": "en-US"}
    try:
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code == 200:
            return resp.json()
        elif resp.status_code == 429:
            # Rate limited — back off
            retry_after = int(resp.headers.get("Retry-After", 2))
            print(f"  Rate limited, sleeping {retry_after}s...")
            time.sleep(retry_after)
            return fetch_tmdb(tmdb_id, api_key)  # retry once
        else:
            return None
    except requests.RequestException:
        return None


def enrich():
    api_key = os.getenv("TMDB_API_KEY", "")
    if not api_key:
        print("ERROR: Set TMDB_API_KEY in your .env or environment.")
        sys.exit(1)

    # Resolve paths
    db_path = os.path.abspath(DB_PATH)
    csv_path = os.path.abspath(LINKS_CSV)
    print(f"DB:   {db_path}", flush=True)
    print(f"CSV:  {csv_path}", flush=True)

    # Load movieId → tmdbId mapping
    links = load_links(csv_path)
    print(f"Loaded {len(links)} movieId→tmdbId mappings from links.csv", flush=True)

    # Connect to DB
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Get movies that haven't been enriched yet
    rows = cur.execute(
        "SELECT id FROM movies WHERE audience_score IS NULL"
    ).fetchall()
    movie_ids = [r[0] for r in rows]
    print(f"Movies to enrich: {len(movie_ids)}", flush=True)

    enriched = 0
    skipped = 0
    errors = 0

    for i, movie_id in enumerate(movie_ids):
        tmdb_id = links.get(movie_id)
        if not tmdb_id:
            skipped += 1
            continue

        data = fetch_tmdb(tmdb_id, api_key)
        if not data:
            errors += 1
            continue

        # Extract fields
        audience_score = data.get("vote_average")
        vote_count = data.get("vote_count")
        language = data.get("original_language")
        runtime = data.get("runtime")
        poster_path = data.get("poster_path")
        overview = data.get("overview")

        # Region: first production country
        countries = data.get("production_countries", [])
        region = countries[0]["iso_3166_1"] if countries else None

        # Poster URL
        poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None

        cur.execute(
            """UPDATE movies SET
                audience_score = ?, vote_count = ?, language = ?,
                region = ?, runtime = ?, poster_url = ?, overview = ?
               WHERE id = ?""",
            (audience_score, vote_count, language, region, runtime,
             poster_url, overview, movie_id)
        )
        enriched += 1

        # Commit in batches
        if enriched % BATCH_SIZE == 0:
            conn.commit()

        # Progress log
        if (i + 1) % 100 == 0:
            print(f"  Progress: {i+1}/{len(movie_ids)} | Enriched: {enriched} | Skipped: {skipped} | Errors: {errors}", flush=True)

        time.sleep(RATE_LIMIT_DELAY)

    conn.commit()
    conn.close()

    print(f"\nDone! Enriched: {enriched} | Skipped (no tmdbId): {skipped} | Errors: {errors}", flush=True)


if __name__ == "__main__":
    # Load .env if python-dotenv is available
    try:
        from dotenv import load_dotenv
        load_dotenv(os.path.join(os.getcwd(), ".env"))
    except ImportError:
        pass

    enrich()
