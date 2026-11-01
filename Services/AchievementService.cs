using Microsoft.EntityFrameworkCore;
using Mintakt.API.DTOs;

namespace Mintakt.API.Services
{
    /// <summary>
    /// Beräknar achievement-progress för en användare baserat på faktisk data.
    /// Issue #53 — Achievements progress-beräkning.
    /// </summary>
    public class AchievementService : IAchievementService
    {
        private readonly DataDbContext _context;

        public AchievementService(DataDbContext context)
        {
            _context = context;
        }

        public async Task<IEnumerable<AchievementStatusDto>> GetUserAchievementsAsync(int userId)
        {
            var achievements = await _context.Achievements.ToListAsync();

            var totalSessions = await _context.WorkoutSessions
                .CountAsync(s => s.UserId == userId);

            var totalVolume = await _context.WorkoutExercises
                .Where(e => e.Session != null && e.Session.UserId == userId)
                .SumAsync(e => (decimal?)(e.Sets ?? 0) * (e.Reps ?? 0) * (e.WeightKg ?? 0)) ?? 0;

            var totalDistanceKm = await _context.RunningSessions
                .Where(r => r.UserId == userId)
                .SumAsync(r => (decimal?)r.DistanceKm) ?? 0;

            var totalPRs = await _context.PersonalRecords
                .CountAsync(pr => pr.UserId == userId);

            var streak = await _context.UserStreaks
                .Where(s => s.UserId == userId)
                .Select(s => (int?)s.CurrentStreak)
                .FirstOrDefaultAsync() ?? 0;

            return achievements.Select(a =>
            {
                decimal current = a.RequirementType switch
                {
                    "total_sessions"  => (decimal)totalSessions,
                    "total_volume"    => totalVolume,
                    "total_distance"  => totalDistanceKm,
                    "personal_record" => (decimal)totalPRs,
                    "streak_days"     => (decimal)streak,
                    _                 => 0m
                };

                var required = a.RequirementValue ?? 1;
                var isUnlocked = current >= required;
                var progress = Math.Min(100.0, (double)(current / required) * 100.0);

                return new AchievementStatusDto
                {
                    Code            = a.RequirementType + "_" + a.RequirementValue,
                    Title           = a.Name ?? "",
                    Description     = a.Description ?? "",
                    Icon            = a.Icon ?? "",
                    RequirementType = a.RequirementType ?? "",
                    Required        = required,
                    Current         = current,
                    IsUnlocked      = isUnlocked,
                    Progress        = Math.Round(progress, 1)
                };
            })
            .OrderByDescending(a => a.IsUnlocked)
            .ThenByDescending(a => a.Progress);
        }
    }
}
