from typing import Dict, Any, Optional

class AnomalyDetector:
    def __init__(self, rtt_threshold: float = 100.0, loss_threshold: float = 5.0, jitter_threshold: float = 20.0):
        self.rtt_threshold = rtt_threshold
        self.loss_threshold = loss_threshold
        self.jitter_threshold = jitter_threshold

    def detect(self, current_metrics: Dict[str, Any], baseline_metrics: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Detects statistical anomalies based on current metrics and thresholds.
        """
        anomaly_detected = False
        reason = ""
        metric = ""
        observed_value = 0.0
        threshold = 0.0

        if current_metrics.get("loss_pct", 0) > self.loss_threshold:
            anomaly_detected = True
            reason = "High packet loss detected"
            metric = "loss_pct"
            observed_value = current_metrics["loss_pct"]
            threshold = self.loss_threshold

        elif current_metrics.get("p95_ms", 0) > self.rtt_threshold:
            anomaly_detected = True
            reason = "P95 Latency spike detected"
            metric = "p95_ms"
            observed_value = current_metrics["p95_ms"]
            threshold = self.rtt_threshold

        elif current_metrics.get("jitter_ms", 0) > self.jitter_threshold:
            anomaly_detected = True
            reason = "High jitter/unstable delay detected"
            metric = "jitter_ms"
            observed_value = current_metrics["jitter_ms"]
            threshold = self.jitter_threshold

        if anomaly_detected:
            return {
                "metric": metric,
                "observed_value": observed_value,
                "baseline": baseline_metrics.get(metric, 0) if baseline_metrics else 0,
                "threshold": threshold,
                "reason": reason
            }
        
        return None
