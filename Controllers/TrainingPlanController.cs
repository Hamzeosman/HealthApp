using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Mintakt.API.Models;

namespace Mintakt.API.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    [Authorize]
    public class TrainingPlanController : ControllerBase
    {
        private readonly DataDbContext _context;

        public TrainingPlanController(DataDbContext context)
        {
            _context = context;
        }

        [HttpGet]
        public async Task<IActionResult> GetAll()
        {
            var plans = await _context.TrainingPlans.ToListAsync();
            return Ok(plans);
        }

        [HttpGet("{id}")]
        public async Task<IActionResult> GetById(int id)
        {
            var plan = await _context.TrainingPlans.FindAsync(id);
            if (plan == null) return NotFound();
            return Ok(plan);
        }

        [HttpGet("{id}/days")]
        public async Task<IActionResult> GetPlanDays(int id)
        {
            var days = await _context.TrainingPlanDays
                .Where(d => d.PlanId == id)
                .OrderBy(d => d.WeekNumber)
                .ThenBy(d => d.DayNumber)
                .ToListAsync();
            return Ok(days);
        }

        [HttpGet("days/{dayId}/exercises")]
public async Task<IActionResult> GetDayExercises(int dayId)
{
    var exercises = await (from tpe in _context.TrainingPlanExercises
                           join ex in _context.Exercises on tpe.ExerciseId equals ex.Id
                           where tpe.PlanDayId == dayId
                           orderby tpe.OrderIndex
                           select new
                           {
                               tpe.Id,
                               tpe.ExerciseId,
                               ExerciseName = ex.Name,
                               ex.Difficulty,
                               ex.ExerciseType,
                               tpe.Sets,
                               tpe.Reps,
                               tpe.RestSeconds,
                               tpe.Intensity,
                               tpe.Notes,
                               tpe.OrderIndex
                           }).ToListAsync();
    return Ok(exercises);
}
    }
}