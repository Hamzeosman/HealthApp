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
        /// nedan är markerad [Obsolete] och planerad att tas bort i PR B när alla
        /// anropare är verifierade som utbytta eller icke-existerande.
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
        /// Fortfarande [Obsolete]. Frontend-grep i HealthApp.Client visade 0 anropare,
        /// men Python-pipelinen är inte sökt än. Behålls tills Python-sökningen är gjord;
        /// planerad borttagning i PR B när alla anropare är verifierade som utbytta
        /// eller icke-existerande.
        /// </summary>
        [Obsolete("Använd GET /api/personalrecord/me istället. Denna endpoint planeras för borttagning i PR B när alla anropare är verifierade.")]
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
        /// Hämtar personbästa för en specifik övning.
        /// 
        /// KÄND SÄKERHETSSVAGHET: Returnerar `PersonalRecord`-objekt inkl.
        /// `UserId`-fältet, vilket läcker vilka users som har records för övningen
        /// (information disclosure). Oförändrad i denna PR — planerad fix via DTO
        /// i separat PR. Se Issue #83 för uppföljning.
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