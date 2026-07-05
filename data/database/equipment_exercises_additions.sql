-- ============================================================
-- equipment_exercises_additions.sql
-- Kopplar övningar som saknade utrustning (67 st)
-- ============================================================

INSERT INTO equipment_exercises (equipment_id, exercise_id, is_primary, difficulty, notes) VALUES

-- ── ARMAR (saknar utrustning) ─────────────────────────────────
-- Bicepscurl (8) → Hantlar, Skivstång, Kabelmaskin
(2,  8,   true,  'beginner',     'Hantelcurl, klassisk bicepsövning'),
(3,  8,   true,  'beginner',     'Skivstångscurl'),
(4,  8,   true,  'beginner',     'Kabelcurl'),

-- Tricepspress (9) → Kabelmaskin, Hantlar
(4,  9,   true,  'beginner',     'Tricep pushdown på kabel'),
(2,  9,   true,  'beginner',     'Overhead tricep extension med hantel'),

-- Preacher Curl (153) → EZ-Curl Bar, Hantlar
(74, 153, true,  'intermediate', 'Preacher curl med EZ-stång'),
(2,  153, true,  'beginner',     'Preacher curl med hantel'),

-- Wrist Curl (159) → EZ-Curl Bar, Hantlar
(74, 159, true,  'beginner',     'Wrist curl för underarmar'),
(2,  159, true,  'beginner',     'Hantel wrist curl'),

-- Reverse Wrist Curl (160) → EZ-Curl Bar, Hantlar
(74, 160, true,  'beginner',     'Reverse wrist curl'),
(2,  160, true,  'beginner',     'Hantel reverse wrist curl'),

-- Stretch-övningar armar → Kroppsvikt / Resistansband
(1,  197, false, 'beginner',     'Bicep wall stretch, kroppsvikt'),
(1,  196, false, 'beginner',     'Overhead tricep stretch, kroppsvikt'),
(1,  202, false, 'beginner',     'Wrist extensor stretch'),
(1,  201, false, 'beginner',     'Wrist flexor stretch'),

-- ── AXLAR (saknar utrustning) ─────────────────────────────────
-- Face Pulls (69) → Kabelmaskin, Cable Crossover
(4,  69,  true,  'beginner',     'Face pulls på kabelmaskin'),
(59, 69,  true,  'beginner',     'Face pulls på cable crossover'),

-- Lateral Raises (64) → Hantlar
(2,  64,  true,  'beginner',     'Lateral raises med hantlar'),

-- Cross-Body Shoulder Stretch (195) → Kroppsvikt
(1,  195, false, 'beginner',     'Cross-body shoulder stretch'),

-- ── BEN (saknar utrustning) ───────────────────────────────────
-- Box Jump (137) → Kroppsvikt
(1,  137, true,  'intermediate', 'Box jump, explosiv benstyrka'),

-- Bulgarian Split Squat (79) → Hantlar, Skivstång, Kroppsvikt
(2,  79,  true,  'intermediate', 'Bulgarian split squat med hantlar'),
(3,  79,  true,  'advanced',     'Bulgarian split squat med skivstång'),
(1,  79,  true,  'intermediate', 'Bulgarian split squat kroppsvikt'),

-- Curtsy Lunge (187) → Hantlar, Kroppsvikt
(2,  187, true,  'beginner',     'Curtsy lunge med hantlar'),
(1,  187, true,  'beginner',     'Curtsy lunge kroppsvikt'),

-- Donkey Kicks (184) → Kroppsvikt, Resistansband
(1,  184, true,  'beginner',     'Donkey kicks kroppsvikt'),
(5,  184, true,  'beginner',     'Donkey kicks med band'),

-- Fire Hydrants (185) → Kroppsvikt, Resistansband
(1,  185, true,  'beginner',     'Fire hydrants kroppsvikt'),
(5,  185, true,  'beginner',     'Fire hydrants med band'),

-- Frog Pump (190) → Kroppsvikt, Resistansband
(1,  190, true,  'beginner',     'Frog pump kroppsvikt'),
(5,  190, true,  'beginner',     'Frog pump med band'),

-- Reverse Lunge (131) → Hantlar, Skivstång, Kroppsvikt
(2,  131, true,  'beginner',     'Reverse lunge med hantlar'),
(3,  131, true,  'intermediate', 'Reverse lunge med skivstång'),
(1,  131, true,  'beginner',     'Reverse lunge kroppsvikt'),

-- Single Leg Hip Thrust (191) → Kroppsvikt, Skivstång
(1,  191, true,  'intermediate', 'Single leg hip thrust kroppsvikt'),
(3,  191, true,  'advanced',     'Single leg hip thrust med skivstång'),

-- Sumo Squat (186) → Hantlar, Kettlebell, Kroppsvikt
(2,  186, true,  'beginner',     'Sumo squat med hantel'),
(6,  186, true,  'beginner',     'Sumo squat med kettlebell'),
(1,  186, true,  'beginner',     'Sumo squat kroppsvikt'),

-- Incline Bänkpress (61) → Skivstång, Hantlar
(3,  61,  true,  'intermediate', 'Incline bänkpress med skivstång'),
(2,  61,  true,  'beginner',     'Incline bänkpress med hantlar'),

-- Stretch-övningar ben → Kroppsvikt / Foam Roller
(1,  216, false, 'beginner',     'Butterfly stretch'),
(1,  217, false, 'beginner',     'Calf stretch mot vägg'),
(1,  226, false, 'beginner',     'Couch stretch'),
(1,  220, false, 'beginner',     'Deep squat hold'),
(1,  215, false, 'beginner',     'Figure four stretch'),
(1,  221, false, 'beginner',     'Glute kickback stretch'),
(1,  219, false, 'beginner',     'Hip circle stretch'),
(1,  213, false, 'beginner',     'Hip flexor lunge stretch'),
(1,  222, false, 'beginner',     'Inner thigh stretch'),
(1,  223, false, 'beginner',     'Lying glute stretch'),
(1,  212, false, 'beginner',     'Lying hamstring stretch'),
(1,  209, false, 'beginner',     'Lying quad stretch'),
(1,  227, false, 'beginner',     'Pancake stretch'),
(1,  96,  false, 'beginner',     'Pigeon pose'),
(1,  214, false, 'beginner',     'Pigeon pose hip stretch'),
(1,  98,  false, 'beginner',     'Seated forward fold'),
(1,  211, false, 'beginner',     'Seated hamstring stretch'),
(1,  218, false, 'beginner',     'Soleus stretch'),
(1,  210, false, 'beginner',     'Standing hamstring stretch'),
(1,  208, false, 'beginner',     'Standing quad stretch'),
(1,  102, false, 'beginner',     'Tree pose'),
(1,  99,  false, 'beginner',     'Bridge pose'),
(1,  94,  false, 'beginner',     'Warrior I'),
(1,  95,  false, 'beginner',     'Warrior II'),
(73, 212, false, 'beginner',     'Foam roller hamstrings'),
(73, 209, false, 'beginner',     'Foam roller quads'),
(73, 223, false, 'beginner',     'Foam roller glutes'),

-- ── BRÖST (saknar utrustning) ─────────────────────────────────
(1,  194, false, 'beginner',     'Chest doorway stretch'),
(1,  103, false, 'beginner',     'Cobra pose'),
(1,  224, false, 'beginner',     'Pec minor stretch'),

-- ── KONDITION (saknar utrustning) ────────────────────────────
-- Box Jumps (178) → Kroppsvikt
(1,  178, true,  'intermediate', 'Box jumps, explosivitet'),
-- Jump Rope (176) → Kroppsvikt
(1,  176, true,  'beginner',     'Hopprep, kondition'),

-- ── MAGE (saknar utrustning) ──────────────────────────────────
(1,  97,  false, 'beginner',     'Cat-cow, rörlighet'),
(1,  93,  false, 'beginner',     'Child''s pose'),
(1,  92,  false, 'beginner',     'Downward dog'),
(1,  101, false, 'beginner',     'Mountain pose'),
(1,  198, false, 'beginner',     'Neck side stretch'),
(1,  10,  true,  'beginner',     'Plankan, kroppsvikt'),
(1,  100, false, 'beginner',     'Supine twist'),
(73, 100, false, 'beginner',     'Foam roller rygg'),

-- ── RYGG (saknar utrustning) ──────────────────────────────────
(1,  204, false, 'beginner',     'Cat-cow stretch'),
(1,  203, false, 'beginner',     'Child''s pose extended'),
(1,  207, false, 'beginner',     'Cobra stretch'),
(3,  225, true,  'advanced',     'Jefferson curl med skivstång'),
(1,  205, false, 'beginner',     'Knees to chest'),
(5,  200, false, 'beginner',     'Lat stretch med band'),
(69, 72,  true,  'intermediate', 'Pull-ups på pull-up bar'),
(68, 72,  true,  'intermediate', 'Pull-ups på power rack'),
(1,  206, false, 'beginner',     'Supine spinal twist'),
(1,  199, false, 'beginner',     'Thoracic spine rotation'),
(73, 204, false, 'beginner',     'Foam roller övre rygg')

ON CONFLICT (equipment_id, exercise_id) DO NOTHING;

-- ── FOAM ROLLER (73) extra övningar ───────────────────────────
INSERT INTO equipment_exercises (equipment_id, exercise_id, is_primary, difficulty, notes) VALUES
(73, 96,  false, 'beginner',     'Foam roller höfter'),
(73, 77,  false, 'beginner',     'Foam roller vader')
ON CONFLICT (equipment_id, exercise_id) DO NOTHING;

-- Sammanfattning efter tillägg
SELECT
  e.name AS utrustning,
  COUNT(ee.exercise_id) AS total_övningar
FROM equipment e
JOIN equipment_exercises ee ON e.id = ee.equipment_id
GROUP BY e.name
ORDER BY total_övningar DESC;