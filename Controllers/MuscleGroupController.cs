using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Mintakt.API.Models;
using Mintakt.API.Services;

namespace Mintakt.API.Controllers
{
    [Authorize]
    [ApiController]
    [Route("api/[controller]")]
    public class MuscleGroupController : ControllerBase
    {
        private readonly IMuscleGroupService _service;

        public MuscleGroupController(IMuscleGroupService service)
        {
            _service = service;
        }

        [HttpGet]
        public async Task<IActionResult> GetAll()
        {
            var muscleGroups = await _service.GetAllAsync();
            return Ok(muscleGroups);
        }

        [HttpGet("{id}")]
        public async Task<IActionResult> GetById(int id)
        {
            var muscleGroup = await _service.GetByIdAsync(id);
            if (muscleGroup == null) return NotFound();
            return Ok(muscleGroup);
        }

        [HttpGet("bodypart/{bodyPartId}")]
        public async Task<IActionResult> GetByBodyPartId(int bodyPartId)
        {
            var muscleGroups = await _service.GetByBodyPartIdAsync(bodyPartId);
            return Ok(muscleGroups);
        }

        [HttpPost]
        public async Task<IActionResult> Add(MuscleGroup muscleGroup)
        {
            await _service.AddAsync(muscleGroup);
            return CreatedAtAction(nameof(GetById), new { id = muscleGroup.Id }, muscleGroup);
        }
    }
}