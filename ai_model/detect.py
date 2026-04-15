from collections import Counter
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

import cv2
from ultralytics import YOLO


@dataclass
class DetectionResult:
    objects: List[Dict[str, Any]]
    counts: Dict[str, int]


class YoloDetector:
    def __init__(self, model_name: str = "yolov8n.pt", confidence_threshold: float = 0.35, classes_filter: Tuple[str, ...] = ()):
        self.model = YOLO(model_name)
        self.confidence_threshold = confidence_threshold
        self.classes_filter = set(classes_filter or [])

    def detect(self, frame) -> DetectionResult:
        results = self.model.predict(frame, verbose=False, conf=self.confidence_threshold)
        objects: List[Dict[str, Any]] = []

        for result in results:
            for box in result.boxes:
                cls_idx = int(box.cls[0].item())
                name = self.model.names.get(cls_idx, str(cls_idx))
                if self.classes_filter and name not in self.classes_filter:
                    continue

                conf = float(box.conf[0].item())
                x1, y1, x2, y2 = [int(v) for v in box.xyxy[0].tolist()]
                objects.append(
                    {
                        "label": name,
                        "confidence": round(conf, 3),
                        "bbox": [x1, y1, x2, y2],
                    }
                )

        counts = dict(Counter(o["label"] for o in objects))
        return DetectionResult(objects=objects, counts=counts)

    @staticmethod
    def draw(frame, detections: DetectionResult):
        for item in detections.objects:
            x1, y1, x2, y2 = item["bbox"]
            label = f"{item['label']} {item['confidence']:.2f}"
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 220, 0), 2)
            cv2.putText(frame, label, (x1, max(20, y1 - 6)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 220, 0), 2)

        return frame
