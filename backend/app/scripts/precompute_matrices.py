import os
import sys
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sklearn.metrics.pairwise import cosine_similarity
from tqdm import tqdm

# Add the project root to the python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal, engine
from app.models.base_models import Movie, Rating, MovieSimilarity, UserSimilarity, Base

def precompute_movie_similarities(session, batch_size=50):
    print("Fetching movies and genres...")
    movies = session.query(Movie).all()
    if not movies:
        print("No movies found.")
        return

    print("Building Movie-Genre matrix...")
    rows = []
    for movie in movies:
        genre_names = [g.name for g in movie.genres]
        rows.append({
            "movie_id": movie.id,
            **{g: 1 for g in genre_names}
        })
        
    df = pd.DataFrame(rows).fillna(0)
    movie_ids = df["movie_id"].values
    features = df.drop(columns=["movie_id"]).values

    print(f"Computing cosine similarity for {len(movie_ids)} movies (Requires high RAM temporarily)...")
    sim_matrix = cosine_similarity(features)

    print("Clearing old movie similarities...")
    session.query(MovieSimilarity).delete()
    session.commit()

    print(f"Extracting Top {batch_size} similarities and inserting into SQLite...")
    insert_data = []
    
    for idx, movie_id in enumerate(tqdm(movie_ids)):
        # Get scores for this movie, enumerate to keep track of target indices
        scores = list(enumerate(sim_matrix[idx]))
        # Sort by score descending, skip index 0 (self)
        scores = sorted(scores, key=lambda x: x[1], reverse=True)[1:batch_size+1]
        
        for sim_idx, score in scores:
            if score > 0: # Only store meaningful similarities
                insert_data.append(MovieSimilarity(
                    movie_id=int(movie_id),
                    similar_movie_id=int(movie_ids[sim_idx]),
                    similarity_score=float(score)
                ))

    print(f"Bulk inserting {len(insert_data)} rows into MovieSimilarity...")
    session.bulk_save_objects(insert_data)
    session.commit()
    print("Movie similarities precomputed successfully!")


def precompute_user_similarities(session, batch_size=50):
    print("Fetching ratings build User CF matrix...")
    ratings = session.query(Rating).all()
    if not ratings:
        print("No ratings found.")
        return

    print("Building User-Movie matrix...")
    data = [{"user_id": r.user_id, "movie_id": r.movie_id, "rating": r.rating} for r in ratings]
    ratings_df = pd.DataFrame(data)
    user_movie_matrix = ratings_df.pivot(index='user_id', columns='movie_id', values='rating').fillna(0)
    
    user_ids = user_movie_matrix.index.values

    print(f"Computing cosine similarity for {len(user_ids)} users...")
    sim_matrix = cosine_similarity(user_movie_matrix.values)

    print("Clearing old user similarities...")
    session.query(UserSimilarity).delete()
    session.commit()

    print(f"Extracting Top {batch_size} similarities and inserting into SQLite...")
    insert_data = []
    
    for idx, user_id in enumerate(tqdm(user_ids)):
        scores = list(enumerate(sim_matrix[idx]))
        scores = sorted(scores, key=lambda x: x[1], reverse=True)[1:batch_size+1]
        
        for sim_idx, score in scores:
            if score > 0:
                insert_data.append(UserSimilarity(
                    user_id=str(user_id),
                    similar_user_id=str(user_ids[sim_idx]),
                    similarity_score=float(score)
                ))

    print(f"Bulk inserting {len(insert_data)} rows into UserSimilarity...")
    session.bulk_save_objects(insert_data)
    session.commit()
    print("User similarities precomputed successfully!")


if __name__ == "__main__":
    print("Creating tables if they do not exist...")
    Base.metadata.create_all(bind=engine)
    
    session = SessionLocal()
    try:
        precompute_movie_similarities(session, batch_size=50) # Save top 50 matches per movie
        precompute_user_similarities(session, batch_size=50)  # Save top 50 matches per user
        print("All machine learning matrices successfully computed and injected into SQLite!")
    finally:
        session.close()
