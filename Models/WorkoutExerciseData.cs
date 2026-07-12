using System.ComponentModel.DataAnnotations.Schema;

namespace HealthApp.API.Models
{
    /// <summary>
    /// Övningar loggade i ett träningspass mot workout_exercises-tabellen
    /// i HealthAppDataDb. Refererar WorkoutSessionData och ExerciseData
    /// via SessionId/ExerciseId. Följer "Data"-suffix-mönstret.
    ///
    /// CHECK constraints på Sets/Reps/WeightKg/Rpe konfigureras i
    /// DataDbContext.OnModelCreating() och matchar Postgres chk_we_*.
    /// </summary>
    [Table("workout_exercises")]
    public class WorkoutExerciseData
    {
        [Column("id")]
        public int Id { get; set; }

        [Column("session_id")]
        public int? SessionId { get; set; }

        [Column("exercise_id")]
        public int? ExerciseId { get; set; }

        [Column("sets")]
        public int? Sets { get; set; }

        [Column("reps")]
        public int? Reps { get; set; }

        [Column("weight_kg")]
        public decimal? WeightKg { get; set; }

        [Column("duration_seconds")]
        public int? DurationSeconds { get; set; }

        [Column("rest_seconds")]
        public int? RestSeconds { get; set; }

        [Column("rpe")]
        public int? Rpe { get; set; }

        [Column("notes")]
        public string? Notes { get; set; }

        // Navigation properties (DataDbContext-world only)
        [ForeignKey(nameof(SessionId))]
        public WorkoutSessionData? Session { get; set; }

        [ForeignKey(nameof(ExerciseId))]
        public ExerciseData? Exercise { get; set; }
    }
}