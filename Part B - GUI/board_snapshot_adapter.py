def build_board_snapshot(snapshot):
    return {
        "pieces": [
            {
                "kind": p["kind"],
                "color": p["color"],
                "position": p["cell"],
                "motion": p["motion"],
            }
            for p in snapshot.pieces
        ],
        "selected_cell": snapshot.selected_cell,
        "is_game_over": snapshot.game_over,
        "timestamp_ms": snapshot.timestamp,
    }