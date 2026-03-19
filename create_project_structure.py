"""
=============================================================================
AI-Powered Business Intelligence Platform
Project Scaffold Generator
Run: python create_project_structure.py
=============================================================================
"""

import os
import json

PROJECT_NAME = "bi-platform"

STRUCTURE = {
    # ── Root config files ──────────────────────────────────────────────────
    ".env.example": """# ── Application ──────────────────────────────────────────────────────────
APP_NAME=BI Platform
APP_ENV=development
SECRET_KEY=your-super-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=60

# ── Database ──────────────────────────────────────────────────────────────
DATABASE_URL=postgresql://biuser:bipassword@localhost:5432/biplatform
REDIS_URL=redis://localhost:6379/0

# ── AI / ML ───────────────────────────────────────────────────────────────
OPENAI_API_KEY=sk-your-openai-api-key-here
HUGGINGFACE_API_KEY=hf-your-huggingface-key-here

# ── Frontend ──────────────────────────────────────────────────────────────
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000
""",
    ".gitignore": """# Python
__pycache__/
*.py[cod]
*.egg
.eggs/
*.egg-info/
dist/
build/
.venv/
venv/
env/
.env

# Node / React
node_modules/
/frontend/build/
/frontend/.env
npm-debug.log*
yarn-debug.log*

# ML models
backend/ml/models/saved/*.pkl
backend/ml/models/saved/*.h5
backend/ml/models/saved/*.json
!backend/ml/models/saved/.gitkeep

# IDE
.vscode/
.idea/
*.swp

# Docker volumes
postgres_data/
redis_data/

# Jupyter checkpoints
.ipynb_checkpoints/
""",
    "README.md": """# AI-Powered Business Intelligence Platform

> A production-grade SaaS BI platform with predictive analytics, anomaly detection,
> and an AI chatbot — built for sales, inventory & customer intelligence.

## Tech Stack
| Layer | Technology |
|-------|-----------|
| Frontend | React.js, Recharts, Ant Design |
| Backend | FastAPI (Python 3.11) |
| Database | PostgreSQL 15, Redis |
| ML/Forecasting | XGBoost, LSTM, Prophet, Scikit-learn |
| NLP/Chatbot | OpenAI GPT-4, HuggingFace Transformers |
| Infrastructure | Docker, Nginx, GitHub Actions |

## Quick Start
```bash
# 1. Clone & enter
git clone <your-repo>
cd bi-platform

# 2. Start all services
docker-compose up -d

# 3. Run DB migrations
cd backend && alembic upgrade head

# 4. Seed sample data
python scripts/seed_data.py

# 5. Start frontend dev server
cd frontend && npm install && npm start
```

Visit http://localhost:3000 — login: admin@bi.com / admin123

## Project Phases
- Phase 1: Foundation & Authentication
- Phase 2: Database Schema & REST APIs  
- Phase 3: Dashboard & Data Visualization
- Phase 4: ML Forecasting (Prophet + LSTM)
- Phase 5: Anomaly Detection
- Phase 6: AI Chatbot (GPT-4 + NLQ)
- Phase 7: Premium Features & Billing
- Phase 8: Deployment & CI/CD
""",
    "docker-compose.yml": """version: '3.9'

services:
  # ── PostgreSQL ─────────────────────────────────────────────────────────
  db:
    image: postgres:15-alpine
    container_name: bi_postgres
    restart: unless-stopped
    environment:
      POSTGRES_DB: biplatform
      POSTGRES_USER: biuser
      POSTGRES_PASSWORD: bipassword
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backend/db/init.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U biuser -d biplatform"]
      interval: 10s
      timeout: 5s
      retries: 5

  # ── Redis ─────────────────────────────────────────────────────────────
  redis:
    image: redis:7-alpine
    container_name: bi_redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  # ── FastAPI Backend ────────────────────────────────────────────────────
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: bi_backend
    restart: unless-stopped
    env_file: .env
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
      - ./backend/ml/models/saved:/app/ml/models/saved
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

  # ── React Frontend ─────────────────────────────────────────────────────
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: bi_frontend
    restart: unless-stopped
    ports:
      - "3000:3000"
    volumes:
      - ./frontend/src:/app/src
    environment:
      - REACT_APP_API_URL=http://localhost:8000
      - REACT_APP_WS_URL=ws://localhost:8000
    depends_on:
      - backend

  # ── Nginx Reverse Proxy ────────────────────────────────────────────────
  nginx:
    image: nginx:alpine
    container_name: bi_nginx
    restart: unless-stopped
    ports:
      - "80:80"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - backend
      - frontend

volumes:
  postgres_data:
  redis_data:
""",
    # ── Backend ────────────────────────────────────────────────────────────
    "backend/Dockerfile": """FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \\
    build-essential libpq-dev gcc && \\
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
""",
    "backend/requirements.txt": """# ── Web Framework ─────────────────────────────────────────────────────
fastapi==0.111.0
uvicorn[standard]==0.30.1
websockets==12.0
python-multipart==0.0.9

# ── Database ──────────────────────────────────────────────────────────
sqlalchemy==2.0.30
asyncpg==0.29.0
alembic==1.13.1
psycopg2-binary==2.9.9
redis==5.0.4

# ── Auth & Security ────────────────────────────────────────────────────
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.1

# ── Data & ML ─────────────────────────────────────────────────────────
pandas==2.2.2
numpy==1.26.4
scikit-learn==1.5.0
xgboost==2.0.3
prophet==1.1.5
tensorflow==2.16.1
torch==2.3.0
transformers==4.41.1

# ── AI / NLP ──────────────────────────────────────────────────────────
openai==1.30.1
langchain==0.2.3
langchain-openai==0.1.8
sentence-transformers==3.0.0

# ── Task Queue ────────────────────────────────────────────────────────
celery==5.4.0
flower==2.0.1

# ── Utilities ─────────────────────────────────────────────────────────
pydantic==2.7.1
pydantic-settings==2.2.1
httpx==0.27.0
aiofiles==23.2.1
python-dateutil==2.9.0
pytz==2024.1
""",
    "backend/main.py": """\"\"\"
BI Platform — FastAPI Entry Point
\"\"\"
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager

from core.config import settings
from core.database import engine, Base
from api.v1 import auth, sales, inventory, customers, forecast, anomaly, chatbot, dashboard


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables if not exists
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown
    await engine.dispose()


app = FastAPI(
    title="AI-Powered BI Platform",
    description="Business Intelligence with ML forecasting and AI chatbot",
    version="1.0.0",
    lifespan=lifespan,
)

# ── Middleware ────────────────────────────────────────────────────────────
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ────────────────────────────────────────────────────────────────
app.include_router(auth.router,       prefix="/api/v1/auth",      tags=["Auth"])
app.include_router(dashboard.router,  prefix="/api/v1/dashboard", tags=["Dashboard"])
app.include_router(sales.router,      prefix="/api/v1/sales",     tags=["Sales"])
app.include_router(inventory.router,  prefix="/api/v1/inventory", tags=["Inventory"])
app.include_router(customers.router,  prefix="/api/v1/customers", tags=["Customers"])
app.include_router(forecast.router,   prefix="/api/v1/forecast",  tags=["Forecast"])
app.include_router(anomaly.router,    prefix="/api/v1/anomaly",   tags=["Anomaly"])
app.include_router(chatbot.router,    prefix="/api/v1/chatbot",   tags=["Chatbot"])


@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}
""",
    "backend/core/__init__.py": "",
    "backend/core/config.py": """from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    APP_NAME: str = "BI Platform"
    APP_ENV: str = "development"
    SECRET_KEY: str = "change-this-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ALGORITHM: str = "HS256"

    DATABASE_URL: str = "postgresql+asyncpg://biuser:bipassword@localhost:5432/biplatform"
    REDIS_URL: str = "redis://localhost:6379/0"

    OPENAI_API_KEY: str = ""
    HUGGINGFACE_API_KEY: str = ""

    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:80",
    ]

    class Config:
        env_file = ".env"


settings = Settings()
""",
    "backend/core/database.py": """from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from core.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.APP_ENV == "development",
    pool_size=10,
    max_overflow=20,
)

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
""",
    "backend/core/security.py": """from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None
""",
    # ── DB Models ───────────────────────────────────────────────────────────
    "backend/models/__init__.py": "",
    "backend/models/user.py": """from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.sql import func
import enum
from core.database import Base


class UserRole(str, enum.Enum):
    admin = "admin"
    analyst = "analyst"
    viewer = "viewer"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.viewer)
    is_active = Column(Boolean, default=True)
    is_premium = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
""",
    "backend/models/sales.py": """from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from core.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    category = Column(String(100), nullable=False)
    sku = Column(String(50), unique=True, nullable=False)
    price = Column(Float, nullable=False)
    cost = Column(Float, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    discount = Column(Float, default=0.0)
    region = Column(String(100))
    channel = Column(String(50))  # online, retail, wholesale
    sale_date = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
""",
    "backend/models/inventory.py": """from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from core.database import Base


class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    warehouse = Column(String(100), nullable=False)
    quantity_on_hand = Column(Integer, default=0)
    reorder_point = Column(Integer, default=50)
    reorder_quantity = Column(Integer, default=200)
    last_restocked = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class InventoryTransaction(Base):
    __tablename__ = "inventory_transactions"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    transaction_type = Column(String(20))  # in, out, adjustment
    quantity = Column(Integer, nullable=False)
    reference = Column(String(100))
    transaction_date = Column(DateTime(timezone=True), server_default=func.now())
""",
    "backend/models/customer.py": """from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean, Text
from sqlalchemy.sql import func
from core.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    email = Column(String(200), unique=True)
    phone = Column(String(50))
    country = Column(String(100))
    region = Column(String(100))
    segment = Column(String(50))  # enterprise, smb, individual
    lifetime_value = Column(Float, default=0.0)
    churn_risk_score = Column(Float, default=0.0)
    acquisition_channel = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
""",
    # ── API Routes ─────────────────────────────────────────────────────────
    "backend/api/__init__.py": "",
    "backend/api/v1/__init__.py": "",
    "backend/api/v1/auth.py": """from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr
from core.database import get_db
from core.security import hash_password, verify_password, create_access_token
from models.user import User, UserRole

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: str
    role: UserRole = UserRole.viewer


class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    role: str


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hash_password(user_data.password),
        role=user_data.role,
    )
    db.add(user)
    await db.flush()
    return {"id": user.id, "email": user.email, "message": "User created successfully"}


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    token = create_access_token({"sub": str(user.id)})
    return Token(access_token=token, token_type="bearer", user_id=user.id, role=user.role)
""",
    "backend/api/v1/dashboard.py": """from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from core.database import get_db

router = APIRouter()


@router.get("/kpis")
async def get_kpis(db: AsyncSession = Depends(get_db)):
    \"\"\"Main dashboard KPI cards — total revenue, orders, customers, inventory alerts.\"\"\"
    result = await db.execute(text(\"\"\"
        SELECT
            COALESCE(SUM(total_amount), 0) AS total_revenue,
            COUNT(*) AS total_orders,
            COALESCE(AVG(total_amount), 0) AS avg_order_value
        FROM sales
        WHERE sale_date >= NOW() - INTERVAL '30 days'
    \"\"\"))
    row = result.fetchone()
    return {
        "total_revenue": round(float(row.total_revenue), 2),
        "total_orders": row.total_orders,
        "avg_order_value": round(float(row.avg_order_value), 2),
    }


@router.get("/revenue-trend")
async def get_revenue_trend(db: AsyncSession = Depends(get_db)):
    \"\"\"Daily revenue trend for the last 90 days.\"\"\"
    result = await db.execute(text(\"\"\"
        SELECT
            DATE(sale_date) AS date,
            SUM(total_amount) AS revenue,
            COUNT(*) AS orders
        FROM sales
        WHERE sale_date >= NOW() - INTERVAL '90 days'
        GROUP BY DATE(sale_date)
        ORDER BY date ASC
    \"\"\"))
    rows = result.fetchall()
    return [
        {"date": str(r.date), "revenue": round(float(r.revenue), 2), "orders": r.orders}
        for r in rows
    ]
""",
    "backend/api/v1/forecast.py": """from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
from ml.forecasting.prophet_model import ProphetForecaster
from ml.forecasting.lstm_model import LSTMForecaster

router = APIRouter()


class ForecastRequest(BaseModel):
    metric: str          # revenue, inventory, demand
    periods: int = 30    # days ahead
    model: str = "prophet"  # prophet | lstm | xgboost


@router.post("/run")
async def run_forecast(req: ForecastRequest):
    \"\"\"Run ML forecast for given metric and return predictions.\"\"\"
    try:
        if req.model == "prophet":
            forecaster = ProphetForecaster()
        elif req.model == "lstm":
            forecaster = LSTMForecaster()
        else:
            raise HTTPException(status_code=400, detail="Unknown model type")

        predictions = await forecaster.predict(req.metric, req.periods)
        return {
            "metric": req.metric,
            "model": req.model,
            "periods": req.periods,
            "predictions": predictions,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models")
async def list_models():
    return {
        "models": [
            {"id": "prophet", "name": "Prophet", "description": "Facebook Prophet — best for seasonal data"},
            {"id": "lstm",    "name": "LSTM",    "description": "Deep learning — captures complex patterns"},
            {"id": "xgboost", "name": "XGBoost", "description": "Gradient boosting — high accuracy with features"},
        ]
    }
""",
    "backend/api/v1/chatbot.py": """from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from ai.chatbot.nlq_engine import NLQEngine
from ai.chatbot.gpt_client import GPTClient

router = APIRouter()
nlq_engine = NLQEngine()
gpt_client = GPTClient()


class ChatRequest(BaseModel):
    message: str
    session_id: str


@router.post("/chat")
async def chat(req: ChatRequest):
    \"\"\"Process natural language query and return structured insights.\"\"\"
    # Try to parse as a data query first
    sql_result = await nlq_engine.process(req.message)
    if sql_result:
        return {"type": "data", "query": req.message, "result": sql_result}

    # Fall back to GPT for general BI questions
    response = await gpt_client.ask(req.message, context="business_intelligence")
    return {"type": "text", "query": req.message, "result": response}


@router.websocket("/ws/{session_id}")
async def websocket_chat(websocket: WebSocket, session_id: str):
    \"\"\"WebSocket endpoint for real-time streaming chat.\"\"\"
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            async for token in gpt_client.stream(data):
                await websocket.send_text(token)
    except WebSocketDisconnect:
        pass
""",
    "backend/api/v1/anomaly.py": """from fastapi import APIRouter
from ml.anomaly.detector import AnomalyDetector

router = APIRouter()
detector = AnomalyDetector()


@router.get("/detect/{metric}")
async def detect_anomalies(metric: str, lookback_days: int = 30):
    \"\"\"Detect anomalies in the given metric over the lookback window.\"\"\"
    anomalies = await detector.detect(metric, lookback_days)
    return {"metric": metric, "anomalies": anomalies, "count": len(anomalies)}
""",
    "backend/api/v1/sales.py": """from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select, func
from core.database import get_db
from models.sales import Sale

router = APIRouter()


@router.get("/summary")
async def get_sales_summary(
    period: str = Query("30d", description="7d | 30d | 90d | 1y"),
    db: AsyncSession = Depends(get_db),
):
    interval_map = {"7d": "7 days", "30d": "30 days", "90d": "90 days", "1y": "1 year"}
    interval = interval_map.get(period, "30 days")
    result = await db.execute(text(f\"\"\"
        SELECT
            SUM(total_amount) AS revenue,
            COUNT(*) AS orders,
            SUM(quantity) AS units_sold,
            AVG(total_amount) AS avg_order_value,
            SUM(discount * total_amount) AS total_discounts
        FROM sales
        WHERE sale_date >= NOW() - INTERVAL '{interval}'
    \"\"\"))
    row = result.fetchone()
    return dict(row._mapping)


@router.get("/by-category")
async def sales_by_category(db: AsyncSession = Depends(get_db)):
    result = await db.execute(text(\"\"\"
        SELECT p.category, SUM(s.total_amount) AS revenue, COUNT(s.id) AS orders
        FROM sales s
        JOIN products p ON s.product_id = p.id
        WHERE s.sale_date >= NOW() - INTERVAL '30 days'
        GROUP BY p.category
        ORDER BY revenue DESC
    \"\"\"))
    return [dict(r._mapping) for r in result.fetchall()]


@router.get("/by-region")
async def sales_by_region(db: AsyncSession = Depends(get_db)):
    result = await db.execute(text(\"\"\"
        SELECT region, SUM(total_amount) AS revenue, COUNT(*) AS orders
        FROM sales
        WHERE sale_date >= NOW() - INTERVAL '30 days'
        GROUP BY region
        ORDER BY revenue DESC
    \"\"\"))
    return [dict(r._mapping) for r in result.fetchall()]
""",
    "backend/api/v1/inventory.py": """from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from core.database import get_db

router = APIRouter()


@router.get("/status")
async def inventory_status(db: AsyncSession = Depends(get_db)):
    result = await db.execute(text(\"\"\"
        SELECT
            p.name, p.sku, p.category,
            i.quantity_on_hand,
            i.reorder_point,
            i.warehouse,
            CASE
                WHEN i.quantity_on_hand <= 0 THEN 'out_of_stock'
                WHEN i.quantity_on_hand <= i.reorder_point THEN 'low_stock'
                ELSE 'in_stock'
            END AS status
        FROM inventory i
        JOIN products p ON i.product_id = p.id
        ORDER BY i.quantity_on_hand ASC
    \"\"\"))
    return [dict(r._mapping) for r in result.fetchall()]


@router.get("/alerts")
async def inventory_alerts(db: AsyncSession = Depends(get_db)):
    result = await db.execute(text(\"\"\"
        SELECT p.name, p.sku, i.quantity_on_hand, i.reorder_point
        FROM inventory i
        JOIN products p ON i.product_id = p.id
        WHERE i.quantity_on_hand <= i.reorder_point
        ORDER BY i.quantity_on_hand ASC
        LIMIT 20
    \"\"\"))
    return {"alerts": [dict(r._mapping) for r in result.fetchall()]}
""",
    "backend/api/v1/customers.py": """from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from core.database import get_db

router = APIRouter()


@router.get("/segments")
async def customer_segments(db: AsyncSession = Depends(get_db)):
    result = await db.execute(text(\"\"\"
        SELECT segment, COUNT(*) AS count, AVG(lifetime_value) AS avg_ltv
        FROM customers
        GROUP BY segment
    \"\"\"))
    return [dict(r._mapping) for r in result.fetchall()]


@router.get("/churn-risk")
async def churn_risk(db: AsyncSession = Depends(get_db)):
    result = await db.execute(text(\"\"\"
        SELECT name, email, churn_risk_score, lifetime_value, segment
        FROM customers
        WHERE churn_risk_score >= 0.6
        ORDER BY churn_risk_score DESC
        LIMIT 50
    \"\"\"))
    return [dict(r._mapping) for r in result.fetchall()]
""",
    # ── ML Engine ──────────────────────────────────────────────────────────
    "backend/ml/__init__.py": "",
    "backend/ml/forecasting/__init__.py": "",
    "backend/ml/forecasting/prophet_model.py": """\"\"\"
Facebook Prophet forecasting model.
Handles seasonal decomposition and holiday effects.
\"\"\"
import pandas as pd
import numpy as np
from prophet import Prophet
from typing import List, Dict


class ProphetForecaster:
    def __init__(self):
        self.model = None

    def _build_training_data(self, metric: str) -> pd.DataFrame:
        \"\"\"Generate synthetic training data for demo purposes.
        In production, query this from the database.
        \"\"\"
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
""",
    "backend/ml/forecasting/lstm_model.py": """\"\"\"
LSTM (Long Short-Term Memory) forecasting model.
Best for complex temporal dependencies.
\"\"\"
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
""",
    "backend/ml/anomaly/__init__.py": "",
    "backend/ml/anomaly/detector.py": """\"\"\"
Anomaly Detection using Isolation Forest + Z-Score.
\"\"\"
import numpy as np
from sklearn.ensemble import IsolationForest
from typing import List, Dict


class AnomalyDetector:
    def __init__(self, contamination: float = 0.05):
        self.model = IsolationForest(
            contamination=contamination, random_state=42, n_estimators=100
        )

    async def detect(self, metric: str, lookback_days: int = 30) -> List[Dict]:
        \"\"\"Detect anomalies in the given metric.\"\"\"
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
""",
    # ── AI Chatbot ─────────────────────────────────────────────────────────
    "backend/ai/__init__.py": "",
    "backend/ai/chatbot/__init__.py": "",
    "backend/ai/chatbot/gpt_client.py": """\"\"\"
OpenAI GPT-4 client for BI conversational queries.
\"\"\"
from openai import AsyncOpenAI
from core.config import settings
from typing import AsyncGenerator

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

SYSTEM_PROMPT = \"\"\"
You are an expert Business Intelligence analyst assistant.
You have access to data about Sales, Inventory, and Customers.
Answer questions clearly and concisely. When presenting numbers,
format them with proper units (e.g. $12,450 or 24.5%).
If asked to chart something, describe the data you would use.
\"\"\"


class GPTClient:
    async def ask(self, message: str, context: str = "") -> str:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message},
            ],
            max_tokens=500,
            temperature=0.3,
        )
        return response.choices[0].message.content

    async def stream(self, message: str) -> AsyncGenerator[str, None]:
        stream = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message},
            ],
            stream=True,
            max_tokens=500,
        )
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
""",
    "backend/ai/chatbot/nlq_engine.py": """\"\"\"
Natural Language Query (NLQ) Engine.
Translates plain English to SQL queries.
\"\"\"
from typing import Optional, Dict, Any
import re


QUERY_PATTERNS = {
    r"(top|best)\\s*(\\d+)?\\s*product": "top_products",
    r"revenue\\s*(today|this week|this month)": "revenue_period",
    r"low\\s*stock|reorder": "low_stock",
    r"churn|at risk customer": "churn_risk",
    r"(sales|revenue) by (region|country)": "sales_by_region",
    r"anomal|unusual|spike|drop": "anomalies",
}

CANNED_QUERIES = {
    "top_products": "SELECT p.name, SUM(s.total_amount) AS revenue FROM sales s JOIN products p ON s.product_id = p.id GROUP BY p.name ORDER BY revenue DESC LIMIT 10",
    "low_stock": "SELECT p.name, i.quantity_on_hand, i.reorder_point FROM inventory i JOIN products p ON i.product_id = p.id WHERE i.quantity_on_hand <= i.reorder_point",
    "churn_risk": "SELECT name, churn_risk_score, lifetime_value FROM customers WHERE churn_risk_score >= 0.6 ORDER BY churn_risk_score DESC LIMIT 20",
    "sales_by_region": "SELECT region, SUM(total_amount) AS revenue FROM sales WHERE sale_date >= NOW() - INTERVAL '30 days' GROUP BY region ORDER BY revenue DESC",
}


class NLQEngine:
    async def process(self, query: str) -> Optional[Dict[str, Any]]:
        query_lower = query.lower()
        for pattern, query_type in QUERY_PATTERNS.items():
            if re.search(pattern, query_lower):
                sql = CANNED_QUERIES.get(query_type)
                if sql:
                    return {"type": query_type, "sql": sql, "description": f"Query: {query_type.replace('_', ' ').title()}"}
        return None
""",
    # ── Scripts ────────────────────────────────────────────────────────────
    "backend/scripts/__init__.py": "",
    "backend/scripts/seed_data.py": """\"\"\"
Seed the database with realistic sample data.
Run: python scripts/seed_data.py
\"\"\"
import asyncio
import random
from datetime import datetime, timedelta
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from core.config import settings
from core.security import hash_password
from models.user import User, UserRole
from models.sales import Product, Sale
from models.inventory import Inventory
from models.customer import Customer
from core.database import Base

CATEGORIES = ["Electronics", "Clothing", "Food & Beverage", "Home & Garden", "Sports", "Books"]
REGIONS = ["North", "South", "East", "West", "Central"]
CHANNELS = ["online", "retail", "wholesale"]
SEGMENTS = ["enterprise", "smb", "individual"]

async def seed():
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    Session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with Session() as db:
        print("Seeding users...")
        admin = User(email="admin@bi.com", full_name="Admin User",
                     hashed_password=hash_password("admin123"), role=UserRole.admin, is_premium=True)
        analyst = User(email="analyst@bi.com", full_name="Data Analyst",
                       hashed_password=hash_password("analyst123"), role=UserRole.analyst)
        db.add_all([admin, analyst])
        await db.flush()

        print("Seeding products...")
        products = []
        for i in range(50):
            p = Product(
                name=f"Product {i+1:03d}",
                category=random.choice(CATEGORIES),
                sku=f"SKU-{i+1:05d}",
                price=round(random.uniform(10, 500), 2),
                cost=round(random.uniform(5, 200), 2),
            )
            db.add(p)
            products.append(p)
        await db.flush()

        print("Seeding customers...")
        customers = []
        for i in range(200):
            c = Customer(
                name=f"Customer {i+1}",
                email=f"customer{i+1}@example.com",
                country="USA",
                region=random.choice(REGIONS),
                segment=random.choice(SEGMENTS),
                lifetime_value=round(random.uniform(100, 50000), 2),
                churn_risk_score=round(random.uniform(0, 1), 3),
                acquisition_channel=random.choice(["organic", "paid", "referral", "direct"]),
            )
            db.add(c)
            customers.append(c)
        await db.flush()

        print("Seeding sales (2 years of data)...")
        start_date = datetime.now() - timedelta(days=730)
        for i in range(5000):
            sale_date = start_date + timedelta(days=random.randint(0, 730))
            product = random.choice(products)
            qty = random.randint(1, 20)
            sale = Sale(
                product_id=product.id,
                customer_id=random.choice(customers).id if random.random() > 0.3 else None,
                quantity=qty,
                unit_price=product.price,
                total_amount=round(product.price * qty * random.uniform(0.85, 1.0), 2),
                discount=round(random.uniform(0, 0.15), 3),
                region=random.choice(REGIONS),
                channel=random.choice(CHANNELS),
                sale_date=sale_date,
            )
            db.add(sale)

        print("Seeding inventory...")
        for product in products:
            inv = Inventory(
                product_id=product.id,
                warehouse=f"WH-{random.choice(['A', 'B', 'C'])}",
                quantity_on_hand=random.randint(0, 1000),
                reorder_point=random.randint(20, 100),
                reorder_quantity=random.randint(100, 500),
            )
            db.add(inv)

        await db.commit()
        print("✅ Database seeded successfully!")
        print("   Login: admin@bi.com / admin123")

if __name__ == "__main__":
    asyncio.run(seed())
""",
    # ── DB migrations ──────────────────────────────────────────────────────
    "backend/db/init.sql": """-- Initial schema for BI Platform
-- This runs automatically on first Docker startup

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- The tables are created by SQLAlchemy/Alembic
-- This file is for extensions and custom functions

-- Function to calculate growth rate
CREATE OR REPLACE FUNCTION growth_rate(current_val FLOAT, previous_val FLOAT)
RETURNS FLOAT AS $$
BEGIN
  IF previous_val = 0 THEN RETURN 0; END IF;
  RETURN ROUND(((current_val - previous_val) / previous_val * 100)::NUMERIC, 2);
END;
$$ LANGUAGE plpgsql;
""",
    "backend/alembic.ini": """[alembic]
script_location = alembic
sqlalchemy.url = postgresql+asyncpg://biuser:bipassword@localhost:5432/biplatform
""",
    # ── Frontend ───────────────────────────────────────────────────────────
    "frontend/Dockerfile": """FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --silent

COPY . .

EXPOSE 3000
CMD ["npm", "start"]
""",
    "frontend/package.json": """{
  "name": "bi-platform-frontend",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-router-dom": "^6.23.1",
    "react-scripts": "5.0.1",
    "axios": "^1.7.2",
    "recharts": "^2.12.7",
    "antd": "^5.18.1",
    "@ant-design/icons": "^5.3.7",
    "@ant-design/charts": "^2.1.4",
    "dayjs": "^1.11.11",
    "zustand": "^4.5.2",
    "react-query": "^3.39.3"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test"
  },
  "proxy": "http://localhost:8000",
  "browserslist": {
    "production": [">0.2%", "not dead"],
    "development": ["last 1 chrome version"]
  }
}
""",
    "frontend/src/index.js": """import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import App from './App';
import './index.css';

const queryClient = new QueryClient({
  defaultOptions: { queries: { refetchOnWindowFocus: false, retry: 1 } },
});

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <QueryClientProvider client={queryClient}>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </QueryClientProvider>
);
""",
    "frontend/src/App.js": """import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { ConfigProvider, theme } from 'antd';
import MainLayout from './layouts/MainLayout';
import Dashboard from './pages/Dashboard';
import Sales from './pages/Sales';
import Inventory from './pages/Inventory';
import Customers from './pages/Customers';
import Forecast from './pages/Forecast';
import Anomaly from './pages/Anomaly';
import Chatbot from './pages/Chatbot';
import Login from './pages/Login';
import { useAuthStore } from './store/authStore';

function App() {
  const { isAuthenticated } = useAuthStore();

  return (
    <ConfigProvider theme={{ algorithm: theme.defaultAlgorithm }}>
      <Routes>
        <Route path="/login" element={<Login />} />
        {isAuthenticated ? (
          <Route element={<MainLayout />}>
            <Route path="/" element={<Navigate to="/dashboard" />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/sales" element={<Sales />} />
            <Route path="/inventory" element={<Inventory />} />
            <Route path="/customers" element={<Customers />} />
            <Route path="/forecast" element={<Forecast />} />
            <Route path="/anomaly" element={<Anomaly />} />
            <Route path="/chatbot" element={<Chatbot />} />
          </Route>
        ) : (
          <Route path="*" element={<Navigate to="/login" />} />
        )}
      </Routes>
    </ConfigProvider>
  );
}

export default App;
""",
    "frontend/src/store/authStore.js": """import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import axios from '../api/axios';

export const useAuthStore = create(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,

      login: async (email, password) => {
        const params = new URLSearchParams();
        params.append('username', email);
        params.append('password', password);
        const res = await axios.post('/api/v1/auth/login', params);
        const { access_token, user_id, role } = res.data;
        axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
        set({ token: access_token, user: { id: user_id, email, role }, isAuthenticated: true });
        return res.data;
      },

      logout: () => {
        delete axios.defaults.headers.common['Authorization'];
        set({ user: null, token: null, isAuthenticated: false });
      },
    }),
    { name: 'bi-auth' }
  )
);
""",
    "frontend/src/api/axios.js": """import axios from 'axios';

const instance = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  timeout: 30000,
});

instance.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('bi-auth');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default instance;
""",
    "frontend/src/layouts/MainLayout.js": """import React, { useState } from 'react';
import { Layout, Menu, Avatar, Typography, Badge } from 'antd';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import {
  DashboardOutlined, ShoppingCartOutlined, InboxOutlined,
  TeamOutlined, LineChartOutlined, AlertOutlined,
  RobotOutlined, LogoutOutlined
} from '@ant-design/icons';
import { useAuthStore } from '../store/authStore';

const { Header, Sider, Content } = Layout;
const { Title } = Typography;

const menuItems = [
  { key: '/dashboard',  icon: <DashboardOutlined />,    label: 'Dashboard' },
  { key: '/sales',      icon: <ShoppingCartOutlined />, label: 'Sales' },
  { key: '/inventory',  icon: <InboxOutlined />,        label: 'Inventory' },
  { key: '/customers',  icon: <TeamOutlined />,         label: 'Customers' },
  { key: '/forecast',   icon: <LineChartOutlined />,    label: 'Forecast' },
  { key: '/anomaly',    icon: <AlertOutlined />,        label: 'Anomaly Detection' },
  { key: '/chatbot',    icon: <RobotOutlined />,        label: 'AI Chatbot' },
];

export default function MainLayout() {
  const [collapsed, setCollapsed] = useState(false);
  const navigate = useNavigate();
  const { pathname } = useLocation();
  const { user, logout } = useAuthStore();

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider collapsible collapsed={collapsed} onCollapse={setCollapsed}
             style={{ background: '#001529' }}>
        <div style={{ padding: '16px', textAlign: 'center' }}>
          {!collapsed && (
            <Title level={5} style={{ color: '#1677ff', margin: 0 }}>
              BI Platform
            </Title>
          )}
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[pathname]}
          items={menuItems}
          onClick={({ key }) => navigate(key)}
        />
      </Sider>
      <Layout>
        <Header style={{ background: '#fff', padding: '0 24px', display: 'flex',
                         justifyContent: 'flex-end', alignItems: 'center', gap: 16,
                         borderBottom: '1px solid #f0f0f0' }}>
          <Badge dot color="green">
            <Avatar style={{ background: '#1677ff' }}>
              {user?.email?.[0]?.toUpperCase() || 'U'}
            </Avatar>
          </Badge>
          <span style={{ color: '#555' }}>{user?.email}</span>
          <LogoutOutlined onClick={logout} style={{ cursor: 'pointer', color: '#999' }} />
        </Header>
        <Content style={{ margin: '24px', background: '#f5f7fa', borderRadius: 8, padding: '24px' }}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
}
""",
    "frontend/src/pages/Dashboard.js": """import React from 'react';
import { Row, Col, Card, Statistic, Spin } from 'antd';
import { ArrowUpOutlined, ArrowDownOutlined } from '@ant-design/icons';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { useQuery } from 'react-query';
import axios from '../api/axios';

function KPICard({ title, value, prefix, suffix, trend }) {
  return (
    <Card bordered={false} style={{ borderRadius: 12, boxShadow: '0 2px 8px rgba(0,0,0,0.06)' }}>
      <Statistic
        title={title}
        value={value}
        prefix={prefix}
        suffix={suffix}
        valueStyle={{ color: trend >= 0 ? '#3f8600' : '#cf1322' }}
      />
      <div style={{ color: trend >= 0 ? '#3f8600' : '#cf1322', marginTop: 4, fontSize: 12 }}>
        {trend >= 0 ? <ArrowUpOutlined /> : <ArrowDownOutlined />}
        {Math.abs(trend)}% vs last period
      </div>
    </Card>
  );
}

export default function Dashboard() {
  const { data: kpis, isLoading: kpiLoading } = useQuery(
    'kpis', () => axios.get('/api/v1/dashboard/kpis').then(r => r.data)
  );
  const { data: trend, isLoading: trendLoading } = useQuery(
    'revenue-trend', () => axios.get('/api/v1/dashboard/revenue-trend').then(r => r.data)
  );

  if (kpiLoading) return <Spin size="large" />;

  return (
    <div>
      <h2 style={{ marginBottom: 24 }}>Dashboard Overview</h2>
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={6}>
          <KPICard title="Total Revenue" value={kpis?.total_revenue?.toLocaleString()}
                   prefix="$" trend={12.5} />
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <KPICard title="Total Orders" value={kpis?.total_orders} trend={8.2} />
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <KPICard title="Avg Order Value" value={kpis?.avg_order_value?.toFixed(2)}
                   prefix="$" trend={-2.1} />
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <KPICard title="Active Customers" value="1,234" trend={5.7} />
        </Col>
      </Row>

      <Card title="Revenue Trend (Last 90 Days)" bordered={false}
            style={{ borderRadius: 12, boxShadow: '0 2px 8px rgba(0,0,0,0.06)' }}>
        {trendLoading ? <Spin /> : (
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={trend}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="date" tick={{ fontSize: 11 }}
                     tickFormatter={v => v.slice(5)} />
              <YAxis tick={{ fontSize: 11 }} tickFormatter={v => `$${(v/1000).toFixed(0)}k`} />
              <Tooltip formatter={(v) => [`$${v.toLocaleString()}`, 'Revenue']} />
              <Legend />
              <Line type="monotone" dataKey="revenue" stroke="#1677ff"
                    strokeWidth={2} dot={false} name="Revenue" />
              <Line type="monotone" dataKey="orders" stroke="#52c41a"
                    strokeWidth={2} dot={false} name="Orders" yAxisId={0} />
            </LineChart>
          </ResponsiveContainer>
        )}
      </Card>
    </div>
  );
}
""",
    "frontend/src/pages/Forecast.js": """import React, { useState } from 'react';
import { Card, Select, Slider, Button, Spin, Alert } from 'antd';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip,
         ResponsiveContainer, Legend } from 'recharts';
import axios from '../api/axios';

const { Option } = Select;

export default function Forecast() {
  const [metric, setMetric] = useState('revenue');
  const [model, setModel] = useState('prophet');
  const [periods, setPeriods] = useState(30);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const runForecast = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await axios.post('/api/v1/forecast/run', { metric, model, periods });
      setData(res.data.predictions);
    } catch (e) {
      setError(e.response?.data?.detail || 'Forecast failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2>ML Forecasting</h2>
      <Card style={{ marginBottom: 24, borderRadius: 12 }}>
        <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap', alignItems: 'center' }}>
          <Select value={metric} onChange={setMetric} style={{ width: 160 }}>
            <Option value="revenue">Revenue</Option>
            <Option value="inventory">Inventory</Option>
            <Option value="demand">Demand</Option>
          </Select>
          <Select value={model} onChange={setModel} style={{ width: 160 }}>
            <Option value="prophet">Prophet</Option>
            <Option value="lstm">LSTM</Option>
            <Option value="xgboost">XGBoost</Option>
          </Select>
          <div style={{ flex: 1, minWidth: 200 }}>
            <span>Forecast days: {periods}</span>
            <Slider min={7} max={365} value={periods} onChange={setPeriods}
                    marks={{ 7: '7d', 30: '30d', 90: '90d', 180: '180d', 365: '1y' }} />
          </div>
          <Button type="primary" onClick={runForecast} loading={loading}>
            Run Forecast
          </Button>
        </div>
      </Card>

      {error && <Alert type="error" message={error} style={{ marginBottom: 16 }} />}

      {loading && <div style={{ textAlign: 'center', padding: 48 }}><Spin size="large" /></div>}

      {data && (
        <Card title={`${metric.charAt(0).toUpperCase() + metric.slice(1)} Forecast — ${model.toUpperCase()} model`}
              style={{ borderRadius: 12 }}>
          <ResponsiveContainer width="100%" height={400}>
            <AreaChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="date" tick={{ fontSize: 11 }} tickFormatter={v => v.slice(5)} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Legend />
              <Area type="monotone" dataKey="upper" stroke="transparent"
                    fill="#1677ff" fillOpacity={0.1} name="Upper bound" />
              <Area type="monotone" dataKey="predicted" stroke="#1677ff"
                    fill="#1677ff" fillOpacity={0.3} strokeWidth={2} name="Predicted" />
              <Area type="monotone" dataKey="lower" stroke="transparent"
                    fill="#ffffff" name="Lower bound" />
            </AreaChart>
          </ResponsiveContainer>
        </Card>
      )}
    </div>
  );
}
""",
    "frontend/src/pages/Chatbot.js": """import React, { useState, useRef, useEffect } from 'react';
import { Card, Input, Button, Typography, Tag } from 'antd';
import { SendOutlined, RobotOutlined, UserOutlined } from '@ant-design/icons';
import axios from '../api/axios';

const { Text } = Typography;

const SAMPLE_QUESTIONS = [
  "What are the top 10 products by revenue?",
  "Show me customers at churn risk",
  "Which region has the highest sales?",
  "What's our inventory alert status?",
];

export default function Chatbot() {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Hi! I\\'m your AI BI assistant. Ask me anything about your sales, inventory, or customer data.' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const send = async (text) => {
    const msg = text || input;
    if (!msg.trim()) return;
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: msg }]);
    setLoading(true);
    try {
      const res = await axios.post('/api/v1/chatbot/chat', {
        message: msg, session_id: 'user-session-1'
      });
      const reply = typeof res.data.result === 'string'
        ? res.data.result
        : JSON.stringify(res.data.result, null, 2);
      setMessages(prev => [...prev, { role: 'assistant', content: reply }]);
    } catch (e) {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, I encountered an error. Please try again.' }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2>AI Chatbot — Natural Language Queries</h2>
      <div style={{ marginBottom: 16 }}>
        {SAMPLE_QUESTIONS.map(q => (
          <Tag key={q} color="blue" style={{ cursor: 'pointer', marginBottom: 8 }}
               onClick={() => send(q)}>{q}</Tag>
        ))}
      </div>
      <Card style={{ borderRadius: 12, height: 500, display: 'flex', flexDirection: 'column' }}>
        <div style={{ flex: 1, overflowY: 'auto', padding: 16, display: 'flex', flexDirection: 'column', gap: 12 }}>
          {messages.map((m, i) => (
            <div key={i} style={{ display: 'flex', justifyContent: m.role === 'user' ? 'flex-end' : 'flex-start' }}>
              <div style={{
                maxWidth: '75%', padding: '10px 14px', borderRadius: 12,
                background: m.role === 'user' ? '#1677ff' : '#f5f5f5',
                color: m.role === 'user' ? '#fff' : '#333',
                fontSize: 14, lineHeight: 1.6,
                whiteSpace: 'pre-wrap',
              }}>
                {m.role === 'assistant' && <RobotOutlined style={{ marginRight: 6 }} />}
                {m.content}
              </div>
            </div>
          ))}
          {loading && (
            <div style={{ display: 'flex', gap: 6 }}>
              <div className="typing-dot" /><div className="typing-dot" /><div className="typing-dot" />
            </div>
          )}
          <div ref={bottomRef} />
        </div>
        <div style={{ padding: '12px 16px', borderTop: '1px solid #f0f0f0', display: 'flex', gap: 8 }}>
          <Input
            value={input}
            onChange={e => setInput(e.target.value)}
            onPressEnter={() => send()}
            placeholder="Ask about sales, inventory, customers..."
            style={{ flex: 1 }}
          />
          <Button type="primary" icon={<SendOutlined />} onClick={() => send()} loading={loading} />
        </div>
      </Card>
    </div>
  );
}
""",
    "frontend/src/pages/Login.js": """import React, { useState } from 'react';
import { Form, Input, Button, Card, Typography, Alert } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';

const { Title, Text } = Typography;

export default function Login() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();
  const login = useAuthStore(s => s.login);

  const onFinish = async ({ email, password }) => {
    setLoading(true);
    setError(null);
    try {
      await login(email, password);
      navigate('/dashboard');
    } catch (e) {
      setError(e.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center',
                  justifyContent: 'center', background: 'linear-gradient(135deg, #001529 0%, #1677ff 100%)' }}>
      <Card style={{ width: 420, borderRadius: 16, boxShadow: '0 20px 60px rgba(0,0,0,0.3)' }}>
        <div style={{ textAlign: 'center', marginBottom: 32 }}>
          <Title level={3} style={{ margin: 0, color: '#1677ff' }}>BI Platform</Title>
          <Text type="secondary">AI-Powered Business Intelligence</Text>
        </div>
        {error && <Alert type="error" message={error} style={{ marginBottom: 16 }} />}
        <Form onFinish={onFinish} layout="vertical" size="large">
          <Form.Item name="email" rules={[{ required: true, type: 'email' }]}>
            <Input prefix={<UserOutlined />} placeholder="Email" />
          </Form.Item>
          <Form.Item name="password" rules={[{ required: true }]}>
            <Input.Password prefix={<LockOutlined />} placeholder="Password" />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" block loading={loading}>
              Sign In
            </Button>
          </Form.Item>
        </Form>
        <Text type="secondary" style={{ fontSize: 12 }}>
          Demo: admin@bi.com / admin123
        </Text>
      </Card>
    </div>
  );
}
""",
    # Placeholder pages
    "frontend/src/pages/Sales.js": """import React from 'react';
import { Card, Row, Col, Spin } from 'antd';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
         ResponsiveContainer, Legend, PieChart, Pie, Cell } from 'recharts';
import { useQuery } from 'react-query';
import axios from '../api/axios';

const COLORS = ['#1677ff','#52c41a','#faad14','#f5222d','#722ed1','#13c2c2'];

export default function Sales() {
  const { data: byCategory, isLoading } = useQuery(
    'salesByCategory', () => axios.get('/api/v1/sales/by-category').then(r => r.data)
  );
  const { data: byRegion } = useQuery(
    'salesByRegion', () => axios.get('/api/v1/sales/by-region').then(r => r.data)
  );
  if (isLoading) return <Spin size="large" />;
  return (
    <div>
      <h2>Sales Analytics</h2>
      <Row gutter={[16, 16]}>
        <Col xs={24} lg={14}>
          <Card title="Revenue by Category" style={{ borderRadius: 12 }}>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={byCategory}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="category" tick={{ fontSize: 11 }} />
                <YAxis tickFormatter={v => `$${(v/1000).toFixed(0)}k`} />
                <Tooltip formatter={v => [`$${Number(v).toLocaleString()}`, 'Revenue']} />
                <Bar dataKey="revenue" fill="#1677ff" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </Col>
        <Col xs={24} lg={10}>
          <Card title="Sales by Region" style={{ borderRadius: 12 }}>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie data={byRegion} dataKey="revenue" nameKey="region" cx="50%" cy="50%"
                     outerRadius={100} label={({ region, percent }) => `${region} ${(percent*100).toFixed(0)}%`}>
                  {byRegion?.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                </Pie>
                <Tooltip formatter={v => [`$${Number(v).toLocaleString()}`, 'Revenue']} />
              </PieChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>
    </div>
  );
}
""",
    "frontend/src/pages/Inventory.js": """import React from 'react';
import { Card, Table, Tag, Badge, Spin } from 'antd';
import { useQuery } from 'react-query';
import axios from '../api/axios';

const statusColor = { in_stock: 'success', low_stock: 'warning', out_of_stock: 'error' };
const statusLabel = { in_stock: 'In Stock', low_stock: 'Low Stock', out_of_stock: 'Out of Stock' };

export default function Inventory() {
  const { data, isLoading } = useQuery('inventory', () => axios.get('/api/v1/inventory/status').then(r => r.data));
  const columns = [
    { title: 'Product', dataIndex: 'name', key: 'name' },
    { title: 'SKU', dataIndex: 'sku', key: 'sku' },
    { title: 'Category', dataIndex: 'category', key: 'category' },
    { title: 'On Hand', dataIndex: 'quantity_on_hand', key: 'qty', sorter: (a,b) => a.quantity_on_hand - b.quantity_on_hand },
    { title: 'Reorder At', dataIndex: 'reorder_point', key: 'reorder' },
    { title: 'Warehouse', dataIndex: 'warehouse', key: 'warehouse' },
    { title: 'Status', dataIndex: 'status', key: 'status',
      render: s => <Badge status={statusColor[s]} text={statusLabel[s]} /> },
  ];
  if (isLoading) return <Spin size="large" />;
  return (
    <div>
      <h2>Inventory Management</h2>
      <Card style={{ borderRadius: 12 }}>
        <Table dataSource={data} columns={columns} rowKey="sku"
               pagination={{ pageSize: 15 }}
               rowClassName={r => r.status === 'out_of_stock' ? 'row-danger' : r.status === 'low_stock' ? 'row-warning' : ''} />
      </Card>
    </div>
  );
}
""",
    "frontend/src/pages/Customers.js": """import React from 'react';
import { Card, Row, Col, Table, Progress, Spin } from 'antd';
import { useQuery } from 'react-query';
import axios from '../api/axios';

export default function Customers() {
  const { data: churn, isLoading } = useQuery('churnRisk', () => axios.get('/api/v1/customers/churn-risk').then(r => r.data));
  const columns = [
    { title: 'Name', dataIndex: 'name', key: 'name' },
    { title: 'Email', dataIndex: 'email', key: 'email' },
    { title: 'Segment', dataIndex: 'segment', key: 'segment' },
    { title: 'LTV', dataIndex: 'lifetime_value', key: 'ltv', render: v => `$${Number(v).toLocaleString()}`, sorter: (a,b) => a.lifetime_value - b.lifetime_value },
    { title: 'Churn Risk', dataIndex: 'churn_risk_score', key: 'churn',
      render: v => <Progress percent={Math.round(v*100)} size="small" status={v > 0.8 ? 'exception' : v > 0.6 ? 'active' : 'normal'} />,
      sorter: (a,b) => b.churn_risk_score - a.churn_risk_score },
  ];
  if (isLoading) return <Spin size="large" />;
  return (
    <div>
      <h2>Customer Analytics</h2>
      <Card title="High Churn Risk Customers" style={{ borderRadius: 12 }}>
        <Table dataSource={churn} columns={columns} rowKey="email" pagination={{ pageSize: 10 }} />
      </Card>
    </div>
  );
}
""",
    "frontend/src/pages/Anomaly.js": """import React, { useState } from 'react';
import { Card, Select, Button, Alert, Spin, Badge } from 'antd';
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import axios from '../api/axios';

export default function Anomaly() {
  const [metric, setMetric] = useState('revenue');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  const detect = async () => {
    setLoading(true);
    const res = await axios.get(`/api/v1/anomaly/detect/${metric}`);
    setData(res.data);
    setLoading(false);
  };

  return (
    <div>
      <h2>Anomaly Detection</h2>
      <Card style={{ marginBottom: 24, borderRadius: 12 }}>
        <div style={{ display: 'flex', gap: 16, alignItems: 'center' }}>
          <Select value={metric} onChange={setMetric} style={{ width: 160 }}>
            <Select.Option value="revenue">Revenue</Select.Option>
            <Select.Option value="inventory">Inventory</Select.Option>
            <Select.Option value="orders">Orders</Select.Option>
          </Select>
          <Button type="primary" onClick={detect} loading={loading}>Detect Anomalies</Button>
        </div>
      </Card>
      {loading && <Spin size="large" />}
      {data && (
        <Card title={`${data.count} anomalies detected in ${metric}`} style={{ borderRadius: 12 }}>
          {data.anomalies.map((a, i) => (
            <Alert key={i} type={a.severity === 'high' ? 'error' : 'warning'} showIcon
                   message={`${a.date} — Value: ${a.value.toLocaleString()} (z-score: ${a.z_score})`}
                   style={{ marginBottom: 8 }} />
          ))}
        </Card>
      )}
    </div>
  );
}
""",
    "frontend/src/index.css": """* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f5f7fa; }
.row-danger td { background: #fff2f0 !important; }
.row-warning td { background: #fffbe6 !important; }
.typing-dot {
  width: 8px; height: 8px; border-radius: 50%; background: #1677ff;
  animation: bounce 1.2s infinite;
}
.typing-dot:nth-child(2) { animation-delay: 0.2s; }
.typing-dot:nth-child(3) { animation-delay: 0.4s; }
@keyframes bounce { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-8px); } }
""",
    # ── Nginx ──────────────────────────────────────────────────────────────
    "nginx/nginx.conf": """worker_processes auto;

events { worker_connections 1024; }

http {
    upstream backend  { server backend:8000; }
    upstream frontend { server frontend:3000; }

    server {
        listen 80;

        location /api/ {
            proxy_pass         http://backend;
            proxy_http_version 1.1;
            proxy_set_header   Host $host;
            proxy_set_header   X-Real-IP $remote_addr;
            proxy_read_timeout 300s;
        }

        location /ws/ {
            proxy_pass         http://backend;
            proxy_http_version 1.1;
            proxy_set_header   Upgrade $http_upgrade;
            proxy_set_header   Connection "upgrade";
        }

        location / {
            proxy_pass http://frontend;
            proxy_http_version 1.1;
            proxy_set_header   Host $host;
        }
    }
}
""",
    # ── Notebooks ──────────────────────────────────────────────────────────
    "notebooks/.gitkeep": "",
    # ── ML model placeholders ─────────────────────────────────────────────
    "backend/ml/models/saved/.gitkeep": "",
    # ── GitHub Actions ─────────────────────────────────────────────────────
    ".github/workflows/ci.yml": """name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - name: Install dependencies
        run: cd backend && pip install -r requirements.txt
      - name: Run tests
        run: cd backend && python -m pytest tests/ -v

  test-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20' }
      - run: cd frontend && npm ci && npm test -- --watchAll=false

  deploy:
    needs: [test-backend, test-frontend]
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to production
        run: echo "Add your deployment commands here"
""",
    "backend/tests/__init__.py": "",
    "backend/tests/test_api.py": """\"\"\"Basic API tests.\"\"\"
import pytest
from httpx import AsyncClient, ASGITransport
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


@pytest.mark.asyncio
async def test_health_check():
    from main import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_forecast_models_list():
    from main import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/forecast/models")
    assert response.status_code == 200
    assert len(response.json()["models"]) == 3
""",
}


def create_structure(base_path: str, structure: dict):
    for rel_path, content in structure.items():
        full_path = os.path.join(base_path, rel_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  ✅ {rel_path}")


def print_tree(base_path: str, prefix: str = "", max_depth: int = 4, current_depth: int = 0):
    if current_depth > max_depth:
        return
    items = sorted(os.listdir(base_path))
    items = [i for i in items if not i.startswith(".") or i in [".env.example", ".gitignore"]]
    for i, item in enumerate(items):
        is_last = i == len(items) - 1
        connector = "└── " if is_last else "├── "
        full = os.path.join(base_path, item)
        print(f"{prefix}{connector}{item}")
        if os.path.isdir(full) and current_depth < max_depth:
            extension = "    " if is_last else "│   "
            print_tree(full, prefix + extension, max_depth, current_depth + 1)


if __name__ == "__main__":
    base = os.path.join(os.getcwd(), PROJECT_NAME)
    if os.path.exists(base):
        print(f"⚠️  Directory '{PROJECT_NAME}' already exists. Overwriting files...")
    else:
        os.makedirs(base)

    print(f"\n🚀 Creating BI Platform project structure in: {base}\n")
    create_structure(base, STRUCTURE)

    print(f"\n📁 Directory Tree:\n")
    print(f"{PROJECT_NAME}/")
    print_tree(base)

    print(f"""
{'='*60}
✅  Project created at: {base}
{'='*60}

NEXT STEPS:
  1.  cd {PROJECT_NAME}
  2.  cp .env.example .env
  3.  docker-compose up -d
  4.  cd backend && pip install -r requirements.txt
  5.  python scripts/seed_data.py
  6.  cd frontend && npm install && npm start

  Open: http://localhost:3000
  Login: admin@bi.com / admin123
  API Docs: http://localhost:8000/docs
{'='*60}
""")