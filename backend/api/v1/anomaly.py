from fastapi import APIRouter, Query
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

router = APIRouter()


def generate_metric_data(metric: str, days: int):
    np.random.seed(42)
    if metric == "revenue":
        base = 50000 + np.cumsum(np.random.randn(days) * 1000)
        data = base + np.random.randn(days) * 3000
    elif metric == "orders":
        base = 150 + np.cumsum(np.random.randn(days) * 3)
        data = base + np.random.randn(days) * 20
    else:
        data = 300 + np.cumsum(np.random.randn(days) * 8)
        data = np.clip(data, 50, 800)

    # Inject clear anomalies
    anomaly_positions = [
        int(days * 0.15),
        int(days * 0.35),
        int(days * 0.55),
        int(days * 0.78),
    ]
    for pos in anomaly_positions:
        if pos < days:
            factor = np.random.choice([0.2, 2.8, 0.15, 3.2])
            data[pos] = data[pos] * factor

    return np.maximum(data, 0)


@router.get("/detect/{metric}")
async def detect_anomalies(
    metric: str,
    lookback_days: int = Query(90, ge=30, le=365),
):
    try:
        data = generate_metric_data(metric, lookback_days)
        dates = pd.date_range(
            end=pd.Timestamp.today(),
            periods=lookback_days,
        )

        # Isolation Forest
        iso = IsolationForest(
            contamination=0.05,
            random_state=42,
            n_estimators=100,
        )
        iso_scores = iso.fit_predict(data.reshape(-1, 1))

        # Z-score
        mean = float(np.mean(data))
        std = float(np.std(data))
        z_scores = np.abs((data - mean) / std) if std > 0 else np.zeros(lookback_days)

        # Build full series for chart
        full_series = []
        anomalies = []

        for i in range(lookback_days):
            is_iso = bool(iso_scores[i] == -1)
            is_z = bool(z_scores[i] > 2.5)
            is_anomaly = is_iso or is_z

            severity = "normal"
            if z_scores[i] > 3.5:
                severity = "high"
            elif z_scores[i] > 2.5:
                severity = "medium"
            elif is_iso:
                severity = "low"

            point = {
                "date": dates[i].strftime("%Y-%m-%d"),
                "value": round(float(data[i]), 2),
                "is_anomaly": is_anomaly,
                "severity": severity,
                "z_score": round(float(z_scores[i]), 3),
                "isolation_forest": is_iso,
            }

            full_series.append(point)
            if is_anomaly:
                anomalies.append(point)

        return {
            "metric": metric,
            "lookback_days": lookback_days,
            "anomaly_count": len(anomalies),
            "anomalies": anomalies,
            "full_series": full_series,
            "stats": {
                "mean": round(mean, 2),
                "std": round(std, 2),
                "min": round(float(np.min(data)), 2),
                "max": round(float(np.max(data)), 2),
            },
        }
    except Exception as e:
        return {"error": str(e)}


@router.get("/summary")
async def anomaly_summary():
    results = {}
    for metric in ["revenue", "orders", "inventory"]:
        data = generate_metric_data(metric, 30)
        iso = IsolationForest(contamination=0.05, random_state=42)
        scores = iso.fit_predict(data.reshape(-1, 1))
        results[metric] = int(np.sum(scores == -1))
    return {"anomalies_last_30_days": results}