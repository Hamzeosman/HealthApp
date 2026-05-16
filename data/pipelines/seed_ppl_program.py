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

def seed_ppl_program():
    with engine.connect() as conn:

        # ================================
        # LÄGG TILL FLER ÖVNINGAR
        # ================================
        log.info("Adding exercises...")

        new_exercises = [
            # Push
            ("Incline Bänkpress", 1, 3, "medel", "styrka", "Bänkpress i uppåtlutad position för övre bröst", "30-45 graders vinkel", 8.5),
            ("Cable Flyes", 1, 4, "nybörjare", "styrka", "Kabelflyes för bröst isolering", "Håll lätt böjda armar", 6.0),
            ("Dips", 1, 1, "medel", "styrka", "Kroppsviktsdips för nedre bröst och triceps", "Luta framåt för mer bröst", 7.0),
            ("Lateral Raises", 4, 2, "nybörjare", "styrka", "Hantellyft åt sidan för laterala deltamuskeln", "Håll lätt böjda armar", 5.0),
            ("Front Raises", 4, 2, "nybörjare", "styrka", "Hantellyft framåt för främre deltamuskeln", "Kontrollerad rörelse", 5.0),
            ("Overhead Tricep Extension", 5, 2, "nybörjare", "styrka", "Tricepsförlängning över huvudet", "Håll armbågarna stilla", 5.0),
            ("Skull Crushers", 5, 3, "medel", "styrka", "EZ-stång tricepspress liggande", "Kontrollera vikten hela vägen", 6.0),

            # Pull
            ("Seated Cable Row", 2, 4, "nybörjare", "styrka", "Sittande kabelrodd för mellankropp och rygg", "Dra mot naveln", 7.0),
            ("Face Pulls", 4, 4, "nybörjare", "styrka", "Kabeldrag mot ansiktet för bakre deltamuskel", "Håll armbågarna högt", 5.0),
            ("Incline Dumbbell Curl", 5, 2, "medel", "styrka", "Bicepscurl i lutad position för full stretch", "Kontrollera hela rörelsen", 5.5),
            ("Hammer Curl", 5, 2, "nybörjare", "styrka", "Neutral greppscurl för brachialis", "Håll armbågarna stilla", 5.0),
            ("Pull-ups", 2, 1, "avancerad", "styrka", "Kroppsvikts chins för rygg och biceps", "Full range of motion", 8.0),

            # Ben
            ("Leg Press", 3, 1, "nybörjare", "styrka", "Benpress i maskin för quad dominans", "Fötterna axelbrett", 9.0),
            ("Romanian Deadlift", 3, 3, "medel", "styrka", "Stelt ben marklyft för hamstrings", "Håll ryggen neutral", 9.5),
            ("Leg Curl", 3, 1, "nybörjare", "styrka", "Benböj i maskin för hamstrings isolering", "Full range of motion", 6.0),
            ("Leg Extension", 3, 1, "nybörjare", "styrka", "Benlyft i maskin för quad isolering", "Kontrollerad ned", 6.0),
            ("Calf Raises", 3, 1, "nybörjare", "styrka", "Tåhävningar för vader", "Full stretch i botten", 4.0),
            ("Hip Thrust", 3, 3, "medel", "styrka", "Höftlyft med skivstång för gluteus", "Pressa i toppen", 7.0),
            ("Bulgarian Split Squat", 3, 2, "avancerad", "styrka", "Enbensknäböj med bak fot upphöjd", "Håll överkroppen upprätt", 9.0),
        ]

        for ex in new_exercises:
            existing = conn.execute(text(
                "SELECT id FROM exercises WHERE name = :name"
            ), {"name": ex[0]}).fetchone()
            if not existing:
                conn.execute(text("""
                    INSERT INTO exercises 
                        (name, body_part_id, equipment_id, difficulty, exercise_type, description, tips, calories_per_minute)
                    VALUES (:name, :bp, :eq, :diff, :type, :desc, :tips, :cal)
                """), {
                    "name": ex[0], "bp": ex[1], "eq": ex[2], "diff": ex[3],
                    "type": ex[4], "desc": ex[5], "tips": ex[6], "cal": ex[7]
                })
        conn.commit()
        log.info("Exercises added!")

        # ================================
        # PPL TRÄNINGSPLAN
        # ================================
        log.info("Creating PPL program...")

        existing_plan = conn.execute(text(
            "SELECT id FROM training_plans WHERE name = 'PPL — Push Pull Legs 13 Week'"
        )).fetchone()

        if existing_plan:
            plan_id = existing_plan[0]
            log.info("Plan already exists, using existing.")
        else:
            result = conn.execute(text("""
                INSERT INTO training_plans 
                    (name, goal, difficulty, duration_weeks, days_per_week, description, target_audience)
                VALUES (
                    'PPL — Push Pull Legs 13 Week',
                    'bygga_muskler',
                    'medel',
                    13,
                    6,
                    'A science-based 13-week Push Pull Legs program with progressive overload. Week 1-4: Foundation, Week 5-8: Volume, Week 9-12: Intensity, Week 13: Deload.',
                    'Intermediate lifters who want to maximize muscle growth with a proven split'
                )
                RETURNING id
            """)).fetchone()
            plan_id = result[0]
            conn.commit()
            log.info(f"PPL plan created with ID: {plan_id}")

        # ================================
        # HÄMTA ÖVNINGS-IDs
        # ================================
        def get_exercise_id(name):
            result = conn.execute(text(
                "SELECT id FROM exercises WHERE name = :name"
            ), {"name": name}).fetchone()
            return result[0] if result else None

        # ================================
        # TRÄNINGSDAGAR STRUKTUR
        # ================================
        phases = [
            {"weeks": range(1, 5), "name": "Foundation", "sets_multiplier": 1.0},
            {"weeks": range(5, 9), "name": "Volume", "sets_multiplier": 1.2},
            {"weeks": range(9, 13), "name": "Intensity", "sets_multiplier": 1.0},
            {"weeks": range(13, 14), "name": "Deload", "sets_multiplier": 0.5},
        ]

        push_exercises = [
            ("Bänkpress", 4, 8, 120, "heavy"),
            ("Incline Bänkpress", 3, 10, 90, "moderate"),
            ("Cable Flyes", 3, 12, 60, "light"),
            ("Militärpress", 3, 8, 90, "heavy"),
            ("Lateral Raises", 4, 15, 60, "light"),
            ("Skull Crushers", 3, 10, 75, "moderate"),
            ("Overhead Tricep Extension", 3, 12, 60, "light"),
        ]

        pull_exercises = [
            ("Marklyft", 4, 6, 150, "heavy"),
            ("Latsdrag", 4, 10, 90, "moderate"),
            ("Seated Cable Row", 3, 10, 90, "moderate"),
            ("Face Pulls", 3, 15, 60, "light"),
            ("Bicepscurl", 3, 10, 75, "moderate"),
            ("Hammer Curl", 3, 12, 60, "light"),
            ("Incline Dumbbell Curl", 2, 12, 60, "light"),
        ]

        leg_exercises = [
            ("Knäböj", 4, 8, 120, "heavy"),
            ("Romanian Deadlift", 3, 10, 90, "moderate"),
            ("Leg Press", 3, 12, 90, "moderate"),
            ("Bulgarian Split Squat", 3, 10, 90, "moderate"),
            ("Leg Curl", 3, 12, 60, "light"),
            ("Leg Extension", 3, 15, 60, "light"),
            ("Calf Raises", 4, 15, 45, "light"),
        ]

        days_structure = [
            (1, "Push A", "Chest, Shoulders, Triceps", push_exercises),
            (2, "Pull A", "Back, Biceps", pull_exercises),
            (3, "Legs A", "Quads, Hamstrings, Glutes, Calves", leg_exercises),
            (4, "Rest", "Active recovery or cardio", []),
            (5, "Push B", "Chest, Shoulders, Triceps", push_exercises),
            (6, "Pull B", "Back, Biceps", pull_exercises),
            (7, "Legs B", "Quads, Hamstrings, Glutes, Calves", leg_exercises),
        ]

        total_days = 0
        for phase in phases:
            for week in phase["weeks"]:
                for day_num, day_name, focus, exercises in days_structure:
                    is_rest = day_name == "Rest"
                    is_deload = phase["name"] == "Deload"

                    result = conn.execute(text("""
                        INSERT INTO training_plan_days
                            (plan_id, week_number, day_number, day_name, focus, rest_day)
                        VALUES (:plan_id, :week, :day, :name, :focus, :rest)
                        RETURNING id
                    """), {
                        "plan_id": plan_id,
                        "week": week,
                        "day": day_num,
                        "name": f"Week {week} — {day_name}" + (f" ({phase['name']})" if day_num == 1 else ""),
                        "focus": focus,
                        "rest": is_rest
                    }).fetchone()
                    day_id = result[0]

                    if not is_rest:
                        for order, (ex_name, sets, reps, rest, intensity) in enumerate(exercises, 1):
                            ex_id = get_exercise_id(ex_name)
                            if ex_id:
                                actual_sets = max(1, round(sets * phase["sets_multiplier"]))
                                if is_deload:
                                    actual_reps = max(5, reps - 2)
                                    intensity = "light"
                                else:
                                    actual_reps = reps

                                conn.execute(text("""
                                    INSERT INTO training_plan_exercises
                                        (plan_day_id, exercise_id, sets, reps, rest_seconds, intensity, order_index)
                                    VALUES (:day_id, :ex_id, :sets, :reps, :rest, :intensity, :order)
                                """), {
                                    "day_id": day_id,
                                    "ex_id": ex_id,
                                    "sets": actual_sets,
                                    "reps": actual_reps,
                                    "rest": rest,
                                    "intensity": intensity,
                                    "order": order
                                })
                    total_days += 1

        conn.commit()
        log.info(f"PPL program created! {total_days} days added.")
        log.info("Week 1-4:  Foundation — learning the movements")
        log.info("Week 5-8:  Volume — more sets and frequency")
        log.info("Week 9-12: Intensity — heavier weights")
        log.info("Week 13:   Deload — rest and recovery")

if __name__ == "__main__":
    log.info("Starting PPL program seed...")
    seed_ppl_program()
    log.info("Done!")