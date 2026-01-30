from app.core.database import SessionLocal
from app.ml.strategy_lookup import get_last_strategy_for_user
from app.ml.strategy_learning import update_strategy_weight, POSITIVE_REWARD
from app.models.user_strategy_stats import UserStrategyStats

def verify_cycle():
    user_id = 42
    db = SessionLocal()
    
    print("--- User 42 Learning Cycle Verification ---")
    
    # 1. Check Weights BEFORE
    stat = db.query(UserStrategyStats).filter_by(user_id=user_id).first()
    if not stat:
        # Create a baseline if somehow missing, though we saw it earlier
        stat = UserStrategyStats(user_id=user_id, strategy='collaborative-filtering', weight=1.0, total_used=1, positive_feedback=0)
        db.add(stat)
        db.commit()
        db.refresh(stat)
    
    initial_weight = stat.weight
    print(f"BEFORE: Strategy: {stat.strategy}, Weight: {initial_weight}")

    # 2. Identify Strategy from Logs
    strategy = get_last_strategy_for_user(user_id)
    print(f"LOGS: Last strategy identified: {strategy}")
    
    if not strategy:
        print("ERROR: No logs found. Attribution will fail.")
        db.close()
        return

    # 3. Simulate Feedback Submit
    print("ACTION: Submitting LIKE feedback...")
    update_strategy_weight(user_id, strategy, liked=1)
    
    # 4. Check Weights AFTER
    db.refresh(stat)
    after_weight = stat.weight
    print(f"AFTER: Strategy: {stat.strategy}, Weight: {after_weight}")
    
    if abs(after_weight - (initial_weight + POSITIVE_REWARD)) < 0.01:
        print(f"\n✅ SUCCESS: Weight increased by {POSITIVE_REWARD} for strategy '{strategy}'!")
    else:
        print(f"\n❌ FAILED: Weight did not increase as expected. (Diff: {after_weight - initial_weight})")

    db.close()

if __name__ == "__main__":
    verify_cycle()
