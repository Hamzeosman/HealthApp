namespace HealthApp.API.DTOs
{
    // DTO för model_predictions-endpoint från Python API.
    // ML-modellens utdata för en given användare och datum: risk-scores samt
    // rekommenderad intensitet/volym baserat på träningshistorik.
    public class ModelPredictionDto
    {
        public int? UserId { get; set; }
        public DateTime? Date { get; set; }
        public decimal? InjuryRiskScore { get; set; }
        public decimal? DropoutRiskScore { get; set; }
        public decimal? OvertrainingRiskScore { get; set; }
        public string? RecommendedIntensity { get; set; }
        public decimal? RecommendedVolumeMultiplier { get; set; }
        public string? PrimaryRecommendation { get; set; }
        public decimal? ConfidenceScore { get; set; }
    }
}