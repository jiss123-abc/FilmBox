def recalculate_user_strategy_weight(row):
    """
    Updates the weight for a specific user-strategy pair.
    Formula: 1.0 + (positive_feedback / total_used)
    """
    if row.total_used == 0:
        row.weight = 1.0
    else:
        row.weight = 1.0 + (row.positive_feedback / row.total_used)
