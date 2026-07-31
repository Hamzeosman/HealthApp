-- ── ACHIEVEMENTS ──────────────────────────────────────────────
-- requirement_type: total_sessions, total_volume, streak_days,
--                   personal_record, total_distance, weight_lost
INSERT INTO achievements (name, description, icon, requirement_type, requirement_value) VALUES

-- Träningssessioner
('100 Sessions',     'Complete 100 workout sessions',    'diamond',  'total_sessions', 100),
('250 Sessions',     'Complete 250 workout sessions',    'crown',    'total_sessions', 250),
('500 Sessions',     'Complete 500 workout sessions',    'legend',   'total_sessions', 500),

-- Streaks
('3 Day Streak',     '3 consecutive training days',      'flame',    'streak_days',    3),
('14 Day Streak',    '14 consecutive training days',     'fire',     'streak_days',    14),
('60 Day Streak',    '60 day workout streak',            'inferno',  'streak_days',    60),
('100 Day Streak',   '100 day workout streak',           'legend',   'streak_days',    100),

-- Volym
('10K Club',         'Lift 10,000 kg total',             'muscle',   'total_volume',   10000),
('50K Club',         'Lift 50,000 kg total',             'star',     'total_volume',   50000),
('500K Club',        'Lift 500,000 kg total',            'diamond',  'total_volume',   500000),
('1M Club',          'Lift 1,000,000 kg total',          'legend',   'total_volume',   1000000),

-- Personal records
('PR Hunter',        'Set 5 personal records',           'trophy',   'personal_record', 5),
('PR Machine',       'Set 25 personal records',          'crown',    'personal_record', 25),
('PR Legend',        'Set 50 personal records',          'diamond',  'personal_record', 50),

-- Löpning
('First Run',        'Complete your first run',          'shoe',     'total_distance',  1),
('5K Runner',        'Run 5km total',                    'shoe',     'total_distance',  5),
('Marathon',         'Run 42.2km total',                 'medal',    'total_distance',  42.2),
('Ultra Runner',     'Run 100km total',                  'crown',    'total_distance',  100),

-- Viktnedgång
('First Kilo',       'Lose your first kilogram',         'scale',    'weight_lost',     1),
('5 Kilos Down',     'Lose 5 kilograms',                 'star',     'weight_lost',     5),
('10 Kilos Down',    'Lose 10 kilograms',                'trophy',   'weight_lost',     10)

ON CONFLICT DO NOTHING;

