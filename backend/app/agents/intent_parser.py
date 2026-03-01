import json
import re
from app.agents.groq_client import get_groq_client, GROQ_MODEL
from app.agents.intent_schema import RecommendationIntent

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
  "time_context": string | null,
  "movie_title": string | null, // ONLY extract if the user mentions a specific, exact movie title. If they ask for a LIST or general recommendations (e.g., "13 highest rated movies"), this MUST be null.
  "max_runtime": int | null,
  "min_score": float | null,
  "language": string | null, // MUST be a 2-letter ISO-639-1 code (e.g. "en", "fr").
  "quantity": int | null     // If the user asks for a specific number of movies (e.g. "13 highest rated").
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
        client = get_groq_client()

        response = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": INTENT_PROMPT.format(message=message),
                }
            ],
            model=GROQ_MODEL,
            temperature=0.0,
            max_completion_tokens=512,
            response_format={"type": "json_object"}
        )

        # Robust null-guard for the text attribute
        raw_text = response.choices[0].message.content
        
        data = safe_parse_json(raw_text)
        
        if not data:
            raise ValueError("Intent JSON invalid or empty")
            
        return RecommendationIntent(**data)

    except Exception as e:
        print(f"⚠️ [Intent Error] Failed to parse intent: {e}")
        try:
             # Try to print preview of response text if possible
             print(f"DEBUG Raw Text: {locals().get('raw_text', 'Start not reached')}")
        except:
             pass
        # Return a safe default to prevent system crashes
        return RecommendationIntent(
            intent="recommend_movie",
            genres=[],
            mood=None,
            time_context=None,
            movie_title=None,
            max_runtime=None,
            min_score=None,
            language=None,
            quantity=None
        )
