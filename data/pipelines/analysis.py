import duckdb
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()

engine = create_engine(os.getenv("DATABASE_URL"))

def fetch_data_from_postgres() -> dict:
    """Hämtar all träningsdata från PostgreSQL."""
    with engine.connect() as conn:
        sessions = pd.read_sql(text("""
            SELECT 
                ws.id AS session_id,
                ws.user_id,
                ws.date,
                ws.duration_minutes,
                ws.total_calories,
                ws.mood
            FROM workout_sessions ws
        """), conn)

        exercises = pd.read_sql(text("""
            SELECT
                we.session_id,
                e.name AS exercise,
                bp.name AS body_part,
                e.difficulty,
                e.calories_per_minute,
                we.sets,
                we.reps,
                we.weight_kg,
                we.rpe
            FROM workout_exercises we
            JOIN exercises e ON we.exercise_id = e.id
            JOIN body_parts bp ON e.body_part_id = bp.id
        """), conn)

    return {"sessions": sessions, "exercises": exercises}

def analyze_with_duckdb(data: dict):
    """Analyserar träningsdata med DuckDB."""
    sessions = data["sessions"]
    exercises = data["exercises"]

    con = duckdb.connect()

    
    con.register("sessions", sessions)
    con.register("exercises", exercises)

    print("=" * 50)
    print("TRÄNINGSANALYS")
    print("=" * 50)

    
    print("\n Mest tränade kroppsdelar:")
    result = con.execute("""
        SELECT 
            body_part,
            COUNT(*) AS antal_gånger
        FROM exercises
        GROUP BY body_part
        ORDER BY antal_gånger DESC
    """).df()
    print(result.to_string(index=False))

    
    print("\n Övningar per svårighetsgrad:")
    result = con.execute("""
        SELECT 
            difficulty,
            COUNT(*) AS antal,
            ROUND(AVG(rpe), 1) AS snitt_ansträngning
        FROM exercises
        GROUP BY difficulty
        ORDER BY antal DESC
    """).df()
    print(result.to_string(index=False))

    
    print("\n Träningspass per vecka:")
    result = con.execute("""
        SELECT 
            STRFTIME(date, '%Y-%W') AS vecka,
            COUNT(*) AS antal_pass,
            SUM(duration_minutes) AS total_minuter
        FROM sessions
        WHERE date IS NOT NULL
        GROUP BY vecka
        ORDER BY vecka DESC
    """).df()
    if result.empty:
        print("   Ingen träningsdata ännu!")
    else:
        print(result.to_string(index=False))

    
    print("\n Topp övningar efter ansträngning:")
    result = con.execute("""
        SELECT 
            exercise,
            body_part,
            ROUND(AVG(rpe), 1) AS snitt_rpe,
            COUNT(*) AS antal_gånger
        FROM exercises
        WHERE rpe IS NOT NULL
        GROUP BY exercise, body_part
        ORDER BY snitt_rpe DESC
        LIMIT 5
    """).df()
    if result.empty:
        print("   Ingen RPE-data ännu!")
    else:
        print(result.to_string(index=False))

    print("\n" + "=" * 50)
    print("Analys klar!")
    con.close()

if __name__ == "__main__":
    print("Hämtar data från PostgreSQL...")
    data = fetch_data_from_postgres()
    print(f"Hämtade {len(data['sessions'])} träningspass och {len(data['exercises'])} övningar\n")
    analyze_with_duckdb(data)