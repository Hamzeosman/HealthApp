-- ============================================================
-- migration_p5_quality_fix.sql
-- Fixar: ADD CONSTRAINT IF NOT EXISTS → DO $$ EXCEPTION block
-- ============================================================

-- ── 1. SLUG & SOFT DELETE ────────────────────────────────────

ALTER TABLE exercises
  ADD COLUMN IF NOT EXISTS slug VARCHAR(150),
  ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP,
  ADD COLUMN IF NOT EXISTS created_by INTEGER REFERENCES users(id) ON DELETE SET NULL;

UPDATE exercises SET slug = TRIM(BOTH '-' FROM
  REGEXP_REPLACE(
    LOWER(
      TRANSLATE(name, 'åäöÅÄÖ ', 'aaoAAO-')
    ), '[^a-z0-9-]+', '-', 'g'
  )
) WHERE slug IS NULL;

CREATE UNIQUE INDEX IF NOT EXISTS idx_exercises_slug
  ON exercises(slug) WHERE deleted_at IS NULL;

ALTER TABLE equipment
  ADD COLUMN IF NOT EXISTS slug VARCHAR(150),
  ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP,
  ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT NOW();

UPDATE equipment SET slug = TRIM(BOTH '-' FROM
  REGEXP_REPLACE(
    LOWER(TRANSLATE(name, 'åäöÅÄÖ ', 'aaoAAO-')),
    '[^a-z0-9-]+', '-', 'g'
  )
) WHERE slug IS NULL;

CREATE UNIQUE INDEX IF NOT EXISTS idx_equipment_slug
  ON equipment(slug) WHERE deleted_at IS NULL;

ALTER TABLE foods
  ADD COLUMN IF NOT EXISTS slug VARCHAR(150),
  ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP,
  ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT NOW();

UPDATE foods SET slug = TRIM(BOTH '-' FROM
  REGEXP_REPLACE(
    LOWER(TRANSLATE(name, 'åäöÅÄÖ% ', 'aaoAAO--')),
    '[^a-z0-9-]+', '-', 'g'
  )
) WHERE slug IS NULL;

CREATE UNIQUE INDEX IF NOT EXISTS idx_foods_slug
  ON foods(slug) WHERE deleted_at IS NULL;

ALTER TABLE gyms
  ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT NOW();

-- ── 2. CHECK CONSTRAINTS (utan IF NOT EXISTS) ─────────────────
DO $$ BEGIN
  ALTER TABLE workout_exercises
    ADD CONSTRAINT chk_we_sets CHECK (sets > 0 AND sets <= 20);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  ALTER TABLE workout_exercises
    ADD CONSTRAINT chk_we_reps CHECK (reps > 0 AND reps <= 100);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  ALTER TABLE workout_exercises
    ADD CONSTRAINT chk_we_weight CHECK (weight_kg >= 0 AND weight_kg <= 500);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  ALTER TABLE workout_exercises
    ADD CONSTRAINT chk_we_rpe CHECK (rpe >= 1 AND rpe <= 10);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  ALTER TABLE recovery_logs
    ADD CONSTRAINT chk_recovery_sleep CHECK (sleep_hours >= 0 AND sleep_hours <= 16);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  ALTER TABLE recovery_logs
    ADD CONSTRAINT chk_recovery_energy CHECK (energy_level >= 1 AND energy_level <= 10);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  ALTER TABLE recovery_logs
    ADD CONSTRAINT chk_recovery_stress CHECK (stress_level >= 1 AND stress_level <= 10);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  ALTER TABLE biometrics
    ADD CONSTRAINT chk_biometrics_steps CHECK (steps >= 0 AND steps <= 100000);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  ALTER TABLE biometrics
    ADD CONSTRAINT chk_biometrics_hr_rest CHECK (heart_rate_resting >= 30 AND heart_rate_resting <= 120);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  ALTER TABLE biometrics
    ADD CONSTRAINT chk_biometrics_hr_max CHECK (heart_rate_max >= 60 AND heart_rate_max <= 230);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  ALTER TABLE biometrics
    ADD CONSTRAINT chk_biometrics_vo2max CHECK (vo2_max >= 10 AND vo2_max <= 90);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  ALTER TABLE biometrics
    ADD CONSTRAINT chk_biometrics_calories CHECK (calories_burned >= 0 AND calories_burned <= 10000);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  ALTER TABLE fatigue_scores
    ADD CONSTRAINT chk_fatigue_readiness CHECK (readiness_score >= 0 AND readiness_score <= 100);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  ALTER TABLE fatigue_scores
    ADD CONSTRAINT chk_fatigue_acwr CHECK (acwr >= 0 AND acwr <= 5);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  ALTER TABLE running_sessions
    ADD CONSTRAINT chk_running_distance CHECK (distance_km >= 0 AND distance_km <= 300);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  ALTER TABLE running_sessions
    ADD CONSTRAINT chk_running_duration CHECK (duration_minutes > 0 AND duration_minutes <= 1440);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  ALTER TABLE running_sessions
    ADD CONSTRAINT chk_running_hr CHECK (avg_heart_rate >= 30 AND avg_heart_rate <= 230);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  ALTER TABLE users
    ADD CONSTRAINT chk_users_weight CHECK (weight_kg >= 20 AND weight_kg <= 400);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  ALTER TABLE users
    ADD CONSTRAINT chk_users_height CHECK (height_cm >= 100 AND height_cm <= 250);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  ALTER TABLE meal_logs
    ADD CONSTRAINT chk_meal_calories CHECK (calories >= 0 AND calories <= 3000);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  ALTER TABLE meal_logs
    ADD CONSTRAINT chk_meal_protein CHECK (protein_g >= 0 AND protein_g <= 500);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  ALTER TABLE meal_logs
    ADD CONSTRAINT chk_meal_fat CHECK (fat_g >= 0 AND fat_g <= 300);
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- ── 3. INDEX ──────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_workout_exercises_exercise
  ON workout_exercises(exercise_id);

CREATE INDEX IF NOT EXISTS idx_personal_records_user_exercise
  ON personal_records(user_id, exercise_id);

CREATE INDEX IF NOT EXISTS idx_personal_records_date
  ON personal_records(user_id, date DESC);

CREATE INDEX IF NOT EXISTS idx_nutrition_logs_user_date
  ON nutrition_logs(user_id, date DESC);

CREATE INDEX IF NOT EXISTS idx_training_metrics_user_date
  ON training_metrics(user_id, date DESC);

CREATE INDEX IF NOT EXISTS idx_exercises_name
  ON exercises(name);

CREATE INDEX IF NOT EXISTS idx_exercises_difficulty
  ON exercises(difficulty);

CREATE INDEX IF NOT EXISTS idx_equipment_exercises_exercise
  ON equipment_exercises(exercise_id);

CREATE INDEX IF NOT EXISTS idx_gyms_city
  ON gyms(city);

CREATE INDEX IF NOT EXISTS idx_gyms_active
  ON gyms(is_active) WHERE is_active = true;

CREATE INDEX IF NOT EXISTS idx_recommendations_user_date
  ON recommendations(user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_ai_insights_user_date
  ON ai_insights(user_id, created_at DESC);

-- Verifiera
SELECT 'exercises slug'  AS kontroll, COUNT(*) FROM exercises WHERE slug IS NOT NULL
UNION ALL SELECT 'equipment slug',    COUNT(*) FROM equipment WHERE slug IS NOT NULL
UNION ALL SELECT 'foods slug',        COUNT(*) FROM foods    WHERE slug IS NOT NULL
UNION ALL SELECT 'nya constraints',   COUNT(*) FROM information_schema.table_constraints
  WHERE constraint_schema = 'public'
  AND constraint_name LIKE 'chk_%'
UNION ALL SELECT 'nya index',         COUNT(*) FROM pg_indexes
  WHERE schemaname = 'public'
  AND indexname LIKE 'idx_%'
ORDER BY kontroll;