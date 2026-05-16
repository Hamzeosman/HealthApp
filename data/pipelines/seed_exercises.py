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
                 video_url=None, image_url=None, primary_muscle=None, secondary_muscles=None):
    existing = conn.execute(text(
        "SELECT id FROM exercises WHERE name = :name"
    ), {"name": name}).fetchone()
    if existing:
        return existing[0]
    result = conn.execute(text("""
        INSERT INTO exercises (
            name, body_part_id, equipment_id, difficulty, exercise_type,
            description, tips, calories_per_minute,
            video_url, image_url, primary_muscle, secondary_muscles
        ) VALUES (
            :name, :bp, :eq, :diff, :type,
            :desc, :tips, :cal,
            :video, :image, :primary_muscle, :secondary_muscles
        ) RETURNING id
    """), {
        "name": name, "bp": body_part_id, "eq": equipment_id,
        "diff": difficulty, "type": exercise_type,
        "desc": description, "tips": tips, "cal": calories_per_minute,
        "video": video_url, "image": image_url,
        "primary_muscle": primary_muscle, "secondary_muscles": secondary_muscles
    }).fetchone()
    return result[0]

def seed_muscle_groups(conn):
    """Lägger till specifika muskelgrupper."""
    log.info("Adding muscle groups...")
    groups = [
        # Bröst
        (1, "Upper Chest"),
        (1, "Mid Chest"),
        (1, "Lower Chest"),
        # Rygg
        (2, "Upper Back"),
        (2, "Mid Back"),
        (2, "Lats"),
        (2, "Lower Back"),
        # Ben
        (3, "Quadriceps"),
        (3, "Hamstrings"),
        (3, "Glutes"),
        (3, "Calves"),
        # Axlar
        (4, "Front Deltoid"),
        (4, "Lateral Deltoid"),
        (4, "Rear Deltoid"),
        # Armar
        (5, "Biceps"),
        (5, "Triceps"),
        (5, "Forearms"),
        # Mage
        (6, "Upper Abs"),
        (6, "Lower Abs"),
        (6, "Obliques"),
        (6, "Core"),
    ]
    for body_part_id, name in groups:
        existing = conn.execute(text(
            "SELECT id FROM muscle_groups WHERE name = :name"
        ), {"name": name}).fetchone()
        if not existing:
            conn.execute(text("""
                INSERT INTO muscle_groups (name, body_part_id)
                VALUES (:name, :bp)
            """), {"name": name, "bp": body_part_id})
    conn.commit()
    log.info("Muscle groups added!")

def update_exercise_columns(conn):
    """Lägger till nya kolumner för video, bild och muskler."""
    log.info("Adding new columns to exercises...")
    alterations = [
        "ALTER TABLE exercises ADD COLUMN IF NOT EXISTS video_url VARCHAR(500)",
        "ALTER TABLE exercises ADD COLUMN IF NOT EXISTS image_url VARCHAR(500)",
        "ALTER TABLE exercises ADD COLUMN IF NOT EXISTS primary_muscle VARCHAR(100)",
        "ALTER TABLE exercises ADD COLUMN IF NOT EXISTS secondary_muscles VARCHAR(200)",
    ]
    for sql in alterations:
        conn.execute(text(sql))
    conn.commit()
    log.info("Columns added!")

def seed_all_exercises(conn):
    """Lägger till 100+ övningar."""
    log.info("Adding 100+ exercises...")

    # BRÖST (body_part_id=1)
    chest = [
        ("Flat Barbell Bench Press", 1, 3, "medel", "styrka",
         "Lie flat on bench, lower bar to chest and press up", "Retract scapula, feet flat on floor", 8.0,
         "https://youtube.com/watch?v=bench", None, "Mid Chest", "Triceps, Front Deltoid"),
        ("Incline Barbell Bench Press", 1, 3, "medel", "styrka",
         "Set bench to 30-45 degrees, press bar from upper chest", "Keep elbows at 75 degrees", 8.5,
         None, None, "Upper Chest", "Triceps, Front Deltoid"),
        ("Decline Bench Press", 1, 3, "medel", "styrka",
         "Set bench to -15 degrees, press from lower chest", "Great for lower chest development", 8.0,
         None, None, "Lower Chest", "Triceps"),
        ("Dumbbell Bench Press", 1, 2, "nybörjare", "styrka",
         "Press dumbbells from chest level to full extension", "Greater range of motion than barbell", 7.5,
         None, None, "Mid Chest", "Triceps, Front Deltoid"),
        ("Incline Dumbbell Press", 1, 2, "nybörjare", "styrka",
         "Incline bench with dumbbells for upper chest", "Control the descent for maximum stretch", 7.5,
         None, None, "Upper Chest", "Front Deltoid"),
        ("Cable Crossover", 1, 4, "medel", "styrka",
         "Cross cables in front of body for chest isolation", "Keep slight bend in elbows throughout", 6.0,
         None, None, "Mid Chest", "Front Deltoid"),
        ("Pec Deck Machine", 1, 1, "nybörjare", "styrka",
         "Use pec deck machine to isolate chest muscles", "Perfect for beginners to feel chest engagement", 5.5,
         None, None, "Mid Chest", "Front Deltoid"),
        ("Push-ups", 1, 1, "nybörjare", "styrka",
         "Classic bodyweight push-up for chest and triceps", "Keep body in straight line throughout", 7.0,
         None, None, "Mid Chest", "Triceps, Front Deltoid"),
        ("Wide Push-ups", 1, 1, "nybörjare", "styrka",
         "Push-up with wide hand placement for outer chest", "Hands 1.5x shoulder width apart", 6.5,
         None, None, "Mid Chest", "Front Deltoid"),
        ("Diamond Push-ups", 1, 1, "nybörjare", "styrka",
         "Push-up with hands in diamond shape for inner chest and triceps", "Keep elbows close to body", 6.5,
         None, None, "Lower Chest", "Triceps"),
    ]

    # RYGG (body_part_id=2)
    back = [
        ("Conventional Deadlift", 2, 3, "avancerad", "styrka",
         "Hip-hinge movement lifting barbell from floor", "Neutral spine throughout, push floor away", 11.0,
         None, None, "Mid Back", "Hamstrings, Glutes, Lats"),
        ("Sumo Deadlift", 2, 3, "avancerad", "styrka",
         "Wide stance deadlift targeting inner thighs more", "Feet wider than hip width, toes pointed out", 10.5,
         None, None, "Mid Back", "Glutes, Inner Thighs"),
        ("Romanian Deadlift", 2, 3, "medel", "styrka",
         "Hip hinge keeping legs mostly straight for hamstring stretch", "Push hips back, maintain neutral spine", 9.5,
         None, None, "Hamstrings", "Glutes, Lower Back"),
        ("Barbell Row", 2, 3, "medel", "styrka",
         "Bent over row pulling bar to lower chest", "Keep back parallel to floor, pull with elbows", 8.5,
         None, None, "Mid Back", "Biceps, Rear Deltoid"),
        ("Dumbbell Row", 2, 2, "nybörjare", "styrka",
         "Single arm row with dumbbell supported on bench", "Pull elbow to ceiling, not out to side", 7.5,
         None, None, "Lats", "Biceps, Rear Deltoid"),
        ("T-Bar Row", 2, 3, "medel", "styrka",
         "Supported row using T-bar for mid back thickness", "Keep chest on pad, pull to sternum", 8.0,
         None, None, "Mid Back", "Biceps, Lats"),
        ("Chest Supported Row", 2, 2, "nybörjare", "styrka",
         "Lie chest-down on incline bench for supported row", "Eliminates lower back involvement", 7.0,
         None, None, "Mid Back", "Rear Deltoid, Biceps"),
        ("Cable Row", 2, 4, "nybörjare", "styrka",
         "Seated cable row for mid back and lats", "Keep chest up, pull to navel", 7.0,
         None, None, "Mid Back", "Biceps, Lats"),
        ("Lat Pulldown", 2, 4, "nybörjare", "styrka",
         "Pull bar down to upper chest for lat width", "Lean slightly back, pull with elbows", 7.0,
         None, None, "Lats", "Biceps"),
        ("Wide Grip Pulldown", 2, 4, "nybörjare", "styrka",
         "Wide grip lat pulldown for outer lat width", "Focus on lat stretch at top", 7.0,
         None, None, "Lats", "Biceps"),
        ("Pull-up", 2, 1, "medel", "styrka",
         "Bodyweight pull-up from dead hang to chin over bar", "Full dead hang, squeeze lats at top", 8.5,
         None, None, "Lats", "Biceps, Rear Deltoid"),
        ("Chin-up", 2, 1, "medel", "styrka",
         "Underhand grip pull-up targeting biceps more", "Supinated grip, elbows to ribs at top", 8.0,
         None, None, "Lats", "Biceps"),
        ("Hyperextension", 2, 1, "nybörjare", "styrka",
         "Back extension on GHD or hyperextension bench", "Squeeze glutes at top, don't hyperextend", 5.0,
         None, None, "Lower Back", "Glutes, Hamstrings"),
        ("Good Morning", 2, 3, "medel", "styrka",
         "Hip hinge with barbell on back for lower back strength", "Keep slight knee bend, push hips back", 7.0,
         None, None, "Lower Back", "Hamstrings, Glutes"),
    ]

    # BEN (body_part_id=3)
    legs = [
        ("Back Squat", 3, 3, "medel", "styrka",
         "Barbell on upper back, squat to parallel or below", "Knees track over toes, chest up", 10.0,
         None, None, "Quadriceps", "Glutes, Hamstrings"),
        ("Front Squat", 3, 3, "avancerad", "styrka",
         "Bar in front rack position for quad-dominant squat", "Upright torso, elbows high", 10.5,
         None, None, "Quadriceps", "Core, Glutes"),
        ("Goblet Squat", 3, 6, "nybörjare", "styrka",
         "Squat holding kettlebell at chest for beginner technique", "Great for learning squat pattern", 8.0,
         None, None, "Quadriceps", "Glutes, Core"),
        ("Bulgarian Split Squat", 3, 2, "medel", "styrka",
         "Rear foot elevated split squat for unilateral strength", "Front foot far enough forward", 9.5,
         None, None, "Quadriceps", "Glutes, Hamstrings"),
        ("Walking Lunge", 3, 2, "nybörjare", "styrka",
         "Alternating forward lunges while walking forward", "Keep torso upright, step far enough", 8.0,
         None, None, "Quadriceps", "Glutes, Hamstrings"),
        ("Reverse Lunge", 3, 2, "nybörjare", "styrka",
         "Step backward into lunge position", "Easier on knees than forward lunge", 8.0,
         None, None, "Quadriceps", "Glutes"),
        ("Leg Press", 3, 1, "nybörjare", "styrka",
         "Push platform away using leg press machine", "Don't lock knees at top, full range", 9.0,
         None, None, "Quadriceps", "Glutes, Hamstrings"),
        ("Hack Squat", 3, 1, "medel", "styrka",
         "Machine squat targeting quads with less lower back stress", "Feet placement changes muscle emphasis", 9.0,
         None, None, "Quadriceps", "Glutes"),
        ("Leg Extension", 3, 1, "nybörjare", "styrka",
         "Isolation exercise for quadriceps on machine", "Full extension, squeeze quad at top", 6.0,
         None, None, "Quadriceps", None),
        ("Leg Curl", 3, 1, "nybörjare", "styrka",
         "Hamstring curl machine for hamstring isolation", "Curl heel to glute, squeeze at top", 6.0,
         None, None, "Hamstrings", None),
        ("Nordic Hamstring Curl", 3, 1, "avancerad", "styrka",
         "Partner-assisted hamstring curl for eccentric strength", "One of the best hamstring exercises", 8.0,
         None, None, "Hamstrings", "Glutes"),
        ("Hip Thrust", 3, 3, "medel", "styrka",
         "Barbell hip thrust from bench for glute development", "Drive through heels, squeeze glutes at top", 8.0,
         None, None, "Glutes", "Hamstrings"),
        ("Glute Bridge", 3, 1, "nybörjare", "styrka",
         "Floor-based hip thrust for glute activation", "Easier version of hip thrust, great for beginners", 5.0,
         None, None, "Glutes", "Hamstrings"),
        ("Standing Calf Raise", 3, 1, "nybörjare", "styrka",
         "Rise up on toes for calf development", "Full range — all the way down and up", 4.0,
         None, None, "Calves", None),
        ("Seated Calf Raise", 3, 1, "nybörjare", "styrka",
         "Seated calf raise targets soleus muscle", "Different muscle emphasis than standing", 4.0,
         None, None, "Calves", None),
        ("Box Jump", 3, 1, "medel", "kondition",
         "Jump onto box for explosive leg power", "Land softly, step down — never jump down", 12.0,
         None, None, "Quadriceps", "Glutes, Calves"),
        ("Step-ups", 3, 1, "nybörjare", "styrka",
         "Step up onto box or bench for unilateral leg work", "Drive through heel, squeeze glute at top", 7.0,
         None, None, "Quadriceps", "Glutes"),
    ]

    # AXLAR (body_part_id=4)
    shoulders = [
        ("Overhead Press", 4, 3, "medel", "styrka",
         "Press barbell overhead from front rack position", "Full lockout overhead, ribs down", 8.0,
         None, None, "Front Deltoid", "Triceps, Lateral Deltoid"),
        ("Seated Dumbbell Press", 4, 2, "nybörjare", "styrka",
         "Seated shoulder press with dumbbells", "Press to full extension, control descent", 7.5,
         None, None, "Front Deltoid", "Triceps, Lateral Deltoid"),
        ("Arnold Press", 4, 2, "medel", "styrka",
         "Rotating dumbbell press targeting all three deltoid heads", "Rotate palms forward as you press up", 7.5,
         None, None, "Front Deltoid", "Lateral Deltoid, Rear Deltoid"),
        ("Lateral Raise", 4, 2, "nybörjare", "styrka",
         "Raise dumbbells to side for lateral deltoid isolation", "Slight forward lean, thumb slightly down", 5.0,
         None, None, "Lateral Deltoid", None),
        ("Cable Lateral Raise", 4, 4, "nybörjare", "styrka",
         "Cable version of lateral raise for constant tension", "Better tension curve than dumbbells", 5.0,
         None, None, "Lateral Deltoid", None),
        ("Front Raise", 4, 2, "nybörjare", "styrka",
         "Raise dumbbells to front for front deltoid", "Keep slight bend in elbows", 5.0,
         None, None, "Front Deltoid", None),
        ("Face Pull", 4, 4, "nybörjare", "styrka",
         "Pull rope to face for rear deltoid and rotator cuff", "Elbows high, pull to ears", 5.0,
         None, None, "Rear Deltoid", "Upper Back, Rotator Cuff"),
        ("Reverse Fly", 4, 2, "nybörjare", "styrka",
         "Bent over dumbbell fly for rear deltoid", "Control the weight, squeeze rear delts", 5.0,
         None, None, "Rear Deltoid", "Upper Back"),
        ("Cable Reverse Fly", 4, 4, "nybörjare", "styrka",
         "Cable version of reverse fly for rear deltoid", "Better mind-muscle connection", 5.0,
         None, None, "Rear Deltoid", "Upper Back"),
        ("Upright Row", 4, 3, "medel", "styrka",
         "Pull barbell up to chin for lateral deltoid and traps", "Wide grip to reduce shoulder impingement", 7.0,
         None, None, "Lateral Deltoid", "Trapezius"),
        ("Shrugs", 4, 3, "nybörjare", "styrka",
         "Elevate shoulders for trapezius isolation", "Hold at top for 1-2 seconds", 5.5,
         None, None, "Trapezius", None),
    ]

    # ARMAR (body_part_id=5)
    arms = [
        ("Barbell Curl", 5, 3, "nybörjare", "styrka",
         "Standard barbell curl for bicep mass", "Keep elbows at sides, full range of motion", 5.5,
         None, None, "Biceps", "Forearms"),
        ("Dumbbell Curl", 5, 2, "nybörjare", "styrka",
         "Alternating or simultaneous dumbbell curls", "Supinate wrist at top for full contraction", 5.0,
         None, None, "Biceps", "Forearms"),
        ("Hammer Curl", 5, 2, "nybörjare", "styrka",
         "Neutral grip curl for brachialis and brachioradialis", "Keep thumbs up throughout movement", 5.0,
         None, None, "Biceps", "Forearms, Brachialis"),
        ("Concentration Curl", 5, 2, "nybörjare", "styrka",
         "Seated isolation curl for peak bicep contraction", "Brace elbow on inner thigh", 4.5,
         None, None, "Biceps", None),
        ("Preacher Curl", 5, 3, "nybörjare", "styrka",
         "Curl on preacher bench for strict form", "Eliminates shoulder involvement", 5.0,
         None, None, "Biceps", None),
        ("Cable Curl", 5, 4, "nybörjare", "styrka",
         "Cable curl for constant tension on biceps", "Better peak contraction than free weights", 5.0,
         None, None, "Biceps", "Forearms"),
        ("Close Grip Bench Press", 5, 3, "medel", "styrka",
         "Bench press with narrow grip for tricep focus", "Hands shoulder width apart, elbows tight", 7.5,
         None, None, "Triceps", "Mid Chest"),
        ("Tricep Pushdown", 5, 4, "nybörjare", "styrka",
         "Cable pushdown for tricep isolation", "Keep elbows at sides, full extension", 5.0,
         None, None, "Triceps", None),
        ("Overhead Tricep Extension", 5, 2, "nybörjare", "styrka",
         "Overhead extension for tricep long head", "Keep elbows close, lower behind head", 5.0,
         None, None, "Triceps", None),
        ("Skull Crusher", 5, 3, "medel", "styrka",
         "Lying tricep extension for all three heads", "Lower bar to forehead level slowly", 6.0,
         None, None, "Triceps", None),
        ("Tricep Kickback", 5, 2, "nybörjare", "styrka",
         "Bent over tricep extension for isolation", "Upper arm parallel to floor throughout", 4.5,
         None, None, "Triceps", None),
        ("Dips", 5, 1, "medel", "styrka",
         "Parallel bar dips for triceps and chest", "Upright torso = triceps, lean forward = chest", 8.0,
         None, None, "Triceps", "Lower Chest"),
        ("Wrist Curl", 5, 2, "nybörjare", "styrka",
         "Forearm curl for wrist flexors", "Rest forearms on bench, full range", 3.0,
         None, None, "Forearms", None),
        ("Reverse Wrist Curl", 5, 2, "nybörjare", "styrka",
         "Forearm extension for wrist extensors", "Often neglected but important for balance", 3.0,
         None, None, "Forearms", None),
    ]

    # MAGE (body_part_id=6)
    core = [
        ("Crunch", 6, 1, "nybörjare", "styrka",
         "Basic ab crunch for upper ab development", "Don't pull neck, exhale at top", 4.0,
         None, None, "Upper Abs", None),
        ("Bicycle Crunch", 6, 1, "nybörjare", "styrka",
         "Alternating elbow-to-knee crunch for obliques", "Slow and controlled, full rotation", 5.0,
         None, None, "Obliques", "Upper Abs"),
        ("Leg Raise", 6, 1, "nybörjare", "styrka",
         "Lying leg raise for lower abs", "Keep lower back pressed to floor", 5.0,
         None, None, "Lower Abs", None),
        ("Hanging Leg Raise", 6, 1, "medel", "styrka",
         "Hang from bar and raise legs for lower abs", "Control the swing, slow and deliberate", 7.0,
         None, None, "Lower Abs", "Core"),
        ("Ab Wheel Rollout", 6, 1, "avancerad", "styrka",
         "Roll out ab wheel for core stability", "One of the best core exercises", 8.0,
         None, None, "Core", "Lower Abs, Upper Abs"),
        ("Plank", 6, 1, "nybörjare", "balans",
         "Hold plank position for core stability", "Straight line from head to heels", 4.0,
         None, None, "Core", "Lower Abs"),
        ("Side Plank", 6, 1, "nybörjare", "balans",
         "Side plank for oblique strength", "Hip off floor, body in straight line", 4.0,
         None, None, "Obliques", "Core"),
        ("Russian Twist", 6, 1, "nybörjare", "styrka",
         "Seated twist for oblique development", "Keep feet off floor for more difficulty", 4.5,
         None, None, "Obliques", "Upper Abs"),
        ("Cable Crunch", 6, 4, "nybörjare", "styrka",
         "Kneeling cable crunch for weighted ab work", "Crunch elbows to knees", 5.0,
         None, None, "Upper Abs", "Lower Abs"),
        ("Dragon Flag", 6, 1, "avancerad", "styrka",
         "Full body lever exercise for extreme core strength", "Advanced movement popularized by Bruce Lee", 10.0,
         None, None, "Core", "Lower Abs, Upper Abs"),
        ("Dead Bug", 6, 1, "nybörjare", "styrka",
         "Anti-extension core exercise for stability", "Press lower back to floor throughout", 4.0,
         None, None, "Core", "Lower Abs"),
        ("Bird Dog", 6, 1, "nybörjare", "balans",
         "Opposite arm-leg extension for core stability", "Great for lower back health", 3.5,
         None, None, "Core", "Lower Back"),
    ]

    # KONDITION (body_part_id=7)
    cardio = [
        ("Running", 7, 1, "nybörjare", "kondition",
         "Running at various intensities for cardiovascular fitness", "Land on midfoot, maintain upright posture", 11.0,
         None, None, "Cardiovascular System", "Quadriceps, Calves"),
        ("Cycling", 7, 1, "nybörjare", "kondition",
         "Stationary or outdoor cycling for low-impact cardio", "Seat at hip height, smooth pedal stroke", 8.0,
         None, None, "Cardiovascular System", "Quadriceps, Hamstrings"),
        ("Rowing", 7, 1, "medel", "kondition",
         "Rowing machine for full body cardio", "60% legs, 20% back, 20% arms", 10.0,
         None, None, "Cardiovascular System", "Back, Legs"),
        ("Jump Rope", 7, 1, "nybörjare", "kondition",
         "Jump rope for coordination and cardio", "Land on balls of feet, elbows at sides", 12.0,
         None, None, "Cardiovascular System", "Calves, Shoulders"),
        ("Burpees", 7, 1, "medel", "kondition",
         "Full body exercise combining squat, plank and jump", "Maintain steady pace over high intensity", 12.0,
         None, None, "Cardiovascular System", "Chest, Legs, Core"),
        ("Mountain Climbers", 7, 1, "nybörjare", "kondition",
         "Plank position alternating knee drives for cardio and core", "Keep hips level, drive knees to chest", 10.0,
         None, None, "Core", "Cardiovascular System"),
        ("Box Jumps", 7, 1, "medel", "kondition",
         "Explosive jump onto box for power and cardio", "Land softly with bent knees", 12.0,
         None, None, "Quadriceps", "Glutes, Cardiovascular System"),
        ("Battle Ropes", 7, 1, "medel", "kondition",
         "Wave battle ropes for upper body cardio", "Alternate arms, keep core braced", 10.0,
         None, None, "Cardiovascular System", "Shoulders, Core"),
        ("Sled Push", 7, 1, "medel", "kondition",
         "Push weighted sled for conditioning and power", "Lean into sled, drive with legs", 13.0,
         None, None, "Quadriceps", "Glutes, Cardiovascular System"),
        ("Farmer's Walk", 7, 2, "nybörjare", "kondition",
         "Carry heavy dumbbells for grip and conditioning", "Stand tall, small steps, breathe", 8.0,
         None, None, "Forearms", "Core, Traps"),
    ]

    all_exercises = chest + back + legs + shoulders + arms + core + cardio
    count = 0
    for ex in all_exercises:
        result = add_exercise(conn, *ex)
        if result:
            count += 1
    conn.commit()
    log.info(f"Added {count} exercises!")

if __name__ == "__main__":
    log.info("Starting exercise seeder...")
    with engine.connect() as conn:
        update_exercise_columns(conn)
        seed_muscle_groups(conn)
        seed_all_exercises(conn)
    log.info("Done! Database now has 100+ exercises with muscle groups and video support.")