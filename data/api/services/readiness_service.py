from sqlalchemy import text
from core.db import get_engine
import pandas as pd
from datetime import date

engine = get_engine()

def get_readiness(user_id: int) -> dict | None:
    with engine.connect() as conn:
        # Fatigue scores
        fs = conn.execute(text("""
            SELECT user_id, date, readiness_score, recovery_score,
                   fatigue_score, acwr, training_zone,
                   deload_recommended, notes
            FROM fatigue_scores
            WHERE user_id = :uid
            ORDER BY date DESC LIMIT 1
        """), {"uid": user_id}).fetchone()

        if not fs:
            return None

        # Recovery — senaste loggen oavsett datum
        rl = conn.execute(text("""
            SELECT sleep_hours, energy_level, stress_level
            FROM recovery_logs
            WHERE user_id = :uid
            ORDER BY date DESC LIMIT 1
        """), {"uid": user_id}).fetchone()

        # Model predictions — senaste
        mp = conn.execute(text("""
            SELECT recommended_intensity
            FROM model_predictions
            WHERE user_id = :uid
            ORDER BY date DESC LIMIT 1
        """), {"uid": user_id}).fetchone()

        readiness = float(fs[2])
        intensity = mp[0] if mp else "moderate"

        if readiness >= 80:
            msg = "Kroppen är redo — kör hårt idag!"
        elif readiness >= 65:
            msg = "Bra status — träna normalt."
        elif readiness >= 50:
            msg = "Måttlig readiness — välj lättare träning."
        elif readiness >= 35:
            msg = "Låg readiness — aktiv vila rekommenderas."
        else:
            msg = "Kritiskt låg readiness — vila idag."

        return {
            "user_id": fs[0],
            "date": fs[1],
            "readiness_score": float(fs[2]),
            "recovery_score": float(fs[3]),
            "fatigue_score": float(fs[4]),
            "acwr": float(fs[5]),
            "training_zone": fs[6],
            "deload_recommended": bool(fs[7]),
            "sleep_hours": float(rl[0]) if rl and rl[0] else None,
            "energy_level": float(rl[1]) if rl and rl[1] else None,
            "stress_level": float(rl[2]) if rl and rl[2] else None,
            "recommended_intensity": intensity,
            "status_message": msg,
        }


def get_fatigue(user_id: int) -> dict | None:
    with engine.connect() as conn:
        row = conn.execute(text("""
            SELECT user_id, date, acute_load, chronic_load, acwr,
                   training_zone, fatigue_score, deload_recommended, notes
            FROM fatigue_scores
            WHERE user_id = :uid
            ORDER BY date DESC LIMIT 1
        """), {"uid": user_id}).fetchone()

        if not row:
            return None

        return {
            "user_id": row[0], "date": row[1],
            "acute_load": float(row[2]), "chronic_load": float(row[3]),
            "acwr": float(row[4]), "training_zone": row[5],
            "fatigue_score": float(row[6]),
            "deload_recommended": bool(row[7]), "notes": row[8],
        }


def get_volume(user_id: int) -> list:
    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT user_id, week_label, sessions,
                   total_volume_kg, avg_rpe, total_sets
            FROM mv_user_weekly_volume
            WHERE user_id = :uid
            ORDER BY week_label DESC LIMIT 12
        """), {"uid": user_id}).fetchall()

        return [
            {
                "user_id": r[0], "week_label": r[1],
                "sessions": int(r[2]),
                "total_volume_kg": float(r[3]),
                "avg_rpe": float(r[4]) if r[4] else None,
                "total_sets": int(r[5]),
            }
            for r in rows
        ]


def get_features(user_id: int) -> dict | None:
    with engine.connect() as conn:
        row = conn.execute(text("""
            SELECT * FROM user_daily_features
            WHERE user_id = :uid
            ORDER BY date DESC LIMIT 1
        """), {"uid": user_id}).fetchone()

        if not row:
            return None

        keys = [
            "id", "user_id", "date",
            "sleep_hours_7d_avg", "sleep_quality_7d_avg",
            "sleep_consistency_score", "volume_7d", "volume_28d_avg",
            "sessions_7d", "avg_rpe_7d", "acwr", "training_zone",
            "recovery_score", "readiness_score", "stress_7d_avg",
            "energy_7d_avg", "hrv_7d_avg", "resting_hr_7d_avg",
            "weight_trend", "body_fat_trend", "calories_7d_avg",
            "protein_7d_avg", "calorie_target_adherence",
            "protein_target_adherence", "days_since_last_workout",
            "streak_current", "workout_consistency_30d", "calculated_at"
        ]
        return {k: (float(v) if hasattr(v, '__float__') and v is not None else v)
                for k, v in zip(keys, row)}
