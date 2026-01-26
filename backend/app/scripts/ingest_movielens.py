import pandas as pd
import sqlite3
from app.core.database import engine
from app.models import base_models
from sqlalchemy.orm import Session
from app.models.base_models import Movie, Genre, Rating

# ---------------------------
# Configuration
# ---------------------------

# MovieLens small dataset (100k) — you can download it from https://grouplens.org/datasets/movielens/
MOVIELENS_PATH = "./app/ml-latest-small/"

# ---------------------------
# Helper Functions
# ---------------------------

def ingest_movies_and_genres(session: Session):
    # Read movies.csv
    movies_df = pd.read_csv(MOVIELENS_PATH + "movies.csv")
    movies_df["movieId"] = movies_df["movieId"].astype(int)
    
    # Extract unique genres
    all_genres = set()
    for genre_list in movies_df['genres']:
        for g in genre_list.split('|'):
            if g != "(no genres listed)":
                all_genres.add(g)
    
    # Insert genres into DB
    genre_objects = {}
    for g in all_genres:
        genre_obj = Genre(name=g)
        session.add(genre_obj)
        genre_objects[g] = genre_obj
    session.commit()
    
    # Insert movies and connect genres
    for _, row in movies_df.iterrows():
        movie = Movie(
            id=row['movieId'],
            title=row['title'],
            release_year=int(row['title'][-5:-1]) if row['title'][-5:-1].isdigit() else None,
            overview=None,
            poster_url=None,
            popularity=0.0
        )
        # Link genres
        for g in row['genres'].split('|'):
            if g in genre_objects:
                movie.genres.append(genre_objects[g])
        session.add(movie)
    session.commit()
    print(f"Inserted {len(movies_df)} movies and {len(all_genres)} genres.")


def ingest_ratings(session: Session):
    ratings_df = pd.read_csv(MOVIELENS_PATH + "ratings.csv")
    ratings_df["userId"] = ratings_df["userId"].astype(int)
    ratings_df["movieId"] = ratings_df["movieId"].astype(int)
    
    for _, row in ratings_df.iterrows():
        rating = Rating(
            user_id=str(int(row['userId'])),
            movie_id=int(row['movieId']),
            rating=int(row['rating'])
        )
        session.add(rating)
    session.commit()
    print(f"Inserted {len(ratings_df)} ratings.")


# ---------------------------
# Main Function
# ---------------------------

def main():
    session = Session(bind=engine)
    try:
        ingest_movies_and_genres(session)
        ingest_ratings(session)
    finally:
        session.close()


if __name__ == "__main__":
    main()
