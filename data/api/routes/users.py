from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from core.db import get_engine

router = APIRouter(prefix="/users", tags=["users"])
engine = get_engine()

@router.get("/")
def get_all_users():
    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT id, name, email, fitness_level, fitness_goal,
                   experience_level, age, weight_kg, height_cm
            FROM users
            WHERE role = 'user' OR role IS NULL
            ORDER BY name
        """)).fetchall()
        return [dict(zip(
            ["id","name","email","fitness_level","fitness_goal",
             "experience_level","age","weight_kg","height_cm"], r
        )) for r in rows]

@router.get("/{user_id}")
def get_user(user_id: int):
    with engine.connect() as conn:
        row = conn.execute(text("""
            SELECT id, name, email, fitness_level, fitness_goal,
                   experience_level, age, weight_kg, height_cm
            FROM users WHERE id = :uid
        """), {"uid": user_id}).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="User not found")
        return dict(zip(
            ["id","name","email","fitness_level","fitness_goal",
             "experience_level","age","weight_kg","height_cm"], row
        ))
