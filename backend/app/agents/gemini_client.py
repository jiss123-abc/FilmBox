import os
from google import genai
from google.genai import types

GEMINI_MODEL = "models/gemini-flash-latest"

def get_gemini_client():
    """
    Returns a configured Gemini client.
    Thread-safe and uses the latest official SDK.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not set in environment or .env")

    # Initialize the NEW Client (Unified V2 SDK)
    client = genai.Client(api_key=api_key.strip())
    return client
