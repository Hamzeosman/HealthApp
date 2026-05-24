"""
HealthApp API — FastAPI entry point
Run: uv run uvicorn api.main:app --reload
Docs: http://localhost:8000/docs
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import users, readiness, recommendations, analytics

app = FastAPI(
    title="HealthApp API",
    description="Training Intelligence Platform — AI-driven coaching & analytics",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
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
        }
    }

@app.get("/health")
def health():
    from core.db import get_engine
    try:
        with get_engine().connect() as conn:
            conn.execute(__import__("sqlalchemy").text("SELECT 1"))
        return {"status": "healthy", "db": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "db": str(e)}
