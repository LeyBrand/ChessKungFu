# Part B - GUI/tests/audio/test_sound_player.py
from audio.sound_player import SoundPlayer


def test_play_skips_and_warns_when_file_missing(tmp_path, capsys):
    calls = []
    player = SoundPlayer(root=str(tmp_path), play_func=lambda path: calls.append(path))

    player.play("does_not_exist.wav")

    assert calls == []
    captured = capsys.readouterr()
    assert "Warning" in captured.out


def test_play_calls_backend_with_correct_path_when_file_exists(tmp_path):
    sound_file = tmp_path / "move.wav"
    sound_file.write_bytes(b"")  # content doesn't matter, only existence

    calls = []
    player = SoundPlayer(root=str(tmp_path), play_func=lambda path: calls.append(path))

    player.play("move.wav")

    assert calls == [str(sound_file)]