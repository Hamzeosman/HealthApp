# HealthApp — Data Engineering

> Träningsplattform byggd av Abdulrahman Fahmi (Data Engineer) och Hamze Osman (Systemutvecklare)

---

## 📁 Projektstruktur
data/
├── database/
│   └── schema.sql              # Hela databasschema (40+ tabeller)
├── pipelines/
│   ├── recommendation_pipeline.py   # Rekommendationssystem
│   ├── analysis.py                  # DuckDB-analys
│   ├── progression_pipeline.py      # Volym och progression
│   ├── personal_records_pipeline.py # Personbästa-detektering
│   ├── weekly_report_pipeline.py    # Veckorapport
│   ├── streak_pipeline.py           # Streaks och achievements
│   ├── seed_test_data.py            # Testdata
│   ├── seed_exercises.py            # 100+ övningar med muskeldata
│   ├── seed_ppl_program.py          # PPL 13-veckors program
│   └── seed_more_programs.py        # 9 träningsprogram
├── dashboard/
│   ├── app.py                  # Streamlit user dashboard (13 sidor)
│   └── pt_dashboard.py         # PT-dashboard (8 sidor)
├── tests/
│   └── test_pipeline.py        # 5 tester
├── run_pipeline.sh             # Kör alla pipelines
└── .env                        # Databasanslutning

---

## 🚀 Kom igång

### Krav
- Python 3.13+
- PostgreSQL 14+
- uv (pakethanterare)

### Installation

```bash
# Klona repot
git clone https://github.com/Hamzeosman/HealthApp.git
cd HealthApp/data

# Installera paket
uv sync

# Skapa .env fil
echo "DATABASE_URL=postgresql://localhost/healthapp" > .env

# Skapa databasen
createdb healthapp
psql healthapp -f database/schema.sql
```

### Seed data

```bash
# Lägg in testdata
uv run pipelines/seed_test_data.py

# Lägg in övningar (100+)
uv run pipelines/seed_exercises.py

# Lägg in träningsprogram
uv run pipelines/seed_ppl_program.py
uv run pipelines/seed_more_programs.py
```

### Kör pipelines

```bash
# Kör alla pipelines på en gång
./run_pipeline.sh

# Eller kör individuellt
uv run pipelines/recommendation_pipeline.py
uv run pipelines/analysis.py
uv run pipelines/progression_pipeline.py
uv run pipelines/personal_records_pipeline.py
uv run pipelines/weekly_report_pipeline.py
uv run pipelines/streak_pipeline.py
```

### Starta dashboards

```bash
# Användardashboard
uv run streamlit run dashboard/app.py

# PT-dashboard
uv run streamlit run dashboard/pt_dashboard.py
```

### Kör tester

```bash
uv run pytest tests/test_pipeline.py -v
```

---

## 🗄️ Databas

### Kärntabeller
| Tabell | Beskrivning |
|--------|-------------|
| `users` | Användare med mål och nivå |
| `exercises` | 100+ övningar med muskeldata, video och bilder |
| `workout_sessions` | Träningspass |
| `workout_exercises` | Övningar per pass med sets, reps, vikt och RPE |
| `personal_records` | Personbästa per övning |
| `recommendations` | AI-rekommendationer per användare |

### Träningsprogram (10 st)
| Program | Veckor | Dagar/vecka | Nivå |
|---------|--------|-------------|------|
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

---

## 🔄 Pipelines

### recommendation_pipeline.py
Analyserar vilka kroppsdelar användaren inte tränat på länge och genererar rekommendationer. Körs automatiskt vid varje pipeline-körning.

### analysis.py
DuckDB-analys av träningsdata. Beräknar volym, frekvens och mönster per muskelgrupp.

### progression_pipeline.py
Spårar volymökning vecka för vecka. Identifierar platåer och varnar om volymen minskar.

### personal_records_pipeline.py
Detekterar automatiskt nya personbästa och sparar dem med datum.

### weekly_report_pipeline.py
Genererar veckorapport med träning, sömn, återhämtning och rekommendationer.

### streak_pipeline.py
Beräknar dagliga träningsstreaks, låser upp achievements och skickar påminnelser om användaren inte tränat på 2+ dagar.

---

## 📊 Dashboards

### app.py — Användardashboard (13 sidor)
- **Overview** — nyckelmetrik, hälsostatus, muskelgrupper
- **Training** — volym, RPE, personbästa
- **Running** — distans, tempo, pulszoner
- **Biometrics** — steg, puls, kalorier
- **Recovery** — sömn, energi, stress
- **Nutrition** — makromål, matdatabas
- **Goals & Plans** — mål med progressbars
- **Training Programs** — alla 10 program med filter
- **Social & Challenges** — utmaningar, leaderboard
- **Achievements** — badges och streaks
- **Health Calculator** — BMI, BMR, TDEE, makron
- **AI Insights** — smarta träningsinsikter
- **Recommendations** — personliga rekommendationer

### pt_dashboard.py — PT-dashboard (8 sidor)
- **Client Overview** — alla klienter med statistik
- **Client Detail** — djupgående klientanalys
- **Muscle Balance Analysis** — muskelbalans-heatmap
- **Recovery & Readiness** — träningsberedskap per klient
- **Progress Tracking** — volym och PR-progression
- **Recommendations** — AI-rekommendationer per klient
- **Training Plans** — tilldela program till klienter
- **Notifications** — alla klientnotifikationer

---

## 🔗 API-integration med Hamzes backend

### Endpoints som Python-pipelinen skriver till

Data genererad av pipelinen lagras i PostgreSQL och kan hämtas via Hamzes API:
GET  /api/recommendation/user/{userId}   → Hämtar rekommendationer
GET  /api/personalrecord/user/{userId}   → Hämtar personbästa
GET  /api/workoutsession/user/{userId}   → Hämtar träningspass

### Hur data flödar
Python Pipeline → PostgreSQL → Hamzes ASP.NET API → React Frontend

### Databas
Python-pipelinen och Hamzes API delar samma PostgreSQL-databas:
- **Python-pipeline**: skriver till `recommendations`, `personal_records`, `ai_insights`, `user_streaks`, `notifications`
- **Hamzes API**: läser och skriver till `workout_sessions`, `workout_exercises`, `users`, `exercises`

---

## ⚙️ Automatisering

Pipelines körs automatiskt via cron:

```bash
# Öppna crontab
crontab -e

# Kör kl 06:00 och 23:00 varje dag
0 6,23 * * * cd /path/to/HealthApp/data && ./run_pipeline.sh
```

---

## 🧪 Tester

```bash
uv run pytest tests/test_pipeline.py -v
```

**5 tester:**
- `test_database_connection` — databaskoppling fungerar
- `test_get_all_users` — hämtar användare
- `test_get_untrained_body_parts` — hittar otränade kroppsdelar
- `test_generate_recommendations` — genererar rekommendationer
- `test_database_tables_exist` — alla tabeller finns

---

## 👥 Team

| Roll | Person | Ansvar |
|------|--------|--------|
| Data Engineer | Abdulrahman Fahmi | Databas, pipelines, dashboards, dataanalys |
| Systemutvecklare | Hamze Osman | ASP.NET API, autentisering, frontend |

---

## 📌 Nästa steg

- [ ] Deployment till Railway/Vercel
- [ ] React frontend (Hamzes ansvar)
- [ ] API-integration i realtid
- [ ] Mobilanpassning
- [ ] Push-notifikationer
- [ ] Premium-funktioner