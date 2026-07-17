-- ============================================================
-- migration_p12_metadata_improvements.sql
-- Förbättringar baserade på feedback:
-- 1. coach_messages: language, tone, condition, min/max_value
-- 2. Master data: status, source, evidence_level, updated_by
-- ============================================================

-- ── 1. COACH MESSAGES — mer strukturerade ────────────────────
ALTER TABLE coach_messages
  ADD COLUMN IF NOT EXISTS language  VARCHAR(10) DEFAULT 'sv',
  ADD COLUMN IF NOT EXISTS tone      VARCHAR(20) DEFAULT 'neutral',
  ADD COLUMN IF NOT EXISTS condition TEXT,
  ADD COLUMN IF NOT EXISTS min_value NUMERIC,
  ADD COLUMN IF NOT EXISTS max_value NUMERIC;

DO $$ BEGIN
  ALTER TABLE coach_messages ADD CONSTRAINT chk_coach_language
    CHECK (language IN ('sv', 'en', 'ar', 'so', 'fr', 'de', 'pt', 'es'));
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  ALTER TABLE coach_messages ADD CONSTRAINT chk_coach_tone
    CHECK (tone IN ('neutral', 'motivating', 'warning', 'celebrating', 'informative'));
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- Uppdatera befintliga meddelanden med rätt tone
UPDATE coach_messages SET language = 'sv', tone = 'motivating'  WHERE trigger_type = 'score_high';
UPDATE coach_messages SET language = 'sv', tone = 'neutral'     WHERE trigger_type = 'score_medium';
UPDATE coach_messages SET language = 'sv', tone = 'warning'     WHERE trigger_type = 'score_low';
UPDATE coach_messages SET language = 'sv', tone = 'warning'     WHERE trigger_type = 'sleep_poor';
UPDATE coach_messages SET language = 'sv', tone = 'motivating'  WHERE trigger_type = 'sleep_good';
UPDATE coach_messages SET language = 'sv', tone = 'warning'     WHERE trigger_type = 'acwr_danger';
UPDATE coach_messages SET language = 'sv', tone = 'warning'     WHERE trigger_type = 'acwr_caution';
UPDATE coach_messages SET language = 'sv', tone = 'motivating'  WHERE trigger_type = 'acwr_optimal';
UPDATE coach_messages SET language = 'sv', tone = 'neutral'     WHERE trigger_type = 'acwr_low';
UPDATE coach_messages SET language = 'sv', tone = 'celebrating' WHERE trigger_type = 'pr_set';
UPDATE coach_messages SET language = 'sv', tone = 'motivating'  WHERE trigger_type = 'rpe_dropping';
UPDATE coach_messages SET language = 'sv', tone = 'motivating'  WHERE trigger_type = 'volume_increase';
UPDATE coach_messages SET language = 'sv', tone = 'warning'     WHERE trigger_type = 'deload_recommended';
UPDATE coach_messages SET language = 'sv', tone = 'informative' WHERE category = 'nutrition';
UPDATE coach_messages SET language = 'sv', tone = 'informative' WHERE category = 'balance';

-- ── 2. MASTER DATA — status, source, evidence_level ──────────

-- exercises
ALTER TABLE exercises
  ADD COLUMN IF NOT EXISTS status       VARCHAR(20) DEFAULT 'published',
  ADD COLUMN IF NOT EXISTS source       VARCHAR(100),
  ADD COLUMN IF NOT EXISTS last_reviewed DATE,
  ADD COLUMN IF NOT EXISTS updated_by   INTEGER REFERENCES users(id) ON DELETE SET NULL;

DO $$ BEGIN
  ALTER TABLE exercises ADD CONSTRAINT chk_exercises_status
    CHECK (status IN ('draft', 'published', 'deprecated', 'archived'));
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

UPDATE exercises SET status = 'published', source = 'HealthApp seed data'
WHERE status IS NULL;

-- foods
ALTER TABLE foods
  ADD COLUMN IF NOT EXISTS status     VARCHAR(20) DEFAULT 'published',
  ADD COLUMN IF NOT EXISTS source     VARCHAR(100),
  ADD COLUMN IF NOT EXISTS updated_by INTEGER REFERENCES users(id) ON DELETE SET NULL;

DO $$ BEGIN
  ALTER TABLE foods ADD CONSTRAINT chk_foods_status
    CHECK (status IN ('draft', 'published', 'deprecated', 'archived'));
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

UPDATE foods SET status = 'published', source = 'Livsmedelsverket'
WHERE status IS NULL;

-- training_plans
ALTER TABLE training_plans
  ADD COLUMN IF NOT EXISTS status         VARCHAR(20) DEFAULT 'published',
  ADD COLUMN IF NOT EXISTS source         VARCHAR(100),
  ADD COLUMN IF NOT EXISTS evidence_level VARCHAR(20) DEFAULT 'evidence_based',
  ADD COLUMN IF NOT EXISTS updated_by     INTEGER REFERENCES users(id) ON DELETE SET NULL;

DO $$ BEGIN
  ALTER TABLE training_plans ADD CONSTRAINT chk_plans_status
    CHECK (status IN ('draft', 'published', 'deprecated', 'archived'));
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  ALTER TABLE training_plans ADD CONSTRAINT chk_plans_evidence
    CHECK (evidence_level IN ('evidence_based', 'expert_opinion', 'experimental'));
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

UPDATE training_plans
SET status = 'published', source = 'HealthApp seed data', evidence_level = 'evidence_based'
WHERE status IS NULL;

-- Verifiera
SELECT 'exercises'     AS tabell, COUNT(*) FILTER (WHERE status = 'published') AS published FROM exercises
UNION ALL SELECT 'foods',         COUNT(*) FILTER (WHERE status = 'published') FROM foods
UNION ALL SELECT 'training_plans',COUNT(*) FILTER (WHERE status = 'published') FROM training_plans
UNION ALL SELECT 'coach_messages (sv)', COUNT(*) FILTER (WHERE language = 'sv') FROM coach_messages;