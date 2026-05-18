using System.ComponentModel.DataAnnotations.Schema;

namespace HealthApp.API.Models
{
    [Table("user_streaks")]
    public class UserStreak
    {
        [Column("id")]
        public int Id { get; set; }

        [Column("user_id")]
        public int? UserId { get; set; }

        [Column("current_streak")]
        public int CurrentStreak { get; set; }

        [Column("longest_streak")]
        public int LongestStreak { get; set; }

        [Column("last_workout_date")]
        public DateTime? LastWorkoutDate { get; set; }

        [Column("total_workouts")]
        public int TotalWorkouts { get; set; }
    }
}