-- ============================================================
-- seed_training_blocks.sql
-- Skapar training_blocks → training_weeks → planned_exercises
-- Per user baserat på deras fitness_goal och fitness_level
-- Datum relativt till träningsdatan (maj 2026)
-- ============================================================

-- ── TRAINING BLOCKS per user ──────────────────────────────────
-- Erik Johansson (id=2) — bygga_muskler, medel
-- Sara Lindqvist (id=3) — hålla_sig_i_form, nybörjare
-- Mohammed Al-Rashid (id=4) — bygga_muskler, avancerad (PT)
-- Fatima Hassan (id=5) — gå_ner_i_vikt, nybörjare
-- Lucas Bergström (id=6) — öka_kondition, nybörjare
-- Amina Osman (id=7) — hålla_sig_i_form, medel
-- Viktor Svensson (id=8) — bygga_muskler, avancerad (PT)
-- Lina Karlsson (id=9) — gå_ner_i_vikt, medel

INSERT INTO training_blocks
  (id, user_id, plan_id, name, block_type, duration_weeks,
   start_date, end_date, target_rpe_min, target_rpe_max,
   target_weekly_sets, is_active, is_completed, notes) VALUES

-- Erik Johansson — Hypertrofi block (bygga_muskler, medel)
(1, 2, 18, 'Hypertrofi Block 1', 'hypertrophy', 4,
 '2026-04-21', '2026-05-18', 6.5, 8.0, 16, false, true,
 'Upper/Lower split, fokus volym'),

(2, 2, 18, 'Styrke Block', 'strength', 4,
 '2026-05-19', '2026-06-15', 7.0, 9.0, 12, true, false,
 'Tyngre vikt, lägre reps'),

-- Sara Lindqvist — Underhåll block (hålla_sig_i_form, nybörjare)
(3, 3, 17, 'Nybörjar Grundblock', 'accumulation', 4,
 '2026-04-21', '2026-05-18', 5.0, 7.0, 10, false, true,
 'Lär grundrörelser, lätt vikt'),

(4, 3, 17, 'Progressionsblock', 'hypertrophy', 4,
 '2026-05-19', '2026-06-15', 6.0, 7.5, 12, true, false,
 'Ökar volym gradvis'),

-- Mohammed Al-Rashid — Styrka block (PT, avancerad)
(5, 4, 20, 'Styrka Intensifiering', 'intensification', 4,
 '2026-04-21', '2026-05-18', 7.5, 9.5, 14, false, true,
 'Tung compound, låga reps'),

(6, 4, 16, 'PPL Volymblock', 'hypertrophy', 4,
 '2026-05-19', '2026-06-15', 7.0, 8.5, 18, true, false,
 'PPL med hög volym'),

-- Fatima Hassan — Fettförbränning (gå_ner_i_vikt, nybörjare)
(7, 5, 19, 'Fettförbränning Block 1', 'endurance', 4,
 '2026-04-21', '2026-05-18', 6.0, 7.5, 12, false, true,
 'Circuit training, kort vila'),

(8, 5, 19, 'Fettförbränning Block 2', 'endurance', 4,
 '2026-05-19', '2026-06-15', 6.5, 8.0, 14, true, false,
 'Ökad intensitet'),

-- Lucas Bergström — Kondition (öka_kondition, nybörjare)
(9, 6, 17, 'Konditionsgrund', 'endurance', 4,
 '2026-04-21', '2026-05-18', 5.0, 7.0, 8, false, true,
 'Bygger aerob bas'),

(10, 6, 17, 'Konditionsökning', 'endurance', 4,
 '2026-05-19', '2026-06-15', 5.5, 7.5, 10, true, false,
 'Längre pass, mer volym'),

-- Amina Osman — Underhåll (hålla_sig_i_form, medel)
(11, 7, 18, 'Underhållsblock', 'hypertrophy', 4,
 '2026-04-21', '2026-05-18', 6.5, 8.0, 14, false, true,
 'Balanserat program'),

(12, 7, 18, 'Intensifiering', 'intensification', 4,
 '2026-05-19', '2026-06-15', 7.0, 8.5, 16, true, false,
 'Ökar vikt, minskar reps'),

-- Viktor Svensson — Styrka (PT, avancerad)
(13, 8, 20, 'Power Block', 'power', 4,
 '2026-04-21', '2026-05-18', 7.5, 9.0, 16, false, true,
 'Explosiv styrka'),

(14, 8, 16, 'Hypertrofi Block', 'hypertrophy', 4,
 '2026-05-19', '2026-06-15', 7.0, 8.5, 20, true, false,
 'Hög volym PPL'),

-- Lina Karlsson — Viktnedgång (gå_ner_i_vikt, medel)
(15, 9, 19, 'Viktnedgång Block 1', 'endurance', 4,
 '2026-04-21', '2026-05-18', 6.0, 7.5, 14, false, true,
 'Styrka + kondition'),

(16, 9, 18, 'Viktnedgång Block 2', 'hypertrophy', 4,
 '2026-05-19', '2026-06-15', 6.5, 8.0, 16, true, false,
 'Mer styrka, behåll muskler')

ON CONFLICT DO NOTHING;

-- ── TRAINING WEEKS ────────────────────────────────────────────
-- 4 veckor per block, vecka 4 = deload
INSERT INTO training_weeks
  (id, block_id, week_number, target_volume_multiplier,
   target_intensity_multiplier, is_deload, focus, notes) VALUES

-- Erik block 1 (block_id=1)
(1,  1, 1, 1.00, 0.90, false, 'Inledning',      'Lär rörelsemönster'),
(2,  1, 2, 1.10, 0.95, false, 'Progresssion',   'Öka volym'),
(3,  1, 3, 1.20, 1.00, false, 'Toppvecka',      'Max volym'),
(4,  1, 4, 0.60, 0.70, true,  'Deload',         'Vila och återhämtning'),

-- Erik block 2 (block_id=2)
(5,  2, 1, 0.90, 1.00, false, 'Styrkestart',    'Tung vikt, låga reps'),
(6,  2, 2, 0.95, 1.05, false, 'Progression',    'Öka vikt'),
(7,  2, 3, 1.00, 1.10, false, 'Toppvecka',      'Max styrka'),
(8,  2, 4, 0.60, 0.75, true,  'Deload',         'Aktiv vila'),

-- Sara block 1 (block_id=3)
(9,  3, 1, 0.80, 0.80, false, 'Teknik',         'Fokus form'),
(10, 3, 2, 0.90, 0.85, false, 'Volymökning',    'Lägg till set'),
(11, 3, 3, 1.00, 0.90, false, 'Progression',    'Normal belastning'),
(12, 3, 4, 0.60, 0.70, true,  'Deload',         'Lättare vecka'),

-- Sara block 2 (block_id=4)
(13, 4, 1, 1.00, 0.90, false, 'Ny start',       'Lite tyngre'),
(14, 4, 2, 1.10, 0.95, false, 'Ökning',         'Mer volym'),
(15, 4, 3, 1.20, 1.00, false, 'Toppvecka',      'Full insats'),
(16, 4, 4, 0.60, 0.75, true,  'Deload',         'Återhämtning'),

-- Mohammed block 1 (block_id=5)
(17, 5, 1, 0.85, 1.05, false, 'Styrkestart',    'Heavy singles'),
(18, 5, 2, 0.90, 1.10, false, 'Progression',    'PR-jakt'),
(19, 5, 3, 0.95, 1.15, false, 'Toppvecka',      'Max styrka'),
(20, 5, 4, 0.60, 0.80, true,  'Deload',         'Aktiv vila'),

-- Mohammed block 2 (block_id=6)
(21, 6, 1, 1.00, 0.90, false, 'PPL start',      'Lär programmet'),
(22, 6, 2, 1.15, 0.95, false, 'Volymökning',    'Fler set'),
(23, 6, 3, 1.25, 1.00, false, 'Max volym',      'Toppvecka'),
(24, 6, 4, 0.60, 0.75, true,  'Deload',         'Vila'),

-- Fatima block 1 (block_id=7)
(25, 7, 1, 0.80, 0.80, false, 'Inledning',      'Lär övningarna'),
(26, 7, 2, 0.90, 0.85, false, 'Progression',    'Kortare vila'),
(27, 7, 3, 1.00, 0.90, false, 'Full intensitet','Max puls'),
(28, 7, 4, 0.60, 0.70, true,  'Deload',         'Lättare'),

-- Fatima block 2 (block_id=8)
(29, 8, 1, 1.00, 0.90, false, 'Ny start',       'Mer intensitet'),
(30, 8, 2, 1.10, 0.95, false, 'Ökning',         'Fler rundor'),
(31, 8, 3, 1.20, 1.00, false, 'Toppvecka',      'Full gas'),
(32, 8, 4, 0.60, 0.75, true,  'Deload',         'Vila'),

-- Lucas block 1 (block_id=9)
(33, 9, 1, 0.80, 0.80, false, 'Konditionsbas',  'Korta pass'),
(34, 9, 2, 0.90, 0.85, false, 'Ökning',         'Längre distans'),
(35, 9, 3, 1.00, 0.90, false, 'Progression',    'Fler intervaller'),
(36, 9, 4, 0.60, 0.70, true,  'Deload',         'Kort promenad'),

-- Lucas block 2 (block_id=10)
(37, 10, 1, 1.00, 0.90, false, 'Ny start',      'Längre pass'),
(38, 10, 2, 1.10, 0.95, false, 'Ökning',        'Mer distans'),
(39, 10, 3, 1.20, 1.00, false, 'Toppvecka',     'Max distans'),
(40, 10, 4, 0.60, 0.75, true,  'Deload',        'Aktiv vila'),

-- Amina block 1 (block_id=11)
(41, 11, 1, 1.00, 0.90, false, 'Underhåll',     'Normal träning'),
(42, 11, 2, 1.10, 0.95, false, 'Progression',   'Lägg till set'),
(43, 11, 3, 1.20, 1.00, false, 'Toppvecka',     'Max volym'),
(44, 11, 4, 0.60, 0.75, true,  'Deload',        'Vila'),

-- Amina block 2 (block_id=12)
(45, 12, 1, 0.90, 1.00, false, 'Styrkestart',   'Tyngre vikt'),
(46, 12, 2, 0.95, 1.05, false, 'Progression',   'Öka vikt'),
(47, 12, 3, 1.00, 1.10, false, 'Intensifiering','Tunga set'),
(48, 12, 4, 0.60, 0.80, true,  'Deload',        'Aktiv vila'),

-- Viktor block 1 (block_id=13)
(49, 13, 1, 0.85, 1.05, false, 'Power start',   'Explosiva rörelser'),
(50, 13, 2, 0.90, 1.10, false, 'Progression',   'Tyngre och snabbare'),
(51, 13, 3, 0.95, 1.15, false, 'Toppvecka',     'Max power'),
(52, 13, 4, 0.60, 0.80, true,  'Deload',        'Aktiv vila'),

-- Viktor block 2 (block_id=14)
(53, 14, 1, 1.00, 0.90, false, 'PPL start',     'Hög volym'),
(54, 14, 2, 1.15, 0.95, false, 'Volymökning',   'Fler set'),
(55, 14, 3, 1.25, 1.00, false, 'Max volym',     'Toppvecka'),
(56, 14, 4, 0.60, 0.75, true,  'Deload',        'Vila'),

-- Lina block 1 (block_id=15)
(57, 15, 1, 0.90, 0.85, false, 'Fettförbränning', 'Styrka + kondition'),
(58, 15, 2, 1.00, 0.90, false, 'Progression',   'Mer volym'),
(59, 15, 3, 1.10, 0.95, false, 'Toppvecka',     'Full intensitet'),
(60, 15, 4, 0.60, 0.75, true,  'Deload',        'Vila'),

-- Lina block 2 (block_id=16)
(61, 16, 1, 1.00, 0.90, false, 'Styrkestart',   'Mer styrka'),
(62, 16, 2, 1.10, 0.95, false, 'Ökning',        'Tyngre vikt'),
(63, 16, 3, 1.20, 1.00, false, 'Toppvecka',     'Max styrka'),
(64, 16, 4, 0.60, 0.80, true,  'Deload',        'Aktiv vila')

ON CONFLICT DO NOTHING;

-- ── PLANNED EXERCISES — Erik Johansson vecka 5 (aktiv block) ─
-- Representativa planerade pass för aktiva users
INSERT INTO planned_exercises
  (week_id, exercise_id, day_number, order_index,
   planned_sets, planned_reps_min, planned_reps_max,
   planned_weight_kg, planned_rpe, rest_seconds, notes) VALUES

-- Måndag — Upper A Styrka (week_id=5, dag 1)
(5, 1,   1, 1, 4, 4, 6,  90.0, 8.0, 180, 'Bänkpress tung'),
(5, 116, 1, 2, 4, 4, 6,  70.0, 8.0, 180, 'Barbell Row tung'),
(5, 7,   1, 3, 3, 5, 7,  60.0, 7.5, 150, 'Militärpress'),
(5, 123, 1, 4, 3, 5, 7,  NULL, 7.5, 150, 'Pull-up kroppsvikt'),
(5, 155, 1, 5, 3, 6, 8,  50.0, 7.0, 120, 'Close Grip Bench'),
(5, 150, 1, 6, 3, 6, 8,  30.0, 7.0, 90,  'Barbell Curl'),

-- Tisdag — Lower A Styrka (week_id=5, dag 2)
(5, 5,   2, 1, 4, 4, 6, 100.0, 8.5, 180, 'Knäböj tung'),
(5, 3,   2, 2, 4, 4, 6, 120.0, 8.5, 180, 'Marklyft'),
(5, 133, 2, 3, 3, 5, 7,  NULL, 8.0, 150, 'Nordic Hamstring'),
(5, 135, 2, 4, 3, 8, 12, NULL, 7.0, 90,  'Standing Calf'),
(5, 166, 2, 5, 3, 45, 60, NULL, 7.0, 60, 'Plank'),

-- Torsdag — Upper B Volym (week_id=5, dag 4)
(5, 108, 4, 1, 4, 8, 12, 30.0, 7.5, 90,  'Incline DB Press'),
(5, 117, 4, 2, 4, 8, 12, 28.0, 7.5, 90,  'Dumbbell Row'),
(5, 140, 4, 3, 3, 10, 14, 22.0, 7.0, 75, 'DB Shoulder Press'),
(5, 145, 4, 4, 3, 12, 15, 20.0, 6.5, 60, 'Face Pull'),
(5, 154, 4, 5, 3, 10, 14, 15.0, 6.5, 60, 'Cable Curl'),
(5, 156, 4, 6, 3, 10, 14, 20.0, 6.5, 60, 'Tricep Pushdown'),

-- Fredag — Lower B Volym (week_id=5, dag 5)
(5, 79,  5, 1, 4, 8, 12, 40.0, 7.5, 90,  'Bulgarian Split'),
(5, 74,  5, 2, 4, 8, 12, 55.0, 7.5, 90,  'Romanian DL'),
(5, 73,  5, 3, 3, 10, 14, 80.0, 7.0, 75, 'Leg Press'),
(5, 78,  5, 4, 3, 10, 14, 60.0, 7.0, 75, 'Hip Thrust'),
(5, 75,  5, 5, 3, 12, 15, 35.0, 6.5, 60, 'Leg Curl'),
(5, 136, 5, 6, 3, 12, 15, 25.0, 6.0, 60, 'Seated Calf')

ON CONFLICT DO NOTHING;

-- Sammanfattning
SELECT
  u.name AS user,
  COUNT(DISTINCT tb.id) AS block,
  COUNT(DISTINCT tw.id) AS veckor,
  COUNT(pe.id) AS planerade_övningar
FROM users u
JOIN training_blocks tb ON u.id = tb.user_id
LEFT JOIN training_weeks tw ON tb.id = tw.block_id
LEFT JOIN planned_exercises pe ON tw.id = pe.week_id
GROUP BY u.name
ORDER BY block DESC;