-- ============================================================
-- migration_p9_history_tables.sql
-- Historik-tabeller för att aldrig tappa data
-- weight_history, goal_history, program_history
-- ============================================================

-- Spårar viktutveckling över tid
CREATE TABLE IF NOT EXISTS weight_history (
  id          SERIAL PRIMARY KEY,
  user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  weight_kg   NUMERIC(5,2) NOT NULL CHECK (weight_kg >= 20 AND weight_kg <= 400),
  measured_at DATE NOT NULL DEFAULT CURRENT_DATE,
  note        TEXT,
  created_at  TIMESTAMP DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_weight_history_user_date
  ON weight_history(user_id, measured_at DESC);

-- Spårar när och varför en user byter mål
CREATE TABLE IF NOT EXISTS goal_history (
  id         SERIAL PRIMARY KEY,
  user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  old_goal   VARCHAR(50),
  new_goal   VARCHAR(50) NOT NULL,
  changed_at TIMESTAMP DEFAULT NOW(),
  reason     TEXT
);

CREATE INDEX IF NOT EXISTS idx_goal_history_user
  ON goal_history(user_id, changed_at DESC);

-- Spårar vilket träningsprogram en user följt och när
CREATE TABLE IF NOT EXISTS program_history (
  id         SERIAL PRIMARY KEY,
  user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  plan_id    INTEGER REFERENCES training_plans(id) ON DELETE SET NULL,
  started_at DATE NOT NULL DEFAULT CURRENT_DATE,
  ended_at   DATE,
  completed  BOOLEAN DEFAULT false,
  notes      TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_program_history_user
  ON program_history(user_id, started_at DESC);

SELECT
  'weight_history'  AS tabell, COUNT(*) FROM weight_history
UNION ALL SELECT 'goal_history',    COUNT(*) FROM goal_history
UNION ALL SELECT 'program_history', COUNT(*) FROM program_history;