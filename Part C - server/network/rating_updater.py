from tournament.elo import update_ratings
from constants import Color


def subscribe_rating_update(event_bus, get_player_ids, connection_manager, player_store):
    """Subscribes a GAME_OVER listener on a room's event_bus that looks up
    both players' current ratings, computes the ELO update, and persists
    it. get_player_ids is a zero-arg callable (not a plain dict) so we
    always read the room's *current* seating at the moment the game ends,
    not whatever it was when the room was created."""

    def _on_game_over(winner=None, **kwargs):
        if winner is None:
            return  # e.g. a draw / no-winner GAME_OVER, if that's ever added

        player_ids = get_player_ids()
        loser_color = Color.BLACK if winner == Color.WHITE else Color.WHITE

        winner_id = player_ids.get(winner)
        loser_id = player_ids.get(loser_color)
        if winner_id is None or loser_id is None:
            return  # room wasn't fully seated - nothing sensible to update

        winner_username = connection_manager.get_username(winner_id)
        loser_username = connection_manager.get_username(loser_id)
        if winner_username is None or loser_username is None:
            return

        winner_rating = player_store.get_rating(winner_username)
        loser_rating = player_store.get_rating(loser_username)

        new_winner_rating, new_loser_rating = update_ratings(winner_rating, loser_rating)
        player_store.update_rating(winner_username, new_winner_rating)
        player_store.update_rating(loser_username, new_loser_rating)

    event_bus.subscribe("GAME_OVER", _on_game_over)