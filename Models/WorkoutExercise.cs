namespace HealthApp.API.Models
{
    public class WorkoutExercise
    {
        public int Id { get; set; }
        public int WorkoutSessionId { get; set; }
        public int ExerciseId { get; set; }
        public int Sets { get; set; }
        public int Reps { get; set; }
        public double WeightKg { get; set; }
    }
}