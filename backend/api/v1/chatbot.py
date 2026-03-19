from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from core.config import settings
import re

router = APIRouter()

SYSTEM_PROMPT = """You are an expert Business Intelligence analyst.
You help analyze sales, inventory, and customer data.
Keep answers short, clear and actionable."""

NLQ_PATTERNS = {
    r"top.*product|best.*product|highest.*sale":
        "Top products this month: Laptop Pro 15, Smartphone X12, Smart Watch, Wireless Headphones, Tablet 10 inch.",
    r"low.*stock|reorder|out of stock":
        "Low stock alerts: 5 products need reordering. Worst: Football Official (2 units), Cotton T-Shirt (4 units).",
    r"churn|at.?risk|losing customer":
        "23 customers with high churn risk (score > 0.8). Recommend targeted retention campaign.",
    r"revenue|income|earning|sales total":
        "Revenue this month: NPR 12,45,678 (+12.5% vs last month). Best region: Bagmati.",
    r"region|area|location|province":
        "Sales by region: Bagmati 36.6%, Gandaki 25%, Lumbini 19.7%, Koshi 13.4%, Madhesh 5.3%.",
    r"customer|client|buyer":
        "300 total customers. Enterprise avg LTV NPR 1,50,000. SMB avg LTV NPR 45,000.",
    r"inventory|stock|warehouse":
        "25 products total. 15 in stock, 7 low stock, 3 out of stock across 3 warehouses.",
    r"forecast|predict|future|next month":
        "Revenue forecast next 30 days: NPR 13,20,000 (Prophet model, +6% growth trend).",
    r"anomal|unusual|spike|drop":
        "4 anomalies detected in last 30 days. 2 revenue spikes, 2 drops. Check Day 12 spike.",
    r"growth|increase|trend":
        "Revenue +12.5% MoM, Orders +8.2% MoM. Electronics leading at +24% growth.",
    r"hello|hi|hey|help":
        "Hello! I can help with sales, inventory, customers, forecasts and anomalies. What would you like to know?",
}


def nlq_match(query: str):
    query_lower = query.lower()
    for pattern, answer in NLQ_PATTERNS.items():
        if re.search(pattern, query_lower):
            return answer
    return None


async def ask_gpt(message: str):
    if not settings.OPENAI_API_KEY:
        return None
    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message},
            ],
            max_tokens=400,
            temperature=0.3,
        )
        return response.choices[0].message.content
    except Exception as e:
        return None


class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"


@router.post("/chat")
async def chat(req: ChatRequest):
    # 1. Try pattern matching first
    result = nlq_match(req.message)
    if result:
        return {"type": "insight", "query": req.message,
                "response": result, "source": "local"}

    # 2. Try OpenAI if key is set
    if settings.OPENAI_API_KEY:
        gpt_result = await ask_gpt(req.message)
        if gpt_result:
            return {"type": "ai", "query": req.message,
                    "response": gpt_result, "source": "openai"}

    # 3. Fallback
    return {
        "type": "fallback",
        "query": req.message,
        "response": "Try asking about: sales, inventory, customers, forecasts, or anomalies.",
        "source": "fallback",
    }


@router.get("/suggestions")
async def get_suggestions():
    return {
        "suggestions": [
            "What are my top products by revenue?",
            "Which customers are at churn risk?",
            "Show me low stock alerts",
            "What is the revenue forecast for next month?",
            "Which region has the highest sales?",
            "Are there any anomalies in revenue?",
            "What is our growth trend?",
            "Which sales channel performs best?",
        ]
    }


@router.websocket("/ws/{session_id}")
async def websocket_chat(websocket: WebSocket, session_id: str):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            result = nlq_match(data)
            if result:
                await websocket.send_text(result)
                continue
            await websocket.send_text(
                "Ask me about sales, inventory, customers or forecasts."
            )
    except WebSocketDisconnect:
        pass