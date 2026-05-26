from fastapi import APIRouter
from sqlalchemy import text
from core.db import get_engine

router = APIRouter(prefix="/analytics", tags=["analytics"])
engine = get_engine()

@router.get("/readiness-dashboard")
def readiness_dashboard():
    """PT-vy: alla klienters readiness status."""
    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT user_id, user_name, fitness_goal, training_zone,
                   readiness_score, recovery_score, fatigue_score,
                   acwr, deload_recommended, current_streak,
                   last_workout_date, active_goals
            FROM mv_fatigue_dashboard
            ORDER BY readiness_score ASC
        """)).fetchall()
        return [dict(zip([
            "user_id","user_name","fitness_goal","training_zone",
            "readiness_score","recovery_score","fatigue_score",
            "acwr","deload_recommended","current_streak",
            "last_workout_date","active_goals"
        ], r)) for r in rows]

@router.get("/weekly-volume")
def weekly_volume():
    """Veckovis volym för alla users."""
    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT user_id, user_name, week_label,
                   sessions, total_volume_kg, avg_rpe, total_sets
            FROM mv_user_weekly_volume
            ORDER BY week_label DESC, total_volume_kg DESC
            LIMIT 100
        """)).fetchall()
        return [dict(zip([
            "user_id","user_name","week_label",
            "sessions","total_volume_kg","avg_rpe","total_sets"
        ], r)) for r in rows]

@router.get("/at-risk")
def at_risk_clients():
    """Klienter med hög risk — för PT-dashboard."""
    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT mp.user_id, u.name,
                   mp.injury_risk_score, mp.dropout_risk_score,
                   mp.overtraining_risk_score, mp.recommended_intensity,
                   mp.primary_recommendation
            FROM model_predictions mp
            JOIN users u ON mp.user_id = u.id
            WHERE mp.date = (
                SELECT MAX(date) FROM model_predictions mp2
                WHERE mp2.user_id = mp.user_id
            )
            AND (mp.injury_risk_score > 50
                 OR mp.dropout_risk_score > 60
                 OR mp.overtraining_risk_score > 50)
            ORDER BY mp.injury_risk_score DESC
        """)).fetchall()
        return [dict(zip([
            "user_id","name","injury_risk","dropout_risk",
            "overtraining_risk","recommended_intensity","recommendation"
        ], r)) for r in rows]
