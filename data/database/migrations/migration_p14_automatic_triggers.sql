-- ============================================================
-- migration_p14_automatic_triggers.sql
-- Automatiska triggers för audit_log och exercise_versions
-- Svarar på code review-frågor:
-- 1. users saknade updated_at trigger — fixat
-- 2. audit_log fylls nu via trigger (inte bara API)
-- 3. exercise_versions skapas automatiskt vid UPDATE
-- ============================================================

-- ── 1. updated_at på users ────────────────────────────────────
DO $$ BEGIN
  CREATE TRIGGER trg_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- ── 2. Automatisk audit trigger för DELETE ────────────────────
-- Loggar automatiskt när kritiska rader raderas
-- Ingen utvecklare kan glömma att logga DELETE
CREATE OR REPLACE FUNCTION log_delete_to_audit()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO audit_log (table_name, action, record_id, old_value, changed_at)
  VALUES (TG_TABLE_NAME, 'DELETE', OLD.id, row_to_json(OLD)::jsonb, NOW());
  RETURN OLD;
END;
$$ LANGUAGE plpgsql;

DO $$ BEGIN
  CREATE TRIGGER trg_audit_users_delete
    BEFORE DELETE ON users
    FOR EACH ROW EXECUTE FUNCTION log_delete_to_audit();
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TRIGGER trg_audit_exercises_delete
    BEFORE DELETE ON exercises
    FOR EACH ROW EXECUTE FUNCTION log_delete_to_audit();
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TRIGGER trg_audit_workout_sessions_delete
    BEFORE DELETE ON workout_sessions
    FOR EACH ROW EXECUTE FUNCTION log_delete_to_audit();
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- ── 3. Automatisk exercise_versions vid UPDATE ────────────────
-- Spårar ändringar i instructions, tips och common_mistakes
-- Versionerna skapas automatiskt — ingen kan glömma
CREATE OR REPLACE FUNCTION log_exercise_version()
RETURNS TRIGGER AS $$
BEGIN
  IF OLD.instructions IS DISTINCT FROM NEW.instructions THEN
    INSERT INTO exercise_versions (exercise_id, field_name, old_value, new_value, reason)
    VALUES (OLD.id, 'instructions', OLD.instructions, NEW.instructions, 'auto');
  END IF;
  IF OLD.tips IS DISTINCT FROM NEW.tips THEN
    INSERT INTO exercise_versions (exercise_id, field_name, old_value, new_value, reason)
    VALUES (OLD.id, 'tips', OLD.tips, NEW.tips, 'auto');
  END IF;
  IF OLD.common_mistakes IS DISTINCT FROM NEW.common_mistakes THEN
    INSERT INTO exercise_versions (exercise_id, field_name, old_value, new_value, reason)
    VALUES (OLD.id, 'common_mistakes', OLD.common_mistakes, NEW.common_mistakes, 'auto');
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DO $$ BEGIN
  CREATE TRIGGER trg_exercise_versions
    AFTER UPDATE ON exercises
    FOR EACH ROW EXECUTE FUNCTION log_exercise_version();
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- ── Trigger-lista (för dokumentation) ────────────────────────
-- ✓ users             — updated_at, audit DELETE
-- ✓ exercises         — updated_at, audit DELETE, exercise_versions
-- ✓ foods             — updated_at
-- ✓ gyms              — updated_at
-- ✓ equipment         — updated_at
-- ✓ recovery_logs     — updated_at
-- ✓ workout_sessions  — updated_at, audit DELETE
-- ✓ workout_exercises — updated_at
-- ✓ personal_records  — updated_at

SELECT event_object_table AS tabell, trigger_name
FROM information_schema.triggers
WHERE trigger_schema = 'public'
AND trigger_name LIKE 'trg_%'
ORDER BY event_object_table;