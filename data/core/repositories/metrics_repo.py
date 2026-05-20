from sqlalchemy import text
from core.db import engine
from datetime import datetime, timedelta

def save_training_metrics(user_id: int, metrics: dict):
    with engine.begin() as conn:
        today = datetime.now().date()
        existing = conn.execute(text(
            "SELECT id FROM training_metrics WHERE user_id = :uid AND date = :date"
        ), {"uid": user_id, "date": today}).fetchone()
        if not existing:
            conn.execute(text("""
                INSERT INTO training_metrics
                    (user_id, date, recovery_score, fatigue_score, weekly_volume_kg, weekly_sets, acwr, readiness_status)
                VALUES (:uid, :date, :recovery, :fatigue, :volume, :sets, :acwr, :readiness)
            """), {"uid": user_id, "date": today, **metrics})

def get_metrics_history(user_id: int, days: int = 30):
    since = datetime.now() - timedelta(days=days)
    with engine.connect() as conn:
        return conn.execute(text("""
            SELECT date, recovery_score, fatigue_score, acwr, readiness_status
            FROM training_metrics WHERE user_id = :uid AND date >= :since ORDER BY date
        """), {"uid": user_id, "since": since.date()}).fetchall()
