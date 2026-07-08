-- ============================================================
-- P2 MIGRATION — Full Platform Upgrade
-- ============================================================

-- ============================================================
-- 1. NUTRITION SYSTEM
-- ============================================================
CREATE TABLE IF NOT EXISTS recipes (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    instructions TEXT,
    prep_time_minutes INT DEFAULT 0,
    cook_time_minutes INT DEFAULT 0,
    servings INT DEFAULT 1,
    calories_per_serving DECIMAL(8,2),
    protein_per_serving DECIMAL(6,2),
    carbs_per_serving DECIMAL(6,2),
    fat_per_serving DECIMAL(6,2),
    goal_tag VARCHAR(30) CHECK (goal_tag IN (
        'muscle_gain', 'fat_loss', 'maintenance',
        'performance', 'recovery', 'any'
    )) DEFAULT 'any',
    difficulty VARCHAR(20) CHECK (difficulty IN ('easy', 'medium', 'hard')) DEFAULT 'easy',
    is_public BOOLEAN DEFAULT TRUE,
    created_by INT REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS recipe_foods (
    id SERIAL PRIMARY KEY,
    recipe_id INT REFERENCES recipes(id) ON DELETE CASCADE,
    food_id INT REFERENCES foods(id) ON DELETE CASCADE,
    amount_g DECIMAL(8,2) NOT NULL,
    notes TEXT,
    UNIQUE(recipe_id, food_id)
);

CREATE TABLE IF NOT EXISTS nutrition_targets (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    goal_phase VARCHAR(30) CHECK (goal_phase IN (
        'bulk', 'cut', 'maintenance', 'recomp', 'performance'
    )) DEFAULT 'maintenance',
    calories_target INT NOT NULL,
    protein_g DECIMAL(6,2) NOT NULL,
    carbs_g DECIMAL(6,2) NOT NULL,
    fat_g DECIMAL(6,2) NOT NULL,
    fiber_g DECIMAL(6,2) DEFAULT 25,
    water_ml INT DEFAULT 3000,
    meal_frequency INT DEFAULT 3,
    is_active BOOLEAN DEFAULT TRUE,
    valid_from DATE DEFAULT CURRENT_DATE,
    valid_until DATE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS food_logs (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    food_id INT REFERENCES foods(id) ON DELETE SET NULL,
    recipe_id INT REFERENCES recipes(id) ON DELETE SET NULL,
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    meal_type VARCHAR(20) CHECK (meal_type IN (
        'breakfast', 'lunch', 'dinner', 'snack',
        'pre_workout', 'post_workout', 'supplement'
    )) NOT NULL,
    amount_g DECIMAL(8,2) NOT NULL,
    calories DECIMAL(8,2),
    protein_g DECIMAL(6,2),
    carbs_g DECIMAL(6,2),
    fat_g DECIMAL(6,2),
    fiber_g DECIMAL(6,2),
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- 2. PROGRAM DESIGN ENGINE
-- ============================================================
CREATE TABLE IF NOT EXISTS training_blocks (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    plan_id INT REFERENCES training_plans(id) ON DELETE SET NULL,
    name VARCHAR(100) NOT NULL,
    block_type VARCHAR(30) CHECK (block_type IN (
        'accumulation', 'intensification', 'realization',
        'deload', 'hypertrophy', 'strength', 'power', 'endurance'
    )) NOT NULL,
    duration_weeks INT NOT NULL DEFAULT 4,
    start_date DATE,
    end_date DATE,
    target_rpe_min DECIMAL(3,1) DEFAULT 6.0,
    target_rpe_max DECIMAL(3,1) DEFAULT 8.5,
    target_weekly_sets INT DEFAULT 15,
    notes TEXT,
    is_active BOOLEAN DEFAULT FALSE,
    is_completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS training_weeks (
    id SERIAL PRIMARY KEY,
    block_id INT REFERENCES training_blocks(id) ON DELETE CASCADE,
    week_number INT NOT NULL,
    target_volume_multiplier DECIMAL(4,2) DEFAULT 1.0,
    target_intensity_multiplier DECIMAL(4,2) DEFAULT 1.0,
    is_deload BOOLEAN DEFAULT FALSE,
    focus VARCHAR(100),
    notes TEXT,
    UNIQUE(block_id, week_number)
);

CREATE TABLE IF NOT EXISTS planned_exercises (
    id SERIAL PRIMARY KEY,
    week_id INT REFERENCES training_weeks(id) ON DELETE CASCADE,
    exercise_id INT REFERENCES exercises(id) ON DELETE CASCADE,
    day_number INT NOT NULL CHECK (day_number BETWEEN 1 AND 7),
    order_index INT DEFAULT 0,
    planned_sets INT NOT NULL DEFAULT 3,
    planned_reps_min INT DEFAULT 6,
    planned_reps_max INT DEFAULT 12,
    planned_weight_kg DECIMAL(6,2),
    planned_rpe DECIMAL(3,1),
    rest_seconds INT DEFAULT 120,
    notes TEXT,
    is_completed BOOLEAN DEFAULT FALSE,
    actual_sets INT,
    actual_reps INT,
    actual_weight_kg DECIMAL(6,2),
    actual_rpe DECIMAL(3,1),
    completed_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS exercise_substitutions (
    id SERIAL PRIMARY KEY,
    original_exercise_id INT REFERENCES exercises(id) ON DELETE CASCADE,
    substitute_exercise_id INT REFERENCES exercises(id) ON DELETE CASCADE,
    reason VARCHAR(100) CHECK (reason IN (
        'injury', 'equipment_unavailable', 'difficulty',
        'preference', 'progression', 'deload'
    )),
    similarity_score DECIMAL(3,2) DEFAULT 0.8,
    notes TEXT,
    UNIQUE(original_exercise_id, substitute_exercise_id)
);

-- ============================================================
-- 3. EXERCISE METADATA
-- ============================================================
ALTER TABLE exercises ADD COLUMN IF NOT EXISTS movement_pattern VARCHAR(30)
    CHECK (movement_pattern IN (
        'squat', 'hinge', 'push_horizontal', 'push_vertical',
        'pull_horizontal', 'pull_vertical', 'carry', 'rotation',
        'isolation', 'cardio', 'mobility'
    ));
ALTER TABLE exercises ADD COLUMN IF NOT EXISTS force_type VARCHAR(20)
    CHECK (force_type IN ('compound', 'isolation', 'unilateral', 'bilateral'));
ALTER TABLE exercises ADD COLUMN IF NOT EXISTS is_unilateral BOOLEAN DEFAULT FALSE;
ALTER TABLE exercises ADD COLUMN IF NOT EXISTS fatigue_score DECIMAL(3,1)
    CHECK (fatigue_score BETWEEN 1 AND 10);
ALTER TABLE exercises ADD COLUMN IF NOT EXISTS stimulus_to_fatigue_ratio DECIMAL(3,1)
    CHECK (stimulus_to_fatigue_ratio BETWEEN 0.1 AND 3.0);
ALTER TABLE exercises ADD COLUMN IF NOT EXISTS skill_requirement INT
    CHECK (skill_requirement BETWEEN 1 AND 5);
ALTER TABLE exercises ADD COLUMN IF NOT EXISTS is_compound BOOLEAN DEFAULT FALSE;
ALTER TABLE exercises ADD COLUMN IF NOT EXISTS primary_muscle_group VARCHAR(50);
ALTER TABLE exercises ADD COLUMN IF NOT EXISTS secondary_muscle_groups TEXT[];
ALTER TABLE exercises ADD COLUMN IF NOT EXISTS video_url VARCHAR(255);

-- ============================================================
-- 4. ML FEATURE STORE
-- ============================================================
CREATE TABLE IF NOT EXISTS user_daily_features (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    sleep_hours_7d_avg DECIMAL(4,2),
    sleep_quality_7d_avg DECIMAL(4,2),
    sleep_consistency_score DECIMAL(5,2),
    volume_7d DECIMAL(12,2),
    volume_28d_avg DECIMAL(12,2),
    sessions_7d INT,
    avg_rpe_7d DECIMAL(4,2),
    acwr DECIMAL(5,3),
    training_zone VARCHAR(20),
    recovery_score DECIMAL(5,2),
    readiness_score DECIMAL(5,2),
    stress_7d_avg DECIMAL(4,2),
    energy_7d_avg DECIMAL(4,2),
    hrv_7d_avg DECIMAL(6,2),
    resting_hr_7d_avg DECIMAL(5,2),
    weight_trend DECIMAL(5,2),
    body_fat_trend DECIMAL(5,2),
    calories_7d_avg DECIMAL(8,2),
    protein_7d_avg DECIMAL(6,2),
    calorie_target_adherence DECIMAL(5,2),
    protein_target_adherence DECIMAL(5,2),
    days_since_last_workout INT,
    streak_current INT,
    workout_consistency_30d DECIMAL(5,2),
    calculated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, date)
);

CREATE TABLE IF NOT EXISTS model_predictions (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    model_version VARCHAR(20) DEFAULT 'v1.0',
    injury_risk_score DECIMAL(5,2),
    dropout_risk_score DECIMAL(5,2),
    plateau_risk_score DECIMAL(5,2),
    overtraining_risk_score DECIMAL(5,2),
    recommended_intensity VARCHAR(20) CHECK (recommended_intensity IN (
        'rest', 'very_light', 'light', 'moderate', 'hard', 'very_hard'
    )),
    recommended_volume_multiplier DECIMAL(4,2) DEFAULT 1.0,
    primary_recommendation TEXT,
    confidence_score DECIMAL(5,2),
    features_used JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, date, model_version)
);

-- ============================================================
-- 5. DB IMPROVEMENTS
-- ============================================================
ALTER TABLE users ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT NOW();
ALTER TABLE workout_sessions ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT NOW();
ALTER TABLE workout_exercises ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT NOW();
ALTER TABLE recovery_logs ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT NOW();
ALTER TABLE user_goals ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT NOW();
ALTER TABLE training_plans ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT NOW();
ALTER TABLE exercises ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT NOW();
ALTER TABLE users ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP;
ALTER TABLE workout_sessions ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP;
ALTER TABLE training_plans ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP;

-- ============================================================
-- 6. INDEXES
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_food_logs_user_date ON food_logs(user_id, date DESC);
CREATE INDEX IF NOT EXISTS idx_training_blocks_user ON training_blocks(user_id, is_active);
CREATE INDEX IF NOT EXISTS idx_planned_exercises_week ON planned_exercises(week_id, day_number);
CREATE INDEX IF NOT EXISTS idx_user_daily_features_user_date ON user_daily_features(user_id, date DESC);
CREATE INDEX IF NOT EXISTS idx_model_predictions_user_date ON model_predictions(user_id, date DESC);
CREATE INDEX IF NOT EXISTS idx_recipes_goal ON recipes(goal_tag, difficulty);
CREATE INDEX IF NOT EXISTS idx_exercises_movement ON exercises(movement_pattern, force_type);

-- ============================================================
-- 7. MATERIALIZED VIEWS
-- ============================================================
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_user_weekly_volume AS
SELECT
    ws.user_id,
    u.name AS user_name,
    DATE_TRUNC('week', ws.date)::DATE AS week_start,
    TO_CHAR(ws.date, 'IYYY-"W"IW') AS week_label,
    COUNT(DISTINCT ws.id) AS sessions,
    SUM(we.sets * we.reps * COALESCE(we.weight_kg, 0)) AS total_volume_kg,
    AVG(we.rpe) AS avg_rpe,
    SUM(we.sets) AS total_sets
FROM workout_sessions ws
JOIN workout_exercises we ON ws.id = we.session_id
JOIN users u ON ws.user_id = u.id
GROUP BY ws.user_id, u.name,
    DATE_TRUNC('week', ws.date),
    TO_CHAR(ws.date, 'IYYY-"W"IW')
ORDER BY ws.user_id, week_start;

CREATE MATERIALIZED VIEW IF NOT EXISTS mv_readiness_trends AS
SELECT
    fs.user_id,
    u.name AS user_name,
    fs.date,
    fs.acwr,
    fs.training_zone,
    fs.readiness_score,
    fs.recovery_score,
    fs.fatigue_score,
    fs.deload_recommended,
    rl.sleep_hours,
    rl.energy_level,
    rl.stress_level
FROM fatigue_scores fs
JOIN users u ON fs.user_id = u.id
LEFT JOIN recovery_logs rl ON fs.user_id = rl.user_id AND fs.date = rl.date
ORDER BY fs.user_id, fs.date;

CREATE MATERIALIZED VIEW IF NOT EXISTS mv_pr_progression AS
SELECT
    pr.user_id,
    u.name AS user_name,
    e.name AS exercise_name,
    bp.name AS body_part,
    pr.weight_kg AS pr_weight,
    pr.reps,
    pr.date AS pr_date,
    ROW_NUMBER() OVER (
        PARTITION BY pr.user_id, pr.exercise_id
        ORDER BY pr.date
    ) AS pr_number
FROM personal_records pr
JOIN users u ON pr.user_id = u.id
JOIN exercises e ON pr.exercise_id = e.id
JOIN body_parts bp ON e.body_part_id = bp.id
ORDER BY pr.user_id, e.name, pr.date;

CREATE MATERIALIZED VIEW IF NOT EXISTS mv_fatigue_dashboard AS
SELECT
    u.id AS user_id,
    u.name AS user_name,
    u.fitness_goal,
    u.fitness_level,
    fs.date AS last_calculated,
    fs.acwr,
    fs.training_zone,
    fs.readiness_score,
    fs.recovery_score,
    fs.fatigue_score,
    fs.deload_recommended,
    us.current_streak,
    us.longest_streak,
    us.total_workouts,
    (SELECT MAX(ws2.date) FROM workout_sessions ws2
     WHERE ws2.user_id = u.id) AS last_workout_date,
    (SELECT COUNT(*) FROM user_goals ug
     WHERE ug.user_id = u.id AND ug.is_achieved = FALSE) AS active_goals
FROM users u
LEFT JOIN fatigue_scores fs ON u.id = fs.user_id
    AND fs.date = (
        SELECT MAX(fs2.date) FROM fatigue_scores fs2
        WHERE fs2.user_id = u.id
    )
LEFT JOIN user_streaks us ON u.id = us.user_id
WHERE u.role = 'user' OR u.role IS NULL
ORDER BY fs.readiness_score ASC NULLS LAST;

-- ============================================================
-- 8. SEED: EXERCISE METADATA
-- ============================================================
UPDATE exercises SET movement_pattern='push_horizontal', force_type='compound',
    is_compound=TRUE, fatigue_score=7.5, stimulus_to_fatigue_ratio=1.2,
    skill_requirement=2, primary_muscle_group='Bröst',
    secondary_muscle_groups=ARRAY['Axlar','Armar']
WHERE name='Bänkpress';

UPDATE exercises SET movement_pattern='hinge', force_type='compound',
    is_compound=TRUE, fatigue_score=9.5, stimulus_to_fatigue_ratio=0.8,
    skill_requirement=5, primary_muscle_group='Rygg',
    secondary_muscle_groups=ARRAY['Ben','Mage']
WHERE name='Marklyft';

UPDATE exercises SET movement_pattern='squat', force_type='compound',
    is_compound=TRUE, fatigue_score=9.0, stimulus_to_fatigue_ratio=1.0,
    skill_requirement=4, primary_muscle_group='Ben',
    secondary_muscle_groups=ARRAY['Mage','Rygg']
WHERE name='Knäböj';

UPDATE exercises SET movement_pattern='pull_vertical', force_type='compound',
    is_compound=TRUE, fatigue_score=6.0, stimulus_to_fatigue_ratio=1.5,
    skill_requirement=2, primary_muscle_group='Rygg',
    secondary_muscle_groups=ARRAY['Armar']
WHERE name='Latsdrag';

UPDATE exercises SET movement_pattern='push_vertical', force_type='compound',
    is_compound=TRUE, fatigue_score=7.0, stimulus_to_fatigue_ratio=1.1,
    skill_requirement=3, primary_muscle_group='Axlar',
    secondary_muscle_groups=ARRAY['Armar','Bröst']
WHERE name='Militärpress';

UPDATE exercises SET movement_pattern='isolation', force_type='isolation',
    is_compound=FALSE, fatigue_score=3.5, stimulus_to_fatigue_ratio=2.0,
    skill_requirement=1, primary_muscle_group='Armar'
WHERE name='Bicepscurl';

-- ============================================================
-- 9. SEED: RECIPES
-- ============================================================
INSERT INTO recipes (name, description, prep_time_minutes, cook_time_minutes,
    servings, calories_per_serving, protein_per_serving,
    carbs_per_serving, fat_per_serving, goal_tag, difficulty)
VALUES
    ('High-Protein Overnight Oats', 'Frukost med hög proteinhalt',
     5, 0, 1, 485, 38, 52, 12, 'muscle_gain', 'easy'),
    ('Kycklingbröst med sötpotatis', 'Klassisk måltid för prestation',
     10, 30, 2, 520, 48, 45, 8, 'performance', 'easy'),
    ('Lax med quinoa', 'Omega-3 rikt för återhämtning',
     5, 20, 2, 580, 42, 38, 18, 'recovery', 'easy'),
    ('Proteinsmoothie', 'Snabb post-workout shake',
     5, 0, 1, 380, 35, 42, 8, 'muscle_gain', 'easy'),
    ('Äggmacka med avokado', 'Proteinrik frukost',
     10, 8, 1, 420, 22, 28, 24, 'maintenance', 'easy')
ON CONFLICT DO NOTHING;

-- ============================================================
-- 10. SEED: EXERCISE SUBSTITUTIONS
-- ============================================================
INSERT INTO exercise_substitutions
    (original_exercise_id, substitute_exercise_id, reason, similarity_score, notes)
SELECT e1.id, e2.id, 'injury', 0.85, 'Skonsammare för axlarna'
FROM exercises e1, exercises e2
WHERE e1.name='Bänkpress' AND e2.name='Hantelflyes'
ON CONFLICT DO NOTHING;

INSERT INTO exercise_substitutions
    (original_exercise_id, substitute_exercise_id, reason, similarity_score, notes)
SELECT e1.id, e2.id, 'equipment_unavailable', 0.80, 'Bra alternativ utan stativ'
FROM exercises e1, exercises e2
WHERE e1.name='Knäböj' AND e2.name='Utfall'
ON CONFLICT DO NOTHING;
