CREATE INDEX IF NOT EXISTS idx_substitution_rules_target ON exercise_substitution_rules(target_exercise_id);
CREATE INDEX IF NOT EXISTS idx_ai_coach_sessions_date ON ai_coach_sessions(session_date DESC);
CREATE INDEX IF NOT EXISTS idx_exercises_compound ON exercises(is_compound, systemic_fatigue);
CREATE INDEX IF NOT EXISTS idx_exercises_body_part_type ON exercises(body_part_id, exercise_type);
CREATE INDEX IF NOT EXISTS idx_exercises_spinal_load ON exercises(spinal_load, knee_stress, shoulder_stress);
CREATE INDEX IF NOT EXISTS idx_fatigue_scores_recent ON fatigue_scores(user_id, date DESC, readiness_score);

ALTER TABLE exercises ALTER COLUMN force_curve SET DEFAULT 'constant';

UPDATE exercises SET is_compound = TRUE WHERE name IN ('Bänkpress','Marklyft','Knäböj','Militärpress','Latsdrag','Utfall','Dumbbell Bench Press','Dumbbell Row','Chest Supported Row','Bulgarian Split Squat','Farmer''s Walk','Pull-ups','Dips','Burpees');
UPDATE exercises SET is_compound = FALSE WHERE name IN ('Bicepscurl','Tricepspress','Hantelflyes','Lateral Raise','Front Raise','Front Raises','Concentration Curl','Hammer Curl','Dumbbell Curl','Plankan','Arnold Press');

UPDATE exercises SET movement_pattern='push_horizontal', force_type='compound', systemic_fatigue=7, spinal_load=4, shoulder_stress=8, knee_stress=1, hip_stress=2, lower_back_stress=4 WHERE name='Dumbbell Bench Press';
UPDATE exercises SET movement_pattern='pull_horizontal', force_type='compound', systemic_fatigue=6, spinal_load=3, shoulder_stress=4, knee_stress=1, hip_stress=2, lower_back_stress=3 WHERE name='Dumbbell Row';
UPDATE exercises SET movement_pattern='isolation', force_type='isolation', systemic_fatigue=3, spinal_load=1, shoulder_stress=2, knee_stress=1, hip_stress=1, lower_back_stress=1 WHERE name IN ('Hantelflyes','Lateral Raise','Front Raise','Front Raises');
UPDATE exercises SET movement_pattern='squat', force_type='unilateral', is_unilateral=TRUE, systemic_fatigue=6, spinal_load=5, shoulder_stress=1, knee_stress=6, hip_stress=6, lower_back_stress=4 WHERE name IN ('Utfall','Bulgarian Split Squat','Curtsy Lunge');
UPDATE exercises SET movement_pattern='isolation', force_type='isolation', systemic_fatigue=2, spinal_load=1, shoulder_stress=1, knee_stress=1, hip_stress=1, lower_back_stress=1, force_curve='bell_curve' WHERE name IN ('Bicepscurl','Dumbbell Curl','Hammer Curl','Concentration Curl');
UPDATE exercises SET movement_pattern='isolation', force_type='isolation', systemic_fatigue=2, spinal_load=1, shoulder_stress=3, knee_stress=1, hip_stress=1, lower_back_stress=1 WHERE name='Tricepspress';
UPDATE exercises SET movement_pattern='hinge', force_type='compound', is_compound=TRUE, systemic_fatigue=7, spinal_load=6, shoulder_stress=2, knee_stress=4, hip_stress=8, lower_back_stress=6 WHERE name IN ('Romanian Deadlift','Romanian Deadlift with Dumbbells');

UPDATE exercises SET tips='Håll armbågarna nära kroppen, full extension, kläm ihop biceps i topp.', common_mistakes='Sving med kroppen, armbågar rör sig, ofullständig rörelse' WHERE name='Bicepscurl';
UPDATE exercises SET tips='Ta ett stort steg framåt, knä rakt ner, överkropp upprätt.', common_mistakes='Knä passerar tå, ojämn vikt, överkropp lutar' WHERE name='Utfall';
UPDATE exercises SET tips='Skulderblad ihopdragna, pressa rakt upp, kontrollera nedfasen.', common_mistakes='Svankrygg, för bredt grepp, studsande i botten' WHERE name='Militärpress';

UPDATE equipment SET supports_unilateral=TRUE, supports_progressive_overload=TRUE, min_weight=2.0, max_weight=100.0 WHERE name='Hantlar';
UPDATE equipment SET supports_unilateral=FALSE, supports_progressive_overload=TRUE, min_weight=20.0, max_weight=500.0 WHERE name='Skivstång';
UPDATE equipment SET supports_unilateral=TRUE, supports_progressive_overload=TRUE, min_weight=5.0, max_weight=200.0 WHERE name='Kabelmaskin';
UPDATE equipment SET supports_unilateral=TRUE, supports_progressive_overload=FALSE, min_weight=5.0, max_weight=50.0 WHERE name='Resistansband';
UPDATE equipment SET supports_unilateral=TRUE, supports_progressive_overload=TRUE, min_weight=8.0, max_weight=48.0 WHERE name='Kettlebell';

INSERT INTO gym_equipment (gym_id, equipment_id, quantity, condition)
SELECT (SELECT id FROM gyms WHERE name='SATS' LIMIT 1), e.id, 3, 'good'
FROM equipment e WHERE e.category IN ('machines','cables','cardio','free_weights')
ON CONFLICT (gym_id, equipment_id) DO NOTHING;

INSERT INTO gym_equipment (gym_id, equipment_id, quantity, condition)
SELECT (SELECT id FROM gyms WHERE name='Hemmagym' LIMIT 1), e.id, 1, 'good'
FROM equipment e WHERE e.name IN ('Hantlar','Resistansband','Kettlebell','Kroppsvikt','Foam Roller')
ON CONFLICT (gym_id, equipment_id) DO NOTHING;
