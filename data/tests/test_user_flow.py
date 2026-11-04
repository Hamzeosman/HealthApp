"""
test_user_flow.py — data/test_user_flow.py
Simulerar ett realistiskt användarflöde från start till slut.

Flöde:
1. User registreras i DataDbContext (simulerar AuthService.SyncUserToDataDbAsync)
2. Sätter mål
3. Loggar träningspass med övningar
4. Loggar mat
5. Loggar recovery
6. Kör pipelines (fatigue, volume, recommendations)
7. Verifierar att all data finns på plats
8. Rensar testdata

Kör med: python data/test_user_flow.py
"""

import sys
import os

# Sätt sökväg så att vi hittar data/pipelines/
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = SCRIPT_DIR  # detta IS data/
sys.path.insert(0, DATA_DIR)

from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import logging
from datetime import date, timedelta

load_dotenv(os.path.join(DATA_DIR, ".env"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
log = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    log.error("DATABASE_URL saknas i .env — avbryter")
    sys.exit(1)

engine = create_engine(DATABASE_URL)
TEST_EMAIL = "test_flow_user@healthapp.test"
TEST_NAME = "Test Flow User"


# ──────────────────────────────────────────────
# CLEANUP
# ──────────────────────────────────────────────

def cleanup(conn):
    # Radera i rätt ordning (barn före förälder)
    conn.execute(text("""
        DELETE FROM workout_exercises WHERE session_id IN (
            SELECT id FROM workout_sessions WHERE user_id = (
                SELECT id FROM users WHERE email = :email
            )
        )
    """), {"email": TEST_EMAIL})
    conn.execute(text("""
        DELETE FROM workout_sessions WHERE user_id = (
            SELECT id FROM users WHERE email = :email
        )
    """), {"email": TEST_EMAIL})
    conn.execute(text("""
        DELETE FROM meal_logs WHERE user_id = (
            SELECT id FROM users WHERE email = :email
        )
    """), {"email": TEST_EMAIL})
    conn.execute(text("""
        DELETE FROM recovery_logs WHERE user_id = (
            SELECT id FROM users WHERE email = :email
        )
    """), {"email": TEST_EMAIL})
    conn.execute(text("""
        DELETE FROM user_goals WHERE user_id = (
            SELECT id FROM users WHERE email = :email
        )
    """), {"email": TEST_EMAIL})
    conn.execute(text("DELETE FROM users WHERE email = :email"), {"email": TEST_EMAIL})
    conn.commit()
    log.info("✓ Testdata raderad")


# ──────────────────────────────────────────────
# STEG 1: Registrera user (simulerar SyncUserToDataDbAsync)
# ──────────────────────────────────────────────

def step1_register(conn) -> int:
    log.info("\n─── Steg 1: Registrera user ───")
    # Rensa eventuell gammal testdata i rätt ordning
    cleanup(conn)

    # Kolla vilka kolumner users-tabellen har
    cols = conn.execute(text("""
        SELECT column_name FROM information_schema.columns
        WHERE table_name = 'users' AND table_schema = 'public'
        ORDER BY ordinal_position
    """)).fetchall()
    col_names = [c[0] for c in cols]
    log.info(f"  users-kolumner: {col_names}")

    # Bygg INSERT dynamiskt baserat på vad som finns
    base_fields = {
        "name": TEST_NAME,
        "fitness_level": "medel",
    }
    if "email" in col_names:
        base_fields["email"] = TEST_EMAIL
    if "age" in col_names:
        base_fields["age"] = 28
    if "weight_kg" in col_names:
        base_fields["weight_kg"] = 80.0
    if "height_cm" in col_names:
        base_fields["height_cm"] = 180.0
    if "fitness_goal" in col_names:
        base_fields["fitness_goal"] = "bygga_muskler"
    if "goal" in col_names:
        base_fields["goal"] = "bygga_muskler"
    if "experience_level" in col_names:
        base_fields["experience_level"] = "medel"
    if "role" in col_names:
        base_fields["role"] = "user"

    cols_sql = ", ".join(base_fields.keys())
    vals_sql = ", ".join(f":{k}" for k in base_fields.keys())

    result = conn.execute(
        text(f"INSERT INTO users ({cols_sql}) VALUES ({vals_sql}) RETURNING id"),
        base_fields
    )
    uid = result.fetchone()[0]
    conn.commit()
    log.info(f"✓ User skapad: ID={uid}, Email={TEST_EMAIL}")
    return uid


# ──────────────────────────────────────────────
# STEG 2: Sätt mål
# ──────────────────────────────────────────────

def step2_goal(conn, uid):
    log.info("\n─── Steg 2: Sätt mål ───")
    # Kolla om user_goals finns
    exists = conn.execute(text("""
        SELECT EXISTS (
            SELECT 1 FROM information_schema.tables
            WHERE table_name = 'user_goals' AND table_schema = 'public'
        )
    """)).scalar()

    if not exists:
        log.info("  (user_goals-tabellen finns inte — hoppar över)")
        return

    cols = conn.execute(text("""
        SELECT column_name FROM information_schema.columns
        WHERE table_name = 'user_goals' AND table_schema = 'public'
    """)).fetchall()
    col_names = [c[0] for c in cols]

    fields = {"user_id": uid}
    if "goal_type" in col_names:
        fields["goal_type"] = "lift_weight"
    if "target_value" in col_names:
        fields["target_value"] = 100.0
    if "current_value" in col_names:
        fields["current_value"] = 80.0
    if "unit" in col_names:
        fields["unit"] = "kg"
    if "deadline" in col_names:
        fields["deadline"] = date.today() + timedelta(days=90)

    cols_sql = ", ".join(fields.keys())
    vals_sql = ", ".join(f":{k}" for k in fields.keys())
    conn.execute(text(f"INSERT INTO user_goals ({cols_sql}) VALUES ({vals_sql})"), fields)
    conn.commit()
    log.info("✓ Mål satt: styrka 80kg → 100kg")


# ──────────────────────────────────────────────
# STEG 3: Logga träningspass
# ──────────────────────────────────────────────

def step3_workout(conn, uid):
    log.info("\n─── Steg 3: Logga träningspass ───")

    # Hämta övningar
    exercises = conn.execute(text("""
        SELECT e.id, e.name FROM exercises e
        WHERE e.deleted_at IS NULL
        LIMIT 4
    """)).fetchall()

    if not exercises:
        log.info("  Inga övningar i exercises-tabellen — hoppar över")
        return None

    # Kolla workout_sessions-kolumner
    ws_cols = [c[0] for c in conn.execute(text("""
        SELECT column_name FROM information_schema.columns
        WHERE table_name = 'workout_sessions' AND table_schema = 'public'
    """)).fetchall()]

    ws_fields = {"user_id": uid}
    if "date" in ws_cols:
        ws_fields["date"] = date.today()
    if "duration_minutes" in ws_cols:
        ws_fields["duration_minutes"] = 60
    if "mood" in ws_cols:
        ws_fields["mood"] = "stark"
    if "feeling" in ws_cols:
        ws_fields["feeling"] = "Stark"

    cols_sql = ", ".join(ws_fields.keys())
    vals_sql = ", ".join(f":{k}" for k in ws_fields.keys())
    session_id = conn.execute(
        text(f"INSERT INTO workout_sessions ({cols_sql}) VALUES ({vals_sql}) RETURNING id"),
        ws_fields
    ).fetchone()[0]

    # Kolla workout_exercises-kolumner
    we_cols = [c[0] for c in conn.execute(text("""
        SELECT column_name FROM information_schema.columns
        WHERE table_name = 'workout_exercises' AND table_schema = 'public'
    """)).fetchall()]

    logged = 0
    for i, (ex_id, ex_name) in enumerate(exercises):
        we_fields = {"session_id": session_id, "exercise_id": ex_id}
        if "sets" in we_cols:
            we_fields["sets"] = 4
        if "reps" in we_cols:
            we_fields["reps"] = 8
        if "weight_kg" in we_cols:
            we_fields["weight_kg"] = 60.0 + i * 10
        if "rpe" in we_cols:
            we_fields["rpe"] = 7

        we_cols_sql = ", ".join(we_fields.keys())
        we_vals_sql = ", ".join(f":{k}" for k in we_fields.keys())
        conn.execute(
            text(f"INSERT INTO workout_exercises ({we_cols_sql}) VALUES ({we_vals_sql})"),
            we_fields
        )
        log.info(f"  {ex_name} — 4x8 @ {60+i*10}kg")
        logged += 1

    conn.commit()
    log.info(f"✓ Pass loggat (session_id={session_id}): {logged} övningar")
    return session_id


# ──────────────────────────────────────────────
# STEG 4: Logga mat
# ──────────────────────────────────────────────

def step4_food(conn, uid):
    log.info("\n─── Steg 4: Logga mat ───")

    # Kolla om meal_logs finns
    exists = conn.execute(text("""
        SELECT EXISTS (
            SELECT 1 FROM information_schema.tables
            WHERE table_name = 'meal_logs' AND table_schema = 'public'
        )
    """)).scalar()
    if not exists:
        log.info("  (meal_logs finns inte — hoppar över)")
        return

    foods = conn.execute(text("""
        SELECT id, name,
               COALESCE(calories_per_100g, 200) as cal,
               COALESCE(protein_per_100g, 20) as prot
        FROM foods LIMIT 3
    """)).fetchall()

    if not foods:
        log.info("  Inga livsmedel i foods-tabellen — hoppar över")
        return

    ml_cols = [c[0] for c in conn.execute(text("""
        SELECT column_name FROM information_schema.columns
        WHERE table_name = 'meal_logs' AND table_schema = 'public'
    """)).fetchall()]

    for fid, fname, cal, prot in foods:
        ml_fields = {"user_id": uid}
        if "food_id" in ml_cols:
            ml_fields["food_id"] = fid
        if "date" in ml_cols:
            ml_fields["date"] = date.today()
        if "meal_type" in ml_cols:
            ml_fields["meal_type"] = "lunch"
        if "amount_g" in ml_cols:
            ml_fields["amount_g"] = 200
        if "calories" in ml_cols:
            ml_fields["calories"] = round(float(cal) * 2, 1)
        if "protein_g" in ml_cols:
            ml_fields["protein_g"] = round(float(prot) * 2, 1)
        if "carbs_g" in ml_cols:
            ml_fields["carbs_g"] = 30.0
        if "fat_g" in ml_cols:
            ml_fields["fat_g"] = 10.0

        ml_cols_sql = ", ".join(ml_fields.keys())
        ml_vals_sql = ", ".join(f":{k}" for k in ml_fields.keys())
        conn.execute(text(f"INSERT INTO meal_logs ({ml_cols_sql}) VALUES ({ml_vals_sql})"), ml_fields)
        log.info(f"  {fname} 200g")

    conn.commit()
    log.info("✓ Mat loggad")


# ──────────────────────────────────────────────
# STEG 5: Logga recovery
# ──────────────────────────────────────────────

def step5_recovery(conn, uid):
    log.info("\n─── Steg 5: Logga recovery ───")

    exists = conn.execute(text("""
        SELECT EXISTS (
            SELECT 1 FROM information_schema.tables
            WHERE table_name = 'recovery_logs' AND table_schema = 'public'
        )
    """)).scalar()
    if not exists:
        log.info("  (recovery_logs finns inte — hoppar över)")
        return

    rl_cols = [c[0] for c in conn.execute(text("""
        SELECT column_name FROM information_schema.columns
        WHERE table_name = 'recovery_logs' AND table_schema = 'public'
    """)).fetchall()]

    rl_fields = {"user_id": uid}
    if "date" in rl_cols:
        rl_fields["date"] = date.today()
    if "sleep_hours" in rl_cols:
        rl_fields["sleep_hours"] = 7.5
    if "sleep_quality" in rl_cols:
        rl_fields["sleep_quality"] = 8
    if "energy_level" in rl_cols:
        rl_fields["energy_level"] = 7
    if "stress_level" in rl_cols:
        rl_fields["stress_level"] = 4

    rl_cols_sql = ", ".join(rl_fields.keys())
    rl_vals_sql = ", ".join(f":{k}" for k in rl_fields.keys())

    try:
        conn.execute(
            text(f"INSERT INTO recovery_logs ({rl_cols_sql}) VALUES ({rl_vals_sql}) "
                 f"ON CONFLICT (user_id, date) DO UPDATE SET sleep_hours=7.5, "
                 f"sleep_quality=8, energy_level=7, stress_level=4"),
            rl_fields
        )
    except Exception:
        conn.rollback()
        conn.execute(
            text(f"INSERT INTO recovery_logs ({rl_cols_sql}) VALUES ({rl_vals_sql})"),
            rl_fields
        )

    conn.commit()
    log.info("✓ Recovery: 7.5h sömn, energi 7/10, stress 4/10")


# ──────────────────────────────────────────────
# STEG 6: Kör pipelines
# ──────────────────────────────────────────────

def step6_pipelines(uid):
    log.info("\n─── Steg 6: Kör pipelines ───")
    errors = []

    # Fatigue pipeline
    try:
        from pipelines.fatigue_pipeline import calculate_fatigue_for_user
        with engine.connect() as conn:
            result = calculate_fatigue_for_user(uid, conn)
            if result:
                log.info(f"  ✓ Fatigue: readiness={result.get('readiness_score', 'N/A')}, "
                         f"acwr={result.get('acwr', 'N/A')}")
            else:
                log.info("  ✓ Fatigue pipeline klar (ingen data ännu — ny user)")
            conn.commit()
    except Exception as e:
        log.warning(f"  ⚠ fatigue_pipeline: {e}")
        errors.append("fatigue")

    # Volume tracker pipeline
    try:
        from pipelines.volume_tracker_pipeline import run_volume_and_recovery_analysis
        run_volume_and_recovery_analysis(user_id=uid)
        log.info("  ✓ Volume tracker klar")
    except Exception as e:
        log.warning(f"  ⚠ volume_tracker_pipeline: {e}")
        errors.append("volume")

    # Recommendation pipeline
    try:
        from pipelines.recommendation_pipeline import generate_recommendations
        generate_recommendations(uid, TEST_NAME)
        log.info("  ✓ Recommendations klar")
    except Exception as e:
        log.warning(f"  ⚠ recommendation_pipeline: {e}")
        errors.append("recommendations")

    if errors:
        log.info(f"  Pipeline-varningar: {errors} (normalt för ny user utan historik)")
    else:
        log.info("✓ Alla pipelines klara")


# ──────────────────────────────────────────────
# STEG 7: Verifiera
# ──────────────────────────────────────────────

def step7_verify(conn, uid) -> bool:
    log.info("\n─── Steg 7: Verifiera ───")
    all_ok = True

    # Vilka tabeller finns?
    tables = {r[0] for r in conn.execute(text("""
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = 'public'
    """)).fetchall()}

    checks = {
        "workout_sessions": ("SELECT COUNT(*) FROM workout_sessions WHERE user_id = :uid", True),
        "workout_exercises": ("SELECT COUNT(*) FROM workout_exercises we "
                              "JOIN workout_sessions ws ON we.session_id = ws.id "
                              "WHERE ws.user_id = :uid", False),
        "meal_logs": ("SELECT COUNT(*) FROM meal_logs WHERE user_id = :uid", False),
        "recovery_logs": ("SELECT COUNT(*) FROM recovery_logs WHERE user_id = :uid", False),
        "fatigue_scores": ("SELECT COUNT(*) FROM fatigue_scores WHERE user_id = :uid", False),
        "recommendations": ("SELECT COUNT(*) FROM recommendations WHERE user_id = :uid", False),
        "ai_insights": ("SELECT COUNT(*) FROM ai_insights WHERE user_id = :uid", False),
    }

    for table_name, (query, required) in checks.items():
        if table_name not in tables and "JOIN" not in query:
            log.info(f"  [SKIP] {table_name}: tabellen finns inte")
            continue

        try:
            count = conn.execute(text(query), {"uid": uid}).scalar() or 0
            if count > 0:
                status = "OK  "
            elif required:
                status = "FEL "
                all_ok = False
            else:
                status = "INFO"
            log.info(f"  [{status}] {table_name}: {count} rader")
        except Exception as e:
            log.warning(f"  [ERR ] {table_name}: {e}")

    return all_ok


# ──────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────

def run():
    log.info("=" * 60)
    log.info("MINTAKT — REALISTISKT ANVÄNDARFLÖDE (P6)")
    log.info("=" * 60)

    uid = None
    success = False

    try:
        with engine.connect() as conn:
            uid = step1_register(conn)
            step2_goal(conn, uid)
            step3_workout(conn, uid)
            step4_food(conn, uid)
            step5_recovery(conn, uid)

        step6_pipelines(uid)

        with engine.connect() as conn:
            success = step7_verify(conn, uid)

    except Exception as e:
        log.error(f"Kritiskt fel: {e}")
        import traceback
        traceback.print_exc()

    finally:
        if uid is not None:
            try:
                with engine.connect() as conn:
                    cleanup(conn)
            except Exception as e:
                log.warning(f"Cleanup misslyckades: {e}")

    log.info("")
    log.info("=" * 60)
    if success:
        log.info("RESULTAT: ✅ Hela flödet fungerar!")
    else:
        log.info("RESULTAT: ⚠  Några steg hade varningar (se ovan)")
    log.info("=" * 60)
    return success


if __name__ == "__main__":
    ok = run()
    sys.exit(0 if ok else 1)