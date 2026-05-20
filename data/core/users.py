from sqlalchemy import text
from core.db import engine

def get_all_users():
    """Alla användare."""
    with engine.connect() as conn:
        result = conn.execute(text(
            "SELECT id, name, fitness_level, fitness_goal, role FROM users"
        ))
        return result.fetchall()

def get_users_by_role(role):
    """Hämtar användare per roll: user / pt / admin."""
    with engine.connect() as conn:
        result = conn.execute(text(
            "SELECT id, name, fitness_level, fitness_goal, role FROM users WHERE role = :role"
        ), {"role": role})
        return result.fetchall()

def get_pts():
    return get_users_by_role("pt")

def get_regular_users():
    return get_users_by_role("user")

def get_admins():
    return get_users_by_role("admin")
