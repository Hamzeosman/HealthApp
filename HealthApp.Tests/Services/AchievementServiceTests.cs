using Mintakt.API;
using Microsoft.EntityFrameworkCore;
using Mintakt.API.DTOs;
using Mintakt.API.Models;
using Mintakt.API.Services;

namespace HealthApp.Tests.Services
{
    public class AchievementServiceTests : IDisposable
    {
        private readonly DataDbContext _context;
        private readonly AchievementService _sut;

        public AchievementServiceTests()
        {
            var options = new DbContextOptionsBuilder<DataDbContext>()
                .UseInMemoryDatabase(Guid.NewGuid().ToString())
                .Options;
            _context = new DataDbContext(options);
            _sut = new AchievementService(_context);
        }

        public void Dispose() => _context.Dispose();

        // ── Seed-hjälpare ──────────────────────────────────────────────
        private void SeedAchievement(string type, decimal required, string name = "Test")
        {
            _context.Achievements.Add(new Achievement
            {
                Name = name,
                Description = "",
                Icon = "🏆",
                RequirementType = type,
                RequirementValue = required
            });
            _context.SaveChanges();
        }

        private void SeedWorkoutSessions(int userId, int count)
        {
            for (int i = 0; i < count; i++)
                _context.WorkoutSessions.Add(new WorkoutSessionData { UserId = userId });
            _context.SaveChanges();
        }

        private void SeedRunning(int userId, decimal km)
        {
            _context.RunningSessions.Add(new RunningSession { UserId = userId, DistanceKm = km });
            _context.SaveChanges();
        }

        private void SeedStreak(int userId, int streak)
        {
            _context.UserStreaks.Add(new UserStreak { UserId = userId, CurrentStreak = streak });
            _context.SaveChanges();
        }

        // ── total_sessions ─────────────────────────────────────────────

        [Fact]
        public async Task GetUserAchievementsAsync_FirstWorkout_UnlockedWhenSessionExists()
        {
            SeedAchievement("total_sessions", 1, "First Workout");
            SeedWorkoutSessions(userId: 1, count: 1);

            var result = (await _sut.GetUserAchievementsAsync(1)).ToList();

            Assert.Single(result);
            Assert.True(result[0].IsUnlocked);
            Assert.Equal(100.0, result[0].Progress);
        }

        [Fact]
        public async Task GetUserAchievementsAsync_TenSessions_PartialProgressAt4()
        {
            SeedAchievement("total_sessions", 10, "10 Sessions");
            SeedWorkoutSessions(userId: 2, count: 4);

            var result = (await _sut.GetUserAchievementsAsync(2)).ToList();

            Assert.False(result[0].IsUnlocked);
            Assert.Equal(40.0, result[0].Progress);
            Assert.Equal(4m, result[0].Current);
            Assert.Equal(10m, result[0].Required);
        }

        [Fact]
        public async Task GetUserAchievementsAsync_Sessions_OnlyCountsCorrectUser()
        {
            SeedAchievement("total_sessions", 5);
            SeedWorkoutSessions(userId: 10, count: 5);  // annan användare
            SeedWorkoutSessions(userId: 99, count: 1);  // vår användare

            var result = (await _sut.GetUserAchievementsAsync(99)).ToList();

            Assert.False(result[0].IsUnlocked);
            Assert.Equal(1m, result[0].Current);
        }

        // ── total_distance ─────────────────────────────────────────────

        [Fact]
        public async Task GetUserAchievementsAsync_Runner_UnlockedAt50km()
        {
            SeedAchievement("total_distance", 50, "Runner");
            SeedRunning(userId: 3, km: 225);

            var result = (await _sut.GetUserAchievementsAsync(3)).ToList();

            Assert.True(result[0].IsUnlocked);
            Assert.Equal(100.0, result[0].Progress);
        }

        [Fact]
        public async Task GetUserAchievementsAsync_Runner_PartialProgressAt20km()
        {
            SeedAchievement("total_distance", 50, "Runner");
            SeedRunning(userId: 4, km: 20);

            var result = (await _sut.GetUserAchievementsAsync(4)).ToList();

            Assert.False(result[0].IsUnlocked);
            Assert.Equal(40.0, result[0].Progress);
        }

        // ── streak_days ────────────────────────────────────────────────

        [Fact]
        public async Task GetUserAchievementsAsync_WeekWarrior_UnlockedAt7DayStreak()
        {
            SeedAchievement("streak_days", 7, "Week Warrior");
            SeedStreak(userId: 5, streak: 7);

            var result = (await _sut.GetUserAchievementsAsync(5)).ToList();

            Assert.True(result[0].IsUnlocked);
        }

        [Fact]
        public async Task GetUserAchievementsAsync_Streak_ZeroWhenNoStreakRow()
        {
            SeedAchievement("streak_days", 7, "Week Warrior");
            // ingen UserStreak-rad

            var result = (await _sut.GetUserAchievementsAsync(1)).ToList();

            Assert.False(result[0].IsUnlocked);
            Assert.Equal(0m, result[0].Current);
        }

        // ── Division-by-zero guard ──────────────────────────────────────

        [Fact]
        public async Task GetUserAchievementsAsync_RequirementValueZero_DoesNotThrow()
        {
            SeedAchievement("total_sessions", 0);  // RequirementValue = 0
            SeedWorkoutSessions(userId: 1, count: 1);

            var ex = await Record.ExceptionAsync(() => _sut.GetUserAchievementsAsync(1));

            Assert.Null(ex);
        }

        [Fact]
        public async Task GetUserAchievementsAsync_RequirementValueZero_ProgressCappedAt100()
        {
            SeedAchievement("total_sessions", 0);
            SeedWorkoutSessions(userId: 1, count: 5);

            var result = (await _sut.GetUserAchievementsAsync(1)).ToList();

            Assert.Equal(100.0, result[0].Progress);
        }

        // ── Sortering ──────────────────────────────────────────────────

        [Fact]
        public async Task GetUserAchievementsAsync_UnlockedAchievementsReturnedFirst()
        {
            SeedAchievement("total_sessions", 1, "First Workout");
            SeedAchievement("total_sessions", 50, "50 Sessions");
            SeedWorkoutSessions(userId: 6, count: 1);

            var result = (await _sut.GetUserAchievementsAsync(6)).ToList();

            Assert.True(result[0].IsUnlocked);   // First Workout unlocked
            Assert.False(result[1].IsUnlocked);  // 50 Sessions ej upplåst
        }
    }
}
