from tournament.elo import expected_score, update_ratings


def test_expected_score_is_half_for_equal_ratings():
    assert expected_score(1200, 1200) == 0.5


def test_expected_score_favors_higher_rated_player():
    assert expected_score(1400, 1200) > 0.5
    assert expected_score(1200, 1400) < 0.5


def test_update_ratings_winner_gains_loser_loses_equal_ratings():
    new_winner, new_loser = update_ratings(1200, 1200)
    assert new_winner == 1216   # 1200 + 32 * 0.5
    assert new_loser == 1184    # 1200 - 32 * 0.5


def test_update_ratings_zero_sum():
    new_winner, new_loser = update_ratings(1350, 1180)
    gain = new_winner - 1350
    loss = 1180 - new_loser
    assert gain == loss  # points gained == points lost (rounding aside)


def test_upset_win_gains_more_than_expected_win():
    # lower-rated player beating a much higher-rated one gains a lot
    upset_gain, _ = update_ratings(winner_rating=1100, loser_rating=1500)
    # higher-rated player beating a much lower-rated one gains little
    expected_gain, _ = update_ratings(winner_rating=1500, loser_rating=1100)

    assert (upset_gain - 1100) > (expected_gain - 1500)


def test_ratings_never_go_negative_for_reasonable_inputs():
    new_winner, new_loser = update_ratings(100, 2000)
    assert new_loser >= 0