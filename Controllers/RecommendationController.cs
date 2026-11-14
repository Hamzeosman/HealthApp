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
    public class RecommendationController : ControllerBase
    {
        private readonly IRecommendationService _service;

        public RecommendationController(IRecommendationService service)
        {
            _service = service;
        }

        /// <summary>
        /// Hämtar inloggade användarens rekommendationer. User-id läses från
        /// JWT-claims via UserHelper — konsistent med /me-pattern från PR A1 (#58)
        /// och A2 (#61).
        /// 
        /// Detta är den PREFERRED endpointen framåt. Den legacy /user/{userId}-endpointen
        /// nedan är markerad [Obsolete] och planerad att tas bort när frontend har
        /// migrerats i PR B.
        /// </summary>
        [HttpGet("me")]
        public async Task<IActionResult> GetMe()
        {
            var userId = UserHelper.GetUserId(User);
            if (userId == null) return Unauthorized();

            var recommendations = await _service.GetByUserIdAsync(userId.Value);
            return Ok(recommendations);
        }

        /// <summary>
        /// Legacy-endpoint: hämtar rekommendationer för en specifik user via userId i URL.
        /// 
        /// Tidigare saknade denna ownership-check — vem som helst inloggad kunde läsa
        /// vems som helst rekommendationer (Issue #82). Nu verifierar vi att URL:s
        /// userId matchar JWT-claim och returnerar NotFound() vid mismatch
        /// (samma IDOR-skydd som GetById och MarkAsSeen).
        /// 
        /// Fortfarande [Obsolete] — behålls för bakåtkompatibilitet med Blazor-frontend
        /// tills frontend migrerats till /me-endpointen i PR B.
        /// </summary>
        [Obsolete("Använd GET /api/recommendation/me istället. Denna endpoint tas bort efter frontend-migration i PR B.")]
        [HttpGet("user/{userId}")]
        public async Task<IActionResult> GetByUserId(int userId)
        {
            var jwtUserId = UserHelper.GetUserId(User);
            if (jwtUserId == null) return Unauthorized();
            if (userId != jwtUserId.Value) return NotFound();

            var recommendations = await _service.GetByUserIdAsync(userId);
            return Ok(recommendations);
        }

        /// <summary>
        /// Hämtar en specifik rekommendation. Säker — returnerar NotFound om
        /// rekommendationen inte tillhör den inloggade användaren (ownership-check).
        /// 
        /// Vi använder NotFound() istället för Forbidden() för att inte avslöja
        /// om en viss ID existerar för en annan user (information disclosure).
        /// </summary>
        [HttpGet("{id}")]
        public async Task<IActionResult> GetById(int id)
        {
            var userId = UserHelper.GetUserId(User);
            if (userId == null) return Unauthorized();

            var recommendation = await _service.GetByIdAsync(id);
            if (recommendation == null) return NotFound();
            if (recommendation.UserId != userId.Value) return NotFound();

            return Ok(recommendation);
        }

        /// <summary>
        /// Skapar en ny rekommendation.
        /// 
        /// TODO: Behöver scope-diskussion med teamet — ska vanlig user kunna skapa
        /// rekommendationer eller är detta Admin-only / AI-pipeline-only? Idag
        /// accepteras body från klient utan JWT-override. Planerat att adresseras
        /// i framtida PR A3c efter arkitektur-beslut.
        /// </summary>
        [HttpPost]
        public async Task<IActionResult> Add(Recommendation recommendation)
        {
            await _service.AddAsync(recommendation);
            return CreatedAtAction(nameof(GetById), new { id = recommendation.Id }, recommendation);
        }

        /// <summary>
        /// Markerar en rekommendation som sedd. Säker — returnerar NotFound om
        /// rekommendationen inte tillhör den inloggade användaren.
        /// </summary>
        [HttpPut("{id}/seen")]
        public async Task<IActionResult> MarkAsSeen(int id)
        {
            var userId = UserHelper.GetUserId(User);
            if (userId == null) return Unauthorized();

            var recommendation = await _service.GetByIdAsync(id);
            if (recommendation == null) return NotFound();
            if (recommendation.UserId != userId.Value) return NotFound();

            await _service.MarkAsSeenAsync(id);
            return NoContent();
        }
    }
}