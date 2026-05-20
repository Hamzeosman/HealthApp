from sqlalchemy import text
from core.db import engine

def save_insight(user_id: int, title: str, content: str, insight_type: str):
    with engine.begin() as conn:
        existing = conn.execute(text(
            "SELECT id FROM ai_insights WHERE user_id = :uid AND title = :title"
        ), {"uid": user_id, "title": title}).fetchone()
        if not existing:
            conn.execute(text("""
                INSERT INTO ai_insights (user_id, title, content, insight_type)
                VALUES (:uid, :title, :content, :itype)
            """), {"uid": user_id, "title": title, "content": content, "itype": insight_type})
