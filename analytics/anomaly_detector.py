from typing import Dict, Any, Optional
from network.settings_manager import load_thresholds, DEFAULT_THRESHOLDS

class AnomalyDetector:
    def __init__(
        self,
        rtt_threshold: Optional[float] = None,
        loss_threshold: Optional[float] = None,
        jitter_threshold: Optional[float] = None,
        config_path: Optional[str] = None
    ):
        # Read saved thresholds from configuration storage if not explicitly provided
        saved = load_thresholds(config_path=config_path) if (
            config_path or rtt_threshold is None or loss_threshold is None or jitter_threshold is None
        ) else DEFAULT_THRESHOLDS

        self.rtt_threshold = float(rtt_threshold) if rtt_threshold is not None else float(saved.get("rtt_ms", 90.0))
        self.loss_threshold = float(loss_threshold) if loss_threshold is not None else float(saved.get("loss_pct", 5.0))
        self.jitter_threshold = float(jitter_threshold) if jitter_threshold is not None else float(saved.get("jitter_ms", 20.0))

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
