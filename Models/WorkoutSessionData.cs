using System.ComponentModel.DataAnnotations.Schema;

namespace Mintakt.API.Models
{
    /// <summary>
    /// Träningspass loggade av användare mot workout_sessions-tabellen
    /// i HealthAppDataDb. Refererar UserData via UserId och har en samling
    /// WorkoutExerciseData via WorkoutExercises-navigationen.
    ///
    /// TemplateId förblir ren int? — workout_templates är out of scope för
    /// Issue #32 och får ingen navigation. Följer "Data"-suffix-mönstret.
    ///
    /// CHECK constraint på Mood konfigureras i DataDbContext.OnModelCreating().
    /// </summary>
    [Table("workout_sessions")]
    public class WorkoutSessionData
    {
        [Column("id")]
        public int Id { get; set; }

        [Column("user_id")]
        public int? UserId { get; set; }

        [Column("template_id")]
        public int? TemplateId { get; set; }

        [Column("date")]
        public DateTime? Date { get; set; }

        [Column("start_time")]
        public DateTime? StartTime { get; set; }

        [Column("end_time")]
        public DateTime? EndTime { get; set; }

        [Column("duration_minutes")]
        public int? DurationMinutes { get; set; }

        [Column("total_calories")]
        public int? TotalCalories { get; set; }

        [Column("mood")]
        public string? Mood { get; set; }

        [Column("notes")]
        public string? Notes { get; set; }

        [Column("created_at")]
        public DateTime? CreatedAt { get; set; }

        // Navigation properties (DataDbContext-world only)
        [ForeignKey(nameof(UserId))]
        public UserData? User { get; set; }

        public ICollection<WorkoutExerciseData> WorkoutExercises { get; set; }
            = new List<WorkoutExerciseData>();
    }
}