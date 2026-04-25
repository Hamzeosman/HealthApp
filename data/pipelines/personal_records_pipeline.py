from sqlalchemy import create_engine, text
from dotenv import load_dotenv
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
    """Hämtar alla användare."""
    with engine.connect() as conn:
        result = conn.execute(text("SELECT id, name FROM users"))
        return result.fetchall()

def get_latest_workout_exercises(user_id: int) -> list:
    """Hämtar övningar från senaste träningspasset."""
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT 
                we.exercise_id,
                e.name AS exercise_name,
                we.weight_kg,
                we.reps,
                ws.date
            FROM workout_exercises we
            JOIN workout_sessions ws ON we.session_id = ws.id
            JOIN exercises e ON we.exercise_id = e.id
            WHERE ws.user_id = :user_id
            AND ws.date = (
                SELECT MAX(date) FROM workout_sessions 
                WHERE user_id = :user_id
            )
        """), {"user_id": user_id})
        return result.fetchall()

def get_current_personal_record(user_id: int, exercise_id: int):
    """Hämtar nuvarande personbästa för en övning."""
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT weight_kg, reps FROM personal_records
            WHERE user_id = :user_id 
            AND exercise_id = :exercise_id
            ORDER BY weight_kg DESC
            LIMIT 1
        """), {"user_id": user_id, "exercise_id": exercise_id})
        return result.fetchone()

def update_personal_record(user_id: int, exercise_id: int, weight_kg: float, reps: int, date):
    """Sparar nytt personbästa i databasen."""
    with engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO personal_records (user_id, exercise_id, weight_kg, reps, date)
            VALUES (:user_id, :exercise_id, :weight_kg, :reps, :date)
        """), {
            "user_id": user_id,
            "exercise_id": exercise_id,
            "weight_kg": weight_kg,
            "reps": reps,
            "date": date
        })
        conn.commit()

def check_personal_records(user_id: int, user_name: str):
    """Kollar och uppdaterar personbästa för en användare."""
    try:
        latest = get_latest_workout_exercises(user_id)

        if not latest:
            log.warning(f"Inga träningspass hittades för {user_name}")
            return

        new_records = 0

        for exercise in latest:
            exercise_id = exercise[0]
            exercise_name = exercise[1]
            weight_kg = exercise[2]
            reps = exercise[3]
            date = exercise[4]

            if not weight_kg:
                continue

            current_pr = get_current_personal_record(user_id, exercise_id)

            if not current_pr:
                
                update_personal_record(user_id, exercise_id, weight_kg, reps, date)
                log.info(f"[{user_name}] Första personbästa! {exercise_name}: {weight_kg}kg x {reps} reps")
                new_records += 1

            elif weight_kg > current_pr[0]:
                
                update_personal_record(user_id, exercise_id, weight_kg, reps, date)
                log.info(f"[{user_name}] NYTT REKORD! {exercise_name}: {weight_kg}kg (tidigare: {current_pr[0]}kg)")
                new_records += 1

            else:
                log.info(f"[{user_name}] {exercise_name}: {weight_kg}kg — inget nytt rekord (bästa: {current_pr[0]}kg)")

        if new_records > 0:
            log.info(f"{user_name} satte {new_records} nya personbästa!")
        else:
            log.info(f"{user_name} satte inga nya personbästa denna gång.")

    except Exception as e:
        log.error(f"Fel vid kontroll av personbästa för {user_name}: {e}")

if __name__ == "__main__":
    log.info("Startar personal records pipeline...")

    users = get_all_users()

    if not users:
        log.warning("Inga användare hittades!")
        exit(0)

    log.info(f"Hittade {len(users)} användare")

    for user in users:
        user_id = user[0]
        user_name = user[1]
        log.info(f"Kollar personbästa för {user_name} (ID: {user_id})")
        check_personal_records(user_id, user_name)

    log.info("Personal records pipeline klar!")