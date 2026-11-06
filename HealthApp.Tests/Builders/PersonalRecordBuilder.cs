using Mintakt.API.Models;

namespace HealthApp.Tests.Builders
{
    /// <summary>Fluent builder for PersonalRecord test entities — keeps tests DRY.</summary>
    public class PersonalRecordBuilder
    {
        private readonly PersonalRecord _record = new()
        {
            Id = 1,
            UserId = 1,
            ExerciseId = 1,
            WeightKg = 100m,
            Reps = 5,
            Date = new DateTime(2026, 1, 1, 0, 0, 0, DateTimeKind.Utc),
            Notes = string.Empty
        };

        public PersonalRecordBuilder WithId(int id) { _record.Id = id; return this; }
        public PersonalRecordBuilder WithUserId(int userId) { _record.UserId = userId; return this; }
        public PersonalRecordBuilder WithExerciseId(int exerciseId) { _record.ExerciseId = exerciseId; return this; }
        public PersonalRecordBuilder WithWeight(decimal kg) { _record.WeightKg = kg; return this; }
        public PersonalRecordBuilder WithReps(int reps) { _record.Reps = reps; return this; }
        public PersonalRecordBuilder WithDate(DateTime date) { _record.Date = date; return this; }
        public PersonalRecordBuilder WithNotes(string notes) { _record.Notes = notes; return this; }

        public PersonalRecord Build() => _record;
    }
}