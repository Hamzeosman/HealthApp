\# Feature Specification: DataDbContext Iteration 1 — Users, Equipment, Exercises



\*\*Feature Branch:\*\* `feat/datadb-iteration-1-users-equipment`

\*\*Created:\*\* 2026-07-05

\*\*Status:\*\* Draft

\*\*Iteration:\*\* 1 of 3 (Issue #32)

\*\*Input:\*\* Utöka DataDbContext med tre EF-mappningar: UserData (fitness-profil), EquipmentData (lookup) och komplettera befintlig ExerciseData.



\## Bakgrund



Issue #32 kräver att .NET-sidan får fullständig EF-mappning mot Abdulrahmans PostgreSQL-schema (`HealthAppDataDb`). Iteration 1 täcker de tre mest grundläggande entiteterna som andra tabeller sedan bygger på: `users`, `equipment`, och `exercises`.



Två av tabellerna finns redan minimalt mappade (`ExerciseData`) eller inte alls (`equipment`, `users`). Iteration 1 kompletterar dem så de matchar schema.sql fullt ut, med constraints och relationer där det är rimligt utan att bryta 400-rader-regeln.



Constitution v1.1.0 §Architecture (data boundary) styr:

\- `AppDbContext` → auth/identity (`AspNetUsers`)

\- `DataDbContext` → fitness-data mot Abdulrahmans schema

\- Två separata C#-entiteter kan mappa mot samma fysiska tabell (`User.cs` för auth, `UserData.cs` för fitness) — det är avsiktligt.



\## User Scenarios \& Testing



\### Primary User Story

Som .NET-utvecklare vill jag att `DataDbContext` exponerar `UserData`, `EquipmentData` och kompletterad `ExerciseData` så att frontend/services kan läsa fitness-profil, utrustningskatalog och övningar utan att duplicera schema-förståelse mellan .NET och Python.



\### Acceptance Scenarios



1\. \*\*Given\*\* en användare finns i `users`-tabellen, \*\*When\*\* jag queryar `dataDbContext.Users.FirstOrDefault(u => u.Id == 1)`, \*\*Then\*\* får jag ett `UserData`-objekt med fitness-fält (name, age, weight\_kg, height\_cm, fitness\_level, goal, created\_at) — men INTE email eller password\_hash.



2\. \*\*Given\*\* en övning i `exercises` refererar till equipment\_id, \*\*When\*\* jag laddar `dataDbContext.Exercises.Include(e => e.Equipment)`, \*\*Then\*\* navigation-propertyn `Equipment` innehåller matchande `EquipmentData`.



3\. \*\*Given\*\* databas-schemat kräver `fitness\_level IN ('nybörjare','medel','avancerad')`, \*\*When\*\* jag försöker spara en `UserData` med `FitnessLevel = "expert"`, \*\*Then\*\* kastas ett constraint-fel från Postgres (verifieras via check constraint i OnModelCreating).



4\. \*\*Given\*\* ExerciseData saknade tidigare `calories\_per\_minute`, \*\*When\*\* jag laddar en övning, \*\*Then\*\* finns `CaloriesPerMinute` som decimal-property som mappar mot `calories\_per\_minute`-kolumnen.



\### Edge Cases



\- Vad händer om `users.name` är null? → Property är nullable string.

\- Vad händer om `exercises.equipment\_id` är null? → EquipmentData-navigation är null (optional relation).

\- Vad händer om någon råkar lägga till `Email` eller `PasswordHash` i `UserData`? → Test failar, blockar merge.



\## Requirements



\### Functional Requirements



\- \*\*FR-001:\*\* `UserData`-entitet MÅSTE mappa mot `users`-tabellen via `\[Table("users")]`.

\- \*\*FR-002:\*\* `UserData` MÅSTE innehålla: `Id`, `Name`, `Age`, `WeightKg`, `HeightCm`, `FitnessLevel`, `Goal`, `CreatedAt`.

\- \*\*FR-003:\*\* `UserData` MÅSTE INTE innehålla `Email`, `PasswordHash`, eller andra auth-fält. Detta är arkitekturregel per Constitution §Architecture.

\- \*\*FR-004:\*\* `EquipmentData`-entitet MÅSTE mappa mot `equipment`-tabellen med fälten `Id` och `Name`.

\- \*\*FR-005:\*\* Befintlig `ExerciseData` MÅSTE utökas med `CaloriesPerMinute` (decimal, nullable) mappad mot `calories\_per\_minute`.

\- \*\*FR-006:\*\* `ExerciseData` MÅSTE ha navigation property `EquipmentData? Equipment` via `EquipmentId`.

\- \*\*FR-007:\*\* `DataDbContext` MÅSTE exponera `DbSet<UserData> Users` och `DbSet<EquipmentData> Equipment`.

\- \*\*FR-008:\*\* `OnModelCreating` MÅSTE konfigurera check constraints i Postgres:

&#x20; - `UserData.FitnessLevel` IN ('nybörjare','medel','avancerad')

&#x20; - `UserData.Goal` IN ('bygga\_muskler','gå\_ner\_i\_vikt','öka\_kondition','hålla\_sig\_i\_form')

&#x20; - `ExerciseData.Difficulty` IN ('nybörjare','medel','avancerad')

&#x20; - `ExerciseData.ExerciseType` IN ('styrka','kondition','stretching','balans')

\- \*\*FR-009:\*\* PascalCase-klasserna `User`, `Equipment`, `Exercise` (som tillhör AppDbContext-världen) MÅSTE INTE modifieras i denna PR.



\### Key Entities



\- \*\*UserData\*\* → tabell `users`, endast fitness-fält (inga auth-fält)

\- \*\*EquipmentData\*\* → tabell `equipment`, lookup-tabell (id, name)

\- \*\*ExerciseData\*\* (uppdatera) → tabell `exercises`, komplett med calories\_per\_minute + navigation till EquipmentData



\## Testing Strategy



Tester i `HealthApp.Tests/Data/`:



1\. \*\*`UserData\_MustNotHaveAuthFields`\*\* — Reflection-baserat test som verifierar att `UserData` inte har properties med namn `Email`, `Password`, `PasswordHash`. Skyddar arkitekturregeln FR-003 mot framtida regression.



2\. \*\*`UserData\_ColumnMapping\_MatchesSnakeCase`\*\* — Verifierar att `\[Column]`-attribut mappar rätt (t.ex. `WeightKg` → `weight\_kg`).



3\. \*\*`EquipmentData\_ColumnMapping`\*\* — Sanity-test för Id/Name mot `equipment`-tabellen.



4\. \*\*`ExerciseData\_HasCaloriesPerMinute`\*\* — Verifierar att den nya kolumnen finns.



5\. \*\*`ExerciseData\_EquipmentNavigation\_LoadsRelatedEntity`\*\* — Integrationstest (via InMemory eller test-DB) som verifierar att `Include(e => e.Equipment)` fungerar.



\## Constitution Alignment



\- \*\*§I. Layered Architecture\*\* ✅ — Endast Model-lagret berörs, inga Controllers/Services rörs.

\- \*\*§II. Security-First\*\* ✅ — Arkitekturregeln FR-003 skyddar mot att auth-data läcker till DataDbContext.

\- \*\*§III. Test-Required\*\* ✅ — 5 tester planerade, inkl. regression-skydd för arkitekturregel.

\- \*\*§V. Code Quality\*\* ✅ — Följer befintligt `Data`-suffix-mönster (ExerciseData, WorkoutSessionData).

\- \*\*§Architecture (data boundary)\*\* ✅ — Tydlig separation mellan AppDbContext (auth) och DataDbContext (fitness).

\- \*\*§PR Size Discipline\*\* ✅ — Uppskattat \~150–180 rader netto, väl inom 400-rader-regeln.



\## Scope Guardrails



\*\*IN SCOPE:\*\*

\- Ny `UserData.cs`

\- Ny `EquipmentData.cs`

\- Uppdatera `ExerciseData.cs`

\- Uppdatera `DataDbContext.cs`

\- Tester



\*\*OUT OF SCOPE (framtida iterationer):\*\*

\- `workout\_sessions`, `workout\_exercises`, `personal\_records` → Iteration 2

\- HttpClient-wrapper mot Python API → Iteration 3

\- Rör `User.cs`, `Equipment.cs`, `Exercise.cs` (AppDbContext-världen)

\- Migration till Postgres (Abdulrahman äger schema)

\- Refactor av existerande `Data`-suffix-namngivning



\## Dependencies



\- Issue #32 (parent tracking issue)

\- Constitution v1.1.0 §Architecture

\- Existerande `ExerciseData.cs`, `DataDbContext.cs` som utgångspunkt

\- Ingen extern beroende till Python API i denna iteration



\## Open Questions



\- \~\~Navigation-strategi för ExerciseData → EquipmentData?\~\~ \*\*Löst:\*\* Använd navigation till EquipmentData (inom DataDbContext-världen), inte till Equipment (AppDbContext-världen).

\- \~\~Ska `users` mappas till både AppDbContext och DataDbContext?\~\~ \*\*Löst:\*\* Ja, samma fysiska tabell, olika C#-entiteter (Abdulrahman bekräftat).

