using System.ComponentModel.DataAnnotations.Schema;

namespace Mintakt.API.Models
{
    [Table("training_plans")]
    public class TrainingPlan
    {
        [Column("id")]
        public int Id { get; set; }

        [Column("name")]
        public string? Name { get; set; }

        [Column("goal")]
        public string? Goal { get; set; }

        [Column("difficulty")]
        public string? Difficulty { get; set; }

        [Column("duration_weeks")]
        public int? DurationWeeks { get; set; }

        [Column("days_per_week")]
        public int? DaysPerWeek { get; set; }

        [Column("description")]
        public string? Description { get; set; }

        [Column("target_audience")]
        public string? TargetAudience { get; set; }

        [Column("created_at")]
        public DateTime? CreatedAt { get; set; }
    }
}