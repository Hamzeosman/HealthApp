using System.ComponentModel.DataAnnotations.Schema;

namespace HealthApp.API.Models
{
    [Table("body_measurements")]
    public class BodyMeasurement
    {
        [Column("id")]
        public int Id { get; set; }

        [Column("user_id")]
        public int? UserId { get; set; }

        [Column("date")]
        public DateTime? Date { get; set; }

        [Column("weight_kg")]
        public decimal? WeightKg { get; set; }

        [Column("body_fat_percentage")]
        public decimal? BodyFatPercentage { get; set; }

        [Column("muscle_mass_kg")]
        public decimal? MuscleMassKg { get; set; }

        [Column("chest_cm")]
        public decimal? ChestCm { get; set; }

        [Column("waist_cm")]
        public decimal? WaistCm { get; set; }

        [Column("hips_cm")]
        public decimal? HipsCm { get; set; }

        [Column("bicep_cm")]
        public decimal? BicepCm { get; set; }

        [Column("thigh_cm")]
        public decimal? ThighCm { get; set; }
    }
}