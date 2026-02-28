from typing import List, Dict
from google.genai import types
from app.agents.gemini_client import get_gemini_client, GEMINI_MODEL

def format_movie_details_response(movie, user_message: str) -> str | None:
    """
    Given a specific Movie object (with enriched TMDb data), generate a conversational
    response talking about the movie.
    """
    prompt = (
        f"You are a friendly movie concierge for 'FilmBox'.\n"
        f"User said: '{user_message}'\n\n"
        f"Movie details found:\n"
        f"- Title: {movie.title}\n"
        f"- Year: {movie.release_year}\n"
        f"- Overview: {movie.overview}\n"
        f"- Audience Score: {movie.audience_score}/10\n"
        f"- Runtime: {movie.runtime} minutes\n\n"
        f"INSTRUCTIONS:\n"
        f"- Write a friendly, conversational paragraph (2-3 sentences) answering the user.\n"
        f"- Highlight an interesting detail from the overview or score.\n"
        f"- Avoid generic filler."
    )

    try:
        client = get_gemini_client()
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.4, max_output_tokens=256)
        )
        return getattr(response, "text", None).strip()
    except Exception as e:
        print(f"⚠️ [Agent Fallback] specific movie narration failed: {e}")
        return None


def format_conversational_response(recommendations: List[Dict], user_message: str) -> str | None:
    """
    Optional narration helper.
    Returns a friendly string if LLM succeeds, or None if it fails.
    """
    # 1. Prepare structured text for LLM
    rec_text_lines = []
    for idx, m in enumerate(recommendations[:3], 1):
        score = m.get('audience_score') or 'N/A'
        runtime = m.get('runtime') or 'N/A'
        overview = m.get('overview', 'No overview available.')
        
        line = f"{idx}. {m['title']} (Score: {score}/10, Runtime: {runtime} mins)\n"
        line += f"   Reason: {m.get('explanation', '')}\n"
        line += f"   Overview: {overview}"
        rec_text_lines.append(line)
        
    rec_text = "\n\n".join(rec_text_lines)

    prompt = (
        f"You are a friendly, highly intelligent movie concierge for 'FilmBox'.\n"
        f"User said: '{user_message}'\n\n"
        f"Backend Top Recommendations:\n{rec_text}\n\n"
        f"INSTRUCTIONS:\n"
        f"- Write a friendly, conversational paragraph (3-4 sentences) responding to the user.\n"
        f"- Seamlessly mention the true audience scores, runtimes, or interesting details from the overviews to make your recommendation compelling.\n"
        f"- Stay 100% grounded in the provided data. Do not hallucinate."
    )

    # 2. Call Gemini via modular utility
    try:
        client = get_gemini_client()
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.4,
                max_output_tokens=256
            )
        )
        
        # SAFE ACCESSOR: Ensure we don't crash on None or empty strings
        raw_text = getattr(response, "text", None)
        
        if not raw_text or not raw_text.strip():
            raise ValueError("Narration empty")
            
        return raw_text.strip()

    except Exception as e:
        # LOG AND RETURN NONE: Narration is optional presentation
        print(f"⚠️ [Agent Fallback] LLM narration failed, using deterministic text: {e}")
        
        # Diagnostic model listing (kept for troubleshooting)
        if "404" in str(e):
            try:
                models = [m.name for m in client.models.list()]
                print(f"DEBUG: Available models: {models}")
            except:
                pass
                
        return None
