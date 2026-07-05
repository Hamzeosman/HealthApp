using System.ComponentModel.DataAnnotations.Schema;

namespace HealthApp.API.Models
{
    /// <summary>
    /// Lookup-tabell för träningsutrustning (44 maskiner) mot equipment-tabellen
    /// i HealthAppDataDb. Refereras av ExerciseData.EquipmentId.
    /// Följer "Data"-suffix-mönstret.
    /// </summary>
    [Table("equipment")]
    public class EquipmentData
    {
        [Column("id")]
        public int Id { get; set; }

        [Column("name")]
        public string? Name { get; set; }
    }
}