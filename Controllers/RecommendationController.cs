using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Mintakt.API.Models;
using Mintakt.API.Services;

namespace Mintakt.API.Controllers
{
    [Authorize]
    [ApiController]
    [Route("api/[controller]")]
    public class RecommendationController : ControllerBase
    {
        private readonly IRecommendationService _service;

        public RecommendationController(IRecommendationService service)
        {
            _service = service;
        }

        [HttpGet("user/{userId}")]
        public async Task<IActionResult> GetByUserId(int userId)
        {
            var recommendations = await _service.GetByUserIdAsync(userId);
            return Ok(recommendations);
        }

        [HttpGet("{id}")]
        public async Task<IActionResult> GetById(int id)
        {
            var recommendation = await _service.GetByIdAsync(id);
            if (recommendation == null) return NotFound();
            return Ok(recommendation);
        }

        [HttpPost]
        public async Task<IActionResult> Add(Recommendation recommendation)
        {
            await _service.AddAsync(recommendation);
            return CreatedAtAction(nameof(GetById), new { id = recommendation.Id }, recommendation);
        }

        [HttpPut("{id}/seen")]
        public async Task<IActionResult> MarkAsSeen(int id)
        {
            var recommendation = await _service.GetByIdAsync(id);
            if (recommendation == null) return NotFound();

            await _service.MarkAsSeenAsync(id);
            return NoContent();
        }
    }
}