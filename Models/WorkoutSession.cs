namespace HealthApp.API.Models
{
    public class WorkoutSession
    {
        public int Id { get; set; }
        public int UserId { get; set; }
        public DateTime Date { get; set; }
        public string Notes { get; set; } = string.Empty;
        public List<WorkoutExercise> WorkoutExercises { get; set; } = new();
    }
}