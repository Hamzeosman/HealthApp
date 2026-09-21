namespace Mintakt.API.Models
{
    public class PersonalRecord
    {
        public int Id { get; set; }
        public int UserId { get; set; }
        public int ExerciseId { get; set; }
        public decimal? WeightKg { get; set; }
        public int Reps { get; set; }
        public DateTime Date { get; set; }
        public string Notes { get; set; } = string.Empty;

        public User? User { get; set; }
        public Exercise? Exercise { get; set; }
    }
}