-- ============================================================
-- seed_equipment_exercises.sql
-- Kopplar 44 maskiner/utrustningar till relevanta övningar
-- equipment_id → exercise_id, is_primary, difficulty, notes
-- ============================================================

INSERT INTO equipment_exercises (equipment_id, exercise_id, is_primary, difficulty, notes) VALUES

-- ── KROPPSVIKT (1) ──────────────────────────────────────────
(1, 111, true,  'beginner',     'Klassisk push-up, grundövning'),
(1, 112, true,  'beginner',     'Bredare grepp, mer bröst'),
(1, 113, true,  'intermediate', 'Smalare grepp, mer triceps'),
(1, 123, true,  'advanced',     'Överhands pull-up'),
(1, 124, true,  'intermediate', 'Underhands chin-up'),
(1, 63,  true,  'intermediate', 'Dips för bröst och triceps'),
(1, 166, true,  'beginner',     'Core-stabilitet'),
(1, 167, true,  'beginner',     'Lateral core'),
(1, 162, true,  'beginner',     'Mage, dynamisk'),
(1, 161, true,  'beginner',     'Grundläggande mageövning'),
(1, 164, true,  'advanced',     'Hängande benlyft, core'),
(1, 165, true,  'advanced',     'Ab wheel, avancerat core'),
(1, 170, true,  'advanced',     'Dragon flag, extrem core'),
(1, 134, true,  'beginner',     'Glute bridge, höft och rumpa'),
(1, 78,  true,  'intermediate', 'Hip thrust, explosiv rumpa'),
(1, 177, true,  'beginner',     'Mountain climbers, kondition'),
(1, 12,  true,  'intermediate', 'Burpees, helkropp'),
(1, 127, false, 'beginner',     'Knäböj med kroppsvikt'),
(1, 6,   false, 'beginner',     'Utfall med kroppsvikt'),
(1, 172, true,  'beginner',     'Bird dog, stabilitet'),
(1, 171, true,  'beginner',     'Dead bug, core'),

-- ── PULL-UP BAR (69) ─────────────────────────────────────────
(69, 123, true,  'advanced',     'Standard pull-up'),
(69, 124, true,  'intermediate', 'Chin-up, underhands'),
(69, 122, true,  'advanced',     'Bred grepp lat'),
(69, 164, true,  'advanced',     'Hanging leg raise'),
(69, 163, true,  'intermediate', 'Leg raise'),
(69, 170, true,  'advanced',     'Dragon flag'),

-- ── DIP BARS (70) ────────────────────────────────────────────
(70, 63,  true,  'intermediate', 'Dips, bröst och triceps'),
(70, 155, true,  'intermediate', 'Close grip fokus triceps'),
(70, 164, false, 'advanced',     'Hängande benlyft'),

-- ── KABELMASKIN (4) ──────────────────────────────────────────
(4, 109, true,  'intermediate', 'Cable crossover, bröst'),
(4, 62,  true,  'intermediate', 'Cable flyes, isolering bröst'),
(4, 120, true,  'intermediate', 'Cable row, rygg'),
(4, 68,  true,  'intermediate', 'Seated cable row'),
(4, 121, true,  'intermediate', 'Lat pulldown via kabel'),
(4, 154, true,  'beginner',     'Cable curl, biceps'),
(4, 156, true,  'beginner',     'Tricep pushdown'),
(4, 143, true,  'intermediate', 'Cable lateral raise'),
(4, 147, true,  'intermediate', 'Cable reverse fly'),
(4, 145, true,  'intermediate', 'Face pull, bakre axel'),
(4, 169, true,  'intermediate', 'Cable crunch, mage'),
(4, 183, true,  'beginner',     'Cable kickback, rumpa'),
(4, 144, false, 'beginner',     'Front raise via kabel'),

-- ── CABLE CROSSOVER (59) ─────────────────────────────────────
(59, 109, true,  'intermediate', 'Primär övning för maskinen'),
(59, 62,  true,  'intermediate', 'Cable flyes'),
(59, 147, true,  'intermediate', 'Cable reverse fly'),
(59, 143, true,  'beginner',     'Cable lateral raise'),
(59, 145, true,  'intermediate', 'Face pull'),
(59, 154, false, 'beginner',     'Cable curl'),
(59, 156, false, 'beginner',     'Tricep pushdown'),

-- ── FUNCTIONAL TRAINER (60) ──────────────────────────────────
(60, 109, true,  'intermediate', 'Crossover på funktionell'),
(60, 145, true,  'intermediate', 'Face pull'),
(60, 183, true,  'beginner',     'Glute kickback'),
(60, 120, true,  'intermediate', 'Cable row'),
(60, 156, false, 'beginner',     'Tricep pushdown'),
(60, 154, false, 'beginner',     'Cable curl'),

-- ── HANTLAR (2) ──────────────────────────────────────────────
(2, 107, true,  'beginner',     'Dumbbell bench press'),
(2, 108, true,  'beginner',     'Incline dumbbell press'),
(2, 2,   true,  'beginner',     'Hantelflyes, bröst'),
(2, 117, true,  'beginner',     'Dumbbell row, rygg'),
(2, 151, true,  'beginner',     'Dumbbell curl, biceps'),
(2, 152, true,  'beginner',     'Concentration curl'),
(2, 70,  true,  'beginner',     'Incline dumbbell curl'),
(2, 71,  true,  'beginner',     'Hammer curl'),
(2, 158, true,  'beginner',     'Tricep kickback'),
(2, 66,  true,  'beginner',     'Overhead tricep extension'),
(2, 140, true,  'beginner',     'Seated dumbbell press'),
(2, 142, true,  'beginner',     'Lateral raise'),
(2, 65,  true,  'beginner',     'Front raises'),
(2, 146, true,  'beginner',     'Reverse fly'),
(2, 149, true,  'beginner',     'Shrugs'),
(2, 74,  true,  'beginner',     'Romanian deadlift med hantlar'),
(2, 192, true,  'beginner',     'Romanian DL med hantlar'),
(2, 6,   false, 'beginner',     'Utfall med hantlar'),
(2, 130, false, 'beginner',     'Walking lunge med hantlar'),
(2, 168, false, 'beginner',     'Russian twist med hantel'),
(2, 181, true,  'intermediate', 'Farmers walk'),

-- ── SKIVSTÅNG (3) ────────────────────────────────────────────
(3, 1,   true,  'intermediate', 'Bänkpress med skivstång'),
(3, 104, true,  'intermediate', 'Flat barbell bench press'),
(3, 105, true,  'intermediate', 'Incline barbell bench press'),
(3, 106, true,  'intermediate', 'Decline bench press'),
(3, 3,   true,  'intermediate', 'Marklyft'),
(3, 114, true,  'intermediate', 'Conventional deadlift'),
(3, 115, true,  'intermediate', 'Sumo deadlift'),
(3, 5,   true,  'intermediate', 'Knäböj med skivstång'),
(3, 127, true,  'intermediate', 'Back squat'),
(3, 128, true,  'advanced',     'Front squat'),
(3, 116, true,  'intermediate', 'Barbell row'),
(3, 118, true,  'intermediate', 'T-bar row'),
(3, 7,   true,  'intermediate', 'Militärpress'),
(3, 139, true,  'intermediate', 'Overhead press'),
(3, 141, false, 'intermediate', 'Arnold press med skivstång'),
(3, 148, true,  'beginner',     'Upright row'),
(3, 149, true,  'beginner',     'Shrugs med skivstång'),
(3, 150, true,  'beginner',     'Barbell curl'),
(3, 155, true,  'intermediate', 'Close grip bench press'),
(3, 157, true,  'intermediate', 'Skull crusher'),
(3, 67,  true,  'intermediate', 'Skull crushers'),
(3, 74,  true,  'intermediate', 'Romanian deadlift'),
(3, 126, true,  'intermediate', 'Good morning'),
(3, 133, true,  'advanced',     'Nordic hamstring curl'),

-- ── EZ-CURL BAR (74) ─────────────────────────────────────────
(74, 150, true,  'beginner',     'Barbell curl med EZ-stång'),
(74, 157, true,  'intermediate', 'Skull crusher med EZ-stång'),
(74, 67,  true,  'intermediate', 'Skull crushers'),
(74, 148, false, 'beginner',     'Upright row'),

-- ── POWER RACK (68) ──────────────────────────────────────────
(68, 127, true,  'intermediate', 'Back squat i rack'),
(68, 128, true,  'advanced',     'Front squat i rack'),
(68, 7,   true,  'intermediate', 'Militärpress i rack'),
(68, 139, true,  'intermediate', 'Overhead press i rack'),
(68, 1,   true,  'intermediate', 'Bänkpress i rack'),
(68, 104, true,  'intermediate', 'Flat bench press'),
(68, 123, false, 'advanced',     'Pull-up på rack'),
(68, 133, true,  'advanced',     'Nordic hamstring curl'),

-- ── KETTLEBELL (6) ───────────────────────────────────────────
(6, 129, true,  'beginner',     'Goblet squat'),
(6, 78,  true,  'intermediate', 'Kettlebell hip thrust'),
(6, 181, true,  'intermediate', 'Farmers walk'),
(6, 168, true,  'beginner',     'Russian twist'),
(6, 134, false, 'beginner',     'Glute bridge med kettlebell'),
(6, 180, false, 'intermediate', 'Sled push ersättning'),

-- ── TRX SUSPENSION TRAINER (71) ──────────────────────────────
(71, 120, true,  'beginner',     'TRX row, rygg'),
(71, 166, true,  'beginner',     'TRX plank'),
(71, 134, false, 'beginner',     'TRX glute bridge'),
(71, 111, false, 'intermediate', 'TRX push-up'),

-- ── BATTLE ROPES (72) ────────────────────────────────────────
(72, 179, true,  'intermediate', 'Battle ropes, kondition'),

-- ── RESISTANSBAND (5) ────────────────────────────────────────
(5, 188, true,  'beginner',     'Banded walk, höft abduktion'),
(5, 134, false, 'beginner',     'Glute bridge med band'),
(5, 183, false, 'beginner',     'Cable kickback med band'),
(5, 228, true,  'beginner',     'Shoulder dislocate'),

-- ── LÖPBAND (61) ─────────────────────────────────────────────
(61, 11,  true,  'beginner',     'Löpning på band'),
(61, 173, true,  'beginner',     'Running'),

-- ── CROSSTRAINER (62) ────────────────────────────────────────
(62, 174, true,  'beginner',     'Low impact kondition'),

-- ── MOTIONSCYKEL (63) ────────────────────────────────────────
(63, 174, true,  'beginner',     'Cycling, kondition'),

-- ── RODDMASKIN (64) ──────────────────────────────────────────
(64, 175, true,  'beginner',     'Rodd, helkroppskonditon'),

-- ── RODDMASKIN / SKI ERG (67) ────────────────────────────────
(67, 175, true,  'beginner',     'Rodd variant'),
(67, 179, false, 'intermediate', 'Battle ropes liknande'),

-- ── AIR BIKE (66) ────────────────────────────────────────────
(66, 174, true,  'intermediate', 'High intensity cycling'),
(66, 12,  false, 'advanced',     'Explosiv kondition'),

-- ── STAIRCLIMBER (65) ────────────────────────────────────────
(65, 173, true,  'beginner',     'Trapphöjning, kondition'),
(65, 138, false, 'beginner',     'Step-ups liknande'),

-- ── LEG PRESS MACHINE (37) ───────────────────────────────────
(37, 73,  true,  'beginner',     'Leg press, quadriceps primär'),
(37, 193, true,  'beginner',     'Fötter högt, mer hamstrings'),
(37, 77,  false, 'beginner',     'Calf raises på leg press'),

-- ── LEG EXTENSION MACHINE (38) ───────────────────────────────
(38, 76,  true,  'beginner',     'Leg extension, quadriceps isolering'),

-- ── LEG CURL MACHINE (39) ────────────────────────────────────
(39, 75,  true,  'beginner',     'Lying leg curl, hamstrings'),

-- ── SEATED LEG CURL MACHINE (40) ─────────────────────────────
(40, 75,  true,  'beginner',     'Seated leg curl, hamstrings'),

-- ── HIP ABDUCTION MACHINE (41) ───────────────────────────────
(41, 182, true,  'beginner',     'Hip abduction, höft utåt'),

-- ── HIP ADDUCTION MACHINE (42) ───────────────────────────────
(42, 182, false, 'beginner',     'Hip adduction, höft inåt'),

-- ── CALF RAISE MACHINE (43) ──────────────────────────────────
(43, 135, true,  'beginner',     'Standing calf raise'),
(43, 77,  true,  'beginner',     'Calf raises'),

-- ── SEATED CALF RAISE MACHINE (44) ───────────────────────────
(44, 136, true,  'beginner',     'Seated calf raise, soleus'),

-- ── HACK SQUAT MACHINE (45) ──────────────────────────────────
(45, 132, true,  'intermediate', 'Hack squat, quadriceps'),
(45, 73,  false, 'beginner',     'Alternativ till leg press'),

-- ── SMITH MACHINE (46) ───────────────────────────────────────
(46, 1,   true,  'beginner',     'Smith machine bench press'),
(46, 127, true,  'beginner',     'Smith machine squat'),
(46, 6,   false, 'beginner',     'Smith machine lunges'),
(46, 7,   true,  'beginner',     'Smith machine OHP'),
(46, 78,  false, 'intermediate', 'Smith machine hip thrust'),
(46, 149, false, 'beginner',     'Smith machine shrugs'),

-- ── GLUTE KICKBACK MACHINE (47) ──────────────────────────────
(47, 189, true,  'beginner',     'Glute kickback, isolering rumpa'),
(47, 183, true,  'beginner',     'Cable kickback variant'),

-- ── LAT PULLDOWN MACHINE (48) ────────────────────────────────
(48, 4,   true,  'beginner',     'Latsdrag, bred grepp'),
(48, 121, true,  'beginner',     'Lat pulldown'),
(48, 122, true,  'beginner',     'Wide grip pulldown'),

-- ── SEATED ROW MACHINE (49) ──────────────────────────────────
(49, 68,  true,  'beginner',     'Seated cable row'),
(49, 120, true,  'beginner',     'Cable row variant'),
(49, 119, false, 'beginner',     'Chest supported alternativ'),

-- ── T-BAR ROW MACHINE (50) ───────────────────────────────────
(50, 118, true,  'intermediate', 'T-bar row'),
(50, 116, false, 'intermediate', 'Barbell row alternativ'),

-- ── PULLOVER MACHINE (51) ────────────────────────────────────
(51, 121, false, 'beginner',     'Lat aktivering'),
(51, 4,   false, 'beginner',     'Latsdrag liknande'),

-- ── BÄNKPRESSMASKIN (52) ─────────────────────────────────────
(52, 110, true,  'beginner',     'Pec deck / bröstpress'),
(52, 1,   false, 'beginner',     'Bänkpress alternativ'),

-- ── SHOULDER PRESS MACHINE (53) ──────────────────────────────
(53, 7,   true,  'beginner',     'Axelpress i maskin'),
(53, 139, false, 'beginner',     'OHP alternativ'),

-- ── PEC DECK / CHEST FLY MACHINE (54) ────────────────────────
(54, 110, true,  'beginner',     'Pec deck, bröst isolering'),
(54, 2,   false, 'beginner',     'Hantelflyes alternativ'),

-- ── INCLINE PRESS MACHINE (55) ───────────────────────────────
(55, 108, true,  'beginner',     'Incline press, övre bröst'),
(55, 105, false, 'beginner',     'Incline barbell alternativ'),

-- ── AB CRUNCH MACHINE (56) ───────────────────────────────────
(56, 161, true,  'beginner',     'Crunch i maskin'),
(56, 169, true,  'beginner',     'Cable crunch variant'),

-- ── CAPTAIN CHAIR / DIP STATION (57) ─────────────────────────
(57, 163, true,  'beginner',     'Leg raise på captain chair'),
(57, 164, true,  'intermediate', 'Hanging leg raise'),
(57, 63,  true,  'intermediate', 'Dips'),

-- ── ROMAN CHAIR / BACK EXTENSION (58) ────────────────────────
(58, 125, true,  'beginner',     'Hyperextension, ländryggen'),
(58, 126, false, 'intermediate', 'Good morning liknande'),
(58, 74,  false, 'beginner',     'Romanian DL alternativ')

ON CONFLICT (equipment_id, exercise_id) DO NOTHING;

SELECT 
  e.name AS utrustning,
  COUNT(ee.exercise_id) AS antal_övningar
FROM equipment e
JOIN equipment_exercises ee ON e.id = ee.equipment_id
GROUP BY e.name
ORDER BY antal_övningar DESC;