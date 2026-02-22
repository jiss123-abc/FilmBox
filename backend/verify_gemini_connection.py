import sys
import os
sys.path.append(os.getcwd())

from app.agents.intent_parser import extract_intent
from app.agents.gemini_client import get_gemini_client

def verify_connection():
    print("\n🔮 Verifying Antigravity Connection to Google AI Studio...\n")
    
    # 1. Check Key Presence
    key = os.getenv("GEMINI_API_KEY")
    if key:
        masked = key[:4] + "*" * (len(key) - 8) + key[-4:]
        print(f"✅ Found API Key: {masked}")
    else:
        print("❌ No API Key found in env!")
        return

    # 2. Test Client Instantiation
    try:
        client = get_gemini_client()
        print("✅ Gemini Client Initialized")
    except Exception as e:
        print(f"❌ Client Init Failed: {e}")
        return

    # 3. Real API Call (Intent Extraction)
    print("\nSending test message: 'I want a funny movie for a rainy day'...")
    try:
        intent = extract_intent("I want a funny movie for a rainy day")
        print(f"\n✅ RESPONSE RECEIVED from Gemini:")
        print(f"   Intent: {intent.intent}")
        print(f"   Genres: {intent.genres}")
        print(f"   Mood: {intent.mood}")
        print(f"   Context: {intent.time_context}")
        
        if intent.genres and "Comedy" in intent.genres:
             print("\n✨ Connection Validated! Antigravity is talking to Google AI Studio.")
        else:
             print("\n⚠️ Connection worked but result was unexpected (Model might be drifting or different version).")
             
    except Exception as e:
        print(f"❌ API Call Failed: {e}")
        print("\nPossible causes:")
        print("1. Invalid API Key")
        print("2. Quota exceeded")
        print("3. Model 'gemini-flash-latest' not found (try 'gemini-1.5-flash')")

if __name__ == "__main__":
    verify_connection()
