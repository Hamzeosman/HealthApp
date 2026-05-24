namespace HealthApp.API.DTOs
{
    public class UserProfileDto
    {
        public string Name { get; set; } = string.Empty;
        public string Email { get; set; } = string.Empty;
        public int? Age { get; set; }
        public decimal? WeightKg { get; set; }
        public decimal? HeightCm { get; set; }
        public string FitnessLevel { get; set; } = string.Empty;
        public string Goal { get; set; } = string.Empty;
        public DateTime CreatedAt { get; set; }
    }
}
