def build_board_snapshot(snapshot):
    return {
        "pieces": [
            {
                "id": p["id"],
                "kind": p["kind"],
                "color": p["color"],
                "position": p["cell"],
                "motion": _extract_motion(p),
                "state": p["state"],
            } for p in snapshot.pieces
        ],
        "selected_cell": snapshot.selected_cell,
        "is_game_over": snapshot.game_over,
        "timestamp_ms": snapshot.timestamp,
        "move_history": snapshot.move_history, 
    }
def _extract_motion(piece_view):
    return piece_view.get("motion")
