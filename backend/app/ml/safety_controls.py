from typing import List, Dict

class SafetyEnforcer:
    """
    Governance layer for recommendations.
    Enforces limits and filters out unsafe/low-quality items.
    """
    MAX_RECOMMENDATIONS = 50
    MIN_CONFIDENCE = 0.15
    DISALLOWED_STRATEGIES = [] # Can be populated dynamically

    @staticmethod
    def enforce_limits(recommendations: List[Dict], limit: int) -> List[Dict]:
        """Truncate to safe maximums."""
        safe_limit = min(limit, SafetyEnforcer.MAX_RECOMMENDATIONS)
        return recommendations[:safe_limit]

    @staticmethod
    def filter_low_confidence(recommendations: List[Dict]) -> List[Dict]:
        """Remove items below confidence threshold."""
        valid_recs = []
        for rec in recommendations:
            # Assume 1.0 confidence if not present (legacy strategies)
            confidence = rec.get("confidence", 1.0)
            if confidence >= SafetyEnforcer.MIN_CONFIDENCE:
                valid_recs.append(rec)
        return valid_recs

    @staticmethod
    def is_strategy_allowed(strategy_name: str) -> bool:
        return strategy_name not in SafetyEnforcer.DISALLOWED_STRATEGIES
