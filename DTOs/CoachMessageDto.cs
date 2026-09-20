namespace HealthApp.API.DTOs
{
    // DTO för coach_messages-endpoint från Python API.
    //
    // OBS: Detta är en KUNSKAPSBAS, inte per-user-data (bekräftat av Abdulrahman
    // i PR #46-review). Ingen UserId finns — meddelanden är generiska texter som
    // kan visas för många användare baserat på trigger_type och kategori.
    //
    // Cachestrategi framöver: eftersom detta är statiskt content kan det cachas
    // aggressivt (kanske 24h+) — men caching är out of scope för Iter 3.
    public class CoachMessageDto
    {
        public string? Category { get; set; }
        public string? TriggerType { get; set; }
        public string? MessageSv { get; set; }
        public string? MessageEn { get; set; }
        public string? Tone { get; set; }
        public string? Language { get; set; }
        public int? Priority { get; set; }
    }
}