from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from core.database import get_db

router = APIRouter()


@router.get("/summary")
async def customer_summary(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(text("""
            SELECT
                COUNT(*) AS total,
                COUNT(CASE WHEN is_active = true THEN 1 END) AS active,
                ROUND(AVG(lifetime_value)::numeric, 2) AS avg_ltv,
                ROUND(SUM(lifetime_value)::numeric, 2) AS total_ltv
            FROM customers
        """))
        row = result.fetchone()
        return dict(row._mapping)
    except Exception as e:
        return {"error": str(e)}


@router.get("/segments")
async def customer_segments(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(text("""
            SELECT
                segment,
                COUNT(*) AS count,
                ROUND(AVG(lifetime_value)::numeric, 2) AS avg_ltv,
                ROUND(SUM(lifetime_value)::numeric, 2) AS total_ltv
            FROM customers
            GROUP BY segment
            ORDER BY total_ltv DESC
        """))
        return [dict(r._mapping) for r in result.fetchall()]
    except Exception as e:
        return {"error": str(e)}


@router.get("/by-region")
async def customers_by_region(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(text("""
            SELECT
                region,
                COUNT(*) AS count,
                ROUND(AVG(lifetime_value)::numeric, 2) AS avg_ltv
            FROM customers
            GROUP BY region
            ORDER BY count DESC
        """))
        return [dict(r._mapping) for r in result.fetchall()]
    except Exception as e:
        return {"error": str(e)}


@router.get("/churn-risk")
async def churn_risk(
    threshold: float = Query(0.6),
    db: AsyncSession = Depends(get_db),
):
    try:
        result = await db.execute(text(f"""
            SELECT
                name,
                email,
                phone,
                segment,
                ROUND(churn_risk_score::numeric, 3) AS churn_risk_score,
                ROUND(lifetime_value::numeric, 2) AS lifetime_value,
                region
            FROM customers
            WHERE churn_risk_score >= {threshold}
            ORDER BY churn_risk_score DESC
            LIMIT 50
        """))
        return [dict(r._mapping) for r in result.fetchall()]
    except Exception as e:
        return {"error": str(e)}


@router.get("/acquisition")
async def acquisition_channels(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(text("""
            SELECT
                acquisition_channel,
                COUNT(*) AS customers,
                ROUND(AVG(lifetime_value)::numeric, 2) AS avg_ltv
            FROM customers
            GROUP BY acquisition_channel
            ORDER BY customers DESC
        """))
        return [dict(r._mapping) for r in result.fetchall()]
    except Exception as e:
        return {"error": str(e)}