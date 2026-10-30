using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Mintakt.API.Helpers;

namespace Mintakt.API.Controllers
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

        /// <summary>
        /// Hämtar inloggade användarens löppass, nyaste först.
        /// User-ID läses från JWT-claims via UserHelper.
        /// 
        /// Historik: tidigare användes hårdkodat userId=1 som tillfällig lösning
        /// medan user-sync mellan AppDbContext och DataDbContext löstes.
        /// Detta är nu fixat via Issue #57 — Register-flödet synkar automatiskt.
        /// </summary>
        [HttpGet]
        public async Task<IActionResult> GetAll()
        {
            var userId = UserHelper.GetUserId(User);
            if (userId == null) return Unauthorized();

            var sessions = await _context.RunningSessions
                .Where(r => r.UserId == userId.Value)
                .OrderByDescending(r => r.Date)
                .ToListAsync();
            return Ok(sessions);
        }

        /// <summary>
        /// Hämtar ett specifikt löppass. Säker — returnerar endast om passet
        /// tillhör den inloggade användaren (ownership-check).
        /// </summary>
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