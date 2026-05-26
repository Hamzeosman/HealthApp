from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    fitness_level: Optional[str]
    fitness_goal: Optional[str]
    experience_level: Optional[str]
    age: Optional[int]
    weight_kg: Optional[float]
    height_cm: Optional[float]

    class Config:
        from_attributes = True
