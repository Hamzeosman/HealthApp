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
        /// Legacy-endpoint: hämtar progress-poster för en specifik user via userId i URL.
        /// 
        /// Tidigare saknade denna ownership-check — vem som helst inloggad kunde läsa
        /// vems som helst progress-poster (Issue #81). Nu verifierar vi att URL:s
        /// userId matchar JWT-claim och returnerar NotFound() vid mismatch
        /// (samma IDOR-skydd som GetById).
        /// 
        /// Fortfarande [Obsolete] — behålls för bakåtkompatibilitet med Blazor-frontend
        /// tills frontend migrerats till /me-endpointen i PR B.
        /// </summary>
        [HttpGet("user/{userId}")]
        [Obsolete("Använd GET /api/userprogress/me — user-ID läses från JWT")]
        public async Task<IActionResult> GetByUserId(int userId)
        {
            var jwtUserId = UserHelper.GetUserId(User);
            if (jwtUserId == null) return Unauthorized();
            if (userId != jwtUserId.Value) return NotFound();

            var progress = await _service.GetByUserIdAsync(userId);
            return Ok(progress);
        }

        /// <summary>
        /// Hämtar en specifik progress-post. Säker — returnerar NotFound om
        /// posten inte tillhör den inloggade användaren (ownership-check).
        /// 
        /// Tidigare saknade denna ownership-check HELT (Issue #81) — vem som
        /// helst inloggad kunde läsa vems som helst progress-post bara genom
        /// att gissa ett id. Nu verifierar vi att progress.UserId matchar
        /// JWT-claim och returnerar NotFound() vid mismatch.
        /// 
        /// Vi använder NotFound() istället för Forbidden() för att inte avslöja
        /// om en viss ID existerar för en annan user (information disclosure).
        /// </summary>
        [HttpGet("{id}")]
        public async Task<IActionResult> GetById(int id)
        {
            var userId = UserHelper.GetUserId(User);
            if (userId == null) return Unauthorized();

            var progress = await _service.GetByIdAsync(id);
            if (progress == null) return NotFound();
            if (progress.UserId != userId.Value) return NotFound();

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