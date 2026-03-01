from typing import Dict, Any
from app.agents.recommendation_agent import run_recommendation_agent
from app.agents.llm_wrapper import format_conversational_response
from app.agents.intent_parser import extract_intent
from app.ml.recommender_interface import get_hybrid_recommendations

def run_conversational_agent(user_id: int, message: str, genres: list[str] | None = None, top_n: int = 10) -> Dict[str, Any]:
    """
    Deterministic version of the conversational agent.
    Acts as a backup or first-pass logic.
    """
    return run_recommendation_agent(user_id, message, genres=genres, top_n=top_n)

def run_conversational_agent_llm(user_id: int, message: str, chat_history: list[dict[str, str]] | None = None) -> Dict[str, Any]:
    """
    Single-pass Conversational Agent (Simplified Architecture).
    1. Parses user message for hard filters (genres, runtime, etc.).
    2. Fetches exactly 10 personalized recommendations meeting those filters.
    3. LLM formats the response and asks a follow-up.
    """
    import json
    from app.agents.groq_client import get_groq_client, GROQ_MODEL
    from app.agents.nlp_parser import parse_user_filters
    
    try:
        # 1. Parse rules from message (incorporating history context)
        history_lines = []
        if chat_history:
            # User specified "Last 3 chat messages"
            history_lines = [msg for msg in chat_history[-3:]]
        
        # Text for the NLP parser to extract filters from previous context + current
        history_text_for_parser = " ".join([m.get("content", "") for m in history_lines if m.get("role") == "user"])
        full_context = history_text_for_parser + " " + message
        filters = parse_user_filters(full_context)
        print(f"DEBUG: Filters extracted: {filters}")
        
        # Text for the LLM prompt to see context
        formatted_history = ""
        if history_lines:
            lines = [f"{m.get('role').capitalize()}: {m.get('content')}" for m in history_lines]
            formatted_history = "\nRecent History:\n" + "\n".join(lines) + "\n"
        
        # 2. Get a STRICT candidate pool of 10 movies matching the parsed filters
        raw_candidates = get_hybrid_recommendations(
            user_id=user_id, 
            top_n=10,
            genres=filters.get("genres"),
            max_runtime=filters.get("max_runtime"),
            min_score=filters.get("min_score"),
            max_score=filters.get("max_score"),
            language=filters.get("language"),
            min_year=filters.get("min_year")
        )
        
        # 2b. Smart Fallback if no exact matches found
        has_exact_matches = True
        if not raw_candidates:
            has_exact_matches = False
            # Fallback to a MIX of personalized and trending to ensure diversity
            # 1. Fetch 5 personalized picks based on taste
            taste_candidates = get_hybrid_recommendations(user_id=user_id, top_n=5)
            
            # 2. Fetch 5 globally trending movies (Popularity-based) to break genre bias
            trending_candidates = get_hybrid_recommendations(user_id=user_id, top_n=5, preferred_strategy="popularity-based")
            
            raw_candidates = taste_candidates + trending_candidates
            import random
            random.shuffle(raw_candidates)
        
        # CRITICAL: Normalize keys: ensure 'movie_id' exists across ALL strategies
        candidates = []
        for rec in raw_candidates:
            # Re-map 'id' to 'movie_id' if needed
            mid = rec.get("movie_id") or rec.get("id")
            if mid:
                rec["movie_id"] = mid
                candidates.append(rec)
        
        if not candidates:
            # Absolute failure (no ratings at all, etc.)
            return {
                "reply": "I'm having a hard time finding movies for you! Try rating a few favorites first so I can learn your taste.",
                "movies": [],
                "follow_up": "Want to try searching for something else?"
            }

        # Prepare candidate string for LLM
        candidate_lines = []
        for c in candidates:
            # Explicitly include the audience score so the LLM knows it is respecting the "below 6" filter
            line = f"ID: {c['movie_id']} | Title: {c['title']} | Genres: {', '.join(c.get('genres', []))} | Runtime: {c.get('runtime')}m | Rating: {c.get('audience_score')}/10"
            candidate_lines.append(line)
        
        candidate_text = "\n".join(candidate_lines)
        print(f"DEBUG: Prompt preparation complete.")

        # 3. LLM Task: Format Response Only (No logic/filtering)
        # If no exact matches were found, we tell the LLM so it can manage expectations
        context_note = ""
        if not has_exact_matches:
            context_note = "NOTE: NONE of the user's filtered criteria matched our database. The movies provided below are general personalized recommendations based on their overall taste. Politely explain that we don't have exactly what they asked for, and offer these others instead."

        prompt = f"""You are a friendly, highly intelligent movie concierge for 'FilmBox'.
You NEVER invent movies.
You ONLY use the provided movie list.
Format response clearly and briefly.
{context_note}
{formatted_history}
User Message: "{message}"

Structured movie list returned by the backend:
{candidate_text}

INSTRUCTIONS:
1. Write a friendly, conversational paragraph (the "reply") responding to the user.
2. IMPORTANT: You MUST explicitly mention the titles of at least 2-3 movies from the provided list in your reply.
3. Ask a short clarifying follow-up question.
4. Provide the integer IDs of the movies in the "movie_ids" field.

You MUST return ONLY valid JSON in this exact schema:
{{
    "reply": "I see you like thrillers! You should check out 'Rear Window' and 'Saboteur'...",
    "movie_ids": [123, 456],
    "follow_up": "Want something shorter?"
}}
"""

        # Use strictly llama-3.3-70b-versatile for high quality formatting
        client = get_groq_client()
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            max_completion_tokens=400,
            response_format={"type": "json_object"},
            timeout=10.0 # Strict timeout for performance as requested
        )
        
        raw_text = response.choices[0].message.content
        data = json.loads(raw_text)
        print(f"DEBUG: LLM call successful.")
        
        narrative = data.get("reply", "Here are some movies I found for you.")
        follow_up = data.get("follow_up", "")
        selected_ids = data.get("movie_ids", [])
        
        # Map IDs back to full movie dicts (Preserve metadata for UI)
        final_movies = [c for c in candidates if c["movie_id"] in selected_ids]
        
        # If LLM didn't select IDs properly or empty, use all 10
        if not final_movies:
            final_movies = candidates

        return {
            "reply": narrative,
            "movies": final_movies,
            "follow_up": follow_up
        }

    except Exception as e:
        print(f"⚠️ [Conversational Agent Logic Error]: {e}")
        # Final fallback to deterministic if the LLM crashes or anything else goes wrong
        try:
            deterministic_result = run_conversational_agent(user_id, message, top_n=5)
            return {
                "reply": f"I had a little trouble understanding that, but here are some general recommendations: {deterministic_result['response']}",
                "movies": deterministic_result["recommendations"],
                "follow_up": "Want to try searching for something else?"
            }
        except Exception as nested_e:
            print(f"⚠️ [Conversational Agent Double Fallback Failed]: {nested_e}")
            return {
                "reply": "I'm experiencing some technical difficulties! Please try again in a moment.",
                "movies": [],
                "follow_up": "Try searching by genre like 'comedy' or 'drama'?"
            }
