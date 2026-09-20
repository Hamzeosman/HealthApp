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

        [HttpGet]
        public async Task<IActionResult> GetAll()
        {
            // TILLFÄLLIG: hårdkodad user_id=1 tills användarsynk mellan databaser är löst
            var measurements = await _context.BodyMeasurements
                .Where(m => m.UserId == 1)
                .OrderByDescending(m => m.Date)
                .ToListAsync();
            return Ok(measurements);
        }

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