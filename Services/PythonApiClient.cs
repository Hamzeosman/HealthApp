using System.Net;
using System.Text.Json;
using HealthApp.API.DTOs;

namespace HealthApp.API.Services
{
    // Typed HttpClient-implementation för Python API.
    //
    // Konstrueras via AddHttpClient<> i Program.cs, vilket automatiskt hanterar:
    //   - HttpClient lifecycle (undviker socket-exhaustion)
    //   - BaseAddress-injektion från PythonApiOptions
    //   - X-API-Key-header (healthapp_ai_service-rollen)
    //   - Timeout från konfiguration
    //
    // Deserialisering använder snake_case-konvention eftersom Python-sidan
    // returnerar snake_case JSON (t.ex. "readiness_score" → ReadinessScore).
    public class PythonApiClient : IPythonApiClient
    {
        private readonly HttpClient _httpClient;

        private static readonly JsonSerializerOptions JsonOptions = new()
        {
            PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower,
            PropertyNameCaseInsensitive = true
        };

        public PythonApiClient(HttpClient httpClient)
        {
            _httpClient = httpClient;
        }

        public Task<FatigueScoreDto?> GetFatigueScoreAsync(int userId, DateTime date, CancellationToken cancellationToken = default)
        {
            var uri = $"api/ai/fatigue-scores?user_id={userId}&date={date:yyyy-MM-dd}";
            return GetSingleAsync<FatigueScoreDto>(uri, cancellationToken);
        }

        public Task<IEnumerable<RecommendationDto>> GetRecommendationsAsync(int userId, CancellationToken cancellationToken = default)
        {
            var uri = $"api/recommendations?user_id={userId}";
            return GetListAsync<RecommendationDto>(uri, cancellationToken);
        }

        public Task<ModelPredictionDto?> GetModelPredictionAsync(int userId, DateTime date, CancellationToken cancellationToken = default)
        {
            var uri = $"api/ai/model-predictions?user_id={userId}&date={date:yyyy-MM-dd}";
            return GetSingleAsync<ModelPredictionDto>(uri, cancellationToken);
        }

        public Task<IEnumerable<AiInsightDto>> GetAiInsightsAsync(int userId, CancellationToken cancellationToken = default)
        {
            var uri = $"api/ai/insights?user_id={userId}";
            return GetListAsync<AiInsightDto>(uri, cancellationToken);
        }

        public Task<IEnumerable<CoachMessageDto>> GetCoachMessagesAsync(string? category = null, CancellationToken cancellationToken = default)
        {
            var uri = category is null
                ? "api/ai/coach-messages"
                : $"api/ai/coach-messages?category={Uri.EscapeDataString(category)}";
            return GetListAsync<CoachMessageDto>(uri, cancellationToken);
        }

        // Hämtar en enskild resurs. 404 → null (t.ex. ny user utan fatigue-score än).
        // Andra fel kastar PythonApiException.
        private async Task<T?> GetSingleAsync<T>(string uri, CancellationToken cancellationToken)
            where T : class
        {
            HttpResponseMessage response;
            try
            {
                response = await _httpClient.GetAsync(uri, cancellationToken);
            }
            catch (TaskCanceledException ex) when (!cancellationToken.IsCancellationRequested)
            {
                throw new PythonApiException("Python API request timed out.", HttpStatusCode.RequestTimeout, uri, ex);
            }
            catch (HttpRequestException ex)
            {
                throw new PythonApiException("Python API request failed.", HttpStatusCode.ServiceUnavailable, uri, ex);
            }

            if (response.StatusCode == HttpStatusCode.NotFound)
            {
                return null;
            }

            if (!response.IsSuccessStatusCode)
            {
                throw new PythonApiException(
                    $"Python API returned {(int)response.StatusCode} {response.ReasonPhrase} for {uri}.",
                    response.StatusCode,
                    uri);
            }

            try
            {
                return await response.Content.ReadFromJsonAsync<T>(JsonOptions, cancellationToken);
            }
            catch (JsonException ex)
            {
                throw new PythonApiException(
                    $"Failed to deserialize Python API response for {uri}.",
                    response.StatusCode,
                    uri,
                    ex);
            }
        }

        // Hämtar en lista. 404 → tom lista (Python-sidan använder 404 när ingen
        // data finns för användaren, vilket är förväntat läge, inte fel).
        // Andra fel kastar PythonApiException.
        private async Task<IEnumerable<T>> GetListAsync<T>(string uri, CancellationToken cancellationToken)
        {
            HttpResponseMessage response;
            try
            {
                response = await _httpClient.GetAsync(uri, cancellationToken);
            }
            catch (TaskCanceledException ex) when (!cancellationToken.IsCancellationRequested)
            {
                throw new PythonApiException("Python API request timed out.", HttpStatusCode.RequestTimeout, uri, ex);
            }
            catch (HttpRequestException ex)
            {
                throw new PythonApiException("Python API request failed.", HttpStatusCode.ServiceUnavailable, uri, ex);
            }

            if (response.StatusCode == HttpStatusCode.NotFound)
            {
                return Enumerable.Empty<T>();
            }

            if (!response.IsSuccessStatusCode)
            {
                throw new PythonApiException(
                    $"Python API returned {(int)response.StatusCode} {response.ReasonPhrase} for {uri}.",
                    response.StatusCode,
                    uri);
            }

            try
            {
                var result = await response.Content.ReadFromJsonAsync<IEnumerable<T>>(JsonOptions, cancellationToken);
                return result ?? Enumerable.Empty<T>();
            }
            catch (JsonException ex)
            {
                throw new PythonApiException(
                    $"Failed to deserialize Python API response for {uri}.",
                    response.StatusCode,
                    uri,
                    ex);
            }
        }
    }
}