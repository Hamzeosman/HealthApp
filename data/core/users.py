from sqlalchemy import text
from core.db import engine

def get_all_users():
    """Single source of truth for user fetching."""
    with engine.connect() as conn:
        result = conn.execute(text(
            "SELECT id, name, fitness_level, fitness_goal FROM users"
        ))
        return result.fetchall()
