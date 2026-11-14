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
        /// Tidigare saknade denna ownership-check — vem som helst inloggad kunde läsa
        /// vems som helst personbästa (Issue #83). Nu verifierar vi att URL:s
        /// userId matchar JWT-claim och returnerar NotFound() vid mismatch
        /// (samma IDOR-skydd som GetById).
        /// 
        /// Fortfarande [Obsolete] — behålls för bakåtkompatibilitet med Blazor-frontend
        /// tills frontend migrerats till /me-endpointen i PR B.
        /// </summary>
        [Obsolete("Använd GET /api/personalrecord/me istället. Denna endpoint tas bort efter frontend-migration i PR B.")]
        [HttpGet("user/{userId}")]
        public async Task<IActionResult> GetByUserId(int userId)
        {
            var jwtUserId = UserHelper.GetUserId(User);
            if (jwtUserId == null) return Unauthorized();
            if (userId != jwtUserId.Value) return NotFound();

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
        /// fält (noterat som separat uppföljning i Issue #83).
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
        /// Skapar ett nytt personbästa. User-id skrivs över från JWT-claim
        /// (JWT-override pattern från PR A3c #69) — body-UserId respekteras aldrig
        /// för att förhindra att en inloggad user skapar records åt andra users.
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