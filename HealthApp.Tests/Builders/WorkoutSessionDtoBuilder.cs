using Mintakt.API.DTOs;

namespace HealthApp.Tests.Builders
{
    /// <summary>Fluent builder for WorkoutSessionDto test objects — keeps tests DRY.</summary>
    public class WorkoutSessionDtoBuilder
    {
        private readonly WorkoutSessionDto _dto = new()
        {
            Id = 1,
            UserId = 1,
            Date = new DateTime(2026, 1, 1, 0, 0, 0, DateTimeKind.Utc),
            Mood = string.Empty,
            Notes = string.Empty
        };

        public WorkoutSessionDtoBuilder WithId(int id) { _dto.Id = id; return this; }
        public WorkoutSessionDtoBuilder WithUserId(int userId) { _dto.UserId = userId; return this; }
        public WorkoutSessionDtoBuilder WithDate(DateTime date) { _dto.Date = date; return this; }
        public WorkoutSessionDtoBuilder WithNotes(string notes) { _dto.Notes = notes; return this; }

        public WorkoutSessionDto Build() => _dto;
    }
}
