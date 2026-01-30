from app.ml.churn_detector import detect_churn_risk

def select_adaptive_strategy(
    base_strategy: str,
    engagement_score: float
) -> dict:
    """
    Determines the strategy and exploration rate based on churn risk.
    
    Rules:
    - Healthy: Keep optimizing (Exploitation).
    - At-Risk: Try Content-Based (Stick to what they liked).
    - Critical: Reset to Popularity (Safe bet) with high diversity.
    """
    churn_risk = detect_churn_risk(engagement_score)

    if churn_risk == "healthy":
        return {
            "strategy": base_strategy,
            "exploration": 0.1,
            "risk_level": "healthy"
        }

    if churn_risk == "at-risk":
        return {
            "strategy": "content-based",
            "exploration": 0.3,
            "risk_level": "at-risk"
        }

    # critical
    return {
        "strategy": "popularity-based",
        "exploration": 0.6,
        "risk_level": "critical" # Force exploration High
    }
