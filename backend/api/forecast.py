from datetime import datetime, timezone
from pathlib import Path
import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
import numpy as np
import pandas as pd
import joblib
import xgboost as xgb
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from core.database import get_db

router = APIRouter()

MODEL_SAVE_DIR = Path(__file__).resolve().parents[2] / "ml" / "models" / "saved"
MODEL_FILE = MODEL_SAVE_DIR / "xgboost_sales_units_global.pkl"
DEFAULT_PERIODS = 30
MODEL_NAME = "xgboost"
METRIC = "sales_units_by_product"
FEATURES = [
    "product_id",
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


async def _ensure_forecast_table(db: AsyncSession) -> None:
    await db.execute(text("""
        CREATE TABLE IF NOT EXISTS monthly_sales_forecasts (
            id SERIAL PRIMARY KEY,
            forecast_month DATE NOT NULL UNIQUE,
            metric VARCHAR(50) NOT NULL,
            model_name VARCHAR(50) NOT NULL,
            periods INTEGER NOT NULL,
            generated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            predictions JSONB NOT NULL,
            summary JSONB NOT NULL,
            metrics JSONB,
            trained_rows INTEGER NOT NULL DEFAULT 0
        )
    """))


def _next_month_start() -> datetime.date:
    now = datetime.now(timezone.utc).date()
    if now.month == 12:
        return now.replace(year=now.year + 1, month=1, day=1)
    return now.replace(month=now.month + 1, day=1)


def _next_month_dates(start_date: datetime.date) -> pd.DatetimeIndex:
    return pd.date_range(start=pd.Timestamp(start_date), periods=DEFAULT_PERIODS, freq="D")


async def _sales_history_from_db(db: AsyncSession) -> pd.DataFrame:
    rows = (await db.execute(text("""
        SELECT
            p.id AS product_id,
            p.name AS product_name,
            DATE(s.sale_date) AS ds,
            COALESCE(SUM(s.quantity), 0)::float AS y
        FROM sales s
        JOIN products p ON p.id = s.product_id
        GROUP BY p.id, p.name, DATE(s.sale_date)
        ORDER BY p.id ASC, ds ASC
    """))).fetchall()

    if not rows:
        return pd.DataFrame(columns=["product_id", "product_name", "ds", "y"])

    df = pd.DataFrame([
        {
            "product_id": int(r.product_id),
            "product_name": r.product_name,
            "ds": r.ds,
            "y": float(r.y or 0),
        }
        for r in rows
    ])
    df["ds"] = pd.to_datetime(df["ds"])
    return df


def _feature_frame(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy().sort_values(["product_id", "ds"]).reset_index(drop=True)
    d["dow"] = d["ds"].dt.dayofweek
    d["month"] = d["ds"].dt.month
    d["quarter"] = d["ds"].dt.quarter
    d["doy"] = d["ds"].dt.dayofyear
    d["year"] = d["ds"].dt.year

    grouped = d.groupby("product_id", group_keys=False)
    d["lag_1"] = grouped["y"].shift(1)
    d["lag_7"] = grouped["y"].shift(7)
    d["lag_14"] = grouped["y"].shift(14)
    d["lag_30"] = grouped["y"].shift(30)
    d["roll_7"] = grouped["y"].shift(1).rolling(7).mean().reset_index(level=0, drop=True)
    d["roll_30"] = grouped["y"].shift(1).rolling(30).mean().reset_index(level=0, drop=True)
    d = d.dropna().reset_index(drop=True)
    return d


def _train_global_model(train_frame: pd.DataFrame) -> xgb.XGBRegressor:
    model = xgb.XGBRegressor(
        n_estimators=280,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.9,
        colsample_bytree=0.9,
        random_state=42,
    )
    model.fit(train_frame[FEATURES], train_frame["y"])
    MODEL_SAVE_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_FILE)
    return model


def _evaluate_model(model: xgb.XGBRegressor, test_frame: pd.DataFrame) -> dict:
    if test_frame.empty:
        return {"mae": 0.0, "rmse": 0.0, "r2": 0.0}

    pred = model.predict(test_frame[FEATURES])
    mae = float(mean_absolute_error(test_frame["y"], pred))
    rmse = float(np.sqrt(mean_squared_error(test_frame["y"], pred)))
    r2 = float(r2_score(test_frame["y"], pred))
    return {
        "mae": round(mae, 2),
        "rmse": round(rmse, 2),
        "r2": round(r2, 4),
    }


def _predict_next_month_units_by_product(
    model: xgb.XGBRegressor,
    raw_df: pd.DataFrame,
    forecast_start: datetime.date,
) -> list[dict]:
    future_days = _next_month_dates(forecast_start)

    products = (
        raw_df[["product_id", "product_name"]]
        .drop_duplicates()
        .sort_values("product_id")
    )

    histories = {}
    for pid, group in raw_df.groupby("product_id"):
        ordered = group.sort_values("ds")
        histories[int(pid)] = [float(v) for v in ordered["y"].tolist()]

    agg = {}
    for _, row in products.iterrows():
        pid = int(row["product_id"])
        agg[pid] = {
            "product_id": pid,
            "product_name": str(row["product_name"]),
            "predicted_units": 0.0,
        }

    for day in future_days:
        for pid, info in agg.items():
            hist = histories.get(pid, [])
            if len(hist) == 0:
                continue

            lag1 = hist[-1]
            lag7 = hist[-7] if len(hist) >= 7 else hist[-1]
            lag14 = hist[-14] if len(hist) >= 14 else hist[-1]
            lag30 = hist[-30] if len(hist) >= 30 else hist[-1]
            roll7 = float(np.mean(hist[-7:])) if len(hist) >= 7 else float(np.mean(hist))
            roll30 = float(np.mean(hist[-30:])) if len(hist) >= 30 else float(np.mean(hist))

            row = pd.DataFrame([
                {
                    "product_id": pid,
                    "dow": day.dayofweek,
                    "month": day.month,
                    "quarter": ((day.month - 1) // 3) + 1,
                    "doy": day.dayofyear,
                    "year": day.year,
                    "lag_1": lag1,
                    "lag_7": lag7,
                    "lag_14": lag14,
                    "lag_30": lag30,
                    "roll_7": roll7,
                    "roll_30": roll30,
                }
            ])

            pred = float(model.predict(row)[0])
            pred = max(pred, 0.0)
            info["predicted_units"] += pred
            hist.append(pred)
            histories[pid] = hist

    out = []
    for _, item in agg.items():
        total = float(item["predicted_units"])
        out.append({
            "product_id": item["product_id"],
            "product_name": item["product_name"],
            "predicted_units": round(total, 2),
            "lower_units": round(max(total * 0.88, 0.0), 2),
            "upper_units": round(total * 1.12, 2),
        })

    out.sort(key=lambda x: float(x["predicted_units"]), reverse=True)
    for i, item in enumerate(out, start=1):
        item["rank"] = i
    return out


def _build_summary(predictions: list[dict]) -> dict:
    if not predictions:
        return {
            "total_predicted_units": 0,
            "product_count": 0,
            "top_product": "-",
            "top_predicted_units": 0,
        }

    vals = [float(p["predicted_units"]) for p in predictions]
    top = max(predictions, key=lambda p: float(p["predicted_units"]))
    return {
        "total_predicted_units": round(float(np.sum(vals)), 2),
        "product_count": len(predictions),
        "top_product": top.get("product_name", "-"),
        "top_predicted_units": round(float(top.get("predicted_units", 0)), 2),
    }


async def _generate_sales_forecast(db: AsyncSession, periods: int = DEFAULT_PERIODS) -> dict:
    df = await _sales_history_from_db(db)
    if len(df) < 45:
        raise HTTPException(
            status_code=400,
            detail="Not enough sales history to train forecast. Add more sales records first.",
        )

    frame = _feature_frame(df)
    if len(frame) < 100:
        raise HTTPException(
            status_code=400,
            detail="Not enough product-level history to generate monthly forecast.",
        )

    split_idx = int(len(frame) * 0.8)
    train_frame = frame.iloc[:split_idx].copy()
    test_frame = frame.iloc[split_idx:].copy()

    model = _train_global_model(train_frame)
    metrics = _evaluate_model(model, test_frame)
    forecast_month = _next_month_start()
    predictions = _predict_next_month_units_by_product(model, df, forecast_month)

    if not predictions:
        raise HTTPException(
            status_code=400,
            detail="Not enough product-level history to generate monthly forecast.",
        )

    summary = _build_summary(predictions)

    return {
        "metric": METRIC,
        "model": MODEL_NAME,
        "periods": periods,
        "predictions": predictions,
        "summary": summary,
        "metrics": metrics,
        "trained_rows": int(len(train_frame)),
        "model_file": str(MODEL_FILE),
    }


async def _ensure_monthly_snapshot(db: AsyncSession) -> dict:
    await _ensure_forecast_table(db)
    forecast_month = _next_month_start()

    existing = (await db.execute(text("""
        SELECT forecast_month, metric, model_name, periods, generated_at,
               predictions, summary, metrics, trained_rows
        FROM monthly_sales_forecasts
        WHERE forecast_month = :forecast_month
        LIMIT 1
    """), {"forecast_month": forecast_month})).fetchone()

    if existing:
        return {
            "forecast_month": str(existing.forecast_month),
            "metric": existing.metric,
            "model": existing.model_name,
            "periods": int(existing.periods),
            "generated_at": existing.generated_at.isoformat() if existing.generated_at else None,
            "predictions": existing.predictions or [],
            "summary": existing.summary or {},
            "metrics": existing.metrics or {},
            "trained_rows": int(existing.trained_rows or 0),
            "source": "database",
        }

    generated = await _generate_sales_forecast(db, DEFAULT_PERIODS)

    await db.execute(text("""
        INSERT INTO monthly_sales_forecasts (
            forecast_month, metric, model_name, periods,
            predictions, summary, metrics, trained_rows
        ) VALUES (
            :forecast_month, :metric, :model_name, :periods,
            CAST(:predictions AS JSONB), CAST(:summary AS JSONB),
            CAST(:metrics AS JSONB), :trained_rows
        )
        ON CONFLICT (forecast_month)
        DO UPDATE SET
            predictions = EXCLUDED.predictions,
            summary = EXCLUDED.summary,
            metrics = EXCLUDED.metrics,
            trained_rows = EXCLUDED.trained_rows,
            generated_at = NOW()
    """), {
        "forecast_month": forecast_month,
        "metric": generated["metric"],
        "model_name": generated["model"],
        "periods": generated["periods"],
        "predictions": json.dumps(generated["predictions"]),
        "summary": json.dumps(generated["summary"]),
        "metrics": json.dumps(generated["metrics"]),
        "trained_rows": generated["trained_rows"],
    })

    return {
        "forecast_month": str(forecast_month),
        "metric": generated["metric"],
        "model": generated["model"],
        "periods": generated["periods"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "predictions": generated["predictions"],
        "summary": generated["summary"],
        "metrics": generated["metrics"],
        "trained_rows": generated["trained_rows"],
        "source": "generated",
    }


@router.get("/latest")
async def latest_sales_forecast(db: AsyncSession = Depends(get_db)):
    return await _ensure_monthly_snapshot(db)


