namespace Mintakt.API.DTOs
{
    /// <summary>
    /// Returneras av GET /api/achievements/me.
    /// Innehåller både upplåsta och pågående prestationer med progress.
    /// </summary>
    public class AchievementStatusDto
    {
        public string Code { get; set; } = "";
        public string Title { get; set; } = "";
        public string Description { get; set; } = "";
        public string Icon { get; set; } = "";
        public string RequirementType { get; set; } = "";
        public decimal Required { get; set; }
        public decimal Current { get; set; }
        public bool IsUnlocked { get; set; }
        public double Progress { get; set; }  // 0–100
    }
}
