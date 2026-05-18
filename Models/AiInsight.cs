using System.ComponentModel.DataAnnotations.Schema;

namespace HealthApp.API.Models
{
    [Table("ai_insights")]
    public class AiInsight
    {
        [Column("id")]
        public int Id { get; set; }

        [Column("user_id")]
        public int? UserId { get; set; }

        [Column("insight_type")]
        public string? InsightType { get; set; }

        [Column("title")]
        public string? Title { get; set; }

        [Column("content")]
        public string? Content { get; set; }

        [Column("is_read")]
        public bool IsRead { get; set; }

        [Column("created_at")]
        public DateTime? CreatedAt { get; set; }
    }
}