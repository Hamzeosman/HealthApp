from pydantic import BaseModel
from datetime import date

class ReadinessResult(BaseModel):
    user_id: int
    recovery_score: float
    acwr: float
    acwr_status: str
    fatigue: int
    fatigue_ratio: float
    readiness_score: float
    readiness_status: str
    deload_recommended: bool

class WeeklyVolume(BaseModel):
    muscle_group: str
    total_sets: int
    total_volume_kg: float
    avg_rpe: float
    sessions: int

class UserMetrics(BaseModel):
    user_id: int
    date: date
    recovery_score: float
    fatigue_score: float
    weekly_volume_kg: float
    weekly_sets: int
    acwr: float
    readiness_status: str
