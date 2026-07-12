\# Feature Specification: DataDbContext Iteration 2 — Workout Tracking



\*\*Feature Branch:\*\* `feat/datadb-iteration-2-workout-tracking`

\*\*Created:\*\* 2026-07-11

\*\*Status:\*\* Draft

\*\*Iteration:\*\* 2 of 3 (Issue #32)

\*\*Input:\*\* Utöka DataDbContext med workout tracking-entiteter: WorkoutExerciseData, PersonalRecordData, och komplettera befintlig WorkoutSessionData.



\## Bakgrund



Iteration 2 av Issue #32 bygger på Iteration 1 (users/exercises/equipment) och lägger till de tre tabeller som utgör själva träningsloggen: `workout\_sessions`, `workout\_exercises`, och `personal\_records`. Dessa är kärnan i användarens fitness-historik och relaterar till både `UserData` och `ExerciseData` från Iteration 1.



Till skillnad från Iteration 1 (som var mest fristående mappings) introducerar denna iteration \*\*relations-nätverk\*\* mellan entiteter — WorkoutSession har många WorkoutExercises, WorkoutExercise refererar Exercise, PersonalRecord kopplar User + Exercise.



Efter PR #39 (P3) har `workout\_exercises` fått fyra CHECK constraints i Postgres (`sets`, `reps`, `weight\_kg`, `rpe`). Iteration 2 speglar dessa i `OnModelCreating()` så EF-modellen dokumenterar databasens sanning.



Constitution v1.1.0 §Architecture styr: dessa är \*\*user data\*\* (skapas av verkliga användare) i motsats till master data (seed:as av utvecklare). Ingen soft-delete i denna iteration — soft-delete är master-data-koncept per P3.



\## User Scenarios \& Testing



\### Primary User Story

Som .NET-utvecklare vill jag att `DataDbContext` exponerar `WorkoutSessionData`, `WorkoutExerciseData` och `PersonalRecordData` med korrekta navigations så att frontend/services kan hämta en användares träningshistorik med enkla EF-queries istället för att bygga JOINs manuellt.



\### Acceptance Scenarios



1\. \*\*Given\*\* en användare har loggade träningspass, \*\*When\*\* jag queryar `dataDbContext.WorkoutSessions.Include(s => s.User).Where(s => s.UserId == 1)`, \*\*Then\*\* får jag pass med tillhörande UserData-objekt.



2\. \*\*Given\*\* ett träningspass har flera övningar loggade, \*\*When\*\* jag queryar `dataDbContext.WorkoutSessions.Include(s => s.WorkoutExercises).ThenInclude(we => we.Exercise)`, \*\*Then\*\* får jag passet med alla dess WorkoutExercises + navigations till ExerciseData.



3\. \*\*Given\*\* en användare försöker spara `WorkoutExerciseData` med `Sets = 25`, \*\*When\*\* ändringen commitas, \*\*Then\*\* kastar Postgres constraint-fel (chk\_we\_sets CHECK sets <= 20).



4\. \*\*Given\*\* en användare har PRs på en specifik övning, \*\*When\*\* jag queryar `dataDbContext.PersonalRecords.Where(pr => pr.UserId == 1 \&\& pr.ExerciseId == 5)`, \*\*Then\*\* får jag alla PRs för den kombinationen.



5\. \*\*Given\*\* `WorkoutSessionData` tidigare saknade `start\_time` och `end\_time`, \*\*When\*\* jag laddar en session, \*\*Then\*\* har den `StartTime` och `EndTime` som DateTime? mappade mot rätt snake\_case-kolumner.



\### Edge Cases



\- Vad händer om `workout\_sessions.user\_id` är null? → Property är nullable, User-navigation är null.

\- Vad händer om `workout\_sessions.template\_id` refererar template som inte finns EF-mappad? → Vi håller `TemplateId` som ren int? utan navigation (workout\_templates är out of scope).

\- Vad händer om `workout\_exercises.session\_id` är null? → Session-navigation är null.

\- Vad händer om någon råkar lägga till `Password` i `WorkoutSessionData`? → Reflection-test (om vi utökar det) failar. FR-003 från Iter 1 fortsätter gälla.



\## Requirements



\### Functional Requirements



\- \*\*FR-001:\*\* `WorkoutExerciseData`-entitet MÅSTE mappa mot `workout\_exercises`-tabellen via `\[Table("workout\_exercises")]`.

\- \*\*FR-002:\*\* `WorkoutExerciseData` MÅSTE innehålla: `Id`, `SessionId`, `ExerciseId`, `Sets`, `Reps`, `WeightKg`, `DurationSeconds`, `RestSeconds`, `Rpe`, `Notes`.

\- \*\*FR-003:\*\* `WorkoutExerciseData` MÅSTE ha navigation properties `Session` (till `WorkoutSessionData`) och `Exercise` (till `ExerciseData`).

\- \*\*FR-004:\*\* `PersonalRecordData`-entitet MÅSTE mappa mot `personal\_records`-tabellen med fälten `Id`, `UserId`, `ExerciseId`, `WeightKg`, `Reps`, `Date`, `Notes`.

\- \*\*FR-005:\*\* `PersonalRecordData` MÅSTE ha navigation properties `User` (till `UserData`) och `Exercise` (till `ExerciseData`).

\- \*\*FR-006:\*\* Befintlig `WorkoutSessionData` MÅSTE utökas med `StartTime` och `EndTime` (DateTime?, mappade mot `start\_time` och `end\_time`).

\- \*\*FR-007:\*\* `WorkoutSessionData` MÅSTE ha navigation properties `User` (till `UserData`) och `WorkoutExercises` (ICollection till `WorkoutExerciseData`).

\- \*\*FR-008:\*\* `DataDbContext` MÅSTE exponera `DbSet<WorkoutExerciseData> WorkoutExercises` och `DbSet<PersonalRecordData> PersonalRecords`.

\- \*\*FR-009:\*\* `OnModelCreating` MÅSTE konfigurera CHECK constraints:

&#x20; - `WorkoutSessionData.Mood` IN ('bra','okej','trött','stark')

&#x20; - `WorkoutExerciseData.Sets` mellan 1 och 20

&#x20; - `WorkoutExerciseData.Reps` mellan 1 och 100

&#x20; - `WorkoutExerciseData.WeightKg` mellan 0 och 500

&#x20; - `WorkoutExerciseData.Rpe` mellan 1 och 10

\- \*\*FR-010:\*\* `OnModelCreating` MÅSTE konfigurera relationer med `OnDelete(DeleteBehavior.SetNull)` för alla nya FK (samma mönster som Iter 1).

\- \*\*FR-011:\*\* `TemplateId` i `WorkoutSessionData` MÅSTE förbli ren `int?` utan navigation (workout\_templates är out of scope).

\- \*\*FR-012:\*\* PascalCase-klasserna `WorkoutSession`, `WorkoutExercise`, `PersonalRecord` (AppDbContext-världen) MÅSTE INTE modifieras.



\### Key Entities



\- \*\*WorkoutExerciseData\*\* (ny) → tabell `workout\_exercises`, med navigation till Session + Exercise

\- \*\*PersonalRecordData\*\* (ny) → tabell `personal\_records`, med navigation till User + Exercise

\- \*\*WorkoutSessionData\*\* (uppdatera) → lägg till StartTime, EndTime + navigation till User och WorkoutExercises



\## Testing Strategy



Tester utökar `HealthApp.Tests/Data/DataDbContextTests.cs`:



1\. \*\*`WorkoutExerciseData\_MapsToWorkoutExercisesTable`\*\* — Verifierar `\[Table]` + snake\_case-kolumner.

2\. \*\*`WorkoutExerciseData\_HasSessionAndExerciseNavigations`\*\* — Verifierar navigation properties finns och pekar på rätt typer.

3\. \*\*`PersonalRecordData\_MapsToPersonalRecordsTable`\*\* — Verifierar `\[Table]` + snake\_case-kolumner.

4\. \*\*`PersonalRecordData\_HasUserAndExerciseNavigations`\*\* — Verifierar navigation properties.

5\. \*\*`WorkoutSessionData\_HasStartTimeAndEndTimeColumns`\*\* — Verifierar de två nya kolumnerna.

6\. \*\*`WorkoutSessionData\_HasUserAndWorkoutExercisesNavigations`\*\* — Verifierar navigation properties.



Reflection-baserade tester — ingen EF InMemory-provider behövs (samma approach som Iter 1).



\## Constitution Alignment



\- \*\*§I. Layered Architecture\*\* ✅ — Endast Model-lagret berörs.

\- \*\*§II. Security-First\*\* ✅ — Ingen känslig data introduceras; CHECK constraints skyddar mot ogiltiga värden.

\- \*\*§III. Test-Required\*\* ✅ — 6 nya tester planerade.

\- \*\*§V. Code Quality\*\* ✅ — Följer `Data`-suffix-mönster.

\- \*\*§Architecture (data boundary)\*\* ✅ — Ren user data-mapping mot Abdulrahmans schema.

\- \*\*§PR Size Discipline\*\* ✅ — Uppskattat \~240 rader netto, väl inom 400-rader-regeln.



\## Scope Guardrails



\*\*IN SCOPE:\*\*

\- Ny `WorkoutExerciseData.cs`

\- Ny `PersonalRecordData.cs`

\- Uppdatera `WorkoutSessionData.cs` (StartTime, EndTime, navigations)

\- Uppdatera `DataDbContext.cs` (DbSets + OnModelCreating)

\- 6 nya tester



\*\*OUT OF SCOPE (framtida iterationer):\*\*

\- HttpClient-wrapper mot Python API → Iteration 3

\- `workout\_templates` EF-mapping

\- Soft-delete på user data (P3 införde det på master data — user data behåller hard delete)

\- CHECK constraints på `UserData.WeightKg`/`HeightCm` (chore-PR senare)

\- Refactor av existerande `Data`-suffix-namngivning

\- Rör `WorkoutSession.cs`, `WorkoutExercise.cs`, `PersonalRecord.cs` (AppDbContext-världen)



\## Dependencies



\- Iteration 1 av Issue #32 (mergad) — `UserData`, `ExerciseData` referens

\- Constitution v1.1.0 §Architecture

\- Migration p5\_quality (mergad via PR #39) — källa till CHECK constraints

\- Ingen extern beroende till Python API i denna iteration



\## Open Questions



\- \~\~Constraints på workout\_sessions/personal\_records?\~\~ \*\*Löst:\*\* Bara `mood` på workout\_sessions (från schema.sql), inga constraints på personal\_records.

\- \~\~Navigation till User/Exercise via Data-suffix eller PascalCase?\~\~ \*\*Löst:\*\* `UserData`/`ExerciseData` (konsekvent med Iter 1).

\- \~\~Ska `template\_id` få navigation?\~\~ \*\*Löst:\*\* Nej, ren int? tills workout\_templates mappas.

