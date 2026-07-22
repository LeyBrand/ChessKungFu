import asyncio
import json
import queue
import threading

import websockets

SERVER_URL = "ws://localhost:8765"


def login_async(username, password, result_queue):
    """Runs in a background thread. Puts a dict on result_queue:
    {"ok": True, "username":..., "rating":...} or {"ok": False, "reason":...}."""
    threading.Thread(
        target=lambda: asyncio.run(_login_flow(username, password, result_queue)),
        daemon=True,
    ).start()


async def _login_flow(username, password, result_queue):
    try:
        async with websockets.connect(SERVER_URL) as ws:
            await ws.send(json.dumps({"type": "LOGIN", "username": username, "password": password}))
            raw = await ws.recv()
            data = json.loads(raw)

        if data.get("type") == "LOGIN_OK":
            result_queue.put({"ok": True, "username": data["username"], "rating": data["rating"]})
        else:
            result_queue.put({"ok": False, "reason": data.get("reason", "login failed")})
    except Exception as exc:  # connection refused, timeout, etc.
        result_queue.put({"ok": False, "reason": f"connection error: {exc}"})