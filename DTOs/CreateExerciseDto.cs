namespace Mintakt.API.DTOs
{
    public class CreateExerciseDto
    {
        public string Name { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public int? BodyPartId { get; set; }
        public int? MuscleGroupId { get; set; }
        public int? EquipmentId { get; set; }
        public string Difficulty { get; set; } = string.Empty;
        public string ExerciseType { get; set; } = string.Empty;
        public string Instructions { get; set; } = string.Empty;
        public string Tips { get; set; } = string.Empty;
        public decimal? CaloriesPerMinute { get; set; }
    }
}