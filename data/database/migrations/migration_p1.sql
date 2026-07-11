-- ============================================================
-- P1 MIGRATION — Database Improvements
-- Branch: feature/p1-database-improvements
-- ============================================================

-- ============================================================
-- 1. SLEEP SESSIONS (detaljerad sömndata)
-- ============================================================
CREATE TABLE IF NOT EXISTS sleep_sessions (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    bed_time TIMESTAMP,
    wake_time TIMESTAMP,
    total_sleep_minutes INT,
    deep_sleep_minutes INT DEFAULT 0,
    rem_sleep_minutes INT DEFAULT 0,
    light_sleep_minutes INT DEFAULT 0,
    awake_minutes INT DEFAULT 0,
    sleep_latency_minutes INT DEFAULT 0,
    sleep_score INT CHECK (sleep_score BETWEEN 0 AND 100),
    sleep_efficiency DECIMAL(5,2),
    notes TEXT,
    source VARCHAR(30) DEFAULT 'manual'
        CHECK (source IN ('manual', 'apple_health', 'garmin', 'fitbit', 'whoop', 'oura')),
    created_at TIMESTAMP DEFAULT NOW()
);

ALTER TABLE recovery_logs
    ADD COLUMN IF NOT EXISTS sleep_session_id INT
    REFERENCES sleep_sessions(id) ON DELETE SET NULL;

-- ============================================================
-- 2. WORKOUT SCHEDULE
-- ============================================================
CREATE TABLE IF NOT EXISTS workout_schedule (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    plan_id INT REFERENCES training_plans(id) ON DELETE SET NULL,
    planned_date DATE NOT NULL,
    workout_type VARCHAR(50) CHECK (workout_type IN (
        'strength', 'cardio', 'hiit', 'mobility', 'recovery',
        'running', 'sport', 'custom'
    )),
    title VARCHAR(100),
    notes TEXT,
    status VARCHAR(20) DEFAULT 'planned' CHECK (status IN (
        'planned', 'completed', 'skipped', 'rescheduled', 'cancelled'
    )),
    completed_at TIMESTAMP,
    session_id INT REFERENCES workout_sessions(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- 3. FATIGUE SCORES
-- ============================================================
CREATE TABLE IF NOT EXISTS fatigue_scores (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    acute_load DECIMAL(10,2) DEFAULT 0,
    chronic_load DECIMAL(10,2) DEFAULT 0,
    acwr DECIMAL(5,3) DEFAULT 0,
    fatigue_score DECIMAL(5,2) DEFAULT 0,
    recovery_score DECIMAL(5,2) DEFAULT 0,
    readiness_score DECIMAL(5,2) DEFAULT 0,
    deload_recommended BOOLEAN DEFAULT FALSE,
    training_zone VARCHAR(20) DEFAULT 'optimal' CHECK (training_zone IN (
        'undertraining', 'optimal', 'caution', 'danger'
    )),
    notes TEXT,
    calculated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, date)
);

-- ============================================================
-- 4. ACTIVITY LOGS
-- ============================================================
CREATE TABLE IF NOT EXISTS activity_logs (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE SET NULL,
    action_type VARCHAR(50) NOT NULL CHECK (action_type IN (
        'workout_completed', 'goal_created', 'goal_achieved',
        'pr_set', 'plan_assigned', 'plan_completed',
        'streak_milestone', 'challenge_joined', 'challenge_won',
        'measurement_logged', 'insight_generated', 'deload_triggered',
        'schedule_created', 'schedule_completed', 'schedule_skipped'
    )),
    entity_type VARCHAR(50),
    entity_id INT,
    description TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- 5. USER MEASUREMENTS
-- ============================================================
CREATE TABLE IF NOT EXISTS user_measurements (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    measured_at TIMESTAMP DEFAULT NOW(),
    weight_kg DECIMAL(5,2),
    body_fat_percentage DECIMAL(4,2),
    muscle_mass_kg DECIMAL(5,2),
    water_percentage DECIMAL(4,2),
    bone_mass_kg DECIMAL(4,2),
    bmi DECIMAL(4,2),
    waist_cm DECIMAL(5,2),
    chest_cm DECIMAL(5,2),
    hips_cm DECIMAL(5,2),
    neck_cm DECIMAL(5,2),
    bicep_cm DECIMAL(5,2),
    thigh_cm DECIMAL(5,2),
    calf_cm DECIMAL(5,2),
    source VARCHAR(30) DEFAULT 'manual'
        CHECK (source IN ('manual', 'scale', 'dexa', 'tape')),
    notes TEXT
);

-- ============================================================
-- 6. WEARABLE METRICS
-- ============================================================
CREATE TABLE IF NOT EXISTS wearable_sources (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    provider VARCHAR(30) NOT NULL CHECK (provider IN (
        'apple_health', 'garmin', 'fitbit', 'whoop',
        'oura', 'polar', 'suunto', 'manual'
    )),
    is_connected BOOLEAN DEFAULT FALSE,
    connected_at TIMESTAMP,
    last_synced_at TIMESTAMP,
    access_token TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, provider)
);

CREATE TABLE IF NOT EXISTS wearable_metrics (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    source_id INT REFERENCES wearable_sources(id) ON DELETE SET NULL,
    date DATE NOT NULL,
    heart_rate_resting INT,
    heart_rate_max INT,
    hrv_ms DECIMAL(6,2),
    vo2_max DECIMAL(5,2),
    steps INT,
    calories_burned INT,
    active_minutes INT,
    distance_km DECIMAL(6,2),
    floors_climbed INT,
    stress_score INT CHECK (stress_score BETWEEN 0 AND 100),
    body_battery INT CHECK (body_battery BETWEEN 0 AND 100),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, date, source_id)
);

-- ============================================================
-- 7. INJURY TRACKING
-- ============================================================
CREATE TABLE IF NOT EXISTS injuries (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    body_part VARCHAR(50) NOT NULL,
    injury_type VARCHAR(50) CHECK (injury_type IN (
        'muscle_strain', 'tendinitis', 'ligament_sprain',
        'stress_fracture', 'bursitis', 'overuse', 'acute', 'other'
    )),
    severity INT CHECK (severity BETWEEN 1 AND 5),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN (
        'active', 'recovering', 'healed', 'chronic'
    )),
    started_at DATE NOT NULL,
    healed_at DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS injury_exercise_restrictions (
    id SERIAL PRIMARY KEY,
    injury_id INT REFERENCES injuries(id) ON DELETE CASCADE,
    exercise_id INT REFERENCES exercises(id) ON DELETE CASCADE,
    restriction_level VARCHAR(20) DEFAULT 'avoid' CHECK (restriction_level IN (
        'avoid', 'modify', 'monitor'
    )),
    notes TEXT,
    UNIQUE(injury_id, exercise_id)
);

-- ============================================================
-- 8. PROGRESSION RULES
-- ============================================================
CREATE TABLE IF NOT EXISTS progression_rules (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    exercise_id INT REFERENCES exercises(id) ON DELETE CASCADE,
    condition_type VARCHAR(50) CHECK (condition_type IN (
        'rpe_below', 'rpe_above', 'all_sets_completed',
        'volume_increase', 'pr_set', 'consecutive_sessions'
    )),
    condition_value DECIMAL(6,2),
    action_type VARCHAR(50) CHECK (action_type IN (
        'increase_weight', 'decrease_weight', 'increase_reps',
        'increase_sets', 'deload', 'maintain'
    )),
    action_value DECIMAL(6,2),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS progression_log (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    rule_id INT REFERENCES progression_rules(id) ON DELETE SET NULL,
    exercise_id INT REFERENCES exercises(id) ON DELETE SET NULL,
    session_id INT REFERENCES workout_sessions(id) ON DELETE SET NULL,
    old_value DECIMAL(6,2),
    new_value DECIMAL(6,2),
    action_taken VARCHAR(50),
    applied_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- 9. EVENTS
-- ============================================================
CREATE TABLE IF NOT EXISTS events (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE SET NULL,
    event_type VARCHAR(60) NOT NULL CHECK (event_type IN (
        'workout_completed', 'pr_unlocked', 'goal_achieved',
        'streak_milestone', 'challenge_joined', 'challenge_won',
        'deload_triggered', 'plan_assigned', 'plan_completed',
        'injury_logged', 'measurement_logged', 'insight_generated',
        'schedule_missed', 'acwr_danger'
    )),
    payload JSONB,
    processed BOOLEAN DEFAULT FALSE,
    processed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- 10. EXERCISE TAGS
-- ============================================================
CREATE TABLE IF NOT EXISTS exercise_tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    category VARCHAR(30) CHECK (category IN (
        'movement_pattern', 'goal', 'equipment', 'difficulty', 'sport'
    )),
    description TEXT
);

CREATE TABLE IF NOT EXISTS exercise_tag_map (
    exercise_id INT REFERENCES exercises(id) ON DELETE CASCADE,
    tag_id INT REFERENCES exercise_tags(id) ON DELETE CASCADE,
    PRIMARY KEY (exercise_id, tag_id)
);

-- ============================================================
-- 11. MESSAGES
-- ============================================================
CREATE TABLE IF NOT EXISTS message_threads (
    id SERIAL PRIMARY KEY,
    pt_id INT REFERENCES users(id) ON DELETE CASCADE,
    client_id INT REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(pt_id, client_id)
);

CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    thread_id INT REFERENCES message_threads(id) ON DELETE CASCADE,
    sender_id INT REFERENCES users(id) ON DELETE SET NULL,
    content TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- 12. PERFORMANCE INDEXES
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_workout_sessions_user_date
    ON workout_sessions(user_id, date DESC);
CREATE INDEX IF NOT EXISTS idx_workout_exercises_session
    ON workout_exercises(session_id);
CREATE INDEX IF NOT EXISTS idx_recovery_logs_user_date
    ON recovery_logs(user_id, date DESC);
CREATE INDEX IF NOT EXISTS idx_biometrics_user_date
    ON biometrics(user_id, date DESC);
CREATE INDEX IF NOT EXISTS idx_running_sessions_user_date
    ON running_sessions(user_id, date DESC);
CREATE INDEX IF NOT EXISTS idx_meal_logs_user_date
    ON meal_logs(user_id, date DESC);
CREATE INDEX IF NOT EXISTS idx_fatigue_scores_user_date
    ON fatigue_scores(user_id, date DESC);
CREATE INDEX IF NOT EXISTS idx_sleep_sessions_user_date
    ON sleep_sessions(user_id, date DESC);
CREATE INDEX IF NOT EXISTS idx_activity_logs_user
    ON activity_logs(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_events_user_type
    ON events(user_id, event_type, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_workout_schedule_user_date
    ON workout_schedule(user_id, planned_date DESC);
CREATE INDEX IF NOT EXISTS idx_wearable_metrics_user_date
    ON wearable_metrics(user_id, date DESC);

-- ============================================================
-- 13. SEED: EXERCISE TAGS
-- ============================================================
INSERT INTO exercise_tags (name, category, description) VALUES
    ('compound', 'movement_pattern', 'Multi-joint movements'),
    ('isolation', 'movement_pattern', 'Single-joint movements'),
    ('push', 'movement_pattern', 'Pushing movements'),
    ('pull', 'movement_pattern', 'Pulling movements'),
    ('hinge', 'movement_pattern', 'Hip hinge movements'),
    ('squat', 'movement_pattern', 'Squat pattern'),
    ('carry', 'movement_pattern', 'Loaded carry'),
    ('hypertrophy', 'goal', 'Muscle building focus'),
    ('strength', 'goal', 'Max strength focus'),
    ('endurance', 'goal', 'Muscular endurance'),
    ('mobility', 'goal', 'Flexibility and mobility'),
    ('rehab', 'goal', 'Rehabilitation exercises'),
    ('barbell', 'equipment', 'Requires barbell'),
    ('dumbbell', 'equipment', 'Requires dumbbells'),
    ('bodyweight', 'equipment', 'No equipment needed'),
    ('cable', 'equipment', 'Cable machine'),
    ('kettlebell', 'equipment', 'Kettlebell'),
    ('beginner_friendly', 'difficulty', 'Safe for beginners'),
    ('advanced', 'difficulty', 'Advanced technique required')
ON CONFLICT (name) DO NOTHING;

-- ============================================================
-- 14. SEED: PROGRESSION RULES
-- ============================================================
INSERT INTO progression_rules
    (name, description, condition_type, condition_value, action_type, action_value)
VALUES
    (
        'Double Progression — Add weight when RPE < 7',
        'If all sets completed and RPE below 7, increase weight by 2.5kg',
        'rpe_below', 7.0, 'increase_weight', 2.5
    ),
    (
        'Deload trigger — RPE > 9',
        'If RPE above 9, reduce weight by 10%',
        'rpe_above', 9.0, 'decrease_weight', 10.0
    ),
    (
        'Volume progression — Increase reps',
        'If all sets completed at target weight, add 1 rep',
        'all_sets_completed', 1.0, 'increase_reps', 1.0
    )
ON CONFLICT DO NOTHING;
