namespace HealthApp.API.Models
{
    public class User
    {
        public int Id { get; set; }
        public string Name { get; set; } = string.Empty;
        public string Email { get; set; } = string.Empty;
        public string PasswordHash { get; set; } = string.Empty;
        public int? Age { get; set; }
        public decimal? WeightKg { get; set; }
        public decimal? HeightCm { get; set; }
        public string FitnessLevel { get; set; } = string.Empty;
        public string Goal { get; set; } = string.Empty;
        public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

        public ICollection<WorkoutSession> WorkoutSessions { get; set; } = new List<WorkoutSession>();
        public ICollection<UserProgress> UserProgressList { get; set; } = new List<UserProgress>();
        public ICollection<PersonalRecord> PersonalRecords { get; set; } = new List<PersonalRecord>();
        public ICollection<Recommendation> Recommendations { get; set; } = new List<Recommendation>();
    }
}