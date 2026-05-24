namespace HealthApp.API.DTOs
{
    public class UpdateProfileDto
    {
        public int? Age { get; set; }
        public decimal? WeightKg { get; set; }
        public decimal? HeightCm { get; set; }
        public string FitnessLevel { get; set; } = string.Empty;
        public string Goal { get; set; } = string.Empty;
    }
}
