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

