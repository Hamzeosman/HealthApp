from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"))

with engine.connect() as conn:
    
    user = conn.execute(text(
        "SELECT id FROM users WHERE email = 'test@healthapp.com'"
    )).fetchone()

    if not user:
        conn.execute(text("""
            INSERT INTO users (name, email, fitness_level, fitness_goal)
            VALUES ('Test User', 'test@healthapp.com', 'medel', 'bygga_muskler')
        """))
        conn.commit()
        user = conn.execute(text(
            "SELECT id FROM users WHERE email = 'test@healthapp.com'"
        )).fetchone()

    user_id = user[0]

    
    sessions = [
        ("2026-04-01", 60, 400, "bra"),
        ("2026-04-05", 45, 300, "okej"),
        ("2026-04-10", 75, 500, "stark"),
    ]

    for date, duration, calories, mood in sessions:
        conn.execute(text("""
            INSERT INTO workout_sessions (user_id, date, duration_minutes, total_calories, mood)
            VALUES (:user_id, :date, :duration, :calories, :mood)
        """), {"user_id": user_id, "date": date, "duration": duration,
               "calories": calories, "mood": mood})

    conn.commit()

    
    session_ids = conn.execute(text(
        "SELECT id FROM workout_sessions WHERE user_id = :user_id ORDER BY id",
    ), {"user_id": user_id}).fetchall()

    
    exercises = conn.execute(text(
        "SELECT id FROM exercises ORDER BY id LIMIT 9"
    )).fetchall()

    
    workout_data = [
        (session_ids[0][0], exercises[0][0], 4, 10, 80, 8),  # Bänkpress
        (session_ids[0][0], exercises[1][0], 3, 12, 20, 6),  # Hantelflyes
        (session_ids[0][0], exercises[7][0], 3, 12, 15, 7),  # Bicepscurl
        (session_ids[1][0], exercises[4][0], 4, 8,  100, 9), # Knäböj
        (session_ids[1][0], exercises[5][0], 3, 12, 0,  6),  # Utfall
        (session_ids[2][0], exercises[2][0], 4, 5,  120, 9), # Marklyft
        (session_ids[2][0], exercises[3][0], 3, 10, 60, 7),  # Latsdrag
        (session_ids[2][0], exercises[6][0], 4, 10, 50, 8),  # Militärpress
        (session_ids[2][0], exercises[8][0], 3, 12, 25, 6),  # Tricepspress
    ]

    for session_id, exercise_id, sets, reps, weight, rpe in workout_data:
        conn.execute(text("""
            INSERT INTO workout_exercises 
                (session_id, exercise_id, sets, reps, weight_kg, rpe)
            VALUES 
                (:session_id, :exercise_id, :sets, :reps, :weight, :rpe)
        """), {"session_id": session_id, "exercise_id": exercise_id,
               "sets": sets, "reps": reps, "weight": weight, "rpe": rpe})

    conn.commit()
    print("Testdata inlagd! 3 träningspass med 9 övningar.")