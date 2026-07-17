-- ============================================================
-- migration_p10_exercise_intelligence.sql
-- Exercise progressions, regressions och coach_messages
-- AI-coachen får en kunskapsbas att svara från
-- ============================================================

-- Svårare varianter av en övning
CREATE TABLE IF NOT EXISTS exercise_progressions (
  id             SERIAL PRIMARY KEY,
  exercise_id    INTEGER NOT NULL REFERENCES exercises(id) ON DELETE CASCADE,
  progression_id INTEGER NOT NULL REFERENCES exercises(id) ON DELETE CASCADE,
  difficulty_jump INTEGER CHECK (difficulty_jump BETWEEN 1 AND 5),
  notes          TEXT,
  UNIQUE (exercise_id, progression_id)
);

CREATE INDEX IF NOT EXISTS idx_exercise_progressions_source
  ON exercise_progressions(exercise_id);

-- Lättare varianter av en övning
CREATE TABLE IF NOT EXISTS exercise_regressions (
  id            SERIAL PRIMARY KEY,
  exercise_id   INTEGER NOT NULL REFERENCES exercises(id) ON DELETE CASCADE,
  regression_id INTEGER NOT NULL REFERENCES exercises(id) ON DELETE CASCADE,
  notes         TEXT,
  UNIQUE (exercise_id, regression_id)
);

CREATE INDEX IF NOT EXISTS idx_exercise_regressions_source
  ON exercise_regressions(exercise_id);

-- AI-coachens kunskapsbas
CREATE TABLE IF NOT EXISTS coach_messages (
  id           SERIAL PRIMARY KEY,
  category     VARCHAR(50) NOT NULL,
  trigger_type VARCHAR(50) NOT NULL,
  message_sv   TEXT NOT NULL,
  message_en   TEXT,
  priority     INTEGER DEFAULT 5,
  is_active    BOOLEAN DEFAULT true,
  created_at   TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_coach_messages_category
  ON coach_messages(category, trigger_type);

-- ── Seed coach_messages ───────────────────────────────────────
INSERT INTO coach_messages (category, trigger_type, message_sv, message_en, priority) VALUES

-- Readiness
('readiness', 'score_high',
 'Din readiness är hög idag. Perfekt tillfälle för ett tungt pass eller att sätta ett personbästa.',
 'Your readiness is high today. Perfect time for a heavy session or setting a personal record.',
 10),

('readiness', 'score_medium',
 'Din readiness är bra. Kör ditt planerade pass med normal intensitet.',
 'Your readiness is good. Run your planned session at normal intensity.',
 8),

('readiness', 'score_low',
 'Din readiness är låg idag. Överväg ett lätt rörlighetspass eller vila.',
 'Your readiness is low today. Consider a light mobility session or rest.',
 10),

-- Sömn
('recovery', 'sleep_poor',
 'Du har sovit under 6 timmar. Prioritera sömn — det är när musklerna växer och återhämtar sig.',
 'You have slept less than 6 hours. Prioritize sleep — that is when muscles grow and recover.',
 9),

('recovery', 'sleep_good',
 'Bra sömn! Du har gett kroppen optimala förutsättningar för träning och återhämtning.',
 'Great sleep! You have given your body optimal conditions for training and recovery.',
 6),

-- ACWR
('load', 'acwr_danger',
 'Din träningsbelastning är mycket hög jämfört med din normala nivå. Risk för skada — kör deload.',
 'Your training load is very high compared to your normal level. Injury risk — run a deload.',
 10),

('load', 'acwr_caution',
 'Din träningsbelastning ökar snabbt. Var försiktig och prioritera återhämtning.',
 'Your training load is increasing rapidly. Be careful and prioritize recovery.',
 8),

('load', 'acwr_optimal',
 'Din träningsbelastning är i optimal zon. Fortsätt med nuvarande progression.',
 'Your training load is in the optimal zone. Continue with your current progression.',
 5),

('load', 'acwr_low',
 'Du tränar under din normala nivå. Om det inte är en planerad deload — öka volymen gradvis.',
 'You are training below your normal level. If this is not a planned deload — increase volume gradually.',
 6),

-- Progression
('progression', 'pr_set',
 'Nytt personbästa! Kom ihåg att deloada nästa vecka för optimal återhämtning.',
 'New personal record! Remember to deload next week for optimal recovery.',
 9),

('progression', 'rpe_dropping',
 'Din RPE sjunker vid samma vikt — du blir starkare! Dags att öka vikten med 2.5kg.',
 'Your RPE is dropping at the same weight — you are getting stronger! Time to increase weight by 2.5kg.',
 8),

('progression', 'volume_increase',
 'Din träningsvolym ökade med mer än 10% denna vecka. Bra progression!',
 'Your training volume increased by more than 10% this week. Great progression!',
 7),

-- Muskelbalans
('balance', 'push_pull_imbalance',
 'Du tränar mer push än pull. Lägg till fler dragövningar för att förebygga skulderbesvär.',
 'You train more push than pull. Add more pulling exercises to prevent shoulder issues.',
 8),

('balance', 'upper_lower_imbalance',
 'Du tränar mer överkropp än underkropp. Lägg till benpass för bättre helkroppsbalans.',
 'You train more upper body than lower body. Add leg sessions for better overall balance.',
 8),

-- Deload
('recovery', 'deload_recommended',
 'Du har tränat hårt i flera veckor. En deload-vecka med 60% vikt förbättrar långsiktig progression.',
 'You have trained hard for several weeks. A deload week at 60% weight improves long-term progression.',
 9),

-- Nutrition
('nutrition', 'calories_low',
 'Ditt kaloriintag är lågt för ditt träningsmål. Se till att äta tillräckligt för återhämtning.',
 'Your calorie intake is low for your training goal. Make sure to eat enough for recovery.',
 7),

('nutrition', 'protein_low',
 'Ditt proteinintag är under rekommenderat. Sikta på 1.6-2.2g protein per kg kroppsvikt.',
 'Your protein intake is below recommended. Aim for 1.6-2.2g protein per kg body weight.',
 8)

ON CONFLICT DO NOTHING;

-- Progressions för compound övningar
-- Knäböj → Bulgarian Split Squat → Pistol Squat
INSERT INTO exercise_progressions (exercise_id, progression_id, difficulty_jump, notes)
SELECT e1.id, e2.id, 2, 'Mer instabilt, kräver bättre balans'
FROM exercises e1, exercises e2
WHERE e1.name = 'Knäböj' AND e2.name = 'Bulgarian Split Squat'
ON CONFLICT DO NOTHING;

-- Bänkpress → Dips
INSERT INTO exercise_progressions (exercise_id, progression_id, difficulty_jump, notes)
SELECT e1.id, e2.id, 2, 'Mer belastning på triceps, kräver kroppskontroll'
FROM exercises e1, exercises e2
WHERE e1.name = 'Bänkpress' AND e2.name = 'Dips'
ON CONFLICT DO NOTHING;

-- Latsdrag → Pull-ups
INSERT INTO exercise_progressions (exercise_id, progression_id, difficulty_jump, notes)
SELECT e1.id, e2.id, 3, 'Full kroppsvikt, svårare kontroll'
FROM exercises e1, exercises e2
WHERE e1.name = 'Latsdrag' AND e2.name = 'Pull-ups'
ON CONFLICT DO NOTHING;

-- Regressions
-- Bulgarian Split Squat → Utfall (lättare)
INSERT INTO exercise_regressions (exercise_id, regression_id, notes)
SELECT e1.id, e2.id, 'Mer stabil, bra för nybörjare'
FROM exercises e1, exercises e2
WHERE e1.name = 'Bulgarian Split Squat' AND e2.name = 'Utfall'
ON CONFLICT DO NOTHING;

-- Pull-ups → Latsdrag
INSERT INTO exercise_regressions (exercise_id, regression_id, notes)
SELECT e1.id, e2.id, 'Maskin hjälper med vikten'
FROM exercises e1, exercises e2
WHERE e1.name = 'Pull-ups' AND e2.name = 'Latsdrag'
ON CONFLICT DO NOTHING;

-- Verifiera
SELECT 'exercise_progressions' AS tabell, COUNT(*) FROM exercise_progressions
UNION ALL SELECT 'exercise_regressions', COUNT(*) FROM exercise_regressions
UNION ALL SELECT 'coach_messages', COUNT(*) FROM coach_messages;