using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using HealthApp.API.Helpers;

namespace HealthApp.API.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    [Authorize]
    public class AiInsightController : ControllerBase
    {
        private readonly DataDbContext _context;

        public AiInsightController(DataDbContext context)
        {
            _context = context;
        }

        [HttpGet]
        public async Task<IActionResult> GetAll()
        {
            // TILLFÄLLIG: hårdkodad user_id=1 tills användarsynk mellan databaser är löst
            var insights = await _context.AiInsights
                .Where(i => i.UserId == 1)
                .OrderByDescending(i => i.CreatedAt)
                .ToListAsync();
            return Ok(insights);
        }

        [HttpGet("{id}")]
        public async Task<IActionResult> GetById(int id)
        {
            var userId = UserHelper.GetUserId(User);
            if (userId == null) return Unauthorized();

            var insight = await _context.AiInsights
                .FirstOrDefaultAsync(i => i.Id == id && i.UserId == userId);
            if (insight == null) return NotFound();
            return Ok(insight);
        }
    }
}