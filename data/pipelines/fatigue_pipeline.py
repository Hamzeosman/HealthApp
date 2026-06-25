"""
fatigue_pipeline.py
Beräknar dagliga fatigue_scores + skriver activity_logs för alla users.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pandas as pd
from datetime import date
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "../.env"))
engine = create_engine(os.getenv("DATABASE_URL"))


def calculate_fatigue_for_user(user_id: int, conn) -> dict | None:
    workout_data = pd.read_sql(text("""
        SELECT
            ws.date,
            SUM(we.sets * we.reps * COALESCE(we.weight_kg, 0)) AS volume,
            AVG(we.rpe) AS avg_rpe,
            COUNT(DISTINCT ws.id) AS sessions
        FROM workout_sessions ws
        JOIN workout_exercises we ON ws.id = we.session_id
        WHERE ws.user_id = :uid
          AND ws.date >= (SELECT MAX(date) - INTERVAL '28 days' FROM workout_sessions WHERE user_id = :uid)
        GROUP BY ws.date
        ORDER BY ws.date
    """), conn, params={"uid": user_id})

    recovery_data = pd.read_sql(text("""
        SELECT sleep_hours, sleep_quality, energy_level, stress_level
        FROM recovery_logs
        WHERE user_id = :uid
        ORDER BY date DESC
        LIMIT 7
    """), conn, params={"uid": user_id})

    if workout_data.empty:
        return None

    workout_data['fatigue'] = workout_data['volume'] * workout_data['avg_rpe'].fillna(7)
    recent = workout_data.tail(7)
    acute_load = float(recent['fatigue'].mean()) if not recent.empty else 0.0
    chronic_load = float(workout_data['fatigue'].mean()) if len(workout_data) >= 4 else acute_load
    acwr = round(acute_load / chronic_load, 3) if chronic_load > 0 else 1.0

    if acwr < 0.8:
        training_zone = 'undertraining'
    elif acwr <= 1.3:
        training_zone = 'optimal'
    elif acwr <= 1.5:
        training_zone = 'caution'
    else:
        training_zone = 'danger'

    deload_recommended = bool(acwr > 1.5 or (acwr > 1.3 and acute_load > chronic_load * 1.3))

    if not recovery_data.empty:
        r = recovery_data.iloc[0]
        recovery_score = round(
            float(r['sleep_hours']) / 10 * 35 +
            float(r['energy_level']) / 10 * 30 +
            (10 - float(r['stress_level'])) / 10 * 20 +
            float(r['sleep_quality']) / 10 * 15, 2)
    else:
        recovery_score = 50.0

    fatigue_normalized = min(100.0, (acute_load / max(chronic_load, 1)) * 50)
    fatigue_score = round(max(0.0, 100.0 - fatigue_normalized), 2)
    acwr_norm = max(0.0, min(100.0, (1 - abs(acwr - 1.0)) * 100))
    readiness_score = round(
        0.4 * recovery_score +
        0.3 * acwr_norm +
        0.3 * fatigue_score, 2)

    # FIX: konvertera ALLA värden till Python-natives (ingen np.float64)
    return {
        "user_id": int(user_id),
        "date": date.today(),
        "acute_load": float(round(acute_load, 2)),
        "chronic_load": float(round(chronic_load, 2)),
        "acwr": float(acwr),
        "fatigue_score": float(fatigue_score),
        "recovery_score": float(recovery_score),
        "readiness_score": float(readiness_score),
        "deload_recommended": deload_recommended,
        "training_zone": training_zone,
        "notes": f"Auto-calculated. ACWR={acwr:.2f}, Zone={training_zone}"
    }


def log_activity(conn, user_id, action_type, description,
                 entity_type=None, entity_id=None, metadata=None):
    import json
    conn.execute(text("""
        INSERT INTO activity_logs
            (user_id, action_type, entity_type, entity_id, description, metadata)
        VALUES (:uid, :action, :etype, :eid, :desc, :meta)
    """), {
        "uid": user_id, "action": action_type, "etype": entity_type,
        "eid": entity_id, "desc": description,
        "meta": json.dumps(metadata) if metadata else None
    })


def log_event(conn, user_id, event_type, payload=None):
    import json
    conn.execute(text("""
        INSERT INTO events (user_id, event_type, payload)
        VALUES (:uid, :etype, :payload)
    """), {
        "uid": user_id, "etype": event_type,
        "payload": json.dumps(payload) if payload else None
    })


def run():
    print("=" * 60)
    print("FATIGUE PIPELINE — startar")
    print("=" * 60)

    with engine.connect() as conn:
        users = pd.read_sql(text("""
            SELECT id, name FROM users
            WHERE role = 'user' OR role IS NULL
            ORDER BY id
        """), conn)

        if users.empty:
            print("Inga users hittades.")
            return

        success = 0
        skipped = 0
        errors = 0

        for _, user in users.iterrows():
            uid = int(user['id'])
            name = user['name']

            # FIX: savepoint per user så ett fel inte crashar hela transaktionen
            try:
                conn.execute(text("SAVEPOINT sp_user"))

                result = calculate_fatigue_for_user(uid, conn)

                if result is None:
                    print(f"  ⏭️  {name} — ingen träningsdata")
                    conn.execute(text("RELEASE SAVEPOINT sp_user"))
                    skipped += 1
                    continue

                conn.execute(text("""
                    INSERT INTO fatigue_scores
                        (user_id, date, acute_load, chronic_load, acwr,
                         fatigue_score, recovery_score, readiness_score,
                         deload_recommended, training_zone, notes)
                    VALUES
                        (:user_id, :date, :acute_load, :chronic_load, :acwr,
                         :fatigue_score, :recovery_score, :readiness_score,
                         :deload_recommended, :training_zone, :notes)
                    ON CONFLICT (user_id, date) DO UPDATE SET
                        acute_load = EXCLUDED.acute_load,
                        chronic_load = EXCLUDED.chronic_load,
                        acwr = EXCLUDED.acwr,
                        fatigue_score = EXCLUDED.fatigue_score,
                        recovery_score = EXCLUDED.recovery_score,
                        readiness_score = EXCLUDED.readiness_score,
                        deload_recommended = EXCLUDED.deload_recommended,
                        training_zone = EXCLUDED.training_zone,
                        calculated_at = NOW()
                """), result)

                log_activity(conn, uid, 'insight_generated',
                    f"Fatigue score: {result['readiness_score']:.1f}/100 | "
                    f"Zone: {result['training_zone']} | ACWR: {result['acwr']:.2f}",
                    entity_type='fatigue_scores',
                    metadata={
                        "acwr": result['acwr'],
                        "zone": result['training_zone'],
                        "readiness": result['readiness_score']
                    })

                if result['deload_recommended']:
                    log_event(conn, uid, 'deload_triggered',
                        {"acwr": result['acwr'],
                         "message": "ACWR above 1.5 — deload recommended"})
                    log_activity(conn, uid, 'deload_triggered',
                        f"Deload recommended. ACWR={result['acwr']:.2f}",
                        metadata={"acwr": result['acwr']})

                conn.execute(text("RELEASE SAVEPOINT sp_user"))

                zone_emoji = {
                    'undertraining': '📉', 'optimal': '✅',
                    'caution': '⚠️', 'danger': '🔴'
                }.get(result['training_zone'], '❓')

                print(f"  {zone_emoji} {name} — "
                      f"Readiness: {result['readiness_score']:.1f} | "
                      f"ACWR: {result['acwr']:.2f} | "
                      f"Zone: {result['training_zone']}"
                      + (" 🔔 DELOAD!" if result['deload_recommended'] else ""))
                success += 1

            except Exception as e:
                conn.execute(text("ROLLBACK TO SAVEPOINT sp_user"))
                conn.execute(text("RELEASE SAVEPOINT sp_user"))
                print(f"  ❌ {name} — fel: {e}")
                errors += 1

        conn.commit()

    print("=" * 60)
    print(f"✅ Success: {success} | ⏭️ Skipped: {skipped} | ❌ Errors: {errors}")
    print("=" * 60)


if __name__ == "__main__":
    run()
