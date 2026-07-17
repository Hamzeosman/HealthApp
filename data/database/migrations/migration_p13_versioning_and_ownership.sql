-- ============================================================
-- migration_p13_versioning_and_ownership.sql
-- created_by, reviewed_by på master data
-- exercise_versions för att spåra ändringar i övningar
-- Audit log kommentar om vad som bör loggas
-- ============================================================

-- ── created_by + reviewed_by på master data ──────────────────
ALTER TABLE exercises
  ADD COLUMN IF NOT EXISTS created_by  INTEGER REFERENCES users(id) ON DELETE SET NULL,
  ADD COLUMN IF NOT EXISTS reviewed_by INTEGER REFERENCES users(id) ON DELETE SET NULL;

ALTER TABLE foods
  ADD COLUMN IF NOT EXISTS created_by INTEGER REFERENCES users(id) ON DELETE SET NULL;

ALTER TABLE training_plans
  ADD COLUMN IF NOT EXISTS created_by  INTEGER REFERENCES users(id) ON DELETE SET NULL,
  ADD COLUMN IF NOT EXISTS reviewed_by INTEGER REFERENCES users(id) ON DELETE SET NULL;

ALTER TABLE equipment
  ADD COLUMN IF NOT EXISTS created_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
  ADD COLUMN IF NOT EXISTS updated_by INTEGER REFERENCES users(id) ON DELETE SET NULL;

-- ── exercise_versions — spårar ändringar i övningar ──────────
-- Om teknikbeskrivningen för Knäböj ändras om 2 år
-- kan vi se exakt vad som ändrades, av vem och varför
CREATE TABLE IF NOT EXISTS exercise_versions (
  id          SERIAL PRIMARY KEY,
  exercise_id INTEGER NOT NULL REFERENCES exercises(id) ON DELETE CASCADE,
  version     INTEGER NOT NULL DEFAULT 1,
  field_name  VARCHAR(100) NOT NULL,
  old_value   TEXT,
  new_value   TEXT,
  changed_by  INTEGER REFERENCES users(id) ON DELETE SET NULL,
  changed_at  TIMESTAMP DEFAULT NOW(),
  reason      TEXT
);

CREATE INDEX IF NOT EXISTS idx_exercise_versions_exercise
  ON exercise_versions(exercise_id, changed_at DESC);

-- ── Audit log — vad bör loggas? ───────────────────────────────
-- LOGGA: DELETE på alla tabeller
-- LOGGA: UPDATE på kritiska fält (weight_kg, fitness_goal, email)
-- LOGGA: Admin actions (role changes, user deletions)
-- LOGGA INTE: varje meal_log UPDATE (blir tusentals rader)
-- LOGGA INTE: biometrics updates (dagliga, många)
-- Detta hanteras av API:et, inte databasen

COMMENT ON TABLE audit_log IS
  'Loggar viktiga händelser. Bör användas för: DELETE på alla tabeller, UPDATE på kritiska fält (email, role, weight), admin actions. Bör INTE användas för: varje meal_log update, dagliga biometrics updates.';

-- Verifiera
SELECT 'exercise_versions' AS tabell, COUNT(*) FROM exercise_versions
UNION ALL SELECT 'exercises med created_by', COUNT(*) FROM exercises WHERE created_by IS NULL
UNION ALL SELECT 'training_plans med reviewed_by', COUNT(*) FROM training_plans WHERE reviewed_by IS NULL;