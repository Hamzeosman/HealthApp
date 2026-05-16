# HealthApp API

> ⚠️ **OBS:** Projektet är under utveckling och kommer att uppdateras löpande.

HealthApp är ett samarbetsprojekt mellan en systemutvecklare och en dataingenjör.
Applikationen låter användare registrera träningspass, logga övningar och filtrera
på muskelgrupper. Backend:en är byggd med ASP.NET Core och kommunicerar med en
PostgreSQL-databas som hanteras av dataingenjören via en Python-pipeline.

## Tekniker
- ASP.NET Core Web API (.NET 10)
- Entity Framework Core med PostgreSQL
- JWT Bearer Authentication
- BCrypt.Net

## Kom igång

### Krav
- .NET 10 SDK
- PostgreSQL

### Installation
1. Klona repot
   git clone https://github.com/Hamzeosman/HealthApp.git

2. Navigera till projektmappen
   cd HealthApp.API

3. Uppdatera connection stringen i appsettings.json
   "DefaultConnection": "Host=localhost;Database=HealthAppDb;Username=postgres;"

4. Kör migrationen
   dotnet ef database update

5. Starta API:t
   dotnet run
   
6. Öppna Scalar UI i webbläsaren
   http://localhost:5137/scalar/v1

## Endpoints

### Autentisering
| Method | Endpoint | Beskrivning |
|--------|----------|-------------|
| POST | /api/auth/register | Registrera användare |
| POST | /api/auth/login | Logga in |

### Övningar
| Method | Endpoint | Beskrivning |
|--------|----------|-------------|
| GET | /api/exercise | Hämta alla övningar |
| GET | /api/exercise/{id} | Hämta övning via id |
| GET | /api/exercise/musclegroup/{muscleGroup} | Filtrera på muskelgrupp |
| POST | /api/exercise | Lägg till övning |

### Träningspass
| Method | Endpoint | Beskrivning |
|--------|----------|-------------|
| GET | /api/workoutsession/user/{userId} | Hämta träningspass per användare |
| GET | /api/workoutsession/{id} | Hämta träningspass via id |
| POST | /api/workoutsession | Logga träningspass |

## Projektstruktur
HealthApp.API/
├── Controllers/
├── Services/
├── Repositories/
├── Models/
│   ├── User.cs
│   ├── Exercise.cs
│   ├── BodyPart.cs
│   ├── MuscleGroup.cs
│   ├── Equipment.cs
│   ├── WorkoutProgram.cs
│   ├── WorkoutTemplate.cs
│   ├── TemplateExercise.cs
│   ├── WorkoutSession.cs
│   ├── WorkoutExercise.cs
│   ├── UserProgress.cs
│   ├── PersonalRecord.cs
│   └── Recommendation.cs
├── DTOs/
└── Migrations/

### Hur man testar 
cd data

# Lägg in testdata
uv run pipelines/seed_test_data.py

# Träningsprogram
uv run pipelines/seed_ppl_program.py
uv run pipelines/seed_more_programs.py

# Kör alla pipelines
uv run pipelines/recommendation_pipeline.py
uv run pipelines/analysis.py
uv run pipelines/progression_pipeline.py
uv run pipelines/personal_records_pipeline.py
uv run pipelines/weekly_report_pipeline.py
uv run pipelines/streak_pipeline.py

# Eller kör alla på en gång
./run_pipeline.sh

# Starta dashboarden
uv run streamlit run dashboard/app.py

# Kör tester
uv run pytest tests/test_pipeline.py -v

## Skapad av
- Hamze – Systemutvecklare (Backend API)
- AbdulRahman – Dataingenjör (Databas & Pipeline)
