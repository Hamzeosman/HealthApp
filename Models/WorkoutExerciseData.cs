using System.ComponentModel.DataAnnotations.Schema;

namespace HealthApp.API.Models
{
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
    }
}