using System.ComponentModel.DataAnnotations.Schema;

namespace HealthApp.API.Models
{
    [Table("achievements")]
    public class Achievement
    {
        [Column("id")]
        public int Id { get; set; }

        [Column("name")]
        public string? Name { get; set; }

        [Column("description")]
        public string? Description { get; set; }

        [Column("icon")]
        public string? Icon { get; set; }

        [Column("requirement_type")]
        public string? RequirementType { get; set; }

        [Column("requirement_value")]
        public decimal? RequirementValue { get; set; }
    }
}