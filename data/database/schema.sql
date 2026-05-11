
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    password_hash VARCHAR(255),
    age INT,
    weight_kg DECIMAL(5,2),
    height_cm DECIMAL(5,2),
    fitness_level VARCHAR(20) CHECK (fitness_level IN ('nybörjare', 'medel', 'avancerad')),
    goal VARCHAR(50) CHECK (goal IN ('bygga_muskler', 'gå_ner_i_vikt', 'öka_kondition', 'hålla_sig_i_form')),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE body_parts (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50),
    description TEXT
);

CREATE TABLE muscle_groups (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50),           
    body_part_id INT REFERENCES body_parts(id)
);

CREATE TABLE equipment (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50)            
);

CREATE TABLE exercises (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    body_part_id INT REFERENCES body_parts(id),
    muscle_group_id INT REFERENCES muscle_groups(id),
    equipment_id INT REFERENCES equipment(id),
    difficulty VARCHAR(20) CHECK (difficulty IN ('nybörjare', 'medel', 'avancerad')),
    exercise_type VARCHAR(30) CHECK (exercise_type IN ('styrka', 'kondition', 'stretching', 'balans')),
    description TEXT,
    instructions TEXT,          
    tips TEXT,                  
    calories_per_minute DECIMAL(4,2)
);

CREATE TABLE workout_programs (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),          
    description TEXT,
    difficulty VARCHAR(20),
    duration_weeks INT,
    days_per_week INT,
    goal VARCHAR(50)
);

CREATE TABLE workout_templates (
    id SERIAL PRIMARY KEY,
    program_id INT REFERENCES workout_programs(id),
    name VARCHAR(100),          
    day_of_week VARCHAR(20)
);

CREATE TABLE template_exercises (
    id SERIAL PRIMARY KEY,
    template_id INT REFERENCES workout_templates(id),
    exercise_id INT REFERENCES exercises(id),
    sets INT,
    reps INT,
    rest_seconds INT,
    order_index INT             
);

CREATE TABLE workout_sessions (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    template_id INT REFERENCES workout_templates(id),
    date DATE,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    duration_minutes INT,
    total_calories INT,
    mood VARCHAR(20) CHECK (mood IN ('bra', 'okej', 'trött', 'stark')),
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE workout_exercises (
    id SERIAL PRIMARY KEY,
    session_id INT REFERENCES workout_sessions(id),
    exercise_id INT REFERENCES exercises(id),
    sets INT,
    reps INT,
    weight_kg DECIMAL(5,2),
    duration_seconds INT,       
    rest_seconds INT,
    rpe INT CHECK (rpe BETWEEN 1 AND 10),  
    notes TEXT
);

CREATE TABLE user_progress (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    date DATE,
    weight_kg DECIMAL(5,2),
    body_fat_percentage DECIMAL(4,2),
    chest_cm DECIMAL(5,2),
    waist_cm DECIMAL(5,2),
    hips_cm DECIMAL(5,2),
    bicep_cm DECIMAL(5,2),
    thigh_cm DECIMAL(5,2)
);

CREATE TABLE personal_records (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    exercise_id INT REFERENCES exercises(id),
    weight_kg DECIMAL(5,2),
    reps INT,
    date DATE,
    notes TEXT
);


CREATE TABLE recommendations (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    exercise_id INT REFERENCES exercises(id),
    reason TEXT,                
    score DECIMAL(4,2),        
    created_at TIMESTAMP DEFAULT NOW(),
    is_seen BOOLEAN DEFAULT FALSE
);

INSERT INTO body_parts (name, description) VALUES
    ('Bröst', 'Främre överkropp'),
    ('Rygg', 'Bakre överkropp'),
    ('Ben', 'Underkropp'),
    ('Axlar', 'Skulderparti'),
    ('Armar', 'Biceps och triceps'),
    ('Mage', 'Core och bålmuskulatur'),
    ('Kondition', 'Cardio och uthållighet');


INSERT INTO equipment (name) VALUES
    ('Kroppsvikt'),
    ('Hantlar'),
    ('Skivstång'),
    ('Kabelmaskin'),
    ('Resistansband'),
    ('Kettlebell');

INSERT INTO exercises (name, body_part_id, equipment_id, difficulty, exercise_type, description, tips, calories_per_minute) VALUES
    ('Bänkpress',       1, 3, 'medel',     'styrka',   'Ligg på bänk och pressa stången uppåt', 'Håll skulderbladen ihop', 8.0),
    ('Hantelflyes',     1, 2, 'nybörjare', 'styrka',   'Öppna armarna med hantlar liggande', 'Håll lätt böjda armar', 6.0),
    ('Marklyft',        2, 3, 'avancerad', 'styrka',   'Lyft stången från golvet', 'Håll ryggen rak hela tiden', 10.0),
    ('Latsdrag',        2, 4, 'medel',     'styrka',   'Dra stången nedåt mot bröstet', 'Dra med armbågarna', 7.0),
    ('Knäböj',          3, 3, 'medel',     'styrka',   'Böj knäna med stången på ryggen', 'Knäna i linje med tårna', 9.0),
    ('Utfall',          3, 2, 'nybörjare', 'styrka',   'Ta ett stort steg framåt', 'Håll överkroppen upprätt', 7.0),
    ('Militärpress',    4, 3, 'medel',     'styrka',   'Pressa stången rakt upp', 'Spänn magen under rörelsen', 8.0),
    ('Bicepscurl',      5, 2, 'nybörjare', 'styrka',   'Curl hantlarna mot axlarna', 'Rör inte armbågarna', 5.0),
    ('Tricepspress',    5, 4, 'nybörjare', 'styrka',   'Pressa ned med triceps', 'Håll armbågarna stilla', 5.0),
    ('Plankan',         6, 1, 'nybörjare', 'balans',   'Håll kroppen rak', 'Andas jämnt, spänn magen', 4.0),
    ('Löpning',         7, 1, 'nybörjare', 'kondition','Löp i jämnt tempo', 'Landa på midfoten', 11.0),
    ('Burpees',         7, 1, 'medel',     'kondition','Kombination av squat, planka och hopp', 'Håll jämnt tempo', 12.0);

-- =====================
-- ANVÄNDARPROFIL (utökad)
-- =====================
ALTER TABLE users ADD COLUMN IF NOT EXISTS age INT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS weight_kg DECIMAL(5,2);
ALTER TABLE users ADD COLUMN IF NOT EXISTS height_cm DECIMAL(5,2);
ALTER TABLE users ADD COLUMN IF NOT EXISTS fitness_goal VARCHAR(50) 
    CHECK (fitness_goal IN ('bygga_muskler', 'gå_ner_i_vikt', 'öka_kondition', 'hålla_sig_i_form'));
ALTER TABLE users ADD COLUMN IF NOT EXISTS experience_level VARCHAR(20)
    CHECK (experience_level IN ('nybörjare', 'medel', 'avancerad'));

-- =====================
-- SÖMNDATA & ÅTERHÄMTNING
-- =====================
CREATE TABLE IF NOT EXISTS recovery_logs (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    date DATE,
    sleep_hours DECIMAL(4,1),
    sleep_quality INT CHECK (sleep_quality BETWEEN 1 AND 10),
    stress_level INT CHECK (stress_level BETWEEN 1 AND 10),
    energy_level INT CHECK (energy_level BETWEEN 1 AND 10),
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- =====================
-- KROPPSMÅTT ÖVER TID
-- =====================
CREATE TABLE IF NOT EXISTS body_measurements (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    date DATE,
    weight_kg DECIMAL(5,2),
    body_fat_percentage DECIMAL(4,2),
    muscle_mass_kg DECIMAL(5,2),
    chest_cm DECIMAL(5,2),
    waist_cm DECIMAL(5,2),
    hips_cm DECIMAL(5,2),
    bicep_cm DECIMAL(5,2),
    thigh_cm DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT NOW()
);

-- =====================
-- TRÄNINGSINTENSITET ÖVER TID
-- =====================
CREATE TABLE IF NOT EXISTS workout_intensity_log (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    week_number INT,
    year INT,
    total_sessions INT,
    total_volume_kg DECIMAL(10,2),
    avg_rpe DECIMAL(4,2),
    total_minutes INT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- =====================
-- SEED: TESTDATA FÖR ÅTERHÄMTNING
-- =====================
INSERT INTO recovery_logs (user_id, date, sleep_hours, sleep_quality, stress_level, energy_level) VALUES
    (1, '2026-04-01', 7.5, 8, 3, 8),
    (1, '2026-04-05', 6.0, 5, 7, 5),
    (1, '2026-04-10', 8.0, 9, 2, 9);

-- =====================
-- SEED: TESTDATA FÖR KROPPSMÅTT
-- =====================
INSERT INTO body_measurements (user_id, date, weight_kg, body_fat_percentage, chest_cm, waist_cm, bicep_cm) VALUES
    (1, '2026-04-01', 80.0, 18.0, 100.0, 85.0, 38.0),
    (1, '2026-04-15', 79.5, 17.5, 101.0, 84.0, 38.5);

-- =====================
-- BIOMETRICS (steps, heart rate, cardio)
-- =====================
CREATE TABLE IF NOT EXISTS biometrics (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    date DATE,
    steps INT,
    heart_rate_resting INT,
    heart_rate_avg INT,
    heart_rate_max INT,
    heart_rate_post_workout INT,
    heart_rate_recovery_1min INT,
    vo2_max DECIMAL(5,2),
    calories_burned INT,
    active_minutes INT,
    distance_km DECIMAL(6,2),
    created_at TIMESTAMP DEFAULT NOW()
);

-- =====================
-- RUNNING SESSIONS (löpning utomhus/löpband)
-- =====================
CREATE TABLE IF NOT EXISTS running_sessions (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    date DATE,
    distance_km DECIMAL(6,2),
    duration_minutes INT,
    avg_pace_min_per_km DECIMAL(5,2),
    avg_heart_rate INT,
    max_heart_rate INT,
    calories_burned INT,
    route_type VARCHAR(30) CHECK (route_type IN ('utomhus', 'löpband', 'spår')),
    elevation_m INT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- =====================
-- NUTRITION (mat och kalorier)
-- =====================
CREATE TABLE IF NOT EXISTS nutrition_logs (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    date DATE,
    calories_consumed INT,
    protein_g DECIMAL(6,2),
    carbs_g DECIMAL(6,2),
    fat_g DECIMAL(6,2),
    water_ml INT,
    meal_type VARCHAR(20) CHECK (meal_type IN ('frukost', 'lunch', 'middag', 'mellanmål')),
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- =====================
-- TRÄNINGSSCHEMA (program för mål)
-- =====================
CREATE TABLE IF NOT EXISTS training_plans (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    goal VARCHAR(50) CHECK (goal IN (
        'bygga_muskler', 
        'gå_ner_i_vikt', 
        'gå_upp_i_vikt', 
        'öka_kondition', 
        'hålla_sig_i_form',
        'löpning'
    )),
    difficulty VARCHAR(20) CHECK (difficulty IN ('nybörjare', 'medel', 'avancerad')),
    duration_weeks INT,
    days_per_week INT,
    description TEXT,
    target_audience TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- =====================
-- TRÄNINGSSCHEMA DAGAR
-- =====================
CREATE TABLE IF NOT EXISTS training_plan_days (
    id SERIAL PRIMARY KEY,
    plan_id INT REFERENCES training_plans(id),
    week_number INT,
    day_number INT,
    day_name VARCHAR(50),
    focus VARCHAR(100),
    rest_day BOOLEAN DEFAULT FALSE
);

-- =====================
-- ÖVNINGAR I SCHEMA
-- =====================
CREATE TABLE IF NOT EXISTS training_plan_exercises (
    id SERIAL PRIMARY KEY,
    plan_day_id INT REFERENCES training_plan_days(id),
    exercise_id INT REFERENCES exercises(id),
    sets INT,
    reps INT,
    rest_seconds INT,
    intensity VARCHAR(20),
    notes TEXT,
    order_index INT
);

-- =====================
-- ANVÄNDARENS AKTIVA SCHEMA
-- =====================
CREATE TABLE IF NOT EXISTS user_training_plans (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    plan_id INT REFERENCES training_plans(id),
    start_date DATE,
    end_date DATE,
    current_week INT DEFAULT 1,
    current_day INT DEFAULT 1,
    is_active BOOLEAN DEFAULT TRUE,
    progress_percentage DECIMAL(5,2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- =====================
-- GOALS (användarmål med deadline)
-- =====================
CREATE TABLE IF NOT EXISTS user_goals (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    goal_type VARCHAR(50) CHECK (goal_type IN (
        'target_weight',
        'target_body_fat',
        'target_muscle_mass',
        'run_distance',
        'lift_weight',
        'workout_streak'
    )),
    target_value DECIMAL(8,2),
    current_value DECIMAL(8,2),
    unit VARCHAR(20),
    deadline DATE,
    is_achieved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- =====================
-- SEED: TRÄNINGSPLANER
-- =====================
INSERT INTO training_plans (name, goal, difficulty, duration_weeks, days_per_week, description, target_audience) VALUES
    (
        'Muscle Builder 12 Week',
        'bygga_muskler',
        'medel',
        12,
        4,
        'A progressive 12-week program focused on hypertrophy with compound and isolation movements.',
        'Intermediate lifters who want to build muscle mass'
    ),
    (
        'Fat Loss 8 Week',
        'gå_ner_i_vikt',
        'nybörjare',
        8,
        5,
        'High intensity program combining strength and cardio to maximize fat burn.',
        'Beginners and intermediates looking to lose body fat'
    ),
    (
        'Bulk Up 10 Week',
        'gå_upp_i_vikt',
        'avancerad',
        10,
        5,
        'Heavy compound movements with progressive overload to maximize muscle and strength gains.',
        'Advanced lifters looking to gain weight and strength'
    ),
    (
        '5K Running Plan',
        'löpning',
        'nybörjare',
        8,
        3,
        'A beginner-friendly plan to go from walking to running 5km without stopping.',
        'Complete beginners who want to start running'
    ),
    (
        'Stay Fit Plan',
        'hålla_sig_i_form',
        'nybörjare',
        0,
        3,
        'A maintenance program combining strength and cardio to stay healthy and active.',
        'Anyone who wants to maintain their fitness level'
    );

-- =====================
-- SEED: BIOMETRICS TESTDATA
-- =====================
INSERT INTO biometrics (user_id, date, steps, heart_rate_resting, heart_rate_avg, calories_burned, active_minutes, distance_km) VALUES
    (1, '2026-04-01', 8500, 62, 75, 2400, 45, 6.2),
    (1, '2026-04-05', 12000, 60, 80, 2800, 90, 9.1),
    (1, '2026-04-10', 6000, 65, 72, 2200, 30, 4.5),
    (1, '2026-04-25', 15000, 58, 85, 3100, 120, 11.3);

-- =====================
-- SEED: LÖPNING TESTDATA
-- =====================
INSERT INTO running_sessions (user_id, date, distance_km, duration_minutes, avg_pace_min_per_km, avg_heart_rate, calories_burned, route_type) VALUES
    (1, '2026-04-03', 5.0, 28, 5.6, 155, 350, 'utomhus'),
    (1, '2026-04-08', 7.5, 42, 5.6, 160, 520, 'utomhus'),
    (1, '2026-04-12', 5.0, 27, 5.4, 150, 340, 'löpband');

-- =====================
-- SEED: ANVÄNDARMÅL
-- =====================
INSERT INTO user_goals (user_id, goal_type, target_value, current_value, unit, deadline) VALUES
    (1, 'target_weight', 75.0, 80.0, 'kg', '2026-08-01'),
    (1, 'target_body_fat', 12.0, 18.0, '%', '2026-08-01'),
    (1, 'run_distance', 10.0, 7.5, 'km', '2026-06-01'),
    (1, 'lift_weight', 200.0, 150.0, 'kg', '2026-12-01');

-- =====================
-- NUTRITION - LIVSMEDEL
-- =====================
CREATE TABLE IF NOT EXISTS foods (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    brand VARCHAR(100),
    calories_per_100g DECIMAL(6,2),
    protein_per_100g DECIMAL(6,2),
    carbs_per_100g DECIMAL(6,2),
    fat_per_100g DECIMAL(6,2),
    fiber_per_100g DECIMAL(6,2),
    category VARCHAR(50) CHECK (category IN (
        'protein', 'kolhydrater', 'fett', 'grönsaker', 
        'frukt', 'mejeri', 'snacks', 'dryck'
    )),
    created_at TIMESTAMP DEFAULT NOW()
);

-- =====================
-- NUTRITION - MÅLTIDSLOGG
-- =====================
CREATE TABLE IF NOT EXISTS meal_logs (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    food_id INT REFERENCES foods(id),
    date DATE,
    meal_type VARCHAR(20) CHECK (meal_type IN (
        'breakfast', 'lunch', 'dinner', 'snack'
    )),
    amount_g DECIMAL(6,2),
    calories DECIMAL(6,2),
    protein_g DECIMAL(6,2),
    carbs_g DECIMAL(6,2),
    fat_g DECIMAL(6,2),
    created_at TIMESTAMP DEFAULT NOW()
);

-- =====================
-- NUTRITION - DAGLIGT MÅL
-- =====================
CREATE TABLE IF NOT EXISTS nutrition_goals (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    calories_target INT,
    protein_target_g DECIMAL(6,2),
    carbs_target_g DECIMAL(6,2),
    fat_target_g DECIMAL(6,2),
    water_target_ml INT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- =====================
-- SOCIAL - VÄNNER
-- =====================
CREATE TABLE IF NOT EXISTS friendships (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    friend_id INT REFERENCES users(id),
    status VARCHAR(20) CHECK (status IN ('pending', 'accepted', 'blocked')),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, friend_id)
);

-- =====================
-- SOCIAL - UTMANINGAR
-- =====================
CREATE TABLE IF NOT EXISTS challenges (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    description TEXT,
    challenge_type VARCHAR(50) CHECK (challenge_type IN (
        'most_steps', 'most_volume', 'most_sessions',
        'longest_streak', 'most_distance', 'weight_loss'
    )),
    start_date DATE,
    end_date DATE,
    created_by INT REFERENCES users(id),
    is_public BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- =====================
-- SOCIAL - UTMANINGSDELTAGARE
-- =====================
CREATE TABLE IF NOT EXISTS challenge_participants (
    id SERIAL PRIMARY KEY,
    challenge_id INT REFERENCES challenges(id),
    user_id INT REFERENCES users(id),
    current_value DECIMAL(10,2) DEFAULT 0,
    rank INT,
    joined_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(challenge_id, user_id)
);

-- =====================
-- SOCIAL - LEADERBOARD
-- =====================
CREATE TABLE IF NOT EXISTS leaderboard (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    week_number INT,
    year INT,
    total_sessions INT DEFAULT 0,
    total_volume_kg DECIMAL(10,2) DEFAULT 0,
    total_steps INT DEFAULT 0,
    total_distance_km DECIMAL(8,2) DEFAULT 0,
    points INT DEFAULT 0,
    rank INT,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, week_number, year)
);

-- =====================
-- SOCIAL - AKTIVITETSFLÖDE
-- =====================
CREATE TABLE IF NOT EXISTS activity_feed (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    activity_type VARCHAR(50) CHECK (activity_type IN (
        'workout_completed', 'personal_record', 'goal_achieved',
        'challenge_joined', 'challenge_won', 'streak_milestone'
    )),
    description TEXT,
    related_id INT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- =====================
-- AI - GENERERADE TRÄNINGSPLANER
-- =====================
CREATE TABLE IF NOT EXISTS ai_training_plans (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    prompt TEXT,
    plan_json JSONB,
    goal VARCHAR(100),
    duration_weeks INT,
    difficulty VARCHAR(20),
    is_active BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- =====================
-- AI - GENERERADE KOSTPLANER
-- =====================
CREATE TABLE IF NOT EXISTS ai_nutrition_plans (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    prompt TEXT,
    plan_json JSONB,
    calories_target INT,
    goal VARCHAR(50),
    is_active BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- =====================
-- AI - SMARTA INSIKTER
-- =====================
CREATE TABLE IF NOT EXISTS ai_insights (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    insight_type VARCHAR(50) CHECK (insight_type IN (
        'training_tip', 'recovery_advice', 'nutrition_tip',
        'progress_summary', 'weekly_analysis'
    )),
    title VARCHAR(200),
    content TEXT,
    data_snapshot JSONB,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- =====================
-- SEED: LIVSMEDEL
-- =====================
INSERT INTO foods (name, calories_per_100g, protein_per_100g, carbs_per_100g, fat_per_100g, category) VALUES
    ('Kycklingbröst', 165, 31.0, 0.0, 3.6, 'protein'),
    ('Havregryn', 370, 13.0, 58.0, 7.0, 'kolhydrater'),
    ('Ägg', 155, 13.0, 1.1, 11.0, 'protein'),
    ('Banan', 89, 1.1, 23.0, 0.3, 'frukt'),
    ('Kvarg', 98, 11.0, 4.0, 4.3, 'mejeri'),
    ('Broccoli', 34, 2.8, 7.0, 0.4, 'grönsaker'),
    ('Lax', 208, 20.0, 0.0, 13.0, 'protein'),
    ('Sötpotatis', 86, 1.6, 20.0, 0.1, 'kolhydrater'),
    ('Mandlar', 579, 21.0, 22.0, 50.0, 'fett'),
    ('Proteinpulver', 400, 80.0, 5.0, 5.0, 'protein');

-- =====================
-- SEED: UTMANINGAR
-- =====================
INSERT INTO challenges (name, description, challenge_type, start_date, end_date, created_by, is_public) VALUES
    (
        'Step Master May',
        'Who can take the most steps in May? Track daily and climb the leaderboard!',
        'most_steps',
        '2026-05-01',
        '2026-05-31',
        1,
        TRUE
    ),
    (
        'Volume King',
        'Most total kg lifted this month wins. May the strongest win!',
        'most_volume',
        '2026-05-01',
        '2026-05-31',
        1,
        TRUE
    );

-- =====================
-- SEED: LEADERBOARD
-- =====================
INSERT INTO leaderboard (user_id, week_number, year, total_sessions, total_volume_kg, total_steps, points) VALUES
    (1, 17, 2026, 3, 15320, 42000, 150);

-- =====================
-- SEED: NUTRITION MÅL
-- =====================
INSERT INTO nutrition_goals (user_id, calories_target, protein_target_g, carbs_target_g, fat_target_g, water_target_ml) VALUES
    (1, 2500, 180, 250, 80, 3000);

-- =====================
-- SEED: AI INSIKTER
-- =====================
INSERT INTO ai_insights (user_id, insight_type, title, content) VALUES
    (1, 'training_tip', 'Increase your leg training!', 
     'Your data shows you train back and chest frequently but legs only twice. Add 1-2 leg sessions per week for balanced development.'),
    (1, 'recovery_advice', 'Good recovery this week!',
     'Your average sleep is 7.2 hours and stress levels are low. Perfect conditions for a harder training week.'),
    (1, 'progress_summary', 'New personal record!',
     'You hit a new deadlift PR of 150kg this week — a 25% increase from your previous best. Outstanding progress!');
-- =====================
-- STREAK SYSTEM
-- =====================
CREATE TABLE IF NOT EXISTS user_streaks (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    current_streak INT DEFAULT 0,
    longest_streak INT DEFAULT 0,
    last_workout_date DATE,
    total_workouts INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS streak_rewards (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    reward_type VARCHAR(50) CHECK (reward_type IN (
        'bronze', 'silver', 'gold', 'platinum', 'diamond'
    )),
    streak_days INT,
    achieved_at TIMESTAMP DEFAULT NOW()
);

-- =====================
-- NOTIFIKATIONER
-- =====================
CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    title VARCHAR(200),
    message TEXT,
    notification_type VARCHAR(50) CHECK (notification_type IN (
        'workout_reminder', 'recovery_alert', 'streak_milestone',
        'personal_record', 'goal_achieved', 'weekly_report',
        'challenge_update', 'ai_insight'
    )),
    is_read BOOLEAN DEFAULT FALSE,
    scheduled_at TIMESTAMP,
    sent_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- =====================
-- BMI & HÄLSOKALKYLATOR
-- =====================
CREATE TABLE IF NOT EXISTS health_calculations (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    date DATE,
    weight_kg DECIMAL(5,2),
    height_cm DECIMAL(5,2),
    age INT,
    gender VARCHAR(10) CHECK (gender IN ('male', 'female', 'other')),
    bmi DECIMAL(5,2),
    bmi_category VARCHAR(30),
    bmr DECIMAL(8,2),
    tdee DECIMAL(8,2),
    activity_level VARCHAR(30) CHECK (activity_level IN (
        'sedentary', 'lightly_active', 'moderately_active',
        'very_active', 'super_active'
    )),
    protein_target_g DECIMAL(6,2),
    carbs_target_g DECIMAL(6,2),
    fat_target_g DECIMAL(6,2),
    calories_target INT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- =====================
-- BADGES & ACHIEVEMENTS
-- =====================
CREATE TABLE IF NOT EXISTS achievements (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    description TEXT,
    icon VARCHAR(50),
    requirement_type VARCHAR(50) CHECK (requirement_type IN (
        'total_sessions', 'total_volume', 'streak_days',
        'personal_record', 'total_distance', 'weight_lost'
    )),
    requirement_value DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS user_achievements (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    achievement_id INT REFERENCES achievements(id),
    achieved_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, achievement_id)
);

-- =====================
-- SEED: STREAK DATA
-- =====================
INSERT INTO user_streaks (user_id, current_streak, longest_streak, last_workout_date, total_workouts) VALUES
    (1, 5, 12, '2026-05-02', 23);

-- =====================
-- SEED: ACHIEVEMENTS
-- =====================
INSERT INTO achievements (name, description, icon, requirement_type, requirement_value) VALUES
    ('First Workout', 'Complete your first workout', 'trophy', 'total_sessions', 1),
    ('10 Sessions', 'Complete 10 workout sessions', 'medal', 'total_sessions', 10),
    ('50 Sessions', 'Complete 50 workout sessions', 'star', 'total_sessions', 50),
    ('Week Warrior', '7 day workout streak', 'fire', 'streak_days', 7),
    ('Iron Will', '30 day workout streak', 'lightning', 'streak_days', 30),
    ('Volume King', 'Lift 100,000 kg total', 'crown', 'total_volume', 100000),
    ('Runner', 'Run 50km total', 'shoe', 'total_distance', 50),
    ('New PR', 'Set your first personal record', 'chart', 'personal_record', 1);

-- =====================
-- SEED: USER ACHIEVEMENTS
-- =====================
INSERT INTO user_achievements (user_id, achievement_id) VALUES
    (1, 1),
    (1, 2),
    (1, 8);

-- =====================
-- SEED: NOTIFIKATIONER
-- =====================
INSERT INTO notifications (user_id, title, message, notification_type, is_read) VALUES
    (1, 'Time to train!', 'You have not trained in 2 days. Keep your streak going!', 'workout_reminder', FALSE),
    (1, 'New personal record!', 'You hit a new deadlift PR of 150kg. Outstanding!', 'personal_record', TRUE),
    (1, 'Weekly report ready', 'Your weekly training report for week 17 is ready to view.', 'weekly_report', FALSE),
    (1, '5-day streak!', 'Amazing! You have trained 5 days in a row. Keep it up!', 'streak_milestone', FALSE);

-- =====================
-- SEED: HEALTH CALCULATIONS
-- =====================
INSERT INTO health_calculations (
    user_id, date, weight_kg, height_cm, age, gender,
    bmi, bmi_category, bmr, tdee, activity_level,
    protein_target_g, carbs_target_g, fat_target_g, calories_target
) VALUES (
    1, '2026-05-02', 80.0, 180.0, 25, 'male',
    24.7, 'Normal weight', 1894.0, 2936.7, 'moderately_active',
    180.0, 330.0, 98.0, 2937
);