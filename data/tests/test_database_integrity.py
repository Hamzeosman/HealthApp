"""
tests/test_database_integrity.py
Databasintegrationstester för:
- CHECK constraints
- UNIQUE constraints
- updated_at triggers
- ON DELETE CASCADE
- NOT NULL constraints
- History tables
"""
import pytest
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"))


# ── Helpers ───────────────────────────────────────────────────

def get_test_user_id():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT id FROM users LIMIT 1"))
        row = result.fetchone()
        assert row, "Ingen user finns — kör seed_test_data.py först"
        return row[0]


# ── CHECK constraints ─────────────────────────────────────────

def test_check_constraint_rpe_too_high():
    """RPE > 10 ska ge constraint-fel."""
    with engine.connect() as conn:
        with pytest.raises(Exception, match="chk_we_rpe|violates check constraint"):
            conn.execute(text("""
                INSERT INTO workout_exercises (session_id, exercise_id, sets, reps, rpe)
                SELECT ws.id, 1, 3, 10, 11
                FROM workout_sessions ws LIMIT 1
            """))
            conn.commit()


def test_check_constraint_rpe_too_low():
    """RPE < 1 ska ge constraint-fel."""
    with engine.connect() as conn:
        with pytest.raises(Exception, match="chk_we_rpe|violates check constraint"):
            conn.execute(text("""
                INSERT INTO workout_exercises (session_id, exercise_id, sets, reps, rpe)
                SELECT ws.id, 1, 3, 10, 0
                FROM workout_sessions ws LIMIT 1
            """))
            conn.commit()


def test_check_constraint_sets_too_high():
    """Sets > 20 ska ge constraint-fel."""
    with engine.connect() as conn:
        with pytest.raises(Exception, match="chk_we_sets|violates check constraint"):
            conn.execute(text("""
                INSERT INTO workout_exercises (session_id, exercise_id, sets, reps)
                SELECT ws.id, 1, 21, 10
                FROM workout_sessions ws LIMIT 1
            """))
            conn.commit()


def test_check_constraint_weight_negative():
    """Negativ vikt ska ge constraint-fel."""
    with engine.connect() as conn:
        with pytest.raises(Exception, match="chk_we_weight|violates check constraint"):
            conn.execute(text("""
                INSERT INTO workout_exercises (session_id, exercise_id, sets, reps, weight_kg)
                SELECT ws.id, 1, 3, 10, -5
                FROM workout_sessions ws LIMIT 1
            """))
            conn.commit()


def test_check_constraint_sleep_too_high():
    """Sömn > 16 timmar ska ge constraint-fel."""
    uid = get_test_user_id()
    with engine.connect() as conn:
        with pytest.raises(Exception, match="chk_recovery_sleep|violates check constraint"):
            conn.execute(text("""
                INSERT INTO recovery_logs (user_id, date, sleep_hours, energy_level, stress_level)
                VALUES (:uid, '2099-01-01', 25, 7, 5)
            """), {"uid": uid})
            conn.commit()


def test_check_constraint_energy_out_of_range():
    """Energy level > 10 ska ge constraint-fel."""
    uid = get_test_user_id()
    with engine.connect() as conn:
        with pytest.raises(Exception, match="chk_recovery_energy|violates check constraint"):
            conn.execute(text("""
                INSERT INTO recovery_logs (user_id, date, sleep_hours, energy_level, stress_level)
                VALUES (:uid, '2099-01-02', 7, 11, 5)
            """), {"uid": uid})
            conn.commit()


def test_check_constraint_food_calories_negative():
    """Negativa kalorier i foods ska ge constraint-fel."""
    with engine.connect() as conn:
        with pytest.raises(Exception, match="chk_foods_calories|violates check constraint"):
            conn.execute(text("""
                INSERT INTO foods (name, calories_per_100g, protein_per_100g, carbs_per_100g, fat_per_100g)
                VALUES ('test_food_bad', -10, 0, 0, 0)
            """))
            conn.commit()


# ── UNIQUE constraints ────────────────────────────────────────

def test_unique_recovery_logs_user_date():
    """Två recovery_logs för samma user och datum ska ge fel."""
    uid = get_test_user_id()
    with engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO recovery_logs (user_id, date, sleep_hours, energy_level, stress_level)
            VALUES (:uid, '2099-06-01', 7, 7, 5)
            ON CONFLICT (user_id, date) DO NOTHING
        """), {"uid": uid})
        conn.commit()

        with pytest.raises(Exception, match="unique|duplicate"):
            conn.execute(text("""
                INSERT INTO recovery_logs (user_id, date, sleep_hours, energy_level, stress_level)
                VALUES (:uid, '2099-06-01', 8, 8, 4)
            """), {"uid": uid})
            conn.commit()

    # Cleanup
    with engine.connect() as conn:
        conn.execute(text(
            "DELETE FROM recovery_logs WHERE user_id = :uid AND date = '2099-06-01'"
        ), {"uid": uid})
        conn.commit()


def test_unique_foods_name():
    """Två foods med samma namn ska ge fel."""
    with engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO foods (name, calories_per_100g, protein_per_100g, carbs_per_100g, fat_per_100g)
            VALUES ('test_unique_food_xyz', 100, 10, 10, 5)
            ON CONFLICT (name) DO NOTHING
        """))
        conn.commit()

        with pytest.raises(Exception, match="unique|duplicate"):
            conn.execute(text("""
                INSERT INTO foods (name, calories_per_100g, protein_per_100g, carbs_per_100g, fat_per_100g)
                VALUES ('test_unique_food_xyz', 200, 20, 20, 10)
            """))
            conn.commit()

    # Cleanup
    with engine.connect() as conn:
        conn.execute(text("DELETE FROM foods WHERE name = 'test_unique_food_xyz'"))
        conn.commit()


# ── NOT NULL constraints ──────────────────────────────────────

def test_not_null_food_name():
    """Food utan namn ska ge fel."""
    with engine.connect() as conn:
        with pytest.raises(Exception, match="null value|not-null|violates not-null"):
            conn.execute(text("""
                INSERT INTO foods (calories_per_100g, protein_per_100g, carbs_per_100g, fat_per_100g)
                VALUES (100, 10, 10, 5)
            """))
            conn.commit()


def test_not_null_exercise_name():
    """Exercise utan namn ska ge fel."""
    with engine.connect() as conn:
        with pytest.raises(Exception, match="null value|not-null|violates not-null"):
            conn.execute(text("""
                INSERT INTO exercises (difficulty, exercise_type)
                VALUES ('medel', 'styrka')
            """))
            conn.commit()


def test_not_null_recovery_log_user_id():
    """Recovery log utan user_id ska ge fel."""
    with engine.connect() as conn:
        with pytest.raises(Exception, match="null value|not-null|violates not-null"):
            conn.execute(text("""
                INSERT INTO recovery_logs (date, sleep_hours, energy_level, stress_level)
                VALUES (CURRENT_DATE, 7, 7, 5)
            """))
            conn.commit()


# ── updated_at TRIGGER ────────────────────────────────────────

def test_updated_at_trigger_exercises():
    """updated_at ska uppdateras automatiskt vid UPDATE."""
    with engine.connect() as conn:
        result = conn.execute(text(
            "SELECT id, updated_at FROM exercises WHERE name = 'Bänkpress' LIMIT 1"
        ))
        row = result.fetchone()
        if not row:
            pytest.skip("Bänkpress finns inte i databasen")

        exercise_id, old_updated_at = row[0], row[1]

        conn.execute(text("""
            UPDATE exercises SET tips = 'Håll skulderbladen indragna'
            WHERE id = :id
        """), {"id": exercise_id})
        conn.commit()

        result = conn.execute(text(
            "SELECT updated_at FROM exercises WHERE id = :id"
        ), {"id": exercise_id})
        new_updated_at = result.fetchone()[0]

        assert new_updated_at >= old_updated_at


# ── ON DELETE CASCADE ─────────────────────────────────────────

def test_on_delete_cascade_recovery_logs():
    """När en user tas bort ska recovery_logs kaskadraderas."""
    with engine.connect() as conn:
        result = conn.execute(text("""
            INSERT INTO users (name, email, fitness_level, fitness_goal)
            VALUES ('Test Delete User', 'delete_test_cascade@test.local', 'medel', 'bygga_muskler')
            RETURNING id
        """))
        test_uid = result.fetchone()[0]

        conn.execute(text("""
            INSERT INTO recovery_logs (user_id, date, sleep_hours, energy_level, stress_level)
            VALUES (:uid, '2099-12-01', 7, 7, 5)
        """), {"uid": test_uid})
        conn.commit()

        count_before = conn.execute(text(
            "SELECT COUNT(*) FROM recovery_logs WHERE user_id = :uid"
        ), {"uid": test_uid}).fetchone()[0]
        assert count_before == 1

        conn.execute(text("DELETE FROM users WHERE id = :uid"), {"uid": test_uid})
        conn.commit()

        count_after = conn.execute(text(
            "SELECT COUNT(*) FROM recovery_logs WHERE user_id = :uid"
        ), {"uid": test_uid}).fetchone()[0]
        assert count_after == 0


# ── Historik-tabeller ─────────────────────────────────────────

def test_history_tables_exist():
    """weight_history, goal_history, program_history ska finnas."""
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name IN ('weight_history', 'goal_history', 'program_history',
                               'audit_log', 'exercise_versions')
        """))
        tables = [row[0] for row in result]
        assert 'weight_history'  in tables
        assert 'goal_history'    in tables
        assert 'program_history' in tables
        assert 'audit_log'       in tables
        assert 'exercise_versions' in tables


def test_weight_history_constraint():
    """Vikt under 20kg ska ge constraint-fel."""
    uid = get_test_user_id()
    with engine.connect() as conn:
        with pytest.raises(Exception, match="violates check constraint"):
            conn.execute(text("""
                INSERT INTO weight_history (user_id, weight_kg, measured_at)
                VALUES (:uid, 5, CURRENT_DATE)
            """), {"uid": uid})
            conn.commit()


# ── Master data integritet ────────────────────────────────────

def test_master_data_exercises_count():
    """Ska finnas minst 100 övningar."""
    with engine.connect() as conn:
        count = conn.execute(text(
            "SELECT COUNT(*) FROM exercises WHERE deleted_at IS NULL"
        )).fetchone()[0]
        assert count >= 100, f"Bara {count} övningar — förväntar minst 100"


def test_master_data_foods_count():
    """Ska finnas minst 50 livsmedel."""
    with engine.connect() as conn:
        count = conn.execute(text("SELECT COUNT(*) FROM foods")).fetchone()[0]
        assert count >= 50, f"Bara {count} livsmedel — förväntar minst 50"


def test_master_data_exercises_have_primary_muscle():
    """Alla övningar ska ha primary_muscle satt."""
    with engine.connect() as conn:
        missing = conn.execute(text("""
            SELECT COUNT(*) FROM exercises
            WHERE primary_muscle IS NULL AND deleted_at IS NULL
        """)).fetchone()[0]
        assert missing == 0, f"{missing} övningar saknar primary_muscle"


def test_master_data_foods_have_macros():
    """Alla livsmedel ska ha calories satt."""
    with engine.connect() as conn:
        missing = conn.execute(text("""
            SELECT COUNT(*) FROM foods WHERE calories_per_100g IS NULL
        """)).fetchone()[0]
        assert missing == 0, f"{missing} livsmedel saknar kalorier"