from sqlalchemy import text
from core.db import engine
from datetime import datetime, timedelta, date as date_type

def get_last_training_date(user_id: int):
    """Hamtar senaste traningsdatum for en user."""
    with engine.connect() as conn:
        result = conn.execute(text(
            "SELECT MAX(date) FROM workout_sessions WHERE user_id = :uid"
        ), {"uid": user_id}).scalar()
        return result

def get_weekly_load(user_id: int, week_offset: int = 0):
    """
    Hamtar training load relativt senaste traningsdatum.
    Anvander senaste datum som referens istallet for idag.
    """
    with engine.connect() as conn:
        last_date = conn.execute(text(
            "SELECT MAX(date) FROM workout_sessions WHERE user_id = :uid"
        ), {"uid": user_id}).scalar()

        if last_date is None:
            return (0, 7, 0, 0)

        if isinstance(last_date, date_type):
            last_date = datetime.combine(last_date, datetime.min.time())

        end_date = last_date - timedelta(weeks=week_offset)
        start_date = end_date - timedelta(days=7)

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
        """), {"uid": user_id,
               "start": start_date.date(),
               "end": end_date.date()}).fetchone()

def get_weekly_volume(user_id: int, week_offset: int = 0):
    """Hamtar volym per muskelgrupp relativt senaste traningsdatum."""
    with engine.connect() as conn:
        last_date = conn.execute(text(
            "SELECT MAX(date) FROM workout_sessions WHERE user_id = :uid"
        ), {"uid": user_id}).scalar()

        if last_date is None:
            return []

        if isinstance(last_date, date_type):
            last_date = datetime.combine(last_date, datetime.min.time())

        end_date = last_date - timedelta(weeks=week_offset)
        start_date = end_date - timedelta(days=7)

        return conn.execute(text("""
            SELECT bp.name, SUM(we.sets),
                   SUM(we.sets * we.reps * COALESCE(we.weight_kg, 0)),
                   AVG(we.rpe), COUNT(DISTINCT ws.id)
            FROM workout_exercises we
            JOIN workout_sessions ws ON we.session_id = ws.id
            JOIN exercises e ON we.exercise_id = e.id
            JOIN body_parts bp ON e.body_part_id = bp.id
            WHERE ws.user_id = :uid
            AND ws.date >= :start AND ws.date < :end
            GROUP BY bp.name ORDER BY 2 DESC
        """), {"uid": user_id,
               "start": start_date.date(),
               "end": end_date.date()}).fetchall()

def get_personal_records(user_id: int):
    with engine.connect() as conn:
        return conn.execute(text("""
            SELECT e.name, pr.weight_kg, pr.reps, pr.date
            FROM personal_records pr
            JOIN exercises e ON pr.exercise_id = e.id
            WHERE pr.user_id = :uid ORDER BY pr.date DESC
        """), {"uid": user_id}).fetchall()

def get_recent_sessions(user_id: int, limit: int = 10):
    with engine.connect() as conn:
        return conn.execute(text("""
            SELECT id, date, duration_minutes, mood
            FROM workout_sessions
            WHERE user_id = :uid
            ORDER BY date DESC LIMIT :limit
        """), {"uid": user_id, "limit": limit}).fetchall()
