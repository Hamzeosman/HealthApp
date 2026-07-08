-- ============================================================
-- P3 MIGRATION — Exercise Intelligence + AI Coach Foundation
-- ============================================================

-- 1. EXERCISE BIOMECHANICS
ALTER TABLE exercises ADD COLUMN IF NOT EXISTS movement_plane VARCHAR(20)
    CHECK (movement_plane IN ('sagittal','frontal','transverse','multi_planar'));
ALTER TABLE exercises ADD COLUMN IF NOT EXISTS unilateral BOOLEAN DEFAULT FALSE;
ALTER TABLE exercises ADD COLUMN IF NOT EXISTS stabilization_level INT CHECK (stabilization_level BETWEEN 1 AND 5);
ALTER TABLE exercises ADD COLUMN IF NOT EXISTS spinal_load INT CHECK (spinal_load BETWEEN 1 AND 10);
ALTER TABLE exercises ADD COLUMN IF NOT EXISTS systemic_fatigue INT CHECK (systemic_fatigue BETWEEN 1 AND 10);
ALTER TABLE exercises ADD COLUMN IF NOT EXISTS mobility_requirement INT CHECK (mobility_requirement BETWEEN 1 AND 5);
ALTER TABLE exercises ADD COLUMN IF NOT EXISTS force_curve VARCHAR(20)
    CHECK (force_curve IN ('ascending','descending','bell_curve','constant','accommodating'));

-- 2. JOINT STRESS
ALTER TABLE exercises ADD COLUMN IF NOT EXISTS shoulder_stress INT CHECK (shoulder_stress BETWEEN 1 AND 10);
ALTER TABLE exercises ADD COLUMN IF NOT EXISTS knee_stress INT CHECK (knee_stress BETWEEN 1 AND 10);
ALTER TABLE exercises ADD COLUMN IF NOT EXISTS hip_stress INT CHECK (hip_stress BETWEEN 1 AND 10);
ALTER TABLE exercises ADD COLUMN IF NOT EXISTS lower_back_stress INT CHECK (lower_back_stress BETWEEN 1 AND 10);
ALTER TABLE exercises ADD COLUMN IF NOT EXISTS wrist_stress INT CHECK (wrist_stress BETWEEN 1 AND 10);

-- 3. EQUIPMENT CAPABILITIES
ALTER TABLE equipment ADD COLUMN IF NOT EXISTS supports_unilateral BOOLEAN DEFAULT FALSE;
ALTER TABLE equipment ADD COLUMN IF NOT EXISTS supports_progressive_overload BOOLEAN DEFAULT TRUE;
ALTER TABLE equipment ADD COLUMN IF NOT EXISTS min_weight NUMERIC(6,2);
ALTER TABLE equipment ADD COLUMN IF NOT EXISTS max_weight NUMERIC(6,2);
ALTER TABLE equipment ADD COLUMN IF NOT EXISTS setup_time_minutes INT DEFAULT 1;

-- 4. EXERCISE SUBSTITUTION RULES
CREATE TABLE IF NOT EXISTS exercise_substitution_rules (
    id SERIAL PRIMARY KEY,
    source_exercise_id INT REFERENCES exercises(id) ON DELETE CASCADE,
    target_exercise_id INT REFERENCES exercises(id) ON DELETE CASCADE,
    substitution_reason VARCHAR(50) CHECK (substitution_reason IN (
        'injury','equipment','fatigue','skill','home_gym',
        'preference','progression','deload'
    )),
    equivalence_score NUMERIC(3,2) CHECK (equivalence_score BETWEEN 0 AND 1),
    fatigue_delta INT,
    stimulus_similarity INT CHECK (stimulus_similarity BETWEEN 1 AND 10),
    notes TEXT,
    UNIQUE(source_exercise_id, target_exercise_id, substitution_reason)
);

-- 5. GYM PROFILES
CREATE TABLE IF NOT EXISTS gyms (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    address TEXT,
    city VARCHAR(50),
    country VARCHAR(50) DEFAULT 'Sweden',
    gym_type VARCHAR(20) CHECK (gym_type IN (
        'commercial','home','outdoor','crossfit','rehabilitation','boutique'
    )) DEFAULT 'commercial',
    description TEXT,
    image_url VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS gym_equipment (
    id SERIAL PRIMARY KEY,
    gym_id INT REFERENCES gyms(id) ON DELETE CASCADE,
    equipment_id INT REFERENCES equipment(id) ON DELETE CASCADE,
    quantity INT DEFAULT 1,
    condition VARCHAR(20) CHECK (condition IN ('excellent','good','fair','poor')),
    notes TEXT,
    UNIQUE(gym_id, equipment_id)
);

CREATE TABLE IF NOT EXISTS user_gym_memberships (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    gym_id INT REFERENCES gyms(id) ON DELETE CASCADE,
    is_primary BOOLEAN DEFAULT TRUE,
    joined_at DATE DEFAULT CURRENT_DATE,
    expires_at DATE,
    is_active BOOLEAN DEFAULT TRUE,
    UNIQUE(user_id, gym_id)
);

-- 6. READINESS TREND MODELING
CREATE TABLE IF NOT EXISTS readiness_trends (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    calculated_at DATE NOT NULL,
    readiness_7d_avg DECIMAL(5,2),
    readiness_28d_avg DECIMAL(5,2),
    readiness_slope DECIMAL(8,4),
    readiness_volatility DECIMAL(8,4),
    recovery_7d_avg DECIMAL(5,2),
    acwr_7d_avg DECIMAL(5,3),
    acwr_trend VARCHAR(20) CHECK (acwr_trend IN (
        'increasing','decreasing','stable','volatile'
    )),
    burnout_risk_score DECIMAL(5,2),
    plateau_risk_score DECIMAL(5,2),
    anomaly_detected BOOLEAN DEFAULT FALSE,
    anomaly_type VARCHAR(50),
    notes TEXT,
    UNIQUE(user_id, calculated_at)
);

-- 7. AI COACH SESSIONS
CREATE TABLE IF NOT EXISTS ai_coach_sessions (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    session_date DATE NOT NULL DEFAULT CURRENT_DATE,
    readiness_at_time DECIMAL(5,2),
    acwr_at_time DECIMAL(5,3),
    training_zone VARCHAR(20),
    recommended_volume_multiplier DECIMAL(4,2) DEFAULT 1.0,
    recommended_intensity VARCHAR(20),
    focus_area VARCHAR(50),
    deload_recommended BOOLEAN DEFAULT FALSE,
    substitutions_applied JSONB,
    workout_generated JSONB,
    coach_message TEXT,
    user_feedback INT CHECK (user_feedback BETWEEN 1 AND 5),
    created_at TIMESTAMP DEFAULT NOW()
);

-- 8. SEED: EXERCISE BIOMECHANICS för nyckellyften
UPDATE exercises SET
    movement_plane = 'sagittal', unilateral = FALSE,
    stabilization_level = 2, spinal_load = 10,
    systemic_fatigue = 10, mobility_requirement = 4,
    force_curve = 'ascending',
    shoulder_stress = 4, knee_stress = 5, hip_stress = 9, lower_back_stress = 9, wrist_stress = 3,
    muscles_primary = ARRAY['Rygg','Ben'], muscles_secondary = ARRAY['Mage','Axlar'],
    tips = 'Håll ryggen neutral, bar nära kroppen, driv med benen.',
    common_mistakes = 'Rundad rygg, bar för långt från kroppen, för snabb rörelse'
WHERE name = 'Marklyft';

UPDATE exercises SET
    movement_plane = 'sagittal', unilateral = FALSE,
    stabilization_level = 3, spinal_load = 9,
    systemic_fatigue = 9, mobility_requirement = 5,
    force_curve = 'ascending',
    shoulder_stress = 3, knee_stress = 8, hip_stress = 7, lower_back_stress = 7, wrist_stress = 2,
    muscles_primary = ARRAY['Ben'], muscles_secondary = ARRAY['Rygg','Mage'],
    tips = 'Knäna i linje med tårna, hälar i marken, bröst upp.',
    common_mistakes = 'Knäna kollapsar inåt, hälar lyfts, för grund rörelse'
WHERE name = 'Knäböj';

UPDATE exercises SET
    movement_plane = 'sagittal', unilateral = FALSE,
    stabilization_level = 2, spinal_load = 4,
    systemic_fatigue = 7, mobility_requirement = 2,
    force_curve = 'descending',
    shoulder_stress = 8, knee_stress = 1, hip_stress = 2, lower_back_stress = 4, wrist_stress = 4,
    muscles_primary = ARRAY['Bröst'], muscles_secondary = ARRAY['Axlar','Armar'],
    tips = 'Skulderbladen ihopdragna, bar mot nedre bröstkorgen, armbågar 75°.',
    common_mistakes = 'Skulderblad utåt, bar för högt, studsande på bröstet'
WHERE name = 'Bänkpress';

UPDATE exercises SET
    movement_plane = 'sagittal', unilateral = FALSE,
    stabilization_level = 2, spinal_load = 3,
    systemic_fatigue = 6, mobility_requirement = 3,
    force_curve = 'constant',
    shoulder_stress = 5, knee_stress = 1, hip_stress = 2, lower_back_stress = 2, wrist_stress = 3,
    muscles_primary = ARRAY['Rygg'], muscles_secondary = ARRAY['Armar'],
    tips = 'Dra till bröstbenet, kläm ihop skulderbladen, kontrollera nedfasen.',
    common_mistakes = 'Drag bakom nacken, för liten rörelse, sving med kroppen'
WHERE name = 'Latsdrag';

UPDATE exercises SET
    movement_plane = 'sagittal', unilateral = FALSE,
    stabilization_level = 4, spinal_load = 7,
    systemic_fatigue = 7, mobility_requirement = 3,
    force_curve = 'ascending',
    shoulder_stress = 9, knee_stress = 1, hip_stress = 3, lower_back_stress = 6, wrist_stress = 5,
    muscles_primary = ARRAY['Axlar'], muscles_secondary = ARRAY['Armar','Bröst'],
    tips = 'Kärnan spänd, press rakt upp, kontrollera nedfasen.',
    common_mistakes = 'Svankrygg vid press, armbågar för bredt, för tung vikt'
WHERE name = 'Militärpress';

UPDATE exercises SET
    movement_plane = 'sagittal', unilateral = TRUE,
    stabilization_level = 3, spinal_load = 2,
    systemic_fatigue = 4, mobility_requirement = 3,
    force_curve = 'ascending',
    shoulder_stress = 1, knee_stress = 4, hip_stress = 5, lower_back_stress = 3, wrist_stress = 2,
    muscles_primary = ARRAY['Ben'], muscles_secondary = ARRAY['Mage'],
    tips = 'Ta ett stort steg framåt, knä rakt ner mot golvet, överkropp upprätt.',
    common_mistakes = 'Knä passerar tå, överkropp lutar, ojämn vikt'
WHERE name = 'Utfall';

UPDATE exercises SET
    movement_plane = 'sagittal', unilateral = FALSE,
    stabilization_level = 1, spinal_load = 1,
    systemic_fatigue = 3, mobility_requirement = 1,
    force_curve = 'bell_curve',
    shoulder_stress = 6, knee_stress = 1, hip_stress = 1, lower_back_stress = 1, wrist_stress = 5,
    muscles_primary = ARRAY['Armar'], muscles_secondary = ARRAY['Axlar'],
    tips = 'Armbågarna stilla, full extension nere, kläm biceps i topp.',
    common_mistakes = 'Sving med kroppen, armbågar rör sig, för tung vikt'
WHERE name = 'Bicepscurl';

-- 9. SEED: SUBSTITUTION RULES
INSERT INTO exercise_substitution_rules
    (source_exercise_id, target_exercise_id, substitution_reason,
     equivalence_score, fatigue_delta, stimulus_similarity, notes)
SELECT e1.id, e2.id, 'injury', 0.85, -3, 8,
    'Hantelpress minskar axelrotation vid axelskada'
FROM exercises e1, exercises e2
WHERE e1.name = 'Bänkpress' AND e2.name = 'Dumbbell Bench Press'
ON CONFLICT DO NOTHING;

INSERT INTO exercise_substitution_rules
    (source_exercise_id, target_exercise_id, substitution_reason,
     equivalence_score, fatigue_delta, stimulus_similarity, notes)
SELECT e1.id, e2.id, 'equipment', 0.80, -2, 7,
    'Goblet squat kräver bara en hantel'
FROM exercises e1, exercises e2
WHERE e1.name = 'Knäböj' AND e2.name = 'Utfall'
ON CONFLICT DO NOTHING;

INSERT INTO exercise_substitution_rules
    (source_exercise_id, target_exercise_id, substitution_reason,
     equivalence_score, fatigue_delta, stimulus_similarity, notes)
SELECT e1.id, e2.id, 'fatigue', 0.75, -4, 7,
    'Leg press är skonsammare för ryggen vid hög fatigue'
FROM exercises e1, exercises e2
WHERE e1.name = 'Knäböj' AND e2.name IN ('Leg Press Machine')
ON CONFLICT DO NOTHING;

INSERT INTO exercise_substitution_rules
    (source_exercise_id, target_exercise_id, substitution_reason,
     equivalence_score, fatigue_delta, stimulus_similarity, notes)
SELECT e1.id, e2.id, 'injury', 0.70, -5, 6,
    'Leg press undviker ryggbelastning vid ryggskada'
FROM exercises e1, exercises e2
WHERE e1.name = 'Marklyft' AND e2.name IN ('Leg Press Machine')
ON CONFLICT DO NOTHING;

-- 10. SEED: GYM PROFILER
INSERT INTO gyms (name, gym_type, city, description) VALUES
    ('SATS', 'commercial', 'Stockholm', 'Stort kommersiellt gym med full utrustning'),
    ('Actic', 'commercial', 'Stockholm', 'Kommersiellt gym med bra gruppträning'),
    ('Hemmagym', 'home', 'Stockholm', 'Hemmagym med basutrustning')
ON CONFLICT DO NOTHING;

-- 11. INDEXES
CREATE INDEX IF NOT EXISTS idx_substitution_rules_source
    ON exercise_substitution_rules(source_exercise_id, substitution_reason);
CREATE INDEX IF NOT EXISTS idx_readiness_trends_user
    ON readiness_trends(user_id, calculated_at DESC);
CREATE INDEX IF NOT EXISTS idx_ai_coach_sessions_user
    ON ai_coach_sessions(user_id, session_date DESC);
CREATE INDEX IF NOT EXISTS idx_gym_equipment_gym
    ON gym_equipment(gym_id);
CREATE INDEX IF NOT EXISTS idx_user_gym_memberships
    ON user_gym_memberships(user_id, is_active);

