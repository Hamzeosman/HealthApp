using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Mintakt.API.Helpers;

namespace Mintakt.API.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    [Authorize]
    public class AchievementsController : ControllerBase
    {
        private readonly DataDbContext _context;

        public AchievementsController(DataDbContext context)
        {
            _context = context;
        }

        [HttpGet]
        public async Task<IActionResult> GetAll()
        {
            var achievements = await _context.Achievements.ToListAsync();
            return Ok(achievements);
        }

        [HttpGet("streak")]
        public async Task<IActionResult> GetStreak()
        {
            var userId = UserHelper.GetUserId(User);
            if (userId == null) return Unauthorized();

            var streak = await _context.UserStreaks.FirstOrDefaultAsync(s => s.UserId == userId);
            return Ok(streak);
        }
    }
}