-- ============================================================
-- EQUIPMENT & EXERCISE MEDIA MIGRATION
-- ============================================================

ALTER TABLE exercises ADD COLUMN IF NOT EXISTS image_url VARCHAR(500);
ALTER TABLE exercises ADD COLUMN IF NOT EXISTS thumbnail_url VARCHAR(500);
ALTER TABLE exercises ADD COLUMN IF NOT EXISTS animation_url VARCHAR(500);
ALTER TABLE exercises ADD COLUMN IF NOT EXISTS muscles_primary TEXT[];
ALTER TABLE exercises ADD COLUMN IF NOT EXISTS muscles_secondary TEXT[];
ALTER TABLE exercises ADD COLUMN IF NOT EXISTS tips TEXT;
ALTER TABLE exercises ADD COLUMN IF NOT EXISTS common_mistakes TEXT;
ALTER TABLE exercises ADD COLUMN IF NOT EXISTS cues TEXT[];

ALTER TABLE equipment ADD COLUMN IF NOT EXISTS description TEXT;
ALTER TABLE equipment ADD COLUMN IF NOT EXISTS image_url VARCHAR(500);
ALTER TABLE equipment ADD COLUMN IF NOT EXISTS thumbnail_url VARCHAR(500);
ALTER TABLE equipment ADD COLUMN IF NOT EXISTS category VARCHAR(30) CHECK (category IN (
    'free_weights','machines','cables','cardio',
    'bodyweight','resistance','functional','stretching'
));
ALTER TABLE equipment ADD COLUMN IF NOT EXISTS muscle_groups TEXT[];
ALTER TABLE equipment ADD COLUMN IF NOT EXISTS difficulty_level VARCHAR(20);
ALTER TABLE equipment ADD COLUMN IF NOT EXISTS space_required VARCHAR(20);
ALTER TABLE equipment ADD COLUMN IF NOT EXISTS weight_adjustable BOOLEAN DEFAULT FALSE;
ALTER TABLE equipment ADD COLUMN IF NOT EXISTS is_cardio BOOLEAN DEFAULT FALSE;
ALTER TABLE equipment ADD COLUMN IF NOT EXISTS tips TEXT;
ALTER TABLE equipment ADD COLUMN IF NOT EXISTS setup_instructions TEXT;
ALTER TABLE equipment ADD COLUMN IF NOT EXISTS commercial_name VARCHAR(100);
ALTER TABLE equipment ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;

CREATE TABLE IF NOT EXISTS equipment_exercises (
    id SERIAL PRIMARY KEY,
    equipment_id INT REFERENCES equipment(id) ON DELETE CASCADE,
    exercise_id INT REFERENCES exercises(id) ON DELETE CASCADE,
    is_primary BOOLEAN DEFAULT TRUE,
    difficulty VARCHAR(20),
    notes TEXT,
    UNIQUE(equipment_id, exercise_id)
);

CREATE TABLE IF NOT EXISTS exercise_media (
    id SERIAL PRIMARY KEY,
    exercise_id INT REFERENCES exercises(id) ON DELETE CASCADE,
    media_type VARCHAR(20) CHECK (media_type IN (
        'image','gif','video','ai_animation','thumbnail','3d_model'
    )),
    url VARCHAR(500) NOT NULL,
    storage_provider VARCHAR(20) DEFAULT 'youtube',
    phase VARCHAR(20) CHECK (phase IN (
        'start','middle','end','full_movement','muscles','mistakes'
    )),
    is_primary BOOLEAN DEFAULT FALSE,
    alt_text VARCHAR(200),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS machine_muscles (
    id SERIAL PRIMARY KEY,
    equipment_id INT REFERENCES equipment(id) ON DELETE CASCADE,
    muscle_name VARCHAR(50) NOT NULL,
    is_primary BOOLEAN DEFAULT TRUE,
    engagement_level INT CHECK (engagement_level BETWEEN 1 AND 5)
);

-- Update befintliga equipment
UPDATE equipment SET category='free_weights', muscle_groups=ARRAY['Armar','Axlar','Bröst','Ben','Rygg'], difficulty_level='all_levels', space_required='small', weight_adjustable=TRUE, is_cardio=FALSE, description='Hantlar är mångsidiga vikter för styrkeövningar. Perfekt för isolationsövningar och stabilitetsutveckling.', tips='Välj en vikt där du klarar 8-15 reps med god teknik.' WHERE name='Hantlar';
UPDATE equipment SET category='free_weights', muscle_groups=ARRAY['Bröst','Rygg','Ben','Axlar'], difficulty_level='intermediate', space_required='medium', weight_adjustable=TRUE, is_cardio=FALSE, description='Skivstången är grunden i all tyngdlyftning. Möjliggör de tyngsta lyften.', tips='Lär dig rätt teknik innan du ökar vikten. Använd alltid säkerhetsstång.' WHERE name='Skivstång';
UPDATE equipment SET category='cables', muscle_groups=ARRAY['Bröst','Rygg','Armar','Axlar','Mage'], difficulty_level='intermediate', space_required='large', weight_adjustable=TRUE, is_cardio=FALSE, description='Kabelmaskinen ger konstant spänning genom hela rörelsebanans.', tips='Justera höjden för att träffa muskeln från olika vinklar.' WHERE name='Kabelmaskin';
UPDATE equipment SET category='resistance', muscle_groups=ARRAY['Ben','Armar','Axlar','Rygg'], difficulty_level='beginner', space_required='minimal', weight_adjustable=FALSE, is_cardio=FALSE, description='Resistansband är perfekt för hemmaträning och rehabilitering.' WHERE name='Resistansband';
UPDATE equipment SET category='functional', muscle_groups=ARRAY['Armar','Axlar','Ben','Rygg','Mage','Kondition'], difficulty_level='intermediate', space_required='small', weight_adjustable=FALSE, is_cardio=FALSE, description='Kettlebells kombinerar styrka och kondition. Perfekt för explosiva rörelser.', tips='Fokusera på hip hinge — grunden i kettlebell-träning.' WHERE name='Kettlebell';
UPDATE equipment SET category='bodyweight', muscle_groups=ARRAY['Bröst','Rygg','Ben','Armar','Axlar','Mage'], difficulty_level='all_levels', space_required='minimal', weight_adjustable=FALSE, is_cardio=FALSE, description='Kroppsviktsövningar kräver ingen utrustning och kan göras var som helst.' WHERE name='Kroppsvikt';

-- Nya maskiner
INSERT INTO equipment (name, category, description, muscle_groups, difficulty_level, space_required, weight_adjustable, is_cardio, tips) VALUES
('Leg Press Machine','machines','Leg press är en av de effektivaste benmaskinerna för quadriceps, hamstrings och glutes.',ARRAY['Ben'],'beginner','large',TRUE,FALSE,'Placera fötterna axelbrett. Pressa aldrig upp knäna helt. Variera fotplacering för olika fokus.'),
('Leg Extension Machine','machines','Isolerar quadriceps i en kontrollerad rörelse. Perfekt för rehabilitering.',ARRAY['Ben'],'beginner','large',TRUE,FALSE,'Lyft kontrollerat och håll 1 sek i topp. Undvik att svänga med kroppen.'),
('Leg Curl Machine','machines','Isolerar hamstrings (baksida lår).',ARRAY['Ben'],'beginner','large',TRUE,FALSE,'Curl hälen mot skinkan. Undvik att lyfta höfterna från kudden.'),
('Seated Leg Curl Machine','machines','Sittande benböjningsmaskin — ger bättre hamstring-stretch än liggande.',ARRAY['Ben'],'beginner','large',TRUE,FALSE,'Sittande position ger bättre stretch i hamstring jämfört med liggande varianten.'),
('Hip Abduction Machine','machines','Tränar höftabduktorerna (yttre lår och glutes).',ARRAY['Ben'],'beginner','large',TRUE,FALSE,'Pressa knäna utåt mot motståndet. Håll ryggen rak och spänn glutes.'),
('Hip Adduction Machine','machines','Tränar höftadduktorerna (inre lår). Viktigt för knästabilitet.',ARRAY['Ben'],'beginner','large',TRUE,FALSE,'Pressa knäna inåt kontrollerat. Bra komplement till abduktionsmaskinen.'),
('Calf Raise Machine','machines','Stående vadpressmaskin för träning av gastrocnemius.',ARRAY['Ben'],'beginner','medium',TRUE,FALSE,'Sänk hälen under plattformen för maximal stretch. Pressa upp och håll 1 sek.'),
('Seated Calf Raise Machine','machines','Sittande vadpress tränar soleus-muskeln effektivare.',ARRAY['Ben'],'beginner','large',TRUE,FALSE,'Specifikt för soleus-muskeln under gastrocnemius.'),
('Hack Squat Machine','machines','Guidad squat med rygglutning. Tränar quadriceps med less ryggbelastning.',ARRAY['Ben'],'intermediate','large',TRUE,FALSE,'Högt fötter = mer hamstring/glutes. Lågt = mer quad. Knäna i linje med tårna.'),
('Smith Machine','machines','Guidad skivstång på räls. Säker träning utan partner.',ARRAY['Ben','Bröst','Axlar','Rygg'],'beginner','large',TRUE,FALSE,'Bra för att öva teknik. Kombinera med fria vikter för bästa resultat.'),
('Glute Kickback Machine','machines','Isolerar gluteus maximus i en kontrollerad kickback-rörelse.',ARRAY['Ben'],'beginner','large',TRUE,FALSE,'Håll ryggen rak och kläm ihop skinkan i toppositionen.'),
('Lat Pulldown Machine','machines','En av de mest populära ryggmaskinerna. Tränar latissimus dorsi effektivt.',ARRAY['Rygg','Armar'],'beginner','large',TRUE,FALSE,'Dra till bröstbenet, inte bakom nacken. Fokusera på att dra med armbågarna.'),
('Seated Row Machine','machines','Sittande roddmaskin för mitten och övre rygg.',ARRAY['Rygg','Armar'],'beginner','large',TRUE,FALSE,'Håll ryggen rak. Dra mot magen och kläm ihop skulderbladen.'),
('T-Bar Row Machine','machines','T-bar roddmaskin för kraftfull ryggträning med bröststöd.',ARRAY['Rygg','Armar'],'intermediate','large',TRUE,FALSE,'Dra vikten mot bröstkorgen med fullt rörelseutslag.'),
('Pullover Machine','machines','Isolerar latissimus dorsi i ett svepande rörelsemönster.',ARRAY['Rygg','Bröst'],'intermediate','large',TRUE,FALSE,'Håll armarna nästan raka. Fokusera på stretch i toppositionen.'),
('Bänkpressmaskin','machines','Guidad bänkpressmaskin. Säkrare än fria vikter, perfekt för nybörjare.',ARRAY['Bröst','Axlar','Armar'],'beginner','large',TRUE,FALSE,'Justera sätets höjd så handtagen är i bröstets höjd.'),
('Shoulder Press Machine','machines','Guidad axelpressmaskin för axlar och triceps.',ARRAY['Axlar','Armar'],'beginner','large',TRUE,FALSE,'Håll handlederna raka och pressa rakt upp. Sänk kontrollerat.'),
('Pec Deck / Chest Fly Machine','machines','Isolerar bröstmuskeln med guidad rörelse. Perfekt för pump.',ARRAY['Bröst'],'beginner','large',TRUE,FALSE,'Håll lätt böjning i armbågarna. Krama ihop bröstmuskeln i slutet.'),
('Incline Press Machine','machines','Guidad inkline-pressmaskin som tränar övre bröstmuskeln.',ARRAY['Bröst','Axlar'],'beginner','large',TRUE,FALSE,'Riktar sig mot övre bröstet. Kombinera med flat och decline.'),
('Ab Crunch Machine','machines','Guidad magmaskin utan nackbelastning.',ARRAY['Mage'],'beginner','large',TRUE,FALSE,'Rulla ihop överkroppen — inte pressa ner handtagen. Andas ut vid sammandragning.'),
('Captain Chair / Dip Station','machines','Armstödsbänk för hängande benlyft. Tränar mage och höftböjare.',ARRAY['Mage','Ben'],'intermediate','medium',FALSE,FALSE,'Håll ryggen mot ryggstödet. Lyft knäna till brösthöjd.'),
('Roman Chair / Back Extension','machines','Ryggextensionsbänk för nedre rygg, glutes och hamstrings.',ARRAY['Rygg','Ben'],'beginner','medium',FALSE,FALSE,'Gå till plant läge eller lätt hyperextension. Håll nacken neutral.'),
('Cable Crossover','cables','Dubbel kabelmaskin med justerbar höjd. Mest mångsidiga maskinen.',ARRAY['Bröst','Axlar','Rygg','Armar','Mage'],'intermediate','large',TRUE,FALSE,'Justera höjden för övre/mitre/nedre bröst. Håll kärnan stabil.'),
('Functional Trainer','cables','Avancerad dubbel kabelmaskin med 180° rotation.',ARRAY['Bröst','Rygg','Axlar','Armar','Mage','Ben'],'intermediate','large',TRUE,FALSE,'Perfekt för sport-specifik träning och rehabilitering.'),
('Löpband','cardio','Löpband för gång, jogging och löpning inomhus.',ARRAY['Kondition','Ben'],'all_levels','large',FALSE,TRUE,'Börja med gång och öka gradvis. Använd lutning för ökad intensitet.'),
('Crosstrainer','cardio','Elliptisk tränare som kombinerar löpning och skidåkning. Skonsam för leder.',ARRAY['Kondition','Ben','Armar'],'all_levels','large',FALSE,TRUE,'Håll ryggen rak och tryck/dra med armarna för att aktivera överkroppen.'),
('Motionscykel','cardio','Stationär cykel för konditionsträning utan ledbelastning.',ARRAY['Kondition','Ben'],'all_levels','medium',FALSE,TRUE,'Sadeln: knäet ska vara lätt böjt vid pedalens lägsta position.'),
('Roddmaskin','cardio','Tränar 86% av alla muskler. Perfekt helkroppskonditionen.',ARRAY['Kondition','Rygg','Ben','Armar'],'intermediate','large',FALSE,TRUE,'Rörelseordning: Ben → Rygg → Armar. Håll ryggen rak.'),
('Stairclimber','cardio','Trappmaskin extremt effektiv för glutes och kondition.',ARRAY['Kondition','Ben'],'intermediate','medium',FALSE,TRUE,'Håll inte i räckena för fullt stöd — det minskar intensiteten.'),
('Air Bike','cardio','Luftmotståndscykel — motståndet ökar automatiskt med din insats.',ARRAY['Kondition','Ben','Armar'],'all_levels','medium',FALSE,TRUE,'Perfekt för HIIT: 20 sek max + 40 sek vila.'),
('Roddmaskin / Ski Erg','cardio','Skidergometer som simulerar längdskidåkning.',ARRAY['Kondition','Armar','Rygg','Mage'],'intermediate','medium',FALSE,TRUE,'Dra handtagen längs med kroppen. Använd hela kroppen koordinerat.'),
('Power Rack','free_weights','Säkerhetsrigg för tung styrketräning med squat, bänkpress och militärpress.',ARRAY['Ben','Bröst','Axlar','Rygg'],'intermediate','large',TRUE,FALSE,'Ställ in säkerhetspinnarna precis under din lägsta position.'),
('Pull-up Bar','bodyweight','Horisontell stång för pull-ups och chin-ups. En av bästa ryggövningarna.',ARRAY['Rygg','Armar'],'intermediate','small',FALSE,FALSE,'Börja med hängande och bygg upp gradvis. Assisted pull-up kan hjälpa.'),
('Dip Bars','bodyweight','Parallella stänger för dips. Tränar triceps, bröst och axlar.',ARRAY['Armar','Bröst','Axlar'],'intermediate','small',FALSE,FALSE,'Luta framåt för mer bröst, upprätt för mer triceps.'),
('TRX Suspension Trainer','functional','Suspensionsbandssystem med justerbar svårighetsgrad.',ARRAY['Bröst','Rygg','Ben','Armar','Mage'],'all_levels','minimal',FALSE,FALSE,'Ju mer horisontellt kroppen är, desto svårare.'),
('Battle Ropes','functional','Kraftiga rep för explosiv kraft, kondition och koordination.',ARRAY['Armar','Axlar','Mage','Kondition'],'intermediate','medium',FALSE,TRUE,'Håll kärnan stabil och knäna lätt böjda.'),
('Foam Roller','stretching','Skumrulle för myofascial release och återhämtning.',ARRAY['Ben','Rygg','Armar'],'all_levels','minimal',FALSE,FALSE,'Rulla långsamt och stanna 30-60 sek på ömma punkter.'),
('EZ-Curl Bar','free_weights','Böjd skivstång som minskar handledsbelastning vid biceps/triceps.',ARRAY['Armar'],'beginner','small',TRUE,FALSE,'Mer naturligt grepp än rak skivstång — bra vid handledsbesvär.')
ON CONFLICT (name) DO UPDATE SET
    category = EXCLUDED.category,
    description = EXCLUDED.description,
    muscle_groups = EXCLUDED.muscle_groups,
    difficulty_level = EXCLUDED.difficulty_level,
    space_required = EXCLUDED.space_required,
    weight_adjustable = EXCLUDED.weight_adjustable,
    is_cardio = EXCLUDED.is_cardio,
    tips = EXCLUDED.tips;

CREATE INDEX IF NOT EXISTS idx_equipment_category ON equipment(category);
CREATE INDEX IF NOT EXISTS idx_exercise_media_exercise ON exercise_media(exercise_id, media_type);
CREATE INDEX IF NOT EXISTS idx_equipment_exercises ON equipment_exercises(equipment_id);
