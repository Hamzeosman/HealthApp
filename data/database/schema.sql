
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