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
        public string Mood { get; set; } = string.Empty;
        public string Notes { get; set; } = string.Empty;
        public List<CreateWorkoutExerciseDto> WorkoutExercises { get; set; } = new();
    }

    public class CreateWorkoutExerciseDto
    {
        public int ExerciseId { get; set; }
        public int Sets { get; set; }
        public int Reps { get; set; }
        public decimal? WeightKg { get; set; }
        public int? DurationSeconds { get; set; }
        public int? RestSeconds { get; set; }
        public int? Rpe { get; set; }
        public string Notes { get; set; } = string.Empty;
    }
}