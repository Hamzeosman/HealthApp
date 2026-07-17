-- ============================================================
-- seed_machine_muscles.sql
-- Vilka muskler varje maskin/utrustning aktiverar
-- engagement_level 1-5 (5 = primär, 1 = minimal aktivering)
-- ============================================================

INSERT INTO machine_muscles (equipment_id, muscle_name, is_primary, engagement_level) VALUES

-- ── LEG PRESS MACHINE (37) ───────────────────────────────────
(37, 'Quadriceps',   true,  5),
(37, 'Glutes',       true,  4),
(37, 'Hamstrings',   false, 3),
(37, 'Calves',       false, 1),

-- ── LEG EXTENSION MACHINE (38) ───────────────────────────────
(38, 'Quadriceps',   true,  5),

-- ── LEG CURL MACHINE (39) ────────────────────────────────────
(39, 'Hamstrings',   true,  5),
(39, 'Calves',       false, 2),

-- ── SEATED LEG CURL MACHINE (40) ─────────────────────────────
(40, 'Hamstrings',   true,  5),
(40, 'Calves',       false, 1),

-- ── HIP ABDUCTION MACHINE (41) ───────────────────────────────
(41, 'Glutes',       true,  4),
(41, 'Hip Abductors', true, 5),

-- ── HIP ADDUCTION MACHINE (42) ───────────────────────────────
(42, 'Hip Adductors', true, 5),
(42, 'Glutes',        false, 2),

-- ── CALF RAISE MACHINE (43) ──────────────────────────────────
(43, 'Calves',       true,  5),
(43, 'Soleus',       false, 3),

-- ── SEATED CALF RAISE MACHINE (44) ───────────────────────────
(44, 'Soleus',       true,  5),
(44, 'Calves',       false, 3),

-- ── HACK SQUAT MACHINE (45) ──────────────────────────────────
(45, 'Quadriceps',   true,  5),
(45, 'Glutes',       true,  3),
(45, 'Hamstrings',   false, 2),
(45, 'Calves',       false, 1),

-- ── SMITH MACHINE (46) ───────────────────────────────────────
(46, 'Quadriceps',   true,  4),
(46, 'Glutes',       true,  4),
(46, 'Hamstrings',   false, 2),
(46, 'Chest',        false, 3),
(46, 'Shoulders',    false, 3),
(46, 'Triceps',      false, 2),

-- ── GLUTE KICKBACK MACHINE (47) ──────────────────────────────
(47, 'Glutes',       true,  5),
(47, 'Hamstrings',   false, 2),

-- ── LAT PULLDOWN MACHINE (48) ────────────────────────────────
(48, 'Lats',         true,  5),
(48, 'Biceps',       false, 4),
(48, 'Rear Deltoids', false, 2),
(48, 'Rhomboids',    false, 3),

-- ── SEATED ROW MACHINE (49) ──────────────────────────────────
(49, 'Lats',         true,  4),
(49, 'Rhomboids',    true,  5),
(49, 'Biceps',       false, 3),
(49, 'Rear Deltoids', false, 3),
(49, 'Traps',        false, 2),

-- ── T-BAR ROW MACHINE (50) ───────────────────────────────────
(50, 'Lats',         true,  5),
(50, 'Rhomboids',    true,  4),
(50, 'Biceps',       false, 3),
(50, 'Rear Deltoids', false, 2),
(50, 'Traps',        false, 3),

-- ── PULLOVER MACHINE (51) ────────────────────────────────────
(51, 'Lats',         true,  5),
(51, 'Triceps',      false, 2),
(51, 'Chest',        false, 2),

-- ── BÄNKPRESSMASKIN (52) ─────────────────────────────────────
(52, 'Chest',        true,  5),
(52, 'Triceps',      false, 3),
(52, 'Shoulders',    false, 2),

-- ── SHOULDER PRESS MACHINE (53) ──────────────────────────────
(53, 'Shoulders',    true,  5),
(53, 'Triceps',      false, 3),
(53, 'Traps',        false, 2),

-- ── PEC DECK / CHEST FLY MACHINE (54) ────────────────────────
(54, 'Chest',        true,  5),
(54, 'Front Deltoids', false, 2),

-- ── INCLINE PRESS MACHINE (55) ───────────────────────────────
(55, 'Upper Chest',  true,  5),
(55, 'Shoulders',    false, 3),
(55, 'Triceps',      false, 3),

-- ── AB CRUNCH MACHINE (56) ───────────────────────────────────
(56, 'Rectus Abdominis', true, 5),
(56, 'Obliques',     false, 2),

-- ── CAPTAIN CHAIR / DIP STATION (57) ─────────────────────────
(57, 'Rectus Abdominis', true, 5),
(57, 'Hip Flexors',  true,  4),
(57, 'Obliques',     false, 3),
(57, 'Triceps',      false, 3),
(57, 'Chest',        false, 2),

-- ── ROMAN CHAIR / BACK EXTENSION (58) ────────────────────────
(58, 'Erector Spinae', true, 5),
(58, 'Glutes',       false, 3),
(58, 'Hamstrings',   false, 3),

-- ── CABLE CROSSOVER (59) ─────────────────────────────────────
(59, 'Chest',        true,  5),
(59, 'Front Deltoids', false, 3),
(59, 'Rear Deltoids', false, 3),
(59, 'Biceps',       false, 2),
(59, 'Lats',         false, 2),

-- ── FUNCTIONAL TRAINER (60) ──────────────────────────────────
(60, 'Chest',        true,  4),
(60, 'Lats',         true,  4),
(60, 'Shoulders',    false, 3),
(60, 'Core',         false, 3),
(60, 'Glutes',       false, 2),

-- ── LÖPBAND (61) ─────────────────────────────────────────────
(61, 'Quadriceps',   true,  4),
(61, 'Hamstrings',   true,  4),
(61, 'Calves',       false, 3),
(61, 'Glutes',       false, 3),
(61, 'Core',         false, 2),

-- ── CROSSTRAINER (62) ────────────────────────────────────────
(62, 'Quadriceps',   true,  4),
(62, 'Hamstrings',   false, 3),
(62, 'Glutes',       false, 3),
(62, 'Core',         false, 2),
(62, 'Upper Back',   false, 2),

-- ── MOTIONSCYKEL (63) ────────────────────────────────────────
(63, 'Quadriceps',   true,  5),
(63, 'Hamstrings',   false, 3),
(63, 'Glutes',       false, 3),
(63, 'Calves',       false, 2),

-- ── RODDMASKIN (64) ──────────────────────────────────────────
(64, 'Lats',         true,  5),
(64, 'Rhomboids',    true,  4),
(64, 'Biceps',       false, 4),
(64, 'Quadriceps',   false, 3),
(64, 'Hamstrings',   false, 3),
(64, 'Core',         false, 3),

-- ── STAIRCLIMBER (65) ────────────────────────────────────────
(65, 'Quadriceps',   true,  4),
(65, 'Glutes',       true,  5),
(65, 'Hamstrings',   false, 3),
(65, 'Calves',       false, 3),

-- ── AIR BIKE (66) ────────────────────────────────────────────
(66, 'Quadriceps',   true,  4),
(66, 'Hamstrings',   false, 3),
(66, 'Shoulders',    false, 3),
(66, 'Triceps',      false, 2),
(66, 'Core',         false, 3),

-- ── RODDMASKIN / SKI ERG (67) ────────────────────────────────
(67, 'Lats',         true,  5),
(67, 'Core',         true,  4),
(67, 'Shoulders',    false, 3),
(67, 'Triceps',      false, 2),

-- ── POWER RACK (68) ──────────────────────────────────────────
(68, 'Quadriceps',   true,  5),
(68, 'Glutes',       true,  4),
(68, 'Hamstrings',   false, 3),
(68, 'Chest',        false, 3),
(68, 'Shoulders',    false, 3),

-- ── PULL-UP BAR (69) ─────────────────────────────────────────
(69, 'Lats',         true,  5),
(69, 'Biceps',       false, 4),
(69, 'Rear Deltoids', false, 3),
(69, 'Core',         false, 2),

-- ── DIP BARS (70) ────────────────────────────────────────────
(70, 'Chest',        true,  4),
(70, 'Triceps',      true,  5),
(70, 'Shoulders',    false, 3),

-- ── TRX SUSPENSION TRAINER (71) ──────────────────────────────
(71, 'Core',         true,  5),
(71, 'Lats',         true,  4),
(71, 'Chest',        false, 3),
(71, 'Glutes',       false, 3),

-- ── BATTLE ROPES (72) ────────────────────────────────────────
(72, 'Shoulders',    true,  5),
(72, 'Core',         true,  4),
(72, 'Biceps',       false, 3),
(72, 'Triceps',      false, 3),
(72, 'Lats',         false, 2),

-- ── FOAM ROLLER (73) ─────────────────────────────────────────
(73, 'Quadriceps',   false, 2),
(73, 'Hamstrings',   false, 2),
(73, 'Lats',         false, 2),
(73, 'Upper Back',   false, 2),

-- ── EZ-CURL BAR (74) ─────────────────────────────────────────
(74, 'Biceps',       true,  5),
(74, 'Triceps',      true,  5),
(74, 'Forearms',     false, 2),

-- ── KROPPSVIKT (1) ───────────────────────────────────────────
(1, 'Chest',         false, 3),
(1, 'Triceps',       false, 3),
(1, 'Lats',          false, 3),
(1, 'Core',          true,  4),
(1, 'Glutes',        false, 3),
(1, 'Quadriceps',    false, 2),

-- ── HANTLAR (2) ──────────────────────────────────────────────
(2, 'Chest',         true,  4),
(2, 'Lats',          false, 3),
(2, 'Biceps',        true,  4),
(2, 'Triceps',       true,  4),
(2, 'Shoulders',     true,  4),
(2, 'Hamstrings',    false, 3),

-- ── SKIVSTÅNG (3) ────────────────────────────────────────────
(3, 'Chest',         true,  5),
(3, 'Lats',          true,  5),
(3, 'Quadriceps',    true,  5),
(3, 'Hamstrings',    true,  5),
(3, 'Glutes',        true,  5),
(3, 'Shoulders',     true,  4),
(3, 'Triceps',       false, 3),
(3, 'Biceps',        false, 3),
(3, 'Core',          false, 4),

-- ── KABELMASKIN (4) ──────────────────────────────────────────
(4, 'Chest',         true,  4),
(4, 'Lats',          true,  4),
(4, 'Biceps',        false, 3),
(4, 'Triceps',       false, 3),
(4, 'Shoulders',     false, 3),
(4, 'Glutes',        false, 2),
(4, 'Core',          false, 2),

-- ── RESISTANSBAND (5) ────────────────────────────────────────
(5, 'Glutes',        true,  4),
(5, 'Hip Abductors', false, 3),
(5, 'Shoulders',     false, 2),

-- ── KETTLEBELL (6) ───────────────────────────────────────────
(6, 'Glutes',        true,  5),
(6, 'Quadriceps',    false, 4),
(6, 'Core',          true,  4),
(6, 'Hamstrings',    false, 3),
(6, 'Shoulders',     false, 2)

ON CONFLICT DO NOTHING;

SELECT
  e.name AS maskin,
  COUNT(mm.id) AS antal_muskler,
  STRING_AGG(mm.muscle_name || ' (' || mm.engagement_level || ')', ', ' ORDER BY mm.engagement_level DESC) AS muskler
FROM equipment e
JOIN machine_muscles mm ON e.id = mm.equipment_id
GROUP BY e.name
ORDER BY antal_muskler DESC
LIMIT 10;