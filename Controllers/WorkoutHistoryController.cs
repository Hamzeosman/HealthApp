using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Mintakt.API.Helpers;

namespace Mintakt.API.Controllers
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
            // TILLFÄLLIG: hårdkodad user_id=1 tills användarsynk mellan databaser är löst
            var sessions = await _context.WorkoutSessions
                .Where(s => s.UserId == 1)
                .OrderByDescending(s => s.Date)
                .ToListAsync();
            return Ok(sessions);
        }

        [HttpGet("{id}")]
        public async Task<IActionResult> GetById(int id)
        {
            var userId = UserHelper.GetUserId(User);
            if (userId == null) return Unauthorized();

            var session = await _context.WorkoutSessions
                .FirstOrDefaultAsync(s => s.Id == id && s.UserId == userId);
            if (session == null) return NotFound();
            return Ok(session);
        }
    }
}