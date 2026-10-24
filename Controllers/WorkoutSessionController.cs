using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Mintakt.API.DTOs;
using Mintakt.API.Helpers;
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

        /// <summary>
        /// Hämtar inloggade användarens egna träningspass.
        /// User-ID läses från JWT-claims (inte från URL).
        /// </summary>
        [HttpGet("me")]
        public async Task<IActionResult> GetMySessions()
        {
            var userId = UserHelper.GetUserId(User);
            if (userId == null) return Unauthorized();

            var sessions = await _service.GetByUserIdAsync(userId.Value);
            return Ok(sessions);
        }

        /// <summary>
        /// Deprecated: använd GET /api/workoutsession/me istället.
        /// Behålls temporärt för bakåtkompatibilitet med äldre frontend-sidor.
        /// Kommer tas bort i framtida PR när alla sidor migrerat till /me.
        /// </summary>
        [HttpGet("user/{userId}")]
        [Obsolete("Använd GET /api/workoutsession/me — user-ID läses från JWT")]
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

        /// <summary>
        /// Skapar ett nytt träningspass för den inloggade användaren.
        /// User-ID sätts från JWT-claims, oavsett vad klienten skickar i body.
        /// Detta förhindrar att en användare skapar pass åt någon annan.
        /// </summary>
        [HttpPost]
        public async Task<IActionResult> Add(CreateWorkoutSessionDto dto)
        {
            var userId = UserHelper.GetUserId(User);
            if (userId == null) return Unauthorized();

            // Override UserId från klient — säkerhet
            dto.UserId = userId.Value;

            var session = await _service.AddWorkoutSessionAsync(dto);
            return CreatedAtAction(nameof(GetById), new { id = session.Id }, session);
        }
    }
}