"""
GameServer: owns the single BusinessBridge instance and the set of
connected clients. No asyncio.serve() call here - that lives in a
thin runner script, so GameServer itself stays easy to unit test.
"""
import asyncio
import json


class GameServer:
    def __init__(self, bridge):
        self.bridge = bridge
        self.clients = set()

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

    async def handle_client(self, websocket):
        await self.register(websocket)
        try:
            await self.broadcast_state()
            async for raw in websocket:
                await self._handle_message(raw)
                await self.broadcast_state()
        finally:
            await self.unregister(websocket)

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