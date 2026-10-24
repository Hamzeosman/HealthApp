using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Mintakt.API.Helpers;
using Mintakt.API.Models;
using Mintakt.API.Services;

namespace Mintakt.API.Controllers
{
    [Authorize]
    [ApiController]
    [Route("api/[controller]")]
    public class UserProgressController : ControllerBase
    {
        private readonly IUserProgressService _service;

        public UserProgressController(IUserProgressService service)
        {
            _service = service;
        }

        /// <summary>
        /// Hämtar inloggade användarens egna progress-poster.
        /// User-ID läses från JWT-claims (inte från URL).
        /// </summary>
        [HttpGet("me")]
        public async Task<IActionResult> GetMyProgress()
        {
            var userId = UserHelper.GetUserId(User);
            if (userId == null) return Unauthorized();

            var progress = await _service.GetByUserIdAsync(userId.Value);
            return Ok(progress);
        }

        /// <summary>
        /// Deprecated: använd GET /api/userprogress/me istället.
        /// Behålls temporärt för bakåtkompatibilitet med äldre frontend-sidor.
        /// Kommer tas bort i framtida PR när alla sidor migrerat till /me.
        /// </summary>
        [HttpGet("user/{userId}")]
        [Obsolete("Använd GET /api/userprogress/me — user-ID läses från JWT")]
        public async Task<IActionResult> GetByUserId(int userId)
        {
            var progress = await _service.GetByUserIdAsync(userId);
            return Ok(progress);
        }

        [HttpGet("{id}")]
        public async Task<IActionResult> GetById(int id)
        {
            var progress = await _service.GetByIdAsync(id);
            if (progress == null) return NotFound();
            return Ok(progress);
        }

        /// <summary>
        /// Skapar ny progress-post för den inloggade användaren.
        /// User-ID sätts från JWT-claims, oavsett vad klienten skickar i body.
        /// Detta förhindrar att en användare skapar poster åt någon annan.
        /// </summary>
        [HttpPost]
        public async Task<IActionResult> Add(UserProgress progress)
        {
            var userId = UserHelper.GetUserId(User);
            if (userId == null) return Unauthorized();

            // Override UserId från klient — säkerhet
            progress.UserId = userId.Value;

            await _service.AddAsync(progress);
            return CreatedAtAction(nameof(GetById), new { id = progress.Id }, progress);
        }
    }
}