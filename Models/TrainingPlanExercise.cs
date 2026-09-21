using System.ComponentModel.DataAnnotations.Schema;

namespace Mintakt.API.Models
{
    [Table("training_plan_exercises")]
    public class TrainingPlanExercise
    {
        [Column("id")]
        public int Id { get; set; }

        [Column("plan_day_id")]
        public int? PlanDayId { get; set; }

        [Column("exercise_id")]
        public int? ExerciseId { get; set; }

        [Column("sets")]
        public int? Sets { get; set; }

        [Column("reps")]
        public int? Reps { get; set; }

        [Column("rest_seconds")]
        public int? RestSeconds { get; set; }

        [Column("intensity")]
        public string? Intensity { get; set; }

        [Column("notes")]
        public string? Notes { get; set; }

        [Column("order_index")]
        public int? OrderIndex { get; set; }
    }
}