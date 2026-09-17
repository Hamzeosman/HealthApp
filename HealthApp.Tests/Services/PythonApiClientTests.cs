using System.Net;
using System.Text;
using HealthApp.API.DTOs;
using HealthApp.API.Services;
using Moq;
using Moq.Protected;

namespace HealthApp.Tests.Services
{
    // Tester för PythonApiClient (Iteration 3 av Issue #32).
    // Använder Moq.Protected för att mocka HttpMessageHandler — standard-approach
    // för HttpClient-testning eftersom HttpClient inte enkelt kan mockas direkt.
    public class PythonApiClientTests
    {
        private readonly Mock<HttpMessageHandler> _handlerMock;
        private readonly PythonApiClient _sut;

        public PythonApiClientTests()
        {
            _handlerMock = new Mock<HttpMessageHandler>();

            var httpClient = new HttpClient(_handlerMock.Object)
            {
                BaseAddress = new Uri("http://test-python-api/")
            };
            httpClient.DefaultRequestHeaders.Add("X-API-Key", "test-api-key");

            _sut = new PythonApiClient(httpClient);
        }

        // Helper: konfigurerar mock att returnera given statuskod + valfri JSON body
        private void GivenResponse(HttpStatusCode statusCode, string? jsonBody = null)
        {
            var response = new HttpResponseMessage(statusCode);
            if (jsonBody is not null)
            {
                response.Content = new StringContent(jsonBody, Encoding.UTF8, "application/json");
            }

            _handlerMock.Protected()
                .Setup<Task<HttpResponseMessage>>(
                    "SendAsync",
                    ItExpr.IsAny<HttpRequestMessage>(),
                    ItExpr.IsAny<CancellationToken>())
                .ReturnsAsync(response);
        }

        // Happy path: 200 OK med snake_case JSON deserialiseras till PascalCase DTO
        [Fact]
        public async Task GetFatigueScoreAsync_WhenOkResponse_ReturnsDeserializedDto()
        {
            var jsonBody = """
            {
                "user_id": 42,
                "date": "2026-09-15",
                "acwr": 1.2,
                "training_zone": "optimal",
                "readiness_score": 85.5,
                "recovery_score": 78.0,
                "fatigue_score": 22.5,
                "deload_recommended": false
            }
            """;
            GivenResponse(HttpStatusCode.OK, jsonBody);

            var result = await _sut.GetFatigueScoreAsync(42, new DateTime(2026, 9, 15));

            Assert.NotNull(result);
            Assert.Equal(42, result.UserId);
            Assert.Equal(1.2m, result.Acwr);
            Assert.Equal("optimal", result.TrainingZone);
            Assert.Equal(85.5m, result.ReadinessScore);
            Assert.False(result.DeloadRecommended);
        }

        // 404 för single-item endpoint → null (förväntat läge för ny user utan data)
        [Fact]
        public async Task GetFatigueScoreAsync_WhenNotFound_ReturnsNull()
        {
            GivenResponse(HttpStatusCode.NotFound);

            var result = await _sut.GetFatigueScoreAsync(999, DateTime.Today);

            Assert.Null(result);
        }

        // 404 för list-endpoint → tom lista (inte null, inte exception)
        [Fact]
        public async Task GetRecommendationsAsync_WhenNotFound_ReturnsEmptyList()
        {
            GivenResponse(HttpStatusCode.NotFound);

            var result = await _sut.GetRecommendationsAsync(999);

            Assert.NotNull(result);
            Assert.Empty(result);
        }

        // Happy path list: JSON-array deserialiseras korrekt
        [Fact]
        public async Task GetRecommendationsAsync_WhenOkResponse_ReturnsDtoList()
        {
            var jsonBody = """
            [
                {
                    "user_id": 42,
                    "exercise_id": 10,
                    "exercise_name": "Squat",
                    "body_part": "legs",
                    "score": 0.95,
                    "reason": "Progressive overload",
                    "created_at": "2026-09-15T10:00:00"
                },
                {
                    "user_id": 42,
                    "exercise_id": 11,
                    "exercise_name": "Bench Press",
                    "body_part": "chest",
                    "score": 0.87,
                    "reason": "Balance push/pull",
                    "created_at": "2026-09-15T10:00:00"
                }
            ]
            """;
            GivenResponse(HttpStatusCode.OK, jsonBody);

            var result = (await _sut.GetRecommendationsAsync(42)).ToList();

            Assert.Equal(2, result.Count);
            Assert.Equal("Squat", result[0].ExerciseName);
            Assert.Equal("chest", result[1].BodyPart);
        }

        // 401 Unauthorized → PythonApiException (inte silent fail)
        [Fact]
        public async Task GetFatigueScoreAsync_WhenUnauthorized_ThrowsPythonApiException()
        {
            GivenResponse(HttpStatusCode.Unauthorized);

            var ex = await Assert.ThrowsAsync<PythonApiException>(() =>
                _sut.GetFatigueScoreAsync(42, DateTime.Today));

            Assert.Equal(HttpStatusCode.Unauthorized, ex.StatusCode);
            Assert.Contains("fatigue-scores", ex.RequestUri);
        }

        // 500 Internal Server Error → PythonApiException
        [Fact]
        public async Task GetRecommendationsAsync_WhenServerError_ThrowsPythonApiException()
        {
            GivenResponse(HttpStatusCode.InternalServerError);

            var ex = await Assert.ThrowsAsync<PythonApiException>(() =>
                _sut.GetRecommendationsAsync(42));

            Assert.Equal(HttpStatusCode.InternalServerError, ex.StatusCode);
        }

        // Invalid JSON → PythonApiException (deserialiseringsfel wrappas)
        [Fact]
        public async Task GetFatigueScoreAsync_WhenInvalidJson_ThrowsPythonApiException()
        {
            GivenResponse(HttpStatusCode.OK, "not valid json {[}");

            var ex = await Assert.ThrowsAsync<PythonApiException>(() =>
                _sut.GetFatigueScoreAsync(42, DateTime.Today));

            Assert.NotNull(ex.InnerException);
        }

        // Verifierar att X-API-Key skickas med i utgående requests
        [Fact]
        public async Task GetFatigueScoreAsync_SendsApiKeyInHeader()
        {
            GivenResponse(HttpStatusCode.NotFound);
            HttpRequestMessage? capturedRequest = null;

            _handlerMock.Protected()
                .Setup<Task<HttpResponseMessage>>(
                    "SendAsync",
                    ItExpr.IsAny<HttpRequestMessage>(),
                    ItExpr.IsAny<CancellationToken>())
                .Callback<HttpRequestMessage, CancellationToken>((req, _) => capturedRequest = req)
                .ReturnsAsync(new HttpResponseMessage(HttpStatusCode.NotFound));

            await _sut.GetFatigueScoreAsync(42, DateTime.Today);

            Assert.NotNull(capturedRequest);
            Assert.True(capturedRequest.Headers.Contains("X-API-Key"));
            Assert.Equal("test-api-key", capturedRequest.Headers.GetValues("X-API-Key").First());
        }

        // Coach messages: endpoint utan user_id (kunskapsbas)
        [Fact]
        public async Task GetCoachMessagesAsync_WithoutCategory_HitsBaseEndpoint()
        {
            var jsonBody = """
            [
                {
                    "category": "motivation",
                    "trigger_type": "workout_completed",
                    "message_sv": "Snyggt jobbat!",
                    "message_en": "Well done!",
                    "tone": "encouraging",
                    "language": "sv",
                    "priority": 1
                }
            ]
            """;
            GivenResponse(HttpStatusCode.OK, jsonBody);
            HttpRequestMessage? capturedRequest = null;

            _handlerMock.Protected()
                .Setup<Task<HttpResponseMessage>>(
                    "SendAsync",
                    ItExpr.IsAny<HttpRequestMessage>(),
                    ItExpr.IsAny<CancellationToken>())
                .Callback<HttpRequestMessage, CancellationToken>((req, _) => capturedRequest = req)
                .ReturnsAsync(new HttpResponseMessage(HttpStatusCode.OK)
                {
                    Content = new StringContent(jsonBody, Encoding.UTF8, "application/json")
                });

            var result = (await _sut.GetCoachMessagesAsync()).ToList();

            Assert.Single(result);
            Assert.Equal("Snyggt jobbat!", result[0].MessageSv);
            Assert.NotNull(capturedRequest);
            Assert.DoesNotContain("?", capturedRequest.RequestUri!.ToString());
        }

        // Coach messages med category-filter → URL innehåller escaped parameter
        [Fact]
        public async Task GetCoachMessagesAsync_WithCategory_EscapesParameter()
        {
            GivenResponse(HttpStatusCode.OK, "[]");
            HttpRequestMessage? capturedRequest = null;

            _handlerMock.Protected()
                .Setup<Task<HttpResponseMessage>>(
                    "SendAsync",
                    ItExpr.IsAny<HttpRequestMessage>(),
                    ItExpr.IsAny<CancellationToken>())
                .Callback<HttpRequestMessage, CancellationToken>((req, _) => capturedRequest = req)
                .ReturnsAsync(new HttpResponseMessage(HttpStatusCode.OK)
                {
                    Content = new StringContent("[]", Encoding.UTF8, "application/json")
                });

            await _sut.GetCoachMessagesAsync("recovery tips");

            Assert.NotNull(capturedRequest);
            Assert.Contains("category=recovery%20tips", capturedRequest.RequestUri!.AbsoluteUri);
        }

        // Model predictions: 9-fälts DTO deserialiseras korrekt
        [Fact]
        public async Task GetModelPredictionAsync_WhenOkResponse_DeserializesAllFields()
        {
            var jsonBody = """
            {
                "user_id": 42,
                "date": "2026-09-15",
                "injury_risk_score": 0.15,
                "dropout_risk_score": 0.08,
                "overtraining_risk_score": 0.22,
                "recommended_intensity": "medium",
                "recommended_volume_multiplier": 0.85,
                "primary_recommendation": "Consider deload week",
                "confidence_score": 0.92
            }
            """;
            GivenResponse(HttpStatusCode.OK, jsonBody);

            var result = await _sut.GetModelPredictionAsync(42, new DateTime(2026, 9, 15));

            Assert.NotNull(result);
            Assert.Equal(0.15m, result.InjuryRiskScore);
            Assert.Equal("medium", result.RecommendedIntensity);
            Assert.Equal(0.85m, result.RecommendedVolumeMultiplier);
            Assert.Equal("Consider deload week", result.PrimaryRecommendation);
        }
    }
}