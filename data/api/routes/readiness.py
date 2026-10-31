from fastapi import APIRouter, HTTPException
from api.services.readiness_service import (
    get_readiness, get_fatigue, get_volume, get_features
)

router = APIRouter(prefix="/users", tags=["readiness"])

@router.get("/{user_id}/readiness")
def readiness(user_id: int):
    result = get_readiness(user_id)
    if not result:
        raise HTTPException(status_code=404, detail="No readiness data found")
    return result

@router.get("/{user_id}/fatigue")
def fatigue(user_id: int):
    result = get_fatigue(user_id)
    if not result:
        raise HTTPException(status_code=404, detail="No fatigue data found")
    return result

@router.get("/{user_id}/volume")
def volume(user_id: int):
    return get_volume(user_id)

@router.get("/{user_id}/features")
def features(user_id: int):
    result = get_features(user_id)
    if not result:
        raise HTTPException(status_code=404, detail="No feature data found")
    return result

@router.get("/{user_id}/readiness-history")
def readiness_history(user_id: int):
    from sqlalchemy import text
    from core.db import get_engine
    engine = get_engine()
    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT date, readiness_score, recovery_score,
                   fatigue_score, acwr, training_zone, deload_recommended
            FROM fatigue_scores
            WHERE user_id = :uid
            ORDER BY date ASC
        """), {"uid": user_id}).fetchall()
        return [dict(zip([
            "date","readiness_score","recovery_score",
            "fatigue_score","acwr","training_zone","deload_recommended"
        ], r)) for r in rows]

@router.get("/{user_id}/fatigue-scores")
def fatigue_scores(user_id: int):
    """Alias för /fatigue — matchar C# IPythonApiClient.GetFatigueScoreAsync"""
    result = get_fatigue(user_id)
    if not result:
        raise HTTPException(status_code=404, detail="No fatigue data found")
    return result
