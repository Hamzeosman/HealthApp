using System.ComponentModel.DataAnnotations;

namespace Mintakt.API.DTOs
{
    public class UpdateProfileDto
    {
        [Range(1, 120, ErrorMessage = "Ålder måste vara mellan 1 och 120")]
        public int? Age { get; set; }

        [Range(20, 500, ErrorMessage = "Vikt måste vara mellan 20 och 500 kg")]
        public decimal? WeightKg { get; set; }

        [Range(50, 250, ErrorMessage = "Längd måste vara mellan 50 och 250 cm")]
        public decimal? HeightCm { get; set; }

        [StringLength(50, ErrorMessage = "FitnessLevel får vara max 50 tecken")]
        public string? FitnessLevel { get; set; }

        [StringLength(100, ErrorMessage = "Goal får vara max 100 tecken")]
        public string? Goal { get; set; }
    }
}