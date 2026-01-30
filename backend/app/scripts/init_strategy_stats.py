from app.core.database import SessionLocal
from app.models.strategy_stats import StrategyStats

DEFAULT_STRATEGIES = [
    "collaborative-filtering",
    "content-based",
    "popularity-based"
]

def init_strategies():
    db = SessionLocal()
    try:
        for name in DEFAULT_STRATEGIES:
            exists = db.query(StrategyStats).filter_by(strategy_name=name).first()
            if not exists:
                db.add(StrategyStats(strategy_name=name))
                print(f"Adding strategy: {name}")
        db.commit()
        print("✅ Strategy stats initialized")
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_strategies()
