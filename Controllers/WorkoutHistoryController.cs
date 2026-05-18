using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using HealthApp.API.Models;

namespace HealthApp.API.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    [Authorize]
    public class WorkoutHistoryController : ControllerBase
    {
        private readonly DataDbContext _context;

        public WorkoutHistoryController(DataDbContext context)
        {
            _context = context;
        }

        [HttpGet]
        public async Task<IActionResult> GetAll()
        {
            var sessions = await _context.WorkoutSessions
                .OrderByDescending(s => s.Date)
                .ToListAsync();
            return Ok(sessions);
        }

        [HttpGet("{id}")]
        public async Task<IActionResult> GetById(int id)
        {
            var session = await _context.WorkoutSessions.FindAsync(id);
            if (session == null) return NotFound();
            return Ok(session);
        }
    }
}