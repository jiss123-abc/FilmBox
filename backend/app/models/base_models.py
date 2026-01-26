from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

# ---------------------------
# Association Tables
# ---------------------------

# Many-to-Many: Movie ↔ Genre
movie_genres_table = Table(
    "movie_genres",
    Base.metadata,
    Column("movie_id", Integer, ForeignKey("movies.id"), primary_key=True),
    Column("genre_id", Integer, ForeignKey("genres.id"), primary_key=True),
)

# Many-to-Many: User ↔ Favorite Genres
user_genres_table = Table(
    "user_genres",
    Base.metadata,
    Column("user_id", String, ForeignKey("users.id"), primary_key=True),
    Column("genre_id", Integer, ForeignKey("genres.id"), primary_key=True),
)

# ---------------------------
# Core Tables
# ---------------------------

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    ratings = relationship("Rating", back_populates="user")
    watchlist = relationship("Watchlist", back_populates="user")
    watch_history = relationship("WatchHistory", back_populates="user")
    favorite_genres = relationship("Genre", secondary=user_genres_table, back_populates="users")
    feedbacks = relationship("UserFeedback", back_populates="user")


class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True)  # TMDB or MovieLens ID
    title = Column(String, nullable=False)
    release_year = Column(Integer)
    poster_url = Column(String)
    overview = Column(String)
    popularity = Column(Float)

    genres = relationship("Genre", secondary=movie_genres_table, back_populates="movies")
    ratings = relationship("Rating", back_populates="movie")
    watchlist_users = relationship("Watchlist", back_populates="movie")
    watched_users = relationship("WatchHistory", back_populates="movie")
    feedbacks = relationship("UserFeedback", back_populates="movie")


class Genre(Base):
    __tablename__ = "genres"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)

    movies = relationship("Movie", secondary=movie_genres_table, back_populates="genres")
    users = relationship("User", secondary=user_genres_table, back_populates="favorite_genres")


# ---------------------------
# User Interactions
# ---------------------------

class Rating(Base):
    __tablename__ = "ratings"

    user_id = Column(String, ForeignKey("users.id"), primary_key=True)
    movie_id = Column(Integer, ForeignKey("movies.id"), primary_key=True)
    rating = Column(Integer, nullable=False)  # 1-5 scale
    rated_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="ratings")
    movie = relationship("Movie", back_populates="ratings")


class WatchHistory(Base):
    __tablename__ = "watch_history"

    user_id = Column(String, ForeignKey("users.id"), primary_key=True)
    movie_id = Column(Integer, ForeignKey("movies.id"), primary_key=True)
    watched_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="watch_history")
    movie = relationship("Movie", back_populates="watched_users")


class Watchlist(Base):
    __tablename__ = "watchlist"

    user_id = Column(String, ForeignKey("users.id"), primary_key=True)
    movie_id = Column(Integer, ForeignKey("movies.id"), primary_key=True)
    added_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="watchlist")
    movie = relationship("Movie", back_populates="watchlist_users")
