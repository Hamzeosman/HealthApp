-- ============================================================
-- seed_workout_programs.sql
-- Fyller workout_programs → workout_templates → template_exercises
-- Evidensbaserade program kopplade till users mål
-- ============================================================

-- ── WORKOUT PROGRAMS ─────────────────────────────────────────
INSERT INTO workout_programs (id, name, description, difficulty, duration_weeks, days_per_week, goal) VALUES

(1, 'PPL Hypertrophy 3-dagars',
   'Push Pull Legs uppdelat på 3 dagar. Optimal för muskeltillväxt med hög volym per muskelgrupp.',
   'medel', 12, 3, 'bygga_muskler'),

(2, 'Full Body Styrka — Nybörjare',
   'Helkroppspass 3 dagar i veckan. Fokus på grundrörelser med progressiv överlast.',
   'nybörjare', 8, 3, 'bygga_muskler'),

(3, 'Fettförbränning HIIT',
   'Hög intensitet, kort vila. Kombinerar styrka och kondition för maximal fettförbränning.',
   'medel', 8, 4, 'gå_ner_i_vikt'),

(4, 'Konditionsbyggande 4-dagars',
   'Progressiv konditionsträning med löpning, rodd och cykling. Bygger aerob kapacitet.',
   'nybörjare', 10, 4, 'öka_kondition'),

(5, 'Hålla Formen — Underhåll',
   'Balanserat program för att hålla styrka och kondition. Passar den aktiva livsstilen.',
   'medel', 12, 3, 'hålla_sig_i_form'),

(6, 'Upper Lower Split',
   'Överkropp och underkropp alternerade 4 dagar. Beprövad split för styrka och hypertrofi.',
   'medel', 10, 4, 'bygga_muskler'),

(7, 'Viktminskning Styrka',
   'Styrketräning i kaloriunderskott. Bevarar muskelmassa under viktnedgång.',
   'nybörjare', 8, 3, 'gå_ner_i_vikt')

ON CONFLICT DO NOTHING;

-- ── WORKOUT TEMPLATES (pass per program) ─────────────────────
INSERT INTO workout_templates (id, program_id, name, day_of_week) VALUES

-- PPL Hypertrophy (program 1)
(1,  1, 'Push — Bröst & Axlar & Triceps', 'monday'),
(2,  1, 'Pull — Rygg & Biceps',           'wednesday'),
(3,  1, 'Legs — Ben & Mage',              'friday'),

-- Full Body Nybörjare (program 2)
(4,  2, 'Full Body A — Tyngre',           'monday'),
(5,  2, 'Full Body B — Lättare',          'wednesday'),
(6,  2, 'Full Body C — Kondition',        'friday'),

-- HIIT Fettförbränning (program 3)
(7,  3, 'HIIT Överkropp',                 'monday'),
(8,  3, 'HIIT Underkropp',                'tuesday'),
(9,  3, 'Kondition & Core',               'thursday'),
(10, 3, 'Full Body Circuit',              'friday'),

-- Kondition (program 4)
(11, 4, 'Löpning — Lång distans',         'monday'),
(12, 4, 'Intervallträning',               'wednesday'),
(13, 4, 'Rodd & Cykling',                 'friday'),
(14, 4, 'Aktiv återhämtning',             'sunday'),

-- Hålla Formen (program 5)
(15, 5, 'Styrka Överkropp',               'monday'),
(16, 5, 'Kondition & Core',               'wednesday'),
(17, 5, 'Styrka Underkropp',              'friday'),

-- Upper Lower Split (program 6)
(18, 6, 'Upper A — Styrka',               'monday'),
(19, 6, 'Lower A — Styrka',               'tuesday'),
(20, 6, 'Upper B — Volym',                'thursday'),
(21, 6, 'Lower B — Volym',               'friday'),

-- Viktminskning Styrka (program 7)
(22, 7, 'Helkropp A — Compound',          'monday'),
(23, 7, 'Kondition',                      'wednesday'),
(24, 7, 'Helkropp B — Circuit',           'friday')

ON CONFLICT DO NOTHING;

-- ── TEMPLATE EXERCISES ────────────────────────────────────────
INSERT INTO template_exercises (template_id, exercise_id, sets, reps, rest_seconds, order_index) VALUES

-- ── PUSH DAG (template 1) — Bröst, Axlar, Triceps ────────────
(1, 1,   4, 8,  180, 1),   -- Bänkpress
(1, 61,  3, 10, 120, 2),   -- Incline Bänkpress
(1, 2,   3, 12, 90,  3),   -- Hantelflyes
(1, 7,   4, 8,  180, 4),   -- Militärpress
(1, 142, 3, 15, 60,  5),   -- Lateral Raise
(1, 156, 3, 12, 90,  6),   -- Tricep Pushdown
(1, 157, 3, 10, 90,  7),   -- Skull Crusher

-- ── PULL DAG (template 2) — Rygg, Biceps ─────────────────────
(2, 3,   4, 5,  180, 1),   -- Marklyft
(2, 4,   4, 8,  120, 2),   -- Latsdrag
(2, 116, 3, 10, 120, 3),   -- Barbell Row
(2, 68,  3, 12, 90,  4),   -- Seated Cable Row
(2, 145, 3, 15, 60,  5),   -- Face Pull
(2, 8,   3, 12, 90,  6),   -- Bicepscurl
(2, 71,  3, 12, 60,  7),   -- Hammer Curl

-- ── LEGS DAG (template 3) — Ben, Mage ────────────────────────
(3, 5,   4, 8,  180, 1),   -- Knäböj
(3, 74,  3, 10, 120, 2),   -- Romanian Deadlift
(3, 73,  3, 12, 90,  3),   -- Leg Press
(3, 78,  3, 12, 90,  4),   -- Hip Thrust
(3, 75,  3, 12, 60,  5),   -- Leg Curl
(3, 77,  3, 15, 60,  6),   -- Calf Raises
(3, 166, 3, 60, 60,  7),   -- Plank (sek)
(3, 162, 3, 15, 60,  8),   -- Bicycle Crunch

-- ── FULL BODY A — Tyngre (template 4) ────────────────────────
(4, 5,   3, 5,  180, 1),   -- Knäböj
(4, 1,   3, 5,  180, 2),   -- Bänkpress
(4, 3,   3, 5,  180, 3),   -- Marklyft
(4, 7,   3, 8,  120, 4),   -- Militärpress
(4, 4,   3, 8,  120, 5),   -- Latsdrag
(4, 166, 3, 30, 60,  6),   -- Plank

-- ── FULL BODY B — Lättare (template 5) ───────────────────────
(5, 129, 3, 12, 90,  1),   -- Goblet Squat
(5, 107, 3, 12, 90,  2),   -- Dumbbell Bench Press
(5, 117, 3, 12, 90,  3),   -- Dumbbell Row
(5, 140, 3, 12, 90,  4),   -- Seated Dumbbell Press
(5, 151, 3, 12, 60,  5),   -- Dumbbell Curl
(5, 158, 3, 12, 60,  6),   -- Tricep Kickback
(5, 134, 3, 15, 60,  7),   -- Glute Bridge

-- ── FULL BODY C — Kondition (template 6) ─────────────────────
(6, 12,  3, 10, 60,  1),   -- Burpees
(6, 111, 3, 15, 60,  2),   -- Push-ups
(6, 123, 3, 8,  90,  3),   -- Pull-up
(6, 127, 3, 12, 90,  4),   -- Back Squat
(6, 177, 3, 20, 45,  5),   -- Mountain Climbers
(6, 162, 3, 15, 45,  6),   -- Bicycle Crunch

-- ── HIIT ÖVERKROPP (template 7) ──────────────────────────────
(7, 111, 4, 15, 45,  1),   -- Push-ups
(7, 123, 4, 8,  45,  2),   -- Pull-up
(7, 113, 3, 12, 45,  3),   -- Diamond Push-ups
(7, 63,  3, 10, 60,  4),   -- Dips
(7, 145, 3, 15, 45,  5),   -- Face Pull
(7, 177, 3, 20, 30,  6),   -- Mountain Climbers

-- ── HIIT UNDERKROPP (template 8) ─────────────────────────────
(8, 137, 4, 8,  60,  1),   -- Box Jump
(8, 78,  4, 12, 60,  2),   -- Hip Thrust
(8, 79,  3, 10, 60,  3),   -- Bulgarian Split Squat
(8, 184, 3, 15, 45,  4),   -- Donkey Kicks
(8, 185, 3, 15, 45,  5),   -- Fire Hydrants
(8, 77,  3, 20, 45,  6),   -- Calf Raises

-- ── KONDITION & CORE (template 9) ────────────────────────────
(9, 11,  1, 20, 60,  1),   -- Löpning (20 min)
(9, 166, 3, 45, 45,  2),   -- Plank
(9, 167, 3, 30, 45,  3),   -- Side Plank
(9, 168, 3, 20, 45,  4),   -- Russian Twist
(9, 171, 3, 10, 45,  5),   -- Dead Bug

-- ── FULL BODY CIRCUIT (template 10) ──────────────────────────
(10, 12,  4, 10, 30,  1),  -- Burpees
(10, 111, 4, 15, 30,  2),  -- Push-ups
(10, 123, 4, 6,  30,  3),  -- Pull-up
(10, 127, 4, 12, 30,  4),  -- Back Squat
(10, 78,  4, 12, 30,  5),  -- Hip Thrust
(10, 177, 4, 20, 30,  6),  -- Mountain Climbers

-- ── LÖPNING LÅNG DISTANS (template 11) ───────────────────────
(11, 11,  1, 40, 0,   1),  -- Löpning 40 min
(11, 173, 1, 10, 0,   2),  -- Running intervals

-- ── INTERVALLTRÄNING (template 12) ───────────────────────────
(12, 173, 6, 5,  120, 1),  -- Running intervals 6x5 min
(12, 176, 3, 60, 60,  2),  -- Jump Rope
(12, 177, 3, 20, 45,  3),  -- Mountain Climbers

-- ── RODD & CYKLING (template 13) ─────────────────────────────
(13, 175, 1, 30, 0,   1),  -- Rowing 30 min
(13, 174, 1, 20, 0,   2),  -- Cycling 20 min

-- ── AKTIV ÅTERHÄMTNING (template 14) ─────────────────────────
(14, 96,  1, 60, 0,   1),  -- Pigeon Pose
(14, 93,  1, 60, 0,   2),  -- Child's Pose
(14, 92,  1, 60, 0,   3),  -- Downward Dog
(14, 206, 1, 60, 0,   4),  -- Supine Spinal Twist

-- ── STYRKA ÖVERKROPP (template 15) ───────────────────────────
(15, 1,   3, 8,  150, 1),  -- Bänkpress
(15, 4,   3, 8,  150, 2),  -- Latsdrag
(15, 7,   3, 10, 120, 3),  -- Militärpress
(15, 68,  3, 10, 90,  4),  -- Seated Cable Row
(15, 8,   3, 12, 60,  5),  -- Bicepscurl
(15, 9,   3, 12, 60,  6),  -- Tricepspress

-- ── KONDITION & CORE (template 16) ───────────────────────────
(16, 11,  1, 25, 0,   1),  -- Löpning 25 min
(16, 166, 3, 45, 45,  2),  -- Plank
(16, 162, 3, 15, 45,  3),  -- Bicycle Crunch
(16, 168, 3, 15, 45,  4),  -- Russian Twist

-- ── STYRKA UNDERKROPP (template 17) ──────────────────────────
(17, 5,   3, 8,  150, 1),  -- Knäböj
(17, 74,  3, 10, 120, 2),  -- Romanian Deadlift
(17, 73,  3, 12, 90,  3),  -- Leg Press
(17, 78,  3, 12, 90,  4),  -- Hip Thrust
(17, 77,  3, 15, 60,  5),  -- Calf Raises

-- ── UPPER A — STYRKA (template 18) ───────────────────────────
(18, 1,   4, 5,  180, 1),  -- Bänkpress
(18, 116, 4, 5,  180, 2),  -- Barbell Row
(18, 7,   3, 6,  150, 3),  -- Militärpress
(18, 123, 3, 6,  150, 4),  -- Pull-up
(18, 155, 3, 8,  120, 5),  -- Close Grip Bench Press
(18, 150, 3, 8,  90,  6),  -- Barbell Curl

-- ── LOWER A — STYRKA (template 19) ───────────────────────────
(19, 5,   4, 5,  180, 1),  -- Knäböj
(19, 3,   4, 5,  180, 2),  -- Marklyft
(19, 133, 3, 6,  150, 3),  -- Nordic Hamstring Curl
(19, 135, 3, 10, 90,  4),  -- Standing Calf Raise
(19, 166, 3, 45, 60,  5),  -- Plank

-- ── UPPER B — VOLYM (template 20) ────────────────────────────
(20, 108, 4, 10, 90,  1),  -- Incline Dumbbell Press
(20, 117, 4, 10, 90,  2),  -- Dumbbell Row
(20, 140, 3, 12, 75,  3),  -- Seated Dumbbell Press
(20, 145, 3, 15, 60,  4),  -- Face Pull
(20, 154, 3, 12, 60,  5),  -- Cable Curl
(20, 156, 3, 12, 60,  6),  -- Tricep Pushdown

-- ── LOWER B — VOLYM (template 21) ────────────────────────────
(21, 79,  4, 10, 90,  1),  -- Bulgarian Split Squat
(21, 74,  4, 10, 90,  2),  -- Romanian Deadlift
(21, 73,  3, 12, 75,  3),  -- Leg Press
(21, 78,  3, 12, 75,  4),  -- Hip Thrust
(21, 75,  3, 15, 60,  5),  -- Leg Curl
(21, 136, 3, 15, 60,  6),  -- Seated Calf Raise

-- ── HELKROPP A — COMPOUND (template 22) ──────────────────────
(22, 5,   3, 8,  150, 1),  -- Knäböj
(22, 1,   3, 8,  150, 2),  -- Bänkpress
(22, 4,   3, 8,  120, 3),  -- Latsdrag
(22, 7,   3, 10, 120, 4),  -- Militärpress
(22, 166, 3, 30, 60,  5),  -- Plank

-- ── KONDITION (template 23) ───────────────────────────────────
(23, 11,  1, 30, 0,   1),  -- Löpning 30 min
(23, 176, 3, 60, 60,  2),  -- Jump Rope
(23, 177, 3, 20, 45,  3),  -- Mountain Climbers

-- ── HELKROPP B — CIRCUIT (template 24) ───────────────────────
(24, 129, 3, 12, 60,  1),  -- Goblet Squat
(24, 111, 3, 15, 45,  2),  -- Push-ups
(24, 117, 3, 12, 60,  3),  -- Dumbbell Row
(24, 134, 3, 15, 45,  4),  -- Glute Bridge
(24, 162, 3, 15, 45,  5),  -- Bicycle Crunch
(24, 12,  3, 8,  60,  6)   -- Burpees

ON CONFLICT DO NOTHING;

-- Sammanfattning
SELECT
  wp.name AS program,
  wp.goal,
  wp.difficulty,
  COUNT(DISTINCT wt.id) AS antal_pass,
  COUNT(te.id) AS totala_övningar
FROM workout_programs wp
LEFT JOIN workout_templates wt ON wp.id = wt.program_id
LEFT JOIN template_exercises te ON wt.id = te.template_id
GROUP BY wp.id, wp.name, wp.goal, wp.difficulty
ORDER BY wp.id;