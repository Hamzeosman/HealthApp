using System.ComponentModel.DataAnnotations.Schema;

namespace Mintakt.API.Models
{
    /// <summary>
    /// Övningar från exercises-tabellen i HealthAppDataDb (168 st).
    /// Refererar EquipmentData via EquipmentId.
    /// Följer "Data"-suffix-mönstret.
    /// </summary>
    [Table("exercises")]
    public class ExerciseData
    {
        [Column("id")]
        public int Id { get; set; }

        [Column("name")]
        public string? Name { get; set; }

        [Column("body_part_id")]
        public int? BodyPartId { get; set; }

        [Column("muscle_group_id")]
        public int? MuscleGroupId { get; set; }

        [Column("equipment_id")]
        public int? EquipmentId { get; set; }

        [Column("difficulty")]
        public string? Difficulty { get; set; }

        [Column("exercise_type")]
        public string? ExerciseType { get; set; }

        [Column("description")]
        public string? Description { get; set; }

        [Column("instructions")]
        public string? Instructions { get; set; }

        [Column("tips")]
        public string? Tips { get; set; }

        [Column("calories_per_minute")]
        public decimal? CaloriesPerMinute { get; set; }

        // Navigation property (DataDbContext-world only)
        [ForeignKey(nameof(EquipmentId))]
        public EquipmentData? Equipment { get; set; }
    }
}