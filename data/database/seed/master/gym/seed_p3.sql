-- ============================================================
-- seed_p3_fix.sql
-- Fixar kolumnnamn: city, amount_g, restriction_level
-- Inkluderar Norrköping-gym
-- ============================================================

-- ── GYMS — svenska gym inkl Norrköping ───────────────────────
INSERT INTO gyms (id, name, city, country, gym_type, description, is_active) VALUES
(4,  'Nordic Wellness',            'Göteborg',   'Sweden', 'commercial', 'Stor kedja med många anläggningar',     true),
(5,  'Fitness24Seven',             'Malmö',      'Sweden', 'commercial', 'Öppet dygnet runt, hela året',          true),
(6,  'Friskis & Svettis',          'Stockholm',  'Sweden', 'commercial', 'Ideell förening, bredd och gemenskap',  true),
(7,  'Life',                       'Stockholm',  'Sweden', 'boutique',   'Premium PT-studio',                     true),
(8,  'EVO Gym',                    'Stockholm',  'Sweden', 'commercial', 'Modern utrustning, central placering',  true),
(9,  'World Class',                'Stockholm',  'Sweden', 'commercial', 'Premium gym med pool och spa',          true),
(10, 'Crossfit Stockholm',         'Stockholm',  'Sweden', 'crossfit',   'Funktionell träning och gemenskap',     true),
(11, 'PT-studio Östermalm',        'Stockholm',  'Sweden', 'boutique',   'Privat PT-studio, personlig träning',  true),
(12, 'Gym Göteborg',               'Göteborg',   'Sweden', 'commercial', 'Lokalt gym med bra atmosfär',           true),
(13, 'Train Hard',                 'Malmö',      'Sweden', 'commercial', 'Styrkelyftinriktat gym',                true),
(14, 'Iron Gym',                   'Uppsala',    'Sweden', 'commercial', 'Klassiskt styrkelyftsgym',              true),
(15, 'Bodystore Gym',              'Örebro',     'Sweden', 'commercial', 'Välutrustat gym med bred träningsyta',  true),
(16, 'SATS Norrköping',            'Norrköping', 'Sweden', 'commercial', 'SATS-anläggning i Norrköping',         true),
(17, 'Fitness24Seven Norrköping',  'Norrköping', 'Sweden', 'commercial', 'Öppet dygnet runt i Norrköping',       true),
(18, 'Nordic Wellness Norrköping', 'Norrköping', 'Sweden', 'commercial', 'Nordic Wellness i Norrköping',         true),
(19, 'Actic Norrköping',           'Norrköping', 'Sweden', 'commercial', 'Actic i Norrköping',                   true)
ON CONFLICT DO NOTHING;

-- ── USER GYM MEMBERSHIPS ──────────────────────────────────────
INSERT INTO user_gym_memberships
  (user_id, gym_id, is_primary, joined_at, expires_at, is_active) VALUES
(2, 1,  true,  '2026-01-01', '2026-12-31', true),   -- Erik → SATS
(3, 6,  true,  '2026-02-01', '2026-12-31', true),   -- Sara → Friskis
(4, 11, true,  '2025-06-01', '2026-12-31', true),   -- Mohammed → PT-studio
(4, 1,  false, '2026-01-01', '2026-12-31', true),   -- Mohammed → SATS också
(5, 5,  true,  '2026-03-01', '2026-12-31', true),   -- Fatima → Fitness24Seven
(6, 2,  true,  '2026-01-15', '2026-12-31', true),   -- Lucas → Actic
(7, 4,  true,  '2026-02-15', '2026-12-31', true),   -- Amina → Nordic Wellness
(8, 9,  true,  '2025-09-01', '2026-12-31', true),   -- Viktor → World Class
(8, 11, false, '2025-09-01', '2026-12-31', true),   -- Viktor → PT-studio
(9, 8,  true,  '2026-07-01', '2026-12-31', true)    -- Lina → EVO Gym
ON CONFLICT (user_id, gym_id) DO NOTHING;

-- ── RECIPE FOODS ──────────────────────────────────────────────
INSERT INTO recipe_foods (recipe_id, food_id, amount_g, notes) VALUES
(1, 2,  80.00,  'Havregryn'),
(1, 5,  200.00, 'Kvarg'),
(1, 4,  100.00, 'Banan'),
(1, 9,  20.00,  'Mandlar'),
(1, 10, 30.00,  'Proteinpulver'),
(2, 1,  200.00, 'Kycklingbröst'),
(2, 8,  250.00, 'Sötpotatis'),
(2, 6,  150.00, 'Broccoli'),
(3, 7,  180.00, 'Lax'),
(3, 6,  200.00, 'Broccoli'),
(4, 4,  150.00, 'Banan'),
(4, 5,  200.00, 'Kvarg'),
(4, 10, 40.00,  'Proteinpulver'),
(4, 9,  15.00,  'Mandlar'),
(5, 3,  150.00, 'Ägg ca 3 st')
ON CONFLICT (recipe_id, food_id) DO NOTHING;

-- ── INJURY EXERCISE RESTRICTIONS ─────────────────────────────
INSERT INTO injury_exercise_restrictions
  (injury_id, exercise_id, restriction_level, notes) VALUES
(1, 5,   'avoid',  'Knäböj — undvik vid knäskada'),
(1, 127, 'avoid',  'Back Squat'),
(1, 73,  'modify', 'Leg Press — lätt vikt OK'),
(1, 79,  'avoid',  'Bulgarian Split Squat'),
(1, 132, 'avoid',  'Hack Squat'),
(2, 7,   'avoid',  'Militärpress — skulderbelastning'),
(2, 139, 'avoid',  'Overhead Press'),
(2, 1,   'modify', 'Bänkpress — lätt vikt med kontroll'),
(2, 141, 'avoid',  'Arnold Press'),
(2, 148, 'avoid',  'Upright Row'),
(3, 3,   'avoid',  'Marklyft — ländryggsbelastning'),
(3, 114, 'avoid',  'Conventional Deadlift'),
(3, 115, 'avoid',  'Sumo Deadlift'),
(3, 126, 'avoid',  'Good Morning'),
(3, 116, 'modify', 'Barbell Row — försiktig böjning'),
(4, 150, 'avoid',  'Barbell Curl — handledsbelastning'),
(4, 157, 'avoid',  'Skull Crusher'),
(4, 104, 'modify', 'Bench Press — neutralt grepp'),
(4, 159, 'avoid',  'Wrist Curl'),
(4, 160, 'avoid',  'Reverse Wrist Curl')
ON CONFLICT (injury_id, exercise_id) DO NOTHING;

-- Sammanfattning
SELECT 'gyms'                        AS tabell, COUNT(*) AS rader FROM gyms
UNION ALL SELECT 'user_gym_memberships',         COUNT(*) FROM user_gym_memberships
UNION ALL SELECT 'nutrition_targets',            COUNT(*) FROM nutrition_targets
UNION ALL SELECT 'recipe_foods',                 COUNT(*) FROM recipe_foods
UNION ALL SELECT 'injury_exercise_restrictions', COUNT(*) FROM injury_exercise_restrictions
UNION ALL SELECT 'progression_log',              COUNT(*) FROM progression_log
ORDER BY tabell;