-- ============================================================
-- migration_p8_audit_log.sql
-- Audit-logg för att spåra ändringar i kritiska tabeller
-- Vem ändrade vad och när
-- ============================================================

CREATE TABLE IF NOT EXISTS audit_log (
  id          BIGSERIAL PRIMARY KEY,
  user_id     INTEGER REFERENCES users(id) ON DELETE SET NULL,
  table_name  VARCHAR(100) NOT NULL,
  action      VARCHAR(10)  NOT NULL CHECK (action IN ('INSERT', 'UPDATE', 'DELETE')),
  record_id   INTEGER,
  old_value   JSONB,
  new_value   JSONB,
  changed_at  TIMESTAMP DEFAULT NOW(),
  ip_address  VARCHAR(45)
);

CREATE INDEX IF NOT EXISTS idx_audit_log_user
  ON audit_log(user_id, changed_at DESC);

CREATE INDEX IF NOT EXISTS idx_audit_log_table
  ON audit_log(table_name, changed_at DESC);

CREATE INDEX IF NOT EXISTS idx_audit_log_record
  ON audit_log(table_name, record_id);

-- Exempel på hur man loggar en ändring (används av API/pipelines):
-- INSERT INTO audit_log (user_id, table_name, action, record_id, old_value, new_value)
-- VALUES (1, 'workout_sessions', 'UPDATE', 42,
--   '{"duration_minutes": 45}'::jsonb,
--   '{"duration_minutes": 60}'::jsonb);

SELECT 'audit_log migration klar!' AS status;