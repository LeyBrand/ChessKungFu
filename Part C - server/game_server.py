import asyncio
import json

from player_registry import PlayerRegistry, ServerFullError
from data.player_store import PlayerStore, InvalidCredentialsError

MAX_PASSWORD_ATTEMPTS = 3


def _default_prompt_username(websocket):
    peer = getattr(websocket, "remote_address", "unknown")
    return input(f"New connection from {peer} - enter username: ")


def _default_prompt_password(websocket, prompt_text):
    """Same idea as _default_prompt_username, but for the password.
    Uses getpass so the password isn't echoed to the server's terminal."""
    import getpass
    return getpass.getpass(prompt_text)


class LoginRejectedError(Exception):
    pass


class GameServer:
    def __init__(
        self,
        bridge,
        player_registry=None,
        player_store=None,
        prompt_username=_default_prompt_username,
        prompt_password=_default_prompt_password,
    ):
        self.bridge = bridge
        self.clients = set()
        self.player_registry = player_registry or PlayerRegistry()
        self.player_store = player_store or PlayerStore()
        self._prompt_username = prompt_username
        self._prompt_password = prompt_password

    async def register(self, websocket):
        self.clients.add(websocket)

    async def unregister(self, websocket):
        self.clients.discard(websocket)

    async def broadcast_state(self):
        if not self.clients:
            return
        snapshot = self.bridge.get_render_snapshot()
        message = json.dumps({"type": "state", "snapshot": snapshot})
        await asyncio.gather(
            *(client.send(message) for client in self.clients),
            return_exceptions=True,
        )

    async def _login(self, websocket):
        """Runs the full username+password exchange on the server's own
        terminal. Returns the logged-in username, or raises
        LoginRejectedError if the client should be rejected."""
        loop = asyncio.get_event_loop()
        username = await loop.run_in_executor(None, self._prompt_username, websocket)

        if self.player_store.player_exists(username):
            for attempt in range(1, MAX_PASSWORD_ATTEMPTS + 1):
                password = await loop.run_in_executor(
                    None, self._prompt_password, websocket, f"Password for {username}: "
                )
                try:
                    self.player_store.verify_password(username, password)
                    return username
                except InvalidCredentialsError:
                    remaining = MAX_PASSWORD_ATTEMPTS - attempt
                    print(f"Wrong password for {username} ({remaining} attempts left)")
            raise LoginRejectedError(f"too many failed password attempts for '{username}'")
        else:
            password = await loop.run_in_executor(
                None, self._prompt_password, websocket, f"New user '{username}' - choose a password: "
            )
            self.player_store.create_player(username, password)
            print(f"Registered new player: {username}")
            return username

    async def handle_client(self, websocket):
        if self.player_registry.is_full():
            await websocket.send(json.dumps({"type": "error", "message": "Server is full"}))
            await websocket.close()
            return

        try:
            username = await self._login(websocket)
        except LoginRejectedError as exc:
            await websocket.send(json.dumps({"type": "error", "message": str(exc)}))
            await websocket.close()
            return

        try:
            color = self.player_registry.register(websocket, username)
        except ServerFullError:
            # two clients raced for the last slot - whoever loses gets rejected
            await websocket.send(json.dumps({"type": "error", "message": "Server is full"}))
            await websocket.close()
            return

        print(f"{username} joined as {color}")

        await self.register(websocket)
        try:
            await self.broadcast_state()
            async for raw in websocket:
                await self._handle_message(raw)
                await self.broadcast_state()
        finally:
            await self.unregister(websocket)
            self.player_registry.unregister(websocket)

    async def _handle_message(self, raw):
        data = json.loads(raw)
        if data["type"] == "click":
            self.bridge.handle_click(data["x"], data["y"])
        elif data["type"] == "jump":
            self.bridge.handle_jump(data["x"], data["y"])

    async def tick_loop(self, interval_sec, clock=None):
        clock = clock or asyncio.get_event_loop().time
        last_time = clock()
        while True:
            await asyncio.sleep(interval_sec)
            now = clock()
            elapsed_ms = (now - last_time) * 1000
            last_time = now
            self.bridge.tick(elapsed_ms)
            await self.broadcast_state()