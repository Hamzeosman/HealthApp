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

@router.get("/{user_id}/coach-v2")
def ai_coach_v2(user_id: int):
    from core.domain.ai_coach_engine import generate_ai_coach_v2
    result = generate_ai_coach_v2(user_id)
    if not result:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="No data found")
    return result

@router.get("/{user_id}/workout-template")
def workout_template(user_id: int):
    from core.domain.ai_coach_engine import _get_full_context
    from core.domain.workout_templates import select_template, get_todays_session, TEMPLATES
    from core.db import get_engine
    import datetime
    engine = get_engine()
    with engine.connect() as conn:
        ctx = _get_full_context(user_id, conn)
    tmpl = select_template(ctx)
    return {
        "user_id": user_id,
        "selected_template": tmpl,
        "template_info": TEMPLATES[tmpl],
        "todays_session": get_todays_session(tmpl, datetime.date.today().weekday()),
        "reason": {"fitness_level": ctx['fitness_level'], "fitness_goal": ctx['fitness_goal'],
                   "deload": ctx['deload_recommended']}
    }

@router.get("/{user_id}/readiness-trend")
def readiness_trend(user_id: int):
    from core.domain.progression_engine import analyze_readiness_trend
    from core.db import get_engine
    engine = get_engine()
    with engine.connect() as conn:
        return analyze_readiness_trend(user_id, conn)
