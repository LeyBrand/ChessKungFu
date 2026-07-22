K_FACTOR = 32


def expected_score(rating_a, rating_b):
    """Probability that player A beats player B, per the standard
    logistic ELO formula."""
    return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))


def update_ratings(winner_rating, loser_rating, k=K_FACTOR):
    """Returns (new_winner_rating, new_loser_rating) as ints, rounded."""
    expected_winner = expected_score(winner_rating, loser_rating)
    expected_loser = 1 - expected_winner

    new_winner = winner_rating + k * (1 - expected_winner)
    new_loser = loser_rating + k * (0 - expected_loser)

    return round(new_winner), round(new_loser)