using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using HealthApp.API.Models;
using HealthApp.API.Services;

namespace HealthApp.API.Controllers
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

        [HttpGet("user/{userId}")]
        public async Task<IActionResult> GetByUserId(int userId)
        {
            var records = await _service.GetByUserIdAsync(userId);
            return Ok(records);
        }

        [HttpGet("exercise/{exerciseId}")]
        public async Task<IActionResult> GetByExerciseId(int exerciseId)
        {
            var records = await _service.GetByExerciseIdAsync(exerciseId);
            return Ok(records);
        }

        [HttpGet("{id}")]
        public async Task<IActionResult> GetById(int id)
        {
            var record = await _service.GetByIdAsync(id);
            if (record == null) return NotFound();
            return Ok(record);
        }

        [HttpPost]
        public async Task<IActionResult> Add(PersonalRecord record)
        {
            await _service.AddAsync(record);
            return CreatedAtAction(nameof(GetById), new { id = record.Id }, record);
        }
    }
}