from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from myproject.api.ws_manager import manager
from myproject.device.mqtt_client import bridge
from myproject.models import DeviceCommand

router = APIRouter()


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.post("/devices/{device_id}/command")
async def send_command(device_id: str, command: DeviceCommand):
    bridge.send_command(device_id, command)
    return {"sent": True, "device_id": device_id}


@router.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await manager.connect(ws)
    try:
        while True:
            # Currently just keeps the connection alive / drains inbound
            # client messages. Parse into ClientMessage here once the web
            # app needs to send commands through this socket too.
            await ws.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect(ws)
