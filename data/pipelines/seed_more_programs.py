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

def add_yoga_exercises(conn):
    """Lägger till riktiga yogaövningar i databasen."""
    log.info("Adding yoga exercises...")
    yoga_exercises = [
        ("Downward Dog", 6, 1, "nybörjare", "stretching", "Start on hands and knees, lift hips up and back forming an inverted V", "Press heels toward floor, keep spine long", 2.5),
        ("Child's Pose", 6, 1, "nybörjare", "stretching", "Kneel and fold forward, arms extended or alongside body", "Breathe deeply into lower back", 1.5),
        ("Warrior I", 3, 1, "nybörjare", "balans", "Lunge forward with back foot turned 45 degrees, arms raised overhead", "Square hips toward front", 3.0),
        ("Warrior II", 3, 1, "nybörjare", "balans", "Wide stance with front knee bent, arms extended parallel to floor", "Gaze over front fingertips", 3.0),
        ("Pigeon Pose", 3, 1, "nybörjare", "stretching", "Front leg bent at 90 degrees, back leg extended, fold forward", "Great for hip flexors and glutes", 2.0),
        ("Cat-Cow", 6, 1, "nybörjare", "stretching", "On hands and knees, alternate arching and rounding spine with breath", "Move slowly with each breath", 2.0),
        ("Seated Forward Fold", 3, 1, "nybörjare", "stretching", "Sit with legs extended, fold forward reaching for feet", "Keep spine long, bend knees if needed", 2.0),
        ("Bridge Pose", 3, 1, "nybörjare", "styrka", "Lie on back, feet flat, lift hips toward ceiling", "Squeeze glutes at top", 3.5),
        ("Supine Twist", 6, 1, "nybörjare", "stretching", "Lie on back, bring knee across body for spinal rotation", "Keep shoulders flat on floor", 1.5),
        ("Mountain Pose", 6, 1, "nybörjare", "balans", "Stand tall, feet together, arms alongside body", "Engage all muscles, breathe deeply", 1.5),
        ("Tree Pose", 3, 1, "nybörjare", "balans", "Stand on one leg, place other foot on inner thigh or calf", "Find a fixed point to gaze at", 2.5),
        ("Cobra Pose", 1, 1, "nybörjare", "stretching", "Lie face down, press up through hands lifting chest", "Keep elbows slightly bent", 2.5),
    ]
    for ex in yoga_exercises:
        existing = conn.execute(text(
            "SELECT id FROM exercises WHERE name = :name"
        ), {"name": ex[0]}).fetchone()
        if not existing:
            conn.execute(text("""
                INSERT INTO exercises
                    (name, body_part_id, equipment_id, difficulty, exercise_type,
                     description, tips, calories_per_minute)
                VALUES (:name, :bp, :eq, :diff, :type, :desc, :tips, :cal)
            """), {
                "name": ex[0], "bp": ex[1], "eq": ex[2], "diff": ex[3],
                "type": ex[4], "desc": ex[5], "tips": ex[6], "cal": ex[7]
            })
    conn.commit()
    log.info("Yoga exercises added!")

def seed_beginner_program(conn):
    log.info("Creating Beginner Full Body Program...")
    plan_id = create_program(conn,
        name="Beginner Full Body — 8 Week",
        goal="hålla_sig_i_form",
        difficulty="nybörjare",
        duration_weeks=8,
        days_per_week=3,
        description="A simple 3-day full body program for complete beginners. Week 1-4: 3x10 at 60% 1RM learning form. Week 5-8: 3-4x8 at 70% 1RM adding load. Progressive overload: add 2.5kg when you complete all reps with good form.",
        target_audience="Complete beginners with no gym experience"
    )
    full_body = [
        ("Knäböj",      3, 10, 90,  "light"),
        ("Bänkpress",   3, 10, 90,  "light"),
        ("Marklyft",    3, 8,  120, "light"),
        ("Latsdrag",    3, 10, 90,  "light"),
        ("Militärpress",3, 10, 90,  "light"),
        ("Plankan",     3, 30, 60,  "light"),
    ]
    total_days = 0
    for week in range(1, 9):
        sets_mult = 1.0 if week <= 4 else 1.1
        for day_num, day_name in [(1, "Day 1"), (2, "Day 2"), (3, "Day 3")]:
            day_id = add_day(conn, plan_id, week, day_num,
                f"Week {week} — Full Body {day_name} | +2.5kg when all reps completed",
                "Full body compound movements | RPE target: 6-7/10")
            for order, (ex_name, sets, reps, rest, intensity) in enumerate(full_body, 1):
                ex_id = get_exercise_id(conn, ex_name)
                add_exercise(conn, day_id, ex_id,
                    max(2, round(sets * sets_mult)), reps, rest, intensity, order)
            total_days += 1
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
        description="A 4-day Upper/Lower split with progressive overload. Upper A: heavy 4x6 at 80-85% 1RM. Upper B: volume 4x10 at 70% 1RM. Add 2.5kg on upper lifts and 5kg on lower lifts each week when all reps completed.",
        target_audience="Intermediate lifters with 6+ months of training experience"
    )
    upper_a = [
        ("Bänkpress",       4, 6,  150, "heavy"),
        ("Latsdrag",        4, 8,  90,  "heavy"),
        ("Militärpress",    3, 8,  90,  "heavy"),
        ("Seated Cable Row",3, 8,  90,  "heavy"),
        ("Skull Crushers",  3, 10, 75,  "moderate"),
        ("Bicepscurl",      3, 10, 75,  "moderate"),
    ]
    upper_b = [
        ("Incline Bänkpress",4, 10, 90, "moderate"),
        ("Pull-ups",         4, 10, 90, "moderate"),
        ("Cable Flyes",      3, 12, 60, "light"),
        ("Face Pulls",       3, 15, 60, "light"),
        ("Lateral Raises",   4, 15, 60, "light"),
        ("Hammer Curl",      3, 12, 60, "light"),
    ]
    lower_a = [
        ("Knäböj",          4, 6,  150, "heavy"),
        ("Romanian Deadlift",3, 8,  90,  "heavy"),
        ("Leg Press",        3, 10, 90,  "moderate"),
        ("Leg Curl",         3, 12, 60,  "light"),
        ("Calf Raises",      4, 15, 45,  "light"),
    ]
    lower_b = [
        ("Marklyft",            4, 6,  150, "heavy"),
        ("Bulgarian Split Squat",3, 10, 90,  "moderate"),
        ("Leg Extension",        3, 12, 60,  "light"),
        ("Hip Thrust",           3, 12, 90,  "moderate"),
        ("Calf Raises",          4, 15, 45,  "light"),
    ]
    days_structure = [
        (1, "Upper A", "Chest, Back, Shoulders, Arms — Strength | RPE 8/10", upper_a),
        (2, "Lower A", "Quads, Hamstrings, Calves — Strength | RPE 8/10", lower_a),
        (3, "Rest", "Active recovery — light walk or mobility", []),
        (4, "Upper B", "Chest, Back, Shoulders, Arms — Volume | RPE 7/10", upper_b),
        (5, "Lower B", "Quads, Hamstrings, Glutes — Volume | RPE 7/10", lower_b),
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
        description="A high-intensity 5-day circuit combining strength and cardio. Target heart rate Zone 3-4 (70-85% max HR) during circuits. 30 sec rest between exercises, 2 min between rounds. Aim to reduce rest time each week.",
        target_audience="Anyone looking to lose body fat while maintaining muscle mass"
    )
    circuit_a = [
        ("Knäböj",   3, 15, 30, "light"),
        ("Bänkpress",3, 12, 30, "light"),
        ("Utfall",   3, 12, 30, "light"),
        ("Latsdrag", 3, 12, 30, "light"),
        ("Plankan",  3, 45, 30, "light"),
        ("Burpees",  3, 10, 45, "moderate"),
    ]
    circuit_b = [
        ("Marklyft",    3, 12, 30, "light"),
        ("Militärpress",3, 12, 30, "light"),
        ("Knäböj",      3, 15, 30, "light"),
        ("Bicepscurl",  3, 15, 30, "light"),
        ("Tricepspress",3, 15, 30, "light"),
        ("Burpees",     4, 12, 45, "moderate"),
    ]
    days_structure = [
        (1, "Circuit A", "Full body circuit | Target: Zone 3-4 HR (70-85%)", circuit_a),
        (2, "Circuit B", "Full body circuit | Target: Zone 3-4 HR (70-85%)", circuit_b),
        (3, "Zone 2 Cardio", "30-45 min Zone 2 cardio (60-70% max HR) — run, bike or row", []),
        (4, "Circuit A", "Full body circuit | Target: Zone 3-4 HR (70-85%)", circuit_a),
        (5, "Circuit B", "Full body circuit | Target: Zone 3-4 HR (70-85%)", circuit_b),
        (6, "Rest", "Active recovery — light walk", []),
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
        description="Heavy compound program for maximum strength and muscle gain. Progressive overload: add 5kg to squat/deadlift and 2.5kg to bench/press each week. Eat 300-500 kcal above TDEE. RPE target 8-9/10 on main lifts.",
        target_audience="Advanced lifters looking to gain serious size and strength"
    )
    heavy_push = [
        ("Bänkpress",       5, 5, 180, "heavy"),
        ("Incline Bänkpress",4, 6, 150, "heavy"),
        ("Militärpress",    4, 5, 150, "heavy"),
        ("Dips",            3, 8, 90,  "heavy"),
        ("Lateral Raises",  3, 12, 60, "moderate"),
    ]
    heavy_pull = [
        ("Marklyft",        5, 5, 180, "heavy"),
        ("Pull-ups",        4, 6, 120, "heavy"),
        ("Latsdrag",        4, 8, 90,  "heavy"),
        ("Seated Cable Row",3, 8, 90,  "heavy"),
        ("Bicepscurl",      3, 10, 75, "moderate"),
    ]
    heavy_legs = [
        ("Knäböj",              5, 5, 180, "heavy"),
        ("Romanian Deadlift",   4, 6, 150, "heavy"),
        ("Leg Press",           4, 8, 120, "heavy"),
        ("Bulgarian Split Squat",3, 8, 90, "moderate"),
        ("Calf Raises",         5, 12, 45, "moderate"),
    ]
    days_structure = [
        (1, "Heavy Push", "Chest, Shoulders, Triceps | RPE 8-9", heavy_push),
        (2, "Heavy Pull", "Back, Biceps | RPE 8-9", heavy_pull),
        (3, "Heavy Legs", "Quads, Hamstrings, Glutes | RPE 8-9", heavy_legs),
        (4, "Rest", "Rest or light mobility work", []),
        (5, "Heavy Push B", "Chest, Shoulders, Triceps | RPE 8-9", heavy_push),
        (6, "Heavy Pull + Legs", "Back, Biceps, Legs | RPE 7-8", heavy_pull),
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
        description="A 16-week periodized powerlifting peaking program. Phase 1 Hypertrophy (W1-4): 4x8 at 70% 1RM. Phase 2 Strength (W5-8): 5x5 at 80% 1RM. Phase 3 Peaking (W9-12): 6x3 at 87-92% 1RM. Phase 4 Comp Prep (W13-15): 4x2 at 93-95% 1RM. Week 16: Deload at 50% volume.",
        target_audience="Advanced lifters who want to maximize their squat, bench and deadlift"
    )
    hypertrophy_squat = [
        ("Knäböj",          4, 8,  120, "moderate"),
        ("Romanian Deadlift",3, 10, 90,  "moderate"),
        ("Leg Press",        3, 12, 90,  "light"),
        ("Leg Curl",         3, 12, 60,  "light"),
        ("Calf Raises",      3, 15, 45,  "light"),
    ]
    hypertrophy_bench = [
        ("Bänkpress",       4, 8,  120, "moderate"),
        ("Incline Bänkpress",3, 10, 90,  "moderate"),
        ("Cable Flyes",      3, 12, 60,  "light"),
        ("Tricepspress",     3, 12, 60,  "light"),
        ("Lateral Raises",   3, 15, 60,  "light"),
    ]
    hypertrophy_deadlift = [
        ("Marklyft",        4, 6,  150, "moderate"),
        ("Latsdrag",        4, 10, 90,  "moderate"),
        ("Seated Cable Row",3, 10, 90,  "moderate"),
        ("Face Pulls",      3, 15, 60,  "light"),
        ("Bicepscurl",      3, 12, 60,  "light"),
    ]
    strength_squat = [
        ("Knäböj",              5, 5, 180, "heavy"),
        ("Romanian Deadlift",   4, 6, 150, "heavy"),
        ("Bulgarian Split Squat",3, 8, 90, "moderate"),
        ("Leg Curl",            3, 10, 75, "moderate"),
    ]
    strength_bench = [
        ("Bänkpress",       5, 5, 180, "heavy"),
        ("Incline Bänkpress",4, 6, 150, "heavy"),
        ("Dips",            3, 8, 90,  "moderate"),
        ("Skull Crushers",  3, 8, 75,  "moderate"),
    ]
    strength_deadlift = [
        ("Marklyft",        5, 5, 180, "heavy"),
        ("Latsdrag",        4, 8, 120, "heavy"),
        ("Seated Cable Row",4, 8, 90,  "heavy"),
        ("Face Pulls",      3, 12, 60, "light"),
    ]
    peak_squat = [
        ("Knäböj",          6, 3, 210, "heavy"),
        ("Romanian Deadlift",3, 5, 150, "heavy"),
        ("Leg Press",        3, 8, 90,  "moderate"),
    ]
    peak_bench = [
        ("Bänkpress",       6, 3, 210, "heavy"),
        ("Incline Bänkpress",3, 5, 150, "heavy"),
        ("Tricepspress",    3, 10, 60, "light"),
    ]
    peak_deadlift = [
        ("Marklyft",        6, 3, 210, "heavy"),
        ("Latsdrag",        3, 8, 90,  "moderate"),
        ("Seated Cable Row",3, 8, 90,  "moderate"),
    ]
    comp_squat = [
        ("Knäböj",  4, 2, 240, "heavy"),
        ("Leg Press",2, 8, 90, "light"),
    ]
    comp_bench = [
        ("Bänkpress", 4, 2, 240, "heavy"),
        ("Cable Flyes",2, 12, 60, "light"),
    ]
    comp_deadlift = [
        ("Marklyft",  4, 2, 240, "heavy"),
        ("Latsdrag",  2, 8, 90,  "light"),
    ]
    deload = [
        ("Knäböj",   2, 5, 120, "light"),
        ("Bänkpress",2, 5, 120, "light"),
        ("Marklyft", 2, 3, 150, "light"),
    ]
    phases = {
        range(1, 5): {"name": "Hypertrophy", "days": [
            (1, "Squat Day", "Squat 4x8 @ 70% 1RM + accessories", hypertrophy_squat),
            (2, "Bench Day", "Bench 4x8 @ 70% 1RM + accessories", hypertrophy_bench),
            (3, "Rest", "Rest", []),
            (4, "Deadlift Day", "Deadlift 4x6 @ 70% 1RM + accessories", hypertrophy_deadlift),
            (5, "Bench Day B", "Bench volume", hypertrophy_bench),
            (6, "Rest", "Rest", []),
            (7, "Rest", "Full rest", []),
        ]},
        range(5, 9): {"name": "Strength", "days": [
            (1, "Squat Heavy", "Squat 5x5 @ 80% 1RM", strength_squat),
            (2, "Bench Heavy", "Bench 5x5 @ 80% 1RM", strength_bench),
            (3, "Rest", "Rest", []),
            (4, "Deadlift Heavy", "Deadlift 5x5 @ 80% 1RM", strength_deadlift),
            (5, "Bench Volume", "Bench volume work", strength_bench),
            (6, "Rest", "Rest", []),
            (7, "Rest", "Full rest", []),
        ]},
        range(9, 13): {"name": "Peaking", "days": [
            (1, "Squat Peak", "Squat 6x3 @ 87-92% 1RM", peak_squat),
            (2, "Bench Peak", "Bench 6x3 @ 87-92% 1RM", peak_bench),
            (3, "Rest", "Rest", []),
            (4, "Deadlift Peak", "Deadlift 6x3 @ 87-92% 1RM", peak_deadlift),
            (5, "Bench Peak B", "Bench peaking work", peak_bench),
            (6, "Rest", "Rest", []),
            (7, "Rest", "Full rest", []),
        ]},
        range(13, 16): {"name": "Competition Prep", "days": [
            (1, "Squat Opener", "Squat 4x2 @ 93-95% 1RM — opener selection", comp_squat),
            (2, "Bench Opener", "Bench 4x2 @ 93-95% 1RM — opener selection", comp_bench),
            (3, "Rest", "Rest", []),
            (4, "Deadlift Opener", "Deadlift 4x2 @ 93-95% 1RM — opener selection", comp_deadlift),
            (5, "Rest", "Rest", []),
            (6, "Rest", "Rest", []),
            (7, "Rest", "Full rest", []),
        ]},
        range(16, 17): {"name": "Deload", "days": [
            (1, "Deload Day", "50% volume deload — let the body recover", deload),
            (2, "Rest", "Rest", []),
            (3, "Deload Day B", "50% volume deload", deload),
            (4, "Rest", "Rest", []),
            (5, "Rest", "Rest", []),
            (6, "Rest", "Rest", []),
            (7, "Rest", "Full rest", []),
        ]},
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
    return plan_id

def seed_running_programs(conn):
    log.info("Creating Running Programs with heart rate zones...")

    # 5K Program
    plan_5k = create_program(conn,
        name="5K Running Plan — 8 Week",
        goal="öka_kondition",
        difficulty="nybörjare",
        duration_weeks=8,
        days_per_week=3,
        description="Beginner 8-week 5K plan using heart rate zones. Zone 1 (50-60% max HR): very easy. Zone 2 (60-70%): aerobic base — conversational pace. Zone 3 (70-80%): tempo — comfortably hard. All easy runs in Zone 2. Max HR = 220 minus your age.",
        target_audience="Complete beginners who want to start running"
    )
    running_5k_structure = [
        (1, [
            (1, "Zone 1-2: Run 1 min, Walk 2 min x8 (60-70% HR)", 24),
            (3, "Zone 1-2: Run 1 min, Walk 2 min x8 (60-70% HR)", 24),
            (5, "Zone 1-2: Run 1 min, Walk 2 min x10 (60-70% HR)", 30),
        ]),
        (2, [
            (1, "Zone 2: Run 2 min, Walk 1 min x7 (65-70% HR)", 21),
            (3, "Zone 2: Run 2 min, Walk 1 min x7 (65-70% HR)", 21),
            (5, "Zone 2: Run 3 min, Walk 1 min x5 (65-70% HR)", 20),
        ]),
        (3, [
            (1, "Zone 2: Run 5 min, Walk 1 min x4 (65-70% HR)", 24),
            (3, "Zone 2: Run 5 min, Walk 1 min x4 (65-70% HR)", 24),
            (5, "Zone 2-3: Run 8 min, Walk 1 min x3 (70-75% HR)", 27),
        ]),
        (4, [
            (1, "Zone 2: Run 10 min continuous (65-70% HR)", 10),
            (3, "Zone 2: Run 10 min continuous (65-70% HR)", 10),
            (5, "Zone 2: Run 15 min continuous (65-70% HR)", 15),
        ]),
        (5, [
            (1, "Zone 2: Run 20 min continuous (65-70% HR)", 20),
            (3, "Zone 2-3: Run 20 min (70-75% HR)", 20),
            (5, "Zone 2: Run 25 min continuous (65-70% HR)", 25),
        ]),
        (6, [
            (1, "Zone 2: Run 25 min (65-70% HR)", 25),
            (3, "Zone 3: Tempo 25 min (75-80% HR)", 25),
            (5, "Zone 2: Run 28 min continuous (65-70% HR)", 28),
        ]),
        (7, [
            (1, "Zone 2: Run 25 min (65-70% HR)", 25),
            (3, "Zone 3: Tempo 28 min (75-80% HR)", 28),
            (5, "Zone 2: Run 30 min continuous (65-70% HR)", 30),
        ]),
        (8, [
            (1, "Zone 2: Easy 30 min (65-70% HR)", 30),
            (3, "Zone 1: Easy 20 min recovery run", 20),
            (5, "Zone 2-3: 5K Race or Time Trial!", 30),
        ]),
    ]
    for week, days in running_5k_structure:
        for day_num, focus, duration in days:
            day_id = add_day(conn, plan_5k, week, day_num,
                f"Week {week} — Run Day", focus)
            ex_id = get_exercise_id(conn, "Löpning")
            add_exercise(conn, day_id, ex_id, 1, duration, 60, "light", 1)
        for rest_day in [2, 4, 6, 7]:
            add_day(conn, plan_5k, week, rest_day,
                f"Week {week} — Rest", "Rest or easy walk", is_rest=True)
    conn.commit()
    log.info("5K program with heart rate zones created!")

    # 10K Program
    plan_10k = create_program(conn,
        name="10K Running Plan — 10 Week",
        goal="öka_kondition",
        difficulty="medel",
        duration_weeks=10,
        days_per_week=4,
        description="10-week 10K plan with structured heart rate zones. Easy runs: Zone 2 (60-70% max HR). Tempo runs: Zone 3 (70-80% max HR). Long runs: Zone 2. Every 4th week is a deload week at 70% volume. Add 10% distance per week maximum.",
        target_audience="Runners who can already run 5km and want to double their distance"
    )
    for week in range(1, 11):
        is_deload = week % 4 == 0
        base_long = 6 + (week * 0.5) if not is_deload else 5
        base_easy = 4 + (week * 0.3) if not is_deload else 3
        days = [
            (1, f"Zone 2 Easy run {base_easy:.0f}km (60-70% HR)", round(base_easy * 6), "light"),
            (3, f"Zone 3 Tempo run {base_easy:.0f}km (75-80% HR)", round(base_easy * 5), "moderate"),
            (5, f"Zone 2 Easy run {base_easy:.0f}km (60-70% HR)", round(base_easy * 6), "light"),
            (6, f"Zone 2 Long run {base_long:.0f}km (60-70% HR)", round(base_long * 6), "moderate"),
        ]
        for day_num, focus, duration, intensity in days:
            day_id = add_day(conn, plan_10k, week, day_num,
                f"Week {week} — {focus}", focus)
            ex_id = get_exercise_id(conn, "Löpning")
            add_exercise(conn, day_id, ex_id, 1, duration, 60, intensity, 1)
        for rest_day in [2, 4, 7]:
            add_day(conn, plan_10k, week, rest_day,
                f"Week {week} — Rest", "Rest or cross training", is_rest=True)
    conn.commit()
    log.info("10K program with heart rate zones created!")

    # Halvmaraton
    plan_half = create_program(conn,
        name="Half Marathon Plan — 14 Week",
        goal="öka_kondition",
        difficulty="avancerad",
        duration_weeks=14,
        days_per_week=5,
        description="14-week half marathon plan with 5 heart rate zones. Easy runs Zone 2 (60-70%). Intervals Zone 4-5 (85-95%). Tempo Zone 3 (75-80%). Long run Zone 2 peaking at 19km. Week 13-14: taper to 50% volume. Never increase weekly distance more than 10%.",
        target_audience="Experienced runners who can run 10km and want to complete a half marathon"
    )
    for week in range(1, 15):
        is_taper = week >= 13
        is_deload = week % 4 == 0 and not is_taper
        long_run = min(19, 8 + week) if not is_taper else (10 if week == 13 else 5)
        days = [
            (1, f"Zone 2 Easy run 6km (60-70% HR)", 36, "light"),
            (2, f"Zone 4-5 Intervals 5km (85-95% HR) — 6x800m with 90s rest", 30, "heavy"),
            (4, f"Zone 3 Tempo run 8km (75-80% HR)", 44, "moderate"),
            (5, f"Zone 2 Easy run 6km (60-70% HR)", 36, "light"),
            (6, f"Zone 2 Long run {long_run}km (60-70% HR)", long_run * 6, "moderate"),
        ]
        if is_deload:
            days = [(d, f, max(20, int(dur * 0.7)), i) for d, f, dur, i in days]
        if is_taper:
            days = [(d, f, max(15, int(dur * 0.5)), "light") for d, f, dur, i in days]
        for day_num, focus, duration, intensity in days:
            day_id = add_day(conn, plan_half, week, day_num,
                f"Week {week} — {focus}", focus)
            ex_id = get_exercise_id(conn, "Löpning")
            add_exercise(conn, day_id, ex_id, 1, duration, 60, intensity, 1)
        for rest_day in [3, 7]:
            add_day(conn, plan_half, week, rest_day,
                f"Week {week} — Rest", "Rest or easy walk", is_rest=True)
    conn.commit()
    log.info("Half Marathon program with heart rate zones created!")

def seed_yoga_program(conn):
    log.info("Creating Yoga & Mobility Program with real yoga exercises...")
    add_yoga_exercises(conn)

    plan_id = create_program(conn,
        name="Yoga & Mobility — 8 Week",
        goal="hålla_sig_i_form",
        difficulty="nybörjare",
        duration_weeks=8,
        days_per_week=5,
        description="An 8-week yoga and mobility program using evidence-based movement patterns. Each session targets specific areas: hips, spine, shoulders, hamstrings and full body. Hold each pose 30-60 seconds. Breathe deeply throughout. Perfect complement to strength training.",
        target_audience="Anyone who wants to improve flexibility, mobility and recovery"
    )

    sessions = {
        "Morning Flow": [
            ("Mountain Pose", 2, 30, 15, "light"),
            ("Downward Dog", 3, 30, 20, "light"),
            ("Cat-Cow", 3, 10, 15, "light"),
            ("Cobra Pose", 3, 30, 20, "light"),
            ("Child's Pose", 2, 45, 15, "light"),
        ],
        "Hip & Lower Body": [
            ("Warrior I", 3, 30, 15, "light"),
            ("Warrior II", 3, 30, 15, "light"),
            ("Pigeon Pose", 3, 45, 20, "light"),
            ("Seated Forward Fold", 3, 45, 20, "light"),
            ("Supine Twist", 2, 45, 15, "light"),
        ],
        "Upper Body & Shoulders": [
            ("Downward Dog", 3, 30, 15, "light"),
            ("Cobra Pose", 3, 30, 20, "light"),
            ("Cat-Cow", 3, 10, 15, "light"),
            ("Warrior I", 3, 30, 15, "light"),
            ("Child's Pose", 2, 45, 15, "light"),
        ],
        "Core & Balance": [
            ("Mountain Pose", 2, 30, 15, "light"),
            ("Tree Pose", 3, 30, 15, "light"),
            ("Warrior II", 3, 30, 15, "light"),
            ("Bridge Pose", 3, 30, 20, "light"),
            ("Supine Twist", 2, 45, 15, "light"),
        ],
        "Full Body Stretch": [
            ("Cat-Cow", 2, 10, 15, "light"),
            ("Downward Dog", 3, 30, 20, "light"),
            ("Pigeon Pose", 3, 45, 20, "light"),
            ("Seated Forward Fold", 3, 45, 20, "light"),
            ("Supine Twist", 3, 45, 15, "light"),
            ("Child's Pose", 2, 60, 15, "light"),
        ],
    }

    session_days = [
        (1, "Morning Flow", "Full body gentle yoga flow — wake up the body"),
        (2, "Hip & Lower Body", "Hip flexors, hamstrings, glutes — great after leg day"),
        (3, "Upper Body & Shoulders", "Chest, shoulders, thoracic spine — great after push day"),
        (4, "Core & Balance", "Core stability and single-leg balance work"),
        (5, "Full Body Stretch", "Deep stretching and full body relaxation"),
    ]

    for week in range(1, 9):
        for day_num, session_name, focus in session_days:
            day_id = add_day(conn, plan_id, week, day_num,
                f"Week {week} — {session_name}", focus)
            for order, (ex_name, sets, reps, rest, intensity) in enumerate(sessions[session_name], 1):
                ex_id = get_exercise_id(conn, ex_name)
                add_exercise(conn, day_id, ex_id, sets, reps, rest, intensity, order)
        for rest_day in [6, 7]:
            add_day(conn, plan_id, week, rest_day,
                f"Week {week} — Rest", "Full rest or gentle walk", is_rest=True)

    conn.commit()
    log.info("Yoga & Mobility program with real yoga poses created!")

def seed_home_workout_program(conn):
    log.info("Creating Home Workout Program...")
    plan_id = create_program(conn,
        name="Home Workout — Bodyweight 12 Week",
        goal="hålla_sig_i_form",
        difficulty="nybörjare",
        duration_weeks=12,
        days_per_week=4,
        description="12-week bodyweight program you can do anywhere. Progressive overload through rep increases: Week 1-4 baseline, Week 5-8 add 2 reps per set, Week 9-12 add 4 reps per set. Rest 60-90 seconds between sets. RPE target 7-8/10.",
        target_audience="Anyone who wants to train at home or while traveling with no equipment"
    )
    push_bodyweight = [
        ("Dips",   4, 10, 60, "moderate"),
        ("Plankan",3, 45, 45, "light"),
        ("Burpees",3, 10, 60, "moderate"),
    ]
    pull_bodyweight = [
        ("Pull-ups",  4, 8,  90, "moderate"),
        ("Face Pulls",3, 15, 45, "light"),
        ("Plankan",   3, 45, 45, "light"),
    ]
    legs_bodyweight = [
        ("Knäböj",              4, 15, 60, "light"),
        ("Utfall",              3, 12, 60, "light"),
        ("Bulgarian Split Squat",3, 10, 75, "moderate"),
        ("Calf Raises",         4, 20, 30, "light"),
    ]
    core_bodyweight = [
        ("Plankan",3, 60, 45, "moderate"),
        ("Burpees",3, 12, 60, "moderate"),
        ("Utfall", 3, 15, 45, "light"),
    ]
    days_structure = [
        (1, "Push Day", "Chest, Shoulders, Triceps — Bodyweight | RPE 7-8", push_bodyweight),
        (2, "Legs Day", "Quads, Hamstrings, Glutes — Bodyweight | RPE 7-8", legs_bodyweight),
        (3, "Rest", "Rest or light walk", []),
        (4, "Pull Day", "Back, Biceps — Bodyweight | RPE 7-8", pull_bodyweight),
        (5, "Core Day", "Core, Cardio — Bodyweight | RPE 7-8", core_bodyweight),
        (6, "Rest", "Rest", []),
        (7, "Rest", "Full rest", []),
    ]
    total_days = 0
    for week in range(1, 13):
        is_deload = week == 12
        sets_mult = 1.0 if week <= 4 else 1.1 if week <= 8 else 1.2
        for day_num, day_name, focus, exercises in days_structure:
            is_rest = len(exercises) == 0
            day_id = add_day(conn, plan_id, week, day_num,
                f"Week {week} — {day_name}", focus, is_rest=is_rest)
            if not is_rest:
                for order, (ex_name, sets, reps, rest, intensity) in enumerate(exercises, 1):
                    ex_id = get_exercise_id(conn, ex_name)
                    actual_sets = max(2, round(sets * (0.5 if is_deload else sets_mult)))
                    add_exercise(conn, day_id, ex_id, actual_sets, reps, rest, intensity, order)
                total_days += 1
    conn.commit()
    log.info(f"Home Workout program created! {total_days} training days added.")

if __name__ == "__main__":
    log.info("Starting program seeder...")
    with engine.connect() as conn:
        seed_beginner_program(conn)
        seed_upper_lower_program(conn)
        seed_fat_loss_program(conn)
        seed_bulk_program(conn)
        seed_powerlifting_program(conn)
        seed_running_programs(conn)
        seed_yoga_program(conn)
        seed_home_workout_program(conn)
    log.info("All programs created!")