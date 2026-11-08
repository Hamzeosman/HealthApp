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
        /// Ägarkontroll: userId i URL:en måste vara samma som inloggad användare (JWT).
        /// Saknas claim returneras 401. Är det någon annans id returneras 404 utan att
        /// tjänsten anropas, så att vi inte avslöjar att id:t finns.
        /// </summary>
        [HttpGet("user/{userId}")]
        [Obsolete("Använd GET /api/workoutsession/me — user-ID läses från JWT")]
        public async Task<IActionResult> GetByUserId(int userId)
        {
            var currentUserId = UserHelper.GetUserId(User);
            if (currentUserId == null) return Unauthorized();

            if (userId != currentUserId.Value) return NotFound();

            var sessions = await _service.GetByUserIdAsync(userId);
            return Ok(sessions);
        }

        /// <summary>
        /// Hämtar ett träningspass via id, men bara om det tillhör den inloggade användaren.
        /// Saknas claim returneras 401. Pass som inte finns eller tillhör någon annan
        /// ger båda 404, så att vi inte avslöjar att id:t existerar (IDOR-skydd).
        /// </summary>
        [HttpGet("{id}")]
        public async Task<IActionResult> GetById(int id)
        {
            var userId = UserHelper.GetUserId(User);
            if (userId == null) return Unauthorized();

            var session = await _service.GetByIdAsync(id);
            if (session == null) return NotFound();
            if (session.UserId != userId.Value) return NotFound();

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