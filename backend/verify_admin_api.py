from fastapi.testclient import TestClient
from app.main import app
import json

client = TestClient(app)

def verify_admin_api():
    print("--- 📊 Verifying Admin Analytics API ---")
    response = client.get("/api/admin/metrics")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Status 200: Success")
        print(f"📡 API Status: {data.get('status')}")
        
        print("\n🤖 Strategy Weights:")
        for s in data.get("strategies", []):
            print(f" - {s['name']:<25} | Weight: {s['weight']:<8} | Conversion: {s['conversion_rate']:.2%}")
            
        print("\n🌍 Global Stats:")
        print(f" - Total Likes: {data['global_stats']['total_likes']}")
        print(f" - Total Dislikes: {data['global_stats']['total_dislikes']}")
        
        print("\n📈 24h Activity:")
        print(f" - Recs Served: {data['activity_24h']['recommendations_served']}")
        print(f" - Feedback:    {data['activity_24h']['feedback_received']}")
        
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    verify_admin_api()
