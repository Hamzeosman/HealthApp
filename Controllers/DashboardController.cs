using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Mintakt.API.Helpers;

namespace Mintakt.API.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    [Authorize]
    public class DashboardController : ControllerBase
    {
        private readonly DataDbContext _context;

        public DashboardController(DataDbContext context)
        {
            _context = context;
        }

        /// <summary>
        /// Returnerar dashboard-statistik för den inloggade användaren.
        /// User-ID läses från JWT-claims via UserHelper.
        /// 
        /// Historik: tidigare användes hårdkodat userId=1 som tillfällig lösning
        /// medan user-sync mellan AppDbContext och DataDbContext löstes.
        /// Detta är nu fixat via Issue #57 — Register-flödet synkar automatiskt.
        /// </summary>
        [HttpGet]
        public async Task<IActionResult> GetStats()
        {
            var userId = UserHelper.GetUserId(User);
            if (userId == null) return Unauthorized();

            var totalWorkouts = await _context.WorkoutSessions.CountAsync(s => s.UserId == userId.Value);
            var totalRunning = await _context.RunningSessions.CountAsync(r => r.UserId == userId.Value);
            var totalDistance = await _context.RunningSessions
                .Where(r => r.UserId == userId.Value)
                .SumAsync(r => r.DistanceKm ?? 0);
            var totalDuration = await _context.WorkoutSessions
                .Where(s => s.UserId == userId.Value)
                .SumAsync(s => s.DurationMinutes ?? 0);
            var totalExercises = await _context.Exercises.CountAsync();
            var totalPrograms = await _context.TrainingPlans.CountAsync();
            var totalInsights = await _context.AiInsights.CountAsync(i => i.UserId == userId.Value);

            return Ok(new
            {
                TotalWorkouts = totalWorkouts,
                TotalRunning = totalRunning,
                TotalDistance = totalDistance,
                TotalDuration = totalDuration,
                TotalExercises = totalExercises,
                TotalPrograms = totalPrograms,
                TotalInsights = totalInsights
            });
        }
    }
}