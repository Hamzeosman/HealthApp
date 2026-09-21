namespace Mintakt.API.Models
{
    public class Recommendation
    {
        public int Id { get; set; }
        public int UserId { get; set; }
        public int ExerciseId { get; set; }
        public string Reason { get; set; } = string.Empty;
        public decimal Score { get; set; }
        public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
        public bool IsSeen { get; set; } = false;

        public User? User { get; set; }
        public Exercise? Exercise { get; set; }
    }
}