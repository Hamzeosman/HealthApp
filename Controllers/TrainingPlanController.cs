using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using HealthApp.API.Models;

namespace HealthApp.API.Controllers
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
    }
}