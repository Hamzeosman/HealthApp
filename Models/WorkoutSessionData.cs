using System.ComponentModel.DataAnnotations.Schema;

namespace HealthApp.API.Models
{
    [Table("workout_sessions")]
    public class WorkoutSessionData
    {
        [Column("id")]
        public int Id { get; set; }

        [Column("user_id")]
        public int? UserId { get; set; }

        [Column("template_id")]
        public int? TemplateId { get; set; }

        [Column("date")]
        public DateTime? Date { get; set; }

        [Column("duration_minutes")]
        public int? DurationMinutes { get; set; }

        [Column("total_calories")]
        public int? TotalCalories { get; set; }

        [Column("mood")]
        public string? Mood { get; set; }

        [Column("notes")]
        public string? Notes { get; set; }

        [Column("created_at")]
        public DateTime? CreatedAt { get; set; }
    }
}