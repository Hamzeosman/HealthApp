"""
seed_p1_data.py
Seedar testdata för P1-tabeller: sleep_sessions, workout_schedule,
user_measurements, wearable_sources, wearable_metrics, injuries, activity_logs
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import random
from datetime import date, datetime, timedelta
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "../.env"))
engine = create_engine(os.getenv("DATABASE_URL"))
random.seed(42)


def run():
    print("=" * 60)
    print("SEED P1 DATA — startar")
    print("=" * 60)

    with engine.connect() as conn:
        users = conn.execute(text(
            "SELECT id, name, weight_kg FROM users WHERE role = 'user' OR role IS NULL ORDER BY id"
        )).fetchall()

        if not users:
            print("Inga users hittades.")
            return

        print(f"Seedar för {len(users)} users...")

        # ── SLEEP SESSIONS ───────────────────────────────────────────
        print("\n😴 Seedar sleep_sessions...")
        sleep_count = 0
        for user in users:
            uid = user[0]
            for days_ago in range(90, 0, -1):
                if random.random() < 0.85:
                    d = date.today() - timedelta(days=days_ago)
                    total = random.randint(300, 540)
                    deep = int(total * random.uniform(0.15, 0.25))
                    rem = int(total * random.uniform(0.20, 0.30))
                    light = total - deep - rem
                    score = random.randint(55, 95)
                    latency = random.randint(5, 30)
                    bed_hour = random.randint(21, 23)
                    bed_time = datetime(d.year, d.month, d.day, bed_hour, random.randint(0, 59))
                    wake_time = bed_time + timedelta(minutes=total + latency)
                    conn.execute(text("""
                        INSERT INTO sleep_sessions
                            (user_id, date, bed_time, wake_time, total_sleep_minutes,
                             deep_sleep_minutes, rem_sleep_minutes, light_sleep_minutes,
                             sleep_latency_minutes, sleep_score, sleep_efficiency, source)
                        VALUES (:uid, :date, :bed, :wake, :total, :deep, :rem, :light,
                                :latency, :score, :eff, 'manual')
                        ON CONFLICT DO NOTHING
                    """), {"uid": uid, "date": d, "bed": bed_time, "wake": wake_time,
                           "total": total, "deep": deep, "rem": rem, "light": light,
                           "latency": latency, "score": score,
                           "eff": round(random.uniform(75, 98), 1)})
                    sleep_count += 1
        print(f"  ✅ {sleep_count} sleep sessions")

        # ── WORKOUT SCHEDULE ─────────────────────────────────────────
        print("\n📅 Seedar workout_schedule...")
        schedule_count = 0
        types = ['strength', 'cardio', 'hiit', 'mobility', 'running']
        titles = {
            'strength': ['Push Day', 'Pull Day', 'Leg Day', 'Upper Body', 'Lower Body'],
            'cardio': ['Zone 2 Run', 'Easy Bike', 'Cardio Session'],
            'hiit': ['HIIT Session', 'Tabata', 'Circuit Training'],
            'mobility': ['Yoga & Stretch', 'Mobility Work', 'Active Recovery'],
            'running': ['Easy Run', 'Tempo Run', 'Long Run', 'Intervals']
        }
        for user in users:
            uid = user[0]
            for days_ago in range(60, 0, -3):
                if random.random() < 0.7:
                    d = date.today() - timedelta(days=days_ago)
                    wtype = random.choice(types)
                    status = random.choices(['completed','skipped','cancelled'], weights=[75,15,10])[0]
                    completed_at = datetime(d.year, d.month, d.day, random.randint(6, 20), 0) if status == 'completed' else None
                    conn.execute(text("""
                        INSERT INTO workout_schedule
                            (user_id, planned_date, workout_type, title, status, completed_at)
                        VALUES (:uid, :date, :wtype, :title, :status, :cat)
                        ON CONFLICT DO NOTHING
                    """), {"uid": uid, "date": d, "wtype": wtype,
                           "title": random.choice(titles[wtype]),
                           "status": status, "cat": completed_at})
                    schedule_count += 1
            for days_ahead in range(1, 15):
                if random.random() < 0.5:
                    d = date.today() + timedelta(days=days_ahead)
                    wtype = random.choice(types)
                    conn.execute(text("""
                        INSERT INTO workout_schedule
                            (user_id, planned_date, workout_type, title, status)
                        VALUES (:uid, :date, :wtype, :title, 'planned')
                        ON CONFLICT DO NOTHING
                    """), {"uid": uid, "date": d, "wtype": wtype,
                           "title": random.choice(titles[wtype])})
                    schedule_count += 1
        print(f"  ✅ {schedule_count} schemalagda pass")

        # ── USER MEASUREMENTS ────────────────────────────────────────
        print("\n📏 Seedar user_measurements...")
        meas_count = 0
        for user in users:
            uid = user[0]
            base_weight = float(user[2]) if user[2] else random.uniform(65, 95)
            base_fat = random.uniform(14, 25)
            for weeks_ago in range(16, 0, -1):
                if random.random() < 0.6:
                    measured = datetime.now() - timedelta(weeks=weeks_ago)
                    weight = round(base_weight - (weeks_ago * random.uniform(-0.1, 0.3)), 1)
                    fat = round(base_fat - (weeks_ago * random.uniform(-0.05, 0.15)), 1)
                    muscle = round(weight * (1 - fat / 100) * 0.45, 1)
                    bmi = round(weight / (1.78 ** 2), 1)
                    conn.execute(text("""
                        INSERT INTO user_measurements
                            (user_id, measured_at, weight_kg, body_fat_percentage,
                             muscle_mass_kg, bmi, waist_cm, chest_cm, bicep_cm, thigh_cm, source)
                        VALUES (:uid, :at, :w, :fat, :muscle, :bmi,
                                :waist, :chest, :bicep, :thigh, 'scale')
                    """), {"uid": uid, "at": measured, "w": weight, "fat": fat,
                           "muscle": muscle, "bmi": bmi,
                           "waist": round(random.uniform(72, 95), 1),
                           "chest": round(random.uniform(90, 110), 1),
                           "bicep": round(random.uniform(32, 42), 1),
                           "thigh": round(random.uniform(50, 65), 1)})
                    meas_count += 1
        print(f"  ✅ {meas_count} mätningar")

        # ── WEARABLE SOURCES + METRICS ───────────────────────────────
        print("\n⌚ Seedar wearable_sources + metrics...")
        providers = ['apple_health', 'garmin', 'fitbit', 'whoop', 'oura']
        source_ids = {}
        for user in users:
            uid = user[0]
            source_ids[uid] = []
            for provider in random.sample(providers, random.randint(1, 2)):
                result = conn.execute(text("""
                    INSERT INTO wearable_sources
                        (user_id, provider, is_connected, connected_at, last_synced_at)
                    VALUES (:uid, :p, TRUE, NOW() - INTERVAL '60 days', NOW())
                    ON CONFLICT (user_id, provider) DO UPDATE SET last_synced_at = NOW()
                    RETURNING id
                """), {"uid": uid, "p": provider})
                source_ids[uid].append(result.fetchone()[0])

        wearable_count = 0
        for user in users:
            uid = user[0]
            if not source_ids.get(uid):
                continue
            sid = source_ids[uid][0]
            for days_ago in range(60, 0, -1):
                if random.random() < 0.9:
                    d = date.today() - timedelta(days=days_ago)
                    conn.execute(text("""
                        INSERT INTO wearable_metrics
                            (user_id, source_id, date, heart_rate_resting, heart_rate_max,
                             hrv_ms, vo2_max, steps, calories_burned, active_minutes,
                             distance_km, stress_score, body_battery)
                        VALUES (:uid, :sid, :date, :hr, :hrmax, :hrv, :vo2,
                                :steps, :cal, :active, :dist, :stress, :battery)
                        ON CONFLICT (user_id, date, source_id) DO NOTHING
                    """), {"uid": uid, "sid": sid, "date": d,
                           "hr": random.randint(48, 75), "hrmax": random.randint(155, 195),
                           "hrv": round(random.uniform(25, 80), 1),
                           "vo2": round(random.uniform(38, 58), 1),
                           "steps": random.randint(4000, 18000),
                           "cal": random.randint(1800, 3500),
                           "active": random.randint(20, 120),
                           "dist": round(random.uniform(2, 12), 1),
                           "stress": random.randint(20, 75),
                           "battery": random.randint(30, 100)})
                    wearable_count += 1
        print(f"  ✅ {wearable_count} wearable metrics")

        # ── INJURIES ─────────────────────────────────────────────────
        print("\n🩹 Seedar injuries...")
        injury_data = [
            (0, 'Knä', 'overuse', 2, 'recovering', 30, None, 'Lätt smärta vid knäböj'),
            (1, 'Axel', 'tendinitis', 3, 'active', 14, None, 'Rotatorcuff höger axel'),
            (2, 'Rygg', 'muscle_strain', 2, 'healed', 60, 30, 'Nedre rygg'),
            (3, 'Handled', 'acute', 1, 'recovering', 7, None, 'Lätt belastning'),
        ]
        for idx, bp, itype, sev, status, started_days, healed_days, notes in injury_data:
            if idx < len(users):
                conn.execute(text("""
                    INSERT INTO injuries
                        (user_id, body_part, injury_type, severity, status,
                         started_at, healed_at, notes)
                    VALUES (:uid, :bp, :it, :sev, :status, :started, :healed, :notes)
                    ON CONFLICT DO NOTHING
                """), {"uid": users[idx][0], "bp": bp, "it": itype, "sev": sev,
                       "status": status,
                       "started": date.today() - timedelta(days=started_days),
                       "healed": date.today() - timedelta(days=healed_days) if healed_days else None,
                       "notes": notes})
        print(f"  ✅ {len(injury_data)} skador")

        # ── ACTIVITY LOGS ────────────────────────────────────────────
        print("\n📋 Seedar activity_logs...")
        actions = [
            ('workout_completed', 'Completed workout session'),
            ('goal_created', 'New goal created'),
            ('pr_set', 'New personal record set'),
            ('streak_milestone', 'Streak milestone reached'),
            ('measurement_logged', 'Body measurements logged'),
        ]
        act_count = 0
        for user in users:
            uid = user[0]
            for days_ago in range(60, 0, -3):
                if random.random() < 0.6:
                    action, desc = random.choice(actions)
                    conn.execute(text("""
                        INSERT INTO activity_logs
                            (user_id, action_type, description, created_at)
                        VALUES (:uid, :action, :desc, :created)
                    """), {"uid": uid, "action": action, "desc": desc,
                           "created": datetime.now() - timedelta(days=days_ago)})
                    act_count += 1
        print(f"  ✅ {act_count} activity logs")

        conn.commit()

    print("\n" + "=" * 60)
    print("SEED P1 DATA — klar! 🎉")
    print("=" * 60)


if __name__ == "__main__":
    run()
