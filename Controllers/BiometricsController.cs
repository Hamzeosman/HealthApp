using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Mintakt.API.Helpers;

namespace Mintakt.API.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    [Authorize]
    public class BiometricsController : ControllerBase
    {
        private readonly DataDbContext _context;

        public BiometricsController(DataDbContext context)
        {
            _context = context;
        }

        /// <summary>
        /// Hämtar inloggade användarens biometri-data, nyaste först.
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

            var biometrics = await _context.Biometrics
                .Where(b => b.UserId == userId.Value)
                .OrderByDescending(b => b.Date)
                .ToListAsync();
            return Ok(biometrics);
        }
    }
}