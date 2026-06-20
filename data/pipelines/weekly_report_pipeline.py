from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import pandas as pd
import duckdb
import logging
import os
from datetime import datetime, timedelta

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


def get_ref_date(user_id: int):
    """Returnerar senaste träningsdatum för en user."""
    with engine.connect() as conn:
        result = conn.execute(text(
            "SELECT MAX(date) FROM workout_sessions WHERE user_id = :uid"
        ), {"uid": user_id}).scalar()
    return result

def get_weekly_training(user_id: int) -> pd.DataFrame:
    """Hämtar veckans träningsdata."""
    with engine.connect() as conn:
        return pd.read_sql(text("""
            SELECT
                ws.date,
                ws.duration_minutes,
                ws.mood,
                e.name AS exercise,
                bp.name AS body_part,
                we.sets,
                we.reps,
                we.weight_kg,
                we.rpe,
                e.calories_per_minute
            FROM workout_sessions ws
            JOIN workout_exercises we ON ws.id = we.session_id
            JOIN exercises e ON we.exercise_id = e.id
            JOIN body_parts bp ON e.body_part_id = bp.id
            WHERE ws.user_id = :user_id
            AND ws.date >= (SELECT MAX(date) - INTERVAL '7 days' FROM workout_sessions WHERE user_id = :user_id)
        """), conn, params={"user_id": user_id})

def get_weekly_recovery(user_id: int) -> pd.DataFrame:
    """Hämtar veckans återhämtningsdata."""
    with engine.connect() as conn:
        return pd.read_sql(text("""
            SELECT
                date,
                sleep_hours,
                sleep_quality,
                stress_level,
                energy_level
            FROM recovery_logs
            WHERE user_id = :user_id
            AND date >= (SELECT MAX(date) - INTERVAL '7 days' FROM workout_sessions WHERE user_id = :user_id)
        """), conn, params={"user_id": user_id})

def get_weekly_body_measurements(user_id: int) -> pd.DataFrame:
    """Hämtar veckans kroppsmått."""
    with engine.connect() as conn:
        return pd.read_sql(text("""
            SELECT
                date,
                weight_kg,
                body_fat_percentage,
                muscle_mass_kg,
                chest_cm,
                waist_cm,
                bicep_cm
            FROM body_measurements
            WHERE user_id = :user_id
            AND date >= CURRENT_DATE - INTERVAL '7 days'
        """), conn, params={"user_id": user_id})

def get_personal_records_this_week(user_id: int) -> pd.DataFrame:
    """Hämtar personbästa satta denna vecka."""
    with engine.connect() as conn:
        return pd.read_sql(text("""
            SELECT
                e.name AS exercise,
                pr.weight_kg,
                pr.reps,
                pr.date
            FROM personal_records pr
            JOIN exercises e ON pr.exercise_id = e.id
            WHERE pr.user_id = :user_id
            AND pr.date >= (SELECT MAX(ws2.date) - INTERVAL '7 days' FROM workout_sessions ws2 WHERE ws2.user_id = :user_id)
            ORDER BY pr.date DESC
        """), conn, params={"user_id": user_id})

def generate_weekly_report(user_id: int, user_name: str):
    """Genererar en komplett veckorapport."""
    try:
        training_df = get_weekly_training(user_id)
        recovery_df = get_weekly_recovery(user_id)
        measurements_df = get_weekly_body_measurements(user_id)
        records_df = get_personal_records_this_week(user_id)

        week = get_ref_date(user_id).strftime('%Y vecka %W') if get_ref_date(user_id) else datetime.now().strftime('%Y vecka %W')

        log.info(f"\n{'='*55}")
        log.info(f"VECKORAPPORT - {user_name.upper()} - {week}")
        log.info(f"{'='*55}")

        # ================================
        # DEL 1: TRANING
        # ================================
        log.info("\n--- TRANINGSSAMMANFATTNING ---")

        if training_df.empty:
            log.info("Ingen traning registrerad denna vecka.")
        else:
            con = duckdb.connect()
            con.register("training", training_df)

            # Antal pass och minuter
            summary = con.execute("""
                SELECT
                    COUNT(DISTINCT date) AS antal_pass,
                    SUM(duration_minutes) AS total_minuter,
                    SUM(sets * reps * COALESCE(weight_kg, 0)) AS total_volym,
                    ROUND(AVG(rpe), 1) AS snitt_rpe,
                    SUM(duration_minutes * COALESCE(calories_per_minute, 7)) AS kalorier
                FROM training
            """).fetchone()

            log.info(f"Antal trningspass: {summary[0]}")
            log.info(f"Total traningstid: {summary[1]} minuter")
            log.info(f"Total volym: {summary[2]:.0f} kg")
            log.info(f"Snitt anstrangning (RPE): {summary[3]}/10")
            log.info(f"Uppskattade kalorier: {summary[4]:.0f} kcal")

            # Trnade kroppsdelar
            body_parts = con.execute("""
                SELECT body_part, COUNT(*) AS antal
                FROM training
                GROUP BY body_part
                ORDER BY antal DESC
            """).df()

            log.info("\nTranade kroppsdelar:")
            for _, row in body_parts.iterrows():
                log.info(f"  {row['body_part']}: {row['antal']} ovningar")

            # Mood analys
            mood = con.execute("""
                SELECT mood, COUNT(*) AS antal
                FROM training
                WHERE mood IS NOT NULL
                GROUP BY mood
                ORDER BY antal DESC
            """).df()

            if not mood.empty:
                log.info(f"\nHumor under traning: {mood.iloc[0]['mood']}")

            con.close()

        # ================================
        # DEL 2: PERSONBASTA
        # ================================
        log.info("\n--- PERSONBASTA DENNA VECKA ---")

        if records_df.empty:
            log.info("Inga nya personbasta denna vecka.")
        else:
            log.info(f"GRATTIS! {len(records_df)} nya personbasta!")
            for _, row in records_df.iterrows():
                log.info(f"  {row['exercise']}: {row['weight_kg']}kg x {row['reps']} reps")

        # ================================
        # DEL 3: ATERHAMTNING
        # ================================
        log.info("\n--- ATERHAMTNING & SOMN ---")

        if recovery_df.empty:
            log.info("Ingen aterhamtningsdata registrerad.")
        else:
            avg_sleep = recovery_df['sleep_hours'].mean()
            avg_quality = recovery_df['sleep_quality'].mean()
            avg_energy = recovery_df['energy_level'].mean()
            avg_stress = recovery_df['stress_level'].mean()

            log.info(f"Snitt somn: {avg_sleep:.1f} timmar/natt")
            log.info(f"Somnkvalitet: {avg_quality:.1f}/10")
            log.info(f"Energiniva: {avg_energy:.1f}/10")
            log.info(f"Stressniva: {avg_stress:.1f}/10")

            # Smarta varningar
            log.info("\nAterhamtningsbedomning:")
            if avg_sleep >= 7 and avg_energy >= 7:
                log.info("  STATUS: OPTIMAL - Kroppen ar redo att prestera!")
            elif avg_sleep < 6:
                log.info("  VARNING: For lite somn! Vila mer for battre resultat.")
            elif avg_stress > 7:
                log.info("  VARNING: Hog stressniva! Overvaag lattare traning.")
            elif avg_energy < 5:
                log.info("  VARNING: Lag energi! Prioritera aterhamtning.")
            else:
                log.info("  STATUS: BRA - Fortsatt bra arbete!")

        # ================================
        # DEL 4: KROPPSMATT
        # ================================
        log.info("\n--- KROPPSUTVECKLING ---")

        if measurements_df.empty:
            log.info("Inga kroppsmatt registrerade denna vecka.")
        else:
            latest = measurements_df.iloc[0]
            log.info(f"Vikt: {latest['weight_kg']}kg")
            if latest['body_fat_percentage']:
                log.info(f"Fettprocent: {latest['body_fat_percentage']}%")
            if latest['muscle_mass_kg']:
                log.info(f"Muskelmassa: {latest['muscle_mass_kg']}kg")

        # ================================
        # DEL 5: REKOMMENDATION FOR NASTA VECKA
        # ================================
        log.info("\n--- REKOMMENDATION FOR NASTA VECKA ---")

        if not training_df.empty:
            con = duckdb.connect()
            con.register("training", training_df)

            # Hitta minst trand kroppsdel
            least_trained = con.execute("""
                SELECT body_part, COUNT(*) AS antal
                FROM training
                GROUP BY body_part
                ORDER BY antal ASC
                LIMIT 1
            """).fetchone()

            if least_trained:
                log.info(f"Fokusera mer pa: {least_trained[0]}")

            # Rekommendera vila om hog RPE
            avg_rpe = training_df['rpe'].mean()
            if avg_rpe and avg_rpe > 8:
                log.info("Overvaeg en aktiv vilodag - du har traint hart!")
            elif avg_rpe and avg_rpe < 6:
                log.info("Du kan oka intensiteten nasta vecka!")

            con.close()

        log.info(f"\n{'='*55}")
        log.info("VECKORAPPORT KLAR!")
        log.info(f"{'='*55}\n")

    except Exception as e:
        log.error(f"Fel vid generering av veckorapport for {user_name}: {e}")

if __name__ == "__main__":
    log.info("Startar veckorapport pipeline...")

    with engine.connect() as conn:
        users = conn.execute(text("SELECT id, name FROM users")).fetchall()

    if not users:
        log.warning("Inga anvandare hittades!")
        exit(0)

    log.info(f"Genererar rapporter for {len(users)} anvandare")

    for user in users:
        generate_weekly_report(user[0], user[1])

    log.info("Alla veckorapporter klara!")