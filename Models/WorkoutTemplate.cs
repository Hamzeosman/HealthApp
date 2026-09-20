namespace Mintakt.API.Models
{
    public class WorkoutTemplate
    {
        public int Id { get; set; }
        public int ProgramId { get; set; }
        public string Name { get; set; } = string.Empty;
        public string DayOfWeek { get; set; } = string.Empty;

        public WorkoutProgram? WorkoutProgram { get; set; }
        public ICollection<TemplateExercise> TemplateExercises { get; set; } = new List<TemplateExercise>();
    }
}