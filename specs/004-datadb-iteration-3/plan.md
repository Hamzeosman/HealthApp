\# Implementation Plan: DataDbContext Iteration 3



\*\*Spec:\*\* `specs/004-datadb-iteration-3/spec.md`

\*\*Target PR size:\*\* \~350 rader netto



\## Files to change



| Fil | Typ | Uppskattad storlek |

|-----|-----|---------------------|

| `Services/IPythonApiClient.cs` | NY | \~30 rader |

| `Services/PythonApiClient.cs` | NY | \~130 rader |

| `Services/PythonApiOptions.cs` | NY | \~15 rader |

| `Services/PythonApiException.cs` | NY | \~25 rader |

| `Models/Dtos/FatigueScoreDto.cs` | NY | \~20 rader |

| `Models/Dtos/RecommendationDto.cs` | NY | \~18 rader |

| `Models/Dtos/ModelPredictionDto.cs` | NY | \~22 rader |

| `Models/Dtos/AiInsightDto.cs` | NY | \~15 rader |

| `Models/Dtos/CoachMessageDto.cs` | NY | \~18 rader |

| `Program.cs` | UPPDATERA | +15 rader (DI-registrering + options-binding) |

| `appsettings.json` | UPPDATERA | +6 rader (PythonApi-sektion utan nyckel) |

| `HealthApp.Tests/Services/PythonApiClientTests.cs` | NY | \~180 rader (8-10 tester) |



\## Implementation order



1\. \*\*DTOs\*\* — börjar med datastrukturerna (rena POCOs, inga beroenden)

2\. \*\*PythonApiException\*\* — typed exception, ingen logik

3\. \*\*PythonApiOptions\*\* — options-klass för konfiguration

4\. \*\*IPythonApiClient\*\* — interface (kontrakt)

5\. \*\*PythonApiClient\*\* — implementation

6\. \*\*Program.cs\*\* — DI-registrering via `AddHttpClient<>`

7\. \*\*appsettings.json\*\* — konfigurationsstruktur

8\. \*\*PythonApiClientTests\*\* — 8-10 tester med mockad HttpMessageHandler

9\. \*\*`dotnet build`\*\* — måste kompilera

10\. \*\*`dotnet test`\*\* — 36 befintliga + \~8-10 nya = \~44-46 gröna



\## Design decisions



\### Typed HttpClient-mönster (inte IHttpClientFactory + manual)



Använder `AddHttpClient<IPythonApiClient, PythonApiClient>()` istället för att injecta `IHttpClientFactory` manuellt. Detta ger:

\- Automatisk lifecycle-hantering (undviker socket-exhaustion)

\- Konfiguration av HttpClient centralt i `Program.cs`

\- X-API-Key och BaseUrl sätts en gång, inte i varje anrop



\### Snake\_case ↔ PascalCase via JsonSerializerOptions



Python API returnerar `snake\_case` JSON. .NET DTOs använder `PascalCase` per konvention. Löses centralt via:



```csharp

services.AddHttpClient<IPythonApiClient, PythonApiClient>()

&#x20;   .ConfigureHttpClient((sp, client) => {

&#x20;       var options = sp.GetRequiredService<IOptions<PythonApiOptions>>().Value;

&#x20;       client.BaseAddress = new Uri(options.BaseUrl);

&#x20;       client.DefaultRequestHeaders.Add("X-API-Key", options.ApiKey);

&#x20;       client.Timeout = TimeSpan.FromSeconds(options.TimeoutSeconds);

&#x20;   });

```



Deserialiseringsalternativ konfigureras i `PythonApiClient` med `PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower`.



\### 404 → null / tom lista, inte exception



Python API returnerar 404 när data inte finns för en användare (t.ex. ny user utan fatigue scores än). Detta är \*\*förväntat\*\*, inte fel. Klienten översätter:



\- Single-item endpoints (`GetFatigueScoreAsync`) → `null`

\- List endpoints (`GetRecommendationsAsync`) → `Enumerable.Empty<T>()`



Andra fel (401, 403, 500, timeout) → `PythonApiException`.



\### X-API-Key från user-secrets, inte appsettings.json



Enligt Constitution §Security-First och `chore(security)`-issuen #40. `appsettings.json` innehåller bara struktur:



```json

{

&#x20; "PythonApi": {

&#x20;   "BaseUrl": "http://localhost:8000",

&#x20;   "TimeoutSeconds": 30

&#x20; }

}

```



`ApiKey` sätts via `dotnet user-secrets set "PythonApi:ApiKey" "..."` för dev. README-uppdatering kommer i egen chore-PR (issue #40).



\### Options-mönster istället för IConfiguration direkt



`PythonApiOptions`-klass binds mot `PythonApi`-sektion i konfigurationen. Ger:

\- Typad access i klientkoden

\- Validation-möjlighet i framtiden (`ValidateDataAnnotations()`)

\- Testbarhet (kan mocka `IOptions<PythonApiOptions>`)



\### DTO-nullability speglar Python API-verkligheten



Python-sidan returnerar `null` för vissa fält när data inte är beräknat än (t.ex. `deload\_recommended` är null första veckan). Alla DTO-properties är därför nullable.



\### Ingen retry i första versionen



Constitution §PR Size Discipline pressar oss att hålla scope smalt. Retry-policy kan läggas till senare via Polly om produktion visar behov. Explicit not i `Open Questions` i spec.md.



\## Test setup



Använder `Moq.Protected` för att mocka `HttpMessageHandler` (standardapproach för HttpClient-testning):



```csharp

var mockHandler = new Mock<HttpMessageHandler>();

mockHandler.Protected()

&#x20;   .Setup<Task<HttpResponseMessage>>("SendAsync", ItExpr.IsAny<HttpRequestMessage>(), ItExpr.IsAny<CancellationToken>())

&#x20;   .ReturnsAsync(new HttpResponseMessage

&#x20;   {

&#x20;       StatusCode = HttpStatusCode.OK,

&#x20;       Content = new StringContent("""{"user\_id":1,"date":"2026-09-15",...}""")

&#x20;   });



var httpClient = new HttpClient(mockHandler.Object) { BaseAddress = new Uri("http://test/") };

httpClient.DefaultRequestHeaders.Add("X-API-Key", "test-key");

var sut = new PythonApiClient(httpClient);

```



Testerna följer projektets AAA-pattern med `\_sut`/`\_mockXxx`-fält som backend-testkonvention.



\## Risker och mitigering



| Risk | Sannolikhet | Mitigering |

|------|-------------|------------|

| Python API-schemat ändras → DTOs blir stale | Medium | Reflection-tester som failar vid saknad property. Vi äger inte schemat. |

| X-API-Key läcker i logs/errors | Låg | `PythonApiException` inkluderar aldrig headers, bara URL + status |

| HttpClient socket-exhaustion | Låg | Typed client-mönster via `AddHttpClient<>` hanterar det automatiskt |

| Snake\_case-mismatch på ny endpoint | Medium | Centralt konfigurerat i `PythonApiClient` — en plats att fixa |

| Timeout för kort för slow AI-endpoints | Låg | Default 30s, konfigurerbar per environment |



\## Constitution Check



\- \*\*§I. Layered Architecture\*\* ✅ Nytt Services-lager

\- \*\*§II. Security-First\*\* ✅ API-nyckel via config, typed exceptions

\- \*\*§III. Test-Required\*\* ✅ Mockad HttpClient, \~8-10 tester

\- \*\*§V. Code Quality\*\* ✅ Typed client, interface-baserad DI

\- \*\*§Architecture (data boundary)\*\* ✅ Ren HTTP-integration

\- \*\*§PR Size Discipline\*\* ⚠️ \~350 rader netto, inom 400-gränsen



\## Out of scope (uttrycklig lista)



\- Retry-policy (Polly) — framtid om behov uppstår

\- Circuit breaker

\- Response caching

\- Frontend-integration

\- Controllers som exponerar Python API-data

\- POST/PUT-endpoints (denna PR läser bara)

\- README-uppdatering med user-secrets-instruktioner (chore #40)



\## Next commands



```powershell

mkdir Services

mkdir Models/Dtos

mkdir HealthApp.Tests/Services



notepad Models/Dtos/FatigueScoreDto.cs

notepad Models/Dtos/RecommendationDto.cs

notepad Models/Dtos/ModelPredictionDto.cs

notepad Models/Dtos/AiInsightDto.cs

notepad Models/Dtos/CoachMessageDto.cs



notepad Services/PythonApiException.cs

notepad Services/PythonApiOptions.cs

notepad Services/IPythonApiClient.cs

notepad Services/PythonApiClient.cs



notepad Program.cs

notepad appsettings.json



notepad HealthApp.Tests/Services/PythonApiClientTests.cs



dotnet build

dotnet test

```

