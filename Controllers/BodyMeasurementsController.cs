using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Mintakt.API.Helpers;
using Mintakt.API.Models;

namespace Mintakt.API.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    [Authorize]
    public class BodyMeasurementsController : ControllerBase
    {
        private readonly DataDbContext _context;

        public BodyMeasurementsController(DataDbContext context)
        {
            _context = context;
        }

        /// <summary>
        /// Hämtar inloggade användarens kroppsmått, nyaste först.
        /// User-ID läses från JWT-claims via UserHelper.
        /// 
        /// Historik: tidigare användes hårdkodat userId=1 som tillfällig lösning
        /// medan user-sync mellan AppDbContext och DataDbContext löstes.
        /// Detta är nu fixat via Issue #57 — Register-flödet synkar automatiskt.
        /// </summary>
        [HttpGet]
        public async Task<IActionResult> GetAll()
        {
            var userId = UserHelper.GetUserId(User);
            if (userId == null) return Unauthorized();

            var measurements = await _context.BodyMeasurements
                .Where(m => m.UserId == userId.Value)
                .OrderByDescending(m => m.Date)
                .ToListAsync();
            return Ok(measurements);
        }

        /// <summary>
        /// Skapar en ny kroppsmätning för den inloggade användaren.
        /// User-ID sätts från JWT-claims, oavsett vad klienten skickar i body.
        /// </summary>
        [HttpPost]
        public async Task<IActionResult> Add([FromBody] BodyMeasurement measurement)
        {
            var userId = UserHelper.GetUserId(User);
            if (userId == null) return Unauthorized();

            measurement.UserId = userId;
            if (measurement.Date.HasValue)
            {
                measurement.Date = DateTime.SpecifyKind(measurement.Date.Value, DateTimeKind.Utc);
            }
            else
            {
                measurement.Date = DateTime.UtcNow;
            }

            _context.BodyMeasurements.Add(measurement);
            await _context.SaveChangesAsync();
            return Ok(measurement);
        }
    }
}