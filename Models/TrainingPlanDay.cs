using System.ComponentModel.DataAnnotations.Schema;

namespace Mintakt.API.Models
{
    [Table("training_plan_days")]
    public class TrainingPlanDay
    {
        [Column("id")]
        public int Id { get; set; }

        [Column("plan_id")]
        public int? PlanId { get; set; }

        [Column("week_number")]
        public int? WeekNumber { get; set; }

        [Column("day_number")]
        public int? DayNumber { get; set; }

        [Column("day_name")]
        public string? DayName { get; set; }

        [Column("focus")]
        public string? Focus { get; set; }

        [Column("rest_day")]
        public bool RestDay { get; set; }
    }
}