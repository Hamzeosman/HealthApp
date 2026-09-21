using System.ComponentModel.DataAnnotations.Schema;

namespace Mintakt.API.Models
{
    [Table("biometrics")]
    public class Biometric
    {
        [Column("id")]
        public int Id { get; set; }

        [Column("user_id")]
        public int? UserId { get; set; }

        [Column("date")]
        public DateTime? Date { get; set; }

        [Column("steps")]
        public int? Steps { get; set; }

        [Column("heart_rate_resting")]
        public int? HeartRateResting { get; set; }

        [Column("heart_rate_avg")]
        public int? HeartRateAvg { get; set; }

        [Column("heart_rate_max")]
        public int? HeartRateMax { get; set; }

        [Column("vo2_max")]
        public decimal? Vo2Max { get; set; }

        [Column("calories_burned")]
        public int? CaloriesBurned { get; set; }

        [Column("active_minutes")]
        public int? ActiveMinutes { get; set; }

        [Column("distance_km")]
        public decimal? DistanceKm { get; set; }
    }
}