import sys
import os
sys.path.append(os.getcwd())

from app.agents.gemini_client import get_gemini_client, GEMINI_MODEL
from app.agents.intent_parser import INTENT_PROMPT
from google.genai import types

def debug_gemini():
    print(f"Attempting to connect using model: {GEMINI_MODEL}")
    
    test_msg = "I want a funny movie for a rainy day"
    print(f"\nSending Intent Prompt with message: '{test_msg}'...")
    
    try:
        client = get_gemini_client()
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=INTENT_PROMPT.format(message=test_msg),
            config=types.GenerateContentConfig(
                temperature=0.0,
                max_output_tokens=128
            )
        )
        print(f"Response Object: {response}")
        try:
            print(f"Response Text: {response.text}")
        except:
            print("response.text access failed")
            
        if hasattr(response, 'candidates'):
             print(f"Candidates: {response.candidates}")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")

if __name__ == "__main__":
    debug_gemini()
