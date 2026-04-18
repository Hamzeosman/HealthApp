from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import pandas as pd
import os

load_dotenv()

engine = create_engine(os.getenv("DATABASE_URL"))

def get_user_workout_history(user_id: int) -> pd.DataFrame:
    """Hämtar användarens träningshistorik."""
    query = text("""
        SELECT 
            ws.date,
            bp.name AS body_part,
            e.name AS exercise,
            e.difficulty
        FROM workout_sessions ws
        JOIN workout_exercises we ON ws.id = we.session_id
        JOIN exercises e ON we.exercise_id = e.id
        JOIN body_parts bp ON e.body_part_id = bp.id
        WHERE ws.user_id = :user_id
        ORDER BY ws.date DESC
    """)
    with engine.connect() as conn:
        return pd.read_sql(query, conn, params={"user_id": user_id})

def get_untrained_body_parts(user_id: int) -> list:
    """Hittar kroppsdelar som inte tränats på 7+ dagar."""
    query = text("""
        SELECT 
            bp.id,
            bp.name,
            MAX(ws.date) AS last_trained
        FROM body_parts bp
        LEFT JOIN exercises e ON e.body_part_id = bp.id
        LEFT JOIN workout_exercises we ON we.exercise_id = e.id
        LEFT JOIN workout_sessions ws ON ws.id = we.session_id 
            AND ws.user_id = :user_id
        GROUP BY bp.id, bp.name
        HAVING MAX(ws.date) IS NULL 
            OR MAX(ws.date) < CURRENT_DATE - INTERVAL '7 days'
    """)
    with engine.connect() as conn:
        result = conn.execute(query, {"user_id": user_id})
        return result.fetchall()

def generate_recommendations(user_id: int):
    """Genererar övningsrekommendationer och sparar i databasen."""
    untrained = get_untrained_body_parts(user_id)

    if not untrained:
        print(" Användaren har tränat alla kroppsdelar nyligen!")
        return

    with engine.connect() as conn:
        
        conn.execute(text("""
            DELETE FROM recommendations WHERE user_id = :user_id
        """), {"user_id": user_id})

        for body_part in untrained:
            body_part_id = body_part[0]
            body_part_name = body_part[1]
            last_trained = body_part[2]

            
            exercise = conn.execute(text("""
                SELECT id, name FROM exercises
                WHERE body_part_id = :body_part_id
                ORDER BY RANDOM()
                LIMIT 1
            """), {"body_part_id": body_part_id}).fetchone()

            if exercise:
                reason = (
                    f"Du har inte tränat {body_part_name} sedan {last_trained}"
                    if last_trained
                    else f"Du har aldrig tränat {body_part_name}!"
                )

                conn.execute(text("""
                    INSERT INTO recommendations (user_id, exercise_id, reason, score)
                    VALUES (:user_id, :exercise_id, :reason, :score)
                """), {
                    "user_id": user_id,
                    "exercise_id": exercise[0],
                    "reason": reason,
                    "score": 1.0
                })

                print(f" Rekommendation: {exercise[1]} — {reason}")

        conn.commit()
        print("\nRekommendationer sparade i databasen!")

if __name__ == "__main__":
    
    print("Lägger till testanvändare...")
    with engine.connect() as conn:
        existing = conn.execute(text(
            "SELECT id FROM users WHERE email = 'test@healthapp.com'"
        )).fetchone()

        if not existing:
            conn.execute(text("""
                INSERT INTO users (name, email, fitness_level, goal)
                VALUES ('Test User', 'test@healthapp.com', 'medel', 'bygga_muskler')
            """))
            conn.commit()

        user = conn.execute(text(
            "SELECT id FROM users WHERE email = 'test@healthapp.com'"
        )).fetchone()

    print(f"Kör pipeline för användare ID: {user[0]}")
    generate_recommendations(user[0])