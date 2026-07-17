-- ============================================================
-- migration_p11_workout_robustness.sql
-- NOT NULL, DEFAULT values och updated_at triggers för
-- workout_sessions, workout_exercises, personal_records
-- Koordinerat med Hamze Iteration 2 (EF-mappningar)
-- ============================================================

-- ── workout_sessions ─────────────────────────────────────────
ALTER TABLE workout_sessions
  ALTER COLUMN user_id SET NOT NULL,
  ALTER COLUMN date    SET NOT NULL,
  ALTER COLUMN date    SET DEFAULT CURRENT_DATE;

-- ── workout_exercises ─────────────────────────────────────────
ALTER TABLE workout_exercises
  ALTER COLUMN session_id  SET NOT NULL,
  ALTER COLUMN exercise_id SET NOT NULL,
  ALTER COLUMN sets        SET NOT NULL,
  ALTER COLUMN sets        SET DEFAULT 1,
  ALTER COLUMN reps        SET NOT NULL,
  ALTER COLUMN reps        SET DEFAULT 1,
  ALTER COLUMN weight_kg   SET DEFAULT 0;

-- ── personal_records ─────────────────────────────────────────
ALTER TABLE personal_records
  ALTER COLUMN user_id     SET NOT NULL,
  ALTER COLUMN exercise_id SET NOT NULL,
  ALTER COLUMN date        SET NOT NULL,
  ALTER COLUMN date        SET DEFAULT CURRENT_DATE,
  ALTER COLUMN weight_kg   SET DEFAULT 0,
  ALTER COLUMN reps        SET DEFAULT 1;

-- ── updated_at triggers ───────────────────────────────────────
DO $$ BEGIN
  CREATE TRIGGER trg_workout_sessions_updated_at
    BEFORE UPDATE ON workout_sessions
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TRIGGER trg_workout_exercises_updated_at
    BEFORE UPDATE ON workout_exercises
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TRIGGER trg_personal_records_updated_at
    BEFORE UPDATE ON personal_records
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- Verifiera
SELECT trigger_name, event_object_table
FROM information_schema.triggers
WHERE trigger_schema = 'public'
AND trigger_name LIKE 'trg_%'
ORDER BY event_object_table;