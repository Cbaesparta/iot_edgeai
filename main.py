import atexit
import threading
import time
from collections import deque
from datetime import datetime
from typing import Dict

import cv2
import psutil
from flask import Flask, Response, jsonify
from dotenv import load_dotenv

from ai_model.detect import DetectionResult, YoloDetector
from alerts.notifier import AlertManager
from camera.capture import CameraCapture
from config.settings import settings
from mqtt.publisher import MqttPublisher

load_dotenv()

app = Flask(__name__)

camera = CameraCapture(settings.camera_index, settings.frame_width, settings.frame_height)
detector = YoloDetector(settings.model_name, settings.confidence_threshold, settings.classes_filter)
mqtt_pub = MqttPublisher(settings.mqtt_host, settings.mqtt_port, settings.mqtt_keepalive, settings.mqtt_enabled)
alerts = AlertManager(settings.alert_cooldown_sec, settings.alerts_enabled)

state_lock = threading.Lock()
latest_raw_frame = None
latest_annotated_frame = None
latest_detection: DetectionResult = DetectionResult(objects=[], counts={})
latest_status: Dict = {
    "fps": 0.0,
    "cpu_percent": 0.0,
    "memory_percent": 0.0,
    "uptime_sec": 0,
    "frame_count": 0,
}
detection_history = deque(maxlen=settings.detections_history_limit)
start_time = time.time()



def _encode_jpeg(frame):
    ok, buffer = cv2.imencode(".jpg", frame)
    if not ok:
        return None
    return buffer.tobytes()



def _processing_loop():
    global latest_raw_frame, latest_annotated_frame, latest_detection

    interval = 1.0 / max(settings.target_fps, 1)
    last_cycle = time.time()

    while True:
        frame = camera.get_frame()
        if frame is None:
            time.sleep(0.01)
            continue

        ts = datetime.now().strftime("%H:%M:%S")

        detection = detector.detect(frame)
        annotated = detector.draw(frame.copy(), detection)

        now = time.time()
        fps = 1.0 / max(now - last_cycle, 1e-6)
        last_cycle = now

        status = {
            "fps": round(fps, 2),
            "cpu_percent": psutil.cpu_percent(interval=0.0),
            "memory_percent": psutil.virtual_memory().percent,
            "uptime_sec": int(now - start_time),
            "frame_count": camera.frame_count,
            "time": ts,
        }

        detection_payload = {
            "time": ts,
            "counts": detection.counts,
            "objects": detection.objects,
        }

        with state_lock:
            latest_raw_frame = frame
            latest_annotated_frame = annotated
            latest_detection = detection
            latest_status.update(status)
            detection_history.append(detection_payload)

        mqtt_pub.publish_json(settings.topic_detections, detection_payload)
        mqtt_pub.publish_json(settings.topic_status, status)
        mqtt_pub.publish_json(settings.topic_framecount, {"frame_count": camera.frame_count, "time": ts})

        alert = alerts.check_and_create(detection.counts, ts)
        if alert:
            mqtt_pub.publish_json(settings.topic_alerts, alert)

        elapsed = time.time() - now
        sleep_time = max(0.0, interval - elapsed)
        if sleep_time > 0:
            time.sleep(sleep_time)



def _generate_mjpeg(annotated: bool = True):
    while True:
        with state_lock:
            frame = latest_annotated_frame if annotated else latest_raw_frame

        if frame is None:
            time.sleep(0.03)
            continue

        jpg = _encode_jpeg(frame)
        if jpg is None:
            continue

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + jpg + b"\r\n"
        )


@app.get("/")
def home():
    return jsonify(
        {
            "name": "jetson-ai-iot",
            "endpoints": ["/video", "/video/raw", "/api/status", "/api/detections", "/api/alerts"],
        }
    )


@app.get("/video")
def video_feed():
    return Response(_generate_mjpeg(annotated=True), mimetype="multipart/x-mixed-replace; boundary=frame")


@app.get("/video/raw")
def video_raw_feed():
    return Response(_generate_mjpeg(annotated=False), mimetype="multipart/x-mixed-replace; boundary=frame")


@app.get("/api/status")
def api_status():
    with state_lock:
        return jsonify(dict(latest_status))


@app.get("/api/detections")
def api_detections():
    with state_lock:
        payload = {
            "latest_counts": latest_detection.counts,
            "history": list(detection_history),
        }
    return jsonify(payload)


@app.get("/api/alerts")
def api_alerts():
    return jsonify({"alerts": alerts.list_alerts()})



def startup() -> None:
    camera.start()
    mqtt_pub.connect()

    worker = threading.Thread(target=_processing_loop, daemon=True)
    worker.start()



def shutdown() -> None:
    mqtt_pub.disconnect()
    camera.stop()


atexit.register(shutdown)

if __name__ == "__main__":
    startup()
    app.run(host=settings.flask_host, port=settings.flask_port, debug=False, threaded=True)
