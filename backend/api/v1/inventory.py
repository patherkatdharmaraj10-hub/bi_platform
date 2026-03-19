from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from core.database import get_db

router = APIRouter()


@router.get("/status")
async def inventory_status(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(text("""
            SELECT
                p.name, p.sku, p.category,
                i.quantity_on_hand,
                i.reorder_point,
                i.reorder_quantity,
                i.warehouse,
                CASE
                    WHEN i.quantity_on_hand <= 0 THEN 'out_of_stock'
                    WHEN i.quantity_on_hand <= i.reorder_point THEN 'low_stock'
                    ELSE 'in_stock'
                END AS status
            FROM inventory i
            JOIN products p ON i.product_id = p.id
            ORDER BY i.quantity_on_hand ASC
        """))
        return [dict(r._mapping) for r in result.fetchall()]
    except Exception as e:
        return {"error": str(e)}


@router.get("/alerts")
async def inventory_alerts(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(text("""
            SELECT
                p.name, p.sku,
                i.quantity_on_hand,
                i.reorder_point,
                i.warehouse
            FROM inventory i
            JOIN products p ON i.product_id = p.id
            WHERE i.quantity_on_hand <= i.reorder_point
            ORDER BY i.quantity_on_hand ASC
        """))
        rows = result.fetchall()
        return {
            "count": len(rows),
            "alerts": [dict(r._mapping) for r in rows],
        }
    except Exception as e:
        return {"error": str(e)}


@router.get("/summary")
async def inventory_summary(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(text("""
            SELECT
                COUNT(*) AS total_products,
                SUM(CASE WHEN quantity_on_hand <= 0 THEN 1 ELSE 0 END) AS out_of_stock,
                SUM(CASE WHEN quantity_on_hand > 0
                    AND quantity_on_hand <= reorder_point THEN 1 ELSE 0 END) AS low_stock,
                SUM(CASE WHEN quantity_on_hand > reorder_point THEN 1 ELSE 0 END) AS in_stock,
                SUM(quantity_on_hand) AS total_units
            FROM inventory
        """))
        row = result.fetchone()
        return dict(row._mapping)
    except Exception as e:
        return {"error": str(e)}