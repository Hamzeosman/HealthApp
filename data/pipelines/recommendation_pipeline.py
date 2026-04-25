from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import pandas as pd
import logging
import os

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("pipeline.log"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)

load_dotenv()

try:
    engine = create_engine(os.getenv("DATABASE_URL"))
    log.info("Anslutning till databas lyckades!")
except Exception as e:
    log.error(f"Kunde inte ansluta till databasen: {e}")
    exit(1)

def get_all_users() -> list:
    """Hämtar alla användare från databasen."""
    with engine.connect() as conn:
        result = conn.execute(text("SELECT id, name FROM users"))
        return result.fetchall()

def get_untrained_body_parts(user_id: int) -> list:
    """Hittar kroppsdelar som inte tränats på 7+ dagar."""
    query = text("""
        SELECT 
            bp.id,
            bp.name,
            MAX(ws.date) AS last_trained,
            CASE 
                WHEN MAX(ws.date) IS NULL THEN 1.0
                ELSE LEAST(1.0, EXTRACT(DAY FROM NOW() - MAX(ws.date)) / 7.0)
            END AS score
        FROM body_parts bp
        LEFT JOIN exercises e ON e.body_part_id = bp.id
        LEFT JOIN workout_exercises we ON we.exercise_id = e.id
        LEFT JOIN workout_sessions ws ON ws.id = we.session_id 
            AND ws.user_id = :user_id
        GROUP BY bp.id, bp.name
        HAVING MAX(ws.date) IS NULL 
            OR MAX(ws.date) < CURRENT_DATE - INTERVAL '7 days'
        ORDER BY score DESC
    """)
    with engine.connect() as conn:
        result = conn.execute(query, {"user_id": user_id})
        return result.fetchall()

def generate_recommendations(user_id: int, user_name: str):
    """Genererar övningsrekommendationer och sparar i databasen."""
    try:
        untrained = get_untrained_body_parts(user_id)

        if not untrained:
            log.info(f"{user_name} har tränat alla kroppsdelar nyligen!")
            return

        with engine.connect() as conn:
            
            conn.execute(text(
                "DELETE FROM recommendations WHERE user_id = :user_id"
            ), {"user_id": user_id})

            for body_part in untrained:
                body_part_id = body_part[0]
                body_part_name = body_part[1]
                last_trained = body_part[2]
                score = float(body_part[3])

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
                        "score": score
                    })

                    log.info(f"[{user_name}] {exercise[1]} — {reason} (score: {score:.2f})")

            conn.commit()
            log.info(f"Rekommendationer sparade för {user_name}!")

    except Exception as e:
        log.error(f"Fel vid generering av rekommendationer för {user_name}: {e}")

if __name__ == "__main__":
    log.info("Startar recommendation pipeline...")
    
    users = get_all_users()
    
    if not users:
        log.warning("Inga användare hittades i databasen!")
        exit(0)

    log.info(f"Hittade {len(users)} användare")

    for user in users:
        user_id = user[0]
        user_name = user[1]
        log.info(f"Kör pipeline för {user_name} (ID: {user_id})")
        generate_recommendations(user_id, user_name)

    log.info("Pipeline klar!")