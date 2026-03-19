"""
LSTM (Long Short-Term Memory) forecasting model.
Best for complex temporal dependencies.
"""
import numpy as np
import pandas as pd
from typing import List, Dict


class LSTMForecaster:
    def __init__(self, lookback: int = 60):
        self.lookback = lookback
        self.model = None

    def _create_sequences(self, data: np.ndarray):
        X, y = [], []
        for i in range(self.lookback, len(data)):
            X.append(data[i - self.lookback : i])
            y.append(data[i])
        return np.array(X), np.array(y)

    def _build_model(self, input_shape):
        try:
            from tensorflow.keras.models import Sequential
            from tensorflow.keras.layers import LSTM, Dense, Dropout
        except ImportError:
            raise ImportError("TensorFlow required for LSTM forecasting.")

        model = Sequential([
            LSTM(50, return_sequences=True, input_shape=input_shape),
            Dropout(0.2),
            LSTM(50, return_sequences=False),
            Dropout(0.2),
            Dense(25),
            Dense(1),
        ])
        model.compile(optimizer="adam", loss="mean_squared_error")
        return model

    async def predict(self, metric: str, periods: int) -> List[Dict]:
        # Generate synthetic data for demo
        np.random.seed(42)
        base = 10000 + np.cumsum(np.random.randn(400) * 150)
        data = base + np.random.randn(400) * 300

        # Normalize
        from sklearn.preprocessing import MinMaxScaler
        scaler = MinMaxScaler()
        scaled = scaler.fit_transform(data.reshape(-1, 1))

        X, y = self._create_sequences(scaled)
        X = X.reshape((X.shape[0], X.shape[1], 1))

        model = self._build_model((self.lookback, 1))
        model.fit(X, y, epochs=10, batch_size=32, verbose=0)

        # Forecast
        last_seq = scaled[-self.lookback:]
        predictions = []
        for _ in range(periods):
            seq = last_seq[-self.lookback:].reshape(1, self.lookback, 1)
            pred = model.predict(seq, verbose=0)[0][0]
            predictions.append(pred)
            last_seq = np.append(last_seq, [[pred]], axis=0)

        predictions_inv = scaler.inverse_transform(
            np.array(predictions).reshape(-1, 1)
        ).flatten()

        future_dates = pd.date_range(
            start=pd.Timestamp.today() + pd.Timedelta(days=1), periods=periods
        )
        return [
            {
                "date": d.strftime("%Y-%m-%d"),
                "predicted": round(float(v), 2),
                "lower": round(float(v * 0.92), 2),
                "upper": round(float(v * 1.08), 2),
            }
            for d, v in zip(future_dates, predictions_inv)
        ]
