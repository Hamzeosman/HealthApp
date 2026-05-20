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

USERS = [
    {
        "name": "Erik Johansson",
        "email": "erik@test.com",
        "age": 28,
        "weight_kg": 82,
        "height_cm": 182,
        "fitness_level": "medel",
        "fitness_goal": "bygga_muskler",
        "experience_level": "medel",
    },
    {
        "name": "Sara Lindqvist",
        "email": "sara@test.com",
        "age": 25,
        "weight_kg": 63,
        "height_cm": 168,
        "fitness_level": "nybörjare",
        "fitness_goal": "hålla_sig_i_form",
        "experience_level": "nybörjare",
    },
    {
        "name": "Mohammed Al-Rashid",
        "email": "mohammed@test.com",
        "age": 32,
        "weight_kg": 90,
        "height_cm": 178,
        "fitness_level": "avancerad",
        "fitness_goal": "bygga_muskler",
        "experience_level": "avancerad",
    },
    {
        "name": "Fatima Hassan",
        "email": "fatima@test.com",
        "age": 27,
        "weight_kg": 58,
        "height_cm": 165,
        "fitness_level": "nybörjare",
        "fitness_goal": "gå_ner_i_vikt",
        "experience_level": "nybörjare",
    },
    {
        "name": "Lucas Bergström",
        "email": "lucas@test.com",
        "age": 22,
        "weight_kg": 75,
        "height_cm": 180,
        "fitness_level": "nybörjare",
        "fitness_goal": "öka_kondition",
        "experience_level": "nybörjare",
    },
    {
        "name": "Amina Osman",
        "email": "amina@test.com",
        "age": 30,
        "weight_kg": 67,
        "height_cm": 170,
        "fitness_level": "medel",
        "fitness_goal": "hålla_sig_i_form",
        "experience_level": "medel",
    },
    {
        "name": "Viktor Svensson",
        "email": "viktor@test.com",
        "age": 35,
        "weight_kg": 95,
        "height_cm": 185,
        "fitness_level": "avancerad",
        "fitness_goal": "bygga_muskler",
        "experience_level": "avancerad",
    },
    {
        "name": "Lina Karlsson",
        "email": "lina@test.com",
        "age": 24,
        "weight_kg": 55,
        "height_cm": 162,
        "fitness_level": "medel",
        "fitness_goal": "gå_ner_i_vikt",
        "experience_level": "medel",
    },
]

def seed_users(conn):
    log.info("Adding test users...")
    user_ids = []
    for u in USERS:
        existing = conn.execute(text(
            "SELECT id FROM users WHERE email = :email"
        ), {"email": u["email"]}).fetchone()
        if existing:
            user_ids.append(existing[0])
            continue
        result = conn.execute(text("""
            INSERT INTO users
                (name, email, password_hash, age, weight_kg, height_cm,
                 fitness_level, fitness_goal, experience_level)
            VALUES
                (:name, :email, :password, :age, :weight, :height,
                 :fitness_level, :fitness_goal, :experience_level)
            RETURNING id
        """), {
            "name": u["name"],
            "email": u["email"],
            "password": "hashed_test_password_123",
            "age": u["age"],
            "weight": u["weight_kg"],
            "height": u["height_cm"],
            "fitness_level": u["fitness_level"],
            "fitness_goal": u["fitness_goal"],
            "experience_level": u["experience_level"],
        }).fetchone()
        user_ids.append(result[0])
    conn.commit()
    log.info(f"Users ready: {len(user_ids)} users")
    return user_ids

def seed_user_data(conn, user_ids):
    """Lägger till träningsdata för varje användare."""
    log.info("Adding training data for all users...")
    exercises = conn.execute(text("SELECT id FROM exercises LIMIT 10")).fetchall()
    if not exercises:
        log.warning("No exercises found!")
        return

    for user_id in user_ids:
        # Streak
        existing = conn.execute(text(
            "SELECT id FROM user_streaks WHERE user_id = :uid"
        ), {"uid": user_id}).fetchone()
        if not existing:
            conn.execute(text("""
                INSERT INTO user_streaks
                    (user_id, current_streak, longest_streak, total_workouts, last_workout_date)
                VALUES (:uid, :cur, :long, :total, :last)
            """), {
                "uid": user_id,
                "cur": random.randint(1, 15),
                "long": random.randint(10, 30),
                "total": random.randint(20, 100),
                "last": datetime.now().date()
            })

        # Träningspass — 4 veckor
        base_date = datetime.now() - timedelta(weeks=4)
        for week in range(4):
            sessions_per_week = random.randint(2, 4)
            days = random.sample(range(7), sessions_per_week)
            for day in days:
                session_date = base_date + timedelta(weeks=week, days=day)
                existing = conn.execute(text("""
                    SELECT id FROM workout_sessions
                    WHERE user_id = :uid AND date = :date
                """), {"uid": user_id, "date": session_date.date()}).fetchone()
                if existing:
                    continue
                result = conn.execute(text("""
                    INSERT INTO workout_sessions (user_id, date, duration_minutes, mood, notes)
                    VALUES (:uid, :date, :duration, :mood, :notes) RETURNING id
                """), {
                    "uid": user_id,
                    "date": session_date.date(),
                    "duration": random.randint(45, 90),
                    "mood": random.choice(["bra", "okej", "trött", "stark"]),
                    "notes": f"Training session week {week + 1}"
                }).fetchone()
                session_id = result[0]
                selected = random.sample(exercises, min(4, len(exercises)))
                for ex in selected:
                    conn.execute(text("""
                        INSERT INTO workout_exercises
                            (session_id, exercise_id, sets, reps, weight_kg, rpe)
                        VALUES (:sid, :eid, :sets, :reps, :weight, :rpe)
                    """), {
                        "sid": session_id,
                        "eid": ex[0],
                        "sets": random.randint(3, 5),
                        "reps": random.randint(6, 12),
                        "weight": round(random.uniform(20, 100), 1),
                        "rpe": random.randint(6, 9)
                    })

        # Recovery — 30 dagar
        base_date = datetime.now() - timedelta(days=30)
        for day in range(30):
            current_date = base_date + timedelta(days=day)
            existing = conn.execute(text("""
                SELECT id FROM recovery_logs WHERE user_id = :uid AND date = :date
            """), {"uid": user_id, "date": current_date.date()}).fetchone()
            if existing:
                continue
            conn.execute(text("""
                INSERT INTO recovery_logs
                    (user_id, date, sleep_hours, sleep_quality, energy_level, stress_level, notes)
                VALUES (:uid, :date, :sleep, :sq, :energy, :stress, :notes)
            """), {
                "uid": user_id,
                "date": current_date.date(),
                "sleep": round(random.uniform(6, 9), 1),
                "sq": random.randint(5, 10),
                "energy": random.randint(5, 10),
                "stress": random.randint(2, 8),
                "notes": "Auto-generated"
            })

        # Biometrics — 30 dagar
        base_date = datetime.now() - timedelta(days=30)
        for day in range(30):
            current_date = base_date + timedelta(days=day)
            existing = conn.execute(text("""
                SELECT id FROM biometrics WHERE user_id = :uid AND date = :date
            """), {"uid": user_id, "date": current_date.date()}).fetchone()
            if existing:
                continue
            conn.execute(text("""
                INSERT INTO biometrics
                    (user_id, date, steps, heart_rate_resting, heart_rate_avg,
                     calories_burned, active_minutes, vo2_max)
                VALUES (:uid, :date, :steps, :hr_rest, :hr_avg, :calories, :active, :vo2)
            """), {
                "uid": user_id,
                "date": current_date.date(),
                "steps": random.randint(5000, 15000),
                "hr_rest": random.randint(55, 75),
                "hr_avg": random.randint(70, 95),
                "calories": random.randint(2000, 3500),
                "active": random.randint(30, 120),
                "vo2": round(random.uniform(38, 55), 1)
            })

        # Goals
        goal_types = [
            ("target_weight", random.uniform(65, 90), random.uniform(60, 85), "kg"),
            ("run_distance", random.uniform(3, 7), 10, "km"),
        ]
        for goal_type, current, target, unit in goal_types:
            existing = conn.execute(text("""
                SELECT id FROM user_goals WHERE user_id = :uid AND goal_type = :gt
            """), {"uid": user_id, "gt": goal_type}).fetchone()
            if existing:
                continue
            conn.execute(text("""
                INSERT INTO user_goals
                    (user_id, goal_type, current_value, target_value, unit, deadline)
                VALUES (:uid, :gt, :cur, :tar, :unit, :deadline)
            """), {
                "uid": user_id,
                "gt": goal_type,
                "cur": round(current, 1),
                "tar": round(target, 1),
                "unit": unit,
                "deadline": (datetime.now() + timedelta(days=90)).date()
            })

        # Leaderboard
        existing = conn.execute(text(
            "SELECT id FROM leaderboard WHERE user_id = :uid"
        ), {"uid": user_id}).fetchone()
        if not existing:
            sessions_count = conn.execute(text(
                "SELECT COUNT(*) FROM workout_sessions WHERE user_id = :uid"
            ), {"uid": user_id}).fetchone()[0]
            conn.execute(text("""
                INSERT INTO leaderboard
                    (user_id, total_sessions, total_volume_kg, total_steps, points)
                VALUES (:uid, :sessions, :volume, :steps, :points)
            """), {
                "uid": user_id,
                "sessions": sessions_count,
                "volume": round(random.uniform(5000, 50000), 2),
                "steps": random.randint(50000, 300000),
                "points": random.randint(100, 1000)
            })

    conn.commit()
    log.info("Training data added for all users!")

def seed_friendships(conn, user_ids):
    """Skapar vänskapsrelationer mellan användare."""
    log.info("Adding friendships...")
    count = 0
    for i, user_id in enumerate(user_ids):
        friends = random.sample([u for u in user_ids if u != user_id], min(3, len(user_ids)-1))
        for friend_id in friends:
            existing = conn.execute(text("""
                SELECT id FROM friendships
                WHERE (user_id = :uid AND friend_id = :fid)
                OR (user_id = :fid AND friend_id = :uid)
            """), {"uid": user_id, "fid": friend_id}).fetchone()
            if existing:
                continue
            conn.execute(text("""
                INSERT INTO friendships (user_id, friend_id, status, created_at)
                VALUES (:uid, :fid, 'accepted', NOW())
            """), {"uid": user_id, "fid": friend_id})
            count += 1
    conn.commit()
    log.info(f"Added {count} friendships!")

def seed_challenge_participants_all(conn, user_ids):
    """Lägger till alla användare i challenges."""
    log.info("Adding all users to challenges...")
    challenges = conn.execute(text("SELECT id FROM challenges")).fetchall()
    count = 0
    for challenge in challenges:
        for user_id in user_ids:
            existing = conn.execute(text("""
                SELECT id FROM challenge_participants
                WHERE user_id = :uid AND challenge_id = :cid
            """), {"uid": user_id, "cid": challenge[0]}).fetchone()
            if existing:
                continue
            conn.execute(text("""
                INSERT INTO challenge_participants (user_id, challenge_id, current_value, rank)
                VALUES (:uid, :cid, :val, :rank)
            """), {
                "uid": user_id,
                "cid": challenge[0],
                "val": round(random.uniform(1000, 80000), 2),
                "rank": random.randint(1, len(user_ids))
            })
            count += 1
    conn.commit()
    log.info(f"Added {count} challenge participants!")

def seed_activity_feed_all(conn, user_ids):
    """Lägger till aktiviteter för alla användare."""
    log.info("Adding activity feed for all users...")
    activities = [
        ("workout_completed", "Completed a training session 💪"),
        ("personal_record", "Set a new personal record! 🏆"),
        ("streak_milestone", "Reached a new streak milestone! 🔥"),
        ("goal_achieved", "Achieved a fitness goal! 📈"),
        ("challenge_joined", "Joined a new challenge! 🚀"),
    ]
    count = 0
    for user_id in user_ids:
        for _ in range(random.randint(3, 8)):
            activity_type, description = random.choice(activities)
            conn.execute(text("""
                INSERT INTO activity_feed (user_id, activity_type, description, created_at)
                VALUES (:uid, :type, :desc, :created)
            """), {
                "uid": user_id,
                "type": activity_type,
                "desc": description,
                "created": datetime.now() - timedelta(days=random.randint(0, 30))
            })
            count += 1
    conn.commit()
    log.info(f"Added {count} activity feed entries!")

if __name__ == "__main__":
    log.info("Starting users and social seeder...")
    with engine.connect() as conn:
        user_ids = seed_users(conn)
        seed_user_data(conn, user_ids)
        seed_friendships(conn, user_ids)
        seed_challenge_participants_all(conn, user_ids)
        seed_activity_feed_all(conn, user_ids)
    log.info("Done!")
    log.info(f"Added 8 test users with full data:")
    log.info("- Erik, Sara, Mohammed, Fatima, Lucas, Amina, Viktor, Lina")
    log.info("- 4 weeks training history each")
    log.info("- 30 days recovery + biometrics each")
    log.info("- Friendships between users")
    log.info("- Leaderboard entries")
    log.info("- Challenge participants")