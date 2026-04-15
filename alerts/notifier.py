import time
from typing import Dict, List


class AlertManager:
    def __init__(self, cooldown_sec: int = 10, enabled: bool = True):
        self.cooldown_sec = cooldown_sec
        self.enabled = enabled
        self._last_alert_at = 0.0
        self._alerts: List[Dict] = []

    def check_and_create(self, counts: Dict[str, int], timestamp: str):
        if not self.enabled:
            return None

        people = counts.get("person", 0)
        now = time.time()
        if people > 0 and now - self._last_alert_at >= self.cooldown_sec:
            alert = {
                "type": "person_detected",
                "message": f"Alert: {people} person(s) detected",
                "time": timestamp,
                "severity": "high" if people >= 2 else "medium",
            }
            self._alerts.append(alert)
            self._last_alert_at = now
            return alert

        return None

    def list_alerts(self, limit: int = 50) -> List[Dict]:
        return self._alerts[-limit:]
