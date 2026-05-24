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
