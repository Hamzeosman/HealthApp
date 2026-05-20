# HealthApp — Data Engineering

> Träningsplattform byggd av Abdulrahman Fahmi (Data Engineer) och Hamze Osman (Systemutvecklare)

---

## Projektstruktur
data/
├── .github/
│   └── workflows/
│       └── test.yml            # GitHub Actions CI
├── database/
│   └── schema.sql              # Hela databasschema (42 tabeller)
├── pipelines/
│   ├── recommendation_pipeline.py
│   ├── analysis.py
│   ├── progression_pipeline.py
│   ├── personal_records_pipeline.py
│   ├── weekly_report_pipeline.py
│   ├── streak_pipeline.py
│   ├── seed_test_data.py
│   ├── seed_exercises.py       # 135+ övningar med muskeldata
│   ├── seed_ppl_program.py     # PPL 13-veckors program
│   ├── seed_more_programs.py   # 11 träningsprogram
│   ├── seed_women_programs.py  # 3 kvinnospecifika program
│   ├── seed_stretching.py      # 35 stretchingövningar + 2 program
│   ├── seed_more_data.py       # Mat + historisk data
│   └── seed_missing_data.py    # Meal logs, activity feed, progress
├── dashboard/
│   ├── app.py                  # Streamlit user dashboard (13 sidor)
│   ├── pt_dashboard.py         # PT-dashboard (8 sidor)
│   └── translations.py         # 8 språk
├── tests/
│   └── test_pipeline.py        # 5 tester
├── requirements.txt
├── run_pipeline.sh
└── .env

---

## Kom igång

### Krav
- Python 3.13+
- PostgreSQL 14+
- uv (pakethanterare)

### Installation

```bash
git clone https://github.com/Hamzeosman/HealthApp.git
cd HealthApp/data
uv sync
echo "DATABASE_URL=postgresql://localhost/healthapp" > .env
createdb healthapp
psql healthapp -f database/schema.sql
```

### Seed data (i ordning)

```bash
uv run pipelines/seed_test_data.py
uv run pipelines/seed_exercises.py
uv run pipelines/seed_ppl_program.py
uv run pipelines/seed_more_programs.py
uv run pipelines/seed_women_programs.py
uv run pipelines/seed_stretching.py
uv run pipelines/seed_more_data.py
uv run pipelines/seed_missing_data.py
```

### Kör pipelines

```bash
./run_pipeline.sh

# Eller individuellt
uv run pipelines/recommendation_pipeline.py
uv run pipelines/analysis.py
uv run pipelines/progression_pipeline.py
uv run pipelines/personal_records_pipeline.py
uv run pipelines/weekly_report_pipeline.py
uv run pipelines/streak_pipeline.py
```

### Starta dashboards

```bash
uv run streamlit run dashboard/app.py
uv run streamlit run dashboard/pt_dashboard.py
```

### Kör tester

```bash
uv run pytest tests/test_pipeline.py -v
```

---

## Databas — 42 tabeller

### Kärntabeller
| Tabell | Beskrivning |
|--------|-------------|
| `users` | Användare med mål och nivå |
| `exercises` | 135+ övningar med muskeldata, video och bilder |
| `workout_sessions` | Träningspass (87 st) |
| `workout_exercises` | Övningar per pass med sets, reps, vikt och RPE |
| `personal_records` | Personbästa per övning |
| `recommendations` | AI-rekommendationer per användare |
| `recovery_logs` | Sömn, energi, stress (90 dagar) |
| `biometrics` | Steg, puls, kalorier (90 dagar) |
| `running_sessions` | Löppass med tempo och distans |
| `foods` | 74 livsmedel med näringsvärden |
| `meal_logs` | Måltidslogg med kalorier och makron |
| `activity_feed` | Aktivitetsflöde |
| `user_progress` | Kroppsmått och progress över tid |

### Träningsprogram (16 st)
| Program | Veckor | Dagar/v | Nivå |
|---------|--------|---------|------|
| PPL — Push Pull Legs | 13 | 6 | Medel |
| Beginner Full Body | 8 | 3 | Nybörjare |
| Upper/Lower Split | 12 | 4 | Medel |
| Fat Loss Circuit | 8 | 5 | Nybörjare |
| Bulk Up Heavy Compound | 10 | 5 | Avancerad |
| Powerlifting Strength Peak | 16 | 4 | Avancerad |
| 5K Running Plan | 8 | 3 | Nybörjare |
| 10K Running Plan | 10 | 4 | Medel |
| Half Marathon Plan | 14 | 5 | Avancerad |
| Yoga & Mobility | 8 | 5 | Nybörjare |
| Home Workout Bodyweight | 12 | 4 | Nybörjare |
| Glute & Lower Body (Kvinnor) | 12 | 4 | Nybörjare |
| Full Body Toning Women | 8 | 3 | Nybörjare |
| Hourglass Figure Women | 10 | 5 | Medel |
| Men's Mobility & Stretching | 8 | 4 | Nybörjare |
| Women's Flexibility & Stretching | 8 | 5 | Nybörjare |

Alla program har: pulszoner (Zone 1-5), RPE-mål, progressionsregler, deload-veckor.

---

## Övningar (135+)

- **88 styrkeövningar** — bröst, rygg, ben, axlar, armar, mage, kondition
- **12 kvinnospecifika** — Hip Thrust, Donkey Kicks, Cable Kickback m.fl.
- **35 stretchingövningar** — övre kropp, rygg, ben, specifikt för män/kvinnor
- **21 muskelgrupper** — med primär och sekundär muskel per övning

---

## Dashboards

### app.py — Användardashboard (13 sidor) — 8 språk
🇬🇧 English · 🇸🇪 Svenska · 🇸🇦 العربية · 🇸🇴 Soomaali · 🇫🇷 Français · 🇩🇪 Deutsch · 🇵🇹 Português · 🇪🇸 Español

- **Overview** — nyckelmetrik, hälsostatus, aktivitetsflöde
- **Training** — volym, RPE, personbästa, progress
- **Running** — distans, tempo, route-analys
- **Biometrics** — steg, puls, kalorier, VO2 max
- **Recovery** — sömn, energi, stress med scatter-analys
- **Nutrition** — makromål, matdatabas (74 livsmedel), måltidslogg
- **Goals & Plans** — mål med progressbars
- **Training Programs** — 16 program med filter
- **Social & Challenges** — utmaningar, leaderboard
- **Achievements** — badges och streaks
- **Health Calculator** — BMI, BMR, TDEE, makron
- **AI Insights** — smarta träningsinsikter
- **Recommendations** — personliga rekommendationer

### pt_dashboard.py — PT-dashboard (8 sidor)
- Client Overview, Client Detail, Muscle Balance Analysis
- Recovery & Readiness, Progress Tracking, Recommendations
- Training Plans, Notifications

---

## CI/CD

GitHub Actions kör automatiskt vid varje push:

```yaml
# .github/workflows/test.yml
- Sätter upp PostgreSQL 14
- Installerar Python 3.13 + dependencies
- Kör pytest tests/test_pipeline.py -v
```

---

## API-integration med Hamzes backend

### Endpoints
GET /api/trainingplan          → 16 träningsprogram
GET /api/exerciselibrary       → 135+ övningar
GET /api/workouthistory        → Träningshistorik
GET /api/aiinsight             → AI-insikter

### Dataflöde
Python Pipeline → PostgreSQL → Hamzes ASP.NET API → React Frontend

### Ansvarsfördelning
- **Python-pipeline** skriver till: `recommendations`, `personal_records`, `ai_insights`, `user_streaks`, `notifications`
- **Hamzes API** läser och skriver till: `workout_sessions`, `workout_exercises`, `users`, `exercises`, `training_plans`

---

## Automatisering

```bash
crontab -e
# Kör kl 06:00 och 23:00 varje dag
0 6,23 * * * cd /path/to/HealthApp/data && ./run_pipeline.sh
```

---

## Tester

```bash
uv run pytest tests/test_pipeline.py -v
```

**5 tester:**
- `test_database_connection`
- `test_get_all_users`
- `test_get_untrained_body_parts`
- `test_generate_recommendations`
- `test_database_tables_exist`

---

## Team

| Roll | Person | Ansvar |
|------|--------|--------|
| Data Engineer | Abdulrahman Fahmi | Databas, pipelines, dashboards, dataanalys |
| Systemutvecklare | Hamze Osman | ASP.NET API, autentisering, React frontend |

---

## Nästa steg

- [ ] API-integration i realtid mot Hamzes endpoints
- [ ] Deployment till Railway/Vercel
- [ ] React frontend (Hamzes ansvar)
- [ ] Fler testanvändare i databasen
- [ ] Push-notifikationer
