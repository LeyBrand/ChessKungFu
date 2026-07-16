def build_board_snapshot(snapshot):
    return {
        "pieces": [
            {
                "kind": p["kind"],
                "color": p["color"],
                "position": p["cell"],           # (col, row) לוגי
                "motion": _extract_motion(p),     # None או {"from": (col,row), "to": (col,row), "progress": 0..1}
            } for p in snapshot.pieces
        ],
        "selected_cell": snapshot.selected_cell,
        "is_game_over": snapshot.game_over,
    }

def _extract_motion(piece_view):
    # רק אם GameEngine בעתיד יחשוף motion logical (start_cell/end_cell/progress)
    # ולא pixel/start_pixel/end_pixel כמו היום
    return piece_view.get("motion")