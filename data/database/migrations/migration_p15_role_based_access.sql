-- ============================================================
-- migration_p15_role_based_access.sql
-- Rollbaserad åtkomst för HealthApp
-- Baserat på feedback: vem får göra vad?
-- ============================================================

-- ── Skapa roller ─────────────────────────────────────────────
CREATE ROLE IF NOT EXISTS healthapp_admin;
CREATE ROLE IF NOT EXISTS healthapp_pt;
CREATE ROLE IF NOT EXISTS healthapp_user;
CREATE ROLE IF NOT EXISTS healthapp_ai_service;
CREATE ROLE IF NOT EXISTS healthapp_analytics;

-- ── Admin — full åtkomst till allt ───────────────────────────
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO healthapp_admin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO healthapp_admin;

-- ── PT (Personal Trainer) ─────────────────────────────────────
-- Läsa alla users och träningsdata
-- Skriva rekommendationer och insights
GRANT SELECT ON users, workout_sessions, workout_exercises,
  personal_records, recovery_logs, biometrics, running_sessions,
  exercises, body_parts, equipment, training_plans,
  fatigue_scores, training_metrics, recommendations,
  exercise_progressions, exercise_regressions, coach_messages
  TO healthapp_pt;

GRANT INSERT, UPDATE ON recommendations, ai_insights, notifications
  TO healthapp_pt;

-- ── User ──────────────────────────────────────────────────────
-- Bara sin egen data (row-level security hanteras av API)
-- Läsa master data
GRANT SELECT, INSERT, UPDATE ON
  workout_sessions, workout_exercises, personal_records,
  recovery_logs, biometrics, running_sessions, meal_logs,
  body_measurements, user_goals, weight_history, goal_history,
  program_history
  TO healthapp_user;

GRANT SELECT ON exercises, foods, equipment, training_plans,
  achievements, body_parts, exercise_tags, exercise_tag_map,
  coach_messages, gyms
  TO healthapp_user;

-- ── AI-service ────────────────────────────────────────────────
-- Läsa allt för att kunna ge personliga svar
-- Skriva insights, rekommendationer och metrics
GRANT SELECT ON ALL TABLES IN SCHEMA public TO healthapp_ai_service;
GRANT INSERT, UPDATE ON ai_insights, recommendations,
  coach_messages, notifications, fatigue_scores, training_metrics
  TO healthapp_ai_service;

-- ── Analytics ─────────────────────────────────────────────────
-- Bara läsåtkomst — för dashboards och rapporter
GRANT SELECT ON ALL TABLES IN SCHEMA public TO healthapp_analytics;

-- ── Rollmatris (dokumentation) ────────────────────────────────
-- Roll              | Läsa users | Skriva user data | Skriva master | Läsa analytics
-- healthapp_admin   | ✓          | ✓                | ✓             | ✓
-- healthapp_pt      | ✓          | rekommendationer | ✗             | ✓
-- healthapp_user    | egen data  | egen data        | ✗             | ✗
-- healthapp_ai_service | ✓       | insights         | ✗             | ✓
-- healthapp_analytics  | ✓       | ✗                | ✗             | ✓

SELECT rolname FROM pg_roles
WHERE rolname LIKE 'healthapp_%'
ORDER BY rolname;