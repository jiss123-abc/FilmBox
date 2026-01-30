import random

def apply_exploration(results: list, exploration_rate: float) -> list:
    """
    Injects diversity by shuffling the tail of the recommendations.
    - Rate 0.0: No change (Pure Exploitation).
    - Rate 0.5: Top 50% fixed, Bottom 50% shuffled.
    - Rate 1.0: Full shuffle (Pure Randomness).
    """
    if exploration_rate <= 0:
        return results

    if not results:
        return []

    cutoff = int(len(results) * (1 - exploration_rate))
    
    # Ensure at least one item remains in 'top' if rate isn't 1.0
    if cutoff == 0 and exploration_rate < 1.0 and len(results) > 0:
        cutoff = 1

    top = results[:cutoff]
    rest = results[cutoff:]

    random.shuffle(rest)
    return top + rest
