\# Feature Specification: DataDbContext Iteration 3 — Python API HttpClient Wrapper



\*\*Feature Branch:\*\* `feat/datadb-iteration-3-python-api-wrapper`

\*\*Created:\*\* 2026-09-15

\*\*Status:\*\* Draft

\*\*Iteration:\*\* 3 of 3 (Issue #32 — final)

\*\*Input:\*\* Skapa HttpClient-wrapper i .NET för att anropa Abdulrahmans Python API. Wrappern hanterar 5 endpoint-familjer: fatigue\_scores, recommendations, model\_predictions, ai\_insights, coach\_messages. Autentiseras via X-API-Key mot healthapp\_ai\_service-rollen.



\## Bakgrund



Iteration 1 \& 2 av Issue #32 mappade EF-entiteter mot fysiska Postgres-tabeller (users, exercises, workout\_sessions m.fl.). Denna iteration är \*\*arkitekturellt annorlunda\*\*: fyra av tabellerna i Issue #32:s scope äger Python-sidan exklusivt via ett REST API, inte via delad Postgres-åtkomst.



\*\*Data boundary per Constitution v1.1.0 §Architecture:\*\*

\- `AppDbContext` → auth-data (EF direkt mot Postgres)

\- `DataDbContext` → analytics-data (EF direkt mot Postgres)

\- \*\*Python API\*\* → AI/predictions (HTTP-anrop, denna PR bygger klienten)



Enligt PR #46 (mergad) har Abdulrahman infört 5 PostgreSQL-roller med tydlig ansvarsfördelning. .NET-koden ska mot Python-API:et använda `healthapp\_ai\_service`-rollen via X-API-Key-headern.



\## User Scenarios \& Testing



\### Primary User Story

Som .NET-utvecklare vill jag ha en typad HttpClient-wrapper som exponerar Python API-endpoints som strongly-typed metoder (`GetFatigueScoreAsync(userId, date)`), så att frontend-services kan hämta AI-genererad data utan att bygga HTTP-anrop manuellt eller hantera serialisering per anrop.



\### Acceptance Scenarios



1\. \*\*Given\*\* en användare finns i systemet, \*\*When\*\* frontend anropar `IPythonApiClient.GetFatigueScoreAsync(userId, date)`, \*\*Then\*\* returneras `FatigueScoreDto` med acwr, readiness\_score, fatigue\_score m.fl.



2\. \*\*Given\*\* en användare har rekommendationer, \*\*When\*\* frontend anropar `GetRecommendationsAsync(userId)`, \*\*Then\*\* returneras `IEnumerable<RecommendationDto>` med exercise\_name och body\_part (denormaliserade från Python-sidan).



3\. \*\*Given\*\* Python API är nere, \*\*When\*\* ett anrop görs, \*\*Then\*\* kastas en typed exception (`PythonApiException`) med meningsfull felinformation — inte en rå `HttpRequestException`.



4\. \*\*Given\*\* X-API-Key saknas eller är felaktig, \*\*When\*\* ett anrop görs, \*\*Then\*\* returneras 401/403 → typed exception med tydlig felmeddelande.



5\. \*\*Given\*\* timeout på Python API-svar, \*\*When\*\* anropet överskrider konfigurerad timeout, \*\*Then\*\* kastas timeout-exception istället för att blockera oändligt.



6\. \*\*Given\*\* coach\_messages är kunskapsbas (inte per user), \*\*When\*\* frontend anropar `GetCoachMessagesAsync(category)`, \*\*Then\*\* returneras `IEnumerable<CoachMessageDto>` utan user\_id-parameter.



\### Edge Cases



\- Vad händer om Python API returnerar 404 (data finns inte för användaren)? → Returnera `null` eller tom lista beroende på endpoint-typ; ingen exception.

\- Vad händer vid transient network-fel? → Retry med exponentiell backoff (max 3 försök).

\- Vad händer om JSON-svaret inte matchar DTO-strukturen? → Deserialiseringsfel loggas + typed exception; misslyckat anrop bryter inte hela applikationen.

\- Vad händer om X-API-Key läggs i appsettings.json? → \*\*Nej.\*\* Nyckeln läses från user-secrets (dev) eller miljövariabler (production).



\## Requirements



\### Functional Requirements



\- \*\*FR-001:\*\* Ett interface `IPythonApiClient` MÅSTE definieras med metoder för alla 5 endpoint-familjer.

\- \*\*FR-002:\*\* En implementation `PythonApiClient` MÅSTE implementera `IPythonApiClient` via `HttpClient` (typed client-mönster).

\- \*\*FR-003:\*\* 5 DTOs MÅSTE skapas i `Models/Dtos/`-mappen:

&#x20; - `FatigueScoreDto` (8 fält: user\_id, date, acwr, training\_zone, readiness\_score, recovery\_score, fatigue\_score, deload\_recommended)

&#x20; - `RecommendationDto` (7 fält: user\_id, exercise\_id, exercise\_name, body\_part, score, reason, created\_at)

&#x20; - `ModelPredictionDto` (9 fält: user\_id, date, injury\_risk\_score, dropout\_risk\_score, overtraining\_risk\_score, recommended\_intensity, recommended\_volume\_multiplier, primary\_recommendation, confidence\_score)

&#x20; - `AiInsightDto` (5 fält: user\_id, title, content, insight\_type, created\_at)

&#x20; - `CoachMessageDto` (7 fält: category, trigger\_type, message\_sv, message\_en, tone, language, priority — INGEN user\_id)

\- \*\*FR-004:\*\* X-API-Key MÅSTE injiceras i alla utgående requests via `DefaultRequestHeaders` konfigurerat vid DI-registrering.

\- \*\*FR-005:\*\* X-API-Key MÅSTE läsas från konfiguration (`IConfiguration`), aldrig hårdkodad i källkod.

\- \*\*FR-006:\*\* `PythonApiClient` MÅSTE ha typed exception `PythonApiException` som inkluderar HTTP-statuskod och request-URL.

\- \*\*FR-007:\*\* 404-svar från Python API MÅSTE returnera `null` (single-item endpoints) eller tom `IEnumerable` (list endpoints) — inte exception.

\- \*\*FR-008:\*\* Timeout MÅSTE konfigureras (default 30 sekunder, konfigurerbar via appsettings).

\- \*\*FR-009:\*\* JSON-deserialisering MÅSTE använda snake\_case-konvention (Python API returnerar snake\_case JSON, DTOs har PascalCase properties).

\- \*\*FR-010:\*\* Klienten MÅSTE registreras via `AddHttpClient<IPythonApiClient, PythonApiClient>()` i `Program.cs` för korrekt HttpClient-lifecycle.



\### Key Entities



\- \*\*IPythonApiClient\*\* (nytt interface) — kontrakt för Python API-anrop

\- \*\*PythonApiClient\*\* (ny klass) — typed HttpClient-implementation

\- \*\*5 DTOs\*\* — matchar Python API:s JSON-svar

\- \*\*PythonApiException\*\* (ny exception) — typed error-hantering

\- \*\*PythonApiOptions\*\* (ny options-klass) — konfiguration för BaseUrl, ApiKey, Timeout



\## Testing Strategy



Tester i ny mapp `HealthApp.Tests/Services/`:



1\. \*\*`PythonApiClientTests`\*\* — verifierar wrapper-beteende med mockad `HttpMessageHandler`:

&#x20;  - Happy path: 200 OK → returnerar korrekt DTO

&#x20;  - 404-hantering: single-item returnerar `null`, list returnerar tom collection

&#x20;  - 401/403-hantering: kastar `PythonApiException` med rätt statuskod

&#x20;  - 500-hantering: kastar exception, inte silent fail

&#x20;  - Timeout: exception kastas

&#x20;  - X-API-Key finns i utgående requests (verifieras via mock)

&#x20;  - Snake\_case JSON deserialiseras korrekt till PascalCase DTOs



Ingen faktisk HTTP-trafik i tester — allt mockat via `Moq.Protected` på `HttpMessageHandler`.



\## Constitution Alignment



\- \*\*§I. Layered Architecture\*\* ✅ — Nytt lager (Services) mellan Controllers och externt API

\- \*\*§II. Security-First\*\* ✅ — API-nyckel via config (aldrig hårdkodad), typed exceptions förhindrar informationsläckage

\- \*\*§III. Test-Required\*\* ✅ — Mockad HttpClient-testning enligt best practice

\- \*\*§V. Code Quality\*\* ✅ — Typed client-mönster, tydligt interface, snake\_case → PascalCase konvention

\- \*\*§Architecture (data boundary)\*\* ✅ — Ren HTTP-integration, ingen delad Postgres-åtkomst

\- \*\*§PR Size Discipline\*\* ⚠️ — Uppskattat \~350 rader netto, nära 400-gränsen men inom



\## Scope Guardrails



\*\*IN SCOPE:\*\*

\- `Services/IPythonApiClient.cs`

\- `Services/PythonApiClient.cs`

\- `Services/PythonApiOptions.cs`

\- `Services/PythonApiException.cs`

\- `Models/Dtos/FatigueScoreDto.cs`

\- `Models/Dtos/RecommendationDto.cs`

\- `Models/Dtos/ModelPredictionDto.cs`

\- `Models/Dtos/AiInsightDto.cs`

\- `Models/Dtos/CoachMessageDto.cs`

\- `Program.cs` — DI-registrering + options-binding

\- `appsettings.json` — placeholder för PythonApi-sektion (utan nyckel)

\- `HealthApp.Tests/Services/PythonApiClientTests.cs`



\*\*OUT OF SCOPE:\*\*

\- Retry-policy (kan läggas till senare med Polly om behovet uppstår)

\- Circuit breaker

\- Response caching

\- Frontend-integration (kommande separat arbete)

\- Controllers som exponerar Python API-data via .NET (kommande PR)

\- POST/PUT-endpoints mot Python API (vi läser bara i denna iteration)

\- Refactor av `DataDbContext` (Iter 1 \& 2 mergade oförändrade)



\## Dependencies



\- Iteration 1 \& 2 av Issue #32 (mergade)

\- Constitution v1.1.0 §Architecture (data boundary)

\- PR #46 (mergad) — rollmatris + `healthapp\_ai\_service`-roll

\- Python API måste vara körande med X-API-Key-autentisering — inte något denna PR verifierar (out of scope)



\## Open Questions



\- \~\~Vilken PostgreSQL-roll mappar X-API-Key mot?\~\~ \*\*Löst (PR #44-review):\*\* `healthapp\_ai\_service`

\- \~\~Vilka DTO-shapes har Python API?\~\~ \*\*Löst (PR #44-review):\*\* 5 DTOs specificerade

\- \~\~coach\_messages per user eller kunskapsbas?\~\~ \*\*Löst:\*\* kunskapsbas, ingen user\_id

\- \*\*Retry-strategi\*\* — För nu ingen retry; om produktion visar behov kan Polly läggas till i separat PR

