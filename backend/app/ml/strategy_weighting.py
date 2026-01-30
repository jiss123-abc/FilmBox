from app.models.strategy_stats import StrategyStats

def recalculate_weights(db):
    """
    Updates the global weights for each strategy based on its conversion rate (Likes/Usage).
    Formula: weight = 1.0 + (likes_received / times_used)
    
    This ensures that even strategies with zero likes have a baseline weight of 1.0, 
    preventing any strategy from being completely disabled.
    """
    stats = db.query(StrategyStats).all()

    for s in stats:
        if s.times_used == 0:
            s.weight = 1.0
        else:
            # Simple conversion-based boost
            s.weight = 1.0 + (s.likes_received / s.times_used)

    db.commit()
