namespace HealthApp.API.Models
{
    public class MuscleGroup
    {
        public int Id { get; set; }
        public string Name { get; set; } = string.Empty;
        public int BodyPartId { get; set; }

        public BodyPart? BodyPart { get; set; }
        public ICollection<Exercise> Exercises { get; set; } = new List<Exercise>();
    }
}