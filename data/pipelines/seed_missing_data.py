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

def seed_meal_logs(conn):
    log.info("Adding meal logs...")
    user_id = conn.execute(text("SELECT id FROM users LIMIT 1")).fetchone()[0]
    foods = conn.execute(text("SELECT id, calories_per_100g, protein_per_100g, carbs_per_100g, fat_per_100g FROM foods")).fetchall()
    if not foods:
        log.warning("No foods found!")
        return
    meal_types = ['breakfast', 'lunch', 'dinner', 'snack']
    base_date = datetime.now() - timedelta(days=30)
    count = 0
    for day in range(30):
        current_date = base_date + timedelta(days=day)
        for meal_type in meal_types:
            selected = random.sample(foods, min(random.randint(1, 3), len(foods)))
            for food in selected:
                existing = conn.execute(text("""
                    SELECT id FROM meal_logs
                    WHERE user_id = :uid AND date = :date AND meal_type = :meal AND food_id = :fid
                """), {"uid": user_id, "date": current_date.date(), "meal": meal_type, "fid": food[0]}).fetchone()
                if existing:
                    continue
                amount = random.randint(100, 400)
                conn.execute(text("""
                    INSERT INTO meal_logs (user_id, food_id, date, meal_type, amount_g, calories, protein_g, carbs_g, fat_g)
                    VALUES (:uid, :fid, :date, :meal, :amount, :cal, :protein, :carbs, :fat)
                """), {
                    "uid": user_id, "fid": food[0],
                    "date": current_date.date(), "meal": meal_type,
                    "amount": amount,
                    "cal": round(amount * food[1] / 100, 2),
                    "protein": round(amount * food[2] / 100, 2),
                    "carbs": round(amount * food[3] / 100, 2),
                    "fat": round(amount * food[4] / 100, 2)
                })
                count += 1
    conn.commit()
    log.info(f"Added {count} meal log entries!")

def seed_nutrition_logs(conn):
    log.info("Adding nutrition logs...")
    user_id = conn.execute(text("SELECT id FROM users LIMIT 1")).fetchone()[0]
    base_date = datetime.now() - timedelta(days=30)
    count = 0
    for day in range(30):
        current_date = base_date + timedelta(days=day)
        existing = conn.execute(text("""
            SELECT id FROM nutrition_logs WHERE user_id = :uid AND date = :date
        """), {"uid": user_id, "date": current_date.date()}).fetchone()
        if existing:
            continue
        conn.execute(text("""
            INSERT INTO nutrition_logs
                (user_id, date, calories_consumed, protein_g, carbs_g, fat_g, water_ml, meal_type)
            VALUES (:uid, :date, :cal, :protein, :carbs, :fat, :water, :meal)
        """), {
            "uid": user_id,
            "date": current_date.date(),
            "cal": random.randint(1800, 3000),
            "protein": random.randint(120, 220),
            "carbs": random.randint(150, 350),
            "fat": random.randint(50, 100),
            "water": random.randint(1500, 3500),
            "meal": random.choice(['frukost', 'lunch', 'middag', 'mellanmål'])
        })
        count += 1
    conn.commit()
    log.info(f"Added {count} nutrition log entries!")

def seed_activity_feed(conn):
    log.info("Adding activity feed...")
    user_id = conn.execute(text("SELECT id FROM users LIMIT 1")).fetchone()[0]
    sessions = conn.execute(text(
        "SELECT id, date FROM workout_sessions WHERE user_id = :uid ORDER BY date DESC LIMIT 20"
    ), {"uid": user_id}).fetchall()
    activities = [
        ("workout_completed", "Completed a training session 💪"),
        ("personal_record", "Set a new personal record! 🏆"),
        ("streak_milestone", "5-day training streak! 🔥"),
        ("goal_achieved", "Reached a goal! 📈"),
        ("challenge_joined", "Joined a new challenge 🚀"),
        ("challenge_won", "Won a challenge! 🥇"),
    ]
    count = 0
    for session in sessions:
        activity_type, description = random.choice(activities)
        existing = conn.execute(text("""
            SELECT id FROM activity_feed WHERE user_id = :uid AND related_id = :rid
        """), {"uid": user_id, "rid": session[0]}).fetchone()
        if existing:
            continue
        conn.execute(text("""
            INSERT INTO activity_feed (user_id, activity_type, description, related_id, created_at)
            VALUES (:uid, :type, :desc, :rid, :created)
        """), {
            "uid": user_id, "type": activity_type,
            "desc": description, "rid": session[0],
            "created": session[1]
        })
        count += 1
    conn.commit()
    log.info(f"Added {count} activity feed entries!")

def seed_user_progress(conn):
    log.info("Adding user progress...")
    user_id = conn.execute(text("SELECT id FROM users LIMIT 1")).fetchone()[0]
    base_date = datetime.now() - timedelta(weeks=12)
    count = 0
    for week in range(12):
        current_date = base_date + timedelta(weeks=week)
        existing = conn.execute(text(
            "SELECT id FROM user_progress WHERE user_id = :uid AND date = :date"
        ), {"uid": user_id, "date": current_date.date()}).fetchone()
        if existing:
            continue
        conn.execute(text("""
            INSERT INTO user_progress
                (user_id, date, weight_kg, body_fat_percentage, chest_cm, waist_cm, hips_cm, bicep_cm, thigh_cm)
            VALUES (:uid, :date, :weight, :fat, :chest, :waist, :hips, :bicep, :thigh)
        """), {
            "uid": user_id,
            "date": current_date.date(),
            "weight": round(82 - (week * 0.3) + random.uniform(-0.5, 0.5), 2),
            "fat": round(18 - (week * 0.15) + random.uniform(-0.3, 0.3), 2),
            "chest": round(100 + (week * 0.2) + random.uniform(-0.5, 0.5), 2),
            "waist": round(85 - (week * 0.3) + random.uniform(-0.5, 0.5), 2),
            "hips": round(95 - (week * 0.2) + random.uniform(-0.5, 0.5), 2),
            "bicep": round(35 + (week * 0.1) + random.uniform(-0.2, 0.2), 2),
            "thigh": round(55 + (week * 0.1) + random.uniform(-0.3, 0.3), 2),
        })
        count += 1
    conn.commit()
    log.info(f"Added {count} user progress entries!")

def seed_user_training_plans(conn):
    log.info("Adding user training plans...")
    user_id = conn.execute(text("SELECT id FROM users LIMIT 1")).fetchone()[0]
    plans = conn.execute(text("SELECT id, duration_weeks FROM training_plans LIMIT 3")).fetchall()
    count = 0
    for i, plan in enumerate(plans):
        existing = conn.execute(text("""
            SELECT id FROM user_training_plans WHERE user_id = :uid AND plan_id = :pid
        """), {"uid": user_id, "pid": plan[0]}).fetchone()
        if existing:
            continue
        start_date = datetime.now() - timedelta(weeks=4*i)
        end_date = start_date + timedelta(weeks=plan[1] if plan[1] else 8)
        conn.execute(text("""
            INSERT INTO user_training_plans
                (user_id, plan_id, start_date, end_date, current_week, current_day, is_active, progress_percentage)
            VALUES (:uid, :pid, :start, :end, :week, :day, :active, :progress)
        """), {
            "uid": user_id, "pid": plan[0],
            "start": start_date.date(),
            "end": end_date.date(),
            "week": 1 if i == 0 else plan[1],
            "day": 1,
            "active": True if i == 0 else False,
            "progress": 0 if i == 0 else 100
        })
        count += 1
    conn.commit()
    log.info(f"Added {count} user training plans!")

def seed_challenge_participants(conn):
    log.info("Adding challenge participants...")
    user_id = conn.execute(text("SELECT id FROM users LIMIT 1")).fetchone()[0]
    challenges = conn.execute(text("SELECT id FROM challenges")).fetchall()
    count = 0
    for challenge in challenges:
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
            "uid": user_id, "cid": challenge[0],
            "val": random.randint(5000, 50000),
            "rank": 1
        })
        count += 1
    conn.commit()
    log.info(f"Added {count} challenge participants!")

def seed_streak_rewards(conn):
    log.info("Adding streak rewards...")
    user_id = conn.execute(text("SELECT id FROM users LIMIT 1")).fetchone()[0]
    rewards = [
        (3, "bronze"), (7, "silver"), (14, "gold"), (30, "platinum"),
    ]
    count = 0
    for streak_days, reward_type in rewards:
        existing = conn.execute(text("""
            SELECT id FROM streak_rewards WHERE user_id = :uid AND streak_days = :days
        """), {"uid": user_id, "days": streak_days}).fetchone()
        if existing:
            continue
        conn.execute(text("""
            INSERT INTO streak_rewards (user_id, reward_type, streak_days)
            VALUES (:uid, :type, :days)
        """), {"uid": user_id, "type": reward_type, "days": streak_days})
        count += 1
    conn.commit()
    log.info(f"Added {count} streak rewards!")

if __name__ == "__main__":
    log.info("Starting missing data seeder...")
    with engine.connect() as conn:
        seed_meal_logs(conn)
        seed_nutrition_logs(conn)
        seed_activity_feed(conn)
        seed_user_progress(conn)
        seed_user_training_plans(conn)
        seed_challenge_participants(conn)
        seed_streak_rewards(conn)
    log.info("Done! All missing tables populated.")
