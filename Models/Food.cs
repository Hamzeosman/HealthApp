using System.ComponentModel.DataAnnotations.Schema;

namespace HealthApp.API.Models
{
    [Table("foods")]
    public class Food
    {
        [Column("id")]
        public int Id { get; set; }

        [Column("name")]
        public string? Name { get; set; }

        [Column("brand")]
        public string? Brand { get; set; }

        [Column("calories_per_100g")]
        public decimal? CaloriesPer100g { get; set; }

        [Column("protein_per_100g")]
        public decimal? ProteinPer100g { get; set; }

        [Column("carbs_per_100g")]
        public decimal? CarbsPer100g { get; set; }

        [Column("fat_per_100g")]
        public decimal? FatPer100g { get; set; }

        [Column("category")]
        public string? Category { get; set; }
    }
}