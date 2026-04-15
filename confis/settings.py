import os
from dataclasses import dataclass


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    camera_index: int = int(os.getenv("CAMERA_INDEX", "0"))
    frame_width: int = int(os.getenv("FRAME_WIDTH", "1280"))
    frame_height: int = int(os.getenv("FRAME_HEIGHT", "720"))
    target_fps: int = int(os.getenv("TARGET_FPS", "20"))

    flask_host: str = os.getenv("FLASK_HOST", "0.0.0.0")
    flask_port: int = int(os.getenv("FLASK_PORT", "5000"))

    mqtt_enabled: bool = _env_bool("MQTT_ENABLED", True)
    mqtt_host: str = os.getenv("MQTT_HOST", "127.0.0.1")
    mqtt_port: int = int(os.getenv("MQTT_PORT", "1883"))
    mqtt_keepalive: int = int(os.getenv("MQTT_KEEPALIVE", "60"))

    topic_detections: str = os.getenv("MQTT_TOPIC_DETECTIONS", "jetson/camera/detections")
    topic_alerts: str = os.getenv("MQTT_TOPIC_ALERTS", "jetson/alerts")
    topic_status: str = os.getenv("MQTT_TOPIC_STATUS", "jetson/status")
    topic_framecount: str = os.getenv("MQTT_TOPIC_FRAMECOUNT", "jetson/framecount")

    model_name: str = os.getenv("MODEL_NAME", "yolov8n.pt")
    confidence_threshold: float = float(os.getenv("CONFIDENCE_THRESHOLD", "0.35"))
    classes_filter: tuple = tuple(
        c.strip() for c in os.getenv("CLASSES_FILTER", "person,car,cell phone,backpack").split(",") if c.strip()
    )

    alerts_enabled: bool = _env_bool("ALERTS_ENABLED", True)
    alert_cooldown_sec: int = int(os.getenv("ALERT_COOLDOWN_SEC", "10"))

    detections_history_limit: int = int(os.getenv("DETECTIONS_HISTORY_LIMIT", "500"))


settings = Settings()
