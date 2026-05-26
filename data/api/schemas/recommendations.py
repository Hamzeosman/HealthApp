from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class Warning(BaseModel):
    type: str
    message: str
    severity: str  # low / medium / high / critical

class Recommendation(BaseModel):
    category: str
    action: str
    reason: str
    priority: int  # 1 = highest

class RiskScore(BaseModel):
    injury_risk: float
    dropout_risk: float
    plateau_risk: float
    overtraining_risk: float

class RecommendationResponse(BaseModel):
    user_id: int
    exercise_name: str
    body_part: str
    reason: str
    score: float

class AICoachResponse(BaseModel):
    user_id: int
    user_name: str
    date: date
    readiness_score: float
    recommended_intensity: str
    risk_scores: RiskScore
    warnings: List[Warning]
    recommendations: List[Recommendation]
    coach_message: str
    next_action: str
