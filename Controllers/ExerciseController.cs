using Microsoft.AspNetCore.Mvc;
using HealthApp.API.Models;
using HealthApp.API.Services;

namespace HealthApp.API.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class ExerciseController : ControllerBase
    {
        private readonly IExerciseService _service;

        public ExerciseController(IExerciseService service)
        {
            _service = service;
        }

        [HttpGet]
        public async Task<IActionResult> GetAll()
        {
            var exercises = await _service.GetAllExercisesAsync();
            return Ok(exercises);
        }

        [HttpGet("{id}")]
        public async Task<IActionResult> GetById(int id)
        {
            var exercise = await _service.GetByIdAsync(id);
            if (exercise == null) return NotFound();
            return Ok(exercise);
        }

        [HttpGet("musclegroup/{muscleGroup}")]
        public async Task<IActionResult> GetByMuscleGroup(string muscleGroup)
        {
            var exercises = await _service.GetByMuscleGroupAsync(muscleGroup);
            return Ok(exercises);
        }

        [HttpPost]
        public async Task<IActionResult> Add(Exercise exercise)
        {
            await _service.AddExerciseAsync(exercise);
            return CreatedAtAction(nameof(GetById), new { id = exercise.Id }, exercise);
        }
    }
}