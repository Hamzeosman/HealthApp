"""
data_quality_pipeline.py
Kör varje natt och validerar att datan är korrekt.
Sparar rapport i audit_log och skickar notifikation till admin vid problem.

Kontroller:
- NULL-värden där det inte ska vara
- Dubbletter
- Värden utanför rimliga gränser
- Orphaned records (FK utan förälder)
- Master data integritet
- Stale data (data som inte uppdaterats på länge)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import logging
from datetime import datetime, date

load_dotenv(os.path.join(os.path.dirname(__file__), "../.env"))
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
log = logging.getLogger(__name__)
engine = create_engine(os.getenv("DATABASE_URL"))


# ── Check-funktioner ──────────────────────────────────────────

def check_null_values(conn) -> list[dict]:
    """Kontrollerar kritiska NOT NULL kolumner."""
    checks = [
        ("exercises", "name", "SELECT COUNT(*) FROM exercises WHERE name IS NULL AND deleted_at IS NULL"),
        ("foods", "name", "SELECT COUNT(*) FROM foods WHERE name IS NULL"),
        ("foods", "calories_per_100g", "SELECT COUNT(*) FROM foods WHERE calories_per_100g IS NULL"),
        ("workout_exercises", "session_id", "SELECT COUNT(*) FROM workout_exercises WHERE session_id IS NULL"),
        ("workout_exercises", "exercise_id", "SELECT COUNT(*) FROM workout_exercises WHERE exercise_id IS NULL"),
        ("recovery_logs", "user_id", "SELECT COUNT(*) FROM recovery_logs WHERE user_id IS NULL"),
        ("recovery_logs", "date", "SELECT COUNT(*) FROM recovery_logs WHERE date IS NULL"),
        ("meal_logs", "user_id", "SELECT COUNT(*) FROM meal_logs WHERE user_id IS NULL"),
    ]

    issues = []
    for table, column, query in checks:
        count = conn.execute(text(query)).scalar() or 0
        if count > 0:
            issues.append({
                "check": "null_values",
                "table": table,
                "column": column,
                "count": count,
                "severity": "HIGH",
                "message": f"{count} NULL-värden i {table}.{column}"
            })
    return issues


def check_duplicates(conn) -> list[dict]:
    """Kontrollerar UNIQUE constraints."""
    checks = [
        ("recovery_logs", "user_id + date", """
            SELECT COUNT(*) FROM (
                SELECT user_id, date, COUNT(*) c
                FROM recovery_logs
                GROUP BY user_id, date
                HAVING COUNT(*) > 1
            ) t
        """),
        ("biometrics", "user_id + date", """
            SELECT COUNT(*) FROM (
                SELECT user_id, date, COUNT(*) c
                FROM biometrics
                GROUP BY user_id, date
                HAVING COUNT(*) > 1
            ) t
        """),
        ("foods", "name", """
            SELECT COUNT(*) FROM (
                SELECT name, COUNT(*) c
                FROM foods
                GROUP BY name
                HAVING COUNT(*) > 1
            ) t
        """),
        ("personal_records", "user_id + exercise_id + date", """
            SELECT COUNT(*) FROM (
                SELECT user_id, exercise_id, date, COUNT(*) c
                FROM personal_records
                GROUP BY user_id, exercise_id, date
                HAVING COUNT(*) > 1
            ) t
        """),
    ]

    issues = []
    for table, columns, query in checks:
        count = conn.execute(text(query)).scalar() or 0
        if count > 0:
            issues.append({
                "check": "duplicates",
                "table": table,
                "column": columns,
                "count": count,
                "severity": "HIGH",
                "message": f"{count} dubbletter i {table} ({columns})"
            })
    return issues


def check_out_of_range(conn) -> list[dict]:
    """Kontrollerar värden utanför rimliga gränser."""
    checks = [
        ("workout_exercises", "rpe", "SELECT COUNT(*) FROM workout_exercises WHERE rpe IS NOT NULL AND (rpe < 1 OR rpe > 10)"),
        ("workout_exercises", "sets", "SELECT COUNT(*) FROM workout_exercises WHERE sets IS NOT NULL AND (sets < 1 OR sets > 20)"),
        ("workout_exercises", "weight_kg", "SELECT COUNT(*) FROM workout_exercises WHERE weight_kg IS NOT NULL AND weight_kg < 0"),
        ("recovery_logs", "sleep_hours", "SELECT COUNT(*) FROM recovery_logs WHERE sleep_hours IS NOT NULL AND (sleep_hours < 0 OR sleep_hours > 16)"),
        ("recovery_logs", "energy_level", "SELECT COUNT(*) FROM recovery_logs WHERE energy_level IS NOT NULL AND (energy_level < 1 OR energy_level > 10)"),
        ("foods", "calories_per_100g", "SELECT COUNT(*) FROM foods WHERE calories_per_100g IS NOT NULL AND (calories_per_100g < 0 OR calories_per_100g > 900)"),
        ("users", "weight_kg", "SELECT COUNT(*) FROM users WHERE weight_kg IS NOT NULL AND (weight_kg < 20 OR weight_kg > 400)"),
    ]

    issues = []
    for table, column, query in checks:
        count = conn.execute(text(query)).scalar() or 0
        if count > 0:
            issues.append({
                "check": "out_of_range",
                "table": table,
                "column": column,
                "count": count,
                "severity": "MEDIUM",
                "message": f"{count} värden utanför giltigt intervall i {table}.{column}"
            })
    return issues


def check_orphaned_records(conn) -> list[dict]:
    """Kontrollerar FK-relationer — poster utan förälder."""
    checks = [
        ("workout_exercises", "session_id → workout_sessions", """
            SELECT COUNT(*) FROM workout_exercises we
            LEFT JOIN workout_sessions ws ON we.session_id = ws.id
            WHERE ws.id IS NULL AND we.session_id IS NOT NULL
        """),
        ("workout_exercises", "exercise_id → exercises", """
            SELECT COUNT(*) FROM workout_exercises we
            LEFT JOIN exercises e ON we.exercise_id = e.id
            WHERE e.id IS NULL AND we.exercise_id IS NOT NULL
        """),
        ("meal_logs", "food_id → foods", """
            SELECT COUNT(*) FROM meal_logs ml
            LEFT JOIN foods f ON ml.food_id = f.id
            WHERE f.id IS NULL AND ml.food_id IS NOT NULL
        """),
        ("recommendations", "exercise_id → exercises", """
            SELECT COUNT(*) FROM recommendations r
            LEFT JOIN exercises e ON r.exercise_id = e.id
            WHERE e.id IS NULL AND r.exercise_id IS NOT NULL
        """),
    ]

    issues = []
    for table, relation, query in checks:
        count = conn.execute(text(query)).scalar() or 0
        if count > 0:
            issues.append({
                "check": "orphaned_records",
                "table": table,
                "column": relation,
                "count": count,
                "severity": "HIGH",
                "message": f"{count} orphaned records i {table} ({relation})"
            })
    return issues


def check_master_data(conn) -> list[dict]:
    """Kontrollerar att master data är komplett."""
    issues = []

    # Övningar utan primary_muscle
    missing_muscle = conn.execute(text("""
        SELECT COUNT(*) FROM exercises
        WHERE primary_muscle IS NULL AND deleted_at IS NULL
    """)).scalar() or 0
    if missing_muscle > 0:
        issues.append({
            "check": "master_data",
            "table": "exercises",
            "column": "primary_muscle",
            "count": missing_muscle,
            "severity": "LOW",
            "message": f"{missing_muscle} övningar saknar primary_muscle"
        })

    # Exercises utan body_part
    missing_bp = conn.execute(text("""
        SELECT COUNT(*) FROM exercises
        WHERE body_part_id IS NULL AND deleted_at IS NULL
    """)).scalar() or 0
    if missing_bp > 0:
        issues.append({
            "check": "master_data",
            "table": "exercises",
            "column": "body_part_id",
            "count": missing_bp,
            "severity": "MEDIUM",
            "message": f"{missing_bp} övningar saknar body_part"
        })

    # Exercises med status != published
    unpublished = conn.execute(text("""
        SELECT COUNT(*) FROM exercises
        WHERE status != 'published' AND deleted_at IS NULL
    """)).scalar() or 0
    if unpublished > 0:
        issues.append({
            "check": "master_data",
            "table": "exercises",
            "column": "status",
            "count": unpublished,
            "severity": "LOW",
            "message": f"{unpublished} övningar är inte published"
        })

    return issues


def check_stale_data(conn) -> list[dict]:
    """Kontrollerar data som inte uppdaterats på länge."""
    issues = []

    # Users som inte loggat träning på 30+ dagar
    inactive = conn.execute(text("""
        SELECT COUNT(DISTINCT u.id)
        FROM users u
        LEFT JOIN workout_sessions ws ON u.id = ws.user_id
        WHERE u.role = 'user'
        AND (ws.date IS NULL OR ws.date < CURRENT_DATE - INTERVAL '30 days')
    """)).scalar() or 0

    if inactive > 0:
        issues.append({
            "check": "stale_data",
            "table": "workout_sessions",
            "column": "date",
            "count": inactive,
            "severity": "INFO",
            "message": f"{inactive} users har inte tränat på 30+ dagar"
        })

    return issues


# ── Rapport och notifikation ──────────────────────────────────

def save_report(conn, all_issues: list[dict]) -> None:
    """Sparar rapport i audit_log."""
    high   = [i for i in all_issues if i["severity"] == "HIGH"]
    medium = [i for i in all_issues if i["severity"] == "MEDIUM"]
    low    = [i for i in all_issues if i["severity"] in ("LOW", "INFO")]

    summary = (
        f"Data Quality Report {date.today()} — "
        f"HIGH: {len(high)}, MEDIUM: {len(medium)}, LOW: {len(low)}"
    )

    import json
    conn.execute(text("""
        INSERT INTO audit_log (table_name, action, old_value, changed_at)
        VALUES ('data_quality_pipeline', 'INSERT', :report, NOW())
    """), {"report": json.dumps({
        "summary": summary,
        "issues": all_issues,
        "total": len(all_issues)
    })})

    log.info(f"\n{summary}")


def notify_admin(conn, high_issues: list[dict]) -> None:
    """Skickar notifikation till admin vid HIGH-problem."""
    if not high_issues:
        return

    admin = conn.execute(text(
        "SELECT id FROM users WHERE role = 'admin' LIMIT 1"
    )).fetchone()
    if not admin:
        return

    message = f"Data Quality Alert: {len(high_issues)} kritiska problem hittades. Kontrollera audit_log."
    conn.execute(text("""
        INSERT INTO notifications (user_id, type, message, created_at)
        VALUES (:uid, 'system_alert', :msg, NOW())
        ON CONFLICT DO NOTHING
    """), {"uid": admin[0], "msg": message})


# ── Main ──────────────────────────────────────────────────────

def run_data_quality():
    log.info("=" * 55)
    log.info("DATA QUALITY PIPELINE — startar")
    log.info("=" * 55)

    with engine.connect() as conn:
        all_issues = []

        log.info("\n1. Kontrollerar NULL-värden...")
        null_issues = check_null_values(conn)
        all_issues.extend(null_issues)
        log.info(f"   {len(null_issues)} problem hittade")

        log.info("2. Kontrollerar dubbletter...")
        dup_issues = check_duplicates(conn)
        all_issues.extend(dup_issues)
        log.info(f"   {len(dup_issues)} problem hittade")

        log.info("3. Kontrollerar värden utanför intervall...")
        range_issues = check_out_of_range(conn)
        all_issues.extend(range_issues)
        log.info(f"   {len(range_issues)} problem hittade")

        log.info("4. Kontrollerar orphaned records...")
        orphan_issues = check_orphaned_records(conn)
        all_issues.extend(orphan_issues)
        log.info(f"   {len(orphan_issues)} problem hittade")

        log.info("5. Kontrollerar master data...")
        master_issues = check_master_data(conn)
        all_issues.extend(master_issues)
        log.info(f"   {len(master_issues)} problem hittade")

        log.info("6. Kontrollerar stale data...")
        stale_issues = check_stale_data(conn)
        all_issues.extend(stale_issues)
        log.info(f"   {len(stale_issues)} problem hittade")

        # Summering
        high   = [i for i in all_issues if i["severity"] == "HIGH"]
        medium = [i for i in all_issues if i["severity"] == "MEDIUM"]
        low    = [i for i in all_issues if i["severity"] in ("LOW", "INFO")]

        # Quality score — varje HIGH räknas som 2 poäng, MEDIUM som 1
        total_checks = 6
        penalty = len(high) * 2 + len(medium) * 1
        quality_score = max(0, round(100 - (penalty / (total_checks * 2)) * 100, 1))

        log.info(f"\n{'=' * 55}")
        log.info(f"DATA QUALITY SCORE: {quality_score}%")
        log.info(f"{'=' * 55}")
        log.info(f"  NULL checks      {'✅' if not any(i['check']=='null_values' for i in all_issues) else '⚠️'}")
        log.info(f"  Duplicates       {'✅' if not any(i['check']=='duplicates' for i in all_issues) else '⚠️'}")
        log.info(f"  Range checks     {'✅' if not any(i['check']=='out_of_range' for i in all_issues) else '⚠️'} {len([i for i in all_issues if i['check']=='out_of_range'])} issues")
        log.info(f"  Foreign keys     {'✅' if not any(i['check']=='orphaned_records' for i in all_issues) else '⚠️'}")
        log.info(f"  Master data      {'✅' if not any(i['check']=='master_data' for i in all_issues) else '⚠️'}")
        log.info(f"  User activity    {'✅' if not any(i['check']=='stale_data' for i in all_issues) else 'ℹ️'}")
        log.info(f"\nRESULTAT:")
        log.info(f"  🔴 HIGH:   {len(high)}")
        log.info(f"  🟡 MEDIUM: {len(medium)}")
        log.info(f"  🟢 LOW:    {len(low)}")

        if all_issues:
            log.info(f"\nPROBLEM:")
            for issue in all_issues:
                emoji = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢", "INFO": "ℹ️"}.get(issue["severity"], "?")
                log.info(f"  {emoji} {issue['message']}")

        save_report(conn, all_issues)
        notify_admin(conn, high)
        conn.commit()

        log.info(f"\n✅ Data quality rapport sparad i audit_log")
        log.info("=" * 55)

        return all_issues


if __name__ == "__main__":
    issues = run_data_quality()