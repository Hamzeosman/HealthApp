-- ============================================================
-- seed_master_data.sql
-- Fyller: exercise_substitutions, exercise_substitution_rules,
--         achievements, progression_rules
-- Alla dessa är master data — inte user data
-- ============================================================

-- ── EXERCISE SUBSTITUTIONS ────────────────────────────────────
-- Reasons: injury, equipment_unavailable, difficulty, preference, progression, deload
INSERT INTO exercise_substitutions
  (original_exercise_id, substitute_exercise_id, reason, similarity_score, notes) VALUES

-- BRÖST substitutioner
(1,   107, 'equipment_unavailable', 0.92, 'Dumbbell bench press — bra alternativ utan skivstång'),
(1,   111, 'equipment_unavailable', 0.70, 'Push-ups — hemgym alternativ'),
(1,   104, 'progression',           0.95, 'Flat barbell bench press — samma rörelse'),
(1,   105, 'progression',           0.80, 'Incline press — mer övre bröst'),
(107, 111, 'equipment_unavailable', 0.72, 'Push-ups om hantlar saknas'),
(61,  108, 'equipment_unavailable', 0.90, 'Incline dumbbell press — samma muskel'),
(2,   109, 'equipment_unavailable', 0.85, 'Cable crossover om hantlar saknas'),
(63,  155, 'injury',               0.75, 'Close grip bench press — axelvänligare'),

-- RYGG substitutioner
(3,   114, 'progression',           0.95, 'Conventional deadlift — samma rörelse'),
(3,   115, 'difficulty',            0.85, 'Sumo deadlift — lättare för ryggen'),
(4,   121, 'equipment_unavailable', 0.90, 'Lat pulldown — om pull-up bar saknas'),
(4,   123, 'progression',           0.88, 'Pull-up — svårare variant'),
(68,  120, 'preference',            0.88, 'Cable row — liknande rörelse'),
(116, 117, 'equipment_unavailable', 0.85, 'Dumbbell row — om skivstång saknas'),
(118, 68,  'equipment_unavailable', 0.82, 'Seated cable row — om T-bar saknas'),

-- BEN substitutioner
(5,   129, 'difficulty',            0.78, 'Goblet squat — lättare för nybörjare'),
(5,   132, 'preference',            0.85, 'Hack squat — mer quadfokus'),
(5,   79,  'progression',           0.82, 'Bulgarian split squat — mer instabilt'),
(73,  5,   'progression',           0.88, 'Knäböj — mer funktionell'),
(74,  192, 'equipment_unavailable', 0.92, 'Romanian DL med hantlar — om skivstång saknas'),
(78,  134, 'difficulty',            0.80, 'Glute bridge — lättare variant av hip thrust'),
(78,  191, 'progression',           0.88, 'Single leg hip thrust — svårare'),
(75,  76,  'deload',                0.60, 'Leg extension — lättare för hamstrings'),

-- AXLAR substitutioner
(7,   139, 'preference',            0.95, 'Overhead press — samma rörelse'),
(7,   140, 'equipment_unavailable', 0.88, 'Seated dumbbell press — om skivstång saknas'),
(142, 143, 'preference',            0.88, 'Cable lateral raise — bättre isolering'),
(145, 69,  'preference',            0.95, 'Face pulls — samma övning'),
(146, 147, 'equipment_unavailable', 0.90, 'Cable reverse fly — om hantlar saknas'),

-- ARMAR substitutioner
(8,   154, 'preference',            0.88, 'Cable curl — konstant spänning'),
(8,   150, 'equipment_unavailable', 0.85, 'Barbell curl — om hantlar saknas'),
(9,   156, 'preference',            0.88, 'Tricep pushdown — konstant spänning'),
(9,   158, 'difficulty',            0.75, 'Tricep kickback — lättare'),
(155, 157, 'preference',            0.85, 'Skull crusher — mer isolering'),

-- MAGE substitutioner
(10,  166, 'difficulty',            0.80, 'Plank — lättare än plankan med vikt'),
(164, 163, 'difficulty',            0.82, 'Leg raise — lättare variant'),
(165, 164, 'difficulty',            0.85, 'Hanging leg raise — lättare än ab wheel'),
(170, 165, 'difficulty',            0.88, 'Ab wheel — lättare än dragon flag'),

-- KONDITION substitutioner
(11,  173, 'preference',            0.95, 'Running — samma rörelse'),
(12,  177, 'difficulty',            0.75, 'Mountain climbers — lättare än burpees'),
(178, 137, 'preference',            0.90, 'Box jump — liknande explosivitet')

ON CONFLICT (original_exercise_id, substitute_exercise_id) DO NOTHING;

-- ── EXERCISE SUBSTITUTION RULES ───────────────────────────────
-- Reasons: injury, equipment, fatigue, skill, home_gym, preference, progression, deload
-- equivalence_score: 0-1, fatigue_delta: negativ=mindre tröttande, stimulus_similarity: 1-10
INSERT INTO exercise_substitution_rules
  (source_exercise_id, target_exercise_id, substitution_reason,
   equivalence_score, fatigue_delta, stimulus_similarity, notes) VALUES

-- BRÖST regler
(1,   107, 'equipment',   0.92, -2,  9, 'Dumbbell bench — minskar axelkompression'),
(1,   111, 'home_gym',    0.70, -4,  7, 'Push-ups — inget gym behövs'),
(1,   104, 'progression', 0.95,  0, 10, 'Flat barbell — identisk rörelse'),
(61,  108, 'equipment',   0.90, -1,  9, 'Incline dumbbell — övre bröst fokus'),
(2,   109, 'equipment',   0.85, -1,  8, 'Cable crossover — konstant spänning'),
(63,  155, 'injury',      0.75, -3,  7, 'Close grip — minskar skulderbelastning'),
(107, 111, 'home_gym',    0.72, -3,  7, 'Push-ups — om hantlar saknas'),

-- RYGG regler
(3,   115, 'skill',       0.85, -2,  8, 'Sumo deadlift — bredare stance, mer glutes'),
(4,   121, 'equipment',   0.90, -1,  9, 'Lat pulldown — bra nybörjaralternativ'),
(4,   123, 'progression', 0.88,  1,  9, 'Pull-up — mer funktionell, svårare'),
(116, 117, 'equipment',   0.85, -1,  8, 'Dumbbell row — om skivstång saknas'),
(118, 68,  'equipment',   0.82, -1,  8, 'Seated cable row — om T-bar saknas'),
(68,  120, 'preference',  0.88,  0,  9, 'Cable row — liknande stimulus'),
(125, 58,  'equipment',   0.88,  0,  9, 'Roman chair — om golv saknas'),

-- BEN regler
(5,   129, 'skill',       0.78, -3,  7, 'Goblet squat — lär rörelsemönster'),
(5,   132, 'preference',  0.85, -1,  8, 'Hack squat — mer quadfokus'),
(5,   79,  'progression', 0.82,  2,  8, 'Bulgarian split — mer instabilt'),
(73,  5,   'progression', 0.88,  2,  9, 'Knäböj — mer funktionell'),
(74,  192, 'equipment',   0.92,  0,  9, 'Romanian DL dumbbells — om skivstång saknas'),
(78,  134, 'deload',      0.80, -4,  8, 'Glute bridge — lättare, mindre ländryggsbelastning'),
(78,  191, 'progression', 0.88,  2,  9, 'Single leg hip thrust — mer isolering'),
(75,  40,  'equipment',   0.85,  0,  8, 'Seated leg curl — maskin alternativ'),

-- AXLAR regler
(7,   140, 'equipment',   0.88, -1,  8, 'Seated DB press — om skivstång saknas'),
(7,   141, 'preference',  0.85, -1,  8, 'Arnold press — mer rörelseomfång'),
(142, 143, 'preference',  0.88,  0,  9, 'Cable lateral — konstant spänning'),
(145, 147, 'fatigue',     0.82, -2,  7, 'Cable reverse fly — lättare för bakre axel'),

-- ARMAR regler
(8,   154, 'preference',  0.88,  0,  9, 'Cable curl — konstant spänning hela rörelsen'),
(8,   152, 'fatigue',     0.85, -1,  8, 'Concentration curl — mer isolering'),
(9,   156, 'preference',  0.88,  0,  9, 'Tricep pushdown — konstant spänning'),
(9,   66,  'equipment',   0.82, -1,  8, 'Overhead extension — om kabel saknas'),
(155, 157, 'preference',  0.85,  0,  9, 'Skull crusher — mer isolering'),

-- MAGE regler
(10,  166, 'deload',      0.80, -3,  8, 'Plank — statisk stabilitet'),
(170, 165, 'skill',       0.88, -2,  9, 'Ab wheel — enklare än dragon flag'),
(164, 163, 'skill',       0.82, -2,  8, 'Leg raise — lättare variant'),

-- KONDITION regler
(12,  177, 'fatigue',     0.75, -3,  7, 'Mountain climbers — lättare än burpees'),
(12,  178, 'preference',  0.80,  0,  7, 'Box jumps — mer explosivitet'),
(11,  174, 'injury',      0.72, -3,  6, 'Cycling — lägre impact för knä/höft')

ON CONFLICT (source_exercise_id, target_exercise_id, substitution_reason) DO NOTHING;

-- ── ACHIEVEMENTS ──────────────────────────────────────────────
-- requirement_type: total_sessions, total_volume, streak_days,
--                   personal_record, total_distance, weight_lost
INSERT INTO achievements (name, description, icon, requirement_type, requirement_value) VALUES

-- Träningssessioner
('100 Sessions',     'Complete 100 workout sessions',    'diamond',  'total_sessions', 100),
('250 Sessions',     'Complete 250 workout sessions',    'crown',    'total_sessions', 250),
('500 Sessions',     'Complete 500 workout sessions',    'legend',   'total_sessions', 500),

-- Streaks
('3 Day Streak',     '3 consecutive training days',      'flame',    'streak_days',    3),
('14 Day Streak',    '14 consecutive training days',     'fire',     'streak_days',    14),
('60 Day Streak',    '60 day workout streak',            'inferno',  'streak_days',    60),
('100 Day Streak',   '100 day workout streak',           'legend',   'streak_days',    100),

-- Volym
('10K Club',         'Lift 10,000 kg total',             'muscle',   'total_volume',   10000),
('50K Club',         'Lift 50,000 kg total',             'star',     'total_volume',   50000),
('500K Club',        'Lift 500,000 kg total',            'diamond',  'total_volume',   500000),
('1M Club',          'Lift 1,000,000 kg total',          'legend',   'total_volume',   1000000),

-- Personal records
('PR Hunter',        'Set 5 personal records',           'trophy',   'personal_record', 5),
('PR Machine',       'Set 25 personal records',          'crown',    'personal_record', 25),
('PR Legend',        'Set 50 personal records',          'diamond',  'personal_record', 50),

-- Löpning
('First Run',        'Complete your first run',          'shoe',     'total_distance',  1),
('5K Runner',        'Run 5km total',                    'shoe',     'total_distance',  5),
('Marathon',         'Run 42.2km total',                 'medal',    'total_distance',  42.2),
('Ultra Runner',     'Run 100km total',                  'crown',    'total_distance',  100),

-- Viktnedgång
('First Kilo',       'Lose your first kilogram',         'scale',    'weight_lost',     1),
('5 Kilos Down',     'Lose 5 kilograms',                 'star',     'weight_lost',     5),
('10 Kilos Down',    'Lose 10 kilograms',                'trophy',   'weight_lost',     10)

ON CONFLICT DO NOTHING;

-- ── PROGRESSION RULES ─────────────────────────────────────────
-- condition_type: rpe_below, rpe_above, all_sets_completed,
--                 volume_increase, pr_set, consecutive_sessions
-- action_type: increase_weight, decrease_weight, increase_reps,
--              increase_sets, deload, maintain
INSERT INTO progression_rules
  (name, description, exercise_id, condition_type, condition_value,
   action_type, action_value, is_active) VALUES

-- Generella regler (exercise_id = NULL = gäller alla övningar)
('Lätt session — öka vikt',
 'RPE under 6 på alla set — öka vikten med 2.5kg',
 NULL, 'rpe_below', 6.0, 'increase_weight', 2.5, true),

('Hög RPE — minska vikt',
 'RPE över 9.5 — minska vikten med 5%',
 NULL, 'rpe_above', 9.5, 'decrease_weight', 5.0, true),

('Konsekutiv progression',
 '3 sessioner i rad utan ökning — öka reps med 1',
 NULL, 'consecutive_sessions', 3.0, 'increase_reps', 1.0, true),

('Volymsökning — lägg till set',
 'Volym ökad 10% senaste 4 veckor — lägg till ett set',
 NULL, 'volume_increase', 10.0, 'increase_sets', 1.0, true),

('PR satt — behåll vikt',
 'Personrekord satt — behåll samma vikt nästa session',
 NULL, 'pr_set', 1.0, 'maintain', 0.0, true),

-- Övningsspecifika regler
('Bänkpress — microload',
 'RPE under 7 på bänkpress — öka med 1.25kg',
 1, 'rpe_below', 7.0, 'increase_weight', 1.25, true),

('Knäböj — konservativ ökning',
 'RPE under 7 på knäböj — öka med 2.5kg',
 5, 'rpe_below', 7.0, 'increase_weight', 2.5, true),

('Marklyft — långsam progression',
 'RPE under 7 på marklyft — öka med 5kg',
 3, 'rpe_below', 7.0, 'increase_weight', 5.0, true),

('Militärpress — microload',
 'RPE under 7 på militärpress — öka med 1.25kg',
 7, 'rpe_below', 7.0, 'increase_weight', 1.25, true),

('Latsdrag — repökning',
 'Alla set klara på latsdrag — öka reps med 1',
 4, 'all_sets_completed', 1.0, 'increase_reps', 1.0, true),

('Deload vecka — minska volym',
 'Hög RPE (>8.5) 3 sessioner i rad — kör deload med 60% vikt',
 NULL, 'rpe_above', 8.5, 'deload', 40.0, true)

ON CONFLICT DO NOTHING;

-- Sammanfattning
SELECT 'exercise_substitutions'      AS tabell, COUNT(*) FROM exercise_substitutions
UNION ALL SELECT 'exercise_substitution_rules', COUNT(*) FROM exercise_substitution_rules
UNION ALL SELECT 'achievements',                COUNT(*) FROM achievements
UNION ALL SELECT 'progression_rules',           COUNT(*) FROM progression_rules
ORDER BY tabell;