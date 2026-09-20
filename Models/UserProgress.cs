namespace Mintakt.API.Models
{
    public class UserProgress
    {
        public int Id { get; set; }
        public int UserId { get; set; }
        public DateTime Date { get; set; }
        public decimal? WeightKg { get; set; }
        public decimal? BodyFatPercentage { get; set; }
        public decimal? ChestCm { get; set; }
        public decimal? WaistCm { get; set; }
        public decimal? HipsCm { get; set; }
        public decimal? BicepCm { get; set; }
        public decimal? ThighCm { get; set; }

        public User? User { get; set; }
    }
}