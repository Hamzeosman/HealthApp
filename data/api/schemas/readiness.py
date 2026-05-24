from pydantic import BaseModel
from typing import Optional
from datetime import date

class ReadinessResponse(BaseModel):
    user_id: int
    date: date
    readiness_score: float
    recovery_score: float
    fatigue_score: float
    acwr: float
    training_zone: str
    deload_recommended: bool
    sleep_hours: Optional[float]
    energy_level: Optional[float]
    stress_level: Optional[float]
    recommended_intensity: str
    status_message: str

class FatigueResponse(BaseModel):
    user_id: int
    date: date
    acute_load: float
    chronic_load: float
    acwr: float
    training_zone: str
    fatigue_score: float
    deload_recommended: bool
    notes: Optional[str]

class VolumeResponse(BaseModel):
    user_id: int
    week_label: str
    sessions: int
    total_volume_kg: float
    avg_rpe: Optional[float]
    total_sets: int
