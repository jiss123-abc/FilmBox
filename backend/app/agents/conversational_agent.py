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

    # 2. Intent-Aware Execution
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
            genres=genres,
            mood=intent.mood,
            time_context=intent.time_context
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

    # 2.2 Generate response text deterministically first (Grounded Baseline)
    if not recommendations:
        base_response = "I don’t have enough information yet. Try rating a few movies first."
    else:
        top_movie = recommendations[0]
        # Handle cases where explanation might be missing
        explanation = top_movie.get("explanation", "Based on your current preferences.")
        base_response = f"I recommend **{top_movie.get('title', 'this movie')}**. {explanation}"

    # 3. LLM formatting (Narration)
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
