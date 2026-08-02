import asyncio
import json

from fastapi import WebSocket


class ConnectionManager:
    """Tracks connected web app clients and broadcasts messages to them.

    MQTT and WebSockets have different lifecycles (thread-based callback vs
    asyncio), so `broadcast` is safe to call from either — see main.py for
    how the MQTT thread schedules it onto the event loop.
    """

    def __init__(self) -> None:
        self._connections: set[WebSocket] = set()
        self._lock = asyncio.Lock()

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        async with self._lock:
            self._connections.add(ws)

    async def disconnect(self, ws: WebSocket) -> None:
        async with self._lock:
            self._connections.discard(ws)

    async def broadcast(self, message: dict) -> None:
        data = json.dumps(message)
        dead: list[WebSocket] = []
        async with self._lock:
            targets = list(self._connections)
        for ws in targets:
            try:
                await ws.send_text(data)
            except Exception:
                dead.append(ws)
        if dead:
            async with self._lock:
                for ws in dead:
                    self._connections.discard(ws)


manager = ConnectionManager()
