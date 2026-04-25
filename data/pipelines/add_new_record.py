from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"))

with engine.connect() as conn:
    # Lägg till nytt träningspass
    conn.execute(text("""
        INSERT INTO workout_sessions (user_id, date, duration_minutes)
        VALUES (1, CURRENT_DATE, 60)
    """))
    
    session = conn.execute(text("""
        SELECT id FROM workout_sessions 
        WHERE user_id = 1 
        ORDER BY id DESC LIMIT 1
    """)).fetchone()
    
    # Marklyft 150kg — nytt rekord!
    conn.execute(text("""
        INSERT INTO workout_exercises (session_id, exercise_id, sets, reps, weight_kg, rpe)
        VALUES (:sid, 3, 5, 3, 150, 10)
    """), {"sid": session[0]})
    
    conn.commit()
    print("Nytt pass med Marklyft 150kg tillagt!")