# demo_client.py - שמרי בתוך Part C - server
import asyncio
import json
import websockets

async def main():
    async with websockets.connect("ws://localhost:8765") as ws:
        initial = json.loads(await ws.recv())
        print("Connected! Pieces on board:", len(initial["snapshot"]["pieces"]))

        # מזיזים חייל: מ-(0,6) ל-(0,4) - שני צעדים קדימה
        await ws.send(json.dumps({"type": "click", "x": 0, "y": 600}))
        await ws.send(json.dumps({"type": "click", "x": 0, "y": 400}))

        await asyncio.sleep(1.5)
        while True:
            try:
                msg = json.loads(await asyncio.wait_for(ws.recv(), timeout=0.5))
                print("Got update, timestamp:", msg["snapshot"]["timestamp_ms"])
            except asyncio.TimeoutError:
                break

asyncio.run(main())
