-- ============================================================
-- migration_p7_robustness.sql
-- NOT NULL på kritiska kolumner, DEFAULT values, updated_at trigger
-- Rör INTE: workout_sessions, workout_exercises, personal_records
-- (Hamze jobbar på dessa i Iteration 2)
-- ============================================================

-- ── 1. UPDATED_AT TRIGGER ────────────────────────────────────
-- En funktion som uppdaterar updated_at automatiskt
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Lägg till updated_at på tabeller som saknar det
ALTER TABLE exercises
  ALTER COLUMN updated_at SET DEFAULT NOW();

ALTER TABLE foods
  ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT NOW();

ALTER TABLE gyms
  ALTER COLUMN updated_at SET DEFAULT NOW();

ALTER TABLE equipment
  ALTER COLUMN updated_at SET DEFAULT NOW();

-- Triggers för updated_at
DO $$ BEGIN
  CREATE TRIGGER trg_exercises_updated_at
    BEFORE UPDATE ON exercises
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TRIGGER trg_foods_updated_at
    BEFORE UPDATE ON foods
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TRIGGER trg_gyms_updated_at
    BEFORE UPDATE ON gyms
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TRIGGER trg_equipment_updated_at
    BEFORE UPDATE ON equipment
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TRIGGER trg_recovery_logs_updated_at
    BEFORE UPDATE ON recovery_logs
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- ── 2. NOT NULL + DEFAULT på kritiska kolumner ────────────────

-- foods — makronäringsdata ska alltid finnas
ALTER TABLE foods
  ALTER COLUMN name SET NOT NULL,
  ALTER COLUMN calories_per_100g SET NOT NULL,
  ALTER COLUMN calories_per_100g SET DEFAULT 0,
  ALTER COLUMN protein_per_100g  SET NOT NULL,
  ALTER COLUMN protein_per_100g  SET DEFAULT 0,
  ALTER COLUMN carbs_per_100g    SET NOT NULL,
  ALTER COLUMN carbs_per_100g    SET DEFAULT 0,
  ALTER COLUMN fat_per_100g      SET NOT NULL,
  ALTER COLUMN fat_per_100g      SET DEFAULT 0;

-- exercises — kritiska fält
ALTER TABLE exercises
  ALTER COLUMN name SET NOT NULL;

-- gyms — namn krävs
ALTER TABLE gyms
  ALTER COLUMN name SET NOT NULL,
  ALTER COLUMN country SET DEFAULT 'Sweden';

-- equipment — namn krävs
ALTER TABLE equipment
  ALTER COLUMN name SET NOT NULL;

-- recovery_logs — user_id och date krävs alltid
ALTER TABLE recovery_logs
  ALTER COLUMN user_id SET NOT NULL,
  ALTER COLUMN date    SET NOT NULL,
  ALTER COLUMN date    SET DEFAULT CURRENT_DATE;

-- meal_logs — kritiska fält
ALTER TABLE meal_logs
  ALTER COLUMN user_id   SET NOT NULL,
  ALTER COLUMN date      SET NOT NULL,
  ALTER COLUMN date      SET DEFAULT CURRENT_DATE,
  ALTER COLUMN meal_type SET NOT NULL,
  ALTER COLUMN amount_g  SET NOT NULL,
  ALTER COLUMN amount_g  SET DEFAULT 0,
  ALTER COLUMN calories  SET DEFAULT 0,
  ALTER COLUMN protein_g SET DEFAULT 0,
  ALTER COLUMN carbs_g   SET DEFAULT 0,
  ALTER COLUMN fat_g     SET DEFAULT 0;

-- running_sessions — user_id och date krävs
ALTER TABLE running_sessions
  ALTER COLUMN user_id  SET NOT NULL,
  ALTER COLUMN date     SET NOT NULL,
  ALTER COLUMN date     SET DEFAULT CURRENT_DATE;

-- biometrics — user_id och date krävs
ALTER TABLE biometrics
  ALTER COLUMN user_id SET NOT NULL,
  ALTER COLUMN date    SET NOT NULL,
  ALTER COLUMN date    SET DEFAULT CURRENT_DATE;

-- ── 3. UNIQUE constraints som saknas ─────────────────────────
DO $$ BEGIN
  ALTER TABLE recovery_logs
    ADD CONSTRAINT recovery_logs_user_date_key UNIQUE (user_id, date);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  ALTER TABLE biometrics
    ADD CONSTRAINT biometrics_user_date_key UNIQUE (user_id, date);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  ALTER TABLE foods
    ADD CONSTRAINT foods_name_unique UNIQUE (name);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- ── 4. ON DELETE-regler ───────────────────────────────────────
-- Säkerställ att CASCADE finns på kritiska FK:er

-- meal_logs → foods: SET NULL om mat tas bort (behåll loggen)
ALTER TABLE meal_logs
  DROP CONSTRAINT IF EXISTS meal_logs_food_id_fkey,
  ADD CONSTRAINT meal_logs_food_id_fkey
    FOREIGN KEY (food_id) REFERENCES foods(id) ON DELETE SET NULL;

-- running_sessions → users: CASCADE om user tas bort
ALTER TABLE running_sessions
  DROP CONSTRAINT IF EXISTS running_sessions_user_id_fkey,
  ADD CONSTRAINT running_sessions_user_id_fkey
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- biometrics → users: CASCADE
ALTER TABLE biometrics
  DROP CONSTRAINT IF EXISTS biometrics_user_id_fkey,
  ADD CONSTRAINT biometrics_user_id_fkey
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- recovery_logs → users: CASCADE
ALTER TABLE recovery_logs
  DROP CONSTRAINT IF EXISTS recovery_logs_user_id_fkey,
  ADD CONSTRAINT recovery_logs_user_id_fkey
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- ── 5. CHECK constraints som saknas ──────────────────────────
DO $$ BEGIN
  ALTER TABLE foods
    ADD CONSTRAINT chk_foods_calories CHECK (calories_per_100g >= 0 AND calories_per_100g <= 900);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  ALTER TABLE foods
    ADD CONSTRAINT chk_foods_protein CHECK (protein_per_100g >= 0 AND protein_per_100g <= 100);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  ALTER TABLE foods
    ADD CONSTRAINT chk_foods_carbs CHECK (carbs_per_100g >= 0 AND carbs_per_100g <= 100);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  ALTER TABLE foods
    ADD CONSTRAINT chk_foods_fat CHECK (fat_per_100g >= 0 AND fat_per_100g <= 100);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  ALTER TABLE recovery_logs
    ADD CONSTRAINT chk_recovery_sleep_quality
      CHECK (sleep_quality >= 1 AND sleep_quality <= 10);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  ALTER TABLE running_sessions
    ADD CONSTRAINT chk_running_pace
      CHECK (avg_pace_min_per_km > 0 AND avg_pace_min_per_km <= 60);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- Verifiera triggers
SELECT trigger_name, event_object_table, event_manipulation
FROM information_schema.triggers
WHERE trigger_schema = 'public'
AND trigger_name LIKE 'trg_%'
ORDER BY event_object_table;