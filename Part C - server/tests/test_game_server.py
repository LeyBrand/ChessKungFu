import asyncio
import json

import pytest

from game_server import GameServer
from player_registry import PlayerRegistry


class FakeWebSocket:
    """Stand-in for a real websockets connection object - just needs to be hashable."""
    pass


@pytest.mark.asyncio
async def test_register_and_unregister_track_clients():
    server = GameServer(bridge=None)
    ws = FakeWebSocket()

    assert server.clients == set()

    await server.register(ws)
    assert server.clients == {ws}

    await server.unregister(ws)
    assert server.clients == set()


class FakeSendingWebSocket:
    def __init__(self):
        self.sent_messages = []

    async def send(self, message):
        self.sent_messages.append(message)


class FakeBridge:
    def get_render_snapshot(self):
        return {"pieces": [], "timestamp_ms": 0}


@pytest.mark.asyncio
async def test_broadcast_state_sends_snapshot_to_all_clients():
    server = GameServer(bridge=FakeBridge())
    ws1, ws2 = FakeSendingWebSocket(), FakeSendingWebSocket()
    await server.register(ws1)
    await server.register(ws2)

    await server.broadcast_state()

    expected = json.dumps({"type": "state", "snapshot": {"pieces": [], "timestamp_ms": 0}})
    assert ws1.sent_messages == [expected]
    assert ws2.sent_messages == [expected]


@pytest.mark.asyncio
async def test_broadcast_state_does_nothing_when_no_clients():
    calls = []

    class TrackingBridge:
        def get_render_snapshot(self):
            calls.append(1)
            return {}

    server = GameServer(bridge=TrackingBridge())
    await server.broadcast_state()

    assert calls == []


class RecordingBridge:
    def __init__(self):
        self.click_calls = []
        self.jump_calls = []

    def get_render_snapshot(self):
        return {"pieces": [], "timestamp_ms": 0}

    def handle_click(self, x, y):
        self.click_calls.append((x, y))

    def handle_jump(self, x, y):
        self.jump_calls.append((x, y))


@pytest.mark.asyncio
async def test_handle_message_routes_click_to_bridge():
    bridge = RecordingBridge()
    server = GameServer(bridge=bridge)

    await server._handle_message(json.dumps({"type": "click", "x": 10, "y": 20}))

    assert bridge.click_calls == [(10, 20)]
    assert bridge.jump_calls == []


@pytest.mark.asyncio
async def test_handle_message_routes_jump_to_bridge():
    bridge = RecordingBridge()
    server = GameServer(bridge=bridge)

    await server._handle_message(json.dumps({"type": "jump", "x": 5, "y": 6}))

    assert bridge.jump_calls == [(5, 6)]
    assert bridge.click_calls == []


class FakeStreamingWebSocket:
    """Simulates a connection that yields a fixed list of messages, then disconnects."""

    def __init__(self, messages):
        self._messages = iter(messages)
        self.sent_messages = []

    async def send(self, message):
        self.sent_messages.append(message)

    async def close(self):
        pass

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            return next(self._messages)
        except StopIteration:
            raise StopAsyncIteration


@pytest.mark.asyncio
async def test_handle_client_processes_messages_then_unregisters():
    bridge = RecordingBridge()
    server = GameServer(bridge=bridge, prompt_username=lambda ws: "alice")
    ws = FakeStreamingWebSocket([
        json.dumps({"type": "click", "x": 0, "y": 600}),
        json.dumps({"type": "click", "x": 0, "y": 500}),
    ])

    await server.handle_client(ws)

    assert bridge.click_calls == [(0, 600), (0, 500)]
    # unregistered after the client's message stream ends (disconnect)
    assert ws not in server.clients
    assert server.player_registry.get_player(ws) is None
    # one broadcast on connect + one per message = 3 state messages
    assert len(ws.sent_messages) == 3


class HeldOpenWebSocket:
    """Stays 'connected' (async iteration blocks) until release() is called -
    lets a test keep two clients simultaneously connected."""

    def __init__(self, username):
        self.username = username
        self.sent_messages = []
        self._release_event = asyncio.Event()

    async def send(self, message):
        self.sent_messages.append(message)

    async def close(self):
        pass

    def release(self):
        self._release_event.set()

    def __aiter__(self):
        return self

    async def __anext__(self):
        await self._release_event.wait()
        raise StopAsyncIteration


@pytest.mark.asyncio
async def test_handle_client_assigns_colors_in_join_order():
    bridge = RecordingBridge()
    server = GameServer(bridge=bridge, prompt_username=lambda ws: ws.username)

    ws1 = HeldOpenWebSocket("alice")
    ws2 = HeldOpenWebSocket("bob")

    task1 = asyncio.create_task(server.handle_client(ws1))
    await asyncio.sleep(0.05)  # let ws1's login (runs in an executor thread) finish
    task2 = asyncio.create_task(server.handle_client(ws2))
    await asyncio.sleep(0.05)  # let ws2's login finish too

    # both still "connected" at this point - check colors while both are live
    assert server.player_registry.get_player(ws1)["color"] == "white"
    assert server.player_registry.get_player(ws2)["color"] == "black"

    ws1.release()
    ws2.release()
    await task1
    await task2


@pytest.mark.asyncio
async def test_third_client_is_rejected_when_server_is_full():
    bridge = RecordingBridge()
    server = GameServer(bridge=bridge, prompt_username=lambda ws: "someone")
    server.player_registry.register(FakeStreamingWebSocket([]), "alice")
    server.player_registry.register(FakeStreamingWebSocket([]), "bob")

    ws3 = FakeStreamingWebSocket([])
    await server.handle_client(ws3)

    assert len(ws3.sent_messages) == 1
    sent = json.loads(ws3.sent_messages[0])
    assert sent["type"] == "error"
    assert ws3 not in server.clients


class TickingBridge(RecordingBridge):
    def __init__(self):
        super().__init__()
        self.tick_calls = []

    def tick(self, elapsed_ms):
        self.tick_calls.append(elapsed_ms)


@pytest.mark.asyncio
async def test_tick_loop_advances_bridge_and_broadcasts():
    bridge = TickingBridge()
    server = GameServer(bridge=bridge)
    ws = FakeSendingWebSocket()
    await server.register(ws)

    task = asyncio.create_task(server.tick_loop(interval_sec=0))
    try:
        await asyncio.wait_for(task, timeout=0.05)
    except asyncio.TimeoutError:
        task.cancel()

    assert len(bridge.tick_calls) > 0
    assert len(ws.sent_messages) > 0