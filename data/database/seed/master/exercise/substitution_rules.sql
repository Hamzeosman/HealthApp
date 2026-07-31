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

