using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Mintakt.API.Models;
using Mintakt.API.Services;

namespace Mintakt.API.Controllers
{
    [Authorize]
    [ApiController]
    [Route("api/[controller]")]
    public class WorkoutTemplateController : ControllerBase
    {
        private readonly IWorkoutTemplateService _service;

        public WorkoutTemplateController(IWorkoutTemplateService service)
        {
            _service = service;
        }

        [HttpGet("program/{programId}")]
        public async Task<IActionResult> GetByProgramId(int programId)
        {
            var templates = await _service.GetByProgramIdAsync(programId);
            return Ok(templates);
        }

        [HttpGet("{id}")]
        public async Task<IActionResult> GetById(int id)
        {
            var template = await _service.GetByIdAsync(id);
            if (template == null) return NotFound();
            return Ok(template);
        }

        [HttpPost]
        public async Task<IActionResult> Add(WorkoutTemplate template)
        {
            await _service.AddAsync(template);
            return CreatedAtAction(nameof(GetById), new { id = template.Id }, template);
        }
    }
}