using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
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

        [HttpGet("user/{userId}")]
        public async Task<IActionResult> GetByUserId(int userId)
        {
            var progress = await _service.GetByUserIdAsync(userId);
            return Ok(progress);
        }

        [HttpGet("{id}")]
        public async Task<IActionResult> GetById(int id)
        {
            var progress = await _service.GetByIdAsync(id);
            if (progress == null) return NotFound();
            return Ok(progress);
        }

        [HttpPost]
        public async Task<IActionResult> Add(UserProgress progress)
        {
            await _service.AddAsync(progress);
            return CreatedAtAction(nameof(GetById), new { id = progress.Id }, progress);
        }
    }
}