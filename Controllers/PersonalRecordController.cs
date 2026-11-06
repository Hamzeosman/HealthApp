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
    public class PersonalRecordController : ControllerBase
    {
        private readonly IPersonalRecordService _service;

        public PersonalRecordController(IPersonalRecordService service)
        {
            _service = service;
        }

        /// <summary>
        /// Hämtar inloggade användarens personbästa. User-id läses från JWT-claims
        /// via UserHelper — konsistent med /me-pattern från PR A1 (#58) och A2 (#61).
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

            var records = await _service.GetByUserIdAsync(userId.Value);
            return Ok(records);
        }

        /// <summary>
        /// Legacy-endpoint: hämtar personbästa för en specifik user via userId i URL.
        ///
        /// MARKERAD [Obsolete]: Saknar ownership-check — vem som helst inloggad kan läsa
        /// vems som helst personbästa. Behålls för bakåtkompatibilitet med
        /// Blazor-frontend tills frontend migrerats till /me-endpointen i PR B.
        ///
        /// Ta bort när frontend-migration är klar.
        /// </summary>
        [Obsolete("Använd GET /api/personalrecord/me istället. Denna endpoint tas bort efter frontend-migration i PR B.")]
        [HttpGet("user/{userId}")]
        public async Task<IActionResult> GetByUserId(int userId)
        {
            var records = await _service.GetByUserIdAsync(userId);
            return Ok(records);
        }

        /// <summary>
        /// Hämtar personbästa för en specifik övning (publik aggregerad data).
        /// Returnerar INTE user-specifik information — endast övningens
        /// gemensamma stats.
        ///
        /// Oförändrad i denna PR eftersom det är öppen aggregerad data, men
        /// kan behöva granskas senare om PR:ar innehåller user-identifierande
        /// fält.
        /// </summary>
        [HttpGet("exercise/{exerciseId}")]
        public async Task<IActionResult> GetByExerciseId(int exerciseId)
        {
            var records = await _service.GetByExerciseIdAsync(exerciseId);
            return Ok(records);
        }

        /// <summary>
        /// Hämtar ett specifikt personbästa. Säker — returnerar NotFound om
        /// recordet inte tillhör den inloggade användaren (ownership-check).
        ///
        /// Vi använder NotFound() istället för Forbidden() för att inte avslöja
        /// om en viss ID existerar för en annan user (information disclosure).
        /// </summary>
        [HttpGet("{id}")]
        public async Task<IActionResult> GetById(int id)
        {
            var userId = UserHelper.GetUserId(User);
            if (userId == null) return Unauthorized();

            var record = await _service.GetByIdAsync(id);
            if (record == null) return NotFound();
            if (record.UserId != userId.Value) return NotFound();

            return Ok(record);
        }

        /// <summary>
        /// Skapar ett nytt personbästa för den inloggade användaren.
        ///
        /// SÄKERHET: UserId läses från JWT-claims via UserHelper och skriver över
        /// eventuellt värde i body (konsistent med JWT-override-pattern från PR A1
        /// för WorkoutSession och UserProgress). Detta förhindrar att en inloggad
        /// user skapar personbästa i någon annans namn.
        ///
        /// Scope-beslut: Enligt discussion i Issue #67 är PersonalRecord ett
        /// legitimt user-facing use case (manuell loggning), så JWT-override är
        /// rätt pattern här. Recommendation POST hanteras separat i PR A3d med
        /// X-API-Key-middleware eftersom det är AI-pipeline-only.
        /// </summary>
        [HttpPost]
        public async Task<IActionResult> Add(PersonalRecord record)
        {
            var userId = UserHelper.GetUserId(User);
            if (userId == null) return Unauthorized();

            record.UserId = userId.Value;
            await _service.AddAsync(record);
            return CreatedAtAction(nameof(GetById), new { id = record.Id }, record);
        }
    }
}