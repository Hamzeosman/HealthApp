namespace HealthApp.API.DTOs
{
    public class ExerciseDto
    {
        public int Id { get; set; }
        public string Name { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public string Difficulty { get; set; } = string.Empty;
        public string ExerciseType { get; set; } = string.Empty;
        public string Instructions { get; set; } = string.Empty;
        public string Tips { get; set; } = string.Empty;
        public decimal? CaloriesPerMinute { get; set; }
        public string? BodyPartName { get; set; }
        public string? MuscleGroupName { get; set; }
        public string? EquipmentName { get; set; }
    }
}