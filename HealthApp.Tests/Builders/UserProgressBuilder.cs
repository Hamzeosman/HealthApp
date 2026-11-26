using Mintakt.API.Models;

namespace HealthApp.Tests.Builders
{
    /// <summary>Fluent builder for UserProgress test entities — keeps tests DRY.</summary>
    public class UserProgressBuilder
    {
        private readonly UserProgress _progress = new()
        {
            Id = 1,
            UserId = 42,
            Date = new DateTime(2026, 1, 1, 0, 0, 0, DateTimeKind.Utc),
            WeightKg = 75m
        };

        public UserProgressBuilder WithId(int id) { _progress.Id = id; return this; }
        public UserProgressBuilder WithUserId(int userId) { _progress.UserId = userId; return this; }
        public UserProgressBuilder WithDate(DateTime date) { _progress.Date = date; return this; }
        public UserProgressBuilder WithWeight(decimal weightKg) { _progress.WeightKg = weightKg; return this; }
        public UserProgressBuilder WithBodyFat(decimal percentage) { _progress.BodyFatPercentage = percentage; return this; }
        public UserProgressBuilder WithChest(decimal cm) { _progress.ChestCm = cm; return this; }
        public UserProgressBuilder WithWaist(decimal cm) { _progress.WaistCm = cm; return this; }
        public UserProgressBuilder WithHips(decimal cm) { _progress.HipsCm = cm; return this; }
        public UserProgressBuilder WithBicep(decimal cm) { _progress.BicepCm = cm; return this; }
        public UserProgressBuilder WithThigh(decimal cm) { _progress.ThighCm = cm; return this; }

        public UserProgress Build() => _progress;
    }
}