"""Test Gemini API call end-to-end"""
import os
from dotenv import load_dotenv
load_dotenv(override=True)

print(f"ENABLE_LLM = {os.getenv('ENABLE_LLM')}")
print(f"GEMINI_API_KEY = {os.getenv('GEMINI_API_KEY')[:10]}...")

from app.agents.gemini_client import get_gemini_client, GEMINI_MODEL
print(f"Model: {GEMINI_MODEL}")

client = get_gemini_client()
print("✅ Client created")

response = client.models.generate_content(
    model=GEMINI_MODEL,
    contents="Say hello in one sentence."
)
print(f"✅ Gemini says: {response.text}")
