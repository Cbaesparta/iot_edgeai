import json
from typing import Any, Dict

import paho.mqtt.client as mqtt


class MqttPublisher:
    def __init__(self, host: str, port: int, keepalive: int = 60, enabled: bool = True):
        self.enabled = enabled
        self.host = host
        self.port = port
        self.keepalive = keepalive
        self.client = mqtt.Client()
        self.connected = False

    def connect(self) -> None:
        if not self.enabled:
            return
        self.client.connect(self.host, self.port, self.keepalive)
        self.client.loop_start()
        self.connected = True

    def publish_json(self, topic: str, payload: Dict[str, Any]) -> None:
        if not self.enabled:
            return
        self.client.publish(topic, json.dumps(payload), qos=0, retain=False)

    def disconnect(self) -> None:
        if not self.enabled:
            return
        if self.connected:
            self.client.loop_stop()
            self.client.disconnect()
            self.connected = False
