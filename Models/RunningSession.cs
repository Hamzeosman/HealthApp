using System.ComponentModel.DataAnnotations.Schema;

namespace HealthApp.API.Models
{
    [Table("running_sessions")]
    public class RunningSession
    {
        [Column("id")]
        public int Id { get; set; }

        [Column("user_id")]
        public int? UserId { get; set; }

        [Column("date")]
        public DateTime? Date { get; set; }

        [Column("distance_km")]
        public decimal? DistanceKm { get; set; }

        [Column("duration_minutes")]
        public int? DurationMinutes { get; set; }

        [Column("avg_pace_min_per_km")]
        public decimal? AvgPaceMinPerKm { get; set; }

        [Column("avg_heart_rate")]
        public int? AvgHeartRate { get; set; }

        [Column("max_heart_rate")]
        public int? MaxHeartRate { get; set; }

        [Column("calories_burned")]
        public int? CaloriesBurned { get; set; }

        [Column("route_type")]
        public string? RouteType { get; set; }

        [Column("elevation_m")]
        public int? ElevationM { get; set; }

        [Column("notes")]
        public string? Notes { get; set; }
    }
}