from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from core.database import get_db

router = APIRouter()

PERIOD_MAP = {
    "7d":  "7 days",
    "30d": "30 days",
    "90d": "90 days",
    "1y":  "365 days",
}


@router.get("/summary")
async def get_sales_summary(
    period: str = Query("30d"),
    db: AsyncSession = Depends(get_db),
):
    interval = PERIOD_MAP.get(period, "30 days")
    try:
        result = await db.execute(text(f"""
            SELECT
                ROUND(COALESCE(SUM(total_amount), 0)::numeric, 2) AS revenue,
                COUNT(*) AS orders,
                COALESCE(SUM(quantity), 0) AS units_sold,
                ROUND(COALESCE(AVG(total_amount), 0)::numeric, 2) AS avg_order_value,
                ROUND(COALESCE(SUM(discount * total_amount), 0)::numeric, 2) AS total_discounts
            FROM sales
            WHERE sale_date >= NOW() - INTERVAL '{interval}'
        """))
        row = result.fetchone()
        return {
            "revenue": float(row.revenue),
            "orders": row.orders,
            "units_sold": row.units_sold,
            "avg_order_value": float(row.avg_order_value),
            "total_discounts": float(row.total_discounts),
            "period": period,
        }
    except Exception as e:
        return {"error": str(e)}


@router.get("/by-category")
async def sales_by_category(
    period: str = Query("30d"),
    db: AsyncSession = Depends(get_db),
):
    interval = PERIOD_MAP.get(period, "30 days")
    try:
        result = await db.execute(text(f"""
            SELECT
                p.category,
                ROUND(SUM(s.total_amount)::numeric, 2) AS revenue,
                COUNT(s.id) AS orders,
                SUM(s.quantity) AS units
            FROM sales s
            JOIN products p ON s.product_id = p.id
            WHERE s.sale_date >= NOW() - INTERVAL '{interval}'
            GROUP BY p.category
            ORDER BY revenue DESC
        """))
        return [
            {
                "category": r.category,
                "revenue": float(r.revenue),
                "orders": r.orders,
                "units": r.units,
            }
            for r in result.fetchall()
        ]
    except Exception as e:
        return {"error": str(e)}


@router.get("/by-region")
async def sales_by_region(
    period: str = Query("30d"),
    db: AsyncSession = Depends(get_db),
):
    interval = PERIOD_MAP.get(period, "30 days")
    try:
        result = await db.execute(text(f"""
            SELECT
                region,
                ROUND(SUM(total_amount)::numeric, 2) AS revenue,
                COUNT(*) AS orders
            FROM sales
            WHERE sale_date >= NOW() - INTERVAL '{interval}'
            GROUP BY region
            ORDER BY revenue DESC
        """))
        return [
            {
                "region": r.region,
                "revenue": float(r.revenue),
                "orders": r.orders,
            }
            for r in result.fetchall()
        ]
    except Exception as e:
        return {"error": str(e)}


@router.get("/monthly-trend")
async def monthly_trend(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(text("""
            SELECT
                TO_CHAR(sale_date, 'YYYY-MM') AS month,
                ROUND(SUM(total_amount)::numeric, 2) AS revenue,
                COUNT(*) AS orders
            FROM sales
            WHERE sale_date >= NOW() - INTERVAL '365 days'
            GROUP BY TO_CHAR(sale_date, 'YYYY-MM')
            ORDER BY month ASC
        """))
        return [
            {
                "month": r.month,
                "revenue": float(r.revenue),
                "orders": r.orders,
            }
            for r in result.fetchall()
        ]
    except Exception as e:
        return {"error": str(e)}


@router.get("/top-products")
async def top_products(
    limit: int = Query(10),
    period: str = Query("30d"),
    db: AsyncSession = Depends(get_db),
):
    interval = PERIOD_MAP.get(period, "30 days")
    try:
        result = await db.execute(text(f"""
            SELECT
                p.name,
                p.category,
                p.sku,
                ROUND(SUM(s.total_amount)::numeric, 2) AS revenue,
                SUM(s.quantity) AS units
            FROM sales s
            JOIN products p ON s.product_id = p.id
            WHERE s.sale_date >= NOW() - INTERVAL '{interval}'
            GROUP BY p.id, p.name, p.category, p.sku
            ORDER BY revenue DESC
            LIMIT {limit}
        """))
        return [
            {
                "name": r.name,
                "category": r.category,
                "sku": r.sku,
                "revenue": float(r.revenue),
                "units": r.units,
            }
            for r in result.fetchall()
        ]
    except Exception as e:
        return {"error": str(e)}