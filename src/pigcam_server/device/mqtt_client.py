import asyncio
import json
import logging

import paho.mqtt.client as mqtt

from myproject.config import settings
from myproject.models import DeviceCommand, DeviceTelemetry

logger = logging.getLogger(__name__)


class MqttBridge:
    """Wraps paho-mqtt (which runs its own network thread) and hands
    incoming messages off to the asyncio event loop via a queue.
    """

    def __init__(self) -> None:
        self._client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
        if settings.mqtt_username:
            self._client.username_pw_set(settings.mqtt_username, settings.mqtt_password)
        self._client.on_connect = self._on_connect
        self._client.on_message = self._on_message
        self._loop: asyncio.AbstractEventLoop | None = None
        self.telemetry_queue: asyncio.Queue[DeviceTelemetry] = asyncio.Queue()

    def _on_connect(self, client, userdata, flags, reason_code, properties=None):
        logger.info("Connected to MQTT broker (rc=%s)", reason_code)
        client.subscribe(settings.device_telemetry_topic)

    def _on_message(self, client, userdata, msg):
        # Runs on paho's network thread — never touch the event loop directly.
        try:
            data = json.loads(msg.payload.decode())
            device_id = msg.topic.split("/")[1]
            telemetry = DeviceTelemetry(device_id=device_id, **data)
        except Exception:
            logger.exception("Bad telemetry payload on %s", msg.topic)
            return

        if self._loop:
            self._loop.call_soon_threadsafe(self.telemetry_queue.put_nowait, telemetry)

    async def start(self) -> None:
        self._loop = asyncio.get_running_loop()
        self._client.reconnect_delay_set(min_delay=1, max_delay=30)
        # connect_async + loop_start: won't block or raise if the broker
        # isn't up yet (e.g. first boot before mosquitto is ready, or
        # running locally without docker) — it retries in the background.
        self._client.connect_async(settings.mqtt_host, settings.mqtt_port)
        self._client.loop_start()  # spawns paho's own background thread

    async def stop(self) -> None:
        self._client.loop_stop()
        self._client.disconnect()

    def send_command(self, device_id: str, command: DeviceCommand) -> None:
        topic = settings.device_command_topic_template.format(device_id=device_id)
        self._client.publish(topic, command.model_dump_json())


bridge = MqttBridge()
