import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


class XGBoostForecaster:
    FEATURES = [
        "dow",
        "month",
        "quarter",
        "doy",
        "year",
        "lag_1",
        "lag_7",
        "lag_14",
        "lag_30",
        "roll_7",
        "roll_30",
    ]

    def __init__(self) -> None:
        self.model = xgb.XGBRegressor(
            n_estimators=250,
            max_depth=5,
            learning_rate=0.05,
            subsample=0.9,
            colsample_bytree=0.9,
            random_state=42,
        )
        self.trained = False

    @staticmethod
    def _feature_frame(df: pd.DataFrame) -> pd.DataFrame:
        d = df.copy()
        d["dow"] = d["ds"].dt.dayofweek
        d["month"] = d["ds"].dt.month
        d["quarter"] = d["ds"].dt.quarter
        d["doy"] = d["ds"].dt.dayofyear
        d["year"] = d["ds"].dt.year

        for lag in [1, 7, 14, 30]:
            d[f"lag_{lag}"] = d["y"].shift(lag)

        d["roll_7"] = d["y"].shift(1).rolling(7).mean()
        d["roll_30"] = d["y"].shift(1).rolling(30).mean()

        return d.dropna().reset_index(drop=True)

    def train(self, df: pd.DataFrame) -> None:
        feat = self._feature_frame(df)
        x_train = feat[self.FEATURES]
        y_train = feat["y"]
        self.model.fit(x_train, y_train)
        self.trained = True

    def evaluate(self, df: pd.DataFrame) -> dict:
        feat = self._feature_frame(df)
        if len(feat) < 120:
            return {"mae": 0.0, "rmse": 0.0, "r2": 0.0}

        split_idx = int(len(feat) * 0.8)
        train = feat.iloc[:split_idx]
        test = feat.iloc[split_idx:]

        model = xgb.XGBRegressor(
            n_estimators=250,
            max_depth=5,
            learning_rate=0.05,
            subsample=0.9,
            colsample_bytree=0.9,
            random_state=42,
        )
        model.fit(train[self.FEATURES], train["y"])
        pred = model.predict(test[self.FEATURES])

        mae = float(mean_absolute_error(test["y"], pred))
        rmse = float(np.sqrt(mean_squared_error(test["y"], pred)))
        r2 = float(r2_score(test["y"], pred))
        return {
            "mae": round(mae, 2),
            "rmse": round(rmse, 2),
            "r2": round(r2, 4),
        }

    def forecast(self, df: pd.DataFrame, periods: int) -> list[dict]:
        if not self.trained:
            self.train(df)

        last_values = list(df["y"].values[-30:])
        start = pd.Timestamp.today().normalize() + pd.Timedelta(days=1)
        future_dates = pd.date_range(start=start, periods=periods, freq="D")

        out = []
        for day in future_dates:
            row = {
                "dow": day.dayofweek,
                "month": day.month,
                "quarter": day.quarter,
                "doy": day.dayofyear,
                "year": day.year,
                "lag_1": last_values[-1],
                "lag_7": last_values[-7],
                "lag_14": last_values[-14],
                "lag_30": last_values[-30],
                "roll_7": float(np.mean(last_values[-7:])),
                "roll_30": float(np.mean(last_values[-30:])),
            }
            pred = float(self.model.predict(pd.DataFrame([row]))[0])
            pred = max(pred, 0.0)
            last_values.append(pred)

            spread = float(np.std(last_values[-30:]) * 0.15)
            out.append({
                "date": day.strftime("%Y-%m-%d"),
                "predicted": round(pred, 2),
                "lower": round(max(pred - spread, 0.0), 2),
                "upper": round(pred + spread, 2),
            })

        return out
