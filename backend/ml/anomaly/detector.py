"""
Anomaly Detection using Isolation Forest + Z-Score.
"""
import numpy as np
from sklearn.ensemble import IsolationForest
from typing import List, Dict


class AnomalyDetector:
    def __init__(self, contamination: float = 0.05):
        self.model = IsolationForest(
            contamination=contamination, random_state=42, n_estimators=100
        )

    async def detect(self, metric: str, lookback_days: int = 30) -> List[Dict]:
        """Detect anomalies in the given metric."""
        import pandas as pd

        # Generate synthetic data for demo
        np.random.seed(42)
        n = lookback_days
        base = 10000 + np.cumsum(np.random.randn(n) * 200)
        data = base + np.random.randn(n) * 400

        # Inject artificial anomalies for demo
        anomaly_idx = [int(n * 0.3), int(n * 0.6), int(n * 0.85)]
        for idx in anomaly_idx:
            data[idx] *= np.random.choice([0.3, 2.5])  # spike or drop

        # Fit and predict
        scores = self.model.fit_predict(data.reshape(-1, 1))
        z_scores = np.abs((data - np.mean(data)) / np.std(data))

        dates = pd.date_range(end=pd.Timestamp.today(), periods=n)
        return [
            {
                "date": dates[i].strftime("%Y-%m-%d"),
                "value": round(float(data[i]), 2),
                "is_anomaly": bool(scores[i] == -1 or z_scores[i] > 2.5),
                "severity": "high" if z_scores[i] > 3.5 else "medium" if z_scores[i] > 2.5 else "low",
                "z_score": round(float(z_scores[i]), 3),
            }
            for i in range(n)
            if scores[i] == -1 or z_scores[i] > 2.5
        ]
