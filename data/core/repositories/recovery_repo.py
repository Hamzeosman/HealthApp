from sqlalchemy import text
from core.db import engine
from datetime import datetime, timedelta

def get_recovery_data(user_id: int, days: int = 3):
    since = datetime.now() - timedelta(days=days)
    with engine.connect() as conn:
        return conn.execute(text("""
            SELECT AVG(sleep_hours), AVG(energy_level), AVG(stress_level), AVG(sleep_quality)
            FROM recovery_logs WHERE user_id = :uid AND date >= :since
        """), {"uid": user_id, "since": since.date()}).fetchone()
