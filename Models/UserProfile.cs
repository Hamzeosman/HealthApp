using System.ComponentModel.DataAnnotations.Schema;

namespace HealthApp.API.Models
{
    [Table("users")]
    public class UserProfile
    {
        [Column("id")]
        public int Id { get; set; }

        [Column("name")]
        public string? Name { get; set; }

        [Column("email")]
        public string? Email { get; set; }

        [Column("age")]
        public int? Age { get; set; }

        [Column("weight_kg")]
        public decimal? WeightKg { get; set; }

        [Column("height_cm")]
        public decimal? HeightCm { get; set; }

        [Column("fitness_level")]
        public string? FitnessLevel { get; set; }

        [Column("fitness_goal")]
        public string? FitnessGoal { get; set; }

        [Column("experience_level")]
        public string? ExperienceLevel { get; set; }
    }
}