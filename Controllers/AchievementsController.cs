using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using HealthApp.API.Helpers;

namespace HealthApp.API.Controllers
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

        [HttpGet("mine")]
        public async Task<IActionResult> GetUserAchievements()
        {
            // TILLFÄLLIG: hårdkodad user_id=1 tills användarsynk mellan databaser är löst
            var userId = 1;

            var achievements = await (from ua in _context.UserAchievements
                                    join a in _context.Achievements on ua.AchievementId equals a.Id
                                    where ua.UserId == userId
                                    orderby ua.AchievedAt descending
                                    select new
                                    {
                                        a.Id,
                                        a.Name,
                                        a.Description,
                                        a.Icon,
                                        ua.AchievedAt
                                    }).ToListAsync();
            return Ok(achievements);
        }
    }
}