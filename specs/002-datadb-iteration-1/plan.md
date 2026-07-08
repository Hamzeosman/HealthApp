\# Implementation Plan: DataDbContext Iteration 1



\*\*Spec:\*\* `specs/002-datadb-iteration-1/spec.md`

\*\*Target PR size:\*\* \~150–180 rader netto



\## Files to change



| Fil | Typ | Uppskattad storlek |

|-----|-----|---------------------|

| `Models/UserData.cs` | NY | \~35 rader |

| `Models/EquipmentData.cs` | NY | \~15 rader |

| `Models/ExerciseData.cs` | UPPDATERA | +5 rader (CaloriesPerMinute + navigation) |

| `DataDbContext.cs` | UPPDATERA | +25 rader (2 DbSets + OnModelCreating) |

| `HealthApp.Tests/Data/DataDbContextTests.cs` | NY | \~80 rader (5 tester) |



\## Implementation order



1\. \*\*UserData.cs\*\* — enklast, ingen navigation.

2\. \*\*EquipmentData.cs\*\* — trivial lookup.

3\. \*\*ExerciseData.cs\*\* — lägg till kolumn + navigation.

4\. \*\*DataDbContext.cs\*\* — DbSets och OnModelCreating.

5\. \*\*DataDbContextTests.cs\*\* — verifiera allt.

6\. \*\*`dotnet build`\*\* — måste kompilera.

7\. \*\*`dotnet test`\*\* — alla tester gröna.



\## Design decisions



\### UserData mappar samma tabell som User



`User.cs` (AppDbContext) och `UserData.cs` (DataDbContext) mappar båda mot fysiska `users`-tabellen men \*\*olika kolumn-subset\*\*. Detta är per Abdulrahmans bekräftelse och Constitution §Architecture — inte en dubblettbug.



\*\*Skydd mot regression:\*\* `UserData\_MustNotHaveAuthFields`-testet använder reflection för att kontrollera att inga properties `Email`/`Password`/`PasswordHash` smyger in.



\### Navigation ExerciseData → EquipmentData (inte → Equipment)



Vi håller oss inom DataDbContext-världen för konsekvens. `EquipmentId` är fortsatt nullable int.



\### Check constraints i OnModelCreating



Anpassade check constraints (Postgres) mappas via `HasCheckConstraint()` i EF Core så att .NET-koden inte behöver duplicera valideringen — databasen är sanningen.



```csharp

modelBuilder.Entity<UserData>()

&#x20;   .ToTable(t => t.HasCheckConstraint(

&#x20;       "CK\_users\_fitness\_level",

&#x20;       "fitness\_level IN ('nybörjare','medel','avancerad')"));

```



\## Test setup



Tester ligger i `HealthApp.Tests/Data/`. Vi använder:



\- \*\*Reflection-tester\*\* för arkitekturregler (ingen DB behövs)

\- \*\*EF Core InMemory\*\* för sanity-tester av kolumnmappning

\- \*\*AAA-pattern\*\* enligt projektstandard (matchar befintlig test-stil)



Ingen ny test-infrastruktur behövs.



\## Risker och mitigering



| Risk | Sannolikhet | Mitigering |

|------|-------------|------------|

| Check constraint krockar med Abdulrahmans befintliga schema | Låg | Constraint-namn har prefix `CK\_` + tabell + kolumn; om Postgres redan har constraint blir det no-op eller EF-error som fångas i test |

| `UserData` och `User` mappar samma tabell → EF varnar om duplicerad DbSet | Medium | Vi har två separata DbContexts, så EF-runtime ser inte konflikten. Varning i modell-validering ignoreras |

| Reflection-test failar vid framtida property-tillägg | Low | Testet är designat exakt för det — att fånga oönskade tillägg |



\## Constitution Check



\- \*\*§I. Layered Architecture\*\* ✅ Endast Models + DbContext berörs

\- \*\*§II. Security-First\*\* ✅ FR-003 skyddad av reflection-test

\- \*\*§III. Test-Required\*\* ✅ 5 tester

\- \*\*§V. Code Quality\*\* ✅ Följer `Data`-suffix-mönster + AAA-tester

\- \*\*§Architecture (data boundary)\*\* ✅ Ingen Python API-integration i denna PR

\- \*\*§PR Size Discipline\*\* ✅ \~160 rader netto



\## Out of scope (uttrycklig lista)



\- Migration-filer (Abdulrahman äger schema)

\- Refactor av `ExerciseData` → `Exercise` (namngivning)

\- Repository/Service-lager ovanpå (kommer i egen PR när behov uppstår)

\- Frontend-ändringar



\## Next commands



Efter att spec + plan är klara, börjar vi implementera i denna ordning:



```powershell

notepad Models/UserData.cs

notepad Models/EquipmentData.cs

notepad Models/ExerciseData.cs  # uppdatera

notepad DataDbContext.cs         # uppdatera

notepad HealthApp.Tests/Data/DataDbContextTests.cs

dotnet build

dotnet test

```

