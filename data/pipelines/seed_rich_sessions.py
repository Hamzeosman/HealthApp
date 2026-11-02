from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os, random, datetime

load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"))

MOODS = ["bra", "bra", "bra", "stark", "stark", "okej", "trött", "okej", "bra", "stark"]

with engine.connect() as conn:
    user = conn.execute(text("SELECT id FROM users WHERE email = 'test@healthapp.com'")).fetchone()
    if not user:
        print("Kör seed_test_data.py först")
        exit(1)
    user_id = user[0]

    ex_ids = [e[0] for e in conn.execute(text("SELECT id FROM exercises ORDER BY id LIMIT 12")).fetchall()]
    if not ex_ids:
        print("Inga övningar i databasen")
        exit(1)

    today = datetime.date(2026, 11, 1)
    dates = sorted(random.sample([today - datetime.timedelta(days=i) for i in range(1, 180)], 40))

    inserted = 0
    for d in dates:
        if conn.execute(text("SELECT id FROM workout_sessions WHERE user_id = :uid AND date = :date"), {"uid": user_id, "date": d}).fetchone():
            continue
        duration = random.choice([30, 45, 45, 60, 60, 60, 75, 90])
        calories = int(duration * random.uniform(5.5, 8.5))
        mood = random.choice(MOODS)
        sid = conn.execute(text("INSERT INTO workout_sessions (user_id, date, duration_minutes, total_calories, mood) VALUES (:uid, :date, :duration, :calories, :mood) RETURNING id"), {"uid": user_id, "date": d, "duration": duration, "calories": calories, "mood": mood}).fetchone()[0]
        for ex_id in random.sample(ex_ids, min(random.randint(3, 5), len(ex_ids))):
            conn.execute(text("INSERT INTO workout_exercises (session_id, exercise_id, sets, reps, weight_kg, rpe) VALUES (:sid, :eid, :sets, :reps, :weight, :rpe)"), {"sid": sid, "eid": ex_id, "sets": random.randint(3, 5), "reps": random.randint(6, 12), "weight": round(random.uniform(20, 120), 1), "rpe": random.randint(6, 10)})
        inserted += 1

    conn.commit()
    total = conn.execute(text("SELECT COUNT(*) FROM workout_sessions WHERE user_id = :uid"), {"uid": user_id}).fetchone()[0]
    print(f"Lade till {inserted} pass. Totalt: {total}")