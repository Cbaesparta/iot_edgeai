import threading
import time
from typing import Optional

import cv2


class CameraCapture:
    def __init__(self, index: int = 0, width: int = 1280, height: int = 720):
        self.index = index
        self.width = width
        self.height = height

        self._cap: Optional[cv2.VideoCapture] = None
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self._frame = None
        self._frame_count = 0
        self._last_frame_time = 0.0

    def start(self) -> None:
        if self._running:
            return

        self._cap = cv2.VideoCapture(self.index)
        if not self._cap.isOpened():
            raise RuntimeError(f"Unable to open camera index {self.index}")

        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

        self._running = True
        self._thread = threading.Thread(target=self._reader_loop, daemon=True)
        self._thread.start()

    def _reader_loop(self) -> None:
        failed_reads = 0
        while self._running and self._cap is not None:
            ok, frame = self._cap.read()
            if not ok:
                failed_reads += 1
                # Attempt camera re-open after repeated read failures (unplug/replug scenarios).
                if failed_reads >= 30:
                    try:
                        self._cap.release()
                    except Exception:
                        pass
                    self._cap = cv2.VideoCapture(self.index)
                    self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
                    self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
                    failed_reads = 0
                time.sleep(0.01)
                continue

            failed_reads = 0

            with self._lock:
                self._frame = frame
                self._frame_count += 1
                self._last_frame_time = time.time()

    def get_frame(self):
        with self._lock:
            return None if self._frame is None else self._frame.copy()

    @property
    def frame_count(self) -> int:
        with self._lock:
            return self._frame_count

    @property
    def last_frame_time(self) -> float:
        with self._lock:
            return self._last_frame_time

    def stop(self) -> None:
        self._running = False
        if self._thread is not None:
            self._thread.join(timeout=1.0)

        if self._cap is not None:
            self._cap.release()
            self._cap = None
