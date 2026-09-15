"""
anomaly_detection_pipeline.py
Flaggar ovanliga värden och mönster i användardata.
Sparar anomalier som notifikationer och i audit_log.

Detekterar:
1. Träningsvolym mer än 2x normalt (överträning)
2. Sömn under 4h tre dagar i rad
3. RPE som plötsligt hoppar (>3 enheter)
4. Ingen träning på 14+ dagar (dropout-risk)
5. Stress > 8 tre dagar i rad
6. Vikt förändring > 2kg på en vecka
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import logging
from datetime import datetime, date, timedelta

load_dotenv(os.path.join(os.path.dirname(__file__), "../.env"))
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
log = logging.getLogger(__name__)
engine = create_engine(os.getenv("DATABASE_URL"))


# ── Anomali-detektorer ────────────────────────────────────────

def detect_overtraining(conn, user_id: int, user_name: str) -> list[dict]:
    """Träningsvolym mer än 2x normalt."""
    result = conn.execute(text("""
        WITH weekly AS (
            SELECT
                DATE_TRUNC('week', ws.date) AS week,
                SUM(we.sets * we.reps * COALESCE(we.weight_kg, 0)) AS volume
            FROM workout_sessions ws
            JOIN workout_exercises we ON ws.id = we.session_id
            WHERE ws.user_id = :uid
            AND ws.date >= CURRENT_DATE - INTERVAL '8 weeks'
            GROUP BY 1
        ),
        stats AS (
            SELECT
                AVG(volume) AS avg_vol,
                STDDEV(volume) AS std_vol
            FROM weekly
            WHERE week < DATE_TRUNC('week', CURRENT_DATE)
        )
        SELECT w.volume, s.avg_vol, s.std_vol
        FROM weekly w, stats s
        WHERE w.week = DATE_TRUNC('week', CURRENT_DATE)
        AND s.avg_vol > 0
        AND w.volume > s.avg_vol * 2
    """), {"uid": user_id}).fetchone()

    if result:
        return [{
            "type": "overtraining",
            "severity": "HIGH",
            "user_id": user_id,
            "message": f"{user_name}: Träningsvolym {result[0]:.0f}kg denna vecka är mer än 2x normalt ({result[1]:.0f}kg). Risk för överträning.",
            "notification_type": "recovery_alert"
        }]
    return []


def detect_poor_sleep_streak(conn, user_id: int, user_name: str) -> list[dict]:
    """Sömn under 4h tre dagar i rad."""
    result = conn.execute(text("""
        SELECT COUNT(*) FROM recovery_logs
        WHERE user_id = :uid
        AND date >= CURRENT_DATE - INTERVAL '3 days'
        AND sleep_hours < 4
        AND sleep_hours IS NOT NULL
    """), {"uid": user_id}).scalar() or 0

    if result >= 3:
        return [{
            "type": "poor_sleep_streak",
            "severity": "HIGH",
            "user_id": user_id,
            "message": f"{user_name}: Sovit under 4h tre dagar i rad. Prioritera sömn för återhämtning.",
            "notification_type": "recovery_alert"
        }]
    return []


def detect_rpe_spike(conn, user_id: int, user_name: str) -> list[dict]:
    """RPE som plötsligt hoppar med mer än 3 enheter."""
    result = conn.execute(text("""
        WITH recent AS (
            SELECT
                ws.date,
                AVG(we.rpe) AS avg_rpe
            FROM workout_sessions ws
            JOIN workout_exercises we ON ws.id = we.session_id
            WHERE ws.user_id = :uid
            AND ws.date >= CURRENT_DATE - INTERVAL '14 days'
            AND we.rpe IS NOT NULL
            GROUP BY ws.date
            ORDER BY ws.date DESC
        ),
        latest AS (SELECT avg_rpe FROM recent LIMIT 1),
        baseline AS (SELECT AVG(avg_rpe) AS avg FROM recent OFFSET 1)
        SELECT l.avg_rpe, b.avg
        FROM latest l, baseline b
        WHERE b.avg > 0
        AND l.avg_rpe - b.avg > 3
    """), {"uid": user_id}).fetchone()

    if result:
        return [{
            "type": "rpe_spike",
            "severity": "MEDIUM",
            "user_id": user_id,
            "message": f"{user_name}: RPE {result[0]:.1f} idag vs snitt {result[1]:.1f} — ökning på {result[0]-result[1]:.1f} enheter. Kontrollera återhämtning.",
            "notification_type": "recovery_alert"
        }]
    return []


def detect_dropout_risk(conn, user_id: int, user_name: str) -> list[dict]:
    """Ingen träning på 14+ dagar trots tidigare aktivitet."""
    result = conn.execute(text("""
        SELECT
            MAX(date) AS last_workout,
            COUNT(*) AS total_sessions
        FROM workout_sessions
        WHERE user_id = :uid
    """), {"uid": user_id}).fetchone()

    if not result or not result[0]:
        return []

    days_since = (date.today() - result[0]).days
    total = result[1]

    if days_since >= 14 and total >= 5:
        return [{
            "type": "dropout_risk",
            "severity": "MEDIUM",
            "user_id": user_id,
            "message": f"{user_name}: Ingen träning på {days_since} dagar. Dropout-risk — skicka påminnelse.",
            "notification_type": "workout_reminder"
        }]
    return []


def detect_high_stress_streak(conn, user_id: int, user_name: str) -> list[dict]:
    """Stress > 8 tre dagar i rad."""
    result = conn.execute(text("""
        SELECT COUNT(*) FROM recovery_logs
        WHERE user_id = :uid
        AND date >= CURRENT_DATE - INTERVAL '3 days'
        AND stress_level > 8
        AND stress_level IS NOT NULL
    """), {"uid": user_id}).scalar() or 0

    if result >= 3:
        return [{
            "type": "high_stress_streak",
            "severity": "MEDIUM",
            "user_id": user_id,
            "message": f"{user_name}: Stressnivå över 8 tre dagar i rad. Överväg deload eller vila.",
            "notification_type": "recovery_alert"
        }]
    return []


def detect_weight_spike(conn, user_id: int, user_name: str) -> list[dict]:
    """Viktutveckling mer än 2kg på en vecka."""
    result = conn.execute(text("""
        SELECT
            MAX(CASE WHEN measured_at >= CURRENT_DATE - INTERVAL '7 days' THEN weight_kg END) AS recent,
            MIN(CASE WHEN measured_at < CURRENT_DATE - INTERVAL '7 days' THEN weight_kg END) AS older
        FROM weight_history
        WHERE user_id = :uid
        AND measured_at >= CURRENT_DATE - INTERVAL '14 days'
    """), {"uid": user_id}).fetchone()

    if result and result[0] and result[1]:
        diff = abs(float(result[0]) - float(result[1]))
        if diff > 2:
            return [{
                "type": "weight_spike",
                "severity": "LOW",
                "user_id": user_id,
                "message": f"{user_name}: Viktutveckling {diff:.1f}kg på en vecka. Kontrollera om det är avsiktligt.",
                "notification_type": "ai_insight"
            }]
    return []


# ── Spara anomalier ───────────────────────────────────────────

def save_anomaly(conn, anomaly: dict) -> None:
    """Sparar anomali som notifikation."""
    # Kolla om samma anomali redan finns idag
    existing = conn.execute(text("""
        SELECT id FROM notifications
        WHERE user_id = :uid
        AND notification_type = :type
        AND DATE(created_at) = CURRENT_DATE
    """), {"uid": anomaly["user_id"], "type": anomaly["notification_type"]}).fetchone()

    if existing:
        return  # Skicka inte dubbletter samma dag

    conn.execute(text("""
        INSERT INTO notifications (user_id, title, message, notification_type, created_at)
        VALUES (:uid, :title, :message, :type, NOW())
    """), {
        "uid": anomaly["user_id"],
        "title": f"Anomali: {anomaly['type']}",
        "message": anomaly["message"],
        "type": anomaly["notification_type"]
    })


# ── Main ──────────────────────────────────────────────────────

def run_anomaly_detection(user_id=None):
    log.info("=" * 55)
    log.info("ANOMALI-DETEKTERING — startar")
    log.info("=" * 55)

    with engine.connect() as conn:
        if user_id:
            users = conn.execute(text(
                "SELECT id, name FROM users WHERE id = :uid"
            ), {"uid": user_id}).fetchall()
        else:
            users = conn.execute(text(
                "SELECT id, name FROM users"
            )).fetchall()

        total_anomalies = 0

        for (uid, name) in users:
            anomalies = []

            anomalies += detect_overtraining(conn, uid, name)
            anomalies += detect_poor_sleep_streak(conn, uid, name)
            anomalies += detect_rpe_spike(conn, uid, name)
            anomalies += detect_dropout_risk(conn, uid, name)
            anomalies += detect_high_stress_streak(conn, uid, name)
            anomalies += detect_weight_spike(conn, uid, name)

            if anomalies:
                log.info(f"\n{name} (ID: {uid}) — {len(anomalies)} anomalier:")
                for a in anomalies:
                    emoji = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(a["severity"], "?")
                    log.info(f"  {emoji} {a['message']}")
                    save_anomaly(conn, a)
                total_anomalies += len(anomalies)
            else:
                log.info(f"  ✓ {name} — inga anomalier")

        conn.commit()

    log.info(f"\n{'=' * 55}")
    log.info(f"Totalt: {total_anomalies} anomalier detekterade")
    log.info("=" * 55)


if __name__ == "__main__":
    run_anomaly_detection()