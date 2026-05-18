using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace HealthApp.API.Controllers
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
            var totalWorkouts = await _context.WorkoutSessions.CountAsync();
            var totalRunning = await _context.RunningSessions.CountAsync();
            var totalDistance = await _context.RunningSessions.SumAsync(r => r.DistanceKm ?? 0);
            var totalDuration = await _context.WorkoutSessions.SumAsync(s => s.DurationMinutes ?? 0);
            var totalExercises = await _context.Exercises.CountAsync();
            var totalPrograms = await _context.TrainingPlans.CountAsync();
            var totalInsights = await _context.AiInsights.CountAsync();

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