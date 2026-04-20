using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using HealthApp.API.Models;
using HealthApp.API.Services;

namespace HealthApp.API.Controllers
{
    [Authorize]
    [ApiController]
    [Route("api/[controller]")]
    public class WorkoutSessionController : ControllerBase
    {
        private readonly IWorkoutSessionService _service;

        public WorkoutSessionController(IWorkoutSessionService service)
        {
            _service = service;
        }

        [HttpGet("user/{userId}")]
        public async Task<IActionResult> GetByUserId(int userId)
        {
            var sessions = await _service.GetByUserIdAsync(userId);
            return Ok(sessions);
        }

        [HttpGet("{id}")]
        public async Task<IActionResult> GetById(int id)
        {
            var session = await _service.GetByIdAsync(id);
            if (session == null) return NotFound();
            return Ok(session);
        }

        [HttpPost]
        public async Task<IActionResult> Add(WorkoutSession session)
        {
            await _service.AddWorkoutSessionAsync(session);
            return CreatedAtAction(nameof(GetById), new { id = session.Id }, session);
        }
    }
}