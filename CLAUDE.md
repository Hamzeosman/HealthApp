# Mintakt API

ASP.NET Core Web API (.NET 10) med PostgreSQL, JWT och Scalar. Python-delen finns i `data/`.

## Regler
- Läs `.specify/memory/constitution.md`. Den går före en plan som strider mot den.
- Nya funktioner och större fixar startas med `/ny-funktion`. Tester skrivs först.
- Svara på svenska, kort och ett steg i taget.
- Conventional Commits och högst 400 ändrade rader per PR, utan genererade filer.
- Merga aldrig och pusha aldrig direkt till `master`.

## Arkitektur
- Flöde: Controller → Service → Repository. Använd DTO:er i API-gränsen.
- `AppDbContext`: inloggning, identitet och användardata.
- `DataDbContext`: delade tabeller. Entiteter har suffixet `Data`, till exempel `ExerciseData`.
- Fel returneras som `ProblemDetails`. Främmande nycklar använder `DeleteBehavior.SetNull`.
- Schemaändringar i datadelen stäms av med Abdulrahman.

## Kör i en worktree
Varje worktree har egna databaser och en egen port. Kör kommandon som behöver dem så här:
```
node scripts/worktree/worktree.mjs exec dotnet run --no-launch-profile
node scripts/worktree/worktree.mjs exec dotnet ef database update --context AppDbContext
```
Kör bara ett tungt jobb åt gången per dator: en server, ett testpass eller ett bygge.

<!-- SPECKIT START -->
For additional context about technologies to be used, project structure,
shell commands, and other important information, read the current plan
<!-- SPECKIT END -->
