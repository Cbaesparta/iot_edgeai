import json

import paho.mqtt.client as mqtt

TOPICS = [
    "jetson/camera/detections",
    "jetson/alerts",
    "jetson/status",
    "jetson/framecount",
]


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker")
        for topic in TOPICS:
            client.subscribe(topic)
    else:
        print(f"MQTT connection failed with code={rc}")



def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode("utf-8"))
    except Exception:
        payload = msg.payload.decode("utf-8", errors="replace")

    print(f"[{msg.topic}] {payload}")


if __name__ == "__main__":
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect("127.0.0.1", 1883, 60)
    client.loop_forever()
