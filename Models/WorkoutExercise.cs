namespace Mintakt.API.Models
{
    public class WorkoutExercise
    {
        public int Id { get; set; }
        public int SessionId { get; set; }
        public int ExerciseId { get; set; }
        public int Sets { get; set; }
        public int Reps { get; set; }
        public decimal? WeightKg { get; set; }
        public int? DurationSeconds { get; set; }
        public int? RestSeconds { get; set; }
        public int? Rpe { get; set; }
        public string Notes { get; set; } = string.Empty;

        public WorkoutSession? WorkoutSession { get; set; }
        public Exercise? Exercise { get; set; }
    }
}