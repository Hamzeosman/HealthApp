using Mintakt.API.Models;

namespace HealthApp.Tests.Builders
{
    /// <summary>Fluent builder for User test entities — keeps tests DRY.</summary>
    public class UserBuilder
    {
        private readonly User _user = new()
        {
            Id = 1,
            Name = "test-user",
            Email = "test-user@example.com",
            PasswordHash = "hash",
            CreatedAt = new DateTime(2025, 1, 1, 0, 0, 0, DateTimeKind.Utc)
        };

        public UserBuilder WithId(int id) { _user.Id = id; return this; }
        public UserBuilder WithName(string name) { _user.Name = name; return this; }
        public UserBuilder WithEmail(string email) { _user.Email = email; return this; }
        public UserBuilder WithPasswordHash(string hash) { _user.PasswordHash = hash; return this; }
        public UserBuilder WithAge(int age) { _user.Age = age; return this; }
        public UserBuilder WithWeight(decimal kg) { _user.WeightKg = kg; return this; }
        public UserBuilder WithHeight(decimal cm) { _user.HeightCm = cm; return this; }
        public UserBuilder WithFitnessLevel(string level) { _user.FitnessLevel = level; return this; }
        public UserBuilder WithGoal(string goal) { _user.Goal = goal; return this; }

        public User Build() => _user;
    }
}
