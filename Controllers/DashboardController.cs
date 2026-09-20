using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

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

        [HttpGet]
        public async Task<IActionResult> GetStats()
        {
            // TILLFÄLLIG: hårdkodad user_id=1 tills användarsynk mellan databaser är löst
            var userId = 1;

            var totalWorkouts = await _context.WorkoutSessions.CountAsync(s => s.UserId == userId);
            var totalRunning = await _context.RunningSessions.CountAsync(r => r.UserId == userId);
            var totalDistance = await _context.RunningSessions
                .Where(r => r.UserId == userId)
                .SumAsync(r => r.DistanceKm ?? 0);
            var totalDuration = await _context.WorkoutSessions
                .Where(s => s.UserId == userId)
                .SumAsync(s => s.DurationMinutes ?? 0);
            var totalExercises = await _context.Exercises.CountAsync();
            var totalPrograms = await _context.TrainingPlans.CountAsync();
            var totalInsights = await _context.AiInsights.CountAsync(i => i.UserId == userId);

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