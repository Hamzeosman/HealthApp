namespace HealthApp.API.Models
{
    public class BodyPart
    {
        public int Id { get; set; }
        public string Name { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;

        public ICollection<Exercise> Exercises { get; set; } = new List<Exercise>();
        public ICollection<MuscleGroup> MuscleGroups { get; set; } = new List<MuscleGroup>();
    }
}