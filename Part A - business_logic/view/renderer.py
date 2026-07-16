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
        "move_history": snapshot.move_history,   # <-- הוסף שורה זו
    }
def _extract_motion(piece_view):
    # רק אם GameEngine בעתיד יחשוף motion logical (start_cell/end_cell/progress)
    # ולא pixel/start_pixel/end_pixel כמו היום
    return piece_view.get("motion")
