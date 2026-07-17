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

