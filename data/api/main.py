"""
HealthApp API — FastAPI entry point
Run: uv run uvicorn api.main:app --reload --port 8000
Docs: http://localhost:8000/docs
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import users, readiness, recommendations, analytics, coach_messages
import logging

log = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    from api.scheduler import setup_scheduler
    scheduler = setup_scheduler()
    log.info("🚀 HealthApp API startad")
    yield
    # Shutdown
    scheduler.shutdown()
    log.info("🛑 HealthApp API stoppad")

app = FastAPI(
    title="HealthApp API",
    description="Training Intelligence Platform — AI-driven coaching & analytics",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(readiness.router)
app.include_router(recommendations.router)
app.include_router(analytics.router)
app.include_router(coach_messages.router)

@app.get("/")
def root():
    return {
        "app": "HealthApp API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "users": "/users/",
            "readiness": "/users/{id}/readiness",
            "fatigue": "/users/{id}/fatigue",
            "volume": "/users/{id}/volume",
            "features": "/users/{id}/features",
            "ai_coach": "/users/{id}/coach",
            "recommendations": "/users/{id}/recommendations",
            "predictions": "/users/{id}/predictions",
            "dashboard": "/analytics/readiness-dashboard",
            "at_risk": "/analytics/at-risk",
            "scheduler": "/scheduler/status",
        }
    }

@app.get("/health")
def health():
    from core.db import get_engine
    from sqlalchemy import text
    try:
        with get_engine().connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "healthy", "db": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "db": str(e)}

@app.get("/scheduler/status")
def scheduler_status():
    from api.scheduler import scheduler
    jobs = []
    for job in scheduler.get_jobs():
        jobs.append({
            "id": job.id,
            "next_run": str(job.next_run_time),
        })
    return {"running": scheduler.running, "jobs": jobs}

@app.post("/scheduler/run/{job_id}")
def run_job_now(job_id: str):
    """Trigga ett specifikt jobb manuellt."""
    from api.scheduler import scheduler
    job = scheduler.get_job(job_id)
    if not job:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found")
    job.modify(next_run_time=__import__('datetime').datetime.now())
    return {"message": f"Job '{job_id}' triggered", "status": "queued"}
