from datetime import datetime, timezone

from pydantic import BaseModel, Field


class DeviceTelemetry(BaseModel):
    """Payload published by the ESP32 on device/{id}/telemetry."""

    device_id: str
    value: float
    unit: str | None = None
    ts: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DeviceCommand(BaseModel):
    """Payload the server publishes to device/{id}/command."""

    action: str
    params: dict = Field(default_factory=dict)


class ClientMessage(BaseModel):
    """Inbound message from a web app client over WebSocket."""

    type: str
    device_id: str | None = None
    payload: dict = Field(default_factory=dict)
