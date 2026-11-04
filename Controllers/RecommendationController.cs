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
        /// Hämtar rekommendationer för en specifik user via userId i URL.
        /// 
        /// SÄKERHET: Denna endpoint saknar ownership-check och är planerad att
        /// markeras [Obsolete] i framtida PR till förmån för GET /me som läser
        /// user-id från JWT. Behålls tillfälligt för bakåtkompatibilitet med
        /// Blazor-frontend innan den migreras.
        /// </summary>
        [HttpGet("user/{userId}")]
        public async Task<IActionResult> GetByUserId(int userId)
        {
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
        /// i framtida PR efter arkitektur-beslut.
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