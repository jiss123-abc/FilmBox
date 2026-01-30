def detect_churn_risk(engagement_score: float) -> str:
    """
    Translates raw engagement score into risk levels (Step 5).
    """
    if engagement_score >= 0.3:
        return "healthy"
    elif engagement_score >= 0.0:
        return "at-risk"
    else:
        return "critical"
