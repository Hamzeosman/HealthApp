namespace Mintakt.API.DTOs
{
    // DTO för fatigue_scores-endpoint från Python API.
    // Alla properties är nullable eftersom Python-sidan returnerar null
    // för fält som inte är beräknade än (t.ex. deload_recommended första veckan).
    public class FatigueScoreDto
    {
        public int? UserId { get; set; }
        public DateTime? Date { get; set; }
        public decimal? Acwr { get; set; }
        public string? TrainingZone { get; set; }
        public decimal? ReadinessScore { get; set; }
        public decimal? RecoveryScore { get; set; }
        public decimal? FatigueScore { get; set; }
        public bool? DeloadRecommended { get; set; }
    }
}