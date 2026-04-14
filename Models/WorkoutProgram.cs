namespace HealthApp.API.Models
{
    public class WorkoutProgram
    {
        public int Id { get; set; }
        public string Name { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public string Difficulty { get; set; } = string.Empty;
        public int DurationWeeks { get; set; }
        public int DaysPerWeek { get; set; }
        public string Goal { get; set; } = string.Empty;

        public ICollection<WorkoutTemplate> WorkoutTemplates { get; set; } = new List<WorkoutTemplate>();
    }
}