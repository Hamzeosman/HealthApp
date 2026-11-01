using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Mintakt.API.Helpers;
using Mintakt.API.Services;

namespace Mintakt.API.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    [Authorize]
    public class AchievementsController : ControllerBase
    {
        private readonly DataDbContext _context;
        private readonly IAchievementService _achievementService;

        public AchievementsController(DataDbContext context, IAchievementService achievementService)
        {
            _context = context;
            _achievementService = achievementService;
        }

        /// <summary>GET /api/achievements — statisk katalog (alla prestationer)</summary>
        [HttpGet]
        public async Task<IActionResult> GetAll()
        {
            var achievements = await _context.Achievements.ToListAsync();
            return Ok(achievements);
        }

        /// <summary>GET /api/achievements/me — personlig progress per prestation</summary>
        [HttpGet("me")]
        public async Task<IActionResult> GetMe()
        {
            var userId = UserHelper.GetUserId(User);
            if (userId == null) return Unauthorized();

            var result = await _achievementService.GetUserAchievementsAsync(userId.Value);
            return Ok(result);
        }

        /// <summary>GET /api/achievements/streak — aktuell streak för inloggad user</summary>
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
