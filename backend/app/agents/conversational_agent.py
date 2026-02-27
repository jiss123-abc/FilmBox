from typing import Dict, Any
from app.agents.recommendation_agent import run_recommendation_agent
from app.agents.llm_wrapper import format_conversational_response
from app.agents.intent_parser import extract_intent
from app.ml.recommender_interface import get_hybrid_recommendations

def run_conversational_agent(user_id: int, message: str, genres: list[str] | None = None) -> Dict[str, Any]:
    """
    Deterministic version of the conversational agent.
    Acts as a backup or first-pass logic.
    """
    return run_recommendation_agent(user_id, message, genres=genres)

def run_conversational_agent_llm(user_id: int, message: str) -> Dict[str, Any]:
    """
    Intent-Aware conversational agent.
    Step 1: Extract intent (filters) from user message
    Step 2: Get filtered deterministic recommendations
    Step 3: Narrate the result
    """
    # 1. Parse Intent (Safe & Structured Extraction)
    intent = extract_intent(message)
    print(f"DEBUG intent: genres={intent.genres}")

    # 2. Specific Movie Lookup (Live TMDb Integration)
    if intent.movie_title:
        from app.core.database import SessionLocal
        from app.models.base_models import Movie
        from app.services.tmdb_service import search_movies, find_or_create_movie
        from app.agents.llm_wrapper import format_movie_details_response
        
        db = SessionLocal()
        try:
            # 2.1 Check local DB
            movie = db.query(Movie).filter(Movie.title.ilike(f"%{intent.movie_title}%")).first()
            
            # 2.2 Fallback to TMDb live search
            if not movie:
                print(f"DEBUG: '{intent.movie_title}' not in DB, searching live TMDb...")
                try:
                    search_results = search_movies(intent.movie_title)
                    if search_results and search_results.get("results"):
                        top_match = search_results["results"][0]["tmdb_id"]
                        movie = find_or_create_movie(top_match, db)
                        print(f"DEBUG: Successfully imported {movie.title} from TMDb")
                except Exception as e:
                    print(f"DEBUG: TMDb live search failed: {e}")
            
            # 2.3 Conversational formatting
            if movie:
                # Narrator gives details
                response_text = format_movie_details_response(movie, message)
                base_text = f"Here's what I found about **{movie.title}** ({movie.release_year}):\n\n{movie.overview}\n\nAudience Score: {movie.audience_score}/10"
                
                return {
                    "response": response_text or base_text,
                    "recommendations": [{
                        "movie_id": movie.id,
                        "title": movie.title,
                        "explanation": f"Specific lookup for {movie.title}."
                    }],
                    "strategy": "specific-movie-lookup"
                }
            else:
                return {
                    "response": f"I couldn't find any information about '{intent.movie_title}' right now.",
                    "recommendations": [],
                    "strategy": "movie-not-found"
                }
        finally:
            db.close()

    # 3. Intent-Aware Execution (Genre/Mood filtering)
    from app.agents.intent_normalizer import normalize_genres
    genres = normalize_genres(intent.genres) if intent.genres else None
    if genres:
        print(f"DEBUG normalized genres: {genres}")
    
    # Check for specific intent branch
    if intent.intent == "recommend_movie" and genres:
        print(f"DEBUG strategy selected: hybrid-intent-aware")
        # Use our refined interface with extracted intent data
        recommendations = get_hybrid_recommendations(
            user_id=user_id,
            genres=genres
        )
        
        # Step 2.1: Fail safely if nothing matches the filters
        if not recommendations:
            print(f"DEBUG: No matches for genres {genres}, falling back to general recs.")
            recommendations = get_hybrid_recommendations(user_id=user_id)
            strategy = "popularity-fallback"
        else:
            strategy = "hybrid-intent-aware"
    else:
        # Fallback to standard deterministic logic if no clear genre filters
        deterministic_result = run_conversational_agent(user_id, message, genres=genres)
        recommendations = deterministic_result["recommendations"]
        strategy = deterministic_result.get("strategy", "deterministic")

    # 3.2 Generate response text deterministically first (Grounded Baseline)
    if not recommendations:
        base_response = "I don’t have enough information yet. Try rating a few movies first."
    else:
        top_movie = recommendations[0]
        # Handle cases where explanation might be missing
        explanation = top_movie.get("explanation", "Based on your current preferences.")
        base_response = f"I recommend **{top_movie.get('title', 'this movie')}**. {explanation}"

    # 4. LLM formatting (Narration)
    # The Narrator can polish the base_response, but the recommendations are already fixed.
    response_text = format_conversational_response(recommendations, message)

    # If narration is None (failed), use the grounded baseline
    if response_text is None:
        response_text = base_response

    return {
        "response": response_text,
        "recommendations": recommendations,
        "strategy": strategy
    }
