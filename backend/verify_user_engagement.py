import requests

def verify_user_engagement():
    base_url = "http://localhost:8000/api/admin/analytics"
    
    print("--- Phase 15.2: User Engagement Analytics Verification ---")
    
    try:
        # Check Pulse first to see if system is alive
        pulse = requests.get(f"{base_url}/pulse").json()
        print(f"System Pulse: {pulse['pulse']['recommendations_served']} recs served in last hour.")

        # Check User Engagement
        engagement = requests.get(f"{base_url}/user-engagement").json()
        
        print("\nUser Engagement Leaderboard:")
        print(f"{'User ID':<10} | {'Interactions':<12} | {'Likes':<8} | {'Score':<8}")
        print("-" * 45)
        
        for user in engagement:
            print(f"{user['user_id']:<10} | {user['total_interactions']:<12} | {user['likes']:<8} | {user['engagement_score']:.2f}")

    except Exception as e:
        print(f"Error during verification: {e}")
        print("Note: Ensure the backend server is running on localhost:8000")

if __name__ == "__main__":
    verify_user_engagement()
