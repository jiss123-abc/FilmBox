import os
from google import genai
from google.genai import types

GEMINI_MODEL = "gemini-2.5-flash"

def get_gemini_client():
    """
    Returns a configured Gemini client.
    Thread-safe and uses the latest official SDK.
    """
    if os.getenv("ENABLE_LLM", "false").lower() != "true":
        raise RuntimeError("LLM is disabled via ENABLE_LLM flag.")

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not set in environment or .env")

    # Initialize the NEW Client (Unified V2 SDK)
    client = genai.Client(api_key=api_key.strip())
    return client
