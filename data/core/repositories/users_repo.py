from sqlalchemy import text
from core.db import engine

def get_all_users():
    with engine.connect() as conn:
        return conn.execute(text(
            "SELECT id, name, fitness_level, fitness_goal, role FROM users"
        )).fetchall()

def get_users_by_role(role: str):
    with engine.connect() as conn:
        return conn.execute(text(
            "SELECT id, name, fitness_level, fitness_goal, role FROM users WHERE role = :role"
        ), {"role": role}).fetchall()

def get_pts():
    return get_users_by_role("pt")

def get_regular_users():
    return get_users_by_role("user")

def get_admins():
    return get_users_by_role("admin")

def get_user_by_id(user_id: int):
    with engine.connect() as conn:
        return conn.execute(text(
            "SELECT id, name, fitness_level, fitness_goal, role FROM users WHERE id = :uid"
        ), {"uid": user_id}).fetchone()
