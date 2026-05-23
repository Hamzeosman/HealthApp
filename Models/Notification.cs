using System.ComponentModel.DataAnnotations.Schema;

namespace HealthApp.API.Models
{
    [Table("notifications")]
    public class Notification
    {
        [Column("id")]
        public int Id { get; set; }

        [Column("user_id")]
        public int? UserId { get; set; }

        [Column("title")]
        public string? Title { get; set; }

        [Column("message")]
        public string? Message { get; set; }

        [Column("notification_type")]
        public string? NotificationType { get; set; }

        [Column("is_read")]
        public bool IsRead { get; set; }

        [Column("created_at")]
        public DateTime? CreatedAt { get; set; }
    }
}