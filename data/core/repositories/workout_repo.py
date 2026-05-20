from sqlalchemy import text
from core.db import engine
from datetime import datetime, timedelta

def get_weekly_load(user_id: int, week_offset: int = 0):
    end_date = datetime.now() - timedelta(weeks=week_offset)
    start_date = end_date - timedelta(days=7)
    with engine.connect() as conn:
        return conn.execute(text("""
            SELECT
                COALESCE(SUM(we.sets * we.reps * COALESCE(we.weight_kg, 0)), 0),
                COALESCE(AVG(we.rpe), 7),
                COALESCE(SUM(we.sets), 0),
                COUNT(DISTINCT ws.id)
            FROM workout_exercises we
            JOIN workout_sessions ws ON we.session_id = ws.id
            WHERE ws.user_id = :uid
            AND ws.date >= :start AND ws.date < :end
        """), {"uid": user_id, "start": start_date.date(), "end": end_date.date()}).fetchone()

def get_weekly_volume(user_id: int, week_offset: int = 0):
    end_date = datetime.now() - timedelta(weeks=week_offset)
    start_date = end_date - timedelta(days=7)
    with engine.connect() as conn:
        return conn.execute(text("""
            SELECT bp.name, SUM(we.sets), SUM(we.sets * we.reps * COALESCE(we.weight_kg,0)), AVG(we.rpe), COUNT(DISTINCT ws.id)
            FROM workout_exercises we
            JOIN workout_sessions ws ON we.session_id = ws.id
            JOIN exercises e ON we.exercise_id = e.id
            JOIN body_parts bp ON e.body_part_id = bp.id
            WHERE ws.user_id = :uid AND ws.date >= :start AND ws.date < :end
            GROUP BY bp.name ORDER BY 2 DESC
        """), {"uid": user_id, "start": start_date.date(), "end": end_date.date()}).fetchall()
