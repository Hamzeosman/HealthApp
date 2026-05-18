using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using HealthApp.API.Models;

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
            var insights = await _context.AiInsights
                .OrderByDescending(i => i.CreatedAt)
                .ToListAsync();
            return Ok(insights);
        }

        [HttpGet("{id}")]
        public async Task<IActionResult> GetById(int id)
        {
            var insight = await _context.AiInsights.FindAsync(id);
            if (insight == null) return NotFound();
            return Ok(insight);
        }
    }
}