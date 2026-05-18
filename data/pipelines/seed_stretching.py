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

def add_exercise(conn, name, body_part_id, equipment_id, difficulty,
                 exercise_type, description, tips, calories_per_minute,
                 primary_muscle=None, secondary_muscles=None):
    existing = conn.execute(text(
        "SELECT id FROM exercises WHERE name = :name"
    ), {"name": name}).fetchone()
    if existing:
        return existing[0]
    result = conn.execute(text("""
        INSERT INTO exercises (
            name, body_part_id, equipment_id, difficulty, exercise_type,
            description, tips, calories_per_minute, primary_muscle, secondary_muscles
        ) VALUES (
            :name, :bp, :eq, :diff, :type,
            :desc, :tips, :cal, :primary_muscle, :secondary_muscles
        ) RETURNING id
    """), {
        "name": name, "bp": body_part_id, "eq": equipment_id,
        "diff": difficulty, "type": exercise_type,
        "desc": description, "tips": tips, "cal": calories_per_minute,
        "primary_muscle": primary_muscle, "secondary_muscles": secondary_muscles
    }).fetchone()
    return result[0]

def seed_stretching_exercises(conn):
    log.info("Adding stretching exercises for men and women...")

    stretches = [
        # ================================
        # ÖVRE KROPP — Både män och kvinnor
        # ================================
        ("Chest Doorway Stretch", 1, 1, "nybörjare", "stretching",
         "Stand in doorway with arms at 90 degrees, lean forward gently to stretch chest",
         "Hold 30-60 seconds. Research shows doorway stretches effectively reduce chest tightness from pushing exercises.",
         2.0, "Mid Chest", "Front Deltoid, Biceps"),

        ("Cross-Body Shoulder Stretch", 4, 1, "nybörjare", "stretching",
         "Pull one arm across chest with other arm, hold to stretch rear deltoid",
         "Hold 30 seconds each side. Essential after any pushing or pressing workout.",
         1.5, "Rear Deltoid", "Upper Back"),

        ("Overhead Tricep Stretch", 5, 1, "nybörjare", "stretching",
         "Raise one arm overhead, bend elbow and use other hand to gently push elbow back",
         "Hold 30 seconds. Stretches the long head of the tricep which is often tight.",
         1.5, "Triceps", None),

        ("Bicep Wall Stretch", 5, 1, "nybörjare", "stretching",
         "Place hand on wall behind you with thumb pointing down, gently rotate away",
         "Hold 30 seconds. Great after heavy curling sessions.",
         1.5, "Biceps", "Front Deltoid"),

        ("Neck Side Stretch", 6, 1, "nybörjare", "stretching",
         "Tilt head to one side, use hand for gentle added pressure to stretch neck",
         "Hold 20-30 seconds each side. Never force or use excessive pressure.",
         1.0, "Core", "Trapezius"),

        ("Thoracic Spine Rotation", 2, 1, "nybörjare", "stretching",
         "Sit on floor with legs crossed, place hand behind head and rotate upper body",
         "Hold 2-3 seconds at end range, 10 reps each side. Improves posture significantly.",
         2.0, "Upper Back", "Obliques"),

        ("Lat Stretch with Band", 2, 1, "nybörjare", "stretching",
         "Hold overhead bar or doorframe with one hand, lean away to stretch lat",
         "Hold 30-60 seconds each side. Critical for lifters who do heavy pulling.",
         2.0, "Lats", "Lower Back"),

        ("Wrist Flexor Stretch", 5, 1, "nybörjare", "stretching",
         "Extend arm in front, use other hand to pull fingers back gently",
         "Hold 30 seconds. Important for anyone doing heavy deadlifts or curls.",
         1.0, "Forearms", None),

        ("Wrist Extensor Stretch", 5, 1, "nybörjare", "stretching",
         "Extend arm, use other hand to push fingers down and toward body",
         "Hold 30 seconds each side. Prevents wrist pain from heavy lifting.",
         1.0, "Forearms", None),

        # ================================
        # RYGG — Både män och kvinnor
        # ================================
        ("Child's Pose Extended", 2, 1, "nybörjare", "stretching",
         "Kneel and extend arms forward on floor, sit hips back to heels",
         "Hold 60-90 seconds. One of the best lower back stretches. Breathe deeply.",
         1.5, "Lower Back", "Lats, Core"),

        ("Cat-Cow Stretch", 2, 1, "nybörjare", "stretching",
         "On hands and knees, alternate between arching and rounding spine",
         "10 slow reps. Lubricates spinal joints and improves mobility.",
         2.0, "Lower Back", "Core"),

        ("Knees to Chest", 2, 1, "nybörjare", "stretching",
         "Lie on back, pull both knees to chest and hold gently",
         "Hold 30-60 seconds. Relieves lower back compression after squats and deadlifts.",
         1.5, "Lower Back", None),

        ("Supine Spinal Twist", 2, 1, "nybörjare", "stretching",
         "Lie on back, drop bent knees to one side while keeping shoulders flat",
         "Hold 45 seconds each side. Excellent for spinal rotation and lower back relief.",
         1.5, "Lower Back", "Obliques"),

        ("Cobra Stretch", 2, 1, "nybörjare", "stretching",
         "Lie face down, press up through hands to extend spine",
         "Hold 20-30 seconds. Counteracts forward flexion from sitting and deadlifting.",
         2.0, "Lower Back", "Core"),

        # ================================
        # BEN — Både män och kvinnor
        # ================================
        ("Standing Quad Stretch", 3, 1, "nybörjare", "stretching",
         "Stand on one leg, pull other foot toward glute to stretch quadricep",
         "Hold 30-45 seconds each side. Essential after squats and leg press.",
         2.0, "Quadriceps", None),

        ("Lying Quad Stretch", 3, 1, "nybörjare", "stretching",
         "Lie on side, pull top foot toward glute for deeper quad stretch",
         "Hold 45-60 seconds. Better stretch than standing version for most people.",
         1.5, "Quadriceps", "Hip Flexors"),

        ("Standing Hamstring Stretch", 3, 1, "nybörjare", "stretching",
         "Place one foot on elevated surface, hinge forward at hips with straight back",
         "Hold 30-45 seconds. Keep spine neutral, don't round back.",
         2.0, "Hamstrings", "Lower Back"),

        ("Seated Hamstring Stretch", 3, 1, "nybörjare", "stretching",
         "Sit on floor with legs extended, reach forward toward feet",
         "Hold 45-60 seconds. Research shows this is most effective hamstring stretch.",
         1.5, "Hamstrings", "Lower Back"),

        ("Lying Hamstring Stretch", 3, 1, "nybörjare", "stretching",
         "Lie on back, lift one leg up and hold behind thigh or calf",
         "Hold 30-45 seconds each leg. Great for post-deadlift recovery.",
         1.5, "Hamstrings", None),

        ("Hip Flexor Lunge Stretch", 3, 1, "nybörjare", "stretching",
         "Kneel in lunge position, push hips forward to stretch hip flexors",
         "Hold 45-60 seconds each side. Critical for anyone who sits a lot.",
         2.5, "Hip Flexors", "Quadriceps"),

        ("Pigeon Pose Hip Stretch", 3, 1, "medel", "stretching",
         "From plank, bring one knee forward and place outside of shin on floor",
         "Hold 60-90 seconds each side. Best stretch for glutes and hip external rotators.",
         2.0, "Glutes", "Hip Flexors"),

        ("Figure Four Stretch", 3, 1, "nybörjare", "stretching",
         "Lie on back, cross ankle over opposite knee and pull legs toward chest",
         "Hold 45-60 seconds each side. Targets piriformis — often tight in lifters.",
         1.5, "Glutes", None),

        ("Butterfly Stretch", 3, 1, "nybörjare", "stretching",
         "Sit with soles of feet together, let knees fall out to sides",
         "Hold 45-60 seconds. Stretches inner thighs and hip adductors.",
         1.5, "Glutes", "Inner Thighs"),

        ("Calf Stretch Wall", 3, 1, "nybörjare", "stretching",
         "Place hands on wall, step one foot back and push heel to floor",
         "Hold 30-45 seconds each side. Essential after running and calf raises.",
         2.0, "Calves", None),

        ("Soleus Stretch", 3, 1, "nybörjare", "stretching",
         "Same as calf stretch but bend back knee slightly to target deeper soleus",
         "Hold 30-45 seconds. Targets the deeper calf muscle — often neglected.",
         1.5, "Calves", None),

        # ================================
        # SPECIFIKT FÖR KVINNOR
        # ================================
        ("Hip Circle Stretch", 3, 1, "nybörjare", "stretching",
         "Stand with feet wide, make large circles with hips to loosen hip joint",
         "10 circles each direction. Excellent warm-up for glute and hip workouts.",
         2.5, "Glutes", "Hip Flexors, Inner Thighs"),

        ("Deep Squat Hold", 3, 1, "nybörjare", "stretching",
         "Hold a deep squat position with elbows pressing knees outward",
         "Hold 30-60 seconds. Opens hips dramatically. Use support if needed.",
         3.0, "Glutes", "Inner Thighs, Hip Flexors"),

        ("Glute Kickback Stretch", 3, 1, "nybörjare", "stretching",
         "On hands and knees, extend one leg back and hold at top",
         "Hold 20-30 seconds each side. Activates and stretches glutes simultaneously.",
         2.5, "Glutes", "Hamstrings"),

        ("Inner Thigh Stretch Side Lunge", 3, 1, "nybörjare", "stretching",
         "Step wide to one side into side lunge, keep other leg straight",
         "Hold 30-45 seconds each side. Targets adductors — important for hip health.",
         3.0, "Inner Thighs", "Glutes"),

        ("Lying Glute Stretch", 3, 1, "nybörjare", "stretching",
         "Lie on back, cross one ankle over opposite knee and hug legs toward chest",
         "Hold 45-60 seconds. Excellent after hip thrust and glute sessions.",
         1.5, "Glutes", None),

        # ================================
        # SPECIFIKT FÖR MÄN
        # ================================
        ("Pec Minor Stretch", 1, 1, "nybörjare", "stretching",
         "Lie on foam roller along spine, let arms fall out to sides at 90 degrees",
         "Hold 60-90 seconds. Reverses rounded shoulder posture from heavy benching.",
         1.5, "Upper Chest", "Front Deltoid"),

        ("Jefferson Curl", 2, 1, "medel", "stretching",
         "Stand on platform, hold light weight, slowly curl spine down vertebra by vertebra",
         "Go slow and controlled. One of the best posterior chain stretches for advanced lifters.",
         3.0, "Lower Back", "Hamstrings"),

        ("Couch Stretch", 3, 1, "medel", "stretching",
         "Kneel with back shin against wall or couch, bring torso upright",
         "Hold 60-90 seconds each side. Best hip flexor stretch for lifters. Very intense.",
         2.5, "Hip Flexors", "Quadriceps"),

        ("Pancake Stretch", 3, 1, "medel", "stretching",
         "Sit with legs spread wide, fold forward between legs",
         "Hold 60+ seconds. Improves hip mobility for squats and deadlifts.",
         2.0, "Inner Thighs", "Hamstrings, Lower Back"),

        ("Shoulder Dislocate with Band", 4, 1, "medel", "stretching",
         "Hold band with wide grip, slowly pass over head and behind body",
         "10 slow reps. Dramatically improves shoulder mobility for overhead work.",
         3.0, "Front Deltoid", "Rear Deltoid, Chest"),
    ]

    count = 0
    for ex in stretches:
        result = add_exercise(conn, *ex)
        if result:
            count += 1

    conn.commit()
    log.info(f"Added {count} stretching exercises!")

def seed_stretching_program_men(conn):
    """Stretchingprogram för män — fokus på styrketräning."""
    log.info("Creating Men's Stretching & Mobility Program...")

    existing = conn.execute(text(
        "SELECT id FROM training_plans WHERE name = :name"
    ), {"name": "Men's Mobility & Stretching — 8 Week"}).fetchone()

    if existing:
        log.info("Program already exists, skipping.")
        return existing[0]

    result = conn.execute(text("""
        INSERT INTO training_plans
            (name, goal, difficulty, duration_weeks, days_per_week, description, target_audience)
        VALUES (
            'Men''s Mobility & Stretching — 8 Week',
            'hålla_sig_i_form',
            'nybörjare',
            8, 4,
            'Science-based 8-week mobility and stretching program designed for men who lift weights. Focuses on areas most restricted in male lifters: hip flexors, thoracic spine, hamstrings and shoulder mobility. Research shows 4x per week flexibility training produces significant improvements in 8 weeks. Hold each stretch 45-60 seconds for optimal collagen remodeling.',
            'Men who lift weights and want to improve flexibility, prevent injury and move better'
        ) RETURNING id
    """)).fetchone()
    plan_id = result[0]
    conn.commit()

    def get_ex(name):
        r = conn.execute(text("SELECT id FROM exercises WHERE name = :n"), {"n": name}).fetchone()
        return r[0] if r else None

    def add_day(week, day_num, day_name, focus):
        r = conn.execute(text("""
            INSERT INTO training_plan_days (plan_id, week_number, day_number, day_name, focus, rest_day)
            VALUES (:pid, :w, :d, :n, :f, false) RETURNING id
        """), {"pid": plan_id, "w": week, "d": day_num, "n": f"Week {week} — {day_name}", "f": focus}).fetchone()
        return r[0]

    def add_ex(day_id, ex_name, sets, reps, rest):
        ex_id = get_ex(ex_name)
        if ex_id:
            conn.execute(text("""
                INSERT INTO training_plan_exercises
                    (plan_day_id, exercise_id, sets, reps, rest_seconds, intensity, order_index)
                VALUES (:d, :e, :s, :r, :rest, 'light', 1)
            """), {"d": day_id, "e": ex_id, "s": sets, "r": reps, "rest": rest})

    # Dag 1: Övre kropp stretching
    upper_stretches = [
        ("Chest Doorway Stretch", 3, 60, 15),
        ("Cross-Body Shoulder Stretch", 3, 45, 15),
        ("Lat Stretch with Band", 3, 60, 15),
        ("Thoracic Spine Rotation", 3, 10, 15),
        ("Wrist Flexor Stretch", 2, 30, 10),
        ("Pec Minor Stretch", 2, 90, 15),
        ("Shoulder Dislocate with Band", 3, 10, 15),
    ]

    # Dag 2: Nedre kropp stretching
    lower_stretches = [
        ("Hip Flexor Lunge Stretch", 3, 60, 15),
        ("Couch Stretch", 3, 90, 15),
        ("Standing Hamstring Stretch", 3, 45, 15),
        ("Pigeon Pose Hip Stretch", 3, 90, 15),
        ("Pancake Stretch", 3, 60, 15),
        ("Calf Stretch Wall", 3, 45, 10),
        ("Jefferson Curl", 3, 10, 20),
    ]

    # Dag 3: Rygg & core stretching
    back_stretches = [
        ("Child's Pose Extended", 3, 90, 15),
        ("Cat-Cow Stretch", 3, 10, 10),
        ("Knees to Chest", 3, 60, 15),
        ("Supine Spinal Twist", 3, 45, 15),
        ("Cobra Stretch", 3, 30, 15),
        ("Figure Four Stretch", 3, 60, 15),
    ]

    # Dag 4: Full body mobility
    full_mobility = [
        ("Deep Squat Hold", 3, 60, 15),
        ("Hip Flexor Lunge Stretch", 2, 45, 10),
        ("Thoracic Spine Rotation", 3, 10, 15),
        ("Standing Hamstring Stretch", 2, 45, 10),
        ("Chest Doorway Stretch", 2, 45, 10),
        ("Pigeon Pose Hip Stretch", 2, 60, 15),
        ("Cat-Cow Stretch", 2, 10, 10),
    ]

    sessions = [
        (1, "Upper Body Stretch", "Chest, shoulders, lats, thoracic spine", upper_stretches),
        (2, "Lower Body Stretch", "Hip flexors, hamstrings, glutes, calves", lower_stretches),
        (4, "Back & Core Mobility", "Lower back, spine rotation, hip mobility", back_stretches),
        (6, "Full Body Mobility", "Complete mobility session", full_mobility),
    ]

    for week in range(1, 9):
        for day_num, day_name, focus, exercises in sessions:
            day_id = add_day(week, day_num, day_name, focus)
            for ex_name, sets, reps, rest in exercises:
                add_ex(day_id, ex_name, sets, reps, rest)

        for rest_day in [3, 5, 7]:
            conn.execute(text("""
                INSERT INTO training_plan_days (plan_id, week_number, day_number, day_name, focus, rest_day)
                VALUES (:pid, :w, :d, :n, 'Rest', true)
            """), {"pid": plan_id, "w": week, "d": rest_day, "n": f"Week {week} — Rest"})

    conn.commit()
    log.info("Men's stretching program created!")
    return plan_id

def seed_stretching_program_women(conn):
    """Stretchingprogram för kvinnor — fokus på höfter, glutes och flexibilitet."""
    log.info("Creating Women's Stretching & Flexibility Program...")

    existing = conn.execute(text(
        "SELECT id FROM training_plans WHERE name = :name"
    ), {"name": "Women's Flexibility & Stretching — 8 Week"}).fetchone()

    if existing:
        log.info("Program already exists, skipping.")
        return existing[0]

    result = conn.execute(text("""
        INSERT INTO training_plans
            (name, goal, difficulty, duration_weeks, days_per_week, description, target_audience)
        VALUES (
            'Women''s Flexibility & Stretching — 8 Week',
            'hålla_sig_i_form',
            'nybörjare',
            8, 5,
            'Science-based 8-week flexibility program for women. Focuses on hip mobility, glute activation and flexibility — areas where women typically have more potential for improvement. Research shows women have greater flexibility gains than men from consistent stretching. Combines static stretching (45-90s holds) with dynamic mobility work for optimal results.',
            'Women who want to improve flexibility, reduce muscle soreness and move more freely'
        ) RETURNING id
    """)).fetchone()
    plan_id = result[0]
    conn.commit()

    def get_ex(name):
        r = conn.execute(text("SELECT id FROM exercises WHERE name = :n"), {"n": name}).fetchone()
        return r[0] if r else None

    def add_day(week, day_num, day_name, focus):
        r = conn.execute(text("""
            INSERT INTO training_plan_days (plan_id, week_number, day_number, day_name, focus, rest_day)
            VALUES (:pid, :w, :d, :n, :f, false) RETURNING id
        """), {"pid": plan_id, "w": week, "d": day_num, "n": f"Week {week} — {day_name}", "f": focus}).fetchone()
        return r[0]

    def add_ex(day_id, ex_name, sets, reps, rest):
        ex_id = get_ex(ex_name)
        if ex_id:
            conn.execute(text("""
                INSERT INTO training_plan_exercises
                    (plan_day_id, exercise_id, sets, reps, rest_seconds, intensity, order_index)
                VALUES (:d, :e, :s, :r, :rest, 'light', 1)
            """), {"d": day_id, "e": ex_id, "s": sets, "r": reps, "rest": rest})

    # Dag 1: Höft & glutes
    hip_glute = [
        ("Pigeon Pose Hip Stretch", 3, 90, 15),
        ("Figure Four Stretch", 3, 60, 15),
        ("Butterfly Stretch", 3, 60, 15),
        ("Hip Circle Stretch", 3, 10, 10),
        ("Inner Thigh Stretch Side Lunge", 3, 45, 15),
        ("Deep Squat Hold", 3, 60, 15),
        ("Lying Glute Stretch", 3, 60, 15),
    ]

    # Dag 2: Övre kropp
    upper = [
        ("Chest Doorway Stretch", 3, 45, 15),
        ("Cross-Body Shoulder Stretch", 3, 45, 15),
        ("Lat Stretch with Band", 3, 60, 15),
        ("Thoracic Spine Rotation", 3, 10, 15),
        ("Neck Side Stretch", 3, 20, 10),
        ("Overhead Tricep Stretch", 2, 30, 10),
    ]

    # Dag 3: Hamstrings & rygg
    hamstring_back = [
        ("Seated Hamstring Stretch", 3, 60, 15),
        ("Lying Hamstring Stretch", 3, 45, 15),
        ("Child's Pose Extended", 3, 90, 15),
        ("Supine Spinal Twist", 3, 45, 15),
        ("Knees to Chest", 3, 60, 15),
        ("Cat-Cow Stretch", 3, 10, 10),
    ]

    # Dag 4: Glute activation stretch
    glute_activation = [
        ("Glute Kickback Stretch", 3, 30, 10),
        ("Hip Flexor Lunge Stretch", 3, 60, 15),
        ("Lying Quad Stretch", 3, 60, 15),
        ("Figure Four Stretch", 3, 60, 15),
        ("Deep Squat Hold", 3, 60, 15),
        ("Hip Circle Stretch", 3, 10, 10),
    ]

    # Dag 5: Full body flexibility
    full_flex = [
        ("Butterfly Stretch", 2, 60, 15),
        ("Pigeon Pose Hip Stretch", 2, 60, 15),
        ("Seated Hamstring Stretch", 2, 45, 15),
        ("Chest Doorway Stretch", 2, 45, 10),
        ("Child's Pose Extended", 2, 60, 15),
        ("Cobra Stretch", 2, 30, 15),
        ("Cat-Cow Stretch", 2, 10, 10),
    ]

    sessions = [
        (1, "Hip & Glute Flexibility", "Hip mobility, glute stretching, inner thighs", hip_glute),
        (2, "Upper Body Flexibility", "Chest, shoulders, lats, neck", upper),
        (3, "Hamstrings & Back", "Posterior chain and spinal mobility", hamstring_back),
        (5, "Glute Activation Stretch", "Glute mobility and activation", glute_activation),
        (6, "Full Body Flexibility", "Complete flexibility session", full_flex),
    ]

    for week in range(1, 9):
        for day_num, day_name, focus, exercises in sessions:
            day_id = add_day(week, day_num, day_name, focus)
            for ex_name, sets, reps, rest in exercises:
                add_ex(day_id, ex_name, sets, reps, rest)

        for rest_day in [4, 7]:
            conn.execute(text("""
                INSERT INTO training_plan_days (plan_id, week_number, day_number, day_name, focus, rest_day)
                VALUES (:pid, :w, :d, :n, 'Rest', true)
            """), {"pid": plan_id, "w": week, "d": rest_day, "n": f"Week {week} — Rest"})

    conn.commit()
    log.info("Women's stretching program created!")
    return plan_id

if __name__ == "__main__":
    log.info("Starting stretching seeder...")
    with engine.connect() as conn:
        seed_stretching_exercises(conn)
        seed_stretching_program_men(conn)
        seed_stretching_program_women(conn)
    log.info("Done! Stretching programs created for both men and women.")
    log.info("Added:")
    log.info("- 35 stretching exercises")
    log.info("- Men's Mobility & Stretching 8 Week")
    log.info("- Women's Flexibility & Stretching 8 Week")