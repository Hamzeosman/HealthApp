namespace Mintakt.API.Models
{
    public class WorkoutSession
    {
        public int Id { get; set; }
        public int UserId { get; set; }
        public int? TemplateId { get; set; }
        public DateTime Date { get; set; }
        public DateTime? StartTime { get; set; }
        public DateTime? EndTime { get; set; }
        public int? DurationMinutes { get; set; }
        public int? TotalCalories { get; set; }
        public string Mood { get; set; } = string.Empty;
        public string Notes { get; set; } = string.Empty;
        public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

        public User? User { get; set; }
        public WorkoutTemplate? WorkoutTemplate { get; set; }
        public ICollection<WorkoutExercise> WorkoutExercises { get; set; } = new List<WorkoutExercise>();
    }
}