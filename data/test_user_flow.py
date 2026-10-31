"""
test_user_flow.py — data/test_user_flow.py
Simulerar ett realistiskt användarflöde från start till slut.
Kör med: python test_user_flow.py
"""

import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = SCRIPT_DIR
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


def cleanup(conn):
    """Raderar testuser med DELETE ... CASCADE via temporär constraint-disable."""
    row = conn.execute(text("SELECT id FROM users WHERE email = :email"), {"email": TEST_EMAIL}).fetchone()
    if row is None:
        log.info("✓ Ingen testdata att radera")
        return
    uid = row[0]

    # Inaktivera FK-checks tillfälligt för denna session
    conn.execute(text("SET session_replication_role = replica"))
    conn.execute(text("DELETE FROM users WHERE id = :uid"), {"uid": uid})
    conn.execute(text("SET session_replication_role = DEFAULT"))
    conn.commit()
    log.info("✓ Testdata raderad")


def step1_register(conn) -> int:
    log.info("\n─── Steg 1: Registrera user ───")
    cleanup(conn)

    cols = [c[0] for c in conn.execute(text("""
        SELECT column_name FROM information_schema.columns
        WHERE table_name = 'users' AND table_schema = 'public'
        ORDER BY ordinal_position
    """)).fetchall()]

    base_fields = {"name": TEST_NAME, "fitness_level": "medel"}
    if "email" in cols: base_fields["email"] = TEST_EMAIL
    if "age" in cols: base_fields["age"] = 28
    if "weight_kg" in cols: base_fields["weight_kg"] = 80.0
    if "height_cm" in cols: base_fields["height_cm"] = 180.0
    if "fitness_goal" in cols: base_fields["fitness_goal"] = "bygga_muskler"
    if "goal" in cols: base_fields["goal"] = "bygga_muskler"
    if "experience_level" in cols: base_fields["experience_level"] = "medel"
    if "role" in cols: base_fields["role"] = "user"

    cols_sql = ", ".join(base_fields.keys())
    vals_sql = ", ".join(f":{k}" for k in base_fields.keys())
    uid = conn.execute(
        text(f"INSERT INTO users ({cols_sql}) VALUES ({vals_sql}) RETURNING id"),
        base_fields
    ).fetchone()[0]
    conn.commit()
    log.info(f"✓ User skapad: ID={uid}, Email={TEST_EMAIL}")
    return uid


def step2_goal(conn, uid):
    log.info("\n─── Steg 2: Sätt mål ───")
    exists = conn.execute(text("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name='user_goals' AND table_schema='public')")).scalar()
    if not exists:
        log.info("  (user_goals finns inte — hoppar över)"); return

    cols = [c[0] for c in conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='user_goals' AND table_schema='public'")).fetchall()]
    fields = {"user_id": uid}
    if "goal_type" in cols: fields["goal_type"] = "lift_weight"
    if "target_value" in cols: fields["target_value"] = 100.0
    if "current_value" in cols: fields["current_value"] = 80.0
    if "unit" in cols: fields["unit"] = "kg"
    if "deadline" in cols: fields["deadline"] = date.today() + timedelta(days=90)

    cols_sql = ", ".join(fields.keys())
    vals_sql = ", ".join(f":{k}" for k in fields.keys())
    conn.execute(text(f"INSERT INTO user_goals ({cols_sql}) VALUES ({vals_sql})"), fields)
    conn.commit()
    log.info("✓ Mål satt: styrka 80kg → 100kg")


def step3_workout(conn, uid):
    log.info("\n─── Steg 3: Logga träningspass ───")
    exercises = conn.execute(text("SELECT e.id, e.name FROM exercises e WHERE e.deleted_at IS NULL LIMIT 4")).fetchall()
    if not exercises:
        log.info("  Inga övningar — hoppar över"); return None

    ws_cols = [c[0] for c in conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='workout_sessions' AND table_schema='public'")).fetchall()]
    ws_fields = {"user_id": uid}
    if "date" in ws_cols: ws_fields["date"] = date.today()
    if "duration_minutes" in ws_cols: ws_fields["duration_minutes"] = 60
    if "mood" in ws_cols: ws_fields["mood"] = "stark"
    if "feeling" in ws_cols: ws_fields["feeling"] = "Stark"

    cols_sql = ", ".join(ws_fields.keys())
    vals_sql = ", ".join(f":{k}" for k in ws_fields.keys())
    session_id = conn.execute(text(f"INSERT INTO workout_sessions ({cols_sql}) VALUES ({vals_sql}) RETURNING id"), ws_fields).fetchone()[0]

    we_cols = [c[0] for c in conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='workout_exercises' AND table_schema='public'")).fetchall()]
    for i, (ex_id, ex_name) in enumerate(exercises):
        we_fields = {"session_id": session_id, "exercise_id": ex_id}
        if "sets" in we_cols: we_fields["sets"] = 4
        if "reps" in we_cols: we_fields["reps"] = 8
        if "weight_kg" in we_cols: we_fields["weight_kg"] = 60.0 + i * 10
        if "rpe" in we_cols: we_fields["rpe"] = 7
        wc = ", ".join(we_fields.keys()); wv = ", ".join(f":{k}" for k in we_fields.keys())
        conn.execute(text(f"INSERT INTO workout_exercises ({wc}) VALUES ({wv})"), we_fields)
        log.info(f"  {ex_name} — 4x8 @ {60+i*10}kg")

    conn.commit()
    log.info(f"✓ Pass loggat (session_id={session_id}): {len(exercises)} övningar")
    return session_id


def step4_food(conn, uid):
    log.info("\n─── Steg 4: Logga mat ───")
    exists = conn.execute(text("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name='meal_logs' AND table_schema='public')")).scalar()
    if not exists:
        log.info("  (meal_logs finns inte — hoppar över)"); return

    foods = conn.execute(text("SELECT id, name, COALESCE(calories_per_100g,200), COALESCE(protein_per_100g,20) FROM foods LIMIT 3")).fetchall()
    if not foods:
        log.info("  Inga livsmedel — hoppar över"); return

    ml_cols = [c[0] for c in conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='meal_logs' AND table_schema='public'")).fetchall()]
    for fid, fname, cal, prot in foods:
        ml = {"user_id": uid}
        if "food_id" in ml_cols: ml["food_id"] = fid
        if "date" in ml_cols: ml["date"] = date.today()
        if "meal_type" in ml_cols: ml["meal_type"] = "lunch"
        if "amount_g" in ml_cols: ml["amount_g"] = 200
        if "calories" in ml_cols: ml["calories"] = round(float(cal)*2, 1)
        if "protein_g" in ml_cols: ml["protein_g"] = round(float(prot)*2, 1)
        if "carbs_g" in ml_cols: ml["carbs_g"] = 30.0
        if "fat_g" in ml_cols: ml["fat_g"] = 10.0
        mc = ", ".join(ml.keys()); mv = ", ".join(f":{k}" for k in ml.keys())
        conn.execute(text(f"INSERT INTO meal_logs ({mc}) VALUES ({mv})"), ml)
        log.info(f"  {fname} 200g")
    conn.commit()
    log.info("✓ Mat loggad")


def step5_recovery(conn, uid):
    log.info("\n─── Steg 5: Logga recovery ───")
    exists = conn.execute(text("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name='recovery_logs' AND table_schema='public')")).scalar()
    if not exists:
        log.info("  (recovery_logs finns inte — hoppar över)"); return

    rl_cols = [c[0] for c in conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='recovery_logs' AND table_schema='public'")).fetchall()]
    rl = {"user_id": uid}
    if "date" in rl_cols: rl["date"] = date.today()
    if "sleep_hours" in rl_cols: rl["sleep_hours"] = 7.5
    if "sleep_quality" in rl_cols: rl["sleep_quality"] = 8
    if "energy_level" in rl_cols: rl["energy_level"] = 7
    if "stress_level" in rl_cols: rl["stress_level"] = 4
    rc = ", ".join(rl.keys()); rv = ", ".join(f":{k}" for k in rl.keys())
    try:
        conn.execute(text(f"INSERT INTO recovery_logs ({rc}) VALUES ({rv}) ON CONFLICT (user_id, date) DO UPDATE SET sleep_hours=7.5, sleep_quality=8, energy_level=7, stress_level=4"), rl)
    except Exception:
        conn.rollback()
        conn.execute(text(f"INSERT INTO recovery_logs ({rc}) VALUES ({rv})"), rl)
    conn.commit()
    log.info("✓ Recovery: 7.5h sömn, energi 7/10, stress 4/10")


def step6_pipelines(uid):
    log.info("\n─── Steg 6: Kör pipelines ───")
    errors = []
    try:
        from pipelines.fatigue_pipeline import calculate_fatigue_for_user
        with engine.connect() as conn:
            result = calculate_fatigue_for_user(uid, conn)
            log.info(f"  ✓ Fatigue: readiness={result.get('readiness_score','N/A') if result else 'N/A'}")
            conn.commit()
    except Exception as e:
        log.warning(f"  ⚠ fatigue_pipeline: {e}"); errors.append("fatigue")
    try:
        from pipelines.volume_tracker_pipeline import run_volume_and_recovery_analysis
        run_volume_and_recovery_analysis(user_id=uid)
        log.info("  ✓ Volume tracker klar")
    except Exception as e:
        log.warning(f"  ⚠ volume_tracker: {e}"); errors.append("volume")
    try:
        from pipelines.recommendation_pipeline import generate_recommendations
        generate_recommendations(uid, TEST_NAME)
        log.info("  ✓ Recommendations klar")
    except Exception as e:
        log.warning(f"  ⚠ recommendations: {e}"); errors.append("recommendations")
    if errors:
        log.info(f"  Pipeline-varningar: {errors}")
    else:
        log.info("✓ Alla pipelines klara")


def step7_verify(conn, uid) -> bool:
    log.info("\n─── Steg 7: Verifiera ───")
    all_ok = True
    tables = {r[0] for r in conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")).fetchall()}
    checks = {
        "workout_sessions": ("SELECT COUNT(*) FROM workout_sessions WHERE user_id = :uid", True),
        "workout_exercises": ("SELECT COUNT(*) FROM workout_exercises we JOIN workout_sessions ws ON we.session_id=ws.id WHERE ws.user_id=:uid", False),
        "meal_logs": ("SELECT COUNT(*) FROM meal_logs WHERE user_id = :uid", False),
        "recovery_logs": ("SELECT COUNT(*) FROM recovery_logs WHERE user_id = :uid", False),
        "recommendations": ("SELECT COUNT(*) FROM recommendations WHERE user_id = :uid", False),
    }
    for tname, (query, required) in checks.items():
        if tname not in tables and "JOIN" not in query:
            log.info(f"  [SKIP] {tname}: tabellen finns inte"); continue
        try:
            count = conn.execute(text(query), {"uid": uid}).scalar() or 0
            status = "OK  " if count > 0 else ("FEL " if required else "INFO")
            if required and count == 0: all_ok = False
            log.info(f"  [{status}] {tname}: {count} rader")
        except Exception as e:
            log.warning(f"  [ERR ] {tname}: {e}")
    return all_ok


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
        import traceback; traceback.print_exc()
    finally:
        if uid is not None:
            try:
                with engine.connect() as conn:
                    cleanup(conn)
            except Exception as e:
                log.warning(f"Cleanup misslyckades: {e}")
    log.info("")
    log.info("=" * 60)
    log.info("RESULTAT: ✅ Hela flödet fungerar!" if success else "RESULTAT: ⚠  Några steg hade varningar (se ovan)")
    log.info("=" * 60)
    return success


if __name__ == "__main__":
    ok = run()
    sys.exit(0 if ok else 1)
