from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager
import asyncpg
import os
from prometheus_fastapi_instrumentator import Instrumentator

DATABASE_URL = os.getenv("DATABASE_URL")

INIT_DB_SCRIPT = """
CREATE TABLE IF NOT EXISTS nodes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    hostname VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'Online',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS metrics (
    id BIGSERIAL PRIMARY KEY,
    node_id UUID REFERENCES nodes(id) ON DELETE CASCADE,
    metric_type VARCHAR(50),
    value FLOAT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
"""

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Initializing Database Connection Pool...")
    # ساخت یک استخر اتصالات با ظرفیت حفظ 10 تا 50 اتصال همزمان
    app.state.pool = await asyncpg.create_pool(DATABASE_URL, min_size=10, max_size=50)
    
    # قرض گرفتن یک اتصال موقت برای ساخت جداول اولیه
    async with app.state.pool.acquire() as conn:
        await conn.execute(INIT_DB_SCRIPT)
        print("Database tables validated/created successfully.")
    
    yield 
    
    # بستن استخر هنگام خاموش شدن سرور
    await app.state.pool.close()

app = FastAPI(title="Enterprise Monitoring API", lifespan=lifespan)
Instrumentator().instrument(app).expose(app)

class NodeCreate(BaseModel):
    hostname: str

class MetricCreate(BaseModel):
    node_id: str
    metric_type: str
    value: float

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API is running with Connection Pool"}

@app.post("/nodes/")
async def register_node(node: NodeCreate):
    async with app.state.pool.acquire() as conn:
        row = await conn.fetchrow(
            "INSERT INTO nodes (hostname) VALUES ($1) RETURNING id",
            node.hostname
        )
        return {"message": "Node registered successfully", "node_id": row['id']}

@app.post("/metrics_ingest/")
async def ingest_metric(metric: MetricCreate):
    # اینجا دیگر کانکشن جدید ساخته نمی‌شود، بلکه از استخر قرض گرفته می‌شود
    async with app.state.pool.acquire() as conn:
        try:
            await conn.execute(
                "INSERT INTO metrics (node_id, metric_type, value) VALUES ($1, $2, $3)",
                metric.node_id, metric.metric_type, metric.value
            )
            return {"message": "Metric ingested successfully"}
        except asyncpg.exceptions.ForeignKeyViolationError:
            raise HTTPException(status_code=400, detail="Invalid node_id. Node does not exist.")