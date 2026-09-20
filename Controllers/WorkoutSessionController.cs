using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Mintakt.API.DTOs;
using Mintakt.API.Services;

namespace Mintakt.API.Controllers
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
        public async Task<IActionResult> Add(CreateWorkoutSessionDto dto)
        {
            var session = await _service.AddWorkoutSessionAsync(dto);
            return CreatedAtAction(nameof(GetById), new { id = session.Id }, session);
        }
    }
}