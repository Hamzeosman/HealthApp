from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import logging
import os

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
log = logging.getLogger(__name__)

load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"))

def get_exercise_id(conn, name):
    result = conn.execute(text(
        "SELECT id FROM exercises WHERE name = :name"
    ), {"name": name}).fetchone()
    return result[0] if result else None

def create_program(conn, name, goal, difficulty, duration_weeks, days_per_week, description, target_audience):
    existing = conn.execute(text(
        "SELECT id FROM training_plans WHERE name = :name"
    ), {"name": name}).fetchone()

    if existing:
        log.info(f"Program '{name}' already exists, skipping.")
        return existing[0]

    result = conn.execute(text("""
        INSERT INTO training_plans
            (name, goal, difficulty, duration_weeks, days_per_week, description, target_audience)
        VALUES (:name, :goal, :diff, :weeks, :days, :desc, :target)
        RETURNING id
    """), {
        "name": name, "goal": goal, "diff": difficulty,
        "weeks": duration_weeks, "days": days_per_week,
        "desc": description, "target": target_audience
    }).fetchone()
    conn.commit()
    return result[0]

def add_day(conn, plan_id, week, day_num, day_name, focus, is_rest=False):
    result = conn.execute(text("""
        INSERT INTO training_plan_days
            (plan_id, week_number, day_number, day_name, focus, rest_day)
        VALUES (:plan_id, :week, :day, :name, :focus, :rest)
        RETURNING id
    """), {
        "plan_id": plan_id, "week": week, "day": day_num,
        "name": day_name, "focus": focus, "rest": is_rest
    }).fetchone()
    return result[0]

def add_exercise(conn, day_id, ex_id, sets, reps, rest_seconds, intensity, order):
    if ex_id:
        conn.execute(text("""
            INSERT INTO training_plan_exercises
                (plan_day_id, exercise_id, sets, reps, rest_seconds, intensity, order_index)
            VALUES (:day_id, :ex_id, :sets, :reps, :rest, :intensity, :order)
        """), {
            "day_id": day_id, "ex_id": ex_id, "sets": sets,
            "reps": reps, "rest": rest_seconds,
            "intensity": intensity, "order": order
        })

def seed_beginner_program(conn):
    log.info("Creating Beginner Full Body Program...")

    plan_id = create_program(conn,
        name="Beginner Full Body — 8 Week",
        goal="hålla_sig_i_form",
        difficulty="nybörjare",
        duration_weeks=8,
        days_per_week=3,
        description="A simple 3-day full body program for complete beginners. Focuses on learning the fundamental movement patterns with light weights and proper form.",
        target_audience="Complete beginners with no gym experience"
    )

    full_body = [
        ("Knäböj", 3, 10, 90, "light"),
        ("Bänkpress", 3, 10, 90, "light"),
        ("Marklyft", 3, 8, 120, "light"),
        ("Latsdrag", 3, 10, 90, "light"),
        ("Militärpress", 3, 10, 90, "light"),
        ("Plankan", 3, 30, 60, "light"),
    ]

    total_days = 0
    for week in range(1, 9):
        for day_num, day_name in [(1, "Day 1"), (2, "Day 2"), (3, "Day 3")]:
            sets_mult = 1.0 if week <= 4 else 1.1
            day_id = add_day(conn, plan_id, week, day_num,
                f"Week {week} — Full Body {day_name}",
                "Full body compound movements")
            for order, (ex_name, sets, reps, rest, intensity) in enumerate(full_body, 1):
                ex_id = get_exercise_id(conn, ex_name)
                add_exercise(conn, day_id, ex_id,
                    max(2, round(sets * sets_mult)), reps, rest, intensity, order)
            total_days += 1

        # Rest days
        for rest_day in [4, 5, 6, 7]:
            add_day(conn, plan_id, week, rest_day,
                f"Week {week} — Rest", "Recovery", is_rest=True)

    conn.commit()
    log.info(f"Beginner program created! {total_days} training days added.")
    return plan_id

def seed_upper_lower_program(conn):
    log.info("Creating Upper/Lower Split Program...")

    plan_id = create_program(conn,
        name="Upper/Lower Split — 12 Week",
        goal="bygga_muskler",
        difficulty="medel",
        duration_weeks=12,
        days_per_week=4,
        description="A 4-day Upper/Lower split with progressive overload. Upper A is strength-focused, Upper B is volume-focused. Great for intermediate lifters looking to build size and strength.",
        target_audience="Intermediate lifters with 6+ months of training experience"
    )

    upper_a = [
        ("Bänkpress", 4, 6, 150, "heavy"),
        ("Latsdrag", 4, 8, 90, "heavy"),
        ("Militärpress", 3, 8, 90, "heavy"),
        ("Seated Cable Row", 3, 8, 90, "heavy"),
        ("Skull Crushers", 3, 10, 75, "moderate"),
        ("Bicepscurl", 3, 10, 75, "moderate"),
    ]

    upper_b = [
        ("Incline Bänkpress", 4, 10, 90, "moderate"),
        ("Pull-ups", 4, 10, 90, "moderate"),
        ("Cable Flyes", 3, 12, 60, "light"),
        ("Face Pulls", 3, 15, 60, "light"),
        ("Lateral Raises", 4, 15, 60, "light"),
        ("Hammer Curl", 3, 12, 60, "light"),
    ]

    lower_a = [
        ("Knäböj", 4, 6, 150, "heavy"),
        ("Romanian Deadlift", 3, 8, 90, "heavy"),
        ("Leg Press", 3, 10, 90, "moderate"),
        ("Leg Curl", 3, 12, 60, "light"),
        ("Calf Raises", 4, 15, 45, "light"),
    ]

    lower_b = [
        ("Marklyft", 4, 6, 150, "heavy"),
        ("Bulgarian Split Squat", 3, 10, 90, "moderate"),
        ("Leg Extension", 3, 12, 60, "light"),
        ("Hip Thrust", 3, 12, 90, "moderate"),
        ("Calf Raises", 4, 15, 45, "light"),
    ]

    days_structure = [
        (1, "Upper A", "Chest, Back, Shoulders, Arms — Strength", upper_a),
        (2, "Lower A", "Quads, Hamstrings, Calves — Strength", lower_a),
        (3, "Rest", "Active recovery", []),
        (4, "Upper B", "Chest, Back, Shoulders, Arms — Volume", upper_b),
        (5, "Lower B", "Quads, Hamstrings, Glutes — Volume", lower_b),
        (6, "Rest", "Active recovery", []),
        (7, "Rest", "Full rest day", []),
    ]

    total_days = 0
    for week in range(1, 13):
        is_deload = week == 12
        sets_mult = 1.0 if week <= 4 else 1.15 if week <= 8 else 1.3

        for day_num, day_name, focus, exercises in days_structure:
            is_rest = len(exercises) == 0
            day_id = add_day(conn, plan_id, week, day_num,
                f"Week {week} — {day_name}", focus, is_rest=is_rest)

            if not is_rest:
                for order, (ex_name, sets, reps, rest, intensity) in enumerate(exercises, 1):
                    ex_id = get_exercise_id(conn, ex_name)
                    actual_sets = max(2, round(sets * (0.5 if is_deload else sets_mult)))
                    actual_reps = max(5, reps - 2) if is_deload else reps
                    add_exercise(conn, day_id, ex_id, actual_sets,
                        actual_reps, rest, "light" if is_deload else intensity, order)
                total_days += 1

    conn.commit()
    log.info(f"Upper/Lower program created! {total_days} training days added.")
    return plan_id

def seed_fat_loss_program(conn):
    log.info("Creating Fat Loss Circuit Program...")

    plan_id = create_program(conn,
        name="Fat Loss Circuit — 8 Week",
        goal="gå_ner_i_vikt",
        difficulty="nybörjare",
        duration_weeks=8,
        days_per_week=5,
        description="A high-intensity 5-day circuit training program combining strength and cardio to maximize fat burning. Short rest periods keep heart rate elevated throughout.",
        target_audience="Anyone looking to lose body fat while maintaining muscle mass"
    )

    circuit_a = [
        ("Knäböj", 3, 15, 30, "light"),
        ("Bänkpress", 3, 12, 30, "light"),
        ("Utfall", 3, 12, 30, "light"),
        ("Latsdrag", 3, 12, 30, "light"),
        ("Plankan", 3, 45, 30, "light"),
        ("Burpees", 3, 10, 45, "moderate"),
    ]

    circuit_b = [
        ("Marklyft", 3, 12, 30, "light"),
        ("Militärpress", 3, 12, 30, "light"),
        ("Knäböj", 3, 15, 30, "light"),
        ("Bicepscurl", 3, 15, 30, "light"),
        ("Tricepspress", 3, 15, 30, "light"),
        ("Burpees", 4, 12, 45, "moderate"),
    ]

    days_structure = [
        (1, "Circuit A", "Full body circuit", circuit_a),
        (2, "Circuit B", "Full body circuit", circuit_b),
        (3, "Cardio", "30-45 min cardio", []),
        (4, "Circuit A", "Full body circuit", circuit_a),
        (5, "Circuit B", "Full body circuit", circuit_b),
        (6, "Rest", "Active recovery", []),
        (7, "Rest", "Full rest", []),
    ]

    total_days = 0
    for week in range(1, 9):
        for day_num, day_name, focus, exercises in days_structure:
            is_rest = len(exercises) == 0
            day_id = add_day(conn, plan_id, week, day_num,
                f"Week {week} — {day_name}", focus, is_rest=is_rest)
            if not is_rest and exercises:
                for order, (ex_name, sets, reps, rest, intensity) in enumerate(exercises, 1):
                    ex_id = get_exercise_id(conn, ex_name)
                    add_exercise(conn, day_id, ex_id, sets, reps, rest, intensity, order)
                total_days += 1

    conn.commit()
    log.info(f"Fat Loss program created! {total_days} training days added.")
    return plan_id

def seed_bulk_program(conn):
    log.info("Creating Bulk Up Program...")

    plan_id = create_program(conn,
        name="Bulk Up — Heavy Compound 10 Week",
        goal="gå_upp_i_vikt",
        difficulty="avancerad",
        duration_weeks=10,
        days_per_week=5,
        description="A heavy compound movement program designed to maximize strength and muscle gain. Uses progressive overload with low reps and heavy weights. Eat in a caloric surplus for best results.",
        target_audience="Advanced lifters looking to gain serious size and strength"
    )

    heavy_push = [
        ("Bänkpress", 5, 5, 180, "heavy"),
        ("Incline Bänkpress", 4, 6, 150, "heavy"),
        ("Militärpress", 4, 5, 150, "heavy"),
        ("Dips", 3, 8, 90, "heavy"),
        ("Lateral Raises", 3, 12, 60, "moderate"),
    ]

    heavy_pull = [
        ("Marklyft", 5, 5, 180, "heavy"),
        ("Pull-ups", 4, 6, 120, "heavy"),
        ("Latsdrag", 4, 8, 90, "heavy"),
        ("Seated Cable Row", 3, 8, 90, "heavy"),
        ("Bicepscurl", 3, 10, 75, "moderate"),
    ]

    heavy_legs = [
        ("Knäböj", 5, 5, 180, "heavy"),
        ("Romanian Deadlift", 4, 6, 150, "heavy"),
        ("Leg Press", 4, 8, 120, "heavy"),
        ("Bulgarian Split Squat", 3, 8, 90, "moderate"),
        ("Calf Raises", 5, 12, 45, "moderate"),
    ]

    days_structure = [
        (1, "Heavy Push", "Chest, Shoulders, Triceps", heavy_push),
        (2, "Heavy Pull", "Back, Biceps", heavy_pull),
        (3, "Heavy Legs", "Quads, Hamstrings, Glutes", heavy_legs),
        (4, "Rest", "Rest", []),
        (5, "Heavy Push", "Chest, Shoulders, Triceps", heavy_push),
        (6, "Heavy Pull + Legs", "Back, Biceps, Legs", heavy_pull),
        (7, "Rest", "Full rest", []),
    ]

    total_days = 0
    for week in range(1, 11):
        is_deload = week == 10
        for day_num, day_name, focus, exercises in days_structure:
            is_rest = len(exercises) == 0
            day_id = add_day(conn, plan_id, week, day_num,
                f"Week {week} — {day_name}", focus, is_rest=is_rest)
            if not is_rest and exercises:
                for order, (ex_name, sets, reps, rest, intensity) in enumerate(exercises, 1):
                    ex_id = get_exercise_id(conn, ex_name)
                    actual_sets = max(2, round(sets * 0.5)) if is_deload else sets
                    actual_reps = max(5, reps + 2) if is_deload else reps
                    add_exercise(conn, day_id, ex_id, actual_sets,
                        actual_reps, rest, "light" if is_deload else intensity, order)
                total_days += 1

    conn.commit()
    log.info(f"Bulk program created! {total_days} training days added.")
    return plan_id

def seed_powerlifting_program(conn):
    log.info("Creating Powerlifting Program...")

    plan_id = create_program(conn,
        name="Powerlifting — Strength Peak 16 Week",
        goal="bygga_muskler",
        difficulty="avancerad",
        duration_weeks=16,
        days_per_week=4,
        description="A 16-week powerlifting peaking program based on periodization. Phase 1: Hypertrophy (Week 1-4), Phase 2: Strength (Week 5-8), Phase 3: Peaking (Week 9-12), Phase 4: Competition prep (Week 13-15), Week 16: Deload/Taper.",
        target_audience="Advanced lifters who want to maximize their squat, bench and deadlift"
    )

    # Hypertrophy phase — vecka 1-4
    hypertrophy_squat = [
        ("Knäböj", 4, 8, 120, "moderate"),
        ("Romanian Deadlift", 3, 10, 90, "moderate"),
        ("Leg Press", 3, 12, 90, "light"),
        ("Leg Curl", 3, 12, 60, "light"),
        ("Calf Raises", 3, 15, 45, "light"),
    ]

    hypertrophy_bench = [
        ("Bänkpress", 4, 8, 120, "moderate"),
        ("Incline Bänkpress", 3, 10, 90, "moderate"),
        ("Cable Flyes", 3, 12, 60, "light"),
        ("Tricepspress", 3, 12, 60, "light"),
        ("Lateral Raises", 3, 15, 60, "light"),
    ]

    hypertrophy_deadlift = [
        ("Marklyft", 4, 6, 150, "moderate"),
        ("Latsdrag", 4, 10, 90, "moderate"),
        ("Seated Cable Row", 3, 10, 90, "moderate"),
        ("Face Pulls", 3, 15, 60, "light"),
        ("Bicepscurl", 3, 12, 60, "light"),
    ]

    # Strength phase — vecka 5-8
    strength_squat = [
        ("Knäböj", 5, 5, 180, "heavy"),
        ("Romanian Deadlift", 4, 6, 150, "heavy"),
        ("Bulgarian Split Squat", 3, 8, 90, "moderate"),
        ("Leg Curl", 3, 10, 75, "moderate"),
    ]

    strength_bench = [
        ("Bänkpress", 5, 5, 180, "heavy"),
        ("Incline Bänkpress", 4, 6, 150, "heavy"),
        ("Dips", 3, 8, 90, "moderate"),
        ("Skull Crushers", 3, 8, 75, "moderate"),
    ]

    strength_deadlift = [
        ("Marklyft", 5, 5, 180, "heavy"),
        ("Latsdrag", 4, 8, 120, "heavy"),
        ("Seated Cable Row", 4, 8, 90, "heavy"),
        ("Face Pulls", 3, 12, 60, "light"),
    ]

    # Peaking phase — vecka 9-12
    peak_squat = [
        ("Knäböj", 6, 3, 210, "heavy"),
        ("Romanian Deadlift", 3, 5, 150, "heavy"),
        ("Leg Press", 3, 8, 90, "moderate"),
    ]

    peak_bench = [
        ("Bänkpress", 6, 3, 210, "heavy"),
        ("Incline Bänkpress", 3, 5, 150, "heavy"),
        ("Tricepspress", 3, 10, 60, "light"),
    ]

    peak_deadlift = [
        ("Marklyft", 6, 3, 210, "heavy"),
        ("Latsdrag", 3, 8, 90, "moderate"),
        ("Seated Cable Row", 3, 8, 90, "moderate"),
    ]

    # Competition prep — vecka 13-15
    comp_squat = [
        ("Knäböj", 4, 2, 240, "heavy"),
        ("Leg Press", 2, 8, 90, "light"),
    ]

    comp_bench = [
        ("Bänkpress", 4, 2, 240, "heavy"),
        ("Cable Flyes", 2, 12, 60, "light"),
    ]

    comp_deadlift = [
        ("Marklyft", 4, 2, 240, "heavy"),
        ("Latsdrag", 2, 8, 90, "light"),
    ]

    # Deload — vecka 16
    deload = [
        ("Knäböj", 2, 5, 120, "light"),
        ("Bänkpress", 2, 5, 120, "light"),
        ("Marklyft", 2, 3, 150, "light"),
    ]

    phases = {
        range(1, 5): {
            "name": "Hypertrophy",
            "days": [
                (1, "Squat Day", "Squat focus + accessories", hypertrophy_squat),
                (2, "Bench Day", "Bench focus + accessories", hypertrophy_bench),
                (3, "Rest", "Rest", []),
                (4, "Deadlift Day", "Deadlift focus + accessories", hypertrophy_deadlift),
                (5, "Bench Day B", "Bench volume", hypertrophy_bench),
                (6, "Rest", "Rest", []),
                (7, "Rest", "Full rest", []),
            ]
        },
        range(5, 9): {
            "name": "Strength",
            "days": [
                (1, "Squat Heavy", "Heavy squat", strength_squat),
                (2, "Bench Heavy", "Heavy bench", strength_bench),
                (3, "Rest", "Rest", []),
                (4, "Deadlift Heavy", "Heavy deadlift", strength_deadlift),
                (5, "Bench Volume", "Bench volume", strength_bench),
                (6, "Rest", "Rest", []),
                (7, "Rest", "Full rest", []),
            ]
        },
        range(9, 13): {
            "name": "Peaking",
            "days": [
                (1, "Squat Peak", "Peak squat", peak_squat),
                (2, "Bench Peak", "Peak bench", peak_bench),
                (3, "Rest", "Rest", []),
                (4, "Deadlift Peak", "Peak deadlift", peak_deadlift),
                (5, "Bench Peak B", "Peak bench", peak_bench),
                (6, "Rest", "Rest", []),
                (7, "Rest", "Full rest", []),
            ]
        },
        range(13, 16): {
            "name": "Competition Prep",
            "days": [
                (1, "Squat Opener", "Competition prep squat", comp_squat),
                (2, "Bench Opener", "Competition prep bench", comp_bench),
                (3, "Rest", "Rest", []),
                (4, "Deadlift Opener", "Competition prep deadlift", comp_deadlift),
                (5, "Rest", "Rest", []),
                (6, "Rest", "Rest", []),
                (7, "Rest", "Full rest", []),
            ]
        },
        range(16, 17): {
            "name": "Deload",
            "days": [
                (1, "Deload Day", "Light full body deload", deload),
                (2, "Rest", "Rest", []),
                (3, "Deload Day B", "Light full body deload", deload),
                (4, "Rest", "Rest", []),
                (5, "Rest", "Rest", []),
                (6, "Rest", "Rest", []),
                (7, "Rest", "Full rest", []),
            ]
        },
    }

    total_days = 0
    for week_range, phase_data in phases.items():
        for week in week_range:
            for day_num, day_name, focus, exercises in phase_data["days"]:
                is_rest = len(exercises) == 0
                day_id = add_day(conn, plan_id, week, day_num,
                    f"Week {week} — {day_name} ({phase_data['name']})",
                    focus, is_rest=is_rest)
                if not is_rest:
                    for order, (ex_name, sets, reps, rest, intensity) in enumerate(exercises, 1):
                        ex_id = get_exercise_id(conn, ex_name)
                        add_exercise(conn, day_id, ex_id, sets, reps, rest, intensity, order)
                    total_days += 1

    conn.commit()
    log.info(f"Powerlifting program created! {total_days} training days added.")
    log.info("Phase 1 (Week 1-4):   Hypertrophy — build the base")
    log.info("Phase 2 (Week 5-8):   Strength — get stronger")
    log.info("Phase 3 (Week 9-12):  Peaking — peak performance")
    log.info("Phase 4 (Week 13-15): Competition prep — opener selection")
    log.info("Phase 5 (Week 16):    Deload — taper for competition")
    return plan_id


if __name__ == "__main__":
    log.info("Starting program seeder...")
    with engine.connect() as conn:
        seed_beginner_program(conn)
        seed_upper_lower_program(conn)
        seed_fat_loss_program(conn)
        seed_bulk_program(conn)
        seed_powerlifting_program(conn)
    log.info("All programs created!")