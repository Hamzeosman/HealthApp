-- ============================================================
-- migration_p6_exercise_metadata.sql
-- Lägger till metadata-kolumner på exercises och fyller data
-- Baserat på feedback: coach_priority, spotter, warmup etc
-- ============================================================

-- ── Nya kolumner ──────────────────────────────────────────────
ALTER TABLE exercises
  ADD COLUMN IF NOT EXISTS requires_spotter        BOOLEAN DEFAULT false,
  ADD COLUMN IF NOT EXISTS warmup_required         BOOLEAN DEFAULT false,
  ADD COLUMN IF NOT EXISTS coach_priority          INTEGER DEFAULT 5,
  ADD COLUMN IF NOT EXISTS is_beginner_friendly    BOOLEAN DEFAULT false,
  ADD COLUMN IF NOT EXISTS estimated_duration_minutes INTEGER;

-- ── primary_muscle för alla övningar ─────────────────────────
UPDATE exercises SET primary_muscle = 'Quadriceps',    is_compound = true,  is_beginner_friendly = true  WHERE name = 'Knäböj';
UPDATE exercises SET primary_muscle = 'Hamstrings',    is_compound = true,  is_beginner_friendly = false WHERE name = 'Marklyft';
UPDATE exercises SET primary_muscle = 'Mid Chest',     is_compound = true,  is_beginner_friendly = true  WHERE name = 'Bänkpress';
UPDATE exercises SET primary_muscle = 'Lats',          is_compound = true,  is_beginner_friendly = true  WHERE name = 'Latsdrag';
UPDATE exercises SET primary_muscle = 'Shoulders',     is_compound = true,  is_beginner_friendly = true  WHERE name = 'Militärpress';
UPDATE exercises SET primary_muscle = 'Biceps',        is_compound = false, is_beginner_friendly = true  WHERE name = 'Bicepscurl';
UPDATE exercises SET primary_muscle = 'Triceps',       is_compound = false, is_beginner_friendly = true  WHERE name = 'Tricepspress';
UPDATE exercises SET primary_muscle = 'Core',          is_compound = false, is_beginner_friendly = true  WHERE name = 'Plankan';
UPDATE exercises SET primary_muscle = 'Quadriceps',    is_compound = true,  is_beginner_friendly = true  WHERE name = 'Utfall';
UPDATE exercises SET primary_muscle = 'Full Body',     is_compound = true,  is_beginner_friendly = false WHERE name = 'Burpees';
UPDATE exercises SET primary_muscle = 'Cardiovascular',is_compound = true,  is_beginner_friendly = true  WHERE name = 'Löpning';
UPDATE exercises SET primary_muscle = 'Mid Chest',     is_compound = false, is_beginner_friendly = true  WHERE name = 'Hantelflyes';
UPDATE exercises SET primary_muscle = 'Quadriceps',    is_compound = true,  is_beginner_friendly = true  WHERE name = 'Leg Press';
UPDATE exercises SET primary_muscle = 'Hamstrings',    is_compound = false, is_beginner_friendly = true  WHERE name = 'Leg Curl';
UPDATE exercises SET primary_muscle = 'Quadriceps',    is_compound = false, is_beginner_friendly = true  WHERE name = 'Leg Extension';
UPDATE exercises SET primary_muscle = 'Calves',        is_compound = false, is_beginner_friendly = true  WHERE name = 'Calf Raises';
UPDATE exercises SET primary_muscle = 'Glutes',        is_compound = true,  is_beginner_friendly = true  WHERE name = 'Hip Thrust';
UPDATE exercises SET primary_muscle = 'Upper Chest',   is_compound = true,  is_beginner_friendly = true  WHERE name = 'Incline Bänkpress';
UPDATE exercises SET primary_muscle = 'Lats',          is_compound = true,  is_beginner_friendly = false WHERE name = 'Pull-ups';
UPDATE exercises SET primary_muscle = 'Hamstrings',    is_compound = true,  is_beginner_friendly = true  WHERE name = 'Romanian Deadlift';
UPDATE exercises SET primary_muscle = 'Lats',          is_compound = true,  is_beginner_friendly = true  WHERE name = 'Seated Cable Row';
UPDATE exercises SET primary_muscle = 'Shoulders',     is_compound = false, is_beginner_friendly = true  WHERE name = 'Lateral Raises';
UPDATE exercises SET primary_muscle = 'Shoulders',     is_compound = false, is_beginner_friendly = true  WHERE name = 'Front Raises';
UPDATE exercises SET primary_muscle = 'Rear Deltoids', is_compound = false, is_beginner_friendly = true  WHERE name = 'Face Pulls';
UPDATE exercises SET primary_muscle = 'Biceps',        is_compound = false, is_beginner_friendly = true  WHERE name = 'Hammer Curl';
UPDATE exercises SET primary_muscle = 'Biceps',        is_compound = false, is_beginner_friendly = true  WHERE name = 'Incline Dumbbell Curl';
UPDATE exercises SET primary_muscle = 'Triceps',       is_compound = false, is_beginner_friendly = true  WHERE name = 'Skull Crushers';
UPDATE exercises SET primary_muscle = 'Triceps',       is_compound = false, is_beginner_friendly = true  WHERE name = 'Overhead Tricep Extension';
UPDATE exercises SET primary_muscle = 'Core',          is_compound = false, is_beginner_friendly = true  WHERE name = 'Bicycle Crunch';
UPDATE exercises SET primary_muscle = 'Core',          is_compound = false, is_beginner_friendly = true  WHERE name = 'Crunch';
UPDATE exercises SET primary_muscle = 'Core',          is_compound = false, is_beginner_friendly = false WHERE name = 'Hanging Leg Raise';
UPDATE exercises SET primary_muscle = 'Core',          is_compound = false, is_beginner_friendly = true  WHERE name = 'Russian Twist';
UPDATE exercises SET primary_muscle = 'Full Body',     is_compound = true,  is_beginner_friendly = false WHERE name = 'Mountain Climbers';
UPDATE exercises SET primary_muscle = 'Cardiovascular',is_compound = true,  is_beginner_friendly = true  WHERE name = 'Rowing';
UPDATE exercises SET primary_muscle = 'Cardiovascular',is_compound = true,  is_beginner_friendly = true  WHERE name = 'Cycling';
UPDATE exercises SET primary_muscle = 'Full Body',     is_compound = true,  is_beginner_friendly = false WHERE name = 'Battle Ropes';
UPDATE exercises SET primary_muscle = 'Full Body',     is_compound = true,  is_beginner_friendly = false WHERE name = 'Sled Push';
UPDATE exercises SET primary_muscle = 'Full Body',     is_compound = true,  is_beginner_friendly = false WHERE name = 'Box Jumps';
UPDATE exercises SET primary_muscle = 'Core',          is_compound = true,  is_beginner_friendly = true  WHERE name = 'Jump Rope';
UPDATE exercises SET primary_muscle = 'Grip/Forearms', is_compound = true,  is_beginner_friendly = false WHERE name = 'Farmer''s Walk';
UPDATE exercises SET primary_muscle = 'Flexibility',   is_compound = false, is_beginner_friendly = true  WHERE name IN ('Cat-Cow', 'Child''s Pose', 'Downward Dog');
UPDATE exercises SET primary_muscle = 'Mid Chest',     is_compound = false, is_beginner_friendly = true  WHERE name = 'Cable Flyes';
UPDATE exercises SET primary_muscle = 'Chest/Spine',   is_compound = false, is_beginner_friendly = true  WHERE name = 'Cobra Pose';
UPDATE exercises SET primary_muscle = 'Triceps',       is_compound = true,  is_beginner_friendly = false WHERE name = 'Dips';
UPDATE exercises SET primary_muscle = 'Glutes',        is_compound = false, is_beginner_friendly = true  WHERE name = 'Bridge Pose';
UPDATE exercises SET primary_muscle = 'Quadriceps',    is_compound = true,  is_beginner_friendly = false WHERE name = 'Bulgarian Split Squat';
UPDATE exercises SET primary_muscle = 'Hip Flexors',   is_compound = false, is_beginner_friendly = true  WHERE name = 'Pigeon Pose';
UPDATE exercises SET primary_muscle = 'Hamstrings',    is_compound = false, is_beginner_friendly = true  WHERE name = 'Seated Forward Fold';
UPDATE exercises SET primary_muscle = 'Balance',       is_compound = false, is_beginner_friendly = true  WHERE name = 'Tree Pose';
UPDATE exercises SET primary_muscle = 'Hip Flexors',   is_compound = false, is_beginner_friendly = true  WHERE name = 'Warrior I';
UPDATE exercises SET primary_muscle = 'Hip Abductors', is_compound = false, is_beginner_friendly = true  WHERE name = 'Warrior II';
UPDATE exercises SET primary_muscle = 'Posture',       is_compound = false, is_beginner_friendly = true  WHERE name = 'Mountain Pose';
UPDATE exercises SET primary_muscle = 'Spine',         is_compound = false, is_beginner_friendly = true  WHERE name = 'Supine Twist';

-- ── requires_spotter ──────────────────────────────────────────
UPDATE exercises SET requires_spotter = true, coach_priority = 10, warmup_required = true
WHERE name IN (
  'Bänkpress', 'Knäböj', 'Marklyft', 'Militärpress',
  'Flat Barbell Bench Press', 'Incline Barbell Bench Press'
);

-- ── warmup_required ───────────────────────────────────────────
UPDATE exercises SET warmup_required = true
WHERE systemic_fatigue >= 7 OR spinal_load >= 7;

-- ── coach_priority ────────────────────────────────────────────
UPDATE exercises SET coach_priority = 10 WHERE is_compound = true  AND systemic_fatigue >= 8;
UPDATE exercises SET coach_priority = 8  WHERE is_compound = true  AND systemic_fatigue >= 5;
UPDATE exercises SET coach_priority = 5  WHERE is_compound = false;
UPDATE exercises SET coach_priority = 3  WHERE exercise_type = 'stretching';

-- ── estimated_duration_minutes ────────────────────────────────
UPDATE exercises SET estimated_duration_minutes = 15 WHERE exercise_type = 'stretching';
UPDATE exercises SET estimated_duration_minutes = 5  WHERE exercise_type = 'kondition' AND is_compound = false;
UPDATE exercises SET estimated_duration_minutes = 8  WHERE exercise_type = 'styrka'    AND is_compound = false;
UPDATE exercises SET estimated_duration_minutes = 12 WHERE exercise_type = 'styrka'    AND is_compound = true;

-- Verifiera
SELECT
  COUNT(*) FILTER (WHERE primary_muscle IS NULL)      AS saknar_primary_muscle,
  COUNT(*) FILTER (WHERE requires_spotter = true)     AS kräver_spotter,
  COUNT(*) FILTER (WHERE warmup_required = true)      AS kräver_uppvärmning,
  COUNT(*) FILTER (WHERE is_beginner_friendly = true) AS nybörjarvänlig,
  COUNT(*) FILTER (WHERE coach_priority = 10)         AS hög_prioritet
FROM exercises;