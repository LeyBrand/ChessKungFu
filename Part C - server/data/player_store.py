import sqlite3
import hashlib
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "players.db")
STARTING_RATING = 1200


class InvalidCredentialsError(Exception):
    pass


class UsernameTakenError(Exception):
    pass


class PlayerStore:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self._conn = sqlite3.connect(self.db_path)
        self._init_schema()

    def close(self):
        self._conn.close()

    def _init_schema(self):
        self._conn.execute(f"""
            CREATE TABLE IF NOT EXISTS players (
                username TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                rating INTEGER NOT NULL DEFAULT {STARTING_RATING}
            )
        """)
        self._conn.commit()

    @staticmethod
    def _hash_password(password, salt):
        return hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000).hex()

    def player_exists(self, username):
        row = self._conn.execute(
            "SELECT 1 FROM players WHERE username = ?", (username,)
        ).fetchone()
        return row is not None

    def create_player(self, username, password):
        if self.player_exists(username):
            raise UsernameTakenError(f"Username already taken: {username}")

        salt = os.urandom(16)
        password_hash = self._hash_password(password, salt)
        self._conn.execute(
            "INSERT INTO players (username, password_hash, salt, rating) VALUES (?, ?, ?, ?)",
            (username, password_hash, salt.hex(), STARTING_RATING),
        )
        self._conn.commit()

    def verify_password(self, username, password):
        row = self._conn.execute(
            "SELECT password_hash, salt FROM players WHERE username = ?", (username,)
        ).fetchone()
        if row is None:
            raise InvalidCredentialsError(f"No such player: {username}")

        stored_hash, salt_hex = row
        salt = bytes.fromhex(salt_hex)
        if self._hash_password(password, salt) != stored_hash:
            raise InvalidCredentialsError("Wrong password")

    def get_rating(self, username):
        row = self._conn.execute(
            "SELECT rating FROM players WHERE username = ?", (username,)
        ).fetchone()
        return row[0] if row else None

    def update_rating(self, username, new_rating):
        self._conn.execute(
            "UPDATE players SET rating = ? WHERE username = ?", (new_rating, username)
        )
        self._conn.commit()