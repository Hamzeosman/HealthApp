\# Implementation Plan: DataDbContext Iteration 2



\*\*Spec:\*\* `specs/003-datadb-iteration-2/spec.md`

\*\*Target PR size:\*\* \~240 rader netto



\## Files to change



| Fil | Typ | Uppskattad storlek |

|-----|-----|---------------------|

| `Models/WorkoutExerciseData.cs` | NY | \~50 rader |

| `Models/PersonalRecordData.cs` | NY | \~30 rader |

| `Models/WorkoutSessionData.cs` | UPPDATERA | +15 rader (StartTime, EndTime, 2 navigations) |

| `DataDbContext.cs` | UPPDATERA | +50 rader (2 DbSets + 5 constraints + 3 relations) |

| `HealthApp.Tests/Data/DataDbContextTests.cs` | UPPDATERA | +100 rader (6 nya tester) |



\## Implementation order



1\. \*\*PersonalRecordData.cs\*\* — enklast, ren mappning + 2 navigations.

2\. \*\*WorkoutExerciseData.cs\*\* — 10 kolumner + 2 navigations + 4 CHECK constraints i separate context.

3\. \*\*WorkoutSessionData.cs\*\* — komplettera med StartTime, EndTime + 2 navigations.

4\. \*\*DataDbContext.cs\*\* — DbSets, OnModelCreating (constraints + relations).

5\. \*\*DataDbContextTests.cs\*\* — utöka med 6 nya tester.

6\. \*\*`dotnet build`\*\* — måste kompilera.

7\. \*\*`dotnet test`\*\* — alla 30+ tester gröna (25 gamla + 5 från Iter 1 + 6 nya = 36).



\## Design decisions



\### Navigations följer Data-suffix-mönstret



Konsekvent med Iter 1-beslutet:

\- `WorkoutSessionData.User` → `UserData` (inte `User`)

\- `WorkoutSessionData.WorkoutExercises` → `ICollection<WorkoutExerciseData>`

\- `WorkoutExerciseData.Session` → `WorkoutSessionData`

\- `WorkoutExerciseData.Exercise` → `ExerciseData` (inte `Exercise`)

\- `PersonalRecordData.User` → `UserData`

\- `PersonalRecordData.Exercise` → `ExerciseData`



Detta håller DataDbContext-världen separerad från AppDbContext-världen.



\### TemplateId förblir int?, ingen navigation



`workout\_templates`-tabellen finns i schemat men är inte i Issue #32-scope. Vi mappar `TemplateId` som ren `int?`. Om vi senare vill EF-mappa `workout\_templates` kan navigation läggas till då.



\### CHECK constraints i OnModelCreating



Samma mönster som Iter 1. Fem constraints att lägga till:



```csharp

modelBuilder.Entity<WorkoutSessionData>()

&#x20;   .ToTable(t => t.HasCheckConstraint(

&#x20;       "CK\_workout\_sessions\_mood",

&#x20;       "mood IN ('bra','okej','trött','stark')"));



modelBuilder.Entity<WorkoutExerciseData>()

&#x20;   .ToTable(t =>

&#x20;   {

&#x20;       t.HasCheckConstraint("CK\_workout\_exercises\_sets",

&#x20;           "sets > 0 AND sets <= 20");

&#x20;       t.HasCheckConstraint("CK\_workout\_exercises\_reps",

&#x20;           "reps > 0 AND reps <= 100");

&#x20;       t.HasCheckConstraint("CK\_workout\_exercises\_weight\_kg",

&#x20;           "weight\_kg >= 0 AND weight\_kg <= 500");

&#x20;       t.HasCheckConstraint("CK\_workout\_exercises\_rpe",

&#x20;           "rpe >= 1 AND rpe <= 10");

&#x20;   });

```



Constraint-namnen speglar Postgres-namnen (`chk\_we\_\*`) för spårbarhet.



\### OnDelete-strategi



`SetNull` för alla FK (samma som Iter 1). Om en användare tas bort ska sessions inte tas bort — de blir orphaned med `UserId = null`. Detta matchar hur analytics-data ofta hanteras: rådata bevaras, ownership tappas.



Alternativ övervägt: `Cascade` för `session\_id → workout\_exercises`. Om ett pass raderas kan man argumentera att övningarna i det passet också bör raderas (de är beroende av passet). Men `SetNull` är säkrare — inget rådata försvinner oväntat.



\### personal\_records har inga CHECK constraints



Verifierat i migration\_p5\_quality.sql. Endast FK-relationer.



\## Test setup



Samma approach som Iter 1:

\- Reflection-baserade tester för mapping-attribut och navigation properties

\- Inga InMemory-provider (håller PR-scope snävt)

\- AAA-pattern enligt projektstandard



Tester utökar befintlig `DataDbContextTests.cs`-fil, ingen ny testfil.



\## Risker och mitigering



| Risk | Sannolikhet | Mitigering |

|------|-------------|------------|

| Constraint-namn krockar med Postgres befintliga | Låg | Vi använder `CK\_\*` prefix, Postgres har `chk\_\*` prefix — ingen konflikt |

| Navigation-collection (ICollection<WorkoutExerciseData>) skapar cirkulär referens vid JSON-serialisering | Medium | Reflection-tester bryr sig inte om detta. Om det blir problem i runtime-kod hanteras det i respektive Controller/Service |

| EF Core förvirras av att `WorkoutSession` och `WorkoutSessionData` mappar samma tabell | Medium | Två separata DbContexts → EF-runtime ser inte konflikten |



\## Constitution Check



\- \*\*§I. Layered Architecture\*\* ✅ Endast Models + DbContext

\- \*\*§II. Security-First\*\* ✅ CHECK constraints skyddar mot ogiltiga värden

\- \*\*§III. Test-Required\*\* ✅ 6 nya tester

\- \*\*§V. Code Quality\*\* ✅ Data-suffix-mönster + AAA-tester

\- \*\*§Architecture (data boundary)\*\* ✅ Ren user data-mapping

\- \*\*§PR Size Discipline\*\* ✅ \~240 rader netto



\## Out of scope (uttrycklig lista)



\- Migration-filer (Abdulrahman äger schema)

\- workout\_templates EF-mapping

\- Soft-delete på user data

\- CHECK constraints på UserData (senare chore-PR)

\- Refactor av existerande namngivning



\## Next commands



```powershell

notepad Models/PersonalRecordData.cs

notepad Models/WorkoutExerciseData.cs

notepad Models/WorkoutSessionData.cs         # uppdatera

notepad DataDbContext.cs                     # uppdatera

notepad HealthApp.Tests/Data/DataDbContextTests.cs  # utöka

dotnet build

dotnet test

```

