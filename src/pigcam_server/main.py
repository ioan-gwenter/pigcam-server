import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from pigcam_server.api.routes import router
from pigcam_server.api.ws_manager import manager
from pigcam_server.device.mqtt_client import bridge

logging.basicConfig(level=logging.INFO)


async def _forward_telemetry_to_clients() -> None:
    """Pulls telemetry the MQTT bridge received from the ESP32 and
    broadcasts it to whatever web app clients are connected."""
    while True:
        telemetry = await bridge.telemetry_queue.get()
        await manager.broadcast(
            {"type": "telemetry", "device_id": telemetry.device_id, "value": telemetry.value}
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    await bridge.start()
    forward_task = asyncio.create_task(_forward_telemetry_to_clients())
    yield
    forward_task.cancel()
    await bridge.stop()


app = FastAPI(title="myproject", lifespan=lifespan)
app.include_router(router)
