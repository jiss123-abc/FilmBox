import os
from groq import Groq

GROQ_MODEL = "llama-3.1-8b-instant"

def get_groq_client():
    """
    Returns a configured Groq client.
    """
    if os.getenv("ENABLE_LLM", "false").lower() != "true":
        raise RuntimeError("LLM is disabled via ENABLE_LLM flag.")

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY not set in environment or .env")

    client = Groq(api_key=api_key.strip())
    return client
