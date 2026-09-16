# HealthApp — Databasdokumentation

## Översikt

HealthApp-databasen är byggd i PostgreSQL 14 och innehåller 83 tabeller fördelade på fyra lager. Arkitekturen följer principen att **master data** underhålls av utvecklarna, medan **user data** alltid skapas av riktiga användare via appen.

---

## Mappstruktur

```
database/
├── schema/
│   └── schema.sql                      # Komplett databasschema
├── seed/
│   ├── equipment_exercises.sql         # Maskiner → övningar (280 kopplingar)
│   ├── equipment_exercises_additions.sql
│   ├── exercise_tag_map.sql            # Övningar → taggar (569 kopplingar)
│   ├── machine_muscles.sql             # Maskiner → muskler (174 kopplingar)
│   ├── substitutions.sql              # Exercise substitutions (42)
│   ├── substitution_rules.sql         # Substitutionsregler (38)
│   ├── achievements.sql               # Prestationer (29)
│   ├── progression_rules.sql          # Progressionsregler (25)
│   ├── workout_programs.sql           # Träningsprogram och mallar
│   ├── training_blocks.sql            # Periodiseringsblock
│   └── seed_p3.sql                    # Gym, nutrition targets
└── migrations/
    ├── migration_p1.sql               # Initial schema
    ├── migration_p2.sql               # Nutrition och recovery
    ├── migration_p3.sql               # AI och analytics
    ├── migration_p4_fixes.sql         # Datumfix och buggfixar
    ├── migration_equipment.sql        # Utrustningskatalog
    ├── migration_p5_quality.sql       # Slug, soft delete, constraints, index
    └── migration_p6_exercise_metadata.sql  # Exercise metadata
```

---

## De fyra lagren

### 1. Kunskapsdatabas (statisk master data)
Underhålls av utvecklarna. Innehåller seed-data som aldrig ändras av användare.

| Tabell | Beskrivning | Rader |
|--------|-------------|-------|
| exercises | 168 övningar med biomekanik, muskelgrupper, svårighetsgrad | 168 |
| equipment | 44 maskiner och utrustningar | 44 |
| equipment_exercises | Koppling maskin → övning | 280 |
| machine_muscles | Vilka muskler varje maskin aktiverar (engagement 1–5) | 174 |
| exercise_tag_map | Övningar taggade med compound/push/pull/hinge etc | 569 |
| exercise_tags | 19 taggar | 19 |
| exercise_substitutions | Alternativa övningar vid skada/brist på utrustning | 42 |
| exercise_substitution_rules | Regler för substitution med equivalence score | 38 |
| foods | 74 livsmedel med makronäringsdata | 74 |
| gyms | 19 gym i Sverige | 19 |
| training_plans | 16 evidensbaserade träningsprogram | 16 |
| workout_programs | 7 program med mallar | 7 |
| achievements | 29 prestationer att låsa upp | 29 |
| progression_rules | 25 regler för automatisk progression | 25 |

### 2. Användardata (dynamisk)
Skapas **enbart** av riktiga användare via appen. Ingen seed-data.

| Tabell | Beskrivning |
|--------|-------------|
| users | Fitnessprofil (inte auth — det hanteras av AppDbContext) |
| workout_sessions | Loggade träningspass |
| workout_exercises | Övningar per pass med sets, reps, vikt, RPE |
| recovery_logs | Sömn, energi, stress per dag |
| sleep_sessions | Detaljerad sömndata |
| biometrics | Steg, hjärtfrekvens, VO2max |
| personal_records | Personbästa per övning |
| meal_logs | Matloggning |
| running_sessions | Löppass med distans, tempo, zoner |
| injuries | Skador med svårighetsgrad och status |
| body_measurements | Kroppsmått över tid |

### 3. Analyslager (beräknas automatiskt av pipelines)
Genereras av Python-pipelines. Läs aldrig direkt — använd API-endpoints.

| Tabell | Pipeline | Beskrivning |
|--------|----------|-------------|
| fatigue_scores | fatigue_pipeline.py | ACWR, readiness score per dag |
| training_metrics | volume_tracker_pipeline.py | Veckovolym, muskelbalans |
| recommendations | recommendation_pipeline.py | AI-rekommendationer |
| ai_insights | volume_tracker_pipeline.py | Veckoanalys |
| personal_records | personal_records_pipeline.py | Uppdateras efter varje pass |
| progression_log | progression_pipeline.py | Viktökningar |

### 4. AI-lager
Bygger på analyslagret för personliga rekommendationer.

| Tabell | Beskrivning |
|--------|-------------|
| ai_coach_sessions | Konversationer med AI-coach |
| model_predictions | Skaderisk, 1RM-prediktioner |
| readiness_trends | Trender i readiness över tid |
| user_daily_features | Feature store för ML-modeller |

---

## Dataflöde

```
Användaren loggar träningspass
        ↓
workout_sessions + workout_exercises
        ↓
Pipelines körs automatiskt
        ↓
fatigue_scores → readiness_score
training_metrics → volym, muskelbalans
personal_records → personbästa
progression_log → viktökningar
        ↓
recommendations → AI-rekommendationer
ai_insights → veckoanalys
        ↓
AI Coach läser allt → personligt svar
```

---

## Developer-konton

| Email | Roll | Syfte |
|-------|------|-------|
| admin@healthapp.local | admin | Systemadministration |
| pt@healthapp.local | pt | Testa PT-funktioner |
| member@healthapp.local | user | Testa användarflöde |

Riktiga användare skapar sina konton via appen. Developer-konton används **endast i utvecklingsmiljö**.

---

## Köra databasen från scratch

```bash
# 1. Skapa databasen
createdb healthapp

# 2. Applicera schema
psql healthapp -f database/schema/schema.sql

# 3. Kör migrations i ordning
psql healthapp -f database/migrations/migration_p1.sql
psql healthapp -f database/migrations/migration_p2.sql
psql healthapp -f database/migrations/migration_p3.sql
psql healthapp -f database/migrations/migration_equipment.sql
psql healthapp -f database/migrations/migration_p4_fixes.sql
psql healthapp -f database/migrations/migration_p5_quality.sql
psql healthapp -f database/migrations/migration_p6_exercise_metadata.sql

# 4. Lägg in master data (seed)
psql healthapp -f database/seed/equipment_exercises.sql
psql healthapp -f database/seed/equipment_exercises_additions.sql
psql healthapp -f database/seed/machine_muscles.sql
psql healthapp -f database/seed/exercise_tag_map.sql
psql healthapp -f database/seed/substitutions.sql
psql healthapp -f database/seed/substitution_rules.sql
psql healthapp -f database/seed/achievements.sql
psql healthapp -f database/seed/progression_rules.sql
psql healthapp -f database/seed/workout_programs.sql
psql healthapp -f database/seed/seed_p3.sql
```

---

## Köra dashboards

### Förutsättningar

```bash
# Installera beroenden
cd HealthApp/data
pip install -r requirements.txt

# Sätt upp .env
cp .env.example .env
# Fyll i DATABASE_URL=postgresql://user:pass@localhost/healthapp
```

### User Dashboard (13 sidor, 8 språk)

```bash
cd HealthApp/data
streamlit run dashboard/app.py
```

Öppnas på http://localhost:8501

**Sidor:**
- Overview — träningsöversikt och hälsostatus
- Training — pass, volym, muskelgrupper
- Running — löppass, tempo, zoner
- Biometrics — steg, hjärtfrekvens, VO2max
- Recovery — sömn, energi, stress
- Nutrition — matloggning och makron
- Goals & Plans — mål och träningsplaner
- Training Programs — 16 program filtrerade på mål och nivå
- Social & Challenges — utmaningar och leaderboard
- Achievements — 29 prestationer att låsa upp
- Health Calculator — BMI, TDEE, makroberäkning
- AI Insights — automatiska insikter från pipelines
- Recommendations — personliga övningsrekommendationer

### PT Dashboard (8 sidor)

```bash
cd HealthApp/data
streamlit run dashboard/pt_dashboard.py
```

Öppnas på http://localhost:8501

**Sidor:**
- Client Overview — alla klienter med readiness
- Client Detail — djupanalys per klient
- Muscle Balance — push/pull och upper/lower ratio
- Recovery & Readiness — sömn och återhämtning
- Progress Tracking — styrke- och konditionsutveckling
- Equipment Analytics — utrustningsanvändning
- AI Insights & Alerts — automatiska varningar
- Smart Recommendations — övningsrekommendationer
- Training Plans — tilldela program till klienter

### Köra pipelines

```bash
cd HealthApp/data

# Kör alla pipelines i rätt ordning
python run_all_pipelines.py

# Eller kör enskilda pipelines
python pipelines/fatigue_pipeline.py
python pipelines/volume_tracker_pipeline.py
python pipelines/recommendation_pipeline.py
python pipelines/weekly_report_pipeline.py
```

---

## Arkitekturprinciper

**Master data vs User data** — Övningar, maskiner och mat är master data med seed-data. Träningshistorik och måltider skapas alltid av riktiga användare.

**Soft delete** — `exercises`, `equipment`, `foods`, `workout_sessions` och `training_plans` använder `deleted_at` istället för `DELETE`. Historik bevaras alltid.

**Slug** — `exercises`, `equipment` och `foods` har `slug`-kolumn för URL-vänliga identifierare (t.ex. `bench-press`, `lat-pulldown-machine`).

**Validering** — 22 CHECK constraints i databasen + `core/validation.py` i Python skyddar mot orimlig data: RPE 1–10, sömn 0–16h, vikt 20–400kg, kalorier 0–3000 per måltid, hjärtfrekvens 30–230.

**Index** — 48 index optimerar de vanligaste frågorna på `user_id + date`, `exercise_id`, `slug`.

---

## Teknisk stack

| Del | Teknologi |
|-----|-----------|
| Databas | PostgreSQL 14 |
| ORM (Python) | SQLAlchemy 2.0 |
| ORM (.NET) | Entity Framework Core (DataDbContext) |
| Pipelines | Python 3.13 |
| Validering | core/validation.py |
| API | FastAPI (Python) + ASP.NET Core (.NET) |
| User Dashboard | Streamlit (13 sidor, 8 språk) |
| PT Dashboard | Streamlit (8 sidor) |
| CI/CD | GitHub Actions |
---

## Backup och återställning

### Backup

```bash
# Daglig backup (kör som cron-job)
pg_dump healthapp > backup_$(date +%Y%m%d).sql

# Komprimerad backup
pg_dump healthapp | gzip > backup_$(date +%Y%m%d).sql.gz
```

### Restore

```bash
# Återställ från backup
psql healthapp < backup_20260101.sql

# Från komprimerad
gunzip -c backup_20260101.sql.gz | psql healthapp
```

### Rollback migration

```bash
# Om en migration gick fel — återställ från senaste backup
psql healthapp < backup_before_migration.sql
```

### Produktionsstrategi

- Kör backup varje natt kl 02:00
- Behåll 30 dagars backup
- Testa restore en gång per månad
- Kör alltid backup innan migration

---

## Admin Dashboard

```bash
cd HealthApp/data
streamlit run dashboard/admin_dashboard.py
```

Öppnas på http://localhost:8502

**Sidor:**
- Oversikt — användare, triggers, constraints, index, pipeline status
- Data Quality — score 100%, checkmatris, historik
- Pipeline Historik — alla 10 pipelines med success rate och duration
- Anomalier — training_volume_spike, sleep_deprivation, rpe_spike, training_dropout
- Databas Status — tabeller, statistik, PostgreSQL-roller

---

## Rollbaserad åtkomst

| Roll | Behörighet |
|------|------------|
| healthapp_admin | Full åtkomst till allt |
| healthapp_pt | Läsa träningsdata, skriva rekommendationer |
| healthapp_user | Bara sin egen data + master data |
| healthapp_ai_service | Läsa allt, skriva insights och metrics |
| healthapp_analytics | Bara läsåtkomst för dashboards |

---

## Köra alla pipelines

```bash
cd HealthApp/data

# Kör alla 10 pipelines i rätt ordning
python pipelines/run_all_pipelines.py

# Enskilda pipelines
python pipelines/feature_store_pipeline.py
python pipelines/fatigue_pipeline.py
python pipelines/anomaly_detection_pipeline.py
python pipelines/data_quality_pipeline.py
```

Körningar loggas automatiskt i `pipeline_logs`-tabellen.
