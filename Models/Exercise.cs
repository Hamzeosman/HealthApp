namespace HealthApp.API.Models
{
    public class Exercise
    {
        public int Id { get; set; }
        public string Name { get; set; } = string.Empty;
        public int? BodyPartId { get; set; }
        public int? MuscleGroupId { get; set; }
        public int? EquipmentId { get; set; }
        public string Difficulty { get; set; } = string.Empty;
        public string ExerciseType { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public string Instructions { get; set; } = string.Empty;
        public string Tips { get; set; } = string.Empty;
        public decimal? CaloriesPerMinute { get; set; }

        public BodyPart? BodyPart { get; set; }
        public MuscleGroup? MuscleGroup { get; set; }
        public Equipment? Equipment { get; set; }
    }
}