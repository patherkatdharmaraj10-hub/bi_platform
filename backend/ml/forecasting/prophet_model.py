"""
Facebook Prophet forecasting model.
Handles seasonal decomposition and holiday effects.
"""
import pandas as pd
import numpy as np
from prophet import Prophet
from typing import List, Dict


class ProphetForecaster:
    def __init__(self):
        self.model = None

    def _build_training_data(self, metric: str) -> pd.DataFrame:
        """Generate synthetic training data for demo purposes.
        In production, query this from the database.
        """
        np.random.seed(42)
        dates = pd.date_range(end=pd.Timestamp.today(), periods=365, freq="D")
        base = 10000 + np.cumsum(np.random.randn(365) * 200)
        seasonal = 2000 * np.sin(np.linspace(0, 4 * np.pi, 365))
        values = base + seasonal + np.random.randn(365) * 500
        return pd.DataFrame({"ds": dates, "y": np.maximum(values, 0)})

    async def predict(self, metric: str, periods: int) -> List[Dict]:
        df = self._build_training_data(metric)
        model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False,
            changepoint_prior_scale=0.05,
        )
        model.fit(df)
        future = model.make_future_dataframe(periods=periods)
        forecast = model.predict(future)

        result = forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].tail(periods)
        return [
            {
                "date": row.ds.strftime("%Y-%m-%d"),
                "predicted": round(float(row.yhat), 2),
                "lower": round(float(row.yhat_lower), 2),
                "upper": round(float(row.yhat_upper), 2),
            }
            for _, row in result.iterrows()
        ]
