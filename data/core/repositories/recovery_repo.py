from sqlalchemy import text
from core.db import engine
from datetime import datetime, timedelta

def get_recovery_data(user_id: int, days: int = None):
    """
    Hamtar recovery data.
    days=None: senaste 3 posterna oavsett datum.
    days=N: senaste N dagarna.
    """
    with engine.connect() as conn:
        if days is None:
            return conn.execute(text("""
                SELECT
                    AVG(sleep_hours), AVG(energy_level),
                    AVG(stress_level), AVG(sleep_quality)
                FROM (
                    SELECT sleep_hours, energy_level, stress_level, sleep_quality
                    FROM recovery_logs
                    WHERE user_id = :uid
                    ORDER BY date DESC
                    LIMIT 3
                ) latest
            """), {"uid": user_id}).fetchone()
        else:
            since = datetime.now() - timedelta(days=days)
            return conn.execute(text("""
                SELECT
                    AVG(sleep_hours), AVG(energy_level),
                    AVG(stress_level), AVG(sleep_quality)
                FROM recovery_logs
                WHERE user_id = :uid AND date >= :since
            """), {"uid": user_id, "since": since.date()}).fetchone()

def get_recovery_history(user_id: int, days: int = 30):
    since = datetime.now() - timedelta(days=days)
    with engine.connect() as conn:
        return conn.execute(text("""
            SELECT date, sleep_hours, energy_level, stress_level, sleep_quality
            FROM recovery_logs
            WHERE user_id = :uid AND date >= :since
            ORDER BY date ASC
        """), {"uid": user_id, "since": since.date()}).fetchall()
