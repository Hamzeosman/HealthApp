namespace Mintakt.API.Models
{
    public class TemplateExercise
    {
        public int Id { get; set; }
        public int TemplateId { get; set; }
        public int ExerciseId { get; set; }
        public int Sets { get; set; }
        public int Reps { get; set; }
        public int RestSeconds { get; set; }
        public int OrderIndex { get; set; }

        public WorkoutTemplate? WorkoutTemplate { get; set; }
        public Exercise? Exercise { get; set; }
    }
}