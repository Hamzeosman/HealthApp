namespace HealthApp.API.DTOs
{
    // DTO för recommendations-endpoint från Python API.
    // ExerciseName och BodyPart är denormaliserade fält som Python-sidan
    // fyller i via JOIN mot exercises-tabellen — vi tar dem som de kommer.
    public class RecommendationDto
    {
        public int? UserId { get; set; }
        public int? ExerciseId { get; set; }
        public string? ExerciseName { get; set; }
        public string? BodyPart { get; set; }
        public decimal? Score { get; set; }
        public string? Reason { get; set; }
        public DateTime? CreatedAt { get; set; }
    }
}