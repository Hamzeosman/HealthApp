using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using HealthApp.API.Models;
using HealthApp.API.Services;

namespace HealthApp.API.Controllers
{
    [Authorize]
    [ApiController]
    [Route("api/[controller]")]
    public class BodyPartController : ControllerBase
    {
        private readonly IBodyPartService _service;

        public BodyPartController(IBodyPartService service)
        {
            _service = service;
        }

        [HttpGet]
        public async Task<IActionResult> GetAll()
        {
            var bodyParts = await _service.GetAllAsync();
            return Ok(bodyParts);
        }

        [HttpGet("{id}")]
        public async Task<IActionResult> GetById(int id)
        {
            var bodyPart = await _service.GetByIdAsync(id);
            if (bodyPart == null) return NotFound();
            return Ok(bodyPart);
        }

        [HttpPost]
        public async Task<IActionResult> Add(BodyPart bodyPart)
        {
            await _service.AddAsync(bodyPart);
            return CreatedAtAction(nameof(GetById), new { id = bodyPart.Id }, bodyPart);
        }
    }
}