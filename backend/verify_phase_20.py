from app.core.database import SessionLocal
from app.models.user_genre_preferences import UserGenrePreferences
from app.ml.taste_updater import update_genre_preferences
from app.ml.decay import decay_preferences
from app.ml.preference_reader import get_genre_preferences
from app.ml.taste_bias import apply_taste_bias

def verify_phase_20():
    print("--- 🕰️ Phase 20: Long-Term Taste Evolution Verification ---")
    db = SessionLocal()
    user_id = "taste_test_user"

    # Cleanup
    db.query(UserGenrePreferences).filter_by(user_id=user_id).delete()
    db.commit()

    print("\n1. Simulating 'Action' Phase (Year 2023)...")
    # User likes 5 Action movies
    for _ in range(5):
        update_genre_preferences(db, user_id, ["Action"], True)
    
    prefs = get_genre_preferences(db, user_id)
    print(f"Action Score: {prefs.get('Action', 0.0):.4f}")

    print("\n2. Simulating Time Passing (Decay)...")
    # Simulate 50 interactions of other stuff/time passing
    for _ in range(50):
        decay_preferences(db, user_id)
        
    prefs = get_genre_preferences(db, user_id)
    action_score = prefs.get('Action', 0.0)
    print(f"Decayed Action Score: {action_score:.4f}")
    
    if action_score < 0.5: # Started at 5*0.2=1.0. 0.98^50 ~ 0.36
        print("✅ Action preference successfully faded.")
    else:
        print("❌ Decay failed or too slow.")

    print("\n3. Simulating 'Drama' Phase (Year 2024)...")
    # User likes 5 Drama movies
    for _ in range(5):
        update_genre_preferences(db, user_id, ["Drama"], True)
        
    prefs = get_genre_preferences(db, user_id)
    drama_score = prefs.get('Drama', 0.0)
    print(f"New Drama Score: {drama_score:.4f}")

    print("\n4. Verifying Re-Ranking Bias...")
    # Mock movies
    movies = [
        {"title": "Die Hard", "genres": ["Action"], "score": 0.5},
        {"title": "The Godfather", "genres": ["Drama"], "score": 0.5},
    ]
    
    ranked = apply_taste_bias(movies, prefs)
    print(f"Top Recommendation: {ranked[0]['title']} (Score: {ranked[0]['score']:.4f})")
    
    if ranked[0]["title"] == "The Godfather":
        print("✅ System prioritized Drama (Current Taste) over Action (Old Taste).")
    else:
        print("❌ Re-ranking failed.")

    db.close()

if __name__ == "__main__":
    verify_phase_20()
