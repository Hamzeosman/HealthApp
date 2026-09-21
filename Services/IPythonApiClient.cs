using Mintakt.API.DTOs;

namespace Mintakt.API.Services
{
    // Kontrakt för Python API-anrop (Iteration 3 av Issue #32).
    //
    // Endpoints använder healthapp_ai_service-rollen via X-API-Key,
    // bekräftat av Abdulrahman i PR #44-review.
    //
    // 404-svar konverteras till null (single-item) eller tom lista (collections)
    // — Python-sidan returnerar 404 när data inte finns för en användare, vilket
    // är förväntat läge (t.ex. ny user utan fatigue-scores än).
    //
    // Alla andra fel (401, 403, 500, timeout) kastar PythonApiException.
    public interface IPythonApiClient
    {
        Task<FatigueScoreDto?> GetFatigueScoreAsync(int userId, DateTime date, CancellationToken cancellationToken = default);

        Task<IEnumerable<RecommendationDto>> GetRecommendationsAsync(int userId, CancellationToken cancellationToken = default);

        Task<ModelPredictionDto?> GetModelPredictionAsync(int userId, DateTime date, CancellationToken cancellationToken = default);

        Task<IEnumerable<AiInsightDto>> GetAiInsightsAsync(int userId, CancellationToken cancellationToken = default);

        Task<IEnumerable<CoachMessageDto>> GetCoachMessagesAsync(string? category = null, CancellationToken cancellationToken = default);
    }
}