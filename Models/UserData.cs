using System.ComponentModel.DataAnnotations.Schema;

namespace HealthApp.API.Models
{
    /// <summary>
    /// Fitness-profil mot users-tabellen i HealthAppDataDb.
    /// INTE en auth-entitet — email och password_hash tillhör AppDbContext (Identity).
    /// Följer "Data"-suffix-mönstret (jfr ExerciseData, WorkoutSessionData).
    /// </summary>
    [Table("users")]
    public class UserData
    {
        [Column("id")]
        public int Id { get; set; }

        [Column("name")]
        public string? Name { get; set; }

        [Column("age")]
        public int? Age { get; set; }

        [Column("weight_kg")]
        public decimal? WeightKg { get; set; }

        [Column("height_cm")]
        public decimal? HeightCm { get; set; }

        [Column("fitness_level")]
        public string? FitnessLevel { get; set; }

        [Column("goal")]
        public string? Goal { get; set; }

        [Column("created_at")]
        public DateTime CreatedAt { get; set; }
    }
}