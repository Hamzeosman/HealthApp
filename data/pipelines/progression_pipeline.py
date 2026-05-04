from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import pandas as pd
import duckdb
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

def get_weekly_volume(user_id: int) -> pd.DataFrame:
    """Hämtar total träningsvolym per vecka per övning."""
    with engine.connect() as conn:
        return pd.read_sql(text("""
            SELECT
                DATE_TRUNC('week', ws.date) AS week,
                e.name AS exercise,
                bp.name AS body_part,
                SUM(we.sets * we.reps * we.weight_kg) AS total_volume_kg,
                MAX(we.weight_kg) AS max_weight,
                AVG(we.rpe) AS avg_rpe,
                COUNT(*) AS total_sets
            FROM workout_sessions ws
            JOIN workout_exercises we ON ws.id = we.session_id
            JOIN exercises e ON we.exercise_id = e.id
            JOIN body_parts bp ON e.body_part_id = bp.id
            WHERE ws.user_id = :user_id
            AND we.weight_kg IS NOT NULL
            GROUP BY week, e.name, bp.name
            ORDER BY week DESC, total_volume_kg DESC
        """), conn, params={"user_id": user_id})

def get_recovery_data(user_id: int) -> pd.DataFrame:
    """Hämtar sömndata och återhämtning."""
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
            ORDER BY date DESC
        """), conn, params={"user_id": user_id})

def analyze_progression(user_id: int, user_name: str):
    """Analyserar progression och genererar smarta insikter."""
    try:
        volume_df = get_weekly_volume(user_id)
        recovery_df = get_recovery_data(user_id)

        if volume_df.empty:
            log.warning(f"Ingen träningsdata för {user_name}")
            return

        con = duckdb.connect()
        con.register("volume", volume_df)

        log.info(f"\n{'='*50}")
        log.info(f"PROGRESSIONSANALYS FÖR {user_name.upper()}")
        log.info(f"{'='*50}")

        # Analys 1: Volymökning per övning
        progression = con.execute("""
            SELECT
                exercise,
                body_part,
                COUNT(DISTINCT week) AS antal_veckor,
                MIN(total_volume_kg) AS min_volym,
                MAX(total_volume_kg) AS max_volym,
                MAX(max_weight) AS bästa_vikt,
                ROUND(
                    (MAX(total_volume_kg) - MIN(total_volume_kg)) 
                    / NULLIF(MIN(total_volume_kg), 0) * 100, 1
                ) AS volym_ökning_procent
            FROM volume
            GROUP BY exercise, body_part
            HAVING COUNT(DISTINCT week) > 1
            ORDER BY volym_ökning_procent DESC
        """).df()

        if not progression.empty:
            log.info("\nVolymökning per övning:")
            for _, row in progression.iterrows():
                trend = "" if row['volym_ökning_procent'] > 0 else "📉"
                log.info(
                    f"  {trend} {row['exercise']}: "
                    f"{row['volym_ökning_procent']}% ökning | "
                    f"Bästa vikt: {row['bästa_vikt']}kg"
                )

        # Analys 2: Svagaste kroppsdelar
        weak = con.execute("""
            SELECT
                body_part,
                ROUND(AVG(total_volume_kg), 1) AS snitt_volym
            FROM volume
            GROUP BY body_part
            ORDER BY snitt_volym ASC
            LIMIT 3
        """).df()

        log.info("\nKroppsdelar som behöver mer fokus:")
        for _, row in weak.iterrows():
            log.info(f"  {row['body_part']}: {row['snitt_volym']}kg snittvolym")

        # Analys 3: Återhämtning vs prestation
        if not recovery_df.empty:
            avg_sleep = recovery_df['sleep_hours'].mean()
            avg_energy = recovery_df['energy_level'].mean()
            avg_stress = recovery_df['stress_level'].mean()

            log.info("\nÅterhämtningsanalys:")
            log.info(f"  Snitt sömn: {avg_sleep:.1f} timmar")
            log.info(f"  Snitt energi: {avg_energy:.1f}/10")
            log.info(f"  Snitt stress: {avg_stress:.1f}/10")

            if avg_sleep < 7:
                log.info("  VARNING: Du sover för lite! Sikta på 7-9 timmar för optimal återhämtning.")
            if avg_stress > 7:
                log.info("  VARNING: Hög stressnivå! Överväg lättare träning denna vecka.")
            if avg_energy < 5:
                log.info("  VARNING: Låg energi! Vila kan vara viktigare än träning just nu.")

        # Analys 4: Spara intensitetslogg
        weekly_summary = con.execute("""
            SELECT
                week,
                COUNT(DISTINCT exercise) AS antal_övningar,
                SUM(total_volume_kg) AS total_volym,
                ROUND(AVG(avg_rpe), 2) AS snitt_rpe,
                SUM(total_sets) AS totala_set
            FROM volume
            GROUP BY week
            ORDER BY week DESC
            LIMIT 4
        """).df()

        log.info("\nSenaste veckornas träning:")
        for _, row in weekly_summary.iterrows():
            log.info(
                f"  Vecka {row['week'].strftime('%Y-%W')}: "
                f"{row['total_volym']:.0f}kg volym | "
                f"RPE: {row['snitt_rpe']} | "
                f"{row['totala_set']} set"
            )

        # Spara till workout_intensity_log
        with engine.connect() as conn:
            for _, row in weekly_summary.iterrows():
                week_num = int(row['week'].strftime('%W'))
                year = int(row['week'].strftime('%Y'))

                existing = conn.execute(text("""
                    SELECT id FROM workout_intensity_log
                    WHERE user_id = :user_id 
                    AND week_number = :week 
                    AND year = :year
                """), {"user_id": user_id, "week": week_num, "year": year}).fetchone()

                if not existing:
                    conn.execute(text("""
                        INSERT INTO workout_intensity_log 
                            (user_id, week_number, year, total_sessions, total_volume_kg, avg_rpe)
                        VALUES (:user_id, :week, :year, :sessions, :volume, :rpe)
                    """), {
                        "user_id": user_id,
                        "week": week_num,
                        "year": year,
                        "sessions": int(row['antal_övningar']),
                        "volume": float(row['total_volym']),
                        "rpe": float(row['snitt_rpe'])
                    })
            conn.commit()
            log.info("\nIntensitetslogg sparad!")

        con.close()

    except Exception as e:
        log.error(f"Fel vid progressionsanalys för {user_name}: {e}")

if __name__ == "__main__":
    log.info("Startar progressionspipeline...")

    with engine.connect() as conn:
        users = conn.execute(text("SELECT id, name FROM users")).fetchall()

    if not users:
        log.warning("Inga användare hittades!")
        exit(0)

    for user in users:
        analyze_progression(user[0], user[1])

    log.info("Progressionspipeline klar!")