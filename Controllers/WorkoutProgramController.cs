using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Mintakt.API.Models;
using Mintakt.API.Services;

namespace Mintakt.API.Controllers
{
    [Authorize]
    [ApiController]
    [Route("api/[controller]")]
    public class WorkoutProgramController : ControllerBase
    {
        private readonly IWorkoutProgramService _service;

        public WorkoutProgramController(IWorkoutProgramService service)
        {
            _service = service;
        }

        [HttpGet]
        public async Task<IActionResult> GetAll()
        {
            var programs = await _service.GetAllAsync();
            return Ok(programs);
        }

        [HttpGet("{id}")]
        public async Task<IActionResult> GetById(int id)
        {
            var program = await _service.GetByIdAsync(id);
            if (program == null) return NotFound();
            return Ok(program);
        }

        [HttpPost]
        public async Task<IActionResult> Add(WorkoutProgram program)
        {
            await _service.AddAsync(program);
            return CreatedAtAction(nameof(GetById), new { id = program.Id }, program);
        }
    }
}