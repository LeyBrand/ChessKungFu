import asyncio
import getpass

from data.player_store import InvalidCredentialsError

MAX_PASSWORD_ATTEMPTS = 3


class LoginRejectedError(Exception):
    pass


def _default_prompt_username(websocket):
    peer = getattr(websocket, "remote_address", "unknown")
    return input(f"New connection from {peer} - enter username: ")


def _default_prompt_password(websocket, prompt_text):
    return getpass.getpass(prompt_text)


async def login(websocket, player_store,
                 prompt_username=_default_prompt_username,
                 prompt_password=_default_prompt_password):
    """Runs the full username+password exchange on the server's own
    terminal. Returns the logged-in username, or raises
    LoginRejectedError if the client should be rejected."""
    loop = asyncio.get_event_loop()
    username = await loop.run_in_executor(None, prompt_username, websocket)

    if player_store.player_exists(username):
        for attempt in range(1, MAX_PASSWORD_ATTEMPTS + 1):
            password = await loop.run_in_executor(
                None, prompt_password, websocket, f"Password for {username}: "
            )
            try:
                player_store.verify_password(username, password)
                return username
            except InvalidCredentialsError:
                remaining = MAX_PASSWORD_ATTEMPTS - attempt
                print(f"Wrong password for {username} ({remaining} attempts left)")
        raise LoginRejectedError(f"too many failed password attempts for '{username}'")
    else:
        password = await loop.run_in_executor(
            None, prompt_password, websocket, f"New user '{username}' - choose a password: "
        )
        player_store.create_player(username, password)
        print(f"Registered new player: {username}")
        return username