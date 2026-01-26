from typing import List, Dict
from google.genai import types
from app.agents.gemini_client import get_gemini_client, GEMINI_MODEL

def format_conversational_response(recommendations: List[Dict], user_message: str) -> str | None:
    """
    Optional narration helper.
    Returns a friendly string if LLM succeeds, or None if it fails.
    """
    # 1. Prepare structured text for LLM
    rec_text = "\n".join(
        [f"- {m['title']}: {m['explanation']}" for m in recommendations[:3]]
    )

    prompt = (
        f"You are a friendly movie concierge for 'FilmBox'.\n"
        f"User said: '{user_message}'\n\n"
        f"Backend recommendations:\n{rec_text}\n\n"
        f"INSTRUCTIONS:\n"
        f"- Write a short, friendly paragraph (2-3 sentences).\n"
        f"- Stay 100% grounded in the provided data."
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
