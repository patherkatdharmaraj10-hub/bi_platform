"""
=============================================================================
PHASE 2 — Database Setup & Seed Data
Run this from: C:\bi-platform\backend
Command: python phase2_database.py
=============================================================================
"""
import asyncio
import os
import sys

# ── Make sure we can import from backend ──────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def setup_database():
    print("\n" + "="*60)
    print("  PHASE 2 — Setting Up Database")
    print("="*60)

    # Step 1 — Create all tables
    print("\n[1/4] Creating database tables...")
    try:
        from core.database import engine, Base
        from models.user import User
        from models.sales import Product, Sale
        from models.inventory import Inventory, InventoryTransaction
        from models.customer import Customer

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("  ✅ Tables created successfully!")
    except Exception as e:
        print(f"  ❌ Error creating tables: {e}")
        return False

    # Step 2 — Seed users
    print("\n[2/4] Creating users...")
    try:
        from sqlalchemy.ext.asyncio import AsyncSession
        from sqlalchemy.orm import sessionmaker
        from sqlalchemy import select
        from core.security import hash_password
        from models.user import UserRole

        Session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        async with Session() as db:
            # Check if admin exists
            result = await db.execute(select(User).where(User.email == "admin@bi.com"))
            if not result.scalar_one_or_none():
                users = [
                    User(email="admin@bi.com", full_name="Admin User",
                         hashed_password=hash_password("admin123"),
                         role=UserRole.admin, is_premium=True),
                    User(email="analyst@bi.com", full_name="Data Analyst",
                         hashed_password=hash_password("analyst123"),
                         role=UserRole.analyst),
                    User(email="viewer@bi.com", full_name="View Only",
                         hashed_password=hash_password("viewer123"),
                         role=UserRole.viewer),
                ]
                for u in users:
                    db.add(u)
                await db.commit()
                print("  ✅ Users created!")
                print("     admin@bi.com   / admin123")
                print("     analyst@bi.com / analyst123")
            else:
                print("  ✅ Users already exist, skipping...")
    except Exception as e:
        print(f"  ❌ Error creating users: {e}")
        return False

    # Step 3 — Seed products, customers, sales, inventory
    print("\n[3/4] Seeding business data (this takes 1-2 minutes)...")
    try:
        import random
        from datetime import datetime, timedelta
        from models.sales import Product, Sale
        from models.inventory import Inventory
        from models.customer import Customer

        Session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

        CATEGORIES = ["Electronics", "Clothing", "Food & Beverage",
                      "Home & Garden", "Sports", "Books", "Health & Beauty"]
        REGIONS    = ["Bagmati", "Gandaki", "Lumbini", "Koshi", "Madhesh"]
        CHANNELS   = ["online", "retail", "wholesale"]
        SEGMENTS   = ["enterprise", "smb", "individual"]
        PRODUCTS   = [
            ("Laptop Pro 15", "Electronics", 85000, 60000),
            ("Smartphone X", "Electronics", 45000, 30000),
            ("Wireless Headphones", "Electronics", 8500, 5000),
            ("Running Shoes", "Sports", 4500, 2500),
            ("Yoga Mat", "Sports", 1800, 900),
            ("Cotton T-Shirt", "Clothing", 1200, 600),
            ("Denim Jeans", "Clothing", 3500, 1800),
            ("Rice 5kg", "Food & Beverage", 800, 500),
            ("Cooking Oil 1L", "Food & Beverage", 350, 200),
            ("Garden Tools Set", "Home & Garden", 2500, 1400),
            ("Python Book", "Books", 1500, 800),
            ("Data Science Book", "Books", 1800, 1000),
            ("Face Cream", "Health & Beauty", 950, 500),
            ("Shampoo 400ml", "Health & Beauty", 450, 250),
            ("Office Chair", "Home & Garden", 12000, 7000),
            ("Standing Desk", "Home & Garden", 25000, 15000),
            ("Tablet 10inch", "Electronics", 35000, 22000),
            ("Smart Watch", "Electronics", 18000, 11000),
            ("Protein Powder", "Health & Beauty", 4500, 2500),
            ("Football", "Sports", 2200, 1200),
        ]

        async with Session() as db:
            # Check if products exist
            result = await db.execute(select(Product))
            existing = result.scalars().first()

            if not existing:
                print("  → Adding products...")
                products = []
                for i, (name, cat, price, cost) in enumerate(PRODUCTS):
                    p = Product(
                        name=name, category=cat,
                        sku=f"SKU-{i+1:05d}",
                        price=float(price), cost=float(cost),
                        description=f"High quality {name}"
                    )
                    db.add(p)
                    products.append(p)
                await db.flush()

                print("  → Adding customers (200)...")
                customers = []
                nepali_names = [
                    "Ram Sharma", "Sita Thapa", "Hari Poudel", "Gita Adhikari",
                    "Krishna Karki", "Maya Tamang", "Binod Rai", "Sunita Gurung",
                    "Prakash Shrestha", "Anita Magar", "Dipak Bista", "Rekha Pandey",
                    "Suresh Koirala", "Puja Basnet", "Nabin Limbu", "Sabita Chhetri",
                ]
                for i in range(200):
                    name = random.choice(nepali_names) + f" {i+1}"
                    c = Customer(
                        name=name,
                        email=f"customer{i+1}@example.com",
                        phone=f"98{random.randint(10000000, 99999999)}",
                        country="Nepal",
                        region=random.choice(REGIONS),
                        segment=random.choice(SEGMENTS),
                        lifetime_value=round(random.uniform(1000, 500000), 2),
                        churn_risk_score=round(random.uniform(0, 1), 3),
                        acquisition_channel=random.choice(
                            ["organic", "paid", "referral", "direct"]
                        ),
                    )
                    db.add(c)
                    customers.append(c)
                await db.flush()

                print("  → Adding 3000 sales records (2 years)...")
                start_date = datetime.now() - timedelta(days=730)
                for i in range(3000):
                    sale_date = start_date + timedelta(
                        days=random.randint(0, 730),
                        hours=random.randint(0, 23),
                        minutes=random.randint(0, 59)
                    )
                    product = random.choice(products)
                    qty = random.randint(1, 15)
                    discount = round(random.uniform(0, 0.20), 3)
                    total = round(product.price * qty * (1 - discount), 2)
                    sale = Sale(
                        product_id=product.id,
                        customer_id=random.choice(customers).id
                                    if random.random() > 0.3 else None,
                        quantity=qty,
                        unit_price=product.price,
                        total_amount=total,
                        discount=discount,
                        region=random.choice(REGIONS),
                        channel=random.choice(CHANNELS),
                        sale_date=sale_date,
                    )
                    db.add(sale)

                print("  → Adding inventory records...")
                warehouses = ["WH-Kathmandu", "WH-Pokhara", "WH-Biratnagar"]
                for product in products:
                    inv = Inventory(
                        product_id=product.id,
                        warehouse=random.choice(warehouses),
                        quantity_on_hand=random.randint(0, 500),
                        reorder_point=random.randint(10, 50),
                        reorder_quantity=random.randint(50, 200),
                    )
                    db.add(inv)

                await db.commit()
                print("  ✅ All business data seeded!")
            else:
                print("  ✅ Data already exists, skipping...")

    except Exception as e:
        print(f"  ❌ Error seeding data: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Step 4 — Verify
    print("\n[4/4] Verifying database...")
    try:
        from sqlalchemy import text
        async with Session() as db:
            r1 = await db.execute(text("SELECT COUNT(*) FROM users"))
            r2 = await db.execute(text("SELECT COUNT(*) FROM products"))
            r3 = await db.execute(text("SELECT COUNT(*) FROM sales"))
            r4 = await db.execute(text("SELECT COUNT(*) FROM customers"))
            r5 = await db.execute(text("SELECT COUNT(*) FROM inventory"))

            print(f"  Users:     {r1.scalar()}")
            print(f"  Products:  {r2.scalar()}")
            print(f"  Sales:     {r3.scalar()}")
            print(f"  Customers: {r4.scalar()}")
            print(f"  Inventory: {r5.scalar()}")
        print("  ✅ Database verified!")
    except Exception as e:
        print(f"  ❌ Verification error: {e}")
        return False

    print("\n" + "="*60)
    print("  ✅ PHASE 2 COMPLETE!")
    print("="*60)
    print("\n  Login credentials:")
    print("  admin@bi.com   / admin123   (full access)")
    print("  analyst@bi.com / analyst123 (analyst access)")
    print("\n  Next: Run Phase 3")
    print("  Command: uvicorn main:app --reload")
    print("="*60 + "\n")
    return True


if __name__ == "__main__":
    asyncio.run(setup_database())