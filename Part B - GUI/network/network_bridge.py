import asyncio
import json
import queue
import threading

import websockets

SERVER_URL = "ws://127.0.0.1:8765"


class NetworkBridge:
    """Owns ONE persistent websocket connection for the whole client
    session - login through gameplay. Runs its own asyncio event loop
    in a background thread; the main (GUI) thread only ever touches
    thread-safe queues, never the socket directly."""

    def __init__(self):
        self.incoming = queue.Queue()   # dicts received from server
        self._outgoing = queue.Queue()  # dicts to send
        self._thread = None

    def start(self):
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def send(self, message: dict):
        self._outgoing.put(message)

    def poll(self):
        """Non-blocking. Returns all messages received since the last
        call (possibly empty list)."""
        messages = []
        while True:
            try:
                messages.append(self.incoming.get_nowait())
            except queue.Empty:
                break
        return messages

    def _run(self):
        asyncio.run(self._main())

    async def _main(self):
        async with websockets.connect(SERVER_URL) as ws:
            await asyncio.gather(self._reader(ws), self._writer(ws))

    async def _reader(self, ws):
        async for raw in ws:
            self.incoming.put(json.loads(raw))

    async def _writer(self, ws):
        while True:
            try:
                message = self._outgoing.get_nowait()
                await ws.send(json.dumps(message))
            except queue.Empty:
                await asyncio.sleep(0.02)

    def _run(self):
        import asyncio as _asyncio
        if hasattr(_asyncio, "WindowsSelectorEventLoopPolicy"):
            _asyncio.set_event_loop_policy(_asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(self._main())