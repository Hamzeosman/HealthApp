using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

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

        [HttpGet]
        public async Task<IActionResult> GetAll()
        {
            // TILLFÄLLIG: hårdkodad user_id=1 tills användarsynk mellan databaser är löst
            var biometrics = await _context.Biometrics
                .Where(b => b.UserId == 1)
                .OrderByDescending(b => b.Date)
                .ToListAsync();
            return Ok(biometrics);
        }
    }
}