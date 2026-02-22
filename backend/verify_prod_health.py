import time
import requests
import sys

def check_health():
    print("Waiting for server to start...")
    url = "http://127.0.0.1:8000/api/health" # Router prefix is /api, but health might be on /health or /api/health depending on main.py include
    # Checking app/main.py: app.include_router(health_router, prefix="/api") AND app/api/router.py usage
    # Actually main.py includes api_router. api_router includes health_router with prefix="/api". 
    # Wait, api_router is included in main without prefix? "app.include_router(api_router)" 
    # And api_router defines: api_router.include_router(health_router, prefix="/api"...)
    # So it should be /api/health ?? Or /api/api/health?
    # Let's check main.py again in my memory or just try both.
    # main.py: @app.get("/health") IS DEFINED DIRECTLY in main.py too!
    
    # The user request said:
    # @app.get("/health") ... in main.py
    
    urls = ["http://127.0.0.1:8000/health", "http://127.0.0.1:8000/api/health"]
    
    for i in range(10):
        try:
            for u in urls:
                try:
                    r = requests.get(u, timeout=1)
                    if r.status_code == 200:
                        print(f"\n✅ Connected to {u}")
                        print(f"Response: {r.json()}")
                        if r.json().get("environment") == "production":
                            print("✅ Environment Verified: production")
                            return
                        else:
                             print(f"⚠️ Environment mismatch: {r.json().get('environment')}")
                             return # Return anyway if connected
                except:
                    pass
            print(".", end="", flush=True)
            time.sleep(1)
        except KeyboardInterrupt:
            break
            
    print("\n❌ Could not connect to server.")

if __name__ == "__main__":
    check_health()
