using System.ComponentModel.DataAnnotations;

namespace Mintakt.API.DTOs
{
    public class CreateWorkoutSessionDto
    {
        public int UserId { get; set; }
        public int? TemplateId { get; set; }
        public DateTime Date { get; set; }
        public DateTime? StartTime { get; set; }
        public DateTime? EndTime { get; set; }
        public int? DurationMinutes { get; set; }
        public int? TotalCalories { get; set; }

        // Matchar CHECK-constrainten på workout_sessions.mood. Humör är valfritt.
        [RegularExpression("^(bra|okej|trött|stark)$", ErrorMessage = "Mood måste vara bra, okej, trött eller stark.")]
        public string? Mood { get; set; }

        public string? Notes { get; set; }
        public List<CreateWorkoutExerciseDto> WorkoutExercises { get; set; } = new();
    }

    // Intervallen matchar CHECK-constraints på workout_exercises.
    public class CreateWorkoutExerciseDto
    {
        [Range(1, int.MaxValue)]
        public int ExerciseId { get; set; }

        [Range(1, 20)]
        public int Sets { get; set; }

        [Range(1, 100)]
        public int Reps { get; set; }

        [Range(typeof(decimal), "0", "500")]
        public decimal? WeightKg { get; set; }

        public int? DurationSeconds { get; set; }
        public int? RestSeconds { get; set; }

        [Range(1, 10)]
        public int? Rpe { get; set; }

        public string? Notes { get; set; }
    }
}
