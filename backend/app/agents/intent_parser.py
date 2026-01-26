import json
import re
from app.agents.gemini_client import get_gemini_client, GEMINI_MODEL
from app.agents.intent_schema import RecommendationIntent
from google.genai import types

def safe_parse_json(text: str) -> dict | None:
    """
    Safely extracts the first valid JSON object from a text block
    using regex and json.loads().
    """
    if not text:
        return None

    # Extract first JSON object using DOTALL to handle multi-line
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None

    try:
        return json.loads(match.group())
    except json.JSONDecodeError:
        return None

INTENT_PROMPT = """
You are an intent extraction engine.

Return ONLY valid JSON.
Do NOT include explanations, markdown, or extra text.

Schema:
{{
  "intent": "recommend_movie" | "other",
  "genres": [string],
  "mood": string | null,
  "time_context": string | null
}}

User message:
"{message}"
"""

def extract_intent(message: str) -> RecommendationIntent:
    """
    Parses a natural language message into a structured RecommendationIntent.
    Uses temperature 0.0 for maximum determinism.
    Completely fail-safe: returns default intent on any error.
    """
    try:
        client = get_gemini_client()

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=INTENT_PROMPT.format(message=message),
            config=types.GenerateContentConfig(
                temperature=0.0,
                max_output_tokens=128
            )
        )

        # Robust null-guard for the text attribute
        raw_text = getattr(response, "text", None)
        
        data = safe_parse_json(raw_text)
        
        if not data:
            raise ValueError("Intent JSON invalid or empty")
            
        return RecommendationIntent(**data)

    except Exception as e:
        print(f"⚠️ [Intent Error] Failed to parse intent, proceeding without filters: {e}")
        # Return a safe default to prevent system crashes
        return RecommendationIntent(
            intent="recommend_movie",
            genres=[],
            mood=None,
            time_context=None
        )
