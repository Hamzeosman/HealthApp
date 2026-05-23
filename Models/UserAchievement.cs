using System.ComponentModel.DataAnnotations.Schema;

namespace HealthApp.API.Models
{
    [Table("user_achievements")]
    public class UserAchievement
    {
        [Column("id")]
        public int Id { get; set; }

        [Column("user_id")]
        public int? UserId { get; set; }

        [Column("achievement_id")]
        public int? AchievementId { get; set; }

        [Column("achieved_at")]
        public DateTime? AchievedAt { get; set; }
    }
}