from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # MQTT broker (the "mqtt" service in docker-compose)
    mqtt_host: str = "mqtt"
    mqtt_port: int = 1883
    mqtt_username: str | None = None
    mqtt_password: str | None = None

    # Topics the ESP32 publishes/subscribes to
    device_telemetry_topic: str = "device/+/telemetry"
    device_command_topic_template: str = "device/{device_id}/command"

    app_env: str = "development"


settings = Settings()
