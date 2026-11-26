using Mintakt.API.Models;

namespace HealthApp.Tests.Builders
{
    /// <summary>Fluent builder for Recommendation test entities — keeps tests DRY.</summary>
    public class RecommendationBuilder
    {
        private readonly Recommendation _recommendation = new()
        {
            Id = 1,
            UserId = 42,
            ExerciseId = 10,
            Reason = "Based on your recent workouts",
            Score = 0.85m,
            CreatedAt = new DateTime(2026, 1, 1, 0, 0, 0, DateTimeKind.Utc),
            IsSeen = false
        };

        public RecommendationBuilder WithId(int id) { _recommendation.Id = id; return this; }
        public RecommendationBuilder WithUserId(int userId) { _recommendation.UserId = userId; return this; }
        public RecommendationBuilder WithExerciseId(int exerciseId) { _recommendation.ExerciseId = exerciseId; return this; }
        public RecommendationBuilder WithReason(string reason) { _recommendation.Reason = reason; return this; }
        public RecommendationBuilder WithScore(decimal score) { _recommendation.Score = score; return this; }
        public RecommendationBuilder WithCreatedAt(DateTime createdAt) { _recommendation.CreatedAt = createdAt; return this; }
        public RecommendationBuilder WithSeen(bool seen) { _recommendation.IsSeen = seen; return this; }

        public Recommendation Build() => _recommendation;
    }
}