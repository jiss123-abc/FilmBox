import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy.orm import Session

from app.models.base_models import Movie, Genre


class ContentRecommender:
    def __init__(self, session: Session):
        self.session = session
        self.movie_features = None
        self.similarity_matrix = None
        self.movie_ids = None
        self._prepare()

    def _prepare(self):
        """
        Build a movie-genre feature matrix
        """
        movies = self.session.query(Movie).all()

        rows = []
        for movie in movies:
            genre_names = [g.name for g in movie.genres]
            rows.append({
                "movie_id": movie.id,
                **{g: 1 for g in genre_names}
            })

        if not rows:
            self.movie_features = pd.DataFrame()
            return

        df = pd.DataFrame(rows).fillna(0)
        self.movie_ids = df["movie_id"]
        self.movie_features = df.drop(columns=["movie_id"])

        self.similarity_matrix = cosine_similarity(self.movie_features)

    def recommend_similar_movies(self, movie_id: int, top_n: int = 10, genre_filter: list[str] | None = None):
        """
        Recommend movies similar to a given movie
        """
        if movie_id not in self.movie_ids.values:
            return []

        idx = self.movie_ids[self.movie_ids == movie_id].index[0]
        similarity_scores = list(enumerate(self.similarity_matrix[idx]))

        # Get more candidates if filtering
        candidate_count = top_n * 10 if genre_filter else top_n + 1
        
        similarity_scores = sorted(
            similarity_scores,
            key=lambda x: x[1],
            reverse=True
        )[1:candidate_count]

        similar_movie_ids = [
            int(self.movie_ids.iloc[i])
            for i, _ in similarity_scores
        ]

        query = (
            self.session.query(Movie)
            .filter(Movie.id.in_(similar_movie_ids))
        )
        
        if genre_filter:
            query = query.filter(Movie.genres.any(Genre.name.in_(genre_filter)))

        movies = query.all()
        
        # Sort by similarity score again
        id_to_score = {int(self.movie_ids.iloc[i]): score for i, score in similarity_scores}
        movies = sorted(movies, key=lambda m: id_to_score.get(m.id, 0), reverse=True)

        return [
            {
                "id": m.id,
                "title": m.title,
                "release_year": m.release_year,
                "genres": [g.name for g in m.genres]
            }
            for m in movies[:top_n]
        ]
