using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using HealthApp.API.Helpers;

namespace HealthApp.API.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    [Authorize]
    public class RunningController : ControllerBase
    {
        private readonly DataDbContext _context;

        public RunningController(DataDbContext context)
        {
            _context = context;
        }

        [HttpGet]
        public async Task<IActionResult> GetAll()
        {
            // TILLFÄLLIG: hårdkodad user_id=1 tills användarsynk mellan databaser är löst
            var sessions = await _context.RunningSessions
                .Where(r => r.UserId == 1)
                .OrderByDescending(r => r.Date)
                .ToListAsync();
            return Ok(sessions);
        }

        [HttpGet("{id}")]
        public async Task<IActionResult> GetById(int id)
        {
            var userId = UserHelper.GetUserId(User);
            if (userId == null) return Unauthorized();

            var session = await _context.RunningSessions
                .FirstOrDefaultAsync(r => r.Id == id && r.UserId == userId);
            if (session == null) return NotFound();
            return Ok(session);
        }
    }
}
