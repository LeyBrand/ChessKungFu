from view.game_snapshot import BoardSnapshot, PieceSnapshot, MotionSnapshot


def build_board_snapshot(snapshot):
    pieces = [
        PieceSnapshot(
            id=p["id"], kind=p["kind"], color=p["color"],
            position=p["cell"],
            motion=_extract_motion(p),
            state=p["state"],
        ) for p in snapshot.pieces
    ]
    return BoardSnapshot(
        pieces=pieces,
        selected_cell=snapshot.selected_cell,
        is_game_over=snapshot.game_over,
        timestamp_ms=snapshot.timestamp,
        move_history=snapshot.move_history,
    ).to_dict()


def _extract_motion(piece_view):
    motion = piece_view.get("motion")
    if motion is None:
        return None
    return MotionSnapshot(from_cell=motion["from"], to_cell=motion["to"], progress=motion["progress"])