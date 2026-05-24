from fastapi import APIRouter, HTTPException
from core.domain.recommendation_engine import generate_ai_coach_response
from sqlalchemy import text
from core.db import get_engine

router = APIRouter(prefix="/users", tags=["ai"])
engine = get_engine()

@router.get("/{user_id}/coach")
def ai_coach(user_id: int):
    result = generate_ai_coach_response(user_id)
    if not result:
        raise HTTPException(status_code=404, detail="No data found for user")
    return result

@router.get("/{user_id}/recommendations")
def recommendations(user_id: int):
    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT r.user_id, e.name AS exercise, bp.name AS body_part,
                   r.reason, r.score
            FROM recommendations r
            JOIN exercises e ON r.exercise_id = e.id
            JOIN body_parts bp ON e.body_part_id = bp.id
            WHERE r.user_id = :uid
            ORDER BY r.score DESC LIMIT 10
        """), {"uid": user_id}).fetchall()
        return [dict(zip(
            ["user_id","exercise","body_part","reason","score"], r
        )) for r in rows]

@router.get("/{user_id}/predictions")
def predictions(user_id: int):
    with engine.connect() as conn:
        row = conn.execute(text("""
            SELECT user_id, date, injury_risk_score, dropout_risk_score,
                   plateau_risk_score, overtraining_risk_score,
                   recommended_intensity, recommended_volume_multiplier,
                   primary_recommendation, confidence_score
            FROM model_predictions
            WHERE user_id = :uid
            ORDER BY date DESC LIMIT 1
        """), {"uid": user_id}).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="No predictions found")
        return dict(zip([
            "user_id","date","injury_risk","dropout_risk",
            "plateau_risk","overtraining_risk","recommended_intensity",
            "volume_multiplier","recommendation","confidence"
        ], row))
