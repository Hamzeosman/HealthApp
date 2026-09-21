using System.ComponentModel.DataAnnotations.Schema;

namespace Mintakt.API.Models
{
    /// <summary>
    /// Personal records (PRs) för en användare per övning mot personal_records-tabellen
    /// i HealthAppDataDb. Refererar UserData och ExerciseData via UserId/ExerciseId.
    /// Följer "Data"-suffix-mönstret.
    /// </summary>
    [Table("personal_records")]
    public class PersonalRecordData
    {
        [Column("id")]
        public int Id { get; set; }

        [Column("user_id")]
        public int? UserId { get; set; }

        [Column("exercise_id")]
        public int? ExerciseId { get; set; }

        [Column("weight_kg")]
        public decimal? WeightKg { get; set; }

        [Column("reps")]
        public int? Reps { get; set; }

        [Column("date")]
        public DateTime? Date { get; set; }

        [Column("notes")]
        public string? Notes { get; set; }

        // Navigation properties (DataDbContext-world only)
        [ForeignKey(nameof(UserId))]
        public UserData? User { get; set; }

        [ForeignKey(nameof(ExerciseId))]
        public ExerciseData? Exercise { get; set; }
    }
}