using System.ComponentModel.DataAnnotations.Schema;

namespace HealthApp.API.Models
{
    [Table("meal_logs")]
    public class MealLog
    {
        [Column("id")]
        public int Id { get; set; }

        [Column("user_id")]
        public int? UserId { get; set; }

        [Column("food_id")]
        public int? FoodId { get; set; }

        [Column("date")]
        public DateTime? Date { get; set; }

        [Column("meal_type")]
        public string? MealType { get; set; }

        [Column("amount_g")]
        public decimal? AmountG { get; set; }

        [Column("calories")]
        public decimal? Calories { get; set; }

        [Column("protein_g")]
        public decimal? ProteinG { get; set; }

        [Column("carbs_g")]
        public decimal? CarbsG { get; set; }

        [Column("fat_g")]
        public decimal? FatG { get; set; }
    }
}