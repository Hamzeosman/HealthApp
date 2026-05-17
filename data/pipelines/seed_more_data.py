from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import logging
import os
import random
from datetime import datetime, timedelta

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
log = logging.getLogger(__name__)

load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"))

def seed_foods(conn):
    """Lägger till 50+ livsmedel med näringsvärden."""
    log.info("Adding foods to database...")

    foods = [
        # Protein
        ("Kycklingfilé", "protein", 165, 31, 0, 3.6),
        ("Lax", "protein", 208, 20, 0, 13),
        ("Torsk", "protein", 82, 18, 0, 0.7),
        ("Tonfisk på burk", "protein", 116, 26, 0, 1),
        ("Räkor", "protein", 85, 18, 0, 1),
        ("Ägg", "protein", 155, 13, 1.1, 11),
        ("Äggvita", "protein", 52, 11, 0.7, 0.2),
        ("Keso", "protein", 72, 12, 3, 1),
        ("Proteinpulver", "protein", 400, 80, 5, 5),
        ("Nötfärs 10%", "protein", 176, 20, 0, 10),
        ("Nötfärs 20%", "protein", 254, 17, 0, 20),
        ("Kycklingfärs", "protein", 142, 17, 0, 8),
        ("Kalkonbröst", "protein", 135, 30, 0, 1),
        ("Sardinburk", "protein", 208, 25, 0, 11),
        ("Makrill", "protein", 205, 19, 0, 14),

        # Kolhydrater
        ("Havregryn", "kolhydrater", 370, 13, 58, 7),
        ("Ris vitt", "kolhydrater", 365, 7, 80, 0.5),
        ("Ris brunt", "kolhydrater", 370, 8, 77, 3),
        ("Pasta fullkorn", "kolhydrater", 352, 13, 67, 3),
        ("Pasta vit", "kolhydrater", 371, 13, 74, 2),
        ("Sötpotatis", "kolhydrater", 86, 1.6, 20, 0.1),
        ("Potatis", "kolhydrater", 77, 2, 17, 0.1),
        ("Quinoa", "kolhydrater", 368, 14, 64, 6),
        ("Bröd fullkorn", "kolhydrater", 259, 9, 45, 4),
        ("Bröd vitt", "kolhydrater", 265, 9, 50, 2),
        ("Bulgur", "kolhydrater", 342, 12, 76, 1),
        ("Linser", "kolhydrater", 353, 26, 60, 1),
        ("Kikärtor", "kolhydrater", 364, 19, 61, 6),
        ("Svarta bönor", "kolhydrater", 341, 22, 63, 1),
        ("Majs", "kolhydrater", 365, 9, 74, 4),

        # Frukt
        ("Banan", "frukt", 89, 1.1, 23, 0.3),
        ("Äpple", "frukt", 52, 0.3, 14, 0.2),
        ("Apelsin", "frukt", 47, 0.9, 12, 0.1),
        ("Jordgubbar", "frukt", 32, 0.7, 7.7, 0.3),
        ("Blåbär", "frukt", 57, 0.7, 14, 0.3),
        ("Mango", "frukt", 60, 0.8, 15, 0.4),
        ("Vindruvor", "frukt", 69, 0.7, 18, 0.2),
        ("Vattenmelon", "frukt", 30, 0.6, 8, 0.2),
        ("Ananas", "frukt", 50, 0.5, 13, 0.1),
        ("Päron", "frukt", 57, 0.4, 15, 0.1),

        # Mejeri
        ("Mjölk 3%", "mejeri", 61, 3.2, 4.8, 3.5),
        ("Mjölk 0.5%", "mejeri", 35, 3.4, 5, 0.5),
        ("Yoghurt naturell", "mejeri", 61, 3.5, 4.7, 3.3),
        ("Yoghurt 0%", "mejeri", 45, 4.5, 6.5, 0.2),
        ("Kvarg", "mejeri", 98, 11, 4, 4.3),
        ("Ost 28%", "mejeri", 353, 25, 0, 28),
        ("Ost 17%", "mejeri", 270, 26, 0, 17),
        ("Ricotta", "mejeri", 174, 11, 3, 13),
        ("Mozzarella", "mejeri", 280, 22, 2.2, 20),
        ("Smör", "mejeri", 717, 0.9, 0.1, 81),

        # Grönsaker
        ("Broccoli", "grönsaker", 34, 2.8, 7, 0.4),
        ("Spenat", "grönsaker", 23, 2.9, 3.6, 0.4),
        ("Tomat", "grönsaker", 18, 0.9, 3.9, 0.2),
        ("Gurka", "grönsaker", 15, 0.7, 3.6, 0.1),
        ("Paprika röd", "grönsaker", 31, 1, 6, 0.3),
        ("Lök", "grönsaker", 40, 1.1, 9.3, 0.1),
        ("Vitlök", "grönsaker", 149, 6.4, 33, 0.5),
        ("Zucchini", "grönsaker", 17, 1.2, 3.1, 0.3),
        ("Blomkål", "grönsaker", 25, 1.9, 5, 0.3),
        ("Kål", "grönsaker", 25, 1.3, 6, 0.1),
        ("Morot", "grönsaker", 41, 0.9, 10, 0.2),
        ("Avokado", "grönsaker", 160, 2, 9, 15),
        ("Böngroddar", "grönsaker", 30, 3, 5.9, 0.2),

        # Fett
        ("Mandlar", "fett", 579, 21, 22, 50),
        ("Valnötter", "fett", 654, 15, 14, 65),
        ("Cashewnötter", "fett", 553, 18, 30, 44),
        ("Jordnötssmör", "fett", 588, 25, 20, 50),
        ("Olivolja", "fett", 884, 0, 0, 100),
        ("Kokosolja", "fett", 862, 0, 0, 100),
        ("Chiafrön", "fett", 486, 17, 42, 31),
        ("Linfrön", "fett", 534, 18, 29, 42),
        ("Solrosfrön", "fett", 584, 21, 20, 51),
        ("Mörk choklad 85%", "fett", 598, 8, 46, 43),
    ]

    count = 0
    for name, category, cal, protein, carbs, fat in foods:
        existing = conn.execute(text(
            "SELECT id FROM foods WHERE name = :name"
        ), {"name": name}).fetchone()
        if not existing:
            conn.execute(text("""
                INSERT INTO foods (name, category, calories_per_100g, protein_per_100g, carbs_per_100g, fat_per_100g)
                VALUES (:name, :cat, :cal, :protein, :carbs, :fat)
            """), {"name": name, "cat": category, "cal": cal, "protein": protein, "carbs": carbs, "fat": fat})
            count += 1

    conn.commit()
    log.info(f"Added {count} new foods!")

def seed_more_training_data(conn):
    """Lägger till mer historisk träningsdata för bättre grafer."""
    log.info("Adding more training history...")

    user_id = conn.execute(text("SELECT id FROM users LIMIT 1")).fetchone()[0]

    exercises = conn.execute(text("""
        SELECT id, name, body_part_id FROM exercises
        WHERE name IN ('Knäböj', 'Bänkpress', 'Marklyft', 'Militärpress',
                       'Latsdrag', 'Bicepscurl', 'Tricepspress', 'Utfall',
                       'Plankan', 'Burpees')
        LIMIT 10
    """)).fetchall()

    if not exercises:
        log.warning("No exercises found!")
        return

    # Skapa 12 veckor historisk data
    base_date = datetime.now() - timedelta(weeks=12)

    sessions_created = 0
    for week in range(12):
        # 3-4 pass per vecka
        sessions_per_week = random.randint(3, 4)
        week_days = random.sample(range(7), sessions_per_week)

        for day_offset in week_days:
            session_date = base_date + timedelta(weeks=week, days=day_offset)

            # Kolla om session redan finns
            existing = conn.execute(text("""
                SELECT id FROM workout_sessions
                WHERE user_id = :uid AND date = :date
            """), {"uid": user_id, "date": session_date.date()}).fetchone()

            if existing:
                continue

            # Skapa träningspass
            result = conn.execute(text("""
                INSERT INTO workout_sessions (user_id, date, duration_minutes, notes)
                VALUES (:uid, :date, :duration, :notes)
                RETURNING id
            """), {
                "uid": user_id,
                "date": session_date.date(),
                "duration": random.randint(45, 90),
                "notes": f"Week {week + 1} training session"
            }).fetchone()
            session_id = result[0]

            # Lägg till 4-6 övningar per pass
            session_exercises = random.sample(exercises, min(random.randint(4, 6), len(exercises)))
            for order, ex in enumerate(session_exercises, 1):
                # Progressiv viktökning över veckor
                base_weight = {
                    'Knäböj': 80, 'Bänkpress': 70, 'Marklyft': 100,
                    'Militärpress': 50, 'Latsdrag': 60, 'Bicepscurl': 20,
                    'Tricepspress': 25, 'Utfall': 30, 'Plankan': 0, 'Burpees': 0
                }.get(ex[1], 40)

                weight = base_weight + (week * random.uniform(1, 3))
                rpe = round(random.uniform(6.5, 9.0), 1)
                sets = random.randint(3, 5)
                reps = random.randint(6, 12)

                conn.execute(text("""
                    INSERT INTO workout_exercises
                        (session_id, exercise_id, sets, reps, weight_kg, rpe)
                    VALUES (:sid, :eid, :sets, :reps, :weight, :rpe)
                """), {
                    "sid": session_id,
                    "eid": ex[0],
                    "sets": sets,
                    "reps": reps,
                    "weight": round(weight, 1),
                    "rpe": int(round(rpe))
                })

            sessions_created += 1

    conn.commit()
    log.info(f"Added {sessions_created} training sessions over 12 weeks!")

def seed_more_biometrics(conn):
    """Lägger till 90 dagar biometridata."""
    log.info("Adding biometrics data for 90 days...")

    user_id = conn.execute(text("SELECT id FROM users LIMIT 1")).fetchone()[0]
    base_date = datetime.now() - timedelta(days=90)
    count = 0

    for day in range(90):
        current_date = base_date + timedelta(days=day)

        existing = conn.execute(text("""
            SELECT id FROM biometrics WHERE user_id = :uid AND date = :date
        """), {"uid": user_id, "date": current_date.date()}).fetchone()

        if existing:
            continue

        # Realistisk stegdata med variation
        base_steps = 8000
        weekend_bonus = 3000 if current_date.weekday() >= 5 else 0
        steps = int(base_steps + weekend_bonus + random.randint(-2000, 4000))

        conn.execute(text("""
            INSERT INTO biometrics
                (user_id, date, steps, heart_rate_resting, heart_rate_avg,
                 calories_burned, active_minutes, vo2_max)
            VALUES (:uid, :date, :steps, :hr_rest, :hr_avg, :calories, :active, :vo2)
        """), {
            "uid": user_id,
            "date": current_date.date(),
            "steps": max(0, steps),
            "hr_rest": random.randint(55, 70),
            "hr_avg": random.randint(70, 90),
            "calories": random.randint(2000, 3500),
            "active": random.randint(30, 120),
            "vo2": round(random.uniform(42, 52), 1)
        })
        count += 1

    conn.commit()
    log.info(f"Added {count} days of biometrics data!")

def seed_more_recovery(conn):
    """Lägger till 90 dagar återhämtningsdata."""
    log.info("Adding recovery data for 90 days...")

    user_id = conn.execute(text("SELECT id FROM users LIMIT 1")).fetchone()[0]
    base_date = datetime.now() - timedelta(days=90)
    count = 0

    for day in range(90):
        current_date = base_date + timedelta(days=day)

        existing = conn.execute(text("""
            SELECT id FROM recovery_logs WHERE user_id = :uid AND date = :date
        """), {"uid": user_id, "date": current_date.date()}).fetchone()

        if existing:
            continue

        conn.execute(text("""
            INSERT INTO recovery_logs
                (user_id, date, sleep_hours, sleep_quality, energy_level,
                 stress_level, notes)
            VALUES (:uid, :date, :sleep, :sq, :energy, :stress, :notes)
        """), {
            "uid": user_id,
            "date": current_date.date(),
            "sleep": round(random.uniform(6.0, 9.0), 1),
            "sq": random.randint(5, 10),
            "energy": random.randint(5, 10),
            "stress": random.randint(2, 8),
            "notes": "Auto-generated recovery log"
        })
        count += 1

    conn.commit()
    log.info(f"Added {count} days of recovery data!")

def seed_more_running(conn):
    """Lägger till löpningsdata för 3 månader."""
    log.info("Adding running sessions...")

    user_id = conn.execute(text("SELECT id FROM users LIMIT 1")).fetchone()[0]
    base_date = datetime.now() - timedelta(weeks=12)
    count = 0

    for week in range(12):
        # 2-3 löppass per vecka
        run_days = random.sample(range(7), random.randint(2, 3))

        for day_offset in run_days:
            run_date = base_date + timedelta(weeks=week, days=day_offset)

            existing = conn.execute(text("""
                SELECT id FROM running_sessions WHERE user_id = :uid AND date = :date
            """), {"uid": user_id, "date": run_date.date()}).fetchone()

            if existing:
                continue

            # Progressiv förbättring i distans och tempo
            base_distance = 5 + (week * 0.3)
            distance = round(base_distance + random.uniform(-1, 2), 1)
            base_pace = 6.0 - (week * 0.05)
            pace = round(base_pace + random.uniform(-0.3, 0.3), 2)
            duration = int(distance * pace)
            route_types = ['utomhus', 'löpband', 'spår']

            conn.execute(text("""
                INSERT INTO running_sessions
                    (user_id, date, distance_km, duration_minutes, avg_pace_min_per_km,
                     avg_heart_rate, calories_burned, route_type)
                VALUES (:uid, :date, :dist, :dur, :pace, :hr, :cal, :route)
            """), {
                "uid": user_id,
                "date": run_date.date(),
                "dist": distance,
                "dur": duration,
                "pace": pace,
                "hr": random.randint(140, 170),
                "cal": int(distance * 60),
                "route": random.choice(route_types)
            })
            count += 1

    conn.commit()
    log.info(f"Added {count} running sessions!")

if __name__ == "__main__":
    log.info("Starting data seeder...")
    with engine.connect() as conn:
        seed_foods(conn)
        seed_more_training_data(conn)
        seed_more_biometrics(conn)
        seed_more_recovery(conn)
        seed_more_running(conn)
    log.info("All data added!")
    log.info("Summary:")
    log.info("- 70+ foods with nutritional values")
    log.info("- 12 weeks training history")
    log.info("- 90 days biometrics")
    log.info("- 90 days recovery logs")
    log.info("- 12 weeks running sessions")