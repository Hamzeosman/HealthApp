namespace HealthApp.API.DTOs
{
    // DTO för ai_insights-endpoint från Python API.
    // Genererade insikter för en användare — träningsobservationer, mönster,
    // eller AI-formulerade tips baserat på historiken.
    //
    // Namnkollision: Models/AiInsight.cs är EF-entiteten mot ai_insights-tabellen.
    // Denna DTO är den HTTP-representation Python API returnerar — de speglar
    // samma data men kan divergera om Python-sidan ändrar sitt schema.
    public class AiInsightDto
    {
        public int? UserId { get; set; }
        public string? Title { get; set; }
        public string? Content { get; set; }
        public string? InsightType { get; set; }
        public DateTime? CreatedAt { get; set; }
    }
}