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

def seed_women_exercises(conn):
    """Lägger till kvinnospecifika övningar med vetenskaplig grund."""
    log.info("Adding women-specific exercises...")

    women_exercises = [
        # Glutes & Höfter (body_part_id=3, equipment_id=1=ingen)
        ("Hip Abduction Machine", 3, 1, "nybörjare", "styrka",
         "Sit in hip abduction machine and push knees outward against resistance",
         "Research shows this is one of the most effective glute med exercises. 3x15-20 reps.",
         4.5, None, None, "Glutes", "Hip Abductors"),

        ("Cable Kickback", 3, 4, "nybörjare", "styrka",
         "Attach ankle strap to cable, kick leg back and up for glute isolation",
         "Keep torso stable, squeeze glute at top. Higher reps (15-20) work best.",
         4.0, None, None, "Glutes", "Hamstrings"),

        ("Donkey Kicks", 3, 1, "nybörjare", "styrka",
         "On hands and knees, kick one heel toward ceiling squeezing glute",
         "Don't rotate hips, focus on glute contraction. Add ankle weight for progression.",
         3.5, None, None, "Glutes", None),

        ("Fire Hydrants", 3, 1, "nybörjare", "styrka",
         "On hands and knees, lift knee out to the side like a dog at a fire hydrant",
         "Targets gluteus medius. Keep core braced, don't shift weight.",
         3.0, None, None, "Glutes", "Hip Abductors"),

        ("Sumo Squat", 3, 2, "nybörjare", "styrka",
         "Wide stance squat with toes pointed outward for inner thigh and glute emphasis",
         "Research shows sumo stance increases glute activation vs narrow stance.",
         8.5, None, None, "Glutes", "Inner Thighs, Quadriceps"),

        ("Curtsy Lunge", 3, 2, "nybörjare", "styrka",
         "Step one foot behind and across the other in a curtsy motion",
         "Excellent for gluteus medius — the muscle that gives the hip the rounded shape.",
         7.5, None, None, "Glutes", "Quadriceps, Hip Abductors"),

        ("Banded Walk", 3, 1, "nybörjare", "styrka",
         "Place resistance band above knees and walk sideways in squat position",
         "Activates gluteus medius before heavy lifts. Use as warm-up or finisher.",
         4.0, None, None, "Glutes", "Hip Abductors"),

        ("Glute Kickback Machine", 3, 1, "nybörjare", "styrka",
         "Use glute kickback machine to isolate and load the glutes",
         "One of the few machines that lets you directly load the glute at full extension.",
         4.5, None, None, "Glutes", "Hamstrings"),

        ("Frog Pump", 3, 1, "nybörjare", "styrka",
         "Lie on back with soles of feet together, pump hips up and down",
         "High activation of glutes with low lower back stress. Great for beginners.",
         3.5, None, None, "Glutes", None),

        ("Single Leg Hip Thrust", 3, 1, "medel", "styrka",
         "Hip thrust on one leg for unilateral glute development",
         "Eliminates dominant leg compensation. Research shows higher glute activation than bilateral.",
         7.0, None, None, "Glutes", "Hamstrings, Core"),

        ("Romanian Deadlift with Dumbbells", 3, 2, "nybörjare", "styrka",
         "Hip hinge with dumbbells for hamstring and glute stretch",
         "Dumbbells allow better positioning for women. Keep close to legs throughout.",
         8.5, None, None, "Hamstrings", "Glutes, Lower Back"),

        ("Leg Press — Feet High", 3, 1, "nybörjare", "styrka",
         "Leg press with feet placed high on platform to shift emphasis to glutes",
         "Foot placement drastically changes muscle emphasis. High feet = more glutes.",
         8.0, None, None, "Glutes", "Hamstrings"),
    ]

    count = 0
    for ex in women_exercises:
        existing = conn.execute(text(
            "SELECT id FROM exercises WHERE name = :name"
        ), {"name": ex[0]}).fetchone()
        if not existing:
            conn.execute(text("""
                INSERT INTO exercises
                    (name, body_part_id, equipment_id, difficulty, exercise_type,
                     description, tips, calories_per_minute,
                     video_url, image_url, primary_muscle, secondary_muscles)
                VALUES (:name, :bp, :eq, :diff, :type, :desc, :tips, :cal,
                        :video, :image, :primary_muscle, :secondary_muscles)
            """), {
                "name": ex[0], "bp": ex[1], "eq": ex[2], "diff": ex[3],
                "type": ex[4], "desc": ex[5], "tips": ex[6], "cal": ex[7],
                "video": ex[8], "image": ex[9],
                "primary_muscle": ex[10], "secondary_muscles": ex[11]
            })
            count += 1
    conn.commit()
    log.info(f"Added {count} women-specific exercises!")

def seed_glute_program(conn):
    """
    Glute & Lower Body 12-veckors program.
    Vetenskaplig grund:
    - Forskning visar att kvinnor svarar bättre på 12-20 reps vs männens 5-8
    - Glutes behöver tränas 2-3x/vecka för optimal tillväxt (Contreras et al.)
    - Progressive overload fungerar likadant för kvinnor som för män
    - Hip thrust, RDL och bulgarskan är de tre bästa gluteövningarna
    """
    log.info("Creating Glute & Lower Body Program...")

    plan_id = create_program(conn,
        name="Glute & Lower Body — 12 Week",
        goal="bygga_muskler",
        difficulty="nybörjare",
        duration_weeks=12,
        days_per_week=4,
        description="Science-based 12-week glute and lower body program for women. Research by Bret Contreras shows hip thrust, RDL and Bulgarian split squat produce the highest glute activation. Uses higher rep ranges (12-20) which research shows women respond better to. Progressive overload: add 2.5kg each week when all reps completed. Trains glutes 2-3x per week for optimal growth.",
        target_audience="Women who want to build stronger and more defined glutes and legs"
    )

    # Glute A — Hip thrust fokus
    glute_day_a = [
        ("Hip Thrust",              4, 12, 90,  "moderate"),
        ("Romanian Deadlift",       3, 12, 75,  "moderate"),
        ("Leg Press — Feet High",   3, 15, 60,  "light"),
        ("Cable Kickback",          3, 15, 45,  "light"),
        ("Hip Abduction Machine",   3, 20, 45,  "light"),
        ("Frog Pump",               2, 20, 30,  "light"),
    ]

    # Glute B — Squat fokus
    glute_day_b = [
        ("Sumo Squat",              4, 12, 90,  "moderate"),
        ("Bulgarian Split Squat",   3, 12, 75,  "moderate"),
        ("Curtsy Lunge",            3, 12, 60,  "light"),
        ("Single Leg Hip Thrust",   3, 10, 60,  "moderate"),
        ("Donkey Kicks",            3, 15, 30,  "light"),
        ("Banded Walk",             3, 20, 30,  "light"),
    ]

    # Upper body (kompletterande)
    upper_day = [
        ("Latsdrag",                3, 12, 75,  "moderate"),
        ("Seated Cable Row",        3, 12, 75,  "moderate"),
        ("Dumbbell Bench Press",    3, 12, 75,  "moderate"),
        ("Lateral Raise",           3, 15, 45,  "light"),
        ("Face Pull",               3, 15, 45,  "light"),
        ("Dumbbell Curl",           3, 15, 45,  "light"),
    ]

    days_structure = [
        (1, "Glute Day A", "Hip thrust focus | RPE 7-8 | Add 2.5kg when all reps done", glute_day_a),
        (2, "Upper Body", "Back, chest, shoulders — supporting muscles", upper_day),
        (3, "Rest", "Active recovery or yoga/stretching", []),
        (4, "Glute Day B", "Squat focus | RPE 7-8 | Higher reps for glute activation", glute_day_b),
        (5, "Glute Day A", "Hip thrust focus — 2nd session this week", glute_day_a),
        (6, "Rest", "Rest or light cardio Zone 2", []),
        (7, "Rest", "Full rest", []),
    ]

    total_days = 0
    for week in range(1, 13):
        is_deload = week % 4 == 0
        sets_mult = 1.0 if week <= 4 else 1.1 if week <= 8 else 1.2

        for day_num, day_name, focus, exercises in days_structure:
            is_rest = len(exercises) == 0
            day_id = add_day(conn, plan_id, week, day_num,
                f"Week {week} — {day_name}", focus, is_rest=is_rest)
            if not is_rest:
                for order, (ex_name, sets, reps, rest, intensity) in enumerate(exercises, 1):
                    ex_id = get_exercise_id(conn, ex_name)
                    actual_sets = max(2, round(sets * (0.5 if is_deload else sets_mult)))
                    actual_reps = reps
                    add_exercise(conn, day_id, ex_id, actual_sets,
                        actual_reps, rest, "light" if is_deload else intensity, order)
                total_days += 1

    conn.commit()
    log.info(f"Glute program created! {total_days} training days added.")
    return plan_id

def seed_toning_program(conn):
    """
    Full Body Toning 8-veckors program.
    Vetenskaplig grund:
    - "Toning" = bygga muskler + minska fett — samma principer som hypertrofi
    - Måttlig vikt med 12-15 reps och kort vila (60s) ökar metabolisk stress
    - Full body 3x/vecka ger optimal frekvens utan överträning
    - Kombinera styrka med circuit-element för maximal kaloriförbränning
    """
    log.info("Creating Full Body Toning Program...")

    plan_id = create_program(conn,
        name="Full Body Toning — Women 8 Week",
        goal="hålla_sig_i_form",
        difficulty="nybörjare",
        duration_weeks=8,
        days_per_week=3,
        description="Science-based 8-week toning program for women. Note: 'toning' = building muscle + reducing fat — the same principles as hypertrophy training but with moderate weights and higher reps. Research shows 12-15 reps at 65-70% 1RM with 60s rest maximizes metabolic stress and muscle definition. Full body 3x per week ensures optimal frequency. Add cardio on off days for fat loss.",
        target_audience="Women who want a leaner, more defined physique without bulking"
    )

    full_body_a = [
        ("Sumo Squat",          3, 15, 60, "moderate"),
        ("Dumbbell Bench Press",3, 12, 60, "moderate"),
        ("Romanian Deadlift",   3, 12, 60, "moderate"),
        ("Latsdrag",            3, 12, 60, "moderate"),
        ("Hip Abduction Machine",3, 20, 45, "light"),
        ("Plankan",             3, 40, 45, "light"),
    ]

    full_body_b = [
        ("Bulgarian Split Squat",3, 12, 60, "moderate"),
        ("Seated Cable Row",    3, 12, 60, "moderate"),
        ("Hip Thrust",          3, 15, 60, "moderate"),
        ("Lateral Raise",       3, 15, 45, "light"),
        ("Cable Kickback",      3, 15, 45, "light"),
        ("Bicycle Crunch",      3, 20, 45, "light"),
    ]

    days_structure = [
        (1, "Full Body A", "Legs, push, pull | RPE 7/10 | 60s rest", full_body_a),
        (2, "Rest", "Zone 2 cardio 30 min or rest", []),
        (3, "Full Body B", "Glutes, pull, shoulders | RPE 7/10 | 60s rest", full_body_b),
        (4, "Rest", "Zone 2 cardio 30 min or rest", []),
        (5, "Full Body A", "Repeat — try to add reps or small weight", full_body_a),
        (6, "Rest", "Active recovery or yoga", []),
        (7, "Rest", "Full rest", []),
    ]

    total_days = 0
    for week in range(1, 9):
        is_deload = week == 8
        for day_num, day_name, focus, exercises in days_structure:
            is_rest = len(exercises) == 0
            day_id = add_day(conn, plan_id, week, day_num,
                f"Week {week} — {day_name}", focus, is_rest=is_rest)
            if not is_rest:
                for order, (ex_name, sets, reps, rest, intensity) in enumerate(exercises, 1):
                    ex_id = get_exercise_id(conn, ex_name)
                    actual_sets = max(2, round(sets * 0.5)) if is_deload else sets
                    add_exercise(conn, day_id, ex_id, actual_sets,
                        reps, rest, "light" if is_deload else intensity, order)
                total_days += 1

    conn.commit()
    log.info(f"Toning program created! {total_days} training days added.")
    return plan_id

def seed_hourglass_program(conn):
    """
    Hourglass Figure 10-veckors program.
    Vetenskaplig grund:
    - Hourglass = bred axlar + bred höft + smal midja
    - Bygg lateral deltoid för bredare axlar (Lateral raises 3-4x/vecka)
    - Bygg gluteus medius för bredare höfter (Hip abduction, curtsy lunge)
    - Core stabilitet minskar midjeomfång över tid
    - 10 veckor är minimum för mätbara strukturella förändringar
    """
    log.info("Creating Hourglass Figure Program...")

    plan_id = create_program(conn,
        name="Hourglass Figure — Women 10 Week",
        goal="bygga_muskler",
        difficulty="medel",
        duration_weeks=10,
        days_per_week=5,
        description="Science-based 10-week program to build an hourglass physique. Strategy: build wider shoulders (lateral deltoid focus), build wider hips (gluteus medius focus with hip abduction and curtsy lunges), and strengthen core for waist definition. Research shows lateral raises 3-4x per week and hip abduction work are the most effective for this goal. RPE 7-8/10 throughout.",
        target_audience="Women who want to build an hourglass figure with wider shoulders and hips"
    )

    # Dag 1: Axlar + Glutes
    shoulders_glutes = [
        ("Seated Dumbbell Press",   4, 12, 75,  "moderate"),
        ("Lateral Raise",           4, 15, 45,  "light"),
        ("Cable Lateral Raise",     3, 15, 45,  "light"),
        ("Hip Thrust",              4, 12, 90,  "moderate"),
        ("Hip Abduction Machine",   3, 20, 45,  "light"),
        ("Curtsy Lunge",            3, 12, 60,  "light"),
    ]

    # Dag 2: Rygg + Höfter
    back_hips = [
        ("Latsdrag",                4, 12, 75,  "moderate"),
        ("Seated Cable Row",        3, 12, 75,  "moderate"),
        ("Face Pull",               3, 15, 45,  "light"),
        ("Banded Walk",             3, 20, 30,  "light"),
        ("Fire Hydrants",           3, 15, 30,  "light"),
        ("Single Leg Hip Thrust",   3, 10, 60,  "moderate"),
    ]

    # Dag 3: Ben + Core
    legs_core = [
        ("Sumo Squat",              4, 12, 90,  "moderate"),
        ("Romanian Deadlift",       3, 12, 75,  "moderate"),
        ("Bulgarian Split Squat",   3, 12, 75,  "moderate"),
        ("Leg Press — Feet High",   3, 15, 60,  "light"),
        ("Plankan",                 3, 45, 45,  "light"),
        ("Russian Twist",           3, 20, 45,  "light"),
    ]

    # Dag 4: Axlar + Arms (volym)
    shoulders_arms = [
        ("Arnold Press",            3, 12, 75,  "moderate"),
        ("Lateral Raise",           4, 15, 45,  "light"),
        ("Reverse Fly",             3, 15, 45,  "light"),
        ("Dumbbell Curl",           3, 15, 45,  "light"),
        ("Tricep Pushdown",         3, 15, 45,  "light"),
        ("Cable Kickback",          3, 15, 45,  "light"),
    ]

    # Dag 5: Glutes + Core (finisher)
    glutes_core = [
        ("Hip Thrust",              3, 15, 75,  "moderate"),
        ("Donkey Kicks",            3, 20, 30,  "light"),
        ("Glute Kickback Machine",  3, 15, 45,  "light"),
        ("Hip Abduction Machine",   3, 20, 45,  "light"),
        ("Dead Bug",                3, 10, 30,  "light"),
        ("Side Plank",              3, 30, 30,  "light"),
    ]

    days_structure = [
        (1, "Shoulders + Glutes", "Lateral deltoid & glute med for hourglass shape | RPE 7-8", shoulders_glutes),
        (2, "Back + Hips", "Lat width + hip abductors for waist-to-hip ratio | RPE 7", back_hips),
        (3, "Rest", "Zone 2 cardio 30 min or active recovery", []),
        (4, "Legs + Core", "Compound leg work + waist definition | RPE 7-8", legs_core),
        (5, "Shoulders + Arms", "Volume day for shoulder width | RPE 7", shoulders_arms),
        (6, "Glutes + Core", "Glute finisher + core stability | RPE 6-7", glutes_core),
        (7, "Rest", "Full rest", []),
    ]

    total_days = 0
    for week in range(1, 11):
        is_deload = week == 10
        sets_mult = 1.0 if week <= 4 else 1.1 if week <= 7 else 1.2

        for day_num, day_name, focus, exercises in days_structure:
            is_rest = len(exercises) == 0
            day_id = add_day(conn, plan_id, week, day_num,
                f"Week {week} — {day_name}", focus, is_rest=is_rest)
            if not is_rest:
                for order, (ex_name, sets, reps, rest, intensity) in enumerate(exercises, 1):
                    ex_id = get_exercise_id(conn, ex_name)
                    actual_sets = max(2, round(sets * (0.5 if is_deload else sets_mult)))
                    add_exercise(conn, day_id, ex_id, actual_sets,
                        reps, rest, "light" if is_deload else intensity, order)
                total_days += 1

    conn.commit()
    log.info(f"Hourglass program created! {total_days} training days added.")
    return plan_id

if __name__ == "__main__":
    log.info("Starting women's program seeder...")
    with engine.connect() as conn:
        seed_women_exercises(conn)
        seed_glute_program(conn)
        seed_toning_program(conn)
        seed_hourglass_program(conn)
    log.info("All women's programs created!")
    log.info("Programs added:")
    log.info("1. Glute & Lower Body 12 Week — science-based glute growth")
    log.info("2. Full Body Toning 8 Week — lean and defined")
    log.info("3. Hourglass Figure 10 Week — wider shoulders and hips")